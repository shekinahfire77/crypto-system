"""SQLAlchemy ORM models matching the crypto_market database schema."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    VARCHAR,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List


class Base(DeclarativeBase):
    """SQLAlchemy base class for all models."""

    pass


class Cryptocurrency(Base):
    """Model for cryptocurrencies table."""

    __tablename__ = "cryptocurrencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(VARCHAR(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    trading_pairs: Mapped[List["TradingPair"]] = relationship(
        "TradingPair", back_populates="cryptocurrency"
    )
    market_sentiment: Mapped[List["MarketSentiment"]] = relationship(
        "MarketSentiment", back_populates="cryptocurrency"
    )
    market_events: Mapped[List["MarketEvent"]] = relationship(
        "MarketEvent", back_populates="cryptocurrency"
    )

    __table_args__ = (
        Index("idx_cryptocurrencies_symbol", "symbol"),
    )


class Exchange(Base):
    """Model for exchanges table."""

    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(100), unique=True, nullable=False)
    country: Mapped[str | None] = mapped_column(VARCHAR(50))
    website: Mapped[str | None] = mapped_column(VARCHAR(255))
    established_year: Mapped[int | None] = mapped_column(Integer)
    trading_volume_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(20, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    trading_pairs: Mapped[List["TradingPair"]] = relationship(
        "TradingPair", back_populates="exchange"
    )

    __table_args__ = (
        Index("idx_exchanges_name", "name"),
    )


class TradingPair(Base):
    """Model for trading_pairs table."""

    __tablename__ = "trading_pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exchange_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exchanges.id"), nullable=False
    )
    crypto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cryptocurrencies.id"), nullable=False
    )
    base_currency: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    quote_currency: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    exchange: Mapped["Exchange"] = relationship(
        "Exchange", back_populates="trading_pairs"
    )
    cryptocurrency: Mapped["Cryptocurrency"] = relationship(
        "Cryptocurrency", back_populates="trading_pairs"
    )
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="trading_pair"
    )

    __table_args__ = (
        UniqueConstraint(
            "exchange_id",
            "crypto_id",
            "base_currency",
            "quote_currency",
            name="uq_trading_pair",
        ),
        Index("idx_trading_pairs_exchange", "exchange_id"),
        Index("idx_trading_pairs_crypto", "crypto_id"),
    )


class PriceHistory(Base):
    """Model for price_history table."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trading_pair_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("trading_pairs.id"), nullable=False
    )
    open_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    trading_pair: Mapped["TradingPair"] = relationship(
        "TradingPair", back_populates="price_history"
    )

    __table_args__ = (
        Index("idx_price_history_pair", "trading_pair_id"),
        Index("idx_price_history_recorded_at", "recorded_at"),
    )


class MarketSentiment(Base):
    """Model for market_sentiment table."""

    __tablename__ = "market_sentiment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    crypto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cryptocurrencies.id"), nullable=False
    )
    sentiment_score: Mapped[Decimal] = mapped_column(DECIMAL(3, 2), nullable=False)
    sentiment_label: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    mentions_count: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    cryptocurrency: Mapped["Cryptocurrency"] = relationship(
        "Cryptocurrency", back_populates="market_sentiment"
    )

    __table_args__ = (
        Index("idx_market_sentiment_crypto", "crypto_id"),
        Index("idx_market_sentiment_recorded_at", "recorded_at"),
    )


class MarketEvent(Base):
    """Model for market_events table."""

    __tablename__ = "market_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    crypto_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("cryptocurrencies.id")
    )
    event_type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    impact_level: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    event_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    cryptocurrency: Mapped["Cryptocurrency | None"] = relationship(
        "Cryptocurrency", back_populates="market_events"
    )

    __table_args__ = (
        Index("idx_market_events_crypto", "crypto_id"),
        Index("idx_market_events_event_date", "event_date"),
    )
