"""Order state tracking and management."""
import logging
from datetime import datetime

logger = logging.getLogger('leviathan.orders')


class OrderManager:
    """Track and manage order lifecycle."""

    def __init__(self, state_db):
        self.db = state_db
        self.active_orders = {}

    def track_order(self, order):
        order_data = {
            'order_id': str(order.id), 'symbol': order.symbol,
            'side': str(order.side), 'qty': float(order.qty or 0),
            'order_type': str(order.order_type), 'status': str(order.status),
        }
        self.db.save_order(order_data)
        self.active_orders[str(order.id)] = order_data

    def update_order_status(self, order_id: str, status: str, filled_price: float = None):
        if order_id in self.active_orders:
            self.active_orders[order_id]['status'] = status
            if filled_price:
                self.active_orders[order_id]['filled_price'] = filled_price
        self.db.save_order({
            'order_id': order_id, 'status': status,
            **self.active_orders.get(order_id, {}),
        })

    def get_pending_orders(self) -> list:
        return [o for o in self.active_orders.values() if o['status'] in ('pending', 'submitted', 'new')]

    def get_filled_orders(self) -> list:
        return [o for o in self.active_orders.values() if o['status'] == 'filled']

    def sync_with_alpaca(self, alpaca_client):
        orders = alpaca_client.get_orders('open')
        for order in orders:
            self.track_order(order)
