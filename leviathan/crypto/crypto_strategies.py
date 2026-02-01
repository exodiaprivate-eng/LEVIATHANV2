"""Crypto-specific trading strategies with higher volatility tolerance."""
import logging
import pandas as pd
import pandas_ta as ta

logger = logging.getLogger('leviathan.crypto_strategy')


class CryptoStrategy:
    """Crypto strategies with faster indicators."""

    def momentum_strategy(self, df: pd.DataFrame) -> dict:
        rsi = ta.rsi(df['close'], length=7)
        macd = ta.macd(df['close'], fast=8, slow=21, signal=5)
        signal = 0.0
        if rsi is not None and len(rsi) > 0:
            if rsi.iloc[-1] < 25: signal += 0.5
            elif rsi.iloc[-1] > 75: signal -= 0.5
        if macd is not None:
            m_cols = [c for c in macd.columns if 'MACD_' in c and 's' not in c.lower()]
            s_cols = [c for c in macd.columns if 'MACDs' in c]
            if m_cols and s_cols:
                if macd[m_cols[0]].iloc[-1] > macd[s_cols[0]].iloc[-1]:
                    signal += 0.3
                else:
                    signal -= 0.3
        return {'signal': signal, 'strategy': 'crypto_momentum'}

    def mean_reversion_strategy(self, df: pd.DataFrame) -> dict:
        bb = ta.bbands(df['close'], length=20, std=2.5)
        signal = 0.0
        if bb is not None:
            lower_col = [c for c in bb.columns if 'BBL' in c]
            upper_col = [c for c in bb.columns if 'BBU' in c]
            if lower_col and df['close'].iloc[-1] < bb[lower_col[0]].iloc[-1]:
                signal = 0.6
            elif upper_col and df['close'].iloc[-1] > bb[upper_col[0]].iloc[-1]:
                signal = -0.6
        return {'signal': signal, 'strategy': 'crypto_mean_reversion'}
