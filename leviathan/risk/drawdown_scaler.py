"""
Drawdown Scaler Module.

Scales position sizes based on drawdown from high water mark.
"""
import logging

logger = logging.getLogger(__name__)


class DrawdownScaler:
    """
    Reduces position sizes as drawdown increases.

    Scale:
    - 0-5% drawdown:  100% position size
    - 5-10% drawdown:  50% position size
    - 10-15% drawdown: 25% position size
    - >15% drawdown:    0% (halt trading)
    """

    TIERS = [
        (0.05, 1.00),   # 0-5% DD → 100%
        (0.10, 0.50),   # 5-10% DD → 50%
        (0.15, 0.25),   # 10-15% DD → 25%
    ]

    def __init__(self, max_drawdown_pct: float = 0.15):
        self._high_water_mark = 0.0
        self.max_drawdown_pct = max_drawdown_pct
        logger.info("DrawdownScaler initialized | max_dd=%.1f%%",
                     max_drawdown_pct * 100)

    def update_high_water_mark(self, equity: float):
        """Update high water mark if new peak."""
        if equity > self._high_water_mark:
            self._high_water_mark = equity

    def get_drawdown_pct(self, current_equity: float) -> float:
        """Calculate current drawdown percentage."""
        if self._high_water_mark <= 0:
            return 0.0
        return max(0.0, (self._high_water_mark - current_equity) / self._high_water_mark)

    def get_position_multiplier(self, current_equity: float,
                                 peak_equity: float = 0.0) -> float:
        """
        Get position size multiplier based on current drawdown.

        Returns float between 0.0 and 1.0.
        """
        if peak_equity > 0:
            self._high_water_mark = max(self._high_water_mark, peak_equity)

        dd = self.get_drawdown_pct(current_equity)

        for threshold, multiplier in self.TIERS:
            if dd <= threshold:
                return multiplier

        # Beyond max tier → halt
        logger.warning("Drawdown %.1f%% exceeds max → position multiplier 0.0", dd * 100)
        return 0.0

    @property
    def high_water_mark(self) -> float:
        return self._high_water_mark

    def get_status(self) -> dict:
        return {
            "high_water_mark": self._high_water_mark,
            "max_drawdown_pct": self.max_drawdown_pct,
        }
