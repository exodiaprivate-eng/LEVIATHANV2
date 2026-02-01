"""CLI backtesting runner."""
import argparse
from backtest.engine import BacktestEngine
from backtest.reports import generate_backtest_report


def main():
    parser = argparse.ArgumentParser(description='Leviathan Backtester')
    parser.add_argument('--capital', type=float, default=500, help='Starting capital')
    parser.add_argument('--symbols', nargs='+', default=['SPY', 'QQQ', 'AAPL'],
                        help='Symbols to backtest')
    parser.add_argument('--start', type=str, default=None, help='Start date YYYY-MM-DD')
    parser.add_argument('--end', type=str, default=None, help='End date YYYY-MM-DD')
    args = parser.parse_args()

    import pandas as pd
    from datetime import datetime, timedelta

    end_date = args.end or datetime.now().strftime('%Y-%m-%d')
    start_date = args.start or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    engine = BacktestEngine(initial_capital=args.capital)

    # Generate simple momentum signals from historical data
    try:
        import yfinance as yf
    except ImportError:
        # Fallback: try alpaca data fetcher
        yf = None

    all_signals = []
    all_prices = pd.DataFrame()

    for symbol in args.symbols:
        try:
            if yf:
                df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            else:
                print(f"Install yfinance for data: pip install yfinance")
                return

            if df is None or len(df) < 50:
                print(f"Insufficient data for {symbol}, skipping")
                continue

            close = df['Close'].squeeze()
            sma_short = close.rolling(10).mean()
            sma_long = close.rolling(30).mean()

            for i in range(30, len(df)):
                date = df.index[i]
                price = float(close.iloc[i])
                if sma_short.iloc[i] > sma_long.iloc[i] and sma_short.iloc[i-1] <= sma_long.iloc[i-1]:
                    all_signals.append({'symbol': symbol, 'action': 'buy', 'date': date, 'price': price})
                elif sma_short.iloc[i] < sma_long.iloc[i] and sma_short.iloc[i-1] >= sma_long.iloc[i-1]:
                    all_signals.append({'symbol': symbol, 'action': 'sell', 'date': date, 'price': price})

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    if not all_signals:
        print("No signals generated. Check data availability.")
        return

    all_signals.sort(key=lambda s: s['date'])
    results = engine.run_backtest(all_signals, pd.DataFrame())
    print(generate_backtest_report(results))


if __name__ == "__main__":
    main()
