"""Real-time market data streaming via Alpaca WebSocket."""
import logging
import asyncio
from typing import Callable

from alpaca.data.live import StockDataStream

logger = logging.getLogger('leviathan.stream')


class MarketDataStream:
    """Real-time bar and quote streaming from Alpaca."""

    def __init__(self, api_key: str, secret_key: str):
        self.stream = StockDataStream(api_key, secret_key)
        self.bar_callbacks: list[Callable] = []
        self.quote_callbacks: list[Callable] = []
        self.trade_callbacks: list[Callable] = []
        self._running = False

    def register_bar_callback(self, callback: Callable):
        self.bar_callbacks.append(callback)

    def register_quote_callback(self, callback: Callable):
        self.quote_callbacks.append(callback)

    async def _handle_bar(self, bar):
        for cb in self.bar_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(bar)
                else:
                    cb(bar)
            except Exception as e:
                logger.error(f"Bar callback error: {e}")

    async def _handle_quote(self, quote):
        for cb in self.quote_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(quote)
                else:
                    cb(quote)
            except Exception as e:
                logger.error(f"Quote callback error: {e}")

    def subscribe_bars(self, symbols: list):
        self.stream.subscribe_bars(self._handle_bar, *symbols)
        logger.info(f"Subscribed to bars: {symbols}")

    def subscribe_quotes(self, symbols: list):
        self.stream.subscribe_quotes(self._handle_quote, *symbols)
        logger.info(f"Subscribed to quotes: {symbols}")

    def unsubscribe_bars(self, symbols: list):
        self.stream.unsubscribe_bars(*symbols)

    def run(self):
        """Start the stream (blocking)."""
        self._running = True
        logger.info("Starting market data stream...")
        self.stream.run()

    def stop(self):
        self._running = False
        self.stream.stop()
        logger.info("Market data stream stopped")
