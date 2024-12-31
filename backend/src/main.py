import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from kafka import KafkaProducer
from minio import Minio
from minio.error import S3Error
from werkzeug.utils import secure_filename

load_dotenv()

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


client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT_URL"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)

bucket = os.getenv("MINIO_BUCKET")
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)
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

    file.filename = secure_filename(file.filename)
    app.logger.info(f"received file : {file.filename}")
    app.logger.info(f"file mime : {file.mimetype}")

    try:
        # we need this to retrieve the file size, as it's still a byte stream
        file_length = file.seek(0, os.SEEK_END)
        file.seek(0, os.SEEK_SET)

        client.put_object(
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

    return (jsonify({"message": f"File '{file.filename}' uploaded successfully"}), 200)


if __name__ == "__main__":
    app.run()
