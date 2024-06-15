from typing import List
from ezpyai.llm.knowledge.knowledge_item import KnowledgeItem


class BaseKnowledge:
    _name: str = None
    _dsn: str = None

    def __init__(self, name: str, dsn: str) -> None:
        self._name = name
        self._dsn = dsn

    def __str__(self) -> str:
        return f"BaseKnowledge(name={self._name}, dsn={self._dsn})"

    def get_name(self) -> str:
        return self._name

    def get_dsn(self) -> str:
        return self._dsn

    def destroy(self) -> None:
        pass

    def store(self, collection: str, data_path: str) -> None:
        pass

    def search(self, collection: str, query: str) -> List[KnowledgeItem]:
        pass
