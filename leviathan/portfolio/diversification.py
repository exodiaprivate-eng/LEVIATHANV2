"""Diversification templates and strategies."""

TEMPLATES = {
    'conservative': {
        'description': 'Low risk, index-heavy',
        'allocations': {'SPY': 0.40, 'QQQ': 0.20, 'BND': 0.30, 'GLD': 0.10}
    },
    'moderate': {
        'description': 'Balanced growth and stability',
        'allocations': {'SPY': 0.30, 'QQQ': 0.25, 'AAPL': 0.15, 'MSFT': 0.15, 'GOOGL': 0.15}
    },
    'aggressive': {
        'description': 'High growth, tech-heavy',
        'allocations': {'QQQ': 0.30, 'NVDA': 0.20, 'AMD': 0.15, 'TSLA': 0.15, 'META': 0.20}
    },
}


class DiversificationManager:
    def get_template(self, name: str) -> dict:
        return TEMPLATES.get(name, TEMPLATES['moderate'])

    def get_all_templates(self) -> dict:
        return TEMPLATES

    def calculate_correlation_score(self, holdings: dict) -> float:
        """Calculate portfolio diversification score based on sector overlap.

        Returns a score from 0.0 (perfectly diversified) to 1.0 (fully concentrated).
        Uses sector-based heuristic groupings when price data isn't available.
        """
        if not holdings or len(holdings) <= 1:
            return 1.0  # Single holding = fully concentrated

        # Sector mapping for common tickers
        SECTOR_MAP = {
            'SPY': 'broad', 'QQQ': 'tech', 'BND': 'bonds', 'GLD': 'commodity',
            'AAPL': 'tech', 'MSFT': 'tech', 'GOOGL': 'tech', 'META': 'tech',
            'AMZN': 'tech', 'NVDA': 'tech', 'AMD': 'tech', 'TSLA': 'auto',
            'JPM': 'finance', 'BAC': 'finance', 'GS': 'finance',
            'JNJ': 'health', 'UNH': 'health', 'PFE': 'health',
            'XOM': 'energy', 'CVX': 'energy', 'COP': 'energy',
            'DIS': 'media', 'NFLX': 'media', 'WMT': 'retail', 'TGT': 'retail',
        }

        # Group holdings by sector
        sector_weights = {}
        total_weight = sum(
            v if isinstance(v, (int, float)) else v.get('weight', v.get('pct', 1))
            if isinstance(v, dict) else 1
            for v in holdings.values()
        )

        if total_weight == 0:
            return 0.5

        for symbol, value in holdings.items():
            weight = (
                value if isinstance(value, (int, float))
                else value.get('weight', value.get('pct', 1)) if isinstance(value, dict)
                else 1
            )
            sector = SECTOR_MAP.get(symbol.upper(), 'other')
            sector_weights[sector] = sector_weights.get(sector, 0) + weight

        # Normalize
        for s in sector_weights:
            sector_weights[s] /= total_weight

        # Herfindahl-Hirschman Index (HHI) based on sector weights
        # HHI ranges from 1/n (perfect diversification) to 1 (single sector)
        hhi = sum(w ** 2 for w in sector_weights.values())
        n_sectors = len(sector_weights)

        # Normalize HHI to 0-1 scale
        min_hhi = 1.0 / n_sectors if n_sectors > 0 else 1.0
        if min_hhi >= 1.0:
            return 1.0

        score = (hhi - min_hhi) / (1.0 - min_hhi)
        return round(max(0.0, min(1.0, score)), 4)
