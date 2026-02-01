"""Economic events tracking with hardcoded FOMC/CPI/NFP schedules and optional API."""
import logging
import time
from datetime import datetime, timedelta, date

logger = logging.getLogger('leviathan.economic')

# High-impact recurring events
HIGH_IMPACT_EVENTS = [
    'FOMC', 'CPI', 'Non-Farm Payrolls', 'GDP', 'PPI',
    'Retail Sales', 'Consumer Confidence', 'PMI',
]

# Known 2025 FOMC meeting dates (announcement days)
FOMC_DATES_2025 = [
    date(2025, 1, 29), date(2025, 3, 19), date(2025, 5, 7),
    date(2025, 6, 18), date(2025, 7, 30), date(2025, 9, 17),
    date(2025, 10, 29), date(2025, 12, 17),
]

# Known 2026 FOMC meeting dates (estimated)
FOMC_DATES_2026 = [
    date(2026, 1, 28), date(2026, 3, 18), date(2026, 5, 6),
    date(2026, 6, 17), date(2026, 7, 29), date(2026, 9, 16),
    date(2026, 10, 28), date(2026, 12, 16),
]

ALL_FOMC_DATES = FOMC_DATES_2025 + FOMC_DATES_2026


def _generate_recurring_events(start: date, end: date) -> list:
    """Generate hardcoded high-impact economic event schedule.

    CPI: ~13th of each month
    NFP: first Friday of each month
    GDP: last week of Jan/Apr/Jul/Oct (advance estimate)
    """
    events = []

    # FOMC dates
    for d in ALL_FOMC_DATES:
        if start <= d <= end:
            events.append({'date': d.isoformat(), 'event': 'FOMC Rate Decision', 'impact': 'high'})

    current = start.replace(day=1)
    while current <= end:
        year, month = current.year, current.month

        # CPI - typically around the 13th
        cpi_date = date(year, month, 13)
        # Adjust to weekday
        while cpi_date.weekday() >= 5:
            cpi_date += timedelta(days=1)
        if start <= cpi_date <= end:
            events.append({'date': cpi_date.isoformat(), 'event': 'CPI Report', 'impact': 'high'})

        # NFP - first Friday of month
        first_day = date(year, month, 1)
        days_until_friday = (4 - first_day.weekday()) % 7
        nfp_date = first_day + timedelta(days=days_until_friday)
        if start <= nfp_date <= end:
            events.append({'date': nfp_date.isoformat(), 'event': 'Non-Farm Payrolls', 'impact': 'high'})

        # GDP - last Thursday of Jan, Apr, Jul, Oct
        if month in (1, 4, 7, 10):
            last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
            d = last_day
            while d.weekday() != 3:  # Thursday
                d -= timedelta(days=1)
            if start <= d <= end:
                events.append({'date': d.isoformat(), 'event': 'GDP Report', 'impact': 'high'})

        # PPI - ~15th of each month
        ppi_date = date(year, month, 15)
        while ppi_date.weekday() >= 5:
            ppi_date += timedelta(days=1)
        if start <= ppi_date <= end:
            events.append({'date': ppi_date.isoformat(), 'event': 'PPI Report', 'impact': 'medium'})

        # Advance to next month
        if month == 12:
            current = date(year + 1, 1, 1)
        else:
            current = date(year, month + 1, 1)

    events.sort(key=lambda e: e['date'])
    return events


class EconomicCalendar:
    """Track economic events that may impact trading."""

    CACHE_TTL = 6 * 3600  # 6 hours

    def __init__(self, news_client=None, alpha_vantage_key: str = None):
        self.news_client = news_client
        self.alpha_vantage_key = alpha_vantage_key
        self._cached_events = []
        self._cache_timestamp = 0

    def _is_cache_valid(self) -> bool:
        return self._cached_events and (time.time() - self._cache_timestamp) < self.CACHE_TTL

    def _fetch_events(self, days_ahead: int = 30) -> list:
        """Fetch events: try Alpha Vantage API, fallback to hardcoded schedule."""
        if self._is_cache_valid():
            return self._cached_events

        today = date.today()
        end = today + timedelta(days=days_ahead)

        events = []

        # Try Alpha Vantage if key provided
        if self.alpha_vantage_key:
            try:
                import requests
                url = (
                    f"https://www.alphavantage.co/query?function=ECONOMIC_CALENDAR"
                    f"&apikey={self.alpha_vantage_key}"
                )
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get('data', []):
                        ev_date = item.get('date', '')
                        if ev_date and today.isoformat() <= ev_date <= end.isoformat():
                            name = item.get('name', item.get('event', 'Unknown'))
                            impact = 'high' if any(k in name.upper() for k in
                                                    ['FOMC', 'CPI', 'PAYROLL', 'NFP', 'GDP']) else 'medium'
                            events.append({'date': ev_date, 'event': name, 'impact': impact})
                    if events:
                        logger.info(f"Fetched {len(events)} events from Alpha Vantage")
                        self._cached_events = events
                        self._cache_timestamp = time.time()
                        return events
            except Exception as e:
                logger.warning(f"Alpha Vantage fetch failed, using hardcoded schedule: {e}")

        # Fallback: hardcoded schedule
        events = _generate_recurring_events(today, end)
        logger.info(f"Generated {len(events)} hardcoded economic events")
        self._cached_events = events
        self._cache_timestamp = time.time()
        return events

    def get_upcoming_events(self, days_ahead: int = 7) -> list:
        """Return list of upcoming events within days_ahead."""
        all_events = self._fetch_events(days_ahead=days_ahead)
        cutoff = (date.today() + timedelta(days=days_ahead)).isoformat()
        today_str = date.today().isoformat()
        return [e for e in all_events if today_str <= e['date'] <= cutoff]

    def is_high_impact_today(self) -> bool:
        """Check if there's a high-impact event (FOMC/CPI/NFP/GDP) today."""
        today_str = date.today().isoformat()
        events = self._fetch_events(days_ahead=1)
        return any(e['date'] == today_str and e['impact'] == 'high' for e in events)

    def is_high_impact_day(self, date_check: datetime = None) -> bool:
        """Check if a given date is a high-impact day."""
        d = (date_check or datetime.now()).date() if isinstance(date_check, datetime) else (date_check or date.today())
        d_str = d.isoformat() if isinstance(d, date) else d
        events = self._fetch_events(days_ahead=60)
        return any(e['date'] == d_str and e['impact'] == 'high' for e in events)

    def get_fomc_dates(self) -> list:
        """Return known FOMC meeting dates."""
        today = date.today()
        return [d for d in ALL_FOMC_DATES if d >= today]

    def should_reduce_exposure(self) -> bool:
        """Check if exposure should be reduced due to upcoming high-impact events."""
        return self.is_high_impact_today()
