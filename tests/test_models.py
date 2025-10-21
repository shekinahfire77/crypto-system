"""Tests for database models and relationships."""

import pytest
from datetime import datetime, date
from decimal import Decimal

from database.models import (
    Cryptocurrency,
    Exchange,
    TradingPair,
    PriceHistory,
    MarketSentiment,
    MarketEvent,
)


class TestCryptocurrencyModel:
    """Test Cryptocurrency model."""

    def test_create_cryptocurrency(self, test_session):
        """Test creating a cryptocurrency."""
        crypto = Cryptocurrency(
            symbol="BTC",
            name="Bitcoin",
            description="Digital currency",
        )
        test_session.add(crypto)
        test_session.commit()

        retrieved = test_session.query(Cryptocurrency).filter_by(symbol="BTC").first()
        assert retrieved is not None
        assert retrieved.name == "Bitcoin"
        assert retrieved.symbol == "BTC"
        assert retrieved.description == "Digital currency"

    def test_cryptocurrency_unique_symbol(self, test_session):
        """Test unique symbol constraint."""
        crypto1 = Cryptocurrency(symbol="ETH", name="Ethereum")
        crypto2 = Cryptocurrency(symbol="ETH", name="Ethereum Classic")

        test_session.add(crypto1)
        test_session.commit()

        test_session.add(crypto2)
        with pytest.raises(Exception):  # IntegrityError
            test_session.commit()

    def test_cryptocurrency_timestamps(self, test_session):
        """Test created_at and updated_at timestamps."""
        crypto = Cryptocurrency(symbol="XRP", name="Ripple")
        test_session.add(crypto)
        test_session.commit()

        assert crypto.created_at is not None
        assert crypto.updated_at is not None
        assert isinstance(crypto.created_at, datetime)


class TestExchangeModel:
    """Test Exchange model."""

    def test_create_exchange(self, test_session):
        """Test creating an exchange."""
        exchange = Exchange(
            name="Binance",
            country="Malta",
            website="https://www.binance.com",
            established_year=2017,
            trading_volume_usd=Decimal("50000000000.00"),
        )
        test_session.add(exchange)
        test_session.commit()

        retrieved = test_session.query(Exchange).filter_by(name="Binance").first()
        assert retrieved is not None
        assert retrieved.country == "Malta"
        assert retrieved.trading_volume_usd == Decimal("50000000000.00")

    def test_exchange_unique_name(self, test_session):
        """Test unique name constraint."""
        ex1 = Exchange(name="Kraken")
        ex2 = Exchange(name="Kraken")

        test_session.add(ex1)
        test_session.commit()

        test_session.add(ex2)
        with pytest.raises(Exception):
            test_session.commit()


class TestTradingPairModel:
    """Test TradingPair model."""

    def test_create_trading_pair(self, test_session):
        """Test creating a trading pair."""
        crypto = Cryptocurrency(symbol="BTC", name="Bitcoin")
        exchange = Exchange(name="Coinbase")

        test_session.add_all([crypto, exchange])
        test_session.commit()

        pair = TradingPair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="BTC",
            quote_currency="USD",
            is_active=True,
        )
        test_session.add(pair)
        test_session.commit()

        retrieved = test_session.query(TradingPair).first()
        assert retrieved is not None
        assert retrieved.base_currency == "BTC"
        assert retrieved.quote_currency == "USD"
        assert retrieved.is_active is True

    def test_trading_pair_relationships(self, test_session):
        """Test trading pair relationships."""
        crypto = Cryptocurrency(symbol="ETH", name="Ethereum")
        exchange = Exchange(name="Kraken")

        test_session.add_all([crypto, exchange])
        test_session.commit()

        pair = TradingPair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="ETH",
            quote_currency="EUR",
        )
        test_session.add(pair)
        test_session.commit()

        # Test relationships
        retrieved_pair = test_session.query(TradingPair).first()
        assert retrieved_pair.cryptocurrency.symbol == "ETH"
        assert retrieved_pair.exchange.name == "Kraken"

    def test_trading_pair_unique_constraint(self, test_session):
        """Test unique constraint on trading pair."""
        crypto = Cryptocurrency(symbol="ADA", name="Cardano")
        exchange = Exchange(name="Gemini")

        test_session.add_all([crypto, exchange])
        test_session.commit()

        pair1 = TradingPair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="ADA",
            quote_currency="USD",
        )
        test_session.add(pair1)
        test_session.commit()

        # Try to add duplicate
        pair2 = TradingPair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="ADA",
            quote_currency="USD",
        )
        test_session.add(pair2)
        with pytest.raises(Exception):
            test_session.commit()


