class NoUserMessage(Exception):
    """Exception raised when there is no user message."""

    def __init__(self, message="No user message", *args):
        super().__init__(message, *args)


class NoLLMResponseMessage(Exception):
    """Exception raised when there is no response from the LLM."""

    def __init__(self, message="No LLM response message", *args):
        super().__init__(message, *args)


class InvokeError(Exception):
    """Exception raised when an invocation error occurs."""

    def __init__(self, message="Invocation error", *args):
        super().__init__(message, *args)
