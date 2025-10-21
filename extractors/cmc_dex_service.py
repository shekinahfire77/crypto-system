"""CoinMarketCap DEX API service for decentralized exchange data."""

from typing import Any, Dict, List, Optional

import structlog

from .base_service import BaseAPIService

logger = structlog.get_logger(__name__)


class CoinMarketCapDEXService(BaseAPIService):
    """CoinMarketCap DEX API service for decentralized exchange data."""

    def get_headers(self) -> Dict[str, str]:
        """Get CoinMarketCap DEX-specific headers."""
        return {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }

    async def get_pairs_latest(
        self,
        blockchain: Optional[str] = None,
        dex: Optional[str] = None,
        quote_currency: str = "USD",
        limit: int = 100,
        sort: str = "volume_24h",
    ) -> Dict[str, Any]:
        """Get latest DEX trading pairs.

        Args:
            blockchain: Blockchain filter (e.g., 'ethereum', 'binance-smart-chain')
            dex: DEX filter (e.g., 'uniswap', 'sushiswap')
            quote_currency: Quote currency for prices
            limit: Maximum results
            sort: Sort by 'volume_24h', 'liquidity', etc.

        Returns:
            Latest DEX pair data
        """
        params = {
            "quote_currency": quote_currency,
            "limit": limit,
            "sort": sort,
        }
        if blockchain:
            params["blockchain"] = blockchain
        if dex:
            params["dex"] = dex

        return await self.make_request("pairs/latest", params)

    async def get_pair_info(
        self,
        pair_address: str,
        blockchain: str,
        quote_currency: str = "USD",
    ) -> Dict[str, Any]:
        """Get specific DEX pair information.

        Args:
            pair_address: DEX pair contract address
            blockchain: Blockchain where pair exists
            quote_currency: Quote currency for prices

        Returns:
            Detailed pair information
        """
        params = {
            "pair_address": pair_address,
            "blockchain": blockchain,
            "quote_currency": quote_currency,
        }
        return await self.make_request("pairs/info", params)

    async def get_pairs_ohlcv(
        self,
        pair_address: str,
        blockchain: str,
        time_period: str = "5m",
        time_start: Optional[int] = None,
        time_end: Optional[int] = None,
        count: int = 10,
        quote_currency: str = "USD",
    ) -> Dict[str, Any]:
        """Get OHLCV data for a DEX pair.

        Args:
            pair_address: DEX pair address
            blockchain: Blockchain ID
            time_period: '1m', '5m', '15m', '30m', '1h', '4h', '1d'
            time_start: Start timestamp
            time_end: End timestamp
            count: Number of candles
            quote_currency: Quote currency

        Returns:
            OHLCV data for the pair
        """
        params = {
            "pair_address": pair_address,
            "blockchain": blockchain,
            "time_period": time_period,
            "count": count,
            "quote_currency": quote_currency,
        }
        if time_start:
            params["time_start"] = time_start
        if time_end:
            params["time_end"] = time_end

        return await self.make_request("pairs/ohlcv/latest", params)

    async def get_dex_list(self) -> Dict[str, Any]:
        """Get list of supported DEXes.

        Returns:
            List of DEXes with metadata
        """
        return await self.make_request("dex/list")

    async def get_blockchain_list(self) -> Dict[str, Any]:
        """Get list of supported blockchains.

        Returns:
            List of blockchains with metadata
        """
        return await self.make_request("blockchain/list")

    async def get_trending_pairs(
        self,
        blockchain: Optional[str] = None,
        dex: Optional[str] = None,
        limit: int = 100,
        time_period: str = "24h",
    ) -> Dict[str, Any]:
        """Get trending DEX pairs.

        Args:
            blockchain: Filter by blockchain
            dex: Filter by DEX
            limit: Maximum results
            time_period: Time period for trending calculation

        Returns:
            Trending pairs data
        """
        params = {
            "limit": limit,
            "time_period": time_period,
        }
        if blockchain:
            params["blockchain"] = blockchain
        if dex:
            params["dex"] = dex

        return await self.make_request("pairs/trending", params)

    async def get_liquidity_analysis(
        self,
        pair_address: str,
        blockchain: str,
        quote_currency: str = "USD",
    ) -> Dict[str, Any]:
        """Get liquidity analysis for a DEX pair.

        Args:
            pair_address: DEX pair address
            blockchain: Blockchain ID
            quote_currency: Quote currency

        Returns:
            Liquidity analysis data
        """
        params = {
            "pair_address": pair_address,
            "blockchain": blockchain,
            "quote_currency": quote_currency,
        }
        return await self.make_request("pairs/liquidity-analysis", params)

    async def get_token_info(
        self,
        token_address: str,
        blockchain: str,
    ) -> Dict[str, Any]:
        """Get token information from DEX data.

        Args:
            token_address: Token contract address
            blockchain: Blockchain ID

        Returns:
            Token information
        """
        params = {
            "token_address": token_address,
            "blockchain": blockchain,
        }
        return await self.make_request("tokens/info", params)

    async def get_dex_volume(
        self,
        dex: Optional[str] = None,
        blockchain: Optional[str] = None,
        time_period: str = "24h",
    ) -> Dict[str, Any]:
        """Get DEX or blockchain volume statistics.

        Args:
            dex: DEX identifier
            blockchain: Blockchain identifier
            time_period: Time period for statistics

        Returns:
            Volume statistics
        """
        params = {"time_period": time_period}
        if dex:
            params["dex"] = dex
        if blockchain:
            params["blockchain"] = blockchain

        return await self.make_request("statistics/volume", params)
