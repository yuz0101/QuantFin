class Error(Exception):
    """Base class for other exceptions"""

class InputError(Error):
    """Raised when the input is wrong"""

class UnkownError(Error):
    """Raised unknown exceptions"""

class QueryError(Error):
    """Invalidate Query"""