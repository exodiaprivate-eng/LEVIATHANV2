"""FinBERT wrapper for financial sentiment analysis."""
import logging
from typing import Optional

logger = logging.getLogger('leviathan.finbert')


class FinBERTAnalyzer:
    """Financial sentiment analysis using ProsusAI/finbert."""

    def __init__(self):
        self._pipeline = None

    def _load(self):
        if self._pipeline is None:
            from transformers import pipeline
            import torch
            device = 0 if torch.cuda.is_available() else -1
            self._pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                device=device,
            )
            logger.info(f"FinBERT loaded (device={device})")

    def analyze(self, texts: list) -> list:
        """Analyze list of texts. Returns list of {label, score}."""
        self._load()
        try:
            return self._pipeline(texts, truncation=True, max_length=512)
        except Exception as e:
            logger.error(f"FinBERT analysis failed: {e}")
            return [{'label': 'neutral', 'score': 0.5}] * len(texts)

    def get_sentiment_score(self, text: str) -> float:
        """Return single score from -1 (negative) to +1 (positive)."""
        result = self.analyze([text])[0]
        if result['label'] == 'positive':
            return result['score']
        elif result['label'] == 'negative':
            return -result['score']
        return 0.0

    def batch_analyze(self, texts: list, batch_size: int = 16) -> list:
        scores = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            results = self.analyze(batch)
            for r in results:
                if r['label'] == 'positive':
                    scores.append(r['score'])
                elif r['label'] == 'negative':
                    scores.append(-r['score'])
                else:
                    scores.append(0.0)
        return scores
