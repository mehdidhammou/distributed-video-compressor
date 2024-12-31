import logging
import os

from dotenv import load_dotenv
from utils import setup_client, setup_kafka_consumer, setup_kafka_producer, pipeline
from video_compressor import VideoCompressor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    load_dotenv()

    bucket = os.getenv("MINIO_BUCKET")
    compress_topic = os.getenv("KAFKA_COMPRESS_TOPIC")

    bucket = os.getenv("MINIO_BUCKET")
    compress_topic = os.getenv("KAFKA_COMPRESS_TOPIC")
    max_workers = int(os.getenv("MAX_WORKERS", 4))

    logging.info("Starting application")
    logging.info(f"MinIO bucket: {bucket}")
    logging.info(f"Kafka compression topic: {compress_topic}")
    logging.info(f"Max workers: {max_workers}")

    client = setup_client()
    producer = setup_kafka_producer()
    consumer = setup_kafka_consumer()

    try:
        for msg in consumer:
            file_name = msg.key

            # Download file from MinIO
            client.fget_object(bucket, file_name, file_name)
            logging.info(f"Successfully downloaded {file_name}")

            # Get resolutions for compression
            resolutions = VideoCompressor.get_compression_resolutions(file_name)
            logging.info(f"Compression resolutions for {file_name}: {resolutions}")

            tasks = [
                (file_name, res, client, bucket, producer, compress_topic)
                for res in resolutions
            ]

            # TODO
            # this is parallelizable
            # potential race conditions when using ffmpeg.
            for task in tasks:
                pipeline(*task)

            os.remove(file_name)

    except Exception as e:
        logging.critical(f"Critical error in main loop: {e}", exc_info=True)


if __name__ == "__main__":
    main()
