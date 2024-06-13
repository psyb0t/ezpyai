GENERIC_SYSTEM_MESSAGE = "You are a helpful AI assistant."


class Prompt:
    _system_message: str = ""
    _context: str = ""
    _user_message: str = ""

    def __init__(
        self,
        user_message: str,
        system_message: str = "",
        context: str = "",
    ) -> None:
        self._system_message = system_message
        self._context = context
        self._user_message = user_message

    def __str__(self) -> str:
        return f"Prompt(system_message={self._system_message}, context={self._context}, user_message={self._user_message})"

    def has_system_message(self) -> bool:
        return bool(self._system_message)

    def get_system_message(self) -> str:
        return self._system_message

    def has_context(self) -> bool:
        return bool(self._context)

    def get_context(self) -> str:
        return self._context

    def has_user_message(self) -> bool:
        return bool(self._user_message)

    def get_user_message(self) -> str:
        return self._user_message
