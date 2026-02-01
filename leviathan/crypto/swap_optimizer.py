"""Multi-hop crypto swap path finder using BFS."""
import logging
from collections import deque

logger = logging.getLogger('leviathan.swap')


class CryptoSwapOptimizer:
    """Find optimal path to swap between any two cryptocurrencies."""

    # All Alpaca-supported trading pairs (updated to match current Alpaca offering)
    TRADING_PAIRS = {
        # USD pairs - all supported cryptos
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD', 'LTC/USD',
        'BCH/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD', 'AVAX/USD', 'DOT/USD',
        'SHIB/USD', 'PEPE/USD', 'XTZ/USD', 'BAT/USD', 'CRV/USD', 'GRT/USD',
        'SUSHI/USD', 'YFI/USD', 'SKY/USD', 'TRUMP/USD',
        'USDC/USD', 'USDT/USD', 'USDG/USD',
        # USDC pairs
        'BTC/USDC', 'ETH/USDC', 'SOL/USDC', 'AVAX/USDC', 'DOT/USDC', 'LINK/USDC',
        'UNI/USDC', 'AAVE/USDC', 'LTC/USDC', 'BCH/USDC', 'DOGE/USDC',
        'SHIB/USDC', 'XTZ/USDC', 'BAT/USDC', 'CRV/USDC', 'GRT/USDC',
        'SUSHI/USDC', 'YFI/USDC', 'SKY/USDC',
        # USDT pairs
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'LINK/USDT', 'UNI/USDT',
        'AVAX/USDT', 'DOT/USDT', 'LTC/USDT', 'BCH/USDT',
        'AAVE/USDT', 'DOGE/USDT', 'SUSHI/USDT', 'YFI/USDT',
        # BTC pairs
        'ETH/BTC', 'BCH/BTC', 'LTC/BTC', 'UNI/BTC',
    }

    FEE_RATE = 0.0025  # 0.25%

    def __init__(self, alpaca_client):
        self.alpaca = alpaca_client
        self.graph = self._build_graph()

    def _build_graph(self) -> dict:
        graph = {}
        for pair in self.TRADING_PAIRS:
            base, quote = pair.split('/')
            graph.setdefault(base, {})[quote] = {'pair': pair, 'direction': 'sell'}
            graph.setdefault(quote, {})[base] = {'pair': pair, 'direction': 'buy'}
        return graph

    def find_optimal_path(self, from_crypto: str, to_crypto: str, amount: float) -> dict:
        f, t = from_crypto.upper(), to_crypto.upper()
        if f == t:
            return {'error': 'Same source and destination'}
        paths = self._bfs(f, t, max_hops=3)
        if not paths:
            return {'error': f'No path from {f} to {t}'}
        evaluated = [self._evaluate_path(p, amount) for p in paths]
        evaluated = [e for e in evaluated if e.get('estimated_output', 0) > 0]
        if not evaluated:
            return {'error': 'All paths failed evaluation'}
        evaluated.sort(key=lambda x: x['estimated_output'], reverse=True)
        return {
            'from': f, 'to': t, 'input_amount': amount,
            'optimal_path': evaluated[0], 'alternatives': evaluated[1:3],
        }

    def _bfs(self, start, end, max_hops=3):
        if start not in self.graph or end not in self.graph:
            return []
        paths = []
        queue = deque([(start, [start])])
        while queue:
            current, path = queue.popleft()
            if len(path) > max_hops + 1:
                continue
            if current == end and len(path) > 1:
                paths.append(path)
                continue
            for neighbor in self.graph.get(current, {}):
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))
        return paths

    def _evaluate_path(self, path, amount):
        current = amount
        total_fees = 0
        total_fees_usd = 0
        trades = []
        for i in range(len(path) - 1):
            edge = self.graph[path[i]][path[i + 1]]
            try:
                quote = self.alpaca.get_crypto_quote(edge['pair'])
                price = (quote['bid'] + quote['ask']) / 2
            except Exception:
                return {'path': path, 'estimated_output': 0}
            output = current * price if edge['direction'] == 'sell' else current / price
            fee = output * self.FEE_RATE
            output -= fee
            total_fees += fee
            trades.append({
                'pair': edge['pair'], 'direction': edge['direction'],
                'input': current, 'output': output, 'price': price, 'fee': fee,
            })
            current = output
        efficiency = (current / amount) if amount > 0 else 0
        return {
            'path': path, 'path_string': ' → '.join(path),
            'num_hops': len(path) - 1, 'trades': trades,
            'estimated_output': current, 'total_fees_usd': total_fees,
            'efficiency': efficiency,
        }

    def execute_swap(self, from_crypto, to_crypto, amount, opus_brain=None):
        result = self.find_optimal_path(from_crypto, to_crypto, amount)
        if 'error' in result:
            return result
        plan = result['optimal_path']['trades']
        current = amount
        completed = []
        for step in plan:
            try:
                side = 'sell' if step['direction'] == 'sell' else 'buy'
                order = self.alpaca.submit_crypto_order(
                    symbol=step['pair'], qty=current, side=side,
                    type='market', time_in_force='gtc')
                completed.append({'pair': step['pair'], 'order_id': str(order.id)})
                current = step['output']
            except Exception as e:
                return {'status': 'partial', 'completed': completed,
                        'error': str(e), 'remaining': current}
        return {'status': 'completed', 'steps': completed, 'output': current}
