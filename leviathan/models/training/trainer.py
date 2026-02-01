"""Model training orchestration."""
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger('leviathan.training')

MODELS_DIR = Path(__file__).parent.parent / 'saved'
MODELS_DIR.mkdir(exist_ok=True)


class ModelTrainer:
    """Orchestrates training of all ML models."""

    def __init__(self, lstm_wrapper=None, lgbm_predictor=None, nbeats_wrapper=None,
                 learning_db=None):
        self.lstm = lstm_wrapper
        self.lgbm = lgbm_predictor
        self.nbeats = nbeats_wrapper
        self.db = learning_db

    def train_all(self, X_train, y_train, X_val=None, y_val=None):
        results = {}
        if self.lstm:
            try:
                self.lstm.train(X_train, y_train, X_val, y_val)
                self.lstm.save(str(MODELS_DIR / 'lstm_latest.pt'))
                results['lstm'] = 'success'
            except Exception as e:
                logger.error(f"LSTM training failed: {e}")
                results['lstm'] = f'failed: {e}'

        if self.lgbm:
            try:
                self.lgbm.train(X_train, y_train, X_val, y_val)
                self.lgbm.save(str(MODELS_DIR / 'lgbm_latest.pkl'))
                results['lgbm'] = 'success'
            except Exception as e:
                logger.error(f"LightGBM training failed: {e}")
                results['lgbm'] = f'failed: {e}'

        if self.nbeats:
            try:
                self.nbeats.train(X_train, y_train)
                self.nbeats.save(str(MODELS_DIR / 'nbeats_latest.pt'))
                results['nbeats'] = 'success'
            except Exception as e:
                logger.error(f"N-BEATS training failed: {e}")
                results['nbeats'] = f'failed: {e}'

        return results

    def evaluate_current_models(self) -> dict:
        """Run predictions on recent data and return accuracy/Sharpe/win_rate per model.

        Pulls the most recent trades from the learning DB and evaluates each
        loaded model against actual outcomes to produce real performance metrics.
        """
        metrics = {}

        # Gather recent trade data for evaluation
        recent_trades = []
        if self.db:
            recent_trades = self.db.get_recent_trades(days=30)

        model_entries = [
            ('lstm', self.lstm),
            ('lgbm', self.lgbm),
            ('nbeats', self.nbeats),
        ]

        for name, model in model_entries:
            if model is None:
                metrics[name] = {'status': 'not_loaded'}
                continue

            # Check if model is trained
            is_trained = False
            if hasattr(model, 'trained'):
                is_trained = model.trained
            elif hasattr(model, 'model'):
                is_trained = model.model is not None
            if not is_trained:
                metrics[name] = {'status': 'not_trained'}
                continue

            if not recent_trades or len(recent_trades) < 5:
                metrics[name] = {'status': 'trained', 'note': 'insufficient_eval_data'}
                continue

            # Build feature vectors from trade data and predict
            try:
                returns = np.array([t['profit_loss_pct'] for t in recent_trades
                                    if t.get('profit_loss_pct') is not None], dtype=float)
                actuals = (returns > 0).astype(int)

                # Create a simple feature matrix from available trade fields
                features = returns.reshape(-1, 1)

                # Handle models that need 3-D input (LSTM)
                try:
                    if name == 'lstm':
                        X_eval = features.reshape(features.shape[0], 1, features.shape[1])
                        preds = model.predict(X_eval)
                    else:
                        preds = model.predict(features)
                except Exception:
                    # Model may require different input shape; mark and skip
                    metrics[name] = {'status': 'trained', 'note': 'eval_input_mismatch'}
                    continue

                # Normalise predictions to binary
                if isinstance(preds, tuple):
                    preds = preds[0]  # Some models return (preds, probas)
                preds = np.asarray(preds).flatten()
                pred_classes = (preds > 0.5).astype(int) if preds.max() <= 1.0 else (preds > 0).astype(int)

                n = len(actuals)
                correct = int(np.sum(pred_classes == actuals))
                accuracy = correct / n if n > 0 else 0.0
                win_rate = float(np.mean(actuals))

                # Sharpe from predicted-aligned returns
                aligned_returns = np.where(pred_classes == actuals, np.abs(returns), -np.abs(returns))
                mean_r = np.mean(aligned_returns)
                std_r = np.std(aligned_returns, ddof=1) if len(aligned_returns) > 1 else 1.0
                sharpe = (mean_r / std_r) * np.sqrt(252) if std_r > 0 else 0.0

                metrics[name] = {
                    'status': 'trained',
                    'accuracy': round(accuracy, 4),
                    'sharpe': round(float(sharpe), 4),
                    'win_rate': round(win_rate, 4),
                    'eval_samples': n,
                }
            except Exception as e:
                logger.error(f"Evaluation of {name} failed: {e}")
                metrics[name] = {'status': 'trained', 'note': f'eval_error: {e}'}

        return metrics

    def evaluate_models(self, results: dict) -> dict:
        """Compare new model metrics against old and return improvement dict.

        ``results`` is expected to contain ``old_metrics`` and ``new_metrics``
        dicts keyed by model name, each with numeric metric values.
        """
        old_metrics = results.get('old_metrics', {})
        new_metrics = results.get('new_metrics', {})
        improvements = {}

        all_models = set(list(old_metrics.keys()) + list(new_metrics.keys()))
        for model_name in all_models:
            old_m = old_metrics.get(model_name, {})
            new_m = new_metrics.get(model_name, {})

            if not isinstance(old_m, dict) or not isinstance(new_m, dict):
                improvements[model_name] = {'improved': False, 'reason': 'non_dict_metrics'}
                continue

            # Compare Sharpe first, then accuracy
            improved = False
            detail = {}
            for metric_key in ('sharpe', 'sharpe_ratio', 'accuracy', 'win_rate'):
                old_val = old_m.get(metric_key)
                new_val = new_m.get(metric_key)
                if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                    delta = new_val - old_val
                    pct_change = (delta / abs(old_val) * 100) if old_val != 0 else (100.0 if delta > 0 else 0.0)
                    detail[metric_key] = {
                        'old': old_val,
                        'new': new_val,
                        'delta': round(delta, 6),
                        'pct_change': round(pct_change, 2),
                    }
                    if delta > 0:
                        improved = True

            improvements[model_name] = {
                'improved': improved,
                'metrics': detail,
            }

        return improvements

    def deploy_models(self, models: dict):
        """Save trained models to the deployment directory and log to learning DB."""
        import shutil
        from datetime import datetime

        logger.info(f"Deploying models: {list(models.keys())}")
        deployed = {}

        for name, model in models.items():
            try:
                # Determine source path (model may be an object or a path string)
                if isinstance(model, str):
                    src = Path(model)
                elif hasattr(model, 'save'):
                    # Save to a timestamped file first, then copy to 'latest'
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ext = '.pt' if name in ('lstm', 'nbeats') else '.pkl'
                    versioned = MODELS_DIR / f'{name}_{ts}{ext}'
                    model.save(str(versioned))
                    src = versioned
                else:
                    logger.warning(f"Cannot deploy {name}: unknown model type")
                    continue

                # Copy to the canonical 'latest' path
                ext = src.suffix
                latest = MODELS_DIR / f'{name}_latest{ext}'
                if src != latest:
                    shutil.copy2(str(src), str(latest))

                deployed[name] = str(latest)
                logger.info(f"Deployed {name} -> {latest}")

            except Exception as e:
                logger.error(f"Failed to deploy {name}: {e}")
                deployed[name] = f'failed: {e}'

        # Record deployment in learning DB
        if self.db and hasattr(self.db, 'mark_session_deployed'):
            try:
                # Get latest training session and mark it deployed
                conn = self.db._conn()
                row = conn.execute(
                    "SELECT id FROM training_sessions ORDER BY id DESC LIMIT 1"
                ).fetchone()
                conn.close()
                if row:
                    self.db.mark_session_deployed(row[0])
            except Exception as e:
                logger.error(f"Failed to mark deployment in DB: {e}")

        return deployed

    def online_update(self, recent_trades: list):
        """Incremental model update with new data points.

        Extracts returns from recent trades and performs a partial fit /
        fine-tune step on each model that supports it.
        """
        if not recent_trades:
            logger.info("Online update: no trades provided")
            return

        returns = np.array(
            [t['profit_loss_pct'] for t in recent_trades if t.get('profit_loss_pct') is not None],
            dtype=float,
        )
        if len(returns) < 2:
            logger.info("Online update: not enough data points")
            return

        targets = (returns > 0).astype(float)
        X = returns.reshape(-1, 1)

        updated = []
        for name, model in [('lstm', self.lstm), ('lgbm', self.lgbm), ('nbeats', self.nbeats)]:
            if model is None:
                continue

            try:
                # Use partial_fit if available (e.g. sklearn-style)
                if hasattr(model, 'partial_fit'):
                    model.partial_fit(X, targets)
                    updated.append(name)
                # LightGBM: refit with continue_training
                elif hasattr(model, 'model') and model.model is not None and hasattr(model, 'train'):
                    # Short fine-tune: 10 extra boosting rounds
                    model.train(X, targets, num_boost_round=10)
                    updated.append(name)
                # LSTM / N-BEATS: single-epoch fine-tune
                elif hasattr(model, 'train') and hasattr(model, 'trained') and model.trained:
                    if name == 'lstm':
                        X_3d = X.reshape(X.shape[0], 1, X.shape[1])
                        model.train(X_3d, targets)
                    else:
                        model.train(X, targets)
                    updated.append(name)
            except Exception as e:
                logger.error(f"Online update for {name} failed: {e}")

        logger.info(f"Online update completed for: {updated or 'none'} ({len(recent_trades)} trades)")
