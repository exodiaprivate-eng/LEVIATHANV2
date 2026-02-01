"""CLI backtesting runner."""
import argparse
from backtest.engine import BacktestEngine
from backtest.reports import generate_backtest_report


def main():
    parser = argparse.ArgumentParser(description='Leviathan Backtester')
    parser.add_argument('--capital', type=float, default=500, help='Starting capital')
    args = parser.parse_args()

    engine = BacktestEngine(initial_capital=args.capital)
    print("Backtester ready. Implement strategy signals and run.")
    # Example: results = engine.run_backtest(signals, prices)
    # print(generate_backtest_report(results))


if __name__ == "__main__":
    main()
