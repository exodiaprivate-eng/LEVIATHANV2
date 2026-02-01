"""Backtesting engine for strategy validation."""
import logging
import pandas as pd
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger('leviathan.backtest')


@dataclass
class BacktestResults:
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    avg_win: float
    avg_loss: float
    equity_curve: list
    trade_log: list


class BacktestEngine:
    """Simple backtesting engine for swing trading strategies."""

    def __init__(self, initial_capital: float = 500.0):
        self.initial_capital = initial_capital

    def run_backtest(self, signals: list, prices: pd.DataFrame) -> BacktestResults:
        capital = self.initial_capital
        equity = [capital]
        trades = []
        position = None

        for signal in signals:
            symbol = signal.get('symbol', '')
            action = signal.get('action', 'hold')
            date = signal.get('date')

            if action == 'buy' and position is None:
                price = signal.get('price', 0)
                qty = (capital * 0.1) / price if price > 0 else 0
                position = {'symbol': symbol, 'entry_price': price, 'qty': qty, 'entry_date': date}

            elif action == 'sell' and position:
                price = signal.get('price', 0)
                pnl = (price - position['entry_price']) * position['qty']
                capital += pnl
                trades.append({**position, 'exit_price': price, 'exit_date': date, 'pnl': pnl})
                position = None

            equity.append(capital)

        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]

        returns = pd.Series(equity).pct_change().dropna()
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        eq = pd.Series(equity)
        peak = eq.cummax()
        dd = (eq - peak) / peak
        max_dd = dd.min()

        return BacktestResults(
            total_return=(capital - self.initial_capital) / self.initial_capital,
            annualized_return=0, sharpe_ratio=float(sharpe),
            sortino_ratio=0, max_drawdown=float(max_dd),
            win_rate=len(wins) / max(len(trades), 1),
            profit_factor=sum(t['pnl'] for t in wins) / max(abs(sum(t['pnl'] for t in losses)), 1),
            total_trades=len(trades),
            avg_trade_duration=0,
            avg_win=sum(t['pnl'] for t in wins) / max(len(wins), 1),
            avg_loss=sum(t['pnl'] for t in losses) / max(len(losses), 1),
            equity_curve=equity, trade_log=trades,
        )
