from abc import ABC, abstractmethod
from typing import List

from ezpyai.llm.conversation import Conversation


class DatasetSource(ABC):
    @abstractmethod
    def to_conversations(self, system_message_tpl: str) -> List[Conversation]:
        pass
