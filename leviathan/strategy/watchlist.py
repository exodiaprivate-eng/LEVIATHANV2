"""Watchlist management."""
import logging
import json
from pathlib import Path

logger = logging.getLogger('leviathan.watchlist')

DEFAULT_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
                  'AMD', 'INTC', 'CRM', 'NFLX', 'PYPL', 'SQ', 'SHOP',
                  'SPY', 'QQQ', 'IWM', 'DIA']


class WatchlistManager:
    """Manage trading watchlist with persistence."""

    def __init__(self, path: str = "watchlist.json"):
        self.path = Path(path)
        self.symbols = self._load()

    def _load(self) -> list:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return DEFAULT_STOCKS.copy()

    def _save(self):
        self.path.write_text(json.dumps(self.symbols, indent=2))

    def add(self, symbol: str):
        s = symbol.upper()
        if s not in self.symbols:
            self.symbols.append(s)
            self._save()

    def remove(self, symbol: str):
        s = symbol.upper()
        if s in self.symbols:
            self.symbols.remove(s)
            self._save()

    def get_watchlist(self) -> list:
        return self.symbols.copy()
