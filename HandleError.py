class Error(Exception):
    """Base class for other exceptions"""
    pass

class InputError(Error):
    """Raised when the input is wrong"""
    pass

class UnkownError(Error):
    """Raised unknown exceptions"""
    pass