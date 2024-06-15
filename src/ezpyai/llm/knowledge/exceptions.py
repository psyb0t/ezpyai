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
