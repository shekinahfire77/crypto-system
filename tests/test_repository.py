"""Tests for database repository layer."""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal

from database.models import Cryptocurrency, Exchange, TradingPair, PriceHistory
from database.repository import CryptoRepository


class TestCryptoRepositoryCryptocurrency:
    """Test cryptocurrency repository operations."""

    def test_get_or_create_cryptocurrency_new(self, test_session):
        """Test creating new cryptocurrency."""
        repo = CryptoRepository(test_session)
        crypto = repo.get_or_create_cryptocurrency(
            symbol="BTC",
            name="Bitcoin",
            description="Digital currency",
        )

        assert crypto.id is not None
        assert crypto.symbol == "BTC"
        assert crypto.name == "Bitcoin"

    def test_get_or_create_cryptocurrency_existing(self, test_session):
        """Test getting existing cryptocurrency."""
        repo = CryptoRepository(test_session)

        # Create first
        crypto1 = repo.get_or_create_cryptocurrency("ETH", "Ethereum")
        id1 = crypto1.id

        # Get existing
        crypto2 = repo.get_or_create_cryptocurrency("ETH", "Ethereum")
        id2 = crypto2.id

        assert id1 == id2

    def test_get_cryptocurrency_by_symbol(self, test_session):
        """Test retrieving cryptocurrency by symbol."""
        repo = CryptoRepository(test_session)
        repo.get_or_create_cryptocurrency("XRP", "Ripple")

        crypto = repo.get_cryptocurrency_by_symbol("XRP")
        assert crypto is not None
        assert crypto.symbol == "XRP"
        assert crypto.name == "Ripple"

    def test_get_all_cryptocurrencies(self, test_session):
        """Test retrieving all cryptocurrencies."""
        repo = CryptoRepository(test_session)
        repo.get_or_create_cryptocurrency("BTC", "Bitcoin")
        repo.get_or_create_cryptocurrency("ETH", "Ethereum")
        repo.get_or_create_cryptocurrency("ADA", "Cardano")

        all_cryptos = repo.get_all_cryptocurrencies()
        assert len(all_cryptos) == 3


class TestCryptoRepositoryExchange:
    """Test exchange repository operations."""

    def test_get_or_create_exchange_new(self, test_session):
        """Test creating new exchange."""
        repo = CryptoRepository(test_session)
        exchange = repo.get_or_create_exchange(
            name="Binance",
            country="Malta",
            website="https://binance.com",
            established_year=2017,
            trading_volume_usd=Decimal("50000000000"),
        )

        assert exchange.id is not None
        assert exchange.name == "Binance"
        assert exchange.country == "Malta"

    def test_get_or_create_exchange_existing(self, test_session):
        """Test getting existing exchange."""
        repo = CryptoRepository(test_session)

        ex1 = repo.get_or_create_exchange("Kraken", "USA")
        id1 = ex1.id

        ex2 = repo.get_or_create_exchange("Kraken", "USA")
        id2 = ex2.id

        assert id1 == id2

    def test_get_exchange_by_name(self, test_session):
        """Test retrieving exchange by name."""
        repo = CryptoRepository(test_session)
        repo.get_or_create_exchange("Coinbase", "USA")

        exchange = repo.get_exchange_by_name("Coinbase")
        assert exchange is not None
        assert exchange.name == "Coinbase"

    def test_get_all_exchanges(self, test_session):
        """Test retrieving all exchanges."""
        repo = CryptoRepository(test_session)
        repo.get_or_create_exchange("Binance", "Malta")
        repo.get_or_create_exchange("Kraken", "USA")

        all_exchanges = repo.get_all_exchanges()
        assert len(all_exchanges) == 2


class TestCryptoRepositoryTradingPair:
    """Test trading pair repository operations."""

    def test_get_or_create_trading_pair_new(self, test_session):
        """Test creating new trading pair."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("BTC", "Bitcoin")
        exchange = repo.get_or_create_exchange("Binance")

        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="BTC",
            quote_currency="USD",
        )

        assert pair.id is not None
        assert pair.base_currency == "BTC"
        assert pair.quote_currency == "USD"

    def test_get_active_trading_pairs(self, test_session):
        """Test retrieving active trading pairs."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("ETH", "Ethereum")
        exchange = repo.get_or_create_exchange("Kraken")

        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="ETH",
            quote_currency="EUR",
            is_active=True,
        )

        active_pairs = repo.get_active_trading_pairs()
        assert len(active_pairs) > 0
        assert pair in active_pairs


