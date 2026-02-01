"""
Portfolio-Level Risk Metrics.

Calculates VaR, beta, sector exposure, and concentration risk.
"""
import logging
import numpy as np
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PortfolioRisk:
    """Portfolio-level risk calculations."""

    # Basic sector mapping for common stocks
    SECTOR_MAP = {
        "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
        "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
        "META": "Technology", "NVDA": "Technology", "AMD": "Technology",
        "JPM": "Financial", "BAC": "Financial", "GS": "Financial",
        "JNJ": "Healthcare", "PFE": "Healthcare", "UNH": "Healthcare",
        "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
        "PG": "Consumer Staples", "KO": "Consumer Staples", "WMT": "Consumer Staples",
    }

    def calculate_portfolio_var(
        self,
        positions: Dict[str, dict],
        returns_data: Optional[Dict[str, np.ndarray]] = None,
        confidence: float = 0.95,
    ) -> float:
        """
        Calculate portfolio Value at Risk using historical simulation.

        Args:
            positions: {symbol: {qty, current_price, market_value}}
            returns_data: {symbol: array of daily returns}
            confidence: VaR confidence level (default 95%)

        Returns:
            VaR as a positive dollar amount (potential loss)
        """
        if not positions or not returns_data:
            return 0.0

        try:
            total_value = sum(p.get("market_value", 0) for p in positions.values())
            if total_value <= 0:
                return 0.0

            # Weight each position
            weights = {}
            for sym, pos in positions.items():
                weights[sym] = pos.get("market_value", 0) / total_value

            # Build portfolio returns
            common_symbols = [s for s in positions if s in returns_data]
            if not common_symbols:
                return 0.0

            min_len = min(len(returns_data[s]) for s in common_symbols)
            portfolio_returns = np.zeros(min_len)
            for sym in common_symbols:
                w = weights.get(sym, 0)
                portfolio_returns += w * returns_data[sym][:min_len]

            # Historical VaR
            var_pct = np.percentile(portfolio_returns, (1 - confidence) * 100)
            var_dollar = abs(var_pct) * total_value

            logger.debug("Portfolio VaR (%.0f%%): $%.2f", confidence * 100, var_dollar)
            return var_dollar

        except Exception as e:
            logger.error("VaR calculation failed: %s", e)
            return 0.0

    def calculate_portfolio_beta(
        self,
        positions: Dict[str, dict],
        position_returns: Dict[str, np.ndarray],
        market_returns: np.ndarray,
    ) -> float:
        """Calculate portfolio beta relative to market."""
        if not positions or not position_returns or len(market_returns) == 0:
            return 1.0

        try:
            total_value = sum(p.get("market_value", 0) for p in positions.values())
            if total_value <= 0:
                return 1.0

            weighted_beta = 0.0
            for sym, pos in positions.items():
                if sym not in position_returns:
                    continue
                w = pos.get("market_value", 0) / total_value
                ret = position_returns[sym]
                min_len = min(len(ret), len(market_returns))
                cov = np.cov(ret[:min_len], market_returns[:min_len])[0][1]
                var = np.var(market_returns[:min_len])
                beta = cov / var if var > 0 else 1.0
                weighted_beta += w * beta

            return weighted_beta

        except Exception as e:
            logger.error("Beta calculation failed: %s", e)
            return 1.0

    def get_sector_exposure(self, positions: Dict[str, dict]) -> Dict[str, float]:
        """Calculate sector exposure as percentage of portfolio."""
        total_value = sum(p.get("market_value", 0) for p in positions.values())
        if total_value <= 0:
            return {}

        sector_values: Dict[str, float] = {}
        for sym, pos in positions.items():
            sector = self.SECTOR_MAP.get(sym, "Unknown")
            mv = pos.get("market_value", 0)
            sector_values[sector] = sector_values.get(sector, 0) + mv

        return {s: v / total_value for s, v in sector_values.items()}

    def get_concentration_risk(self, positions: Dict[str, dict]) -> Dict[str, float]:
        """Calculate position concentration (HHI-like metric)."""
        total_value = sum(p.get("market_value", 0) for p in positions.values())
        if total_value <= 0:
            return {"hhi": 0.0, "max_position_pct": 0.0, "positions": {}}

        weights = {}
        for sym, pos in positions.items():
            weights[sym] = pos.get("market_value", 0) / total_value

        hhi = sum(w ** 2 for w in weights.values())
        max_pct = max(weights.values()) if weights else 0.0

        return {
            "hhi": hhi,
            "max_position_pct": max_pct,
            "positions": weights,
        }
