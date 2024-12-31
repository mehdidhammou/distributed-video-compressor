from kafka import KafkaConsumer
import os
import logging
from minio import Minio
import json
from kafka import KafkaConsumer, KafkaProducer
from video_compressor import VideoCompressor
from datetime import datetime


def setup_client() -> Minio:
    return Minio(
        endpoint=os.getenv("MINIO_ENDPOINT_URL"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False,
    )


def setup_kafka_consumer() -> KafkaConsumer:
    upload_topic = os.getenv("KAFKA_UPLOAD_TOPIC")
    server = os.getenv("KAFKA_SERVER")

    return KafkaConsumer(
        upload_topic,
        bootstrap_servers=[server],
        key_deserializer=bytes.decode,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )


def setup_kafka_producer() -> KafkaProducer:
    server = os.getenv("KAFKA_SERVER")

    return KafkaProducer(
        bootstrap_servers=[server],
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def pipeline(
    file_name: str,
    resolution: int,
    client: Minio,
    bucket: str,
    producer: KafkaProducer,
    topic: str,
):
    try:
        # Compress the video
        output_file = VideoCompressor.compress(
            file_name=file_name, target_res=resolution
        )

        # Upload the compressed file to MinIO
        client.fput_object(
            bucket_name=bucket,
            object_name=output_file,
            file_path=output_file,
        )
        logging.info(f"Uploaded {output_file} to bucket {bucket}")

        # Prepare the Kafka message
        message = {
            "bucket": bucket,
            "file_name": output_file,
            "resolution": f"{resolution}p",
            "uploaded_at": datetime.now().isoformat(),
        }

        # Publish the message to Kafka
        producer.send(
            topic=topic,
            key=output_file,  # Ensure key is bytes
            value=message,
        )
        producer.flush()
        logging.info(f"Published message to topic {topic}: {message}")

    except Exception as e:
        logging.error(
            f"Error processing {file_name} at {resolution}p: {e}", exc_info=True
        )
    finally:
        # Cleanup local file
        if os.path.exists(output_file):
            os.remove(output_file)
            logging.info(f"Cleaned up local file {output_file}")
        else:
            logging.warning(f"Local file {output_file} not found for cleanup")
