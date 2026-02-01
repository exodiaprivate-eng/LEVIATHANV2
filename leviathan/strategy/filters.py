"""Trade filters for quality control."""
import logging

logger = logging.getLogger('leviathan.filters')


class TradeFilter:
    """Pre-trade quality filters."""

    def __init__(self, min_volume_ratio: float = 1.0, max_spread_pct: float = 0.5,
                 min_atr: float = 0.01, avoid_earnings: bool = True):
        self.min_volume_ratio = min_volume_ratio
        self.max_spread_pct = max_spread_pct
        self.min_atr = min_atr
        self.avoid_earnings = avoid_earnings

    def volume_filter(self, volume_ratio: float) -> tuple[bool, str]:
        if volume_ratio < self.min_volume_ratio:
            return False, f"Volume ratio {volume_ratio:.1f} below minimum {self.min_volume_ratio}"
        return True, ""

    def spread_filter(self, bid: float, ask: float) -> tuple[bool, str]:
        if bid <= 0:
            return False, "Invalid bid price"
        spread_pct = (ask - bid) / bid * 100
        if spread_pct > self.max_spread_pct:
            return False, f"Spread {spread_pct:.2f}% exceeds max {self.max_spread_pct}%"
        return True, ""

    def volatility_filter(self, atr: float, price: float) -> tuple[bool, str]:
        atr_pct = atr / price if price > 0 else 0
        if atr_pct < self.min_atr:
            return False, f"ATR% {atr_pct:.3f} too low"
        return True, ""

    def earnings_filter(self, has_earnings_soon: bool) -> tuple[bool, str]:
        if self.avoid_earnings and has_earnings_soon:
            return False, "Earnings within 2 days"
        return True, ""

    def apply_all_filters(self, **kwargs) -> tuple[bool, str]:
        checks = [
            self.volume_filter(kwargs.get('volume_ratio', 1.5)),
            self.volatility_filter(kwargs.get('atr', 1), kwargs.get('price', 100)),
            self.earnings_filter(kwargs.get('has_earnings_soon', False)),
        ]
        if 'bid' in kwargs and 'ask' in kwargs:
            checks.append(self.spread_filter(kwargs['bid'], kwargs['ask']))
        for passed, reason in checks:
            if not passed:
                return False, reason
        return True, ""
