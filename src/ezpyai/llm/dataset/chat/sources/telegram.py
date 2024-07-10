import os
import json
import re

from typing import List, Dict, Any, Tuple, Match
from datetime import datetime
from jinja2 import Template

from ezpyai._logger import logger
from ezpyai.exceptions import FileNotFoundError, JSONParseError
from ezpyai.llm.dataset.chat.sources._dataset_source import DatasetSource
from ezpyai.llm.conversation import Message, Conversation

from ezpyai.constants import (
    DICT_KEY_CHATS,
    DICT_KEY_LIST,
    DICT_KEY_TYPE,
    DICT_KEY_ID,
    DICT_KEY_NAME,
    DICT_KEY_MESSAGES,
    DICT_KEY_NUM_MESSAGES,
    DICT_KEY_DATE,
    DICT_KEY_DATE_UNIXTIME,
    DICT_KEY_TEXT,
    DICT_KEY_TEXT_ENTITIES,
    DICT_KEY_FROM,
    DICT_KEY_FROM_ID,
    NAME_UNKNOWN,
    CHAT_ID_TELEGRAM,
    CHAT_ROLE_USER,
    CHAT_ROLE_ASSISTANT,
)

_TELEGRAM_CHAT_TYPE_PERSONAL: str = "personal_chat"
_TELEGRAM_MESSAGE_TYPE_MESSAGE: str = "message"


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
            DICT_KEY_ID: self.id,
            DICT_KEY_TYPE: self.type,
            DICT_KEY_DATE: self.date,
            DICT_KEY_DATE_UNIXTIME: self.date_unixtime,
            DICT_KEY_FROM: self.from_name,
            DICT_KEY_FROM_ID: self.from_id,
            DICT_KEY_TEXT: self.text,
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
        dict_repr[DICT_KEY_NUM_MESSAGES] = len(dict_repr[DICT_KEY_MESSAGES])
        dict_repr.pop(DICT_KEY_MESSAGES)

        return f"{self.__class__.__name__}: {dict_repr}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            DICT_KEY_ID: self.id,
            DICT_KEY_NAME: self.name,
            DICT_KEY_MESSAGES: [message.to_dict() for message in self.messages],
        }


class DatasetSourceTelegram(DatasetSource):
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

    def _get_chats(
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

        if len(message[DICT_KEY_TEXT_ENTITIES]) == 0:
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

    def limit_repeats(
        self,
        text: str,
        max_repeats: int = 3,
        min_repetitions_before_limiting: int = 5,
    ) -> str:
        def replace_func(match: Match[str]) -> str:
            char = match.group(1)
            return char * min(
                len(match.group(0)), min_repetitions_before_limiting - 1 + max_repeats
            )

        pattern = rf"(.)(\1{{{min_repetitions_before_limiting-1},}})"
        return re.sub(pattern, replace_func, text)

    def to_conversations(
        self,
        system_message_tpl: str = "",
        replace_rules: List[Tuple[str, str]] = [],
        max_character_repeats: int = 0,
        min_repetitions_before_limiting: int = 0,
    ) -> List[Conversation]:
        conversations: List[Conversation] = []
        chats = self._get_chats(with_zero_messages=False)

        for chat in chats:
            conversation_messages: List[Message] = []
            system_message: str = ""

            if system_message_tpl:
                user_message: _TelegramChatMessage | None = (
                    self._get_user_message_from_chat(chat)
                )
                if user_message:
                    template = Template(system_message_tpl)
                    system_message = template.render(chat=chat, message=user_message)

            last_role: str | None = None
            for message in chat.messages:
                role: str = CHAT_ROLE_USER
                if message.from_id == self._assistant_from_id:
                    role = CHAT_ROLE_ASSISTANT

                content = message.text.strip()

                # Apply replace rules
                for pattern, replacement in replace_rules:
                    content = re.sub(pattern, replacement, content)

                if content:
                    if (
                        max_character_repeats > 0
                        and min_repetitions_before_limiting > 0
                    ):
                        content = self.limit_repeats(
                            content,
                            max_repeats=max_character_repeats,
                            min_repetitions_before_limiting=min_repetitions_before_limiting,
                        )

                    if role == last_role and conversation_messages:
                        # Append the current message text to the previous message's content
                        # separated by a newline
                        conversation_messages[-1].content += f"\n{content}"
                    else:
                        # Add a new message if the role is different
                        conversation_messages.append(
                            Message(role=role, content=content)
                        )
                    last_role = role

            conversations.append(
                Conversation(
                    system_message=system_message,
                    messages=conversation_messages,
                )
            )

        return conversations

    def _get_user_message_from_chat(
        self, chat: _TelegramChat
    ) -> _TelegramChatMessage | None:
        for message in chat.messages:
            if message.from_id != self._assistant_from_id:
                return message

        return None
