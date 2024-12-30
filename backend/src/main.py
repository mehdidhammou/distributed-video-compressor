import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from minio import Minio
from minio.error import S3Error
from werkzeug.utils import secure_filename

load_dotenv()

# Flask app
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024)
)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,  # Logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Log all incoming requests using before_request hook
@app.before_request
def log_request_info():
    app.logger.info(f"Request {request.method} {request.path} received.")


# Log all responses using after_request hook (optional, logs after request is processed)
@app.after_request
def log_response_info(response):
    app.logger.info(f"Response status code: {response.status_code}")
    return response


client = Minio(
    endpoint=os.getenv("ENDPOINT_URL"),
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    secure=False,
)

bucket = os.getenv("BUCKET")
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)
    app.logger.info(f"Bucket {bucket} created.")


@app.route("/")
def home():
    return "Hello, World!"


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

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
            object_name=secure_filename(file.filename),
            data=file.stream,
            length=file_length,
            content_type=file.content_type,
        )

        return (
            jsonify({"message": f"File '{file.filename}' uploaded successfully"}),
            200,
        )

        # publish event to kafka

    except S3Error as e:
        app.logger.error(e)
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500


if __name__ == "__main__":
    app.run()
