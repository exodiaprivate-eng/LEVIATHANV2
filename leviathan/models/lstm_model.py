"""LSTM model for price direction prediction."""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, Optional, Tuple


class LSTMPredictor(nn.Module):
    """LSTM neural network for BUY/HOLD/SELL classification."""

    def __init__(self, input_size: int, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 3),  # BUY, HOLD, SELL
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])


class LSTMWrapper:
    """Training / inference wrapper around LSTMPredictor."""

    def __init__(self, config: dict):
        self.config = config
        self.input_size: int = config.get("input_size", 10)
        self.hidden_size: int = config.get("hidden_size", 64)
        self.num_layers: int = config.get("num_layers", 2)
        self.dropout: float = config.get("dropout", 0.2)
        self.learning_rate: float = config.get("learning_rate", 1e-3)
        self.batch_size: int = config.get("batch_size", 64)
        self.epochs: int = config.get("epochs", 100)
        self.patience: int = config.get("patience", 10)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[LSTMPredictor] = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_tensor(self, arr: np.ndarray, dtype=torch.float32) -> torch.Tensor:
        if isinstance(arr, torch.Tensor):
            return arr.to(dtype).to(self.device)
        return torch.tensor(np.asarray(arr), dtype=dtype).to(self.device)

    def _make_loader(self, X: np.ndarray, y: np.ndarray, shuffle: bool = True) -> DataLoader:
        X_t = self._to_tensor(X)
        y_t = self._to_tensor(y, dtype=torch.long)
        return DataLoader(TensorDataset(X_t, y_t), batch_size=self.batch_size, shuffle=shuffle)

    # ------------------------------------------------------------------
    # Train
    # ------------------------------------------------------------------

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray) -> Dict:
        """Full training loop with early stopping. Returns metrics dict."""

        self.input_size = X_train.shape[-1]
        self.model = LSTMPredictor(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
        ).to(self.device)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.CrossEntropyLoss()

        train_loader = self._make_loader(X_train, y_train, shuffle=True)
        val_loader = self._make_loader(X_val, y_val, shuffle=False)

        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
        best_val_loss = float("inf")
        best_state = None
        wait = 0

        for epoch in range(self.epochs):
            # --- training ---
            self.model.train()
            epoch_loss, correct, total = 0.0, 0, 0
            for X_b, y_b in train_loader:
                optimizer.zero_grad()
                logits = self.model(X_b)
                loss = criterion(logits, y_b)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * X_b.size(0)
                correct += (logits.argmax(dim=1) == y_b).sum().item()
                total += X_b.size(0)

            train_loss = epoch_loss / total
            train_acc = correct / total

            # --- validation ---
            self.model.eval()
            val_loss_sum, val_correct, val_total = 0.0, 0, 0
            with torch.no_grad():
                for X_b, y_b in val_loader:
                    logits = self.model(X_b)
                    val_loss_sum += criterion(logits, y_b).item() * X_b.size(0)
                    val_correct += (logits.argmax(dim=1) == y_b).sum().item()
                    val_total += X_b.size(0)

            val_loss = val_loss_sum / val_total
            val_acc = val_correct / val_total

            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            history["train_acc"].append(train_acc)
            history["val_acc"].append(val_acc)

            # --- early stopping ---
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                wait = 0
            else:
                wait += 1
                if wait >= self.patience:
                    break

        # Restore best weights
        if best_state is not None:
            self.model.load_state_dict(best_state)
            self.model.to(self.device)

        return {
            "history": history,
            "best_val_loss": best_val_loss,
            "epochs_trained": len(history["train_loss"]),
            "final_train_acc": history["train_acc"][-1],
            "final_val_acc": history["val_acc"][-1],
        }

    # ------------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Return (predictions, probabilities) arrays."""
        if self.model is None:
            raise RuntimeError("Model not trained or loaded.")

        self.model.eval()
        X_t = self._to_tensor(X)
        with torch.no_grad():
            logits = self.model(X_t)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = logits.argmax(dim=1).cpu().numpy()
        return preds, probs

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        if self.model is None:
            raise RuntimeError("No model to save.")
        torch.save({
            "state_dict": self.model.state_dict(),
            "config": {
                "input_size": self.input_size,
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "dropout": self.dropout,
            },
        }, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path, map_location=self.device)
        cfg = checkpoint["config"]
        self.input_size = cfg["input_size"]
        self.hidden_size = cfg["hidden_size"]
        self.num_layers = cfg["num_layers"]
        self.dropout = cfg["dropout"]
        self.model = LSTMPredictor(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
        ).to(self.device)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()
