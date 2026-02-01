"""Sentiment score aggregation with time decay."""
import math
import logging
from datetime import datetime

logger = logging.getLogger('leviathan.sentiment')


def apply_sentiment_decay(sentiment_score: float, published_time: datetime,
                          half_life_hours: float = 6.0) -> float:
    """Exponential decay - news >24h old has minimal impact."""
    hours_old = (datetime.now() - published_time).total_seconds() / 3600
    decay = math.exp(-0.693 * hours_old / half_life_hours)
    return sentiment_score * decay


def aggregate_sentiment(news_items: list, analyzer) -> float:
    """Aggregate multiple news items into single sentiment score."""
    if not news_items:
        return 0.0
    scores = []
    for item in news_items:
        text = item.get('headline', item.get('clean_text', ''))
        if not text:
            continue
        score = analyzer.get_sentiment_score(text)
        ts = item.get('datetime', item.get('published'))
        if isinstance(ts, (int, float)):
            pub = datetime.fromtimestamp(ts)
        elif isinstance(ts, str):
            try:
                pub = datetime.fromisoformat(ts)
            except ValueError:
                pub = datetime.now()
        else:
            pub = datetime.now()
        scores.append(apply_sentiment_decay(score, pub))
    return sum(scores) / len(scores) if scores else 0.0


class SentimentAggregator:
    """Full sentiment aggregation pipeline."""

    def __init__(self, analyzer, news_client, news_processor):
        self.analyzer = analyzer
        self.news = news_client
        self.processor = news_processor

    async def get_symbol_sentiment(self, symbol: str) -> float:
        raw_news = await self.news.get_company_news(symbol, days=3)
        processed = self.processor.process_news_batch(raw_news, symbol)
        return aggregate_sentiment(processed, self.analyzer)

    async def get_market_sentiment(self) -> float:
        raw_news = await self.news.get_market_news()
        processed = self.processor.process_news_batch(raw_news)
        return aggregate_sentiment(processed, self.analyzer)
