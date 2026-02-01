"""
Portfolio Analyzer Module.

Correlation analysis, concentration checks, and diversification scoring.
"""
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Analyzes portfolio for correlation and concentration risks."""

    def analyze_correlation(
        self,
        positions: Dict[str, dict],
        price_data: Dict[str, np.ndarray],
    ) -> Dict[str, any]:
        """
        Calculate correlation matrix for current positions.

        Args:
            positions: {symbol: position_info}
            price_data: {symbol: array of prices}

        Returns:
            Dict with correlation_matrix, high_correlation_pairs
        """
        symbols = [s for s in positions if s in price_data]
        if len(symbols) < 2:
            return {"correlation_matrix": {}, "high_correlation_pairs": []}

        # Calculate returns
        returns = {}
        for sym in symbols:
            prices = price_data[sym]
            if len(prices) > 1:
                returns[sym] = np.diff(prices) / prices[:-1]

        valid_symbols = [s for s in symbols if s in returns]
        if len(valid_symbols) < 2:
            return {"correlation_matrix": {}, "high_correlation_pairs": []}

        # Build matrix
        min_len = min(len(returns[s]) for s in valid_symbols)
        matrix = np.array([returns[s][:min_len] for s in valid_symbols])
        corr = np.corrcoef(matrix)

        # Find high correlation pairs
        high_pairs = []
        for i in range(len(valid_symbols)):
            for j in range(i + 1, len(valid_symbols)):
                c = corr[i][j]
                if abs(c) > 0.7:
                    high_pairs.append({
                        "pair": (valid_symbols[i], valid_symbols[j]),
                        "correlation": float(c),
                    })

        # Build dict representation
        corr_dict = {}
        for i, sym in enumerate(valid_symbols):
            corr_dict[sym] = {
                valid_symbols[j]: float(corr[i][j])
                for j in range(len(valid_symbols))
            }

        return {
            "correlation_matrix": corr_dict,
            "high_correlation_pairs": high_pairs,
        }

    def check_concentration(
        self,
        positions: Dict[str, dict],
        max_single: float = 0.20,
        max_sector: float = 0.30,
    ) -> Tuple[bool, List[str]]:
        """
        Check if portfolio concentration is within limits.

        Returns:
            (is_ok: bool, warnings: list of warning strings)
        """
        warnings = []
        total_value = sum(p.get("market_value", 0) for p in positions.values())
        if total_value <= 0:
            return True, []

        # Single position concentration
        for sym, pos in positions.items():
            pct = pos.get("market_value", 0) / total_value
            if pct > max_single:
                warnings.append(
                    f"{sym} at {pct:.1%} exceeds {max_single:.0%} single position limit"
                )

        # Sector concentration (basic mapping)
        from leviathan.risk.portfolio import PortfolioRisk
        pr = PortfolioRisk()
        sector_exp = pr.get_sector_exposure(positions)
        for sector, pct in sector_exp.items():
            if pct > max_sector:
                warnings.append(
                    f"{sector} sector at {pct:.1%} exceeds {max_sector:.0%} limit"
                )

        is_ok = len(warnings) == 0
        if not is_ok:
            logger.warning("Concentration warnings: %s", warnings)
        return is_ok, warnings

    def get_diversification_score(self, positions: Dict[str, dict]) -> float:
        """
        Calculate diversification score from 0.0 (concentrated) to 1.0 (diversified).

        Uses inverse HHI normalized to [0, 1].
        """
        total_value = sum(p.get("market_value", 0) for p in positions.values())
        n = len(positions)
        if n <= 1 or total_value <= 0:
            return 0.0

        weights = [p.get("market_value", 0) / total_value for p in positions.values()]
        hhi = sum(w ** 2 for w in weights)

        # Normalize: HHI ranges from 1/n (perfect diversification) to 1.0 (single stock)
        min_hhi = 1.0 / n
        if hhi <= min_hhi:
            return 1.0

        score = (1.0 - hhi) / (1.0 - min_hhi)
        return max(0.0, min(1.0, score))
