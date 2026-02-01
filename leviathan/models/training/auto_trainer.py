"""Automatic model retraining based on schedules and performance degradation."""
import logging
import numpy as np
from datetime import datetime, timedelta

import schedule

logger = logging.getLogger('leviathan.auto_trainer')


class AutoTrainer:
    """Automatically retrains models based on schedules and performance."""

    def __init__(self, learning_db, model_trainer, alpaca_client=None, feature_engine=None):
        self.db = learning_db
        self.trainer = model_trainer
        self.alpaca_client = alpaca_client
        self.feature_engine = feature_engine
        self.performance_threshold = 0.20
        self.sharpe_threshold = 0.5  # Minimum acceptable Sharpe ratio

    def setup_schedules(self):
        schedule.every().saturday.at("02:00").do(self.scheduled_retrain)
        schedule.every().day.at("17:00").do(self.check_performance_degradation)
        schedule.every().hour.do(self.incremental_update)

    def scheduled_retrain(self):
        logger.info("Running scheduled weekly retrain")
        self._run_training_session('scheduled', 'Weekly scheduled retrain', 365)

    def check_performance_degradation(self):
        """Use Sharpe ratio as degradation trigger, not win rate."""
        recent_sharpe = self._calculate_recent_sharpe(days=14)
        baseline_sharpe = self._calculate_recent_sharpe(days=90)

        if recent_sharpe is None or baseline_sharpe is None:
            return

        if baseline_sharpe > 0 and recent_sharpe < baseline_sharpe * (1 - self.performance_threshold):
            logger.warning(
                f"Performance degradation: Sharpe {baseline_sharpe:.3f} -> {recent_sharpe:.3f}"
            )
            self._run_training_session(
                'automatic',
                f'Performance degradation: Sharpe dropped from {baseline_sharpe:.3f} to {recent_sharpe:.3f}',
                180,
            )
        elif recent_sharpe < self.sharpe_threshold:
            logger.warning(f"Sharpe ratio below threshold: {recent_sharpe:.3f} < {self.sharpe_threshold}")
            self._run_training_session(
                'automatic',
                f'Sharpe below threshold: {recent_sharpe:.3f} < {self.sharpe_threshold}',
                180,
            )

    def incremental_update(self):
        recent = self.db.get_recent_trades(hours=24)
        if len(recent) >= 3:
            self.trainer.online_update(recent)

    def manual_retrain(self, lookback_days: int = 365, specific_model: str = None,
                       custom_params: dict = None):
        self._run_training_session('manual', f'Manual trigger: {custom_params}', lookback_days,
                                   specific_model, custom_params)

    def _calculate_recent_sharpe(self, days: int = 14) -> float:
        """Calculate annualized Sharpe ratio from recent trades in learning DB."""
        trades = self.db.get_recent_trades(days=days)
        if not trades or len(trades) < 2:
            return None

        returns = [t['profit_loss_pct'] for t in trades if t.get('profit_loss_pct') is not None]
        if len(returns) < 2:
            return None

        returns_arr = np.array(returns, dtype=float)
        mean_ret = np.mean(returns_arr)
        std_ret = np.std(returns_arr, ddof=1)

        if std_ret == 0:
            return 0.0

        # Annualize assuming ~252 trading days.  Estimate trades per year from
        # the sample: trades_per_day * 252.
        trades_per_day = len(returns) / max(days, 1)
        annualization_factor = np.sqrt(trades_per_day * 252)
        sharpe = (mean_ret / std_ret) * annualization_factor
        return float(sharpe)

    def _fetch_training_data(self, lookback_days: int = 365, symbols: list = None):
        """Fetch OHLCV + feature data for model training.

        Returns (X, y) numpy arrays ready for model consumption.  If no
        alpaca_client is configured falls back to learning DB trade history.
        """
        import pandas as pd

        if symbols is None:
            # Derive symbols from recent trades
            recent = self.db.get_recent_trades(days=lookback_days)
            symbols = list({t['symbol'] for t in recent if t.get('symbol')})

        if not symbols:
            logger.warning("No symbols available for training data fetch")
            return None, None

        all_frames = []
        for symbol in symbols:
            try:
                if self.alpaca_client:
                    bars = self.alpaca_client.get_historical_bars(symbol, days=lookback_days)
                    if bars is not None and not (hasattr(bars, '__len__') and len(bars) == 0):
                        df = pd.DataFrame(bars) if not isinstance(bars, pd.DataFrame) else bars
                        df['symbol'] = symbol
                        all_frames.append(df)
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")

        if not all_frames:
            logger.warning("No training data fetched for any symbol")
            return None, None

        data = pd.concat(all_frames, ignore_index=True)

        # Build features if engine available
        if self.feature_engine and hasattr(self.feature_engine, 'compute'):
            data = self.feature_engine.compute(data)

        # Construct target: next-bar return direction (1 = up, 0 = down)
        if 'close' in data.columns:
            data['target'] = (data['close'].shift(-1) > data['close']).astype(int)
            data.dropna(inplace=True)

        feature_cols = [c for c in data.columns if c not in ('target', 'symbol', 'timestamp', 'date')]
        X = data[feature_cols].values.astype(float)
        y = data['target'].values.astype(float) if 'target' in data.columns else None

        logger.info(f"Fetched training data: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y

    def _calculate_improvement(self, old_metrics: dict, new_metrics: dict) -> float:
        """Compare old vs new model metrics and return improvement percentage.

        Primary metric is Sharpe ratio when available; falls back to accuracy.
        """
        def _extract_sharpe(m: dict) -> float:
            """Try to pull a numeric Sharpe value from a metrics dict."""
            if isinstance(m, dict):
                for key in ('sharpe', 'sharpe_ratio', 'avg_sharpe'):
                    if key in m and isinstance(m[key], (int, float)):
                        return float(m[key])
                # Try nested per-model dicts
                sharpes = []
                for v in m.values():
                    if isinstance(v, dict):
                        for key in ('sharpe', 'sharpe_ratio'):
                            if key in v and isinstance(v[key], (int, float)):
                                sharpes.append(float(v[key]))
                if sharpes:
                    return float(np.mean(sharpes))
            return None

        old_sharpe = _extract_sharpe(old_metrics)
        new_sharpe = _extract_sharpe(new_metrics)

        if old_sharpe is not None and new_sharpe is not None:
            if old_sharpe == 0:
                return 100.0 if new_sharpe > 0 else 0.0
            return ((new_sharpe - old_sharpe) / abs(old_sharpe)) * 100.0

        # Fallback: compare accuracy / win_rate
        def _extract_accuracy(m: dict) -> float:
            if isinstance(m, dict):
                for key in ('accuracy', 'win_rate'):
                    if key in m and isinstance(m[key], (int, float)):
                        return float(m[key])
            return None

        old_acc = _extract_accuracy(old_metrics)
        new_acc = _extract_accuracy(new_metrics)
        if old_acc is not None and new_acc is not None and old_acc > 0:
            return ((new_acc - old_acc) / old_acc) * 100.0

        return 0.0

    def _notify_for_approval(self, results: dict):
        """Log training results and flag for human approval before deployment."""
        improvement = results.get('improvement_pct', 0)
        session_id = results.get('session_id')
        new_metrics = results.get('new_metrics', {})
        old_metrics = results.get('old_metrics', {})

        logger.info(
            f"=== RETRAINING COMPLETE (session {session_id}) ===\n"
            f"  Improvement: {improvement:+.2f}%\n"
            f"  Old metrics: {old_metrics}\n"
            f"  New metrics: {new_metrics}\n"
            f"  Status: AWAITING APPROVAL — review before deploying."
        )

        if improvement > 0:
            logger.info(f"Session {session_id}: positive improvement, recommended for deployment.")
        else:
            logger.warning(f"Session {session_id}: no improvement — deployment NOT recommended.")

    # ------------------------------------------------------------------ #

    def _run_training_session(self, session_type, trigger_reason, lookback_days,
                              specific_model=None, custom_params=None):
        session_id = self.db.start_training_session(session_type, trigger_reason)
        try:
            current_metrics = self.trainer.evaluate_current_models()
            X, y = self._fetch_training_data(lookback_days)

            if X is None or y is None:
                logger.warning(f"Session {session_id}: no training data available, skipping")
                self.db.fail_training_session(session_id, "No training data available")
                return

            results = self.trainer.train_all(X, y)
            new_metrics = self.trainer.evaluate_current_models()
            improvement = self._calculate_improvement(current_metrics, new_metrics)

            self.db.complete_training_session(
                session_id, len(y), current_metrics, new_metrics, improvement
            )

            self._notify_for_approval({
                'session_id': session_id,
                'improvement_pct': improvement,
                'old_metrics': current_metrics,
                'new_metrics': new_metrics,
                'train_results': results,
            })

            logger.info(f"Training session {session_id} completed: {results}")
        except Exception as e:
            self.db.fail_training_session(session_id, str(e))
            logger.error(f"Training session {session_id} failed: {e}")
