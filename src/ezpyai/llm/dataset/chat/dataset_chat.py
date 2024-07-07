from typing import List, Dict


class DatasetChatEntry:
    def __init__(self, role: str, content: str) -> None:
        self.role: str = role
        self.content: str = content

    def __str__(self) -> str:
        return f"{self.role}: {self.content}"

    def to_sharegpt_format(self) -> Dict[str, str]:

        return {"from": self.role, "value": self.content}


class DatasetChat:
    def __init__(
        self,
        system_message: str | None = None,
        entries: List[DatasetChatEntry] | None = None,
    ) -> None:
        if system_message is None:
            system_message = ""

        self.system_message: str = system_message

        if entries is None:
            entries = []

        self.entries: List[DatasetChatEntry] = entries

    def add_entry(self, role: str, content: str) -> None:
        self.entries.append(DatasetChatEntry(role=role, content=content))

    def to_sharegpt_format(self) -> List[Dict[str, str]]:
        return [entry.to_sharegpt_format() for entry in self.entries]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: system_message={self.system_message}, num_entries={len(self.entries)}"
