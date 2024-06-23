from typing import List
from abc import ABC, abstractmethod
from ezpyai.llm.providers._llm_provider import LLMProvider
from ezpyai.llm.knowledge.knowledge_item import KnowledgeItem


class KnowledgeDB(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_dsn(self) -> str:
        pass

    @abstractmethod
    def destroy(self) -> None:
        pass

    @abstractmethod
    def store(self, collection: str, data_path: str) -> None:
        pass

    @abstractmethod
    def search(self, collection: str, query: str) -> List[KnowledgeItem]:
        pass


class BaseKnowledgeDB(KnowledgeDB):
    def __init__(self, name: str, dsn: str) -> None:
        self._name = name
        self._dsn = dsn

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name}, dsn={self._dsn})"

    def get_name(self) -> str:
        return self._name

    def get_dsn(self) -> str:
        return self._dsn

    def destroy(self) -> None:
        pass

    def store(
        self,
        collection: str,
        data_path: str,
        summarizer: LLMProvider = None,
    ) -> None:
        pass

    def search(
        self,
        collection: str,
        query: str,
    ) -> List[KnowledgeItem]:
        pass