class TestPriceHistoryModel:
    """Test PriceHistory model."""

    def test_create_price_history(self, test_session):
        """Test creating price history record."""
        crypto = Cryptocurrency(symbol="SOL", name="Solana")
        exchange = Exchange(name="FTX")
        pair = TradingPair(
            exchange_id=None,
            crypto_id=None,
            base_currency="SOL",
            quote_currency="USD",
        )

        test_session.add_all([crypto, exchange])
        test_session.commit()

        pair.exchange_id = exchange.id
        pair.crypto_id = crypto.id
        test_session.add(pair)
        test_session.commit()

        price = PriceHistory(
            trading_pair_id=pair.id,
            open_price=Decimal("100.50"),
            high_price=Decimal("110.00"),
            low_price=Decimal("95.00"),
            close_price=Decimal("105.75"),
            volume=Decimal("1000000.50"),
            recorded_at=datetime.utcnow(),
        )
        test_session.add(price)
        test_session.commit()

        retrieved = test_session.query(PriceHistory).first()
        assert retrieved is not None
        assert retrieved.open_price == Decimal("100.50")
        assert retrieved.high_price == Decimal("110.00")
        assert retrieved.low_price == Decimal("95.00")
        assert retrieved.close_price == Decimal("105.75")

    def test_price_history_relationship(self, test_session):
        """Test price history relationship to trading pair."""
        crypto = Cryptocurrency(symbol="DOT", name="Polkadot")
        exchange = Exchange(name="Kraken")

        test_session.add_all([crypto, exchange])
        test_session.commit()

        pair = TradingPair(
            exchange_id=exchange.id,
            crypto_id=crypto.id,
            base_currency="DOT",
            quote_currency="USD",
        )
        test_session.add(pair)
        test_session.commit()

        price = PriceHistory(
            trading_pair_id=pair.id,
            open_price=Decimal("10.00"),
            high_price=Decimal("12.00"),
            low_price=Decimal("9.00"),
            close_price=Decimal("11.00"),
            volume=Decimal("500000"),
            recorded_at=datetime.utcnow(),
        )
        test_session.add(price)
        test_session.commit()

        retrieved = test_session.query(PriceHistory).first()
        assert retrieved.trading_pair.cryptocurrency.symbol == "DOT"


class TestMarketSentimentModel:
    """Test MarketSentiment model."""

    def test_create_market_sentiment(self, test_session):
        """Test creating market sentiment record."""
        crypto = Cryptocurrency(symbol="DOGE", name="Dogecoin")
        test_session.add(crypto)
        test_session.commit()

        sentiment = MarketSentiment(
            crypto_id=crypto.id,
            sentiment_score=Decimal("0.75"),
            sentiment_label="positive",
            mentions_count=1500,
            recorded_at=datetime.utcnow(),
        )
        test_session.add(sentiment)
        test_session.commit()

        retrieved = test_session.query(MarketSentiment).first()
        assert retrieved is not None
        assert retrieved.sentiment_score == Decimal("0.75")
        assert retrieved.sentiment_label == "positive"
        assert retrieved.mentions_count == 1500

    def test_sentiment_relationship(self, test_session):
        """Test sentiment relationship to cryptocurrency."""
        crypto = Cryptocurrency(symbol="SHIB", name="Shiba Inu")
        test_session.add(crypto)
        test_session.commit()

        sentiment = MarketSentiment(
            crypto_id=crypto.id,
            sentiment_score=Decimal("-0.30"),
            sentiment_label="negative",
            mentions_count=800,
            recorded_at=datetime.utcnow(),
        )
        test_session.add(sentiment)
        test_session.commit()

        retrieved = test_session.query(MarketSentiment).first()
        assert retrieved.cryptocurrency.symbol == "SHIB"


class TestMarketEventModel:
    """Test MarketEvent model."""

    def test_create_market_event(self, test_session):
        """Test creating market event record."""
        crypto = Cryptocurrency(symbol="ETH", name="Ethereum")
        test_session.add(crypto)
        test_session.commit()

        event = MarketEvent(
            crypto_id=crypto.id,
            event_type="upgrade",
            title="Ethereum Merge",
            description="Transition from PoW to PoS",
            impact_level="high",
            event_date=date(2022, 9, 15),
        )
        test_session.add(event)
        test_session.commit()

        retrieved = test_session.query(MarketEvent).first()
        assert retrieved is not None
        assert retrieved.event_type == "upgrade"
        assert retrieved.title == "Ethereum Merge"
        assert retrieved.impact_level == "high"

    def test_event_without_cryptocurrency(self, test_session):
        """Test market event without linked cryptocurrency."""
        event = MarketEvent(
            crypto_id=None,
            event_type="regulation",
            title="SEC Bitcoin Approval",
            description="SEC approves Bitcoin ETF",
            impact_level="high",
            event_date=date(2023, 1, 10),
        )
        test_session.add(event)
        test_session.commit()

        retrieved = test_session.query(MarketEvent).first()
        assert retrieved.crypto_id is None
        assert retrieved.event_type == "regulation"

    def test_event_relationship(self, test_session):
        """Test event relationship to cryptocurrency."""
        crypto = Cryptocurrency(symbol="BTC", name="Bitcoin")
        test_session.add(crypto)
        test_session.commit()

        event = MarketEvent(
            crypto_id=crypto.id,
            event_type="fork",
            title="Bitcoin Fork",
            description="Protocol upgrade",
            impact_level="medium",
            event_date=date(2023, 6, 1),
        )
        test_session.add(event)
        test_session.commit()

        retrieved = test_session.query(MarketEvent).first()
        assert retrieved.cryptocurrency.symbol == "BTC"
