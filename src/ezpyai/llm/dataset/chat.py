from typing import List, Dict

from ezpyai._constants import DICT_KEY_FROM, DICT_KEY_VALUE


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

    def to_sharegpt(self) -> Dict[str, str]:
        """
        Convert the DatasetChatEntry object to a ShareGPT style dictionary.

        Returns:
            Dict[str, str]: A dictionary containing the role and content of the chat entry.
        """

        return {DICT_KEY_FROM: self.role, DICT_KEY_VALUE: self.content}


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

    def to_sharegpt(self) -> List[Dict[str, str]]:
        """
        Convert the DatasetChat object to a list of ShareGPT style dictionaries.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the role and content of the chat entries as a ShareGPT style dictionary.
        """

        return [entry.to_sharegpt() for entry in self.entries]
