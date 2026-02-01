"""Automatic data fetching for learning and analysis."""
import asyncio
import logging
import os
import time
from pathlib import Path

import pandas as pd

logger = logging.getLogger('leviathan.fetcher')

DATA_DIR = Path(__file__).parent.parent / 'storage' / 'market_data'


class AutoDataFetcher:
    """AI fetches its own data for learning and analysis."""

    def __init__(self, alpaca_client, news_client, learning_db):
        self.alpaca = alpaca_client
        self.news = news_client
        self.db = learning_db
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    async def fetch_learning_data(self, symbols: list):
        tasks = [
            self._fetch_price_data(symbols),
            self._fetch_news_data(symbols),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Fetch error: {r}")

    async def _fetch_price_data(self, symbols: list):
        for symbol in symbols:
            try:
                bars = self.alpaca.get_historical_bars(symbol, days=30)
                if bars is not None:
                    self._save_to_parquet(symbol, 'price', bars)
            except Exception as e:
                logger.error(f"Price fetch failed for {symbol}: {e}")

    async def _fetch_news_data(self, symbols: list):
        for symbol in symbols:
            try:
                news = await self.news.get_company_news(symbol, days=7)
                if news is not None:
                    self._save_to_parquet(symbol, 'news', news)
            except Exception as e:
                logger.error(f"News fetch failed for {symbol}: {e}")

    def _save_to_parquet(self, symbol: str, data_type: str, data):
        """Persist fetched data to parquet files."""
        try:
            filepath = DATA_DIR / f"{symbol}_{data_type}.parquet"
            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                logger.warning(f"Unsupported data type for {symbol} {data_type}: {type(data)}")
                return

            if filepath.exists():
                existing = pd.read_parquet(filepath)
                df = pd.concat([existing, df]).drop_duplicates().reset_index(drop=True)

            df.to_parquet(filepath, index=False)
            logger.info(f"Saved {len(df)} rows to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save {symbol} {data_type} to parquet: {e}")

    def run_continuous(self, symbols: list, interval_minutes: int = 15):
        while True:
            try:
                asyncio.run(self.fetch_learning_data(symbols))
            except Exception as e:
                logger.error(f"Data fetch cycle failed: {e}")
            time.sleep(interval_minutes * 60)
