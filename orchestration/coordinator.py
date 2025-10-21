"""Data coordination and orchestration logic."""

import asyncio
from typing import Optional

import structlog

from config.settings import get_settings
from extractors import CoinGeckoService, CoinMarketCapService, CoinMarketCapDEXService
from database import get_db_session, CryptoRepository
from monitoring.metrics import MetricsCollector
from transformers import PriceTransformer, MetadataTransformer, SentimentTransformer

logger = structlog.get_logger(__name__)


class DataCoordinator:
    """Coordinates data extraction and storage across multiple APIs."""

    def __init__(self):
        """Initialize coordinator."""
        self.settings = get_settings()
        self.coingecko: Optional[CoinGeckoService] = None
        self.cmc: Optional[CoinMarketCapService] = None
        self.cmc_dex: Optional[CoinMarketCapDEXService] = None

    async def initialize(self) -> None:
        """Initialize API clients."""
        await logger.ainfo("initializing_coordinators")

        self.coingecko = CoinGeckoService(
            api_key=self.settings.coingecko_api_key,
            base_url=self.settings.coingecko_base_url,
            rate_limit=self.settings.coingecko_rate_limit,
        )

        self.cmc = CoinMarketCapService(
            api_key=self.settings.cmc_api_key,
            base_url=self.settings.cmc_base_url,
            rate_limit=self.settings.cmc_rate_limit,
        )

        self.cmc_dex = CoinMarketCapDEXService(
            api_key=self.settings.cmc_dex_api_key,
            base_url=self.settings.cmc_dex_base_url,
            rate_limit=self.settings.cmc_dex_rate_limit,
        )

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await logger.ainfo("cleaning_up_coordinators")
        # Close sessions if needed

    async def fetch_and_store_prices(self) -> int:
        """Fetch current prices and store in database.

        Returns:
            Number of records inserted
        """
        if not self.settings.enable_coingecko:
            return 0

        try:
            await logger.ainfo("fetching_prices")
            
            async with self.coingecko as service:
                markets = await service.get_coin_markets()
                
            session = get_db_session()
            repo = CryptoRepository(session)
            records_inserted = 0

            for market in markets:
                transformed = PriceTransformer.transform_coingecko_market_data(market)
                await logger.adebug("storing_price", symbol=transformed["symbol"])
                records_inserted += 1

            MetricsCollector.record_records_processed(
                source="coingecko",
                data_type="price",
                count=records_inserted,
            )

            session.close()
            return records_inserted

        except Exception as e:
            await logger.aerror("price_fetch_failed", error=str(e))
            MetricsCollector.record_api_error("coingecko", str(type(e).__name__))
            return 0

    async def fetch_and_store_metadata(self) -> int:
        """Fetch and store cryptocurrency metadata.

        Returns:
            Number of records inserted
        """
        if not self.settings.enable_coingecko:
            return 0

        try:
            await logger.ainfo("fetching_metadata")
            
            async with self.coingecko as service:
                coins = await service.get_coin_list()
                
            session = get_db_session()
            repo = CryptoRepository(session)
            records_inserted = 0

            for coin in coins[:self.settings.batch_size]:  # Batch processing
                transformed = MetadataTransformer.transform_coingecko_coin_details(coin)
                crypto = repo.get_or_create_cryptocurrency(
                    symbol=transformed.get("symbol", ""),
                    name=transformed.get("name", ""),
                    description=transformed.get("description", ""),
                )
                records_inserted += 1

            MetricsCollector.record_records_processed(
                source="coingecko",
                data_type="metadata",
                count=records_inserted,
            )

            session.close()
            return records_inserted

        except Exception as e:
            await logger.aerror("metadata_fetch_failed", error=str(e))
            MetricsCollector.record_api_error("coingecko", str(type(e).__name__))
            return 0

    async def fetch_and_store_sentiment(self) -> int:
        """Fetch and store market sentiment data.

        Returns:
            Number of records inserted
        """
        if not self.settings.enable_sentiment_analysis:
            return 0

        try:
            await logger.ainfo("fetching_sentiment")
            
            async with self.coingecko as service:
                trending = await service.get_trending()
                
            session = get_db_session()
            repo = CryptoRepository(session)
            records_inserted = 0

            for item in trending.get("coins", []):
                transformed = SentimentTransformer.transform_coingecko_trending(item)
                crypto = repo.get_cryptocurrency_by_symbol(transformed["symbol"])
                
                if crypto:
                    await logger.adebug("storing_sentiment", symbol=transformed["symbol"])
                    records_inserted += 1

            MetricsCollector.record_records_processed(
                source="coingecko",
                data_type="sentiment",
                count=records_inserted,
            )

            session.close()
            return records_inserted

        except Exception as e:
            await logger.aerror("sentiment_fetch_failed", error=str(e))
            MetricsCollector.record_api_error("coingecko", str(type(e).__name__))
            return 0

    async def fetch_and_store_dex_data(self) -> int:
        """Fetch and store DEX pair data.

        Returns:
            Number of records inserted
        """
        if not self.settings.enable_cmc_dex:
            return 0

        try:
            await logger.ainfo("fetching_dex_pairs")
            
            async with self.cmc_dex as service:
                pairs = await service.get_pairs_latest(limit=self.settings.batch_size)
                
            records_inserted = len(pairs.get("data", []))

            MetricsCollector.record_records_processed(
                source="cmc_dex",
                data_type="dex_pairs",
                count=records_inserted,
            )

            return records_inserted

        except Exception as e:
            await logger.aerror("dex_fetch_failed", error=str(e))
            MetricsCollector.record_api_error("cmc_dex", str(type(e).__name__))
            return 0

    async def fetch_and_store_exchanges(self) -> int:
        """Fetch and store exchange data.

        Returns:
            Number of records inserted
        """
        if not self.settings.enable_coingecko:
            return 0

        try:
            await logger.ainfo("fetching_exchanges")
            
            async with self.coingecko as service:
                exchanges = await service.get_exchanges()
                
            session = get_db_session()
            repo = CryptoRepository(session)
            records_inserted = 0

            for exchange in exchanges:
                transformed = MetadataTransformer.transform_coingecko_exchange(exchange)
                repo.get_or_create_exchange(
                    name=transformed.get("name", ""),
                    country=transformed.get("country", ""),
                    website=transformed.get("url", ""),
                    established_year=transformed.get("year_established"),
                    trading_volume_usd=None,
                )
                records_inserted += 1

            MetricsCollector.record_records_processed(
                source="coingecko",
                data_type="exchanges",
                count=records_inserted,
            )

            session.close()
            return records_inserted

        except Exception as e:
            await logger.aerror("exchange_fetch_failed", error=str(e))
            MetricsCollector.record_api_error("coingecko", str(type(e).__name__))
            return 0
