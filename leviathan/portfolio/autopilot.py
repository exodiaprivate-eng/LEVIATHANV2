"""Long-term portfolio autopilot for auto-diversification and rotation."""
import logging

logger = logging.getLogger('leviathan.autopilot')


class PortfolioAutopilot:
    """Automatic portfolio management for long-term holdings."""

    def __init__(self, alpaca_client, opus_brain=None):
        self.alpaca = alpaca_client
        self.opus = opus_brain

    def auto_diversify(self, account_value: float, template: str = 'moderate') -> dict:
        templates = {
            'conservative': {'SPY': 0.4, 'QQQ': 0.2, 'BND': 0.3, 'GLD': 0.1},
            'moderate': {'SPY': 0.3, 'QQQ': 0.25, 'AAPL': 0.15, 'MSFT': 0.15, 'GOOGL': 0.15},
            'aggressive': {'QQQ': 0.3, 'NVDA': 0.2, 'AMD': 0.15, 'TSLA': 0.15, 'META': 0.2},
        }
        alloc = templates.get(template, templates['moderate'])
        return {'template': template, 'allocations': alloc, 'account_value': account_value}

    def rotate_holdings(self) -> dict:
        """Evaluate current holdings and suggest sector rotation based on momentum."""
        try:
            positions = self.alpaca.get_positions()
        except Exception as e:
            logger.error(f"Failed to get positions for rotation: {e}")
            return {'status': 'error', 'error': str(e)}

        if not positions:
            return {'status': 'no_positions'}

        # Evaluate each holding's recent performance
        underperformers = []
        performers = []
        for pos in positions:
            symbol = getattr(pos, 'symbol', '')
            if '/' in symbol:  # skip crypto
                continue
            pnl_pct = float(getattr(pos, 'unrealized_plpc', 0))
            market_value = float(getattr(pos, 'market_value', 0))
            if pnl_pct < -0.05:  # Down more than 5%
                underperformers.append({
                    'symbol': symbol, 'pnl_pct': pnl_pct, 'value': market_value
                })
            else:
                performers.append({
                    'symbol': symbol, 'pnl_pct': pnl_pct, 'value': market_value
                })

        if not underperformers:
            return {'status': 'no_rotation_needed', 'holdings_checked': len(positions)}

        # If Opus brain is available, ask for rotation advice
        rotation_suggestions = []
        if self.opus and hasattr(self.opus, 'client'):
            try:
                from anthropic import Anthropic
                prompt = (
                    f"Given these underperforming holdings: {underperformers}, "
                    f"suggest replacement tickers. Respond ONLY with JSON: "
                    f'{{"rotations": [{{"sell": "SYM", "buy": "SYM", "reason": "..."}}]}}'
                )
                resp = self.opus.client.messages.create(
                    model='claude-sonnet-4-20250514', max_tokens=500,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                import json
                data = json.loads(resp.content[0].text)
                rotation_suggestions = data.get('rotations', [])
            except Exception as e:
                logger.error(f"Opus rotation advice failed: {e}")

        # Fallback: suggest selling underperformers without replacements
        if not rotation_suggestions:
            rotation_suggestions = [
                {'sell': u['symbol'], 'buy': None, 'reason': f"Down {u['pnl_pct']:.1%}"}
                for u in underperformers
            ]

        return {
            'status': 'rotation_suggested',
            'underperformers': underperformers,
            'suggestions': rotation_suggestions,
        }

    def rebalance(self) -> dict:
        """Compare current allocations to target template and generate rebalance trades."""
        try:
            account = self.alpaca.get_account()
            account_value = float(account.portfolio_value)
            positions = self.alpaca.get_positions()
        except Exception as e:
            logger.error(f"Failed to get account for rebalance: {e}")
            return {'status': 'error', 'error': str(e)}

        if not positions:
            return {'status': 'no_positions'}

        # Calculate current allocation percentages
        current_alloc = {}
        for pos in positions:
            symbol = getattr(pos, 'symbol', '')
            if '/' in symbol:
                continue
            market_value = float(getattr(pos, 'market_value', 0))
            current_alloc[symbol] = market_value / account_value if account_value > 0 else 0

        # Get target from auto_diversify template
        target_info = self.auto_diversify(account_value)
        target_alloc = target_info.get('allocations', {})

        # Find symbols that need rebalancing (>2% drift)
        trades_needed = []
        all_symbols = set(list(current_alloc.keys()) + list(target_alloc.keys()))

        for symbol in all_symbols:
            current_pct = current_alloc.get(symbol, 0)
            target_pct = target_alloc.get(symbol, 0)
            diff = target_pct - current_pct

            if abs(diff) > 0.02:  # 2% threshold
                dollar_amount = abs(diff) * account_value
                trades_needed.append({
                    'symbol': symbol,
                    'action': 'buy' if diff > 0 else 'sell',
                    'current_pct': round(current_pct, 4),
                    'target_pct': round(target_pct, 4),
                    'diff_pct': round(diff, 4),
                    'dollar_amount': round(dollar_amount, 2),
                })

        if not trades_needed:
            return {'status': 'balanced', 'holdings': len(current_alloc)}

        return {
            'status': 'rebalance_needed',
            'trades': trades_needed,
            'current_allocations': current_alloc,
            'target_allocations': target_alloc,
        }
