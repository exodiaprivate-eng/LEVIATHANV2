"""
Pattern Day Trader (PDT) Protection Module.

Tracks day trades in a rolling 5-business-day window.
Accounts under $25K are limited to 3 day trades per 5 rolling business days.
"""
import logging
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DayTrade:
    """Record of a single day trade."""
    symbol: str
    buy_time: datetime
    sell_time: datetime
    quantity: float
    buy_price: float
    sell_price: float
    pnl: float = 0.0


class PDTTracker:
    """
    Tracks day trades to ensure PDT rule compliance.

    A day trade = buying and selling (or selling short and covering)
    the same security on the same trading day.

    Rule: Max 3 day trades in any rolling 5-business-day window
    for accounts under $25,000.
    """

    PDT_LIMIT = 3
    ROLLING_WINDOW_DAYS = 5
    PDT_ACCOUNT_THRESHOLD = 25_000.0

    def __init__(self, account_value: float = 0.0):
        self.account_value = account_value
        self._day_trades: List[DayTrade] = []
        self._intraday_buys: dict = {}  # symbol -> [(time, qty, price)]
        logger.info("PDTTracker initialized | account=$%.2f | exempt=%s",
                     account_value, account_value >= self.PDT_ACCOUNT_THRESHOLD)

    @property
    def is_exempt(self) -> bool:
        """Accounts >= $25K are exempt from PDT rule."""
        return self.account_value >= self.PDT_ACCOUNT_THRESHOLD

    def update_account_value(self, value: float):
        """Update account value for PDT threshold check."""
        self.account_value = value

    def record_buy(self, symbol: str, quantity: float, price: float,
                   timestamp: Optional[datetime] = None):
        """Record an intraday buy for potential day trade tracking."""
        ts = timestamp or datetime.now()
        if symbol not in self._intraday_buys:
            self._intraday_buys[symbol] = []
        self._intraday_buys[symbol].append((ts, quantity, price))
        logger.debug("Recorded buy: %s x%.1f @ $%.2f", symbol, quantity, price)

    def record_sell(self, symbol: str, quantity: float, price: float,
                    timestamp: Optional[datetime] = None):
        """
        Record a sell. If a same-day buy exists for this symbol,
        it counts as a day trade.
        """
        ts = timestamp or datetime.now()
        today = ts.date()

        if symbol in self._intraday_buys:
            remaining_qty = quantity
            buys_today = [b for b in self._intraday_buys[symbol]
                          if b[0].date() == today]

            for buy_time, buy_qty, buy_price in buys_today:
                if remaining_qty <= 0:
                    break
                matched_qty = min(remaining_qty, buy_qty)
                pnl = (price - buy_price) * matched_qty

                trade = DayTrade(
                    symbol=symbol,
                    buy_time=buy_time,
                    sell_time=ts,
                    quantity=matched_qty,
                    buy_price=buy_price,
                    sell_price=price,
                    pnl=pnl,
                )
                self._day_trades.append(trade)
                remaining_qty -= matched_qty
                logger.warning(
                    "DAY TRADE RECORDED: %s x%.1f | PnL=$%.2f | Count=%d/%d",
                    symbol, matched_qty, pnl,
                    self.get_day_trade_count(), self.PDT_LIMIT
                )

    def would_be_day_trade(self, symbol: str) -> bool:
        """
        Check if selling this symbol now would constitute a day trade.
        Returns True if the symbol was bought today.
        """
        today = datetime.now().date()
        if symbol in self._intraday_buys:
            return any(b[0].date() == today for b in self._intraday_buys[symbol])
        return False

    def can_day_trade(self) -> bool:
        """
        Check if another day trade is allowed.
        Returns True if exempt or under the PDT limit.
        """
        if self.is_exempt:
            return True
        return self.get_day_trade_count() < self.PDT_LIMIT

    def get_day_trade_count(self) -> int:
        """Count day trades in the rolling 5-business-day window."""
        cutoff = datetime.now() - timedelta(days=7)  # 7 calendar days ~ 5 business days
        return sum(1 for t in self._day_trades if t.sell_time >= cutoff)

    def get_remaining_day_trades(self) -> int:
        """How many day trades are still allowed in current window."""
        if self.is_exempt:
            return 999
        return max(0, self.PDT_LIMIT - self.get_day_trade_count())

    def get_day_trades(self, days: int = 7) -> List[DayTrade]:
        """Get recent day trades."""
        cutoff = datetime.now() - timedelta(days=days)
        return [t for t in self._day_trades if t.sell_time >= cutoff]

    def cleanup_old_records(self, days: int = 14):
        """Remove day trade records older than N days."""
        cutoff = datetime.now() - timedelta(days=days)
        self._day_trades = [t for t in self._day_trades if t.sell_time >= cutoff]

        for symbol in list(self._intraday_buys.keys()):
            self._intraday_buys[symbol] = [
                b for b in self._intraday_buys[symbol] if b[0] >= cutoff
            ]
            if not self._intraday_buys[symbol]:
                del self._intraday_buys[symbol]

    def get_status(self) -> dict:
        """Get PDT status summary."""
        return {
            "account_value": self.account_value,
            "is_exempt": self.is_exempt,
            "day_trades_count": self.get_day_trade_count(),
            "remaining_day_trades": self.get_remaining_day_trades(),
            "can_day_trade": self.can_day_trade(),
            "recent_day_trades": [
                {
                    "symbol": t.symbol,
                    "buy_time": t.buy_time.isoformat(),
                    "sell_time": t.sell_time.isoformat(),
                    "pnl": t.pnl,
                }
                for t in self.get_day_trades()
            ],
        }
