"""Data access layer for crypto database."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

import structlog
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from database.models import (
    Cryptocurrency,
    Exchange,
    MarketEvent,
    MarketSentiment,
    PriceHistory,
    TradingPair,
)

logger = structlog.get_logger(__name__)


class CryptoRepository:
    """Repository for data access operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy Session
        """
        self.session = session

    # Cryptocurrency operations
    def get_or_create_cryptocurrency(
        self,
        symbol: str,
        name: str,
        description: Optional[str] = None,
    ) -> Cryptocurrency:
        """Get existing or create new cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol
            name: Cryptocurrency name
            description: Cryptocurrency description

        Returns:
            Cryptocurrency instance
        """
        crypto = self.session.query(Cryptocurrency).filter_by(symbol=symbol).first()
        if not crypto:
            crypto = Cryptocurrency(
                symbol=symbol,
                name=name,
                description=description,
            )
            self.session.add(crypto)
            self.session.commit()

        return crypto

    def get_cryptocurrency_by_symbol(self, symbol: str) -> Optional[Cryptocurrency]:
        """Get cryptocurrency by symbol.

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            Cryptocurrency or None
        """
        return self.session.query(Cryptocurrency).filter_by(symbol=symbol).first()

    def get_all_cryptocurrencies(self) -> List[Cryptocurrency]:
        """Get all cryptocurrencies.

        Returns:
            List of cryptocurrencies
        """
        return self.session.query(Cryptocurrency).all()

    # Exchange operations
    def get_or_create_exchange(
        self,
        name: str,
        country: Optional[str] = None,
        website: Optional[str] = None,
        established_year: Optional[int] = None,
        trading_volume_usd: Optional[Decimal] = None,
    ) -> Exchange:
        """Get existing or create new exchange.

        Args:
            name: Exchange name
            country: Country of exchange
            website: Exchange website
            established_year: Year established
            trading_volume_usd: 24h trading volume in USD

        Returns:
            Exchange instance
        """
        exchange = self.session.query(Exchange).filter_by(name=name).first()
        if not exchange:
            exchange = Exchange(
                name=name,
                country=country,
                website=website,
                established_year=established_year,
                trading_volume_usd=trading_volume_usd,
            )
            self.session.add(exchange)
            self.session.commit()
        else:
            # Update trading volume
            if trading_volume_usd:
                exchange.trading_volume_usd = trading_volume_usd
                self.session.commit()

        return exchange

    def get_exchange_by_name(self, name: str) -> Optional[Exchange]:
        """Get exchange by name.

        Args:
            name: Exchange name

        Returns:
            Exchange or None
        """
        return self.session.query(Exchange).filter_by(name=name).first()

    def get_all_exchanges(self) -> List[Exchange]:
        """Get all exchanges.

        Returns:
            List of exchanges
        """
        return self.session.query(Exchange).all()

    # Trading pair operations
    def get_or_create_trading_pair(
        self,
        exchange_id: int,
        crypto_id: int,
        base_currency: str,
        quote_currency: str,
        is_active: bool = True,
    ) -> TradingPair:
        """Get existing or create new trading pair.

        Args:
            exchange_id: Exchange ID
            crypto_id: Cryptocurrency ID
            base_currency: Base asset symbol
            quote_currency: Quote asset symbol
            is_active: Whether pair is active

        Returns:
            TradingPair instance
        """
        pair = self.session.query(TradingPair).filter_by(
            exchange_id=exchange_id,
            crypto_id=crypto_id,
            base_currency=base_currency,
            quote_currency=quote_currency,
        ).first()

        if not pair:
            pair = TradingPair(
                exchange_id=exchange_id,
                crypto_id=crypto_id,
                base_currency=base_currency,
                quote_currency=quote_currency,
                is_active=is_active,
            )
            self.session.add(pair)
            self.session.commit()
        else:
            pair.is_active = is_active
            self.session.commit()

        return pair

    def get_active_trading_pairs(self) -> List[TradingPair]:
        """Get all active trading pairs.

        Returns:
            List of active trading pairs
        """
        return self.session.query(TradingPair).filter_by(is_active=True).all()

    # Price history operations
    def add_price_history(
        self,
        trading_pair_id: int,
        open_price: Decimal,
        high_price: Decimal,
        low_price: Decimal,
        close_price: Decimal,
        volume: Decimal,
        recorded_at: datetime,
    ) -> PriceHistory:
        """Add price history record.

        Args:
            trading_pair_id: Trading pair ID
            open_price: Opening price
            high_price: Highest price
            low_price: Lowest price
            close_price: Closing price
            volume: Trading volume
            recorded_at: Price record timestamp

        Returns:
            PriceHistory instance
        """
        price = PriceHistory(
            trading_pair_id=trading_pair_id,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume,
            recorded_at=recorded_at,
        )
        self.session.add(price)
        self.session.commit()

        return price

    def get_latest_price(self, trading_pair_id: int) -> Optional[PriceHistory]:
        """Get latest price for a trading pair.

        Args:
            trading_pair_id: Trading pair ID

        Returns:
            Latest PriceHistory or None
        """
        return (
            self.session.query(PriceHistory)
            .filter_by(trading_pair_id=trading_pair_id)
            .order_by(desc(PriceHistory.recorded_at))
            .first()
        )

    def get_price_history_range(
        self,
        trading_pair_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> List[PriceHistory]:
        """Get price history for a date range.

        Args:
            trading_pair_id: Trading pair ID
            start_date: Start datetime
            end_date: End datetime

        Returns:
            List of PriceHistory records
        """
        return (
            self.session.query(PriceHistory)
            .filter(
                and_(
                    PriceHistory.trading_pair_id == trading_pair_id,
                    PriceHistory.recorded_at >= start_date,
                    PriceHistory.recorded_at <= end_date,
                )
            )
            .order_by(PriceHistory.recorded_at)
            .all()
        )

    def get_price_history_last_hours(
        self,
        trading_pair_id: int,
        hours: int = 24,
    ) -> List[PriceHistory]:
        """Get price history for last N hours.

        Args:
            trading_pair_id: Trading pair ID
            hours: Number of hours

        Returns:
            List of PriceHistory records
        """
        start_date = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.session.query(PriceHistory)
            .filter(
                and_(
                    PriceHistory.trading_pair_id == trading_pair_id,
                    PriceHistory.recorded_at >= start_date,
                )
            )
            .order_by(PriceHistory.recorded_at)
            .all()
        )

    # Market sentiment operations
    def add_market_sentiment(
        self,
        crypto_id: int,
        sentiment_score: Decimal,
        sentiment_label: str,
        mentions_count: int,
        recorded_at: datetime,
    ) -> MarketSentiment:
        """Add market sentiment record.

        Args:
            crypto_id: Cryptocurrency ID
            sentiment_score: Score from -1.0 to 1.0
            sentiment_label: Label (negative, neutral, positive)
            mentions_count: Number of mentions
            recorded_at: Timestamp

        Returns:
            MarketSentiment instance
        """
        sentiment = MarketSentiment(
            crypto_id=crypto_id,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            mentions_count=mentions_count,
            recorded_at=recorded_at,
        )
        self.session.add(sentiment)
        self.session.commit()

        return sentiment

    def get_latest_sentiment(self, crypto_id: int) -> Optional[MarketSentiment]:
        """Get latest sentiment for cryptocurrency.

        Args:
            crypto_id: Cryptocurrency ID

        Returns:
            Latest MarketSentiment or None
        """
        return (
            self.session.query(MarketSentiment)
            .filter_by(crypto_id=crypto_id)
            .order_by(desc(MarketSentiment.recorded_at))
            .first()
        )

    # Market event operations
    def add_market_event(
        self,
        event_type: str,
        title: str,
        description: str,
        impact_level: str,
        event_date: datetime,
        crypto_id: Optional[int] = None,
    ) -> MarketEvent:
        """Add market event record.

        Args:
            event_type: Event type (fork, listing, regulation, etc.)
            title: Event title
            description: Event description
            impact_level: Impact level (low, medium, high)
            event_date: Event date
            crypto_id: Related cryptocurrency (optional)

        Returns:
            MarketEvent instance
        """
        event = MarketEvent(
            crypto_id=crypto_id,
            event_type=event_type,
            title=title,
            description=description,
            impact_level=impact_level,
            event_date=event_date,
        )
        self.session.add(event)
        self.session.commit()

        return event

    def get_recent_events(
        self,
        days: int = 30,
        crypto_id: Optional[int] = None,
    ) -> List[MarketEvent]:
        """Get recent market events.

        Args:
            days: Number of days in past
            crypto_id: Filter by cryptocurrency (optional)

        Returns:
            List of MarketEvent records
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = self.session.query(MarketEvent).filter(
            MarketEvent.event_date >= start_date.date()
        )

        if crypto_id:
            query = query.filter_by(crypto_id=crypto_id)

        return query.order_by(desc(MarketEvent.event_date)).all()

    # Batch operations
    def batch_add_prices(
        self,
        prices: List[tuple],
    ) -> int:
        """Add multiple price records in batch.

        Args:
            prices: List of (trading_pair_id, open, high, low, close, volume, recorded_at)

        Returns:
            Number of records added
        """
        price_records = [
            PriceHistory(
                trading_pair_id=p[0],
                open_price=p[1],
                high_price=p[2],
                low_price=p[3],
                close_price=p[4],
                volume=p[5],
                recorded_at=p[6],
            )
            for p in prices
        ]

        self.session.add_all(price_records)
        self.session.commit()

        return len(price_records)
