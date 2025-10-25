"""
Output formatters for OCR results.

This module provides different output format options for OCR text,
including HOCR, plain text, and other structured formats.
"""
from .base import BaseFormatter
from .hocr import HOCRFormatter


# Formatter registry
FORMATTERS = {
    'hocr': HOCRFormatter,
}


def get_formatter(format_name: str) -> BaseFormatter:
    """
    Get a formatter instance by name.

    Args:
        format_name: Name of the formatter ('hocr', etc.)

    Returns:
        Formatter instance

    Raises:
        ValueError: If format_name is not recognized
    """
    if format_name not in FORMATTERS:
        available = ', '.join(FORMATTERS.keys())
        raise ValueError(
            f"Unknown format '{format_name}'. "
            f"Available formats: {available}"
        )

    formatter_class = FORMATTERS[format_name]
    return formatter_class()


__all__ = [
    'BaseFormatter',
    'HOCRFormatter',
    'get_formatter',
    'FORMATTERS',
]
