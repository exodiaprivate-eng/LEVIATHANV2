"""Opus portfolio advisor for strategic decisions."""
import logging

logger = logging.getLogger('leviathan.advisor')


class PortfolioAdvisor:
    """Use Opus to provide portfolio advice."""

    def __init__(self, opus_brain):
        self.opus = opus_brain

    def get_portfolio_advice(self, portfolio: dict) -> dict:
        """Use Opus to analyze the portfolio and provide strategic advice."""
        import json

        # If no Opus brain or no client, return rule-based advice
        if not self.opus or not hasattr(self.opus, 'client'):
            return self._rule_based_advice(portfolio)

        try:
            prompt = (
                f"Analyze this trading portfolio and provide strategic advice.\n\n"
                f"Portfolio: {json.dumps(portfolio, default=str)}\n\n"
                f"Respond ONLY with JSON:\n"
                f'{{"advice": "...", "risk_assessment": "low|medium|high", '
                f'"confidence": 0.0-1.0, "suggestions": ["..."], '
                f'"concentration_risk": "...", "sector_exposure": "..."}}'
            )

            resp = self.opus.client.messages.create(
                model='claude-sonnet-4-20250514', max_tokens=800,
                messages=[{'role': 'user', 'content': prompt}]
            )

            text = resp.content[0].text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            result = json.loads(text)

            # Ensure required fields
            result.setdefault('advice', 'Review portfolio')
            result.setdefault('confidence', 0.7)
            return result

        except Exception as e:
            logger.error(f"Opus portfolio advice failed: {e}")
            return self._rule_based_advice(portfolio)

    def _rule_based_advice(self, portfolio: dict) -> dict:
        """Fallback rule-based portfolio advice when Opus is unavailable."""
        positions = portfolio.get('positions', {})
        total_value = portfolio.get('total_value', 0)

        if not positions:
            return {'advice': 'Portfolio is empty — consider building positions',
                    'confidence': 0.9, 'risk_assessment': 'low'}

        # Check concentration
        max_pct = 0
        max_symbol = ''
        for sym, info in positions.items():
            pct = info.get('pct', 0) if isinstance(info, dict) else 0
            if pct > max_pct:
                max_pct = pct
                max_symbol = sym

        suggestions = []
        risk = 'medium'

        if max_pct > 0.30:
            suggestions.append(f"Reduce {max_symbol} concentration ({max_pct:.0%} of portfolio)")
            risk = 'high'
        if len(positions) < 3:
            suggestions.append("Diversify — fewer than 3 holdings")
        if len(positions) > 15:
            suggestions.append("Consider consolidating — too many positions may dilute returns")

        advice = 'Maintain diversification' if not suggestions else '; '.join(suggestions)
        return {
            'advice': advice,
            'confidence': 0.7,
            'risk_assessment': risk,
            'suggestions': suggestions,
        }

    def suggest_rebalance(self, current: dict, target: dict) -> list:
        trades = []
        for symbol, target_pct in target.items():
            current_pct = current.get(symbol, 0)
            diff = target_pct - current_pct
            if abs(diff) > 0.02:
                trades.append({'symbol': symbol, 'action': 'buy' if diff > 0 else 'sell',
                               'amount_pct': abs(diff)})
        return trades
