"""Python API class for PyWebView JS bridge - all methods callable from JavaScript."""
import json
import logging
import threading
import time
from datetime import datetime
from typing import Optional

logger = logging.getLogger('leviathan.gui.api')


class LeviathanAPI:
    """API bridge between frontend JS and Python backend."""

    def __init__(self, trading_engine, learning_db, state_db):
        self.engine = trading_engine
        self.learning_db = learning_db
        self.state_db = state_db
        self.is_running = False
        self.trading_thread: Optional[threading.Thread] = None
        self._activity_log = []
        self._window = None  # Set by LeviathanGUI after window creation

    # ── Window Controls ──────────────────────────────────────────────
    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def maximize_window(self):
        if self._window:
            if getattr(self, '_maximized', False):
                self._window.restore()
                self._maximized = False
            else:
                self._window.maximize()
                self._maximized = True

    def close_window(self):
        if self._window:
            self._window.destroy()

    def resize_window(self, edge, dx, dy, start_w, start_h, start_left, start_top):
        """Resize the frameless window from a given edge/corner."""
        if not self._window:
            return
        min_w, min_h = 1024, 600
        x, y, w, h = int(start_left), int(start_top), int(start_w), int(start_h)
        dx, dy = int(dx), int(dy)

        if 'r' in edge:
            w = max(min_w, start_w + dx)
        if 'b' in edge:
            h = max(min_h, start_h + dy)
        if 'l' in edge:
            new_w = max(min_w, start_w - dx)
            x = start_left + (start_w - new_w)
            w = new_w
        if 't' in edge:
            new_h = max(min_h, start_h - dy)
            y = start_top + (start_h - new_h)
            h = new_h

        self._window.move(x, y)
        self._window.resize(w, h)

    def start_trading(self) -> str:
        if self.is_running:
            return json.dumps({'status': 'already_running'})
        self.is_running = True
        self._log('SYSTEM', 'Trading started - Opus brain initializing...')
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        return json.dumps({'status': 'running'})

    def stop_trading(self) -> str:
        if not self.is_running:
            return json.dumps({'status': 'already_stopped'})
        self.is_running = False
        self._log('SYSTEM', 'Stopping trading...')
        try:
            self.engine.cancel_all_orders()
            self._log('SYSTEM', 'All open orders cancelled')
        except Exception as e:
            self._log('ERROR', f'Cancel orders failed: {e}')
        return json.dumps({'status': 'stopped'})

    def _trading_loop(self):
        self._log('OPUS', 'Opus brain active - scanning...')
        while self.is_running:
            try:
                result = self.engine.run_cycle()
                if result and result.get('trade_executed'):
                    self._log('TRADE', f"{result.get('action','')} {result.get('symbol','')} - {result.get('reason','')}")
            except Exception as e:
                self._log('ERROR', f'Cycle error: {e}')
            time.sleep(60)

    def get_dashboard_data(self) -> str:
        try:
            account = self.engine.alpaca.get_account()
            positions = self.engine.alpaca.get_positions()
            pos_data = [{
                'symbol': p.symbol, 'qty': float(p.qty),
                'entry_price': float(p.avg_entry_price),
                'current_price': float(p.current_price),
                'pnl': float(p.unrealized_pl),
                'pnl_pct': float(p.unrealized_plpc) * 100,
            } for p in positions]
            stats = self.learning_db.get_performance_stats()
            chart = self.state_db.get_portfolio_history(days=7)
            equity = float(account.equity)
            last_eq = float(account.last_equity)
            return json.dumps({
                'portfolio': {
                    'balance': equity, 'buying_power': float(account.buying_power),
                    'today_pnl': equity - last_eq,
                    'today_pnl_pct': ((equity / last_eq) - 1) * 100 if last_eq > 0 else 0,
                    'total_pnl_pct': stats.get('total_return_pct', 0),
                    'opus_decisions': stats.get('total_decisions', 0),
                    'opus_cost': stats.get('total_api_cost', 0),
                    'win_rate': stats.get('win_rate', 0),
                    'wins': stats.get('wins', 0), 'losses': stats.get('losses', 0),
                },
                'positions': pos_data, 'chart_data': chart,
                'is_running': self.is_running,
                'mode': 'PAPER' if self.engine.paper_mode else 'LIVE',
            })
        except Exception as e:
            return json.dumps({
                'error': str(e),
                'portfolio': {'balance': 0, 'buying_power': 0, 'today_pnl': 0,
                              'today_pnl_pct': 0, 'total_pnl_pct': 0, 'opus_decisions': 0,
                              'opus_cost': 0, 'win_rate': 0, 'wins': 0, 'losses': 0},
                'positions': [], 'chart_data': [],
                'is_running': self.is_running, 'mode': 'PAPER',
            })

    def get_activity_log(self) -> str:
        return json.dumps(self._activity_log[-50:])

    def open_settings(self):
        self._log('SYSTEM', 'Settings opened')
        return json.dumps({'status': 'opened'})

    def open_crypto_swap(self):
        self._log('SYSTEM', 'Crypto swap opened')
        return json.dumps({'status': 'opened'})

    def open_autopilot(self):
        self._log('SYSTEM', 'Autopilot opened')
        return json.dumps({'status': 'opened'})

    def open_training(self):
        self._log('SYSTEM', 'Training opened')
        return json.dumps({'status': 'opened'})

    # ── Additional API methods ──────────────────────────────────────────

    def save_settings(self, settings_json: str) -> str:
        """Save user settings to the config / state store."""
        try:
            settings = json.loads(settings_json) if isinstance(settings_json, str) else settings_json
            self.state_db.save_settings(settings)
            self._log('SYSTEM', 'Settings saved')
            return json.dumps({'status': 'ok'})
        except Exception as e:
            self._log('ERROR', f'Failed to save settings: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def start_manual_training(self, params_json: str) -> str:
        """Trigger the training pipeline with the given parameters."""
        try:
            params = json.loads(params_json) if isinstance(params_json, str) else params_json
            self._log('TRAINING', f"Manual training started: {params.get('name', 'unnamed')}")
            thread = threading.Thread(
                target=self._run_training, args=(params,), daemon=True
            )
            thread.start()
            return json.dumps({'status': 'training_started'})
        except Exception as e:
            self._log('ERROR', f'Training launch failed: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def _run_training(self, params: dict):
        """Background worker for the training pipeline."""
        try:
            result = self.engine.run_training(params)
            self._log('TRAINING', f"Training complete: {result}")
        except Exception as e:
            self._log('ERROR', f'Training error: {e}')

    def find_swap_path(self, from_coin: str, to_coin: str, amount: float) -> str:
        """Find the optimal swap path between two crypto assets."""
        try:
            path = self.engine.find_swap_path(from_coin, to_coin, float(amount))
            self._log('SWAP', f'Path found: {from_coin} -> {to_coin} ({amount})')
            return json.dumps({'status': 'ok', 'path': path})
        except Exception as e:
            self._log('ERROR', f'Swap path error: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def execute_swap(self, path_json: str) -> str:
        """Execute a previously computed swap path."""
        try:
            path = json.loads(path_json) if isinstance(path_json, str) else path_json
            result = self.engine.execute_swap(path)
            self._log('SWAP', f"Swap executed: {result.get('summary', '')}")
            return json.dumps({'status': 'ok', 'result': result})
        except Exception as e:
            self._log('ERROR', f'Swap execution failed: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def get_analytics_data(self) -> str:
        """Return analytics metrics for the analytics page."""
        try:
            stats = self.learning_db.get_performance_stats()
            equity_curve = self.state_db.get_portfolio_history(days=30)
            trade_history = self.learning_db.get_trade_history(limit=100)
            return json.dumps({
                'win_rate': stats.get('win_rate', 0),
                'total_trades': stats.get('total_trades', 0),
                'total_pnl': stats.get('total_pnl', 0),
                'sharpe_ratio': stats.get('sharpe_ratio', 0),
                'max_drawdown': stats.get('max_drawdown', 0),
                'avg_win': stats.get('avg_win', 0),
                'avg_loss': stats.get('avg_loss', 0),
                'equity_curve': equity_curve,
                'trade_history': trade_history,
            })
        except Exception as e:
            self._log('ERROR', f'Analytics data error: {e}')
            return json.dumps({
                'win_rate': 0, 'total_trades': 0, 'total_pnl': 0,
                'sharpe_ratio': 0, 'max_drawdown': 0, 'avg_win': 0,
                'avg_loss': 0, 'equity_curve': [], 'trade_history': [],
                'error': str(e),
            })

    # ── Crypto Trading ──────────────────────────────────────────────

    def get_crypto_holdings(self) -> str:
        """Get current crypto portfolio holdings."""
        try:
            positions = self.engine.alpaca.get_positions()
            holdings = []
            total_value = 0
            for p in positions:
                if '/' in p.symbol:
                    val = float(p.market_value)
                    total_value += val
                    holdings.append({
                        'symbol': p.symbol.split('/')[0],
                        'pair': p.symbol,
                        'qty': float(p.qty),
                        'value': val,
                        'avg_entry': float(p.avg_entry_price),
                        'current_price': float(p.current_price),
                        'pnl': float(p.unrealized_pl),
                        'pnl_pct': float(p.unrealized_plpc) * 100,
                    })
            # Calculate allocation percentages
            for h in holdings:
                h['allocation'] = (h['value'] / total_value * 100) if total_value > 0 else 0
            return json.dumps({
                'holdings': holdings,
                'total_value': total_value,
                'count': len(holdings),
            })
        except Exception as e:
            return json.dumps({'holdings': [], 'total_value': 0, 'count': 0, 'error': str(e)})

    def get_crypto_opportunities(self) -> str:
        """Scan cryptos for AI trading signals."""
        try:
            from leviathan.crypto.crypto_trader import CryptoTrader
            trader = CryptoTrader(self.engine.alpaca)
            opps = trader.get_crypto_opportunities()
            return json.dumps({'opportunities': opps, 'count': len(opps)})
        except Exception as e:
            self._log('ERROR', f'Crypto scan failed: {e}')
            return json.dumps({'opportunities': [], 'count': 0, 'error': str(e)})

    def start_crypto_trading(self) -> str:
        """Start 24/7 AI crypto trading loop."""
        if getattr(self, '_crypto_running', False):
            return json.dumps({'status': 'already_running'})
        self._crypto_running = True
        self._log('CRYPTO', 'Crypto AI trading started - 24/7 mode')
        import threading
        self._crypto_thread = threading.Thread(target=self._crypto_trading_loop, daemon=True)
        self._crypto_thread.start()
        return json.dumps({'status': 'running'})

    def stop_crypto_trading(self) -> str:
        """Stop crypto trading loop."""
        self._crypto_running = False
        self._log('CRYPTO', 'Crypto AI trading stopped')
        return json.dumps({'status': 'stopped'})

    def _crypto_trading_loop(self):
        """Background 24/7 crypto trading loop."""
        from leviathan.crypto.crypto_trader import CryptoTrader
        from leviathan.crypto.crypto_strategies import CryptoStrategy
        trader = CryptoTrader(self.engine.alpaca, getattr(self.engine, 'opus_brain', None))
        strategy = CryptoStrategy()
        while getattr(self, '_crypto_running', False):
            try:
                opps = trader.get_crypto_opportunities()
                for opp in opps[:3]:  # Top 3 opportunities
                    self._log('CRYPTO', f"Signal: {opp['symbol']} {opp['direction']} "
                              f"(strength: {opp['strength']:.2f}, RSI: {opp['rsi']:.1f})")
                    if opp['strength'] >= 0.8 and opp['direction'] == 'long':
                        # Execute buy if strong enough
                        try:
                            trader.buy_crypto(opp['symbol'], notional=50)
                            self._log('TRADE', f"Bought ${50} of {opp['symbol']}")
                        except Exception as e:
                            self._log('ERROR', f"Crypto buy failed: {e}")
            except Exception as e:
                self._log('ERROR', f'Crypto cycle error: {e}')
            time.sleep(300)  # Every 5 minutes

    def rebalance_crypto(self, allocations_json: str) -> str:
        """Rebalance crypto portfolio to target allocations."""
        try:
            from leviathan.crypto.swap_optimizer import CryptoSwapOptimizer
            from leviathan.crypto.portfolio_rebalancer import CryptoPortfolioManager
            allocations = json.loads(allocations_json) if isinstance(allocations_json, str) else allocations_json
            optimizer = CryptoSwapOptimizer(self.engine.alpaca)
            manager = CryptoPortfolioManager(self.engine.alpaca, optimizer)
            result = manager.rebalance_portfolio(allocations, execute=True)
            self._log('CRYPTO', f"Rebalance complete: {len(result.get('executed', []))} trades")
            return json.dumps(result)
        except Exception as e:
            self._log('ERROR', f'Rebalance failed: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def buy_crypto(self, symbol: str, notional: float) -> str:
        """Buy crypto with notional USD amount."""
        try:
            from leviathan.crypto.crypto_trader import CryptoTrader
            trader = CryptoTrader(self.engine.alpaca)
            result = trader.buy_crypto(f"{symbol}/USD", float(notional))
            self._log('TRADE', f"Bought ${notional} of {symbol}")
            return json.dumps({'status': 'ok', 'order_id': str(result.id) if result else None})
        except Exception as e:
            self._log('ERROR', f'Crypto buy failed: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def sell_crypto(self, symbol: str, qty: float) -> str:
        """Sell a quantity of crypto."""
        try:
            from leviathan.crypto.crypto_trader import CryptoTrader
            trader = CryptoTrader(self.engine.alpaca)
            result = trader.sell_crypto(f"{symbol}/USD", float(qty))
            self._log('TRADE', f"Sold {qty} of {symbol}")
            return json.dumps({'status': 'ok', 'order_id': str(result.id) if result else None})
        except Exception as e:
            self._log('ERROR', f'Crypto sell failed: {e}')
            return json.dumps({'status': 'error', 'message': str(e)})

    def _log(self, activity_type: str, message: str):
        self._activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': activity_type, 'message': message,
        })
        if len(self._activity_log) > 100:
            self._activity_log = self._activity_log[-100:]
