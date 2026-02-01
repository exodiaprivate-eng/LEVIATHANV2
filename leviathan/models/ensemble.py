"""Ensemble model combining LSTM, LightGBM, and N-BEATS predictions."""
import logging
import numpy as np

logger = logging.getLogger('leviathan.models.ensemble')


class EnsemblePredictor:
    """Combine multiple model predictions with configurable weights."""

    def __init__(self, models: list = None, weights: list = None):
        self.models = models or []
        self.weights = weights or ([1 / len(models)] * len(models) if models else [])

    def add_model(self, model, weight: float = None):
        self.models.append(model)
        if weight:
            self.weights.append(weight)
        else:
            n = len(self.models)
            self.weights = [1 / n] * n

    def predict(self, X) -> np.ndarray:
        if not self.models:
            raise ValueError("No models in ensemble")
        predictions = []
        for model, weight in zip(self.models, self.weights):
            try:
                pred = model.predict(X)
                predictions.append(pred * weight)
            except Exception as e:
                logger.warning(f"Model prediction failed: {e}")
        if not predictions:
            raise ValueError("All models failed")
        return sum(predictions)

    def predict_with_confidence(self, X) -> tuple:
        """Return (prediction, confidence) where confidence = agreement between models."""
        preds = []
        for model in self.models:
            try:
                preds.append(model.predict(X))
            except Exception:
                continue
        if not preds:
            return np.zeros(3), 0.0
        avg = sum(p * w for p, w in zip(preds, self.weights[:len(preds)]))
        confidence = 1.0 - np.std([p.argmax(axis=-1) for p in preds], axis=0).mean()
        return avg, float(confidence)

    def evaluate(self, X, y_true) -> dict:
        preds = self.predict(X)
        y_pred = np.argmax(preds, axis=1)
        accuracy = np.mean(y_pred == y_true)
        return {'accuracy': accuracy, 'predictions': len(y_pred)}
