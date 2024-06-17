from typing import List

GENERIC_SYSTEM_MESSAGE = "You are a helpful AI assistant."
SUMMARIZER_SYSTEM_MESSAGE = """You are a summarizer AI assistant.
whenever a human gives you a chunk of text, you will respond with a summary of the text."""


class Prompt:
    def __init__(
        self,
        user_message: str,
        system_message: str = None,
        context: List[str] = None,
    ) -> None:
        if system_message is None:
            system_message = ""

        if context is None:
            context = []

        self._user_message = user_message
        self._system_message = system_message
        self._context = context

    def __str__(self) -> str:
        return f"Prompt(system_message={self._system_message}, context={self._context}, user_message={self._user_message})"

    def has_system_message(self) -> bool:
        return bool(self._system_message)

    def get_system_message(self) -> str:
        return self._system_message

    def set_system_message(self, system_message: str) -> None:
        self._system_message = system_message

    def has_context(self) -> bool:
        return bool(self._context)

    def get_context(self) -> str:
        return self._context

    def get_context_as_string(self) -> str:
        return "\n".join(self._context)

    def set_context(self, context: List[str]) -> None:
        self._context = context

    def add_context(self, context: str) -> None:
        self._context.append(context)

    def has_user_message(self) -> bool:
        return bool(self._user_message)

    def get_user_message(self) -> str:
        return self._user_message

    def set_user_message(self, user_message: str) -> None:
        self._user_message = user_message
