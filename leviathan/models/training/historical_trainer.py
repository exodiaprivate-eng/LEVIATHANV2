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

        # Collect all data first
        all_X, all_y, all_prices = [], [], []
        for symbol in symbols:
            try:
                df = self._fetch_data(symbol, start_date, end_date)
                if df is None or len(df) < 100:
                    continue
                features_df = self._generate_features(df)
                labels = self._generate_training_labels(df)
                if features_df is None or labels is None:
                    continue

                min_len = min(len(features_df), len(labels), len(df))
                X = features_df.values[:min_len]
                y = labels[:min_len]
                prices = df['close'].values[:min_len]

                valid = ~(np.isnan(X).any(axis=1) | np.isnan(y))
                all_X.append(X[valid])
                all_y.append(y[valid].astype(int))
                all_prices.append(prices[valid])
            except Exception as e:
                logger.error("Backtest data prep failed for %s: %s", symbol, e)

        if not all_X:
            results['error'] = 'No data'
            results['status'] = 'failed'
            return results

        X = np.vstack(all_X)
        y = np.concatenate(all_y)
        prices = np.concatenate(all_prices)

        # Walk-forward: train on first portion, test on remainder
        splits = self._walk_forward_split(X, y, n_splits=5)
        all_returns = []
        total_wins = 0
        total_trades = 0

        for fold_idx, (train_idx, val_idx) in enumerate(splits):
            X_train, y_train = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx], y[val_idx]
            val_prices = prices[val_idx]

            # Train models on this fold
            if self.trainer:
                try:
                    self.trainer.train_all(X_train, y_train, X_val, y_val)
                except Exception as e:
                    logger.error("Fold %d training failed: %s", fold_idx, e)
                    continue

            # Generate predictions on validation set
            preds = np.ones(len(y_val))  # default HOLD
            if self.trainer:
                for name, model in [('lstm', self.trainer.lstm),
                                     ('lgbm', self.trainer.lgbm),
                                     ('nbeats', self.trainer.nbeats)]:
                    if model is None:
                        continue
                    try:
                        if name == 'lstm':
                            X_3d = X_val.reshape(X_val.shape[0], 1, X_val.shape[1])
                            p, _ = model.predict(X_3d)
                        else:
                            p = model.predict(X_val)
                            if isinstance(p, tuple):
                                p = p[0]
                        preds = np.asarray(p).flatten()
                        break  # Use first working model
                    except Exception:
                        continue

            # Simulate trades: BUY=2, SELL=0, HOLD=1
            fold_returns = []
            for i in range(len(preds) - 1):
                if preds[i] == 2:  # BUY signal
                    ret = (val_prices[i + 1] - val_prices[i]) / val_prices[i]
                    fold_returns.append(ret)
                    total_trades += 1
                    if ret > 0:
                        total_wins += 1
                elif preds[i] == 0:  # SELL signal
                    ret = (val_prices[i] - val_prices[i + 1]) / val_prices[i]
                    fold_returns.append(ret)
                    total_trades += 1
                    if ret > 0:
                        total_wins += 1

            all_returns.extend(fold_returns)

        # Compute metrics
        if all_returns:
            returns_arr = np.array(all_returns)
            results['total_return'] = float(np.sum(returns_arr))
            mean_r = np.mean(returns_arr)
            std_r = np.std(returns_arr, ddof=1) if len(returns_arr) > 1 else 1.0
            results['sharpe_ratio'] = float((mean_r / std_r) * np.sqrt(252)) if std_r > 0 else 0.0

            # Max drawdown from cumulative returns
            cum = np.cumsum(returns_arr)
            peak = np.maximum.accumulate(cum)
            dd = cum - peak
            results['max_drawdown'] = float(np.min(dd)) if len(dd) > 0 else 0.0

        results['total_trades'] = total_trades
        results['win_rate'] = total_wins / total_trades if total_trades > 0 else 0.0
        results['status'] = 'complete'

        # Also include training results
        train_results = self.train_from_history(symbols, start_date, end_date)
        results['training'] = train_results

        return results