class TestCryptoRepositoryPriceHistory:
    """Test price history repository operations."""

    def test_add_price_history(self, test_session):
        """Test adding price history record."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("SOL", "Solana")
        exchange = repo.get_or_create_exchange("FTX")
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="SOL",
            quote_currency="USD",
        )

        now = datetime.utcnow()
        price = repo.add_price_history(
            trading_pair_id=pair.id,
            open_price=Decimal("100.00"),
            high_price=Decimal("110.00"),
            low_price=Decimal("95.00"),
            close_price=Decimal("105.00"),
            volume=Decimal("1000000"),
            recorded_at=now,
        )

        assert price.id is not None
        assert price.close_price == Decimal("105.00")

    def test_get_latest_price(self, test_session):
        """Test getting latest price for trading pair."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("DOT", "Polkadot")
        exchange = repo.get_or_create_exchange("Coinbase")
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="DOT",
            quote_currency="USD",
        )

        now = datetime.utcnow()
        repo.add_price_history(
            trading_pair_id=pair.id,
            open_price=Decimal("10.00"),
            high_price=Decimal("12.00"),
            low_price=Decimal("9.00"),
            close_price=Decimal("11.00"),
            volume=Decimal("500000"),
            recorded_at=now,
        )

        latest = repo.get_latest_price(pair.id)
        assert latest is not None
        assert latest.close_price == Decimal("11.00")

    def test_get_price_history_range(self, test_session):
        """Test getting price history for date range."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("ADA", "Cardano")
        exchange = repo.get_or_create_exchange("Kraken")
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="ADA",
            quote_currency="USD",
        )

        now = datetime.utcnow()
        start = now - timedelta(hours=2)
        end = now + timedelta(hours=1)

        # Add multiple prices
        for i in range(3):
            repo.add_price_history(
                trading_pair_id=pair.id,
                open_price=Decimal(str(10 + i)),
                high_price=Decimal(str(12 + i)),
                low_price=Decimal(str(9 + i)),
                close_price=Decimal(str(11 + i)),
                volume=Decimal("500000"),
                recorded_at=now - timedelta(hours=i),
            )

        prices = repo.get_price_history_range(pair.id, start, end)
        assert len(prices) >= 3

    def test_get_price_history_last_hours(self, test_session):
        """Test getting price history for last N hours."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("XRP", "Ripple")
        exchange = repo.get_or_create_exchange("Binance")
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="XRP",
            quote_currency="USD",
        )

        now = datetime.utcnow()

        # Add prices for last 24 hours
        for i in range(24):
            repo.add_price_history(
                trading_pair_id=pair.id,
                open_price=Decimal("0.50"),
                high_price=Decimal("0.55"),
                low_price=Decimal("0.45"),
                close_price=Decimal("0.52"),
                volume=Decimal("1000000"),
                recorded_at=now - timedelta(hours=i),
            )

        prices = repo.get_price_history_last_hours(pair.id, hours=12)
        assert len(prices) >= 12

    def test_batch_add_prices(self, test_session):
        """Test batch adding price records."""
        repo = CryptoRepository(test_session)

        crypto = repo.get_or_create_cryptocurrency("LUNA", "Luna")
        exchange = repo.get_or_create_exchange("Terra Station")
        pair = repo.get_or_create_trading_pair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="LUNA",
            quote_currency="USD",
        )

        now = datetime.utcnow()
        prices = [
            (
                pair.id,
                Decimal("1.00"),
                Decimal("1.10"),
                Decimal("0.90"),
                Decimal("1.05"),
                Decimal("1000000"),
                now - timedelta(hours=i),
            )
            for i in range(10)
        ]

        count = repo.batch_add_prices(prices)
        assert count == 10

        all_prices = repo.get_price_history_last_hours(pair.id, hours=24)
        assert len(all_prices) == 10
