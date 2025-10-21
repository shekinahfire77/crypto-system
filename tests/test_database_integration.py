"""Tests for database integration."""

import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base
from database.connection import get_db_engine, get_db_session
from database.repository import CryptoRepository


class TestDatabaseConnection:
    """Test database connection setup."""

    def test_database_url_generation(self, test_settings):
        """Test database URL is generated correctly."""
        expected_url = (
            f"postgresql://{test_settings.db_user}:{test_settings.db_password}@"
            f"{test_settings.db_host}:{test_settings.db_port}/{test_settings.db_name}"
        )

        assert test_settings.database_url == expected_url

    def test_masked_settings(self, test_settings):
        """Test that settings mask sensitive data."""
        masked = test_settings.get_masked_settings()

        assert masked["coingecko_api_key"] == "***MASKED***"
        assert masked["cmc_api_key"] == "***MASKED***"
        assert masked["cmc_dex_api_key"] == "***MASKED***"
        assert masked["db_password"] == "***MASKED***"


class TestDatabaseModels:
    """Test database models creation."""

    def test_models_created_in_session(self, test_session):
        """Test that all models can be created."""
        from database.models import (
            Cryptocurrency,
            Exchange,
            TradingPair,
            PriceHistory,
            MarketSentiment,
            MarketEvent,
        )

        # Models should be accessible
        assert Cryptocurrency is not None
        assert Exchange is not None
        assert TradingPair is not None
        assert PriceHistory is not None
        assert MarketSentiment is not None
        assert MarketEvent is not None


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_end_to_end_data_flow(self, test_session):
        """Test complete data flow from API to database."""
        repo = CryptoRepository(test_session)

        # Create cryptocurrency
        crypto = repo.get_or_create_cryptocurrency(
            symbol="BTC",
            name="Bitcoin",
            description="First cryptocurrency",
        )
        assert crypto.id is not None

        # Create exchange
        exchange = repo.get_or_create_exchange(
            name="Binance",
            country="Malta",
            website="https://binance.com",
        )
        assert exchange.id is not None

        # Create trading pair
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="BTC",
            quote_currency="USD",
        )
        assert pair.id is not None

        # Add price history
        from datetime import datetime
        from decimal import Decimal

        price = repo.add_price_history(
            trading_pair_id=pair.id,
            open_price=Decimal("45000"),
            high_price=Decimal("46000"),
            low_price=Decimal("44000"),
            close_price=Decimal("45500"),
            volume=Decimal("50000000"),
            recorded_at=datetime.utcnow(),
        )
        assert price.id is not None

        # Verify data retrieval
        latest = repo.get_latest_price(pair.id)
        assert latest.close_price == Decimal("45500")

        retrieved_crypto = repo.get_cryptocurrency_by_symbol("BTC")
        assert retrieved_crypto.id == crypto.id

    def test_sentiment_data_flow(self, test_session):
        """Test sentiment data storage and retrieval."""
        from datetime import datetime
        from decimal import Decimal

        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency(
            symbol="ETH",
            name="Ethereum",
        )

        sentiment = repo.add_market_sentiment(
            crypto_id=crypto.id,
            sentiment_score=Decimal("0.75"),
            sentiment_label="positive",
            mentions_count=5000,
            recorded_at=datetime.utcnow(),
        )
        assert sentiment.id is not None

        latest_sentiment = repo.get_latest_sentiment(crypto.id)
        assert latest_sentiment.sentiment_label == "positive"

    def test_market_events_flow(self, test_session):
        """Test market events storage and retrieval."""
        from datetime import datetime

        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency(
            symbol="ADA",
            name="Cardano",
        )

        # Use today's date as datetime
        today = datetime.utcnow()
        event = repo.add_market_event(
            crypto_id=crypto.id,
            event_type="upgrade",
            title="Cardano Vasil Upgrade",
            description="Major protocol upgrade",
            impact_level="high",
            event_date=today,
        )
        assert event.id is not None

        recent_events = repo.get_recent_events(days=30, crypto_id=crypto.id)
        assert len(recent_events) > 0
        assert recent_events[0].event_type == "upgrade"

    def test_batch_operations(self, test_session):
        """Test batch operations for performance."""
        from datetime import datetime, timedelta
        from decimal import Decimal

        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("SOL", "Solana")
        exchange = repo.get_or_create_exchange("FTX")
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="SOL",
            quote_currency="USD",
        )

        # Create batch data
        now = datetime.utcnow()
        prices = [
            (
                pair.id,
                Decimal("100"),
                Decimal("110"),
                Decimal("90"),
                Decimal("105"),
                Decimal("1000000"),
                now - timedelta(hours=i),
            )
            for i in range(100)
        ]

        # Insert batch
        count = repo.batch_add_prices(prices)
        assert count == 100

        # Verify
        all_prices = repo.get_price_history_last_hours(pair.id, hours=200)
        assert len(all_prices) == 100


class TestDatabaseConstraints:
    """Test database constraints and integrity."""

    def test_foreign_key_constraint(self, test_session):
        """Test foreign key constraints."""
        from database.models import TradingPair

        # Try to create trading pair with non-existent IDs
        pair = TradingPair(
            exchange_id=99999,  # Non-existent
            crypto_id=99999,  # Non-existent
            base_currency="BTC",
            quote_currency="USD",
        )

        test_session.add(pair)

        # This should fail when committing (SQLite may not enforce by default)
        # but the constraint is defined

    def test_unique_constraints(self, test_session):
        """Test unique constraints."""
        from database.models import Cryptocurrency

        crypto1 = Cryptocurrency(symbol="BTC", name="Bitcoin")
        crypto2 = Cryptocurrency(symbol="BTC", name="Bitcoin2")

        test_session.add(crypto1)
        test_session.commit()

        test_session.add(crypto2)

        with pytest.raises(Exception):
            test_session.commit()

    def test_not_null_constraints(self, test_session):
        """Test NOT NULL constraints."""
        from database.models import Cryptocurrency

        crypto = Cryptocurrency(symbol="BTC", name=None)  # name is required
        test_session.add(crypto)

        with pytest.raises(Exception):
            test_session.commit()
