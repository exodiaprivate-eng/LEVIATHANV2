"""Options exit management - DTE, profit targets, theta decay."""
import logging
from datetime import datetime

logger = logging.getLogger('leviathan.options_exits')


class OptionsExitManager:
    """Manage exits for options positions with expiration awareness."""

    def __init__(self, alpaca_client, profit_target_pct=0.50,
                 stop_loss_mult=2.0, min_dte=7, theta_threshold=0.70):
        self.alpaca = alpaca_client
        self.profit_target = profit_target_pct
        self.stop_loss_mult = stop_loss_mult
        self.min_dte = min_dte
        self.theta_threshold = theta_threshold

    def check_all_options(self) -> list:
        exits = []
        # Options positions would be fetched here
        return exits

    def evaluate_position(self, position: dict) -> dict:
        current_value = float(position.get('market_value', 0))
        cost_basis = float(position.get('cost_basis', 0))
        expiration = position.get('expiration_date')

        if cost_basis < 0:  # Credit
            credit = abs(cost_basis)
            cost_to_close = abs(current_value)
            pnl = credit - cost_to_close
            pnl_pct = pnl / credit if credit > 0 else 0
        else:  # Debit
            pnl = current_value - cost_basis
            pnl_pct = pnl / cost_basis if cost_basis > 0 else 0

        dte = 999
        if expiration:
            try:
                dte = (datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days
            except ValueError:
                pass

        symbol = position.get('symbol', '')

        # Profit target
        if pnl_pct >= self.profit_target:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'PROFIT_TARGET',
                    'pnl': pnl, 'dte': dte}
        # Stop loss
        if cost_basis < 0 and abs(pnl) > abs(cost_basis) * self.stop_loss_mult:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'STOP_LOSS',
                    'pnl': pnl, 'dte': dte}
        if cost_basis > 0 and pnl_pct <= -0.50:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'STOP_LOSS',
                    'pnl': pnl, 'dte': dte}
        # DTE
        if dte <= self.min_dte:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'EXPIRATION_APPROACHING',
                    'pnl': pnl, 'dte': dte}
        # Theta captured
        original_dte = position.get('original_dte', 45)
        elapsed = 1 - (dte / original_dte) if original_dte > 0 else 0
        if elapsed >= self.theta_threshold and pnl > 0:
            return {'symbol': symbol, 'should_exit': True, 'reason': 'THETA_CAPTURED',
                    'pnl': pnl, 'dte': dte}

        return {'symbol': symbol, 'should_exit': False, 'pnl': pnl, 'dte': dte}
