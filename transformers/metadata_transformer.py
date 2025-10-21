"""Cryptocurrency metadata transformation utilities."""

from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class MetadataTransformer:
    """Transform API metadata into database format."""

    @staticmethod
    def transform_coingecko_coin_details(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CoinGecko coin details.

        Args:
            data: CoinGecko coin details

        Returns:
            Transformed data
        """
        return {
            "id": data.get("id", ""),
            "symbol": data.get("symbol", "").upper(),
            "name": data.get("name", ""),
            "description": data.get("description", {}).get("en", ""),
            "website": data.get("links", {}).get("homepage", [None])[0],
            "github": data.get("links", {}).get("repos_url", {}).get("github", [None])[0],
            "twitter": data.get("links", {}).get("twitter_screen_handle", ""),
            "reddit": data.get("links", {}).get("subreddit_url", ""),
            "community_score": data.get("community_score"),
            "developer_score": data.get("developer_score"),
        }

    @staticmethod
    def transform_coingecko_exchange(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CoinGecko exchange data.

        Args:
            data: CoinGecko exchange data

        Returns:
            Transformed data
        """
        return {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "country": data.get("country", ""),
            "url": data.get("url", ""),
            "image": data.get("image", ""),
            "trust_score": data.get("trust_score"),
            "trust_score_rank": data.get("trust_score_rank"),
            "trade_volume_24h_btc": data.get("trade_volume_24h_btc"),
            "year_established": data.get("year_established"),
        }

    @staticmethod
    def transform_cmc_cryptocurrency_map(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CMC cryptocurrency map.

        Args:
            data: CMC cryptocurrency data

        Returns:
            Transformed data
        """
        return {
            "id": data.get("id", ""),
            "rank": data.get("rank", ""),
            "name": data.get("name", ""),
            "symbol": data.get("symbol", "").upper(),
            "slug": data.get("slug", ""),
            "is_active": data.get("is_active", 0),
            "first_historical_data": data.get("first_historical_data", ""),
            "last_historical_data": data.get("last_historical_data", ""),
            "platform": data.get("platform"),
        }

    @staticmethod
    def transform_cmc_exchange(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CMC exchange data.

        Args:
            data: CMC exchange data

        Returns:
            Transformed data
        """
        quote = data.get("quote", {}).get("USD", {})
        
        return {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "slug": data.get("slug", ""),
            "is_active": data.get("is_active", 0),
            "first_noticed": data.get("first_noticed"),
            "notification": data.get("notice"),
            "volume_24h": quote.get("volume_24h"),
            "volume_24h_adjusted": quote.get("volume_24h_adjusted"),
        }

    @staticmethod
    def transform_dex_list(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform DEX list item.

        Args:
            data: DEX data

        Returns:
            Transformed data
        """
        return {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "slug": data.get("slug", ""),
            "website": data.get("website", ""),
            "description": data.get("description", ""),
            "logo": data.get("logo", ""),
        }

    @staticmethod
    def transform_blockchain_list(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform blockchain list item.

        Args:
            data: Blockchain data

        Returns:
            Transformed data
        """
        return {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "slug": data.get("slug", ""),
            "symbol": data.get("symbol", ""),
            "chain_id": data.get("chain_id"),
            "description": data.get("description", ""),
            "logo": data.get("logo", ""),
        }
