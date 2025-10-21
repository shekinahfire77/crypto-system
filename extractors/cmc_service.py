"""CoinMarketCap API service for cryptocurrency market data."""

from typing import Any, Dict, List, Optional

import structlog

from .base_service import BaseAPIService

logger = structlog.get_logger(__name__)


class CoinMarketCapService(BaseAPIService):
    """CoinMarketCap API service for centralized exchange data."""

    def get_headers(self) -> Dict[str, str]:
        """Get CoinMarketCap-specific headers."""
        return {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }

    async def get_cryptocurrency_map(
        self,
        listing_status: str = "active",
        start: int = 1,
        limit: int = 5000,
    ) -> Dict[str, Any]:
        """Get cryptocurrency ID map.

        Args:
            listing_status: 'active', 'inactive', or 'untracked'
            start: Starting index
            limit: Maximum records (max 5000)

        Returns:
            Cryptocurrency map data
        """
        params = {
            "listing_status": listing_status,
            "start": start,
            "limit": limit,
        }
        return await self.make_request("cryptocurrency/map", params)

    async def get_quotes_latest(
        self,
        symbol: Optional[str] = None,
        slug: Optional[str] = None,
        id: Optional[str] = None,
        convert: str = "USD",
    ) -> Dict[str, Any]:
        """Get latest market quotes.

        Args:
            symbol: Cryptocurrency symbol (comma-separated for multiple)
            slug: Cryptocurrency slug
            id: Cryptocurrency ID
            convert: Target currency (e.g., 'USD', 'EUR')

        Returns:
            Latest quote data
        """
        params = {"convert": convert}
        if symbol:
            params["symbol"] = symbol
        if slug:
            params["slug"] = slug
        if id:
            params["id"] = id

        return await self.make_request("cryptocurrency/quotes/latest", params)

    async def get_ohlcv_latest(
        self,
        symbol: Optional[str] = None,
        slug: Optional[str] = None,
        convert: str = "USD",
    ) -> Dict[str, Any]:
        """Get latest OHLCV data.

        Args:
            symbol: Cryptocurrency symbol
            slug: Cryptocurrency slug
            convert: Target currency

        Returns:
            Latest OHLCV data
        """
        params = {"convert": convert}
        if symbol:
            params["symbol"] = symbol
        if slug:
            params["slug"] = slug

        return await self.make_request("cryptocurrency/ohlcv/latest", params)

    async def get_ohlcv_historical(
        self,
        symbol: str,
        time_period: str = "daily",
        time_start: Optional[int] = None,
        time_end: Optional[int] = None,
        count: int = 10,
        convert: str = "USD",
    ) -> Dict[str, Any]:
        """Get historical OHLCV data.

        Args:
            symbol: Cryptocurrency symbol
            time_period: 'daily', 'weekly', or 'monthly'
            time_start: Unix timestamp start
            time_end: Unix timestamp end
            count: Number of time periods
            convert: Target currency

        Returns:
            Historical OHLCV data
        """
        params = {
            "symbol": symbol,
            "time_period": time_period,
            "count": count,
            "convert": convert,
        }
        if time_start:
            params["time_start"] = time_start
        if time_end:
            params["time_end"] = time_end

        return await self.make_request("cryptocurrency/ohlcv/historical", params)

    async def get_exchange_map(
        self,
        listing_status: str = "active",
        slug: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get exchange ID map.

        Args:
            listing_status: 'active' or 'inactive'
            slug: Exchange slug filter
            limit: Maximum records

        Returns:
            Exchange map data
        """
        params = {
            "listing_status": listing_status,
            "limit": limit,
        }
        if slug:
            params["slug"] = slug

        return await self.make_request("exchange/map", params)

    async def get_exchange_info(
        self,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        convert: str = "USD",
    ) -> Dict[str, Any]:
        """Get exchange information.

        Args:
            id: Exchange ID
            slug: Exchange slug
            convert: Target currency

        Returns:
            Exchange information
        """
        params = {"convert": convert}
        if id:
            params["id"] = id
        if slug:
            params["slug"] = slug

        return await self.make_request("exchange/info", params)

    async def get_global_quotes_latest(
        self,
        convert: str = "USD",
    ) -> Dict[str, Any]:
        """Get latest global market data.

        Args:
            convert: Target currency

        Returns:
            Global market quotes
        """
        params = {"convert": convert}
        return await self.make_request("global-metrics/quotes/latest", params)

    async def get_trending(self) -> Dict[str, Any]:
        """Get trending cryptocurrencies.

        Returns:
            Trending cryptocurrency data
        """
        return await self.make_request("cryptocurrency/trending/latest")

    async def get_price_performance(
        self,
        symbol: str,
        time_period: str = "24h",
        convert: str = "USD",
    ) -> Dict[str, Any]:
        """Get price performance data.

        Args:
            symbol: Cryptocurrency symbol
            time_period: '1h', '24h', '7d', '30d', '90d', etc.
            convert: Target currency

        Returns:
            Price performance data
        """
        params = {
            "symbol": symbol,
            "time_period": time_period,
            "convert": convert,
        }
        return await self.make_request("cryptocurrency/price-performance-stats/latest", params)

    async def get_gainers_losers(
        self,
        time_period: str = "24h",
        convert: str = "USD",
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get top gainers and losers.

        Args:
            time_period: Time period for comparison
            convert: Target currency
            limit: Maximum results

        Returns:
            Gainers and losers data
        """
        params = {
            "time_period": time_period,
            "convert": convert,
            "limit": limit,
        }
        return await self.make_request("cryptocurrency/gainers-losers", params)
