"""Fill processing - update positions and P&L on order fills."""
import logging
from datetime import datetime

logger = logging.getLogger('leviathan.fills')


class FillHandler:
    """Process order fills and update state."""

    def __init__(self, state_db, learning_db):
        self.state_db = state_db
        self.learning_db = learning_db

    def process_fill(self, order, fill_price: float):
        symbol = order.get('symbol', '')
        side = order.get('side', '')
        qty = float(order.get('qty', 0))

        if side == 'buy':
            self.state_db.save_position(symbol, qty, fill_price)
            logger.info(f"Position opened: {symbol} {qty} @ {fill_price}")
        elif side == 'sell':
            trade_info = self.state_db.get_trade_info(symbol)
            if trade_info:
                pnl = (fill_price - trade_info['avg_entry_price']) * qty
                self.state_db.log_exit(symbol, 'filled', fill_price, datetime.now())
                logger.info(f"Position closed: {symbol} PnL=${pnl:.2f}")
                return pnl
        return 0.0

    def calculate_realized_pnl(self, entry_price: float, exit_price: float,
                                qty: float, side: str) -> float:
        if side == 'buy':
            return (exit_price - entry_price) * qty
        return (entry_price - exit_price) * qty
