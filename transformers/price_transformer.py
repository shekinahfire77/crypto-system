"""Price data transformation utilities."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class PriceTransformer:
    """Transform API price data into database format."""

    @staticmethod
    def transform_coingecko_market_data(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CoinGecko market data.

        Args:
            data: CoinGecko market data

        Returns:
            Transformed data
        """
        return {
            "symbol": data.get("symbol", "").upper(),
            "name": data.get("name", ""),
            "current_price": Decimal(str(data.get("current_price", 0))),
            "market_cap": Decimal(str(data.get("market_cap", 0))) if data.get("market_cap") else None,
            "market_cap_rank": data.get("market_cap_rank"),
            "total_volume": Decimal(str(data.get("total_volume", 0))) if data.get("total_volume") else None,
            "high_24h": Decimal(str(data.get("high_24h", 0))) if data.get("high_24h") else None,
            "low_24h": Decimal(str(data.get("low_24h", 0))) if data.get("low_24h") else None,
            "price_change_24h": Decimal(str(data.get("price_change_24h", 0))) if data.get("price_change_24h") else None,
            "price_change_percentage_24h": Decimal(str(data.get("price_change_percentage_24h", 0))) if data.get("price_change_percentage_24h") else None,
        }

    @staticmethod
    def transform_coingecko_ohlc(
        ohlc_data: List[List[float]],
        trading_pair_id: int,
    ) -> List[Dict[str, Any]]:
        """Transform CoinGecko OHLC data.

        Args:
            ohlc_data: List of [timestamp, open, high, low, close]
            trading_pair_id: Trading pair ID

        Returns:
            List of transformed OHLC records
        """
        records = []
        for candle in ohlc_data:
            if len(candle) >= 5:
                records.append({
                    "trading_pair_id": trading_pair_id,
                    "recorded_at": datetime.fromtimestamp(candle[0] / 1000),
                    "open_price": Decimal(str(candle[1])),
                    "high_price": Decimal(str(candle[2])),
                    "low_price": Decimal(str(candle[3])),
                    "close_price": Decimal(str(candle[4])),
                    "volume": Decimal("0"),  # CoinGecko OHLC doesn't include volume
                })
        return records

    @staticmethod
    def transform_cmc_quote(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CoinMarketCap quote data.

        Args:
            data: CMC quote data

        Returns:
            Transformed data
        """
        quote = data.get("quote", {}).get("USD", {})
        
        return {
            "symbol": data.get("symbol", ""),
            "name": data.get("name", ""),
            "current_price": Decimal(str(quote.get("price", 0))),
            "market_cap": Decimal(str(quote.get("market_cap", 0))) if quote.get("market_cap") else None,
            "market_cap_rank": data.get("cmc_rank"),
            "total_volume": Decimal(str(quote.get("volume_24h", 0))) if quote.get("volume_24h") else None,
            "high_24h": Decimal(str(quote.get("high_24h", 0))) if quote.get("high_24h") else None,
            "low_24h": Decimal(str(quote.get("low_24h", 0))) if quote.get("low_24h") else None,
            "price_change_24h": Decimal(str(quote.get("price_change_24h", 0))) if quote.get("price_change_24h") else None,
        }

    @staticmethod
    def transform_cmc_ohlcv(
        data: Dict[str, Any],
        trading_pair_id: int,
    ) -> List[Dict[str, Any]]:
        """Transform CoinMarketCap OHLCV data.

        Args:
            data: CMC OHLCV data
            trading_pair_id: Trading pair ID

        Returns:
            List of transformed records
        """
        records = []
        quotes = data.get("quotes", [])
        
        for quote in quotes:
            records.append({
                "trading_pair_id": trading_pair_id,
                "recorded_at": datetime.fromisoformat(quote.get("timestamp", "").replace("Z", "+00:00")),
                "open_price": Decimal(str(quote.get("open", 0))),
                "high_price": Decimal(str(quote.get("high", 0))),
                "low_price": Decimal(str(quote.get("low", 0))),
                "close_price": Decimal(str(quote.get("close", 0))),
                "volume": Decimal(str(quote.get("volume", 0))),
            })
        
        return records

    @staticmethod
    def transform_dex_pair(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform DEX pair data.

        Args:
            data: DEX pair data

        Returns:
            Transformed data
        """
        quote = data.get("quote", {}).get("USD", {})
        
        return {
            "pair_address": data.get("pair_address", ""),
            "blockchain": data.get("blockchain", ""),
            "dex": data.get("dex", ""),
            "base_token": data.get("base_token", {}),
            "quote_token": data.get("quote_token", {}),
            "price": Decimal(str(quote.get("price", 0))) if quote.get("price") else None,
            "liquidity": Decimal(str(quote.get("liquidity", 0))) if quote.get("liquidity") else None,
            "volume_24h": Decimal(str(quote.get("volume_24h", 0))) if quote.get("volume_24h") else None,
            "price_change_24h": Decimal(str(quote.get("price_change_24h", 0))) if quote.get("price_change_24h") else None,
        }
