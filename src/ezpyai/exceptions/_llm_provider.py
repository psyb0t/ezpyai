# LLMProvider Exceptions
class UnsupportedModelError(Exception):
    """Exception raised when an unsupported model is used."""

    def __init__(self, message="Unsupported model", *args):
        super().__init__(message, *args)


class UnsupportedLoraError(Exception):
    """Exception raised when an unsupported lora is used."""

    def __init__(self, message="Unsupported lora", *args):
        super().__init__(message, *args)
