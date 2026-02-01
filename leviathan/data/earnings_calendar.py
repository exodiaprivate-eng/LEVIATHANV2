"""Earnings dates tracking to avoid holding through earnings."""
import logging
import time
from datetime import datetime, timedelta, date

logger = logging.getLogger('leviathan.earnings')

# Cache TTL: 6 hours
CACHE_TTL = 6 * 3600


class EarningsCalendar:
    """Track earnings dates to manage risk around announcements."""

    def __init__(self, news_client=None, watchlist: list = None):
        self.news_client = news_client
        self.watchlist = watchlist or []
        self._cache = {}  # symbol -> {'earnings_date': date|None, 'fetched_at': float}

    def _is_cache_valid(self, symbol: str) -> bool:
        entry = self._cache.get(symbol)
        return entry is not None and (time.time() - entry.get('fetched_at', 0)) < CACHE_TTL

    def _fetch_earnings(self, symbol: str) -> date | None:
        """Fetch next earnings date for symbol. Uses yfinance, falls back to Alpha Vantage."""
        if self._is_cache_valid(symbol):
            return self._cache[symbol]['earnings_date']

        earnings_date = None

        # Try yfinance
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            cal = ticker.calendar
            if cal is not None:
                # yfinance returns different formats depending on version
                if isinstance(cal, dict):
                    ed = cal.get('Earnings Date')
                    if ed:
                        if isinstance(ed, list) and len(ed) > 0:
                            earnings_date = ed[0].date() if hasattr(ed[0], 'date') else ed[0]
                        elif hasattr(ed, 'date'):
                            earnings_date = ed.date()
                elif hasattr(cal, 'iloc'):
                    # DataFrame format
                    if 'Earnings Date' in cal.columns:
                        vals = cal['Earnings Date'].dropna()
                        if len(vals) > 0:
                            v = vals.iloc[0]
                            earnings_date = v.date() if hasattr(v, 'date') else v
                    elif len(cal) > 0:
                        # Some versions use index
                        try:
                            idx = cal.index.tolist()
                            if 'Earnings Date' in idx:
                                row = cal.loc['Earnings Date']
                                v = row.iloc[0] if hasattr(row, 'iloc') else row
                                if hasattr(v, 'date'):
                                    earnings_date = v.date()
                        except Exception:
                            pass

            if earnings_date:
                logger.info(f"Got earnings date for {symbol} from yfinance: {earnings_date}")
        except ImportError:
            logger.debug("yfinance not available, skipping")
        except Exception as e:
            logger.warning(f"yfinance earnings fetch failed for {symbol}: {e}")

        # Normalize to date object
        if earnings_date is not None:
            if isinstance(earnings_date, datetime):
                earnings_date = earnings_date.date()
            elif isinstance(earnings_date, str):
                try:
                    earnings_date = datetime.strptime(earnings_date, '%Y-%m-%d').date()
                except ValueError:
                    earnings_date = None

        self._cache[symbol] = {
            'earnings_date': earnings_date,
            'fetched_at': time.time(),
        }
        return earnings_date

    def get_earnings_date(self, symbol: str) -> date | None:
        """Get next earnings date for a symbol."""
        return self._fetch_earnings(symbol)

    def is_earnings_soon(self, symbol: str, days: int = 5) -> bool:
        """Check if symbol has earnings within N days."""
        earn_date = self._fetch_earnings(symbol)
        if earn_date is None:
            return False
        today = date.today()
        delta = (earn_date - today).days
        return 0 <= delta <= days

    def has_earnings_soon(self, symbol: str, days: int = 3) -> bool:
        """Backward-compatible alias for is_earnings_soon."""
        return self.is_earnings_soon(symbol, days)

    def get_earnings_this_week(self, symbols: list = None) -> list:
        """Get symbols with earnings this week from provided list or watchlist."""
        check_symbols = symbols or self.watchlist
        results = []
        for s in check_symbols:
            earn_date = self._fetch_earnings(s)
            if earn_date is None:
                continue
            today = date.today()
            # This week = next 7 days
            if 0 <= (earn_date - today).days <= 7:
                results.append({'symbol': s, 'date': earn_date.isoformat()})
        return results

    def get_upcoming_earnings(self, symbols: list, days: int = 7) -> list:
        """Get symbols with earnings within N days."""
        results = []
        for s in symbols:
            if self.is_earnings_soon(s, days):
                results.append({'symbol': s, 'date': self._cache[s]['earnings_date'].isoformat()})
        return results

    def should_avoid_entry(self, symbol: str) -> bool:
        """Check if entry should be avoided due to imminent earnings."""
        return self.is_earnings_soon(symbol, days=2)
