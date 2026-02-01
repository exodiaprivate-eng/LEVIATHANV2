"""News API integration for sentiment analysis."""
import logging
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

logger = logging.getLogger('leviathan.news')


class NewsClient:
    """Fetch financial news from Finnhub and Alpha Vantage."""

    def __init__(self, finnhub_key: str = '', alpha_vantage_key: str = ''):
        self.finnhub_key = finnhub_key
        self.alpha_vantage_key = alpha_vantage_key
        self.finnhub_url = "https://finnhub.io/api/v1"

    async def get_company_news(self, symbol: str, days: int = 7) -> list:
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        url = f"{self.finnhub_url}/company-news"
        params = {'symbol': symbol, 'from': start, 'to': end, 'token': self.finnhub_key}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    logger.warning(f"Finnhub returned {resp.status} for {symbol}")
                    return []
        except Exception as e:
            logger.error(f"News fetch failed for {symbol}: {e}")
            return []

    async def get_market_news(self, category: str = 'general') -> list:
        url = f"{self.finnhub_url}/news"
        params = {'category': category, 'token': self.finnhub_key}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    return await resp.json() if resp.status == 200 else []
        except Exception as e:
            logger.error(f"Market news fetch failed: {e}")
            return []

    async def get_general_sentiment(self, symbol: str) -> dict:
        """Get pre-computed sentiment from Finnhub."""
        url = f"{self.finnhub_url}/news-sentiment"
        params = {'symbol': symbol, 'token': self.finnhub_key}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    return await resp.json() if resp.status == 200 else {}
        except Exception as e:
            logger.error(f"Sentiment fetch failed for {symbol}: {e}")
            return {}
