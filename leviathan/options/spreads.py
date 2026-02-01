"""Options spread construction - verticals, iron condors, P&L calculations."""
import logging
from typing import Optional

logger = logging.getLogger('leviathan.spreads')


class SpreadBuilder:
    """Build and evaluate multi-leg options strategies."""

    # ------------------------------------------------------------------
    # Vertical spreads
    # ------------------------------------------------------------------
    def build_vertical_spread(self, chain: dict, direction: str = 'bullish',
                              spread_type: str = 'debit',
                              width: float = 5.0,
                              target_delta: float = 0.40) -> dict:
        """Construct a vertical spread (2 legs, same expiration).

        Args:
            chain: Options chain dict from OptionsTrader.get_options_chain().
            direction: 'bullish' or 'bearish'.
            spread_type: 'debit' or 'credit'.
            width: Distance between strikes in dollars.
            target_delta: Target delta for the anchor leg.

        Returns:
            Spread dict with legs, greeks, max profit/loss, breakeven.
        """
        if direction == 'bullish':
            if spread_type == 'debit':
                return self._bull_call_spread(chain, width, target_delta)
            else:
                return self._bull_put_spread(chain, width, target_delta)
        else:
            if spread_type == 'debit':
                return self._bear_put_spread(chain, width, target_delta)
            else:
                return self._bear_call_spread(chain, width, target_delta)

    def _bull_call_spread(self, chain: dict, width: float,
                          target_delta: float) -> dict:
        """Buy lower strike call, sell higher strike call."""
        calls = chain.get('calls', [])
        if len(calls) < 2:
            return self._empty_spread('bull_call_spread', 'Not enough calls')

        long_leg = self._find_by_delta(calls, target_delta)
        short_leg = self._find_by_strike(calls, long_leg['strike'] + width)
        if not short_leg:
            short_leg = self._nearest_strike(calls, long_leg['strike'] + width)

        actual_width = short_leg['strike'] - long_leg['strike']
        net_debit = long_leg['mid'] - short_leg['mid']

        return self._build_spread_result(
            name='bull_call_spread',
            spread_type='debit',
            direction='bullish',
            long_leg=long_leg,
            short_leg=short_leg,
            width=actual_width,
            net_premium=net_debit,
        )

    def _bull_put_spread(self, chain: dict, width: float,
                         target_delta: float) -> dict:
        """Sell higher strike put, buy lower strike put (credit)."""
        puts = chain.get('puts', [])
        if len(puts) < 2:
            return self._empty_spread('bull_put_spread', 'Not enough puts')

        short_leg = self._find_by_delta(puts, -target_delta)
        long_leg = self._find_by_strike(puts, short_leg['strike'] - width)
        if not long_leg:
            long_leg = self._nearest_strike(puts, short_leg['strike'] - width)

        actual_width = short_leg['strike'] - long_leg['strike']
        net_credit = short_leg['mid'] - long_leg['mid']

        return self._build_spread_result(
            name='bull_put_spread',
            spread_type='credit',
            direction='bullish',
            long_leg=long_leg,
            short_leg=short_leg,
            width=actual_width,
            net_premium=net_credit,
        )

    def _bear_put_spread(self, chain: dict, width: float,
                         target_delta: float) -> dict:
        """Buy higher strike put, sell lower strike put (debit)."""
        puts = chain.get('puts', [])
        if len(puts) < 2:
            return self._empty_spread('bear_put_spread', 'Not enough puts')

        long_leg = self._find_by_delta(puts, -target_delta)
        short_leg = self._find_by_strike(puts, long_leg['strike'] - width)
        if not short_leg:
            short_leg = self._nearest_strike(puts, long_leg['strike'] - width)

        actual_width = long_leg['strike'] - short_leg['strike']
        net_debit = long_leg['mid'] - short_leg['mid']

        return self._build_spread_result(
            name='bear_put_spread',
            spread_type='debit',
            direction='bearish',
            long_leg=long_leg,
            short_leg=short_leg,
            width=actual_width,
            net_premium=net_debit,
        )

    def _bear_call_spread(self, chain: dict, width: float,
                          target_delta: float) -> dict:
        """Sell lower strike call, buy higher strike call (credit)."""
        calls = chain.get('calls', [])
        if len(calls) < 2:
            return self._empty_spread('bear_call_spread', 'Not enough calls')

        short_leg = self._find_by_delta(calls, target_delta)
        long_leg = self._find_by_strike(calls, short_leg['strike'] + width)
        if not long_leg:
            long_leg = self._nearest_strike(calls, short_leg['strike'] + width)

        actual_width = long_leg['strike'] - short_leg['strike']
        net_credit = short_leg['mid'] - long_leg['mid']

        return self._build_spread_result(
            name='bear_call_spread',
            spread_type='credit',
            direction='bearish',
            long_leg=long_leg,
            short_leg=short_leg,
            width=actual_width,
            net_premium=net_credit,
        )

    # ------------------------------------------------------------------
    # Iron condor
    # ------------------------------------------------------------------
    def build_iron_condor(self, chain: dict, width: float = 5.0,
                          wing_delta: float = 0.20) -> dict:
        """Build a 4-leg iron condor (sell inner strikes, buy outer wings).

        Structure:
            Buy OTM put  (lowest strike)
            Sell OTM put (higher strike)  -- put credit spread
            Sell OTM call (lower strike)  -- call credit spread
            Buy OTM call (highest strike)

        Args:
            chain: Options chain dict.
            width: Width of each vertical in dollars.
            wing_delta: Target delta for the short strikes.
        """
        puts = chain.get('puts', [])
        calls = chain.get('calls', [])
        if len(puts) < 2 or len(calls) < 2:
            return self._empty_spread('iron_condor', 'Insufficient contracts')

        # Put side (bull put spread)
        short_put = self._find_by_delta(puts, -wing_delta)
        long_put = self._find_by_strike(puts, short_put['strike'] - width)
        if not long_put:
            long_put = self._nearest_strike(puts, short_put['strike'] - width)

        # Call side (bear call spread)
        short_call = self._find_by_delta(calls, wing_delta)
        long_call = self._find_by_strike(calls, short_call['strike'] + width)
        if not long_call:
            long_call = self._nearest_strike(calls, short_call['strike'] + width)

        put_width = short_put['strike'] - long_put['strike']
        call_width = long_call['strike'] - short_call['strike']

        put_credit = short_put['mid'] - long_put['mid']
        call_credit = short_call['mid'] - long_call['mid']
        total_credit = put_credit + call_credit

        max_loss_put = (put_width - put_credit) * 100
        max_loss_call = (call_width - call_credit) * 100
        max_loss = max(max_loss_put, max_loss_call)

        return {
            'name': 'iron_condor',
            'spread_type': 'credit',
            'direction': 'neutral',
            'legs': [
                {'role': 'long_put', 'side': 'buy', **long_put},
                {'role': 'short_put', 'side': 'sell', **short_put},
                {'role': 'short_call', 'side': 'sell', **short_call},
                {'role': 'long_call', 'side': 'buy', **long_call},
            ],
            'net_credit': round(total_credit, 2),
            'max_profit': round(total_credit * 100, 2),
            'max_loss': round(max_loss, 2),
            'breakeven_lower': round(short_put['strike'] - total_credit, 2),
            'breakeven_upper': round(short_call['strike'] + total_credit, 2),
            'put_width': put_width,
            'call_width': call_width,
            'margin_requirement': round(max(put_width, call_width) * 100, 2),
            'risk_reward': (round(total_credit * 100 / max_loss, 2)
                            if max_loss > 0 else 0),
            'valid': True,
        }

    # ------------------------------------------------------------------
    # P&L calculations
    # ------------------------------------------------------------------
    def calculate_max_profit(self, spread: dict) -> float:
        """Max profit for a spread in dollars (per 1 contract / 100 shares)."""
        if not spread.get('valid'):
            return 0.0
        if 'max_profit' in spread:
            return spread['max_profit']

        if spread['spread_type'] == 'credit':
            return round(spread['net_credit'] * 100, 2)
        else:
            # Debit spread: width - debit paid
            return round((spread['width'] - spread['net_debit']) * 100, 2)

    def calculate_max_loss(self, spread: dict) -> float:
        """Max loss for a spread in dollars (per 1 contract / 100 shares)."""
        if not spread.get('valid'):
            return 0.0
        if 'max_loss' in spread:
            return spread['max_loss']

        if spread['spread_type'] == 'credit':
            return round((spread['width'] - spread['net_credit']) * 100, 2)
        else:
            return round(spread['net_debit'] * 100, 2)

    def calculate_margin_requirement(self, spread: dict) -> float:
        """Margin / buying power required for the spread.

        Credit spreads: width * 100 (per contract)
        Debit spreads:  net debit * 100 (cost is the margin)
        Iron condors:   max of put/call wing width * 100
        """
        if not spread.get('valid'):
            return 0.0
        if 'margin_requirement' in spread:
            return spread['margin_requirement']

        if spread['spread_type'] == 'credit':
            return round(spread['width'] * 100, 2)
        else:
            return round(spread.get('net_debit', 0) * 100, 2)

    def calculate_breakeven(self, spread: dict) -> list:
        """Return breakeven price(s) for a spread."""
        if not spread.get('valid'):
            return []
        if 'breakeven_lower' in spread and 'breakeven_upper' in spread:
            return [spread['breakeven_lower'], spread['breakeven_upper']]
        if 'breakeven' in spread:
            return [spread['breakeven']]
        return []

    def calculate_risk_reward(self, spread: dict) -> float:
        """Risk/reward ratio (max_profit / max_loss)."""
        profit = self.calculate_max_profit(spread)
        loss = self.calculate_max_loss(spread)
        if loss == 0:
            return 0.0
        return round(profit / loss, 2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_spread_result(self, name: str, spread_type: str,
                             direction: str, long_leg: dict,
                             short_leg: dict, width: float,
                             net_premium: float) -> dict:
        """Assemble a standard vertical spread result dict."""
        net_premium = round(max(net_premium, 0), 2)

        if spread_type == 'credit':
            max_profit = round(net_premium * 100, 2)
            max_loss = round((width - net_premium) * 100, 2)
            if direction == 'bullish':
                breakeven = round(short_leg['strike'] - net_premium, 2)
            else:
                breakeven = round(short_leg['strike'] + net_premium, 2)
        else:
            max_profit = round((width - net_premium) * 100, 2)
            max_loss = round(net_premium * 100, 2)
            if direction == 'bullish':
                breakeven = round(long_leg['strike'] + net_premium, 2)
            else:
                breakeven = round(long_leg['strike'] - net_premium, 2)

        return {
            'name': name,
            'spread_type': spread_type,
            'direction': direction,
            'legs': [
                {'role': 'long', 'side': 'buy', **long_leg},
                {'role': 'short', 'side': 'sell', **short_leg},
            ],
            'width': width,
            'net_credit' if spread_type == 'credit' else 'net_debit': net_premium,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'breakeven': breakeven,
            'margin_requirement': round(width * 100, 2) if spread_type == 'credit'
                                  else round(net_premium * 100, 2),
            'risk_reward': round(max_profit / max_loss, 2) if max_loss > 0 else 0,
            'valid': True,
        }

    @staticmethod
    def _empty_spread(name: str, reason: str) -> dict:
        return {'name': name, 'valid': False, 'reason': reason, 'legs': []}

    @staticmethod
    def _find_by_delta(contracts: list, target_delta: float) -> dict:
        """Find the contract closest to *target_delta*."""
        if not contracts:
            return contracts[0] if contracts else {}
        best = min(contracts, key=lambda c: abs(c.get('delta', 0) - target_delta))
        # If all deltas are zero (missing data), fall back to mid-list
        if best.get('delta', 0) == 0 and target_delta != 0:
            idx = len(contracts) // 2
            if target_delta > 0:
                idx = len(contracts) // 3          # slightly ITM for calls
            else:
                idx = 2 * len(contracts) // 3      # slightly ITM for puts
            best = contracts[min(idx, len(contracts) - 1)]
        return best

    @staticmethod
    def _find_by_strike(contracts: list, target_strike: float) -> Optional[dict]:
        """Find exact strike match."""
        for c in contracts:
            if c['strike'] == target_strike:
                return c
        return None

    @staticmethod
    def _nearest_strike(contracts: list, target_strike: float) -> dict:
        """Find the nearest strike."""
        return min(contracts, key=lambda c: abs(c['strike'] - target_strike))
