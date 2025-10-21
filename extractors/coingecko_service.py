"""CoinGecko API service for cryptocurrency market data."""

from typing import Any, Dict, List, Optional

import structlog

from .base_service import BaseAPIService

logger = structlog.get_logger(__name__)


class CoinGeckoService(BaseAPIService):
    """CoinGecko API service for centralized exchange cryptocurrency data."""

    def get_headers(self) -> Dict[str, str]:
        """Get CoinGecko-specific headers."""
        return {
            "x-cg-demo-api-key": self.api_key,
            "accept": "application/json",
        }

    async def get_coin_list(self, include_platform: bool = True) -> List[Dict[str, Any]]:
        """Fetch list of all supported coins.

        Args:
            include_platform: Include platform addresses

        Returns:
            List of coins with id, symbol, name
        """
        params = {"include_platform": str(include_platform).lower()}
        return await self.make_request("coins/list", params)

    async def get_coin_markets(
        self,
        vs_currency: str = "usd",
        ids: Optional[str] = None,
        per_page: int = 250,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get market data for multiple coins.

        Args:
            vs_currency: Target currency (e.g., 'usd')
            ids: Comma-separated cryptocurrency IDs
            per_page: Results per page (max 250)
            page: Page number

        Returns:
            List of market data for coins
        """
        params = {
            "vs_currency": vs_currency,
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d,30d",
        }
        if ids:
            params["ids"] = ids

        return await self.make_request("coins/markets", params)

    async def get_coin_details(self, coin_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific coin.

        Args:
            coin_id: Cryptocurrency ID (e.g., 'bitcoin')

        Returns:
            Detailed coin information
        """
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "true",
            "developer_data": "false",
            "sparkline": "false",
        }
        return await self.make_request(f"coins/{coin_id}", params)

    async def get_ohlc_data(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 1,
    ) -> List[List[float]]:
        """Get OHLC data (max 365 days).

        Args:
            coin_id: Cryptocurrency ID
            vs_currency: Target currency
            days: Number of days (max 365)

        Returns:
            List of [timestamp, open, high, low, close]
        """
        params = {
            "vs_currency": vs_currency,
            "days": min(days, 365),
        }
        return await self.make_request(f"coins/{coin_id}/ohlc", params)

    async def get_historical_data(
        self,
        coin_id: str,
        date: str,
        vs_currency: str = "usd",
    ) -> Dict[str, Any]:
        """Get historical data for a specific date.

        Args:
            coin_id: Cryptocurrency ID
            date: Date in dd-mm-yyyy format
            vs_currency: Target currency

        Returns:
            Historical data for the date
        """
        params = {
            "date": date,
            "localization": "false",
        }
        return await self.make_request(f"coins/{coin_id}/history", params)

    async def get_exchanges(
        self,
        per_page: int = 100,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get list of exchanges with volume data.

        Args:
            per_page: Results per page
            page: Page number

        Returns:
            List of exchange data
        """
        params = {
            "per_page": per_page,
            "page": page,
        }
        return await self.make_request("exchanges", params)

    async def get_exchange_tickers(
        self,
        exchange_id: str,
        coin_ids: Optional[str] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Get trading pairs for a specific exchange.

        Args:
            exchange_id: Exchange ID (e.g., 'binance')
            coin_ids: Filter by coin IDs (comma-separated)
            page: Page number for pagination

        Returns:
            Exchange ticker data
        """
        params = {"page": page}
        if coin_ids:
            params["coin_ids"] = coin_ids

        return await self.make_request(f"exchanges/{exchange_id}/tickers", params)

    async def get_trending(self) -> Dict[str, Any]:
        """Get trending coins (sentiment indicator).

        Returns:
            Trending cryptocurrencies data
        """
        return await self.make_request("search/trending")

    async def get_global_data(self, vs_currency: str = "usd") -> Dict[str, Any]:
        """Get global cryptocurrency market data.

        Args:
            vs_currency: Target currency

        Returns:
            Global market statistics
        """
        params = {"include_market_cap": "true", "include_24hr_vol": "true"}
        return await self.make_request("global", params)

    async def get_market_chart_data(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get price, market cap, and volume chart data.

        Args:
            coin_id: Cryptocurrency ID
            vs_currency: Target currency
            days: Number of days of data

        Returns:
            Chart data with timestamps and values
        """
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily",
        }
        return await self.make_request(f"coins/{coin_id}/market_chart", params)

    async def get_coin_by_contract_address(
        self,
        contract_address: str,
        asset_platform_id: str = "ethereum",
    ) -> Dict[str, Any]:
        """Get coin data by contract address.

        Args:
            contract_address: Contract address
            asset_platform_id: Blockchain ID (default: ethereum)

        Returns:
            Coin data for contract
        """
        return await self.make_request(
            f"coins/{asset_platform_id}/contract/{contract_address}"
        )
