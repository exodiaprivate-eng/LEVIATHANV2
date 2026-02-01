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
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        input_size = X_train.shape[-1]

        best_score = float('inf')
        best_params = {}

        for i in range(n_trials):
            params = {
                'hidden_size': random.choice([32, 64, 128, 256]),
                'num_layers': random.choice([1, 2, 3]),
                'dropout': random.choice([0.1, 0.2, 0.3, 0.4]),
                'lr': random.choice([0.0005, 0.001, 0.002, 0.005]),
                'batch_size': random.choice([32, 64, 128]),
            }

            try:
                from models.lstm_model import LSTMPredictor

                model = LSTMPredictor(
                    input_size=input_size,
                    hidden_size=params['hidden_size'],
                    num_layers=params['num_layers'],
                    dropout=params['dropout'],
                ).to(device)

                optimizer = torch.optim.Adam(model.parameters(), lr=params['lr'])
                criterion = nn.CrossEntropyLoss()

                X_t = torch.tensor(np.asarray(X_train), dtype=torch.float32).to(device)
                y_t = torch.tensor(np.asarray(y_train), dtype=torch.long).to(device)
                X_v = torch.tensor(np.asarray(X_val), dtype=torch.float32).to(device)
                y_v = torch.tensor(np.asarray(y_val), dtype=torch.long).to(device)

                loader = DataLoader(
                    TensorDataset(X_t, y_t),
                    batch_size=params['batch_size'], shuffle=True
                )

                # Quick train: 15 epochs per trial
                model.train()
                for epoch in range(15):
                    for X_b, y_b in loader:
                        optimizer.zero_grad()
                        logits = model(X_b)
                        loss = criterion(logits, y_b)
                        loss.backward()
                        optimizer.step()

                # Evaluate on validation set
                model.eval()
                with torch.no_grad():
                    val_logits = model(X_v)
                    val_loss = criterion(val_logits, y_v).item()

                if val_loss < best_score:
                    best_score = val_loss
                    best_params = params

                logger.info(f"LSTM trial {i+1}/{n_trials}: val_loss={val_loss:.4f} params={params}")

            except Exception as e:
                logger.error(f"LSTM trial {i+1} failed: {e}")
                continue

        if not best_params:
            best_params = {
                'hidden_size': 64, 'num_layers': 2, 'dropout': 0.2, 'lr': 0.001,
                'batch_size': 64,
            }
            logger.warning("All LSTM trials failed, returning defaults")

        logger.info(f"Best LSTM params (score={best_score:.4f}): {best_params}")
        return best_params
