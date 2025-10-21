"""Market sentiment data transformation utilities."""

from decimal import Decimal
from typing import Any, Dict

import structlog

logger = structlog.get_logger(__name__)


class SentimentTransformer:
    """Transform sentiment data into database format."""

    @staticmethod
    def determine_sentiment_label(score: float) -> str:
        """Determine sentiment label from score.

        Args:
            score: Sentiment score from -1.0 to 1.0

        Returns:
            Sentiment label
        """
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "negative"
        else:
            return "neutral"

    @staticmethod
    def transform_coingecko_trending(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform CoinGecko trending data.

        Args:
            data: CoinGecko trending coin data

        Returns:
            Transformed sentiment data
        """
        # CoinGecko trending indicates positive sentiment
        sentiment_score = Decimal("0.7")  # Trending = positive
        
        return {
            "symbol": data.get("item", {}).get("symbol", "").upper(),
            "name": data.get("item", {}).get("name", ""),
            "sentiment_score": sentiment_score,
            "sentiment_label": SentimentTransformer.determine_sentiment_label(float(sentiment_score)),
            "mentions_count": 1,  # Being in trending list = at least 1 mention
        }

    @staticmethod
    def transform_social_sentiment(
        mentions_count: int,
        positive_ratio: float,
    ) -> Dict[str, Any]:
        """Transform generic social sentiment data.

        Args:
            mentions_count: Total mentions
            positive_ratio: Ratio of positive mentions (0-1)

        Returns:
            Transformed sentiment data
        """
        # Convert positive ratio to sentiment score (-1.0 to 1.0)
        sentiment_score = Decimal(str((positive_ratio * 2) - 1))
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": SentimentTransformer.determine_sentiment_label(float(sentiment_score)),
            "mentions_count": mentions_count,
        }

    @staticmethod
    def calculate_composite_sentiment(
        sentiment_scores: list[Decimal],
    ) -> Dict[str, Any]:
        """Calculate composite sentiment from multiple sources.

        Args:
            sentiment_scores: List of sentiment scores

        Returns:
            Composite sentiment data
        """
        if not sentiment_scores:
            return {
                "sentiment_score": Decimal("0"),
                "sentiment_label": "neutral",
            }
        
        avg_score = sum(sentiment_scores) / len(sentiment_scores)
        
        return {
            "sentiment_score": avg_score,
            "sentiment_label": SentimentTransformer.determine_sentiment_label(float(avg_score)),
        }

    @staticmethod
    def transform_market_event(
        event_type: str,
        impact: str,
    ) -> Dict[str, Any]:
        """Transform market event to sentiment impact.

        Args:
            event_type: Type of event
            impact: Impact level

        Returns:
            Sentiment impact data
        """
        impact_to_sentiment = {
            "high": {"positive": Decimal("0.8"), "neutral": Decimal("0"), "negative": Decimal("-0.8")},
            "medium": {"positive": Decimal("0.5"), "neutral": Decimal("0"), "negative": Decimal("-0.5")},
            "low": {"positive": Decimal("0.3"), "neutral": Decimal("0"), "negative": Decimal("-0.3")},
        }
        
        sentiment_score = impact_to_sentiment.get(impact, {}).get("positive", Decimal("0"))
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": SentimentTransformer.determine_sentiment_label(float(sentiment_score)),
            "event_type": event_type,
        }
