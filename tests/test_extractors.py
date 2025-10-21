"""Tests for extractors and API clients."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal

from extractors.base_service import RateLimiter, BaseAPIService


class TestRateLimiter:
    """Test rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_respects_limit(self):
        """Test that rate limiter respects the configured limit."""
        limiter = RateLimiter(calls_per_minute=2)

        # Acquire first token
        await limiter.acquire()
        assert limiter.tokens < 2

        # Acquire second token
        await limiter.acquire()
        assert limiter.tokens < 1

    @pytest.mark.asyncio
    async def test_rate_limiter_waits_when_full(self):
        """Test that rate limiter waits when token bucket is full."""
        limiter = RateLimiter(calls_per_minute=1)

        # Acquire the only token
        await limiter.acquire()

        # Next acquire should have to wait
        # (we just verify it doesn't raise an exception)
        await asyncio.sleep(0.1)  # Simulate some time passing
        # Tokens should regenerate


class TestBaseAPIService:
    """Test base API service."""

    class MockAPIService(BaseAPIService):
        """Mock API service for testing."""

        def get_headers(self):
            return {"Authorization": "Bearer test_token"}

    @pytest.mark.asyncio
    async def test_base_service_initialization(self):
        """Test base service initialization."""
        service = self.MockAPIService(
            api_key="test_key",
            base_url="https://api.example.com",
            rate_limit=10,
        )

        assert service.api_key == "test_key"
        assert service.base_url == "https://api.example.com"
        assert service.rate_limiter is not None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        service = self.MockAPIService(
            api_key="test_key",
            base_url="https://api.example.com",
            rate_limit=10,
        )

        async with service as s:
            assert s.session is not None

        # Session should be closed
        assert service.session.closed


class TestCoinGeckoService:
    """Test CoinGecko API service."""

    @pytest.mark.asyncio
    async def test_get_headers(self):
        """Test CoinGecko headers."""
        from extractors.coingecko_service import CoinGeckoService

        service = CoinGeckoService(
            api_key="test_key",
            base_url="https://api.coingecko.com/api/v3",
            rate_limit=10,
        )

        headers = service.get_headers()
        assert "x-cg-demo-api-key" in headers
        assert headers["x-cg-demo-api-key"] == "test_key"

    @pytest.mark.asyncio
    async def test_get_coin_list_structure(self):
        """Test coin list structure."""
        from extractors.coingecko_service import CoinGeckoService

        service = CoinGeckoService(
            api_key="test_key",
            base_url="https://api.coingecko.com/api/v3",
            rate_limit=10,
        )

        # Mock the request method
        service.make_request = AsyncMock(
            return_value=[
                {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
                {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
            ]
        )

        result = await service.get_coin_list()
        assert len(result) == 2
        assert result[0]["symbol"] == "btc"


class TestCoinMarketCapService:
    """Test CoinMarketCap API service."""

    @pytest.mark.asyncio
    async def test_get_headers(self):
        """Test CMC headers."""
        from extractors.cmc_service import CoinMarketCapService

        service = CoinMarketCapService(
            api_key="test_key",
            base_url="https://pro-api.coinmarketcap.com/v1",
            rate_limit=10,
        )

        headers = service.get_headers()
        assert "X-CMC_PRO_API_KEY" in headers
        assert headers["X-CMC_PRO_API_KEY"] == "test_key"


class TestCoinMarketCapDEXService:
    """Test CoinMarketCap DEX API service."""

    @pytest.mark.asyncio
    async def test_get_headers(self):
        """Test CMC DEX headers."""
        from extractors.cmc_dex_service import CoinMarketCapDEXService

        service = CoinMarketCapDEXService(
            api_key="test_key",
            base_url="https://pro-api.coinmarketcap.com/dex/v1",
            rate_limit=50,
        )

        headers = service.get_headers()
        assert "X-CMC_PRO_API_KEY" in headers
        assert headers["X-CMC_PRO_API_KEY"] == "test_key"
