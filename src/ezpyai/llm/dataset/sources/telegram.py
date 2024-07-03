import os

from ezpyai.exceptions import FileNotFoundError


class DatasetSourceTelegram:
    def __init__(self, json_export_file_path: str) -> None:
        if not os.path.exists(json_export_file_path):
            raise FileNotFoundError(f"File not found: {json_export_file_path}")

        self._json_export_file_path = json_export_file_path
