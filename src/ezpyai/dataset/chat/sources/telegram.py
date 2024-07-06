import os
import json
from typing import List

from ezpyai.exceptions import FileNotFoundError


class _DatasetSourceEntryTelegram:
    pass


class DatasetSourceTelegram:
    def __init__(self, json_export_file_path: str) -> None:
        if not os.path.exists(json_export_file_path):
            raise FileNotFoundError(f"File not found: {json_export_file_path}")

        self._json_export_file_path: str = json_export_file_path
        self._entries: List[_DatasetSourceEntryTelegram] = []

        self._parse_json_export_file()

    def _parse_json_export_file(self):

        with open(self._json_export_file_path, "r") as f:
            data = json.load(f)

        # chats = data["chats"]["list"]
