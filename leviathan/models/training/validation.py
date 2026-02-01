"""Walk-forward validation for time series models."""
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger('leviathan.validation')


def walk_forward_validation(model_class, data: pd.DataFrame,
                            train_window: int = 252, test_window: int = 21,
                            step: int = 21) -> dict:
    """Walk-forward validation - never use random splits for time series."""
    results = []
    for i in range(0, len(data) - train_window - test_window, step):
        train_end = i + train_window
        test_end = train_end + test_window
        train = data.iloc[i:train_end]
        test = data.iloc[train_end:test_end]
        try:
            model = model_class()
            feature_cols = [c for c in train.columns if c != 'target']
            model.train(train[feature_cols].values, train['target'].values)
            preds = model.predict(test[feature_cols].values)
            metrics = calculate_metrics(preds, test['target'].values)
            results.append(metrics)
        except Exception as e:
            logger.warning(f"Fold failed: {e}")
    return aggregate_results(results) if results else {}


def calculate_metrics(predictions, actual) -> dict:
    if hasattr(predictions, 'argmax'):
        pred_labels = predictions.argmax(axis=1) if predictions.ndim > 1 else predictions
    else:
        pred_labels = np.array(predictions)
    actual = np.array(actual)
    accuracy = np.mean(pred_labels == actual) if len(actual) > 0 else 0
    return {'accuracy': float(accuracy), 'samples': len(actual)}


def aggregate_results(results: list) -> dict:
    if not results:
        return {}
    return {
        'mean_accuracy': float(np.mean([r['accuracy'] for r in results])),
        'std_accuracy': float(np.std([r['accuracy'] for r in results])),
        'num_folds': len(results),
        'total_samples': sum(r['samples'] for r in results),
    }
