class PromptUserMessageMissingError(Exception):
    """Exception raised when there is no user message in the prompt."""

    def __init__(self, message="Prompt user message missing", *args):
        super().__init__(message, *args)


class LLMResponseEmptyError(Exception):
    """Exception raised when there is no LLM response message."""

    def __init__(self, message="LLM response empty", *args):
        super().__init__(message, *args)


class LLMInferenceError(Exception):
    """Exception raised when there is an error during the LLM inference."""

    def __init__(self, message="LLM inference error", *args):
        super().__init__(message, *args)
