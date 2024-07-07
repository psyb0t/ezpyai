from typing import Any


class UnsupportedModelError(Exception):
    """Exception raised when an unsupported model is used."""

    def __init__(self, message: str = "Unsupported model", *args: Any) -> None:
        super().__init__(message, *args)


class UnsupportedLoraError(Exception):
    """Exception raised when an unsupported lora is used."""

    def __init__(self, message: str = "Unsupported lora", *args: Any):
        super().__init__(message, *args)
