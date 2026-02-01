"""Order submission wrapper with error handling and retry logic."""
import logging
import time

logger = logging.getLogger('leviathan.adapter')


class AlpacaAdapter:
    """High-level order management wrapping AlpacaClient."""

    def __init__(self, alpaca_client):
        self.client = alpaca_client
        self.max_retries = 3

    def _retry(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def submit_market_order(self, symbol, qty, side):
        return self._retry(self.client.submit_market_order, symbol, qty, side)

    def submit_limit_order(self, symbol, qty, side, limit_price):
        return self._retry(self.client.submit_limit_order, symbol, qty, side, limit_price)

    def submit_bracket_order(self, symbol, qty, side, take_profit, stop_loss):
        return self._retry(self.client.submit_bracket_order, symbol, qty, side, take_profit, stop_loss)

    def cancel_order(self, order_id):
        return self._retry(self.client.cancel_order, order_id)

    def cancel_all_orders(self):
        return self._retry(self.client.cancel_all_orders)

    def submit_limit_bracket_order(self, symbol, qty, side, limit_price,
                                    stop_loss_price, take_profit_price):
        """
        Submit a limit entry order with bracket (stop loss + take profit).

        Uses Alpaca's bracket order class with limit entry.
        """
        logger.info(
            "Limit bracket: %s %s x%d limit=$%.2f SL=$%.2f TP=$%.2f",
            side, symbol, qty, limit_price, stop_loss_price, take_profit_price
        )
        return self._retry(
            self.client.submit_bracket_order,
            symbol, qty, side, take_profit_price, stop_loss_price,
            limit_price=limit_price,
        )

    def get_order_status(self, order_id):
        orders = self.client.get_orders('all')
        for o in orders:
            if str(o.id) == str(order_id):
                return o
        return None
