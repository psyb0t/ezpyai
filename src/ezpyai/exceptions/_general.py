class JSONParseError(Exception):
    """Exception raised when a JSON parse error occurs."""

    def __init__(self, message="JSON parse error", *args):
        super().__init__(message, *args)


class FileReadError(Exception):
    """Exception raised when there is an error reading a file."""

    def __init__(self, message="Error reading file", *args):
        super().__init__(message, *args)


class UnsupportedFileTypeError(Exception):
    """Exception raised when attempting to process an unsupported file type."""

    def __init__(self, message="Unsupported file type", *args):
        super().__init__(message, *args)


class FileProcessingError(Exception):
    """Exception raised for any errors during the file processing."""

    def __init__(self, message="Error during file processing", *args):
        super().__init__(message, *args)


class FileNotFoundError(Exception):
    """Exception raised when a file is not found."""

    def __init__(self, message="File not found", *args):
        super().__init__(message, *args)
