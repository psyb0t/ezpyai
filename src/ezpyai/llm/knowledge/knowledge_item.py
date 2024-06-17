import logging

from typing import Dict
from ezpyai.llm.prompt import Prompt, SUMMARIZER_SYSTEM_MESSAGE
from ezpyai.llm._llm import LLM


class KnowledgeItem:
    """
    A class to store knowledge data.

    Attributes:
        metadata (Dict[str, str]): The metadata of the knowledge item.
        content (str): The content of the knowledge item.
        summary (str): The summary of the knowledge item's content.
    """

    def __init__(self, content: str, metadata: Dict[str, str] = None):
        if metadata is None:
            metadata = {}

        self.metadata = metadata
        self.content = content
        self.summary = ""

    def __str__(self):
        return f"{self.__class__.__name__}(metadata={self.metadata}, content={self.content}, summary={self.summary})"

    def summarize(self, summarizer: LLM) -> str:
        logging.debug(
            f"Summarizing content {self.content} with metadata {self.metadata}"
        )

        prompt: Prompt = Prompt(
            system_message=SUMMARIZER_SYSTEM_MESSAGE,
            user_message=f"Summarize the following text: {self.content}",
        )

        self.summary = summarizer.get_structured_response(
            prompt, response_format={"summary": ""}
        )["summary"]

        return self.summary
