"""Wash sale tracking for tax compliance (30-day rule)."""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('leviathan.tax')


class WashSaleTracker:
    """Track wash sales to ensure tax compliance."""

    def __init__(self):
        self._sales = []

    def record_sale(self, symbol: str, date: datetime, loss: float):
        if loss < 0:
            self._sales.append({'symbol': symbol, 'date': date, 'loss': loss})

    def check_wash_sale(self, symbol: str, buy_date: datetime) -> bool:
        for sale in self._sales:
            if sale['symbol'] == symbol:
                days = abs((buy_date - sale['date']).days)
                if days <= 30:
                    logger.warning(f"Potential wash sale: {symbol} sold {sale['date'].date()}, buying {buy_date.date()}")
                    return True
        return False

    def get_wash_sales(self) -> list:
        return self._sales.copy()
