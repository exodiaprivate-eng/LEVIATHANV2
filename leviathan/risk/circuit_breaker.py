"""
Circuit Breaker Module.

Emergency trading halt based on daily loss limits and consecutive losses.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Halts trading when loss thresholds are exceeded.

    Triggers:
    - Daily P&L loss exceeds max_daily_loss_pct of account
    - Consecutive losses exceed threshold
    - Cooldown period after trigger before resuming
    """

    def __init__(
        self,
        max_daily_loss_pct: float = 0.03,
        max_consecutive_losses: int = 3,
        cooldown_minutes: int = 30,
    ):
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_consecutive_losses = max_consecutive_losses
        self.cooldown_minutes = cooldown_minutes

        self._consecutive_losses = 0
        self._tripped = False
        self._trip_time: datetime | None = None
        self._trip_reason: str = ""
        self._daily_pnl = 0.0
        self._trade_count = 0

        logger.info(
            "CircuitBreaker initialized | max_daily_loss=%.1f%% | "
            "max_consecutive=%d | cooldown=%dm",
            max_daily_loss_pct * 100, max_consecutive_losses, cooldown_minutes
        )

    def check(self, daily_pnl: float, account_value: float) -> bool:
        """
        Check if circuit breaker should trip.
        Returns True if trading should be HALTED.
        """
        self._daily_pnl = daily_pnl

        # Check if cooling down from previous trip
        if self.is_cooling_down():
            return True

        # Check daily loss threshold
        if account_value > 0:
            loss_pct = abs(min(daily_pnl, 0)) / account_value
            if loss_pct >= self.max_daily_loss_pct:
                self._trip(f"Daily loss {loss_pct:.1%} exceeds {self.max_daily_loss_pct:.1%} limit")
                return True

        # Check consecutive losses
        if self._consecutive_losses >= self.max_consecutive_losses:
            self._trip(f"{self._consecutive_losses} consecutive losses")
            return True

        return False

    def record_loss(self):
        """Record a losing trade."""
        self._consecutive_losses += 1
        self._trade_count += 1
        logger.debug("Loss recorded | consecutive=%d", self._consecutive_losses)

    def record_win(self):
        """Record a winning trade - resets consecutive loss counter."""
        self._consecutive_losses = 0
        self._trade_count += 1

    def is_cooling_down(self) -> bool:
        """Check if still in cooldown period after a trip."""
        if not self._tripped or not self._trip_time:
            return False
        elapsed = datetime.now() - self._trip_time
        if elapsed >= timedelta(minutes=self.cooldown_minutes):
            self._tripped = False
            self._trip_time = None
            self._trip_reason = ""
            logger.info("CircuitBreaker cooldown ended, trading resumed")
            return False
        return True

    def _trip(self, reason: str):
        """Trip the circuit breaker."""
        self._tripped = True
        self._trip_time = datetime.now()
        self._trip_reason = reason
        logger.warning("CIRCUIT BREAKER TRIPPED: %s | Cooldown: %dm",
                       reason, self.cooldown_minutes)

    def reset(self):
        """Manual reset of circuit breaker."""
        self._tripped = False
        self._trip_time = None
        self._trip_reason = ""
        self._consecutive_losses = 0
        logger.info("CircuitBreaker manually reset")

    def reset_daily(self):
        """Reset daily counters (call at start of trading day)."""
        self._daily_pnl = 0.0
        self._trade_count = 0
        self._consecutive_losses = 0
        if not self.is_cooling_down():
            self._tripped = False

    def get_status(self) -> dict:
        """Get circuit breaker status."""
        return {
            "tripped": self._tripped,
            "cooling_down": self.is_cooling_down(),
            "trip_reason": self._trip_reason,
            "trip_time": self._trip_time.isoformat() if self._trip_time else None,
            "consecutive_losses": self._consecutive_losses,
            "daily_pnl": self._daily_pnl,
            "trade_count": self._trade_count,
        }
