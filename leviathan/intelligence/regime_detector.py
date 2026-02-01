"""Market regime detection - trending, ranging, volatile."""
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger('leviathan.regime')


class MarketRegimeDetector:
    """Detect current market regime for strategy adaptation."""

    def detect_regime(self, df: pd.DataFrame) -> str:
        if len(df) < 50:
            return 'unknown'
        returns = df['close'].pct_change().dropna()
        vol = returns.std() * np.sqrt(252)
        sma_20 = df['close'].rolling(20).mean()
        sma_50 = df['close'].rolling(50).mean()
        trend = (sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1] if sma_50.iloc[-1] > 0 else 0

        if vol > 0.35:
            return 'volatile'
        if trend > 0.02:
            return 'trending_up'
        if trend < -0.02:
            return 'trending_down'
        return 'ranging'

    def get_regime_confidence(self, df: pd.DataFrame) -> float:
        regime = self.detect_regime(df)
        if regime == 'unknown':
            return 0.0
        returns = df['close'].pct_change().dropna()
        vol = returns.std() * np.sqrt(252)
        if regime == 'volatile':
            return min(vol / 0.5, 1.0)
        sma_20 = df['close'].rolling(20).mean()
        sma_50 = df['close'].rolling(50).mean()
        trend = abs(sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1] if sma_50.iloc[-1] > 0 else 0
        return min(trend / 0.05, 1.0)
