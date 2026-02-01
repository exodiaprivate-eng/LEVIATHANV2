"""
Risk Manager Module.

Central risk management with pre-trade checks, position limits,
and portfolio-level risk controls.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, date
from typing import Tuple, Optional, Dict, List

from leviathan.risk.pdt_tracker import PDTTracker
from leviathan.risk.circuit_breaker import CircuitBreaker
from leviathan.risk.drawdown_scaler import DrawdownScaler

logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """Configurable risk parameters."""
    max_position_pct: float = 0.05       # Max 5% of portfolio per position
    max_portfolio_risk: float = 0.02     # Max 2% portfolio risk per trade
    max_daily_loss_pct: float = 0.03     # Max 3% daily loss
    max_drawdown_pct: float = 0.10       # Max 10% drawdown from peak
    max_correlation: float = 0.70        # Max correlation between positions
    max_sector_exposure: float = 0.30    # Max 30% in any single sector
    max_open_positions: int = 10         # Max concurrent positions
    max_single_loss_pct: float = 0.02    # Max 2% loss per trade (stop loss)


class RiskManager:
    """
    Central risk management engine.

    Performs pre-trade checks, tracks daily P&L, enforces position limits,
    and coordinates with PDT tracker and circuit breaker.
    """

    def __init__(self, config=None, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.config = config

        # Sub-components
        self.pdt_tracker = PDTTracker()
        self.circuit_breaker = CircuitBreaker(
            max_daily_loss_pct=self.limits.max_daily_loss_pct
        )
        self.drawdown_scaler = DrawdownScaler(
            max_drawdown_pct=self.limits.max_drawdown_pct
        )

        # Daily tracking
        self._daily_pnl = 0.0
        self._daily_trades: List[dict] = []
        self._current_positions: Dict[str, dict] = {}
        self._account_value = 0.0
        self._peak_value = 0.0
        self._last_reset_date: Optional[date] = None

        logger.info("RiskManager initialized with limits: %s", self.limits)

    def update_account(self, value: float, positions: Dict[str, dict]):
        """Update account value and current positions."""
        self._account_value = value
        self._current_positions = positions
        self.pdt_tracker.update_account_value(value)
        self.drawdown_scaler.update_high_water_mark(value)

    def pre_trade_check(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
    ) -> Tuple[bool, str]:
        """
        Run all pre-trade risk checks.

        Returns:
            (approved: bool, reason: str)
        """
        trade_value = qty * price

        # 1. Circuit breaker check
        if self.circuit_breaker.check(self._daily_pnl, self._account_value):
            return False, "Circuit breaker active - trading halted"

        # 2. Daily reset if new day
        today = date.today()
        if self._last_reset_date and self._last_reset_date != today:
            self.reset_daily()
        self._last_reset_date = today

        # 3. PDT check (for sells that would be day trades)
        if side.upper() == "SELL":
            if self.pdt_tracker.would_be_day_trade(symbol):
                if not self.pdt_tracker.can_day_trade():
                    return False, (
                        f"PDT limit reached ({self.pdt_tracker.get_day_trade_count()}"
                        f"/{PDTTracker.PDT_LIMIT} day trades used)"
                    )

        # 4. Position size check
        if self._account_value > 0:
            position_pct = trade_value / self._account_value
            if position_pct > self.limits.max_position_pct:
                return False, (
                    f"Position size {position_pct:.1%} exceeds "
                    f"{self.limits.max_position_pct:.1%} limit"
                )

        # 5. Max open positions check
        if (side.upper() == "BUY" and
                len(self._current_positions) >= self.limits.max_open_positions):
            return False, (
                f"Max open positions ({self.limits.max_open_positions}) reached"
            )

        # 6. Drawdown scaling
        multiplier = self.drawdown_scaler.get_position_multiplier(
            self._account_value, self._peak_value or self._account_value
        )
        if multiplier <= 0.0:
            return False, "Drawdown too severe - position sizing at 0%"

        # 7. Daily loss check
        if self._account_value > 0:
            daily_loss_pct = abs(min(self._daily_pnl, 0)) / self._account_value
            if daily_loss_pct >= self.limits.max_daily_loss_pct:
                return False, (
                    f"Daily loss {daily_loss_pct:.1%} at limit "
                    f"({self.limits.max_daily_loss_pct:.1%})"
                )

        # 8. Duplicate position check
        if side.upper() == "BUY" and symbol in self._current_positions:
            logger.warning("Adding to existing position in %s", symbol)

        logger.info("Pre-trade check PASSED: %s %s x%.1f @ $%.2f",
                     side, symbol, qty, price)
        return True, "approved"

    def get_adjusted_quantity(self, qty: float, price: float) -> float:
        """Adjust quantity based on drawdown scaler."""
        multiplier = self.drawdown_scaler.get_position_multiplier(
            self._account_value, self._peak_value or self._account_value
        )
        adjusted = max(1, int(qty * multiplier))
        if adjusted != qty:
            logger.info("Quantity adjusted by drawdown scaler: %d -> %d (%.0f%%)",
                        qty, adjusted, multiplier * 100)
        return adjusted

    def record_trade(self, symbol: str, side: str, qty: float, price: float,
                     pnl: Optional[float] = None):
        """Record a completed trade for daily tracking."""
        trade = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "pnl": pnl or 0.0,
            "timestamp": datetime.now().isoformat(),
        }
        self._daily_trades.append(trade)

        if pnl is not None:
            self._daily_pnl += pnl
            if pnl < 0:
                self.circuit_breaker.record_loss()
            else:
                self.circuit_breaker.record_win()

        # Track for PDT
        if side.upper() == "BUY":
            self.pdt_tracker.record_buy(symbol, qty, price)
        elif side.upper() == "SELL":
            self.pdt_tracker.record_sell(symbol, qty, price)

        logger.info("Trade recorded: %s %s x%.1f @ $%.2f | PnL=$%.2f | Daily=$%.2f",
                     side, symbol, qty, price, pnl or 0, self._daily_pnl)

    def reset_daily(self):
        """Reset daily counters for new trading day."""
        logger.info("Daily reset | Previous day PnL: $%.2f | Trades: %d",
                     self._daily_pnl, len(self._daily_trades))
        self._daily_pnl = 0.0
        self._daily_trades.clear()
        self.circuit_breaker.reset_daily()
        self.pdt_tracker.cleanup_old_records()
        self._last_reset_date = date.today()

    def get_risk_report(self) -> dict:
        """Get comprehensive risk status report."""
        return {
            "account_value": self._account_value,
            "daily_pnl": self._daily_pnl,
            "daily_trades": len(self._daily_trades),
            "open_positions": len(self._current_positions),
            "max_positions": self.limits.max_open_positions,
            "drawdown_multiplier": self.drawdown_scaler.get_position_multiplier(
                self._account_value, self._peak_value or self._account_value
            ),
            "pdt_status": self.pdt_tracker.get_status(),
            "circuit_breaker": self.circuit_breaker.get_status(),
        }
