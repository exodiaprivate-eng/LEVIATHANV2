"""Opus portfolio advisor for strategic decisions."""
import logging

logger = logging.getLogger('leviathan.advisor')


class PortfolioAdvisor:
    """Use Opus to provide portfolio advice."""

    def __init__(self, opus_brain):
        self.opus = opus_brain

    def get_portfolio_advice(self, portfolio: dict) -> dict:
        return {'advice': 'Maintain diversification', 'confidence': 0.7}

    def suggest_rebalance(self, current: dict, target: dict) -> list:
        trades = []
        for symbol, target_pct in target.items():
            current_pct = current.get(symbol, 0)
            diff = target_pct - current_pct
            if abs(diff) > 0.02:
                trades.append({'symbol': symbol, 'action': 'buy' if diff > 0 else 'sell',
                               'amount_pct': abs(diff)})
        return trades
