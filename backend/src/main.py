import json
import logging
import os
from datetime import datetime
from utils import generate_uuid
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from kafka import KafkaProducer, KafkaConsumer
from minio import Minio
from minio.error import S3Error
from werkzeug.utils import secure_filename
import threading
import time

load_dotenv()

clients = {}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024)
)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.before_request
def log_request_info():
    app.logger.info(f"Request {request.method} {request.path} received.")


@app.after_request
def log_response_info(response):
    app.logger.info(f"Response status code: {response.status_code}")
    return response


s3_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT_URL"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)

bucket = os.getenv("MINIO_BUCKET")
if not s3_client.bucket_exists(bucket):
    s3_client.make_bucket(bucket)
    app.logger.info(f"Bucket {bucket} created.")


upload_topic = os.getenv("KAFKA_UPLOAD_TOPIC")
producer = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_SERVER")],
    key_serializer=str.encode,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


@app.route("/")
def home():
    return "Hello, World!"


@app.route("/upload", methods=["POST"])
def upload_file():
    if "video" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["video"]

    # Check if a file was selected
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file.mimetype.split("/")[0] != "video":
        return jsonify({"error": "File is not a video"})

    # hash filename
    file.filename = generate_uuid(secure_filename(file.filename))
    app.logger.info(f"received file : {file.filename}")
    app.logger.info(f"file mime : {file.mimetype}")

    try:
        # we need this to retrieve the file size, as it's still a byte stream
        file_length = file.seek(0, os.SEEK_END)
        file.seek(0, os.SEEK_SET)

        s3_client.put_object(
            bucket_name=bucket,
            object_name=file.filename,
            data=file.stream,
            length=file_length,
            content_type=file.content_type,
        )

    except S3Error as e:
        app.logger.error(e)
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500

    message = {
        "bucket": bucket,
        "file_name": file.filename,
        "uploaded_at": datetime.now().isoformat(),
    }

    # publish event to kafka
    producer.send(
        topic=upload_topic,
        key=file.filename,
        value=message,
    )

    producer.flush()

    app.logger.info(f"Message {file.filename} sent to kafka topic {upload_topic}")

    return (
        jsonify(
            {
                "message": f"File saved as {file.filename}",
                "video": file.filename,
            }
        ),
        200,
    )


# Kafka Consumer Thread
def consume_kafka(video):
    compress_topic = os.getenv("KAFKA_COMPRESS_TOPIC")

    consumer = KafkaConsumer(
        compress_topic,
        bootstrap_servers=[os.getenv("KAFKA_SERVER")],
        key_deserializer=bytes.decode,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    while True:
        for msg in consumer:
            # If the Kafka message's key matches the video ID, send the event to the client
            if msg.key == video:
                event = msg.value
                if video in clients:
                    for client in clients[video]:
                        client.put(event)  # Push event to the SSE client queue

            time.sleep(1)  # Slight delay to avoid overloading the Kafka consumer


# SSE Response for Compression Status
@app.route("/compression-status/<video>")
def compression_status(video):
    def generate():
        # Each client has its own queue for SSE updates
        from queue import Queue

        q = Queue()

        # Add the queue to the global clients dict for this video
        if video not in clients:
            clients[video] = []
        clients[video].append(q)

        try:
            while True:
                event = q.get()  # Block until a new event is added
                if event:
                    yield f"data: {json.dumps(event)}\n\n"  # Format for SSE event
        except GeneratorExit:
            # Remove the client when the connection is closed
            clients[video].remove(q)

    # Ensure Kafka consumer is started for this video
    if video not in clients:
        threading.Thread(target=consume_kafka, args=(video,), daemon=True).start()

    # Return the SSE stream to the client
    return Response(generate(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run()
