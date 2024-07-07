import os
import json
from typing import List, Dict, Any
from datetime import datetime

from ezpyai._logger import logger
from ezpyai.exceptions import FileNotFoundError, JSONParseError
from ezpyai.constants import (
    DICT_KEY_CHATS,
    DICT_KEY_LIST,
    DICT_KEY_TYPE,
    DICT_KEY_ID,
    DICT_KEY_NAME,
    DICT_KEY_MESSAGES,
    DICT_KEY_DATE_UNIXTIME,
    DICT_KEY_TEXT,
    DICT_KEY_TEXT_ENTITIES,
    DICT_KEY_FROM,
    DICT_KEY_FROM_ID,
    NAME_UNKNOWN,
    CHAT_ID_TELEGRAM,
)

_TELEGRAM_CHAT_TYPE_PERSONAL: str = "personal_chat"
_TELEGRAM_MESSAGE_TYPE_MESSAGE: str = "message"


# dict_keys(['id', 'type', 'date', 'date_unixtime', 'from', 'from_id', 'text', 'text_entities'])
class _TelegramChatMessage:
    def __init__(
        self,
        message_id: str,
        message_type: str,
        message_date_unixtime: int,
        message_from_name: str,
        message_from_id: str,
        message_text: str,
    ):
        self.id: str = message_id
        self.type: str = message_type
        self.date: datetime = datetime.fromtimestamp(message_date_unixtime)
        self.date_unixtime: int = message_date_unixtime
        self.from_name: str = message_from_name
        self.from_id: str = message_from_id
        self.text: str = message_text

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.to_dict()}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "date_unixtime": self.date_unixtime,
            "from": self.from_name,
            "from_id": self.from_id,
            "text": self.text,
        }


class _TelegramChat:
    def __init__(
        self,
        chat_id: int,
        chat_name: str,
        chat_messages: List[_TelegramChatMessage],
    ) -> None:
        self.id: int = chat_id
        self.name: str = chat_name
        self.messages: List[_TelegramChatMessage] = chat_messages

    def __str__(self) -> str:
        dict_repr = self.to_dict()
        dict_repr["num_messages"] = len(dict_repr["messages"])
        dict_repr.pop("messages")

        return f"{self.__class__.__name__}: {dict_repr}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "messages": [message.to_dict() for message in self.messages],
        }


