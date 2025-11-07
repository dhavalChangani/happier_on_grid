"""OnGrid exception classes"""


class OnGridException(Exception):
    """Base exception for OnGrid operations"""

    pass


class ValidationException(OnGridException):
    """Validation error exception"""

    pass
