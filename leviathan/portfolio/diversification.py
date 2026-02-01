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
        return 0.5  # Placeholder
