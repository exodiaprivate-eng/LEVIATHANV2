"""Performance metrics for backtesting."""
import numpy as np
import pandas as pd


def calculate_sharpe_ratio(returns: pd.Series, risk_free: float = 0.05) -> float:
    excess = returns - risk_free / 252
    return float(excess.mean() / excess.std() * np.sqrt(252)) if excess.std() > 0 else 0

def calculate_sortino_ratio(returns: pd.Series, risk_free: float = 0.05) -> float:
    excess = returns - risk_free / 252
    downside = excess[excess < 0].std()
    return float(excess.mean() / downside * np.sqrt(252)) if downside > 0 else 0

def calculate_max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())

def calculate_win_rate(trades: list) -> float:
    if not trades:
        return 0
    wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
    return wins / len(trades)

def calculate_profit_factor(trades: list) -> float:
    gross_profit = sum(t['pnl'] for t in trades if t.get('pnl', 0) > 0)
    gross_loss = abs(sum(t['pnl'] for t in trades if t.get('pnl', 0) < 0))
    return gross_profit / gross_loss if gross_loss > 0 else float('inf')
