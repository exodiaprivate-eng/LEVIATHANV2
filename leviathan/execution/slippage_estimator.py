"""Slippage estimation based on volume and spread."""
import logging

logger = logging.getLogger('leviathan.slippage')


class SlippageEstimator:
    """Estimate and track trade slippage."""

    def __init__(self):
        self._history = []

    def estimate_slippage(self, symbol: str, qty: float, side: str,
                          avg_volume: float = 1000000, spread: float = 0.01) -> float:
        """Estimate slippage in dollars per share."""
        volume_impact = qty / avg_volume if avg_volume > 0 else 0
        base_slippage = spread / 2
        impact = base_slippage * (1 + volume_impact * 10)
        return round(impact, 4)

    def record_actual_slippage(self, expected_price: float, actual_price: float,
                                symbol: str, side: str):
        slip = abs(actual_price - expected_price)
        self._history.append({'symbol': symbol, 'side': side, 'slippage': slip})
        if len(self._history) > 1000:
            self._history = self._history[-500:]

    def get_average_slippage(self) -> float:
        if not self._history:
            return 0.0
        return sum(h['slippage'] for h in self._history) / len(self._history)
