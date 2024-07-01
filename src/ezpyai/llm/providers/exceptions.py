class UnsupportedModelError(Exception):
    """Exception raised when an unsupported model is used."""

    def __init__(self, message="Unsupported model", *args):
        super().__init__(message, *args)
