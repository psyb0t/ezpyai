from typing import List


class DatasetChatEntry:
    def __init__(self, role: str, content: str) -> None:
        self.role: str = role
        self.content: str = content

    def __str__(self) -> str:
        return f"{self.role}: {self.content}"


class DatasetChat:
    def __init__(self, entries: List[DatasetChatEntry] | None = None) -> None:
        if entries is None:
            entries = []

        self.entries: List[DatasetChatEntry] = entries

    def add_entry(self, role: str, content: str) -> None:
        self.entries.append(DatasetChatEntry(role=role, content=content))