class DatasetSourceTelegram:
    def __init__(
        self,
        json_export_file_path: str,
        assistant_from_id: str,
    ) -> None:
        logger.debug(f"initializing {self.__class__.__name__}")

        if not os.path.exists(json_export_file_path):
            raise FileNotFoundError(f"File not found: {json_export_file_path}")

        self._json_export_file_path: str = json_export_file_path
        self._assistant_from_id: str = assistant_from_id
        self._chats: List[_TelegramChat] = []

        self._parse_json_export_file()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(json_export_file_path={self._json_export_file_path}, assistant_from_id={self._assistant_from_id}, entries={len(self._chats)})"

    def get_chats(
        self,
        with_zero_messages: bool = True,
    ) -> List[_TelegramChat]:
        if with_zero_messages:
            return self._chats

        return [chat for chat in self._chats if len(chat.messages) > 0]

    def _parse_json_export_file(self):
        logger.debug(f"parsing Telegram export file: {self._json_export_file_path}")

        with open(self._json_export_file_path, "r", encoding="utf-8") as f:
            data: Dict[Any, Any] = json.load(f)

        if DICT_KEY_CHATS not in data:
            raise JSONParseError(
                f"Missing key '{DICT_KEY_CHATS}' in telegram export file JSON data (File: {self._json_export_file_path})"
            )

        if DICT_KEY_LIST not in data[DICT_KEY_CHATS]:
            raise JSONParseError(
                f"Missing key '{DICT_KEY_LIST}' in telegram export file JSON data[{DICT_KEY_CHATS}] (File: {self._json_export_file_path})"
            )

        self._process_chats(data[DICT_KEY_CHATS][DICT_KEY_LIST])

        logger.debug(f"parsed {len(self._chats)} chats")

    def _process_chats(self, chats: List[Dict[Any, Any]]):
        logger.debug(f"processing {len(chats)} chats")

        for chat in chats:
            if not self._is_valid_chat(chat):
                logger.debug(f"invalid chat: {chat}")

                continue

            if chat[DICT_KEY_ID] == CHAT_ID_TELEGRAM:
                continue

            if chat[DICT_KEY_TYPE] != _TELEGRAM_CHAT_TYPE_PERSONAL:
                continue

            self._chats.append(self._get_processed_chat(chat))

    def _is_valid_chat(self, chat: Dict[str, Any]) -> bool:
        logger.debug(f"validating chat: {chat}")

        if DICT_KEY_TYPE not in chat:
            return False

        if DICT_KEY_ID not in chat:
            return False

        if DICT_KEY_NAME not in chat:
            return False

        if DICT_KEY_MESSAGES not in chat:
            return False

        return True

    def _get_processed_chat(self, chat: Dict[str, Any]) -> _TelegramChat:
        logger.debug(f"getting processed _TelegramChat from chat: {chat}")

        chat_id: int = int(chat[DICT_KEY_ID])

        chat_name: str = NAME_UNKNOWN
        if chat[DICT_KEY_NAME] is not None:
            chat_name = str(chat[DICT_KEY_NAME])

        chat_messages: List[Dict[str, Any]] = chat[DICT_KEY_MESSAGES]
        telegram_chat_messages: List[_TelegramChatMessage] = (
            self._get_processed_messages(chat_messages)
        )

        return _TelegramChat(chat_id, chat_name, telegram_chat_messages)

    def _get_processed_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[_TelegramChatMessage]:
        logger.debug(f"processing {len(messages)} messages")

        telegram_chat_messages: List[_TelegramChatMessage] = []

        for message in messages:
            if not self._is_valid_message(message):
                logger.debug(f"invalid message: {message}")
                continue

            telegram_chat_messages.append(self._get_processed_message(message))

        logger.debug(f"processed {len(telegram_chat_messages)} messages")

        return telegram_chat_messages

    def _is_valid_message(self, message: Dict[str, Any]) -> bool:
        logger.debug(f"validating message: {message}")

        if DICT_KEY_ID not in message:
            return False

        if DICT_KEY_TYPE not in message:
            return False

        if message[DICT_KEY_TYPE] != _TELEGRAM_MESSAGE_TYPE_MESSAGE:
            return False

        if DICT_KEY_DATE_UNIXTIME not in message:
            return False

        if DICT_KEY_FROM not in message:
            return False

        if DICT_KEY_FROM_ID not in message:
            return False

        if DICT_KEY_TEXT_ENTITIES not in message:
            return False

        return True

    def _get_processed_message(self, message: Dict[str, Any]) -> _TelegramChatMessage:
        logger.debug(f"getting processed _TelegramChatMessage from message: {message}")

        message_id: str = str(message[DICT_KEY_ID])
        message_type: str = str(message[DICT_KEY_TYPE])

        message_date_unixtime: int = 0
        try:
            message_date_unixtime = int(message[DICT_KEY_DATE_UNIXTIME])
        except ValueError:
            pass

        message_from_name: str = NAME_UNKNOWN
        if message[DICT_KEY_FROM] is not None:
            message_from_name = message[DICT_KEY_FROM]

        message_from_id: str = str(message[DICT_KEY_FROM_ID])
        message_text: str = "".join(
            [
                text_entity[DICT_KEY_TEXT]
                for text_entity in message[DICT_KEY_TEXT_ENTITIES]
            ]
        )

        return _TelegramChatMessage(
            message_id,
            message_type,
            message_date_unixtime,
            message_from_name,
            message_from_id,
            message_text,
        )
