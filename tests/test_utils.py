"""Tests for utilities."""

import pytest
from datetime import datetime
from decimal import Decimal

from utils.cache import SimpleCache
from utils.validators import validate_price_data, validate_exchange_data, validate_sentiment_data
from utils.helpers import format_decimal, parse_timestamp, truncate_string


class TestSimpleCache:
    """Test caching utilities."""

    def test_cache_set_and_get(self):
        """Test cache set and get."""
        cache = SimpleCache(ttl_seconds=60)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_expiration(self):
        """Test cache expiration."""
        import time

        cache = SimpleCache(ttl_seconds=1)
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = SimpleCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_cleanup_expired(self):
        """Test cleaning up expired entries."""
        import time

        cache = SimpleCache(ttl_seconds=1)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        time.sleep(1.1)

        removed = cache.cleanup_expired()
        assert removed == 2


class TestValidators:
    """Test data validators."""

    def test_validate_price_data_valid(self):
        """Test validating valid price data."""
        data = {
            "close_price": 100.50,
            "open_price": 99.00,
            "high_price": 102.00,
            "low_price": 98.00,
        }

        assert validate_price_data(data) is True

    def test_validate_price_data_missing_field(self):
        """Test validating price data with missing field."""
        data = {
            "close_price": 100.50,
            "open_price": 99.00,
            "high_price": 102.00,
            # Missing low_price
        }

        assert validate_price_data(data) is False

    def test_validate_price_data_negative(self):
        """Test validating price data with negative price."""
        data = {
            "close_price": -100.50,
            "open_price": 99.00,
            "high_price": 102.00,
            "low_price": 98.00,
        }

        assert validate_price_data(data) is False

    def test_validate_exchange_data_valid(self):
        """Test validating valid exchange data."""
        data = {"name": "Binance"}

        assert validate_exchange_data(data) is True

    def test_validate_exchange_data_invalid(self):
        """Test validating exchange data without name."""
        data = {}

        assert validate_exchange_data(data) is False

    def test_validate_sentiment_data_valid(self):
        """Test validating valid sentiment data."""
        data = {
            "sentiment_score": 0.5,
            "sentiment_label": "positive",
            "mentions_count": 1000,
        }

        assert validate_sentiment_data(data) is True

    def test_validate_sentiment_data_out_of_range(self):
        """Test validating sentiment score out of range."""
        data = {
            "sentiment_score": 1.5,  # > 1.0
            "sentiment_label": "positive",
            "mentions_count": 1000,
        }

        assert validate_sentiment_data(data) is False


class TestHelpers:
    """Test helper functions."""

    def test_format_decimal(self):
        """Test decimal formatting."""
        value = Decimal("123.456789")
        formatted = format_decimal(value, places=2)
        assert formatted == "123.46"

    def test_format_decimal_none(self):
        """Test formatting None value."""
        formatted = format_decimal(None)
        assert formatted == "N/A"

    def test_parse_timestamp_iso(self):
        """Test parsing ISO format timestamp."""
        iso_str = "2023-01-15T10:30:00+00:00"
        timestamp = parse_timestamp(iso_str)
        assert timestamp is not None
        assert isinstance(timestamp, datetime)

    def test_parse_timestamp_with_z(self):
        """Test parsing ISO format with Z suffix."""
        iso_str = "2023-01-15T10:30:00Z"
        timestamp = parse_timestamp(iso_str)
        assert timestamp is not None

    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        result = parse_timestamp("invalid")
        assert result is None

    def test_truncate_string(self):
        """Test string truncation."""
        text = "This is a very long text that needs truncation"
        truncated = truncate_string(text, max_length=20)
        assert len(truncated) <= 20
        assert truncated.endswith("...")

    def test_truncate_string_short(self):
        """Test truncating short string."""
        text = "Short"
        truncated = truncate_string(text, max_length=20)
        assert truncated == "Short"
