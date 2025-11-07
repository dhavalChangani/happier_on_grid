"""OnGrid exception classes"""

from typing import Any, Dict, Optional


class OnGridException(Exception):
    """Base exception for OnGrid operations"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize OnGrid exception.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: API response data if applicable
        """
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of exception"""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class ValidationException(OnGridException):
    """Validation error exception"""

    def __init__(
        self, message: str, field_errors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize validation exception.

        Args:
            message: Error message
            field_errors: Dictionary mapping field names to error messages
        """
        self.field_errors = field_errors or {}
        super().__init__(message, status_code=400)

    def __str__(self) -> str:
        """Return string representation with field errors"""
        if self.field_errors:
            errors = "\n".join(f"  - {field}: {error}" for field, error in self.field_errors.items())
            return f"{self.message}\n{errors}"
        return self.message


class APIException(OnGridException):
    """API request/response exception"""

    pass


class AuthenticationException(OnGridException):
    """Authentication/authorization exception"""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize authentication exception"""
        super().__init__(message, status_code=401)


class NetworkException(OnGridException):
    """Network/connection exception"""

    pass
