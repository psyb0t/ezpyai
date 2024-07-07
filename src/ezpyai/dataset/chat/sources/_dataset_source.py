from abc import ABC, abstractmethod
from typing import List

from ezpyai.dataset.chat import DatasetChat


class DatasetSource(ABC):
    @abstractmethod
    def to_dataset_chats(self, system_message_tpl: str) -> List[DatasetChat]:
        pass
