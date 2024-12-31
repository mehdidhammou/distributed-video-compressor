import ffmpeg
import os
from minio.datatypes import Object
import logging


class VideoCompressor:

    @staticmethod
    def _get_original_resolution(file: str) -> tuple[int, int]:
        try:
            probe = ffmpeg.probe(
                file,
                v="error",
                select_streams="v:0",
                show_entries="stream=width,height",
            )

            if not probe.get("streams"):
                raise ValueError(f"No video streams found in {file}")

            video_stream = probe["streams"][0]
            width = video_stream["width"]
            height = video_stream["height"]

            return width, height

        except ffmpeg.Error as e:
            logging.error(
                f"FFmpeg error occurred while probing {file}: {e.stderr.decode()}"
            )
            raise  # Reraise the exception or handle as needed

        except ValueError as e:
            logging.error(f"ValueError: {e}")
            raise

        except Exception as e:
            logging.error(
                f"An unexpected error occurred while getting resolution for {file}: {str(e)}"
            )
            raise

    @staticmethod
    def _get_new_file_name(file: str, target_res: int) -> str:
        # Create new filename based on target resolution
        res = f"{target_res}p"
        file_name, ext = os.path.splitext(os.path.basename(file))
        return f"{file_name}-{res}{ext}"

    @staticmethod
    def get_compression_resolutions(file: str) -> list[int]:
        width, height = VideoCompressor._get_original_resolution(file)
        max_res = min(width, height)

        all_resolutions = [144, 240, 360, 480, 720, 1080, 2160]
        available_resolutions = [
            res for res in all_resolutions if res <= int(os.getenv("MAX_RESOLUTION"))
        ]
        return [res for res in available_resolutions if res <= max_res]

    @staticmethod
    def _get_new_resolution(
        width: int, height: int, target_res: int
    ) -> tuple[int, int]:
        # Calculate target resolution while maintaining aspect ratio
        if width > height:  # Landscape video
            aspect_ratio = height / width
            width = target_res
            height = int(width * aspect_ratio)
        else:
            aspect_ratio = width / height
            height = target_res
            width = int(height * aspect_ratio)

        return width, height

    @staticmethod
    def compress(file_name: str, target_res: int) -> str:
        # Compress the video to the target resolution
        width, height = VideoCompressor._get_original_resolution(file_name)
        width, height = VideoCompressor._get_new_resolution(width, height, target_res)
        try:
            output_file = VideoCompressor._get_new_file_name(file_name, target_res)
            stream = ffmpeg.input(file_name)
            stream = ffmpeg.filter(stream, "scale", width, height)
            stream = ffmpeg.output(stream, output_file)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

            logging.debug(f"Compressed video saved as {output_file}")

            return output_file

        except ffmpeg.Error as e:
            logging.error(f"Error occurred: {e.stderr.decode()}")

        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
