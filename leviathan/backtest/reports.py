"""Backtest report generation."""


def generate_backtest_report(results) -> str:
    lines = [
        "BACKTEST RESULTS",
        "=" * 40,
        f"Total Return:      {results.total_return:.2%}",
        f"Sharpe Ratio:      {results.sharpe_ratio:.2f}",
        f"Max Drawdown:      {results.max_drawdown:.2%}",
        f"Win Rate:          {results.win_rate:.2%}",
        f"Profit Factor:     {results.profit_factor:.2f}",
        f"Total Trades:      {results.total_trades}",
        f"Avg Win:           ${results.avg_win:.2f}",
        f"Avg Loss:          ${results.avg_loss:.2f}",
    ]
    return '\n'.join(lines)
