"""Hyperparameter tuning via random search."""
import logging
import random
import numpy as np

logger = logging.getLogger('leviathan.hyperopt')


class HyperparameterTuner:
    """Random search hyperparameter optimization."""

    def tune_lgbm(self, X_train, y_train, X_val, y_val, n_trials: int = 20) -> dict:
        from models.lgbm_model import LGBMPredictor
        best_score, best_params = float('inf'), {}
        for i in range(n_trials):
            params = {
                'objective': 'multiclass', 'num_class': 3, 'metric': 'multi_logloss',
                'num_leaves': random.choice([15, 31, 63, 127]),
                'learning_rate': random.choice([0.01, 0.03, 0.05, 0.1]),
                'feature_fraction': random.uniform(0.6, 1.0),
                'bagging_fraction': random.uniform(0.6, 1.0),
                'bagging_freq': random.choice([3, 5, 7]),
                'verbose': -1,
            }
            model = LGBMPredictor(params)
            model.train(X_train, y_train, X_val, y_val)
            preds = model.predict(X_val)
            score = -np.mean(np.log(preds[np.arange(len(y_val)), y_val.astype(int)] + 1e-10))
            if score < best_score:
                best_score = score
                best_params = params
            logger.info(f"Trial {i+1}/{n_trials}: score={score:.4f}")
        return best_params

    def tune_lstm(self, X_train, y_train, X_val, y_val, n_trials: int = 10) -> dict:
        best_params = {
            'hidden_size': 64, 'num_layers': 2, 'dropout': 0.2, 'lr': 0.001
        }
        # Simplified - would iterate different configs
        return best_params
