"""Tests for data transformers."""

import pytest
from datetime import datetime
from decimal import Decimal

from transformers.price_transformer import PriceTransformer
from transformers.metadata_transformer import MetadataTransformer
from transformers.sentiment_transformer import SentimentTransformer


class TestPriceTransformer:
    """Test price data transformation."""

    def test_transform_coingecko_market_data(self):
        """Test transforming CoinGecko market data."""
        data = {
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 45000.50,
            "market_cap": 900000000000,
            "market_cap_rank": 1,
            "total_volume": 50000000000,
            "high_24h": 46000,
            "low_24h": 44000,
            "price_change_24h": 500,
            "price_change_percentage_24h": 1.12,
        }

        transformed = PriceTransformer.transform_coingecko_market_data(data)

        assert transformed["symbol"] == "BTC"
        assert transformed["name"] == "Bitcoin"
        assert transformed["current_price"] == Decimal("45000.50")
        assert transformed["market_cap_rank"] == 1

    def test_transform_coingecko_ohlc(self):
        """Test transforming CoinGecko OHLC data."""
        ohlc_data = [
            [1635360000000, 43000, 44000, 42000, 43500],
            [1635446400000, 43500, 45000, 43000, 44500],
        ]

        transformed = PriceTransformer.transform_coingecko_ohlc(ohlc_data, trading_pair_id=1)

        assert len(transformed) == 2
        assert transformed[0]["open_price"] == Decimal("43000")
        assert transformed[0]["close_price"] == Decimal("43500")
        assert transformed[0]["trading_pair_id"] == 1

    def test_transform_cmc_quote(self):
        """Test transforming CMC quote data."""
        data = {
            "symbol": "ETH",
            "name": "Ethereum",
            "cmc_rank": 2,
            "quote": {
                "USD": {
                    "price": 3000.50,
                    "market_cap": 360000000000,
                    "volume_24h": 20000000000,
                    "high_24h": 3100,
                    "low_24h": 2900,
                    "price_change_24h": 50,
                }
            },
        }

        transformed = PriceTransformer.transform_cmc_quote(data)

        assert transformed["symbol"] == "ETH"
        assert transformed["current_price"] == Decimal("3000.50")
        assert transformed["market_cap_rank"] == 2


class TestMetadataTransformer:
    """Test metadata transformation."""

    def test_transform_coingecko_coin_details(self):
        """Test transforming CoinGecko coin details."""
        data = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "description": {"en": "Bitcoin is a cryptocurrency"},
            "links": {
                "homepage": ["https://bitcoin.org"],
                "repos_url": {"github": ["https://github.com/bitcoin"]},
                "twitter_screen_handle": "bitcoin",
                "subreddit_url": "https://reddit.com/r/bitcoin",
            },
            "community_score": 85.5,
            "developer_score": 90.2,
        }

        transformed = MetadataTransformer.transform_coingecko_coin_details(data)

        assert transformed["symbol"] == "BTC"
        assert transformed["name"] == "Bitcoin"
        assert "Bitcoin is a cryptocurrency" in transformed["description"]
        assert transformed["community_score"] == 85.5

    def test_transform_coingecko_exchange(self):
        """Test transforming CoinGecko exchange data."""
        data = {
            "id": "binance",
            "name": "Binance",
            "country": "Malta",
            "url": "https://www.binance.com",
            "image": "https://assets.coingecko.com/...",
            "trust_score": 10,
            "trust_score_rank": 1,
            "trade_volume_24h_btc": 500000,
            "year_established": 2017,
        }

        transformed = MetadataTransformer.transform_coingecko_exchange(data)

        assert transformed["name"] == "Binance"
        assert transformed["country"] == "Malta"
        assert transformed["trust_score"] == 10


class TestSentimentTransformer:
    """Test sentiment data transformation."""

    def test_determine_sentiment_label_positive(self):
        """Test positive sentiment label."""
        label = SentimentTransformer.determine_sentiment_label(0.7)
        assert label == "positive"

    def test_determine_sentiment_label_negative(self):
        """Test negative sentiment label."""
        label = SentimentTransformer.determine_sentiment_label(-0.7)
        assert label == "negative"

    def test_determine_sentiment_label_neutral(self):
        """Test neutral sentiment label."""
        label = SentimentTransformer.determine_sentiment_label(0.1)
        assert label == "neutral"

    def test_transform_coingecko_trending(self):
        """Test transforming CoinGecko trending data."""
        data = {
            "item": {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
            }
        }

        transformed = SentimentTransformer.transform_coingecko_trending(data)

        assert transformed["symbol"] == "BTC"
        assert transformed["sentiment_label"] == "positive"
        assert transformed["sentiment_score"] == Decimal("0.7")

    def test_calculate_composite_sentiment(self):
        """Test calculating composite sentiment."""
        scores = [Decimal("0.5"), Decimal("0.8"), Decimal("0.6")]

        result = SentimentTransformer.calculate_composite_sentiment(scores)

        assert result["sentiment_label"] == "positive"
        # Use approximate comparison for Decimal
        assert abs(result["sentiment_score"] - Decimal("0.6333333333")) < Decimal("0.0001")

    def test_calculate_composite_sentiment_empty(self):
        """Test composite sentiment with empty list."""
        result = SentimentTransformer.calculate_composite_sentiment([])

        assert result["sentiment_label"] == "neutral"
        assert result["sentiment_score"] == Decimal("0")
