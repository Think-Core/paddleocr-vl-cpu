"""
Base formatter class for OCR output formats.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseFormatter(ABC):
    """Abstract base class for all output formatters."""

    @abstractmethod
    def format(self, text: str, image_width: int = None, image_height: int = None, **kwargs) -> str:
        """
        Format the OCR text output.

        Args:
            text: The raw OCR text output
            image_width: Optional width of the source image
            image_height: Optional height of the source image
            **kwargs: Additional formatter-specific parameters

        Returns:
            Formatted output string
        """
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """
        Get the MIME content type for this format.

        Returns:
            Content type string (e.g., 'text/html', 'application/json')
        """
        pass
