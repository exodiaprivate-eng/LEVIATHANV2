"""Technical indicator calculation using pandas-ta."""
import logging
import pandas as pd
import pandas_ta as ta

logger = logging.getLogger('leviathan.features')


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical features to OHLCV DataFrame.
    Input columns: open, high, low, close, volume
    """
    df = df.copy()
    # Trend
    df['sma_20'] = ta.sma(df['close'], length=20)
    df['sma_50'] = ta.sma(df['close'], length=50)
    df['sma_200'] = ta.sma(df['close'], length=200)
    df['ema_12'] = ta.ema(df['close'], length=12)
    df['ema_26'] = ta.ema(df['close'], length=26)

    # Momentum
    df['rsi_14'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)

    # Volatility
    bbands = ta.bbands(df['close'], length=20, std=2)
    if bbands is not None:
        df = pd.concat([df, bbands], axis=1)
    df['atr_14'] = ta.atr(df['high'], df['low'], df['close'], length=14)

    # Volume
    df['volume_sma_20'] = ta.sma(df['volume'], length=20)
    df['volume_ratio'] = df['volume'] / df['volume_sma_20'].replace(0, 1)

    # Price-based
    df['returns_1d'] = df['close'].pct_change(1)
    df['returns_5d'] = df['close'].pct_change(5)
    df['returns_20d'] = df['close'].pct_change(20)
    df['high_low_range'] = (df['high'] - df['low']) / df['close']

    # ADX
    adx = ta.adx(df['high'], df['low'], df['close'], length=14)
    if adx is not None:
        df = pd.concat([df, adx], axis=1)

    # Target (5-day forward return direction)
    df['target'] = (df['close'].shift(-5) > df['close']).astype(int)

    return df.dropna()
