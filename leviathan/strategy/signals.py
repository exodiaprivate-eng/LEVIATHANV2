"""Signal generation combining technical, sentiment, and ML predictions."""
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger('leviathan.signals')


class SignalType(Enum):
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    confidence: float
    technical_score: float
    sentiment_score: float
    ml_prediction: float
    reasoning: str


class SignalGenerator:
    """Combine technical analysis, sentiment, and ML into trading signals."""

    def __init__(self, technical_weight: float = 0.4,
                 sentiment_weight: float = 0.3, ml_weight: float = 0.3):
        self.weights = {'technical': technical_weight,
                        'sentiment': sentiment_weight, 'ml': ml_weight}

    def generate_signal(self, symbol: str, technical_indicators: dict,
                        sentiment_score: float, ml_prediction: float) -> TradingSignal:
        tech_score = self._calculate_technical_score(technical_indicators)
        ml_score = (ml_prediction - 0.5) * 2
        combined = (tech_score * self.weights['technical'] +
                    sentiment_score * self.weights['sentiment'] +
                    ml_score * self.weights['ml'])
        signal_type, confidence = self._score_to_signal(combined)
        reasoning = self._generate_reasoning(technical_indicators, sentiment_score, ml_prediction)
        return TradingSignal(symbol=symbol, signal_type=signal_type, confidence=confidence,
                             technical_score=tech_score, sentiment_score=sentiment_score,
                             ml_prediction=ml_prediction, reasoning=reasoning)

    def _calculate_technical_score(self, ind: dict) -> float:
        score = 0.0
        rsi = ind.get('rsi', 50)
        if rsi < 30: score += 0.3
        elif rsi > 70: score -= 0.3
        macd, macd_sig = ind.get('macd', 0), ind.get('macd_signal', 0)
        score += 0.3 if macd > macd_sig else -0.3
        price, sma_50 = ind.get('close', 0), ind.get('sma_50', ind.get('close', 0))
        score += 0.2 if price > sma_50 else -0.2
        bb_lower = ind.get('bb_lower', price)
        bb_upper = ind.get('bb_upper', price)
        if price < bb_lower: score += 0.2
        elif price > bb_upper: score -= 0.2
        return max(-1, min(1, score))

    def _score_to_signal(self, score: float) -> tuple:
        confidence = abs(score)
        if score >= 0.6: return SignalType.STRONG_BUY, confidence
        elif score >= 0.2: return SignalType.BUY, confidence
        elif score <= -0.6: return SignalType.STRONG_SELL, confidence
        elif score <= -0.2: return SignalType.SELL, confidence
        return SignalType.HOLD, confidence

    def _generate_reasoning(self, ind: dict, sentiment: float, ml: float) -> str:
        parts = []
        rsi = ind.get('rsi', 50)
        if rsi < 30: parts.append(f"RSI oversold ({rsi:.0f})")
        elif rsi > 70: parts.append(f"RSI overbought ({rsi:.0f})")
        if sentiment > 0.3: parts.append(f"Positive sentiment ({sentiment:.2f})")
        elif sentiment < -0.3: parts.append(f"Negative sentiment ({sentiment:.2f})")
        if ml > 0.6: parts.append(f"ML bullish ({ml:.1%})")
        elif ml < 0.4: parts.append(f"ML bearish ({ml:.1%})")
        return '; '.join(parts) or 'Neutral conditions'
