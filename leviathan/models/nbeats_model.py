"""N-BEATS model for time series forecasting."""
import logging
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

logger = logging.getLogger('leviathan.models.nbeats')


class NBEATSBlock(nn.Module):
    def __init__(self, input_size: int, theta_size: int, hidden_size: int = 256):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, hidden_size), nn.ReLU(),
            nn.Linear(hidden_size, hidden_size), nn.ReLU(),
            nn.Linear(hidden_size, hidden_size), nn.ReLU(),
            nn.Linear(hidden_size, hidden_size), nn.ReLU(),
        )
        self.theta_b = nn.Linear(hidden_size, theta_size)
        self.theta_f = nn.Linear(hidden_size, theta_size)
        self.backcast = nn.Linear(theta_size, input_size)
        self.forecast = nn.Linear(theta_size, input_size)

    def forward(self, x):
        h = self.fc(x)
        return self.backcast(self.theta_b(h)), self.forecast(self.theta_f(h))


class NBEATSModel(nn.Module):
    def __init__(self, input_size: int = 20, num_blocks: int = 4,
                 hidden_size: int = 256, theta_size: int = 32):
        super().__init__()
        self.blocks = nn.ModuleList([
            NBEATSBlock(input_size, theta_size, hidden_size) for _ in range(num_blocks)
        ])
        self.fc_out = nn.Linear(input_size, 3)  # Buy/Hold/Sell

    def forward(self, x):
        residual = x
        forecast_sum = torch.zeros_like(x)
        for block in self.blocks:
            backcast, forecast = block(residual)
            residual = residual - backcast
            forecast_sum = forecast_sum + forecast
        return self.fc_out(forecast_sum)


class NBEATSWrapper:
    def __init__(self, input_size: int = 20, num_blocks: int = 4, lr: float = 0.001):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = NBEATSModel(input_size, num_blocks).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.CrossEntropyLoss()
        self.trained = False

    def train(self, X_train, y_train, epochs: int = 50, batch_size: int = 32):
        self.model.train()
        X = torch.FloatTensor(np.array(X_train)).to(self.device)
        y = torch.LongTensor(np.array(y_train)).to(self.device)
        dataset = torch.utils.data.TensorDataset(X, y)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        for epoch in range(epochs):
            total_loss = 0
            for bx, by in loader:
                self.optimizer.zero_grad()
                out = self.model(bx)
                loss = self.criterion(out, by)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            if epoch % 10 == 0:
                logger.info(f"N-BEATS epoch {epoch}: loss={total_loss/len(loader):.4f}")
        self.trained = True

    def predict(self, X) -> np.ndarray:
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(np.array(X)).to(self.device)
            out = self.model(x)
            return torch.softmax(out, dim=1).cpu().numpy()

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.trained = True
