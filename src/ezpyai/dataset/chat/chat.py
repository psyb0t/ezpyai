from typing import List
from ezpyai.dataset.chat.sources.telegram import DatasetSourceTelegram


class DatasetChatEntry:
    """
    A class to store chat entry data.

    Attributes:
        role (str): The role of the chat entry.
        content (str): The content of the chat entry.
    """

    def __init__(self, role: str, content: str) -> None:
        """
        Initialize the DatasetChatEntry object.

        Args:
            role (str): The role of the chat entry.
            content (str): The content of the chat entry.
        """
        self.role: str = role
        self.content: str = content


class DatasetChat:
    """
    A class to store chat data.

    Attributes:
        entries (List[DatasetChatEntry]): A list of DatasetChatEntry objects.
    """

    def __init__(self) -> None:
        """
        Initialize the DatasetChat object.
        """

        self.entries: List[DatasetChatEntry] = []

    def from_telegram_json_export_file(json_export_file_path: str):
        """
        Create a DatasetChat object from a Telegram export file.

        Args:
            json_export_file_path (str): The path to the Telegram export file.
        """

        source: DatasetSourceTelegram = DatasetSourceTelegram(json_export_file_path)
