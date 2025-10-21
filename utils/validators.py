"""Data validation utilities."""

from decimal import Decimal
from typing import Any, Dict

import structlog

logger = structlog.get_logger(__name__)


def validate_price_data(data: Dict[str, Any]) -> bool:
    """Validate price data structure.

    Args:
        data: Price data dictionary

    Returns:
        True if valid
    """
    required_fields = {"close_price", "open_price", "high_price", "low_price"}
    
    if not all(field in data for field in required_fields):
        logger.error("invalid_price_data", missing_fields=required_fields - set(data.keys()))
        return False

    try:
        for field in required_fields:
            value = Decimal(str(data[field]))
            if value < 0:
                logger.error("negative_price", field=field, value=value)
                return False
    except (ValueError, TypeError) as e:
        logger.error("price_conversion_error", error=str(e))
        return False

    return True


def validate_exchange_data(data: Dict[str, Any]) -> bool:
    """Validate exchange data structure.

    Args:
        data: Exchange data dictionary

    Returns:
        True if valid
    """
    required_fields = {"name"}
    
    if not all(field in data for field in required_fields):
        logger.error("invalid_exchange_data", missing_fields=required_fields - set(data.keys()))
        return False

    if not data["name"] or not isinstance(data["name"], str):
        logger.error("invalid_exchange_name")
        return False

    return True


def validate_sentiment_data(data: Dict[str, Any]) -> bool:
    """Validate sentiment data structure.

    Args:
        data: Sentiment data dictionary

    Returns:
        True if valid
    """
    required_fields = {"sentiment_score", "sentiment_label", "mentions_count"}
    
    if not all(field in data for field in required_fields):
        logger.error("invalid_sentiment_data", missing_fields=required_fields - set(data.keys()))
        return False

    try:
        score = float(data["sentiment_score"])
        if not -1.0 <= score <= 1.0:
            logger.error("sentiment_score_out_of_range", score=score)
            return False
    except (ValueError, TypeError) as e:
        logger.error("sentiment_score_error", error=str(e))
        return False

    if not isinstance(data["mentions_count"], int) or data["mentions_count"] < 0:
        logger.error("invalid_mentions_count")
        return False

    return True
