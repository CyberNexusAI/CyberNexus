from fastapi import status
from typing import Any
import logging

# Get logger
logger = logging.getLogger(__name__)

# Custom exception classes
class AppException(Exception):
    """Base application exception class"""
    def __init__(
        self, 
        message: str = "An error occurred", 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: Any = None
    ):
        self.message = message
        self.status_code = status_code
        self.data = data
        logger.error("AppException: %s (code: %d)", message, status_code)
        super().__init__(self.message)


class ResourceNotFoundException(AppException):
    """Resource not found exception"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    """Bad request exception"""
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)
