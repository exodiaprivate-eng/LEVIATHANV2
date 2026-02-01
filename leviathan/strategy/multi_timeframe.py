"""Multi-timeframe analysis for signal confirmation."""
import logging
import pandas as pd
import pandas_ta as ta

logger = logging.getLogger('leviathan.multi_tf')


class MultiTimeframeAnalyzer:
    """Analyze signals across daily, hourly, and weekly timeframes."""

    def analyze(self, daily: pd.DataFrame, hourly: pd.DataFrame = None,
                weekly: pd.DataFrame = None) -> dict:
        scores = {}
        scores['daily'] = self._score_timeframe(daily)
        if hourly is not None:
            scores['hourly'] = self._score_timeframe(hourly)
        if weekly is not None:
            scores['weekly'] = self._score_timeframe(weekly)
        alignment = self._check_alignment(scores)
        return {'scores': scores, 'alignment': alignment,
                'overall': sum(scores.values()) / len(scores)}

    def _score_timeframe(self, df: pd.DataFrame) -> float:
        if df.empty or len(df) < 20:
            return 0.0
        score = 0.0
        rsi = ta.rsi(df['close'], length=14)
        if rsi is not None and len(rsi) > 0:
            r = rsi.iloc[-1]
            if r < 30: score += 0.5
            elif r > 70: score -= 0.5
        sma = ta.sma(df['close'], length=20)
        if sma is not None and len(sma) > 0:
            score += 0.3 if df['close'].iloc[-1] > sma.iloc[-1] else -0.3
        return max(-1, min(1, score))

    def _check_alignment(self, scores: dict) -> str:
        vals = list(scores.values())
        if all(v > 0.2 for v in vals): return 'bullish_aligned'
        if all(v < -0.2 for v in vals): return 'bearish_aligned'
        return 'mixed'
