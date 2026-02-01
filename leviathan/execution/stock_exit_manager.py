"""Stock exit management - stop loss, trailing stop, take profit, time stop."""
import logging
from datetime import datetime

logger = logging.getLogger('leviathan.exits')


class StockExitManager:
    """Manage exits for stock positions using multiple exit rules."""

    def __init__(self, alpaca_client, state_db, default_tp_pct=0.05,
                 default_sl_pct=0.03, default_time_days=5, trailing_pct=0.02):
        self.alpaca = alpaca_client
        self.db = state_db
        self.default_tp = default_tp_pct
        self.default_sl = default_sl_pct
        self.default_time = default_time_days
        self.trailing_pct = trailing_pct

    def check_all_positions(self) -> list:
        exits = []
        try:
            positions = self.alpaca.get_positions()
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
        for pos in positions:
            if '/' in pos.symbol:
                continue
            result = self._evaluate(pos)
            if result.get('should_exit'):
                exits.append(result)
        return exits

    def _evaluate(self, pos) -> dict:
        symbol = pos.symbol
        entry = float(pos.avg_entry_price)
        current = float(pos.current_price)
        pnl_pct = float(pos.unrealized_plpc)
        info = self.db.get_trade_info(symbol)
        sl = info.get('stop_loss_price', entry * (1 - self.default_sl))
        tp = info.get('take_profit_price', entry * (1 + self.default_tp))
        highest = info.get('highest_price_since_entry', current)
        entry_time = info.get('entry_time')
        days_held = (datetime.now() - entry_time).days if entry_time else 0
        time_stop = info.get('time_stop_days', self.default_time)

        if current > highest:
            highest = current
            self.db.update_highest_price(symbol, highest)

        # 1. Stop loss
        if current <= sl:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'STOP_LOSS',
                    'order_type': 'market', 'details': f'Price {current:.2f} <= SL {sl:.2f}'}
        # 2. Trailing stop
        trail = highest * (1 - self.trailing_pct)
        if current <= trail and pnl_pct > 0.02:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'TRAILING_STOP',
                    'order_type': 'market', 'details': f'Trailing from {highest:.2f}'}
        # 3. Take profit
        if current >= tp:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'TAKE_PROFIT',
                    'order_type': 'limit', 'details': f'Target {tp:.2f} reached'}
        # 4. Time stop
        if days_held >= time_stop:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'TIME_STOP',
                    'order_type': 'limit', 'details': f'Held {days_held} days'}
        return {'symbol': symbol, 'should_exit': False, 'days_held': days_held, 'pnl_pct': pnl_pct}

    def execute_exit(self, exit_signal: dict):
        symbol = exit_signal['symbol']
        try:
            pos = self.alpaca.get_position(symbol)
            qty = float(pos.qty)
            if exit_signal.get('order_type') == 'market':
                order = self.alpaca.submit_market_order(symbol, qty, 'sell')
            else:
                price = float(pos.current_price) * 0.999
                order = self.alpaca.submit_limit_order(symbol, qty, 'sell', price)
            self.db.log_exit(symbol, exit_signal['reason'], float(pos.current_price), datetime.now())
            logger.info(f"Exit executed: {symbol} reason={exit_signal['reason']}")
            return {'status': 'submitted', 'order_id': str(order.id)}
        except Exception as e:
            logger.error(f"Exit failed for {symbol}: {e}")
            return {'status': 'failed', 'error': str(e)}
