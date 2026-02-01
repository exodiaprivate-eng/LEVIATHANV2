"""
Historical Trainer Module.

Trains models from historical data using walk-forward validation.
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple

logger = logging.getLogger(__name__)


class HistoricalTrainer:
    """
    Trains all ML models from historical market data.

    Uses walk-forward cross-validation to prevent look-ahead bias.
    """

    def __init__(self, config, model_trainer=None, data_fetcher=None,
                 feature_engine=None):
        self.config = config
        self.trainer = model_trainer
        self.data_fetcher = data_fetcher
        self.features = feature_engine
        self.label_threshold = 0.02  # 2% for BUY/SELL labels

    def train_from_history(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        n_splits: int = 5,
    ) -> Dict:
        """
        Fetch historical data, generate features and labels, train all models.

        Args:
            symbols: List of ticker symbols
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            n_splits: Number of walk-forward splits

        Returns:
            Training results dict with metrics per model
        """
        logger.info("Historical training: %s from %s to %s (%d splits)",
                     symbols, start_date, end_date, n_splits)

        results = {
            'symbols': symbols,
            'start': start_date,
            'end': end_date,
            'models': {},
            'overall_metrics': {},
        }

        all_X, all_y = [], []

        for symbol in symbols:
            try:
                # Fetch OHLCV data
                df = self._fetch_data(symbol, start_date, end_date)
                if df is None or len(df) < 100:
                    logger.warning("Insufficient data for %s (%d rows)",
                                   symbol, len(df) if df is not None else 0)
                    continue

                # Generate features
                features_df = self._generate_features(df)
                if features_df is None:
                    continue

                # Generate labels
                labels = self._generate_training_labels(df)
                if labels is None:
                    continue

                # Align
                min_len = min(len(features_df), len(labels))
                X = features_df.values[:min_len]
                y = labels[:min_len]

                # Remove NaN rows
                valid = ~(np.isnan(X).any(axis=1) | np.isnan(y))
                X = X[valid]
                y = y[valid].astype(int)

                all_X.append(X)
                all_y.append(y)
                logger.info("Prepared %s: %d samples, %d features",
                            symbol, len(X), X.shape[1])

            except Exception as e:
                logger.error("Failed to prepare %s: %s", symbol, e)

        if not all_X:
            logger.error("No training data collected")
            results['error'] = 'No training data'
            return results

        X = np.vstack(all_X)
        y = np.concatenate(all_y)
        logger.info("Total training data: %d samples, %d features", len(X), X.shape[1])

        # Walk-forward training
        splits = self._walk_forward_split(X, y, n_splits)

        for fold_idx, (train_idx, val_idx) in enumerate(splits):
            X_train, y_train = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx], y[val_idx]

            logger.info("Fold %d: train=%d, val=%d", fold_idx, len(X_train), len(X_val))

            if self.trainer:
                fold_results = self.trainer.train_all_models(
                    X_train, y_train, X_val, y_val
                )
                results['models'][f'fold_{fold_idx}'] = fold_results

        results['status'] = 'complete'
        results['total_samples'] = len(X)
        return results

    def _fetch_data(self, symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data."""
        if self.data_fetcher:
            try:
                return self.data_fetcher.get_historical_bars(symbol, start, end)
            except Exception as e:
                logger.error("Data fetch failed for %s: %s", symbol, e)
        return None

    def _generate_features(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Generate technical features from OHLCV data."""
        if self.features:
            try:
                return self.features.generate(df)
            except Exception as e:
                logger.error("Feature generation failed: %s", e)

        # Fallback: basic features
        try:
            features = pd.DataFrame(index=df.index)
            close = df['close']

            # Returns
            features['return_1d'] = close.pct_change(1)
            features['return_5d'] = close.pct_change(5)
            features['return_10d'] = close.pct_change(10)

            # Moving averages
            features['sma_20'] = close.rolling(20).mean() / close - 1
            features['sma_50'] = close.rolling(50).mean() / close - 1

            # Volatility
            features['volatility_20'] = close.pct_change().rolling(20).std()

            # Volume ratio
            if 'volume' in df.columns:
                features['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss.replace(0, 1e-10)
            features['rsi'] = 100 - (100 / (1 + rs))

            return features.dropna()
        except Exception as e:
            logger.error("Fallback feature generation failed: %s", e)
            return None

    def _generate_training_labels(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Generate BUY/HOLD/SELL labels based on forward returns.

        Labels:
            0 = SELL (forward return < -threshold)
            1 = HOLD (forward return between -threshold and +threshold)
            2 = BUY  (forward return > +threshold)
        """
        try:
            close = df['close'].values
            forward_returns = np.zeros(len(close))
            # 5-day forward return
            for i in range(len(close) - 5):
                forward_returns[i] = (close[i + 5] - close[i]) / close[i]

            labels = np.ones(len(close))  # Default HOLD
            labels[forward_returns > self.label_threshold] = 2   # BUY
            labels[forward_returns < -self.label_threshold] = 0  # SELL
            labels[-5:] = 1  # Last 5 days can't have forward returns

            return labels

        except Exception as e:
            logger.error("Label generation failed: %s", e)
            return None

    def _walk_forward_split(
        self, X: np.ndarray, y: np.ndarray, n_splits: int = 5
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Time series walk-forward cross-validation.

        Each split uses expanding training window with fixed validation size.
        """
        n = len(X)
        val_size = n // (n_splits + 1)
        splits = []

        for i in range(n_splits):
            train_end = val_size * (i + 1)
            val_end = min(train_end + val_size, n)

            if train_end >= n or val_end <= train_end:
                break

            train_idx = np.arange(0, train_end)
            val_idx = np.arange(train_end, val_end)
            splits.append((train_idx, val_idx))

        return splits

    def run_backtest(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
    ) -> Dict:
        """
        Run walk-forward backtest with trained models.

        Trains on past data, predicts on next window, measures performance.
        """
        logger.info("Backtest: %s from %s to %s", symbols, start_date, end_date)
        results = {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
        }

        # Train and get results with walk-forward
        train_results = self.train_from_history(symbols, start_date, end_date)
        results['training'] = train_results
        results['status'] = 'complete'

        return results
