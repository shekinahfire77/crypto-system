"""Helper utility functions."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Optional


def format_decimal(value: Any, places: int = 2) -> str:
    """Format decimal value to string.

    Args:
        value: Value to format
        places: Decimal places

    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"

    try:
        decimal_value = Decimal(str(value))
        return f"{decimal_value:.{places}f}"
    except (ValueError, TypeError):
        return str(value)


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO format timestamp string.

    Args:
        timestamp_str: ISO format timestamp

    Returns:
        datetime object or None
    """
    try:
        # Handle various ISO formats
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str.replace("Z", "+00:00")

        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return None


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    *args,
    **kwargs,
) -> Any:
    """Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        backoff_factor: Exponential backoff factor
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result
    """
    import time

    last_exception = None

    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)

    if last_exception:
        raise last_exception

    return None
