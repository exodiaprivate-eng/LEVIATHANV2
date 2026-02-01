"""Market hours and timezone utilities."""
from datetime import datetime, time
import pytz

ET = pytz.timezone('US/Eastern')
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)
EXTENDED_OPEN = time(4, 0)
EXTENDED_CLOSE = time(20, 0)


def now_et() -> datetime:
    return datetime.now(ET)


def is_market_open() -> bool:
    now = now_et()
    if now.weekday() >= 5:
        return False
    return MARKET_OPEN <= now.time() <= MARKET_CLOSE


def is_extended_hours() -> bool:
    now = now_et()
    if now.weekday() >= 5:
        return False
    return EXTENDED_OPEN <= now.time() <= EXTENDED_CLOSE


def time_until_close() -> float:
    """Minutes until market close."""
    now = now_et()
    close = now.replace(hour=16, minute=0, second=0)
    diff = (close - now).total_seconds() / 60
    return max(0, diff)


def next_market_open() -> datetime:
    now = now_et()
    day = now
    while True:
        day = day.replace(hour=9, minute=30, second=0, microsecond=0)
        if day > now and day.weekday() < 5:
            return day
        day = day.replace(hour=0) + __import__('datetime').timedelta(days=1)
