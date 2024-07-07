import json
from typing import List, Dict
from ezpyai.constants import (
    DICT_KEY_ROLE,
    DICT_KEY_CONTENT,
    DICT_KEY_VALUE,
    DICT_KEY_FROM,
    CHAT_ROLE_SYSTEM,
)


class Message:
    def __init__(self, role: str, content: str) -> None:
        self.role: str = role
        self.content: str = content

    def __str__(self) -> str:
        return f"{self.role}: {self.content}"

    def to_dict(self) -> Dict[str, str]:
        return {DICT_KEY_ROLE: self.role, DICT_KEY_CONTENT: self.content}

    def to_sharegpt_format(self) -> Dict[str, str]:
        return {DICT_KEY_FROM: self.role, DICT_KEY_VALUE: self.content}


class Conversation:
    def __init__(
        self,
        system_message: str | None = None,
        messages: List[Message] | None = None,
    ) -> None:
        if system_message is None:
            system_message = ""

        self.system_message: str = system_message

        if messages is None:
            messages = []

        self.messages: List[Message] = messages

    def add_entry(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def split(self, max_messages_per_split: int) -> List["Conversation"]:
        if max_messages_per_split <= 0:
            raise ValueError("max_messages_per_split must be a positive integer")

        # no, I didn't wanna do it the pythonic way, I wanted to keep it clear for all
        conversations: List[Conversation] = []

        for i in range(0, len(self.messages), max_messages_per_split):
            messages: List[Message] = self.messages[i : i + max_messages_per_split]
            conversations.append(Conversation(self.system_message, messages))

        return conversations

    def split_with_overlap(
        self,
        max_messages_per_split: int,
        num_overlapping_messages: int,
    ) -> List["Conversation"]:
        if max_messages_per_split <= 0:
            raise ValueError("max_messages_per_split must be a positive integer")
        if num_overlapping_messages < 0:
            raise ValueError("num_overlapping_messages must be a non-negative integer")
        if num_overlapping_messages >= max_messages_per_split:
            raise ValueError(
                "num_overlapping_messages must be less than max_messages_per_split"
            )

        conversations: List[Conversation] = []
        start = 0
        while start < len(self.messages):
            end = min(start + max_messages_per_split, len(self.messages))
            messages: List[Message] = self.messages[start:end]
            conversations.append(Conversation(self.system_message, messages))
            if end == len(self.messages):
                break

            start = max(start + 1, end - num_overlapping_messages)

        return conversations

    def to_dict_list(self) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if self.system_message:
            messages.append(
                Message(role=CHAT_ROLE_SYSTEM, content=self.system_message).to_dict()
            )

        for message in self.messages:
            messages.append(message.to_dict())

        return messages

    def to_json(self, pretty_print: bool = False) -> str:
        if pretty_print:
            return json.dumps(self.to_dict_list(), indent=4)

        return json.dumps(self.to_dict_list())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: system_message={self.system_message}, num_messages={len(self.messages)}"
