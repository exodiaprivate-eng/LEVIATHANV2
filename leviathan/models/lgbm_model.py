"""LightGBM model for price direction prediction."""
import logging
import pickle
from pathlib import Path

import numpy as np
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit

logger = logging.getLogger('leviathan.models.lgbm')


class LGBMPredictor:
    """LightGBM classifier for Buy/Hold/Sell prediction."""

    def __init__(self, params: dict = None):
        self.model = None
        self.params = params or {
            'objective': 'multiclass', 'num_class': 3,
            'metric': 'multi_logloss', 'boosting_type': 'gbdt',
            'num_leaves': 31, 'learning_rate': 0.05,
            'feature_fraction': 0.8, 'bagging_fraction': 0.8,
            'bagging_freq': 5, 'verbose': -1,
        }
        self.feature_names = None

    def train(self, X_train, y_train, X_val=None, y_val=None,
              num_boost_round: int = 1000, early_stopping: int = 50):
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = [train_data]
        if X_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
        callbacks = [lgb.early_stopping(early_stopping)] if X_val is not None else []
        self.model = lgb.train(
            self.params, train_data, num_boost_round=num_boost_round,
            valid_sets=valid_sets, callbacks=callbacks,
        )
        if hasattr(X_train, 'columns'):
            self.feature_names = list(X_train.columns)
        logger.info(f"LightGBM trained: {self.model.best_iteration} iterations")

    def predict(self, X) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.predict(X)

    def feature_importance(self) -> dict:
        if self.model is None:
            return {}
        importance = self.model.feature_importance(importance_type='gain')
        names = self.feature_names or [f"f{i}" for i in range(len(importance))]
        return dict(sorted(zip(names, importance), key=lambda x: x[1], reverse=True))

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'params': self.params,
                         'features': self.feature_names}, f)

    def load(self, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.model = data['model']
        self.params = data['params']
        self.feature_names = data.get('features')
        logger.info(f"LightGBM loaded from {path}")
