import os
import uuid


def generate_uuid(file_name: str):
    file, ext = os.path.splitext(file_name)
    if not ext:
        raise ValueError(f"{file_name} doesn't have an extension")

    generated_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, file))
    return f"{generated_uuid}{ext}"
