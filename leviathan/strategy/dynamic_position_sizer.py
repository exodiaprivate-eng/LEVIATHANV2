"""Dynamic position sizing based on performance tiers and learning."""
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger('leviathan.dynamic_sizer')


@dataclass
class PerformanceTier:
    name: str
    min_profit_pct: float
    min_win_rate: float
    min_trades: int
    base_position_pct: float
    max_position_pct: float
    confidence_multiplier: float


class DynamicPositionSizer:
    """Auto-adjust position sizes based on AI's track record."""

    TIERS = [
        PerformanceTier('LEARNING', -999, 0.0, 0, 0.05, 0.10, 0.5),
        PerformanceTier('CAUTIOUS', 0.0, 0.45, 10, 0.08, 0.15, 0.7),
        PerformanceTier('CONFIDENT', 5.0, 0.52, 25, 0.12, 0.20, 0.85),
        PerformanceTier('AGGRESSIVE', 15.0, 0.55, 50, 0.15, 0.25, 1.0),
        PerformanceTier('MAXIMUM', 30.0, 0.58, 100, 0.20, 0.30, 1.2),
    ]

    def __init__(self, starting_capital: float, db=None):
        self.starting_capital = starting_capital
        self.db = db

    def get_current_tier(self, stats: dict) -> PerformanceTier:
        current = self.TIERS[0]
        for tier in self.TIERS:
            if (stats.get('cumulative_profit_pct', 0) >= tier.min_profit_pct and
                stats.get('win_rate', 0) >= tier.min_win_rate and
                stats.get('total_trades', 0) >= tier.min_trades):
                current = tier
        return current

    def calculate_dynamic_size(self, account_value: float, signal_confidence: float,
                                performance_stats: dict, current_drawdown_pct: float) -> dict:
        tier = self.get_current_tier(performance_stats)
        base = tier.base_position_pct
        adj = base * (0.5 + signal_confidence * tier.confidence_multiplier)
        if current_drawdown_pct > 5:
            adj *= max(0.3, 1 - current_drawdown_pct / 20)
        if performance_stats.get('last_5_trades_wins', 0) >= 4:
            adj *= 1.2
        if self.db:
            hist = self._get_historical_optimal(signal_confidence,
                                                     performance_stats.get('win_rate'),
                                                     current_drawdown_pct)
            if hist:
                adj = adj * 0.7 + hist * 0.3
        final = max(0.02, min(adj, tier.max_position_pct))
        return {
            'position_pct': final, 'position_dollars': account_value * final,
            'tier': tier.name,
            'reasoning': f"Tier={tier.name}, Base={base:.1%}, Conf={signal_confidence:.2f}, DD={current_drawdown_pct:.1f}%, Final={final:.1%}"
        }

    def _get_historical_optimal(self, confidence: float, win_rate: float = None,
                                  current_drawdown_pct: float = None):
        if not self.db:
            return None
        try:
            # Calculate actual metrics from learning DB if not provided
            if win_rate is None or current_drawdown_pct is None:
                stats = self.db.get_performance_stats()
                if win_rate is None:
                    win_rate = stats.get('win_rate', 0.5)
                if current_drawdown_pct is None:
                    current_drawdown_pct = stats.get('max_drawdown_pct', 0.0)
            return self.db.query_best_position_size(confidence, win_rate, current_drawdown_pct)
        except Exception as e:
            logger.warning(f"Historical optimal lookup failed: {e}")
            return None

    def record_outcome(self, position_pct, signal_confidence, win_rate, drawdown, result):
        if self.db:
            self.db.record_position_outcome(
                position_pct=position_pct, confidence=signal_confidence,
                win_rate=win_rate, drawdown=drawdown, profit_loss=result,
                timestamp=datetime.now())
