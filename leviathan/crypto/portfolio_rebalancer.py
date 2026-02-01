"""Crypto portfolio rebalancing with swap execution."""
import logging

logger = logging.getLogger('leviathan.crypto_rebalance')


class CryptoPortfolioManager:
    """Manage multi-crypto holdings with rebalancing via swap optimizer."""

    def __init__(self, alpaca_client, swap_optimizer):
        self.alpaca = alpaca_client
        self.optimizer = swap_optimizer

    def get_holdings(self) -> dict:
        """Get current crypto positions with values."""
        positions = self.alpaca.get_positions()
        holdings = {}
        for p in positions:
            if '/' in p.symbol:
                holdings[p.symbol.split('/')[0]] = {
                    'qty': float(p.qty),
                    'value': float(p.market_value),
                    'avg_entry': float(p.avg_entry_price),
                    'current_price': float(p.current_price),
                    'pnl': float(p.unrealized_pl),
                    'pnl_pct': float(p.unrealized_plpc) * 100,
                }
        return holdings

    def rebalance_portfolio(self, target_allocations: dict, execute: bool = True) -> dict:
        """
        Rebalance crypto portfolio to target allocations.

        Args:
            target_allocations: {'BTC': 0.5, 'ETH': 0.3, 'SOL': 0.2}
            execute: If True, execute trades via swap optimizer
        """
        holdings = self.get_holdings()
        total = sum(h['value'] for h in holdings.values())
        if total <= 0:
            return {'status': 'empty_portfolio'}

        trades = []
        for crypto, target_pct in target_allocations.items():
            current_val = holdings.get(crypto, {}).get('value', 0)
            target_val = total * target_pct
            diff = target_val - current_val
            if abs(diff) > 5:  # Min $5 trade
                trades.append({
                    'crypto': crypto,
                    'diff': diff,
                    'direction': 'buy' if diff > 0 else 'sell',
                    'amount_usd': abs(diff),
                })

        result = {'trades_planned': trades, 'total_value': total, 'executed': []}

        if not execute or not trades:
            return result

        # Sell overweight first, then buy underweight
        sells = [t for t in trades if t['direction'] == 'sell']
        buys = [t for t in trades if t['direction'] == 'buy']

        for trade in sells + buys:
            try:
                crypto = trade['crypto']
                amount = trade['amount_usd']

                if trade['direction'] == 'sell':
                    path = self.optimizer.find_optimal_path(
                        from_crypto=crypto, to_crypto='USD', amount=amount
                    )
                else:
                    path = self.optimizer.find_optimal_path(
                        from_crypto='USD', to_crypto=crypto, amount=amount
                    )

                if path and not path.get('error'):
                    swap_result = self.optimizer.execute_swap(
                        from_crypto=crypto if trade['direction'] == 'sell' else 'USD',
                        to_crypto='USD' if trade['direction'] == 'sell' else crypto,
                        amount=amount,
                    )
                    trade['executed'] = True
                    trade['swap_result'] = swap_result
                    result['executed'].append(trade)
                    logger.info(
                        "Rebalance %s %s: $%.2f",
                        trade['direction'], crypto, amount,
                    )
                else:
                    trade['executed'] = False
                    trade['error'] = path.get('error', 'No swap path found')
                    logger.warning("No swap path for %s %s", trade['direction'], crypto)

            except Exception as e:
                trade['executed'] = False
                trade['error'] = str(e)
                logger.error("Rebalance trade failed for %s: %s", crypto, e)

        result['status'] = 'complete'
        return result

    def auto_optimize(self):
        """Default rebalancing with preset allocation."""
        return self.rebalance_portfolio(
            {'BTC': 0.4, 'ETH': 0.3, 'SOL': 0.15, 'LINK': 0.15}
        )
