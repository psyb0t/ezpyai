from typing import Dict


class KnowledgeItem:
    """
    A class to store knowledge data.

    Attributes:
        metadata (Dict[str, str]): The metadata of the knowledge item.
        content (str): The content of the knowledge item.
    """

    metadata: Dict[str, str]
    content: str
    summary: str  # TODO: implement summarization using uncensored open-source model

    def __init__(self, content: str, metadata: Dict[str, str]):
        self.content = content
        self.metadata = metadata

    def __str__(self):
        return f"KnowledgeItem(metadata={self.metadata}, content length={len(self.content)})"
