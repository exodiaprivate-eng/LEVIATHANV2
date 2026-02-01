"""Autonomous trade execution - executes Opus decisions without human intervention."""
import logging
from datetime import datetime

logger = logging.getLogger('leviathan.executor')


class AutonomousExecutor:
    """Execute Opus trading decisions autonomously."""

    def __init__(self, alpaca_client, opus_brain, risk_manager, learning_db):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        self.risk = risk_manager
        self.db = learning_db
        self.is_running = False

    def submit_limit_bracket_order(self, symbol: str, qty: float, limit_price: float,
                                   stop_loss: float, take_profit: float,
                                   side: str = 'buy') -> object:
        """Submit a limit order with bracket (stop-loss and take-profit) using Alpaca OTO/OCO.

        This creates a primary limit order with attached stop-loss and take-profit legs.
        """
        from alpaca.trading.requests import (
            LimitOrderRequest, TakeProfitRequest, StopLossRequest
        )
        from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL

        request = LimitOrderRequest(
            symbol=symbol,
            qty=round(qty, 4),
            side=order_side,
            time_in_force=TimeInForce.GTC,
            limit_price=round(limit_price, 2),
            order_class=OrderClass.BRACKET,
            take_profit=TakeProfitRequest(limit_price=round(take_profit, 2)),
            stop_loss=StopLossRequest(stop_price=round(stop_loss, 2)),
        )

        order = self.alpaca.api.submit_order(request)
        logger.info(
            f"LIMIT BRACKET: {side} {qty:.4f} {symbol} limit={limit_price:.2f} "
            f"SL={stop_loss:.2f} TP={take_profit:.2f} order_id={order.id}"
        )
        return order

    def execute_decision(self, decision: dict, symbol: str) -> dict:
        if decision.get('action') == 'REJECT':
            return {'status': 'rejected', 'reason': decision.get('reasoning', '')}
        if decision.get('action') not in ('EXECUTE', 'MODIFY'):
            return {'status': 'invalid_action', 'decision': decision}

        # Final risk check
        approved, reason = self.risk.pre_trade_check(type('Order', (), {
            'qty': decision.get('position_size_dollars', 0),
            'price': 1.0, 'symbol': symbol, 'side': decision.get('side', 'buy')
        })())
        if not approved:
            return {'status': 'risk_rejected', 'reason': reason}

        # Get current price and calculate qty
        price = self.alpaca.get_latest_price(symbol)
        if price <= 0:
            return {'status': 'error', 'reason': 'Could not get price'}
        qty = decision['position_size_dollars'] / price

        try:
            order_type = decision.get('order_type', 'market')
            stop_loss = decision.get('stop_loss_price', price * 0.97)
            take_profit = decision.get('take_profit_price', price * 1.05)

            if order_type == 'market':
                order = self.alpaca.submit_bracket_order(
                    symbol=symbol, qty=round(qty, 4), side=decision['side'],
                    take_profit=take_profit,
                    stop_loss=stop_loss)
            else:
                # Limit order with bracket (SL/TP)
                limit_price = decision.get('limit_price', price)
                order = self.submit_limit_bracket_order(
                    symbol=symbol, qty=round(qty, 4),
                    limit_price=limit_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    side=decision['side'])

            self.db.log_opus_decision(
                timestamp=datetime.now(), symbol=symbol,
                ml_signal={'confidence': decision.get('confidence', 0)},
                decision=decision)

            logger.info(f"EXECUTED: {decision['side']} {qty:.4f} {symbol} @ ~{price:.2f}")
            return {
                'status': 'executed', 'order_id': str(order.id),
                'symbol': symbol, 'qty': qty, 'side': decision['side'],
                'reasoning': decision.get('reasoning', ''),
            }
        except Exception as e:
            logger.error(f"Execution failed for {symbol}: {e}")
            return {'status': 'execution_failed', 'error': str(e)}
