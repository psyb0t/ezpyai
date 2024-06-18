from typing import Dict
from ezpyai._constants import (
    _DICT_KEY_ID,
    _DICT_KEY_METADATA,
    _DICT_KEY_CONTENT,
    _DICT_KEY_SUMMARY,
)


class KnowledgeItem:
    """
    A class to store knowledge data.

    Attributes:
        id (str): The unique identifier of the knowledge item.
        metadata (Dict[str, str]): The metadata of the knowledge item.
        content (str): The content of the knowledge item.
        summary (str): The summary of the knowledge item's content.
    """

    def __init__(
        self,
        id: str,
        content: str,
        summary: str = "",
        metadata: Dict[str, str] = None,
    ):
        if metadata is None:
            metadata = {}

        self.id = id
        self.metadata = metadata
        self.content = content
        self.summary = summary

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, metadata={self.metadata}, content={self.content}, summary={self.summary})"

    def to_dict(self) -> Dict[str, str]:
        return {
            _DICT_KEY_ID: self.id,
            _DICT_KEY_METADATA: self.metadata,
            _DICT_KEY_CONTENT: self.content,
            _DICT_KEY_SUMMARY: self.summary,
        }
