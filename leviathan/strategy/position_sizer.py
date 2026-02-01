"""Position sizing using Kelly Criterion."""
import logging

logger = logging.getLogger('leviathan.position_sizer')


def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """K = W - (1-W)/R where W=win rate, R=win/loss ratio."""
    if avg_loss == 0:
        return 0
    r = avg_win / avg_loss
    kelly = win_rate - (1 - win_rate) / r
    return max(0, kelly)


def calculate_position_size(account_value: float, signal_confidence: float,
                            win_rate: float = 0.55, avg_win: float = 0.03,
                            avg_loss: float = 0.02, max_position_pct: float = 0.20) -> float:
    """Calculate position size in dollars using Half-Kelly scaled by confidence."""
    full_kelly = kelly_criterion(win_rate, avg_win, avg_loss)
    half_kelly = full_kelly / 2
    confidence_mult = 0.5 + (signal_confidence * 0.5)
    adjusted = half_kelly * confidence_mult
    position_pct = min(adjusted, max_position_pct)
    return account_value * position_pct
