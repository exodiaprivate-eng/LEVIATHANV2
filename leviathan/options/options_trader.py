"""Options trading module - fetches chains, analyzes Greeks, executes option orders."""
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger('leviathan.options')

# Target DTE range per project spec
MIN_DTE = 21
MAX_DTE = 45
CLOSE_BEFORE_DTE = 7


class OptionsTrader:
    """Options trading interface using Alpaca options API."""

    def __init__(self, config: dict, alpaca_adapter):
        """
        Args:
            config: Trading configuration dict (risk params, sizing, etc.)
            alpaca_adapter: AlpacaAdapter wrapping the AlpacaClient.
        """
        self.config = config
        self.adapter = alpaca_adapter
        self.client = alpaca_adapter.client  # underlying AlpacaClient
        self.trading = self.client.trading_client
        self.default_dte_min = config.get('options_dte_min', MIN_DTE)
        self.default_dte_max = config.get('options_dte_max', MAX_DTE)
        self.max_contracts = config.get('options_max_contracts', 10)

    # ------------------------------------------------------------------
    # Chain retrieval
    # ------------------------------------------------------------------
    def get_options_chain(self, symbol: str, expiration: str = None) -> dict:
        """Fetch the options chain for *symbol* via Alpaca.

        Returns a dict with keys:
            symbol, expirations, calls, puts
        Each of calls/puts is a list of contract dicts with fields:
            symbol, strike, expiration, bid, ask, mid, volume,
            open_interest, implied_volatility, delta, gamma, theta, vega, dte
        """
        self.client._rate_limit()
        try:
            from alpaca.trading.requests import GetOptionContractsRequest
            # Pick expiration window
            if expiration:
                exp_gte = expiration
                exp_lte = expiration
            else:
                today = datetime.now().date()
                exp_gte = str(today + timedelta(days=self.default_dte_min))
                exp_lte = str(today + timedelta(days=self.default_dte_max))

            request = GetOptionContractsRequest(
                underlying_symbols=[symbol],
                expiration_date_gte=exp_gte,
                expiration_date_lte=exp_lte,
                status='active',
            )
            contracts = self.trading.get_option_contracts(request)

            calls, puts = [], []
            expirations = set()
            for c in contracts.option_contracts if contracts.option_contracts else []:
                exp_date = str(c.expiration_date)
                expirations.add(exp_date)
                dte = (datetime.strptime(exp_date, '%Y-%m-%d').date()
                       - datetime.now().date()).days
                entry = {
                    'symbol': c.symbol,
                    'strike': float(c.strike_price),
                    'expiration': exp_date,
                    'bid': 0.0,
                    'ask': 0.0,
                    'mid': 0.0,
                    'volume': 0,
                    'open_interest': int(c.open_interest or 0),
                    'implied_volatility': 0.0,
                    'delta': 0.0,
                    'gamma': 0.0,
                    'theta': 0.0,
                    'vega': 0.0,
                    'dte': dte,
                    'contract_type': c.type,
                }
                if c.type == 'call':
                    calls.append(entry)
                else:
                    puts.append(entry)

            # Sort by strike
            calls.sort(key=lambda x: x['strike'])
            puts.sort(key=lambda x: x['strike'])

            chain = {
                'symbol': symbol,
                'expirations': sorted(expirations),
                'calls': calls,
                'puts': puts,
                'retrieved_at': datetime.now().isoformat(),
            }
            logger.info(
                f"Options chain for {symbol}: {len(calls)} calls, "
                f"{len(puts)} puts across {len(expirations)} expirations"
            )
            return chain

        except Exception as e:
            logger.error(f"Failed to fetch options chain for {symbol}: {e}")
            return {'symbol': symbol, 'expirations': [], 'calls': [], 'puts': [],
                    'error': str(e)}

    # ------------------------------------------------------------------
    # Chain analysis
    # ------------------------------------------------------------------
    def analyze_chain(self, chain: dict, direction: str = 'bullish') -> dict:
        """Analyse the chain and find the best contracts by Greeks / DTE.

        Args:
            chain: Result of get_options_chain().
            direction: 'bullish' or 'bearish'.

        Returns dict with recommended contracts and reasoning.
        """
        contracts = chain['calls'] if direction == 'bullish' else chain['puts']
        if not contracts:
            return {'recommendation': None, 'reason': 'No contracts available'}

        # Filter to sweet-spot DTE
        candidates = [c for c in contracts
                      if self.default_dte_min <= c['dte'] <= self.default_dte_max]
        if not candidates:
            candidates = contracts  # fallback to all

        # Score each contract  (higher is better)
        scored = []
        for c in candidates:
            # Prefer: high absolute delta (0.3-0.5), reasonable theta, good liquidity
            abs_delta = abs(c['delta']) if c['delta'] else 0.35  # default mid
            delta_score = 1.0 - abs(abs_delta - 0.40) * 5  # peak at 0.40 delta
            delta_score = max(0, delta_score)

            liquidity_score = min(c['open_interest'] / 500, 1.0)
            dte_score = 1.0 - abs(c['dte'] - 30) / 30  # peak at 30 DTE
            dte_score = max(0, dte_score)

            total = delta_score * 0.4 + liquidity_score * 0.3 + dte_score * 0.3
            scored.append((total, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1] if scored else None

        return {
            'direction': direction,
            'recommendation': best,
            'alternatives': [s[1] for s in scored[1:4]],
            'total_candidates': len(candidates),
            'criteria': {
                'target_delta': 0.40,
                'target_dte': 30,
                'min_open_interest': 500,
            },
        }

    # ------------------------------------------------------------------
    # Order execution
    # ------------------------------------------------------------------
    def execute_option_trade(self, symbol: str, strategy: str = 'single',
                             direction: str = 'bullish',
                             qty: int = 1,
                             limit_price: Optional[float] = None) -> dict:
        """Submit an option order.

        Args:
            symbol: OCC option symbol (e.g. 'AAPL240119C00150000').
            strategy: 'single', 'vertical', 'iron_condor'.
            direction: 'bullish' or 'bearish'.
            qty: Number of contracts.
            limit_price: Limit price per contract (None = market).

        Returns order result dict.
        """
        qty = min(qty, self.max_contracts)
        side = 'buy'  # buying to open

        try:
            self.client._rate_limit()
            if limit_price is not None:
                from alpaca.trading.requests import LimitOrderRequest
                from alpaca.trading.enums import OrderSide, TimeInForce
                request = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY if side == 'buy' else OrderSide.SELL,
                    limit_price=limit_price,
                    time_in_force=TimeInForce.DAY,
                )
            else:
                from alpaca.trading.requests import MarketOrderRequest
                from alpaca.trading.enums import OrderSide, TimeInForce
                request = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY if side == 'buy' else OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                )

            order = self.trading.submit_order(request)
            logger.info(
                f"Options order submitted: {side} {qty}x {symbol} "
                f"strategy={strategy} -> {order.id}"
            )
            return {
                'status': 'submitted',
                'order_id': str(order.id),
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'strategy': strategy,
                'direction': direction,
                'limit_price': limit_price,
            }

        except Exception as e:
            logger.error(f"Options order failed for {symbol}: {e}")
            return {'status': 'failed', 'error': str(e), 'symbol': symbol}

    # ------------------------------------------------------------------
    # Multi-leg order (vertical spread / iron condor)
    # ------------------------------------------------------------------
    def execute_multi_leg(self, legs: list, strategy: str,
                          limit_price: Optional[float] = None) -> dict:
        """Submit a multi-leg options order.

        Args:
            legs: List of dicts with keys: symbol, side ('buy'/'sell'), qty.
            strategy: Name for logging ('vertical', 'iron_condor', etc.)
            limit_price: Net debit/credit limit.
        """
        try:
            self.client._rate_limit()
            from alpaca.trading.enums import OrderSide, TimeInForce
            leg_objects = []
            for leg in legs:
                leg_objects.append({
                    'symbol': leg['symbol'],
                    'side': OrderSide.BUY if leg['side'] == 'buy' else OrderSide.SELL,
                    'qty': leg.get('qty', 1),
                })

            # Alpaca multi-leg via order_class='mleg'
            order_data = {
                'order_class': 'mleg',
                'time_in_force': TimeInForce.DAY,
                'legs': leg_objects,
            }
            if limit_price is not None:
                order_data['limit_price'] = limit_price

            order = self.trading.submit_order(order_data)
            logger.info(f"Multi-leg order ({strategy}): {len(legs)} legs -> {order.id}")
            return {
                'status': 'submitted',
                'order_id': str(order.id),
                'strategy': strategy,
                'legs': len(legs),
            }
        except Exception as e:
            logger.error(f"Multi-leg order failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    # ------------------------------------------------------------------
    # Position management
    # ------------------------------------------------------------------
    def get_positions(self) -> list:
        """Return current options positions with DTE tracking."""
        self.client._rate_limit()
        try:
            all_positions = self.trading.get_all_positions()
            options_positions = []
            for pos in all_positions:
                # Options symbols are longer and contain expiry/strike info
                sym = pos.symbol
                if len(sym) > 10 or any(c in sym for c in ['C0', 'P0']):
                    dte = self._estimate_dte_from_symbol(sym)
                    options_positions.append({
                        'symbol': sym,
                        'qty': int(pos.qty),
                        'side': pos.side,
                        'avg_entry_price': float(pos.avg_entry_price),
                        'current_price': float(pos.current_price),
                        'market_value': float(pos.market_value),
                        'unrealized_pl': float(pos.unrealized_pl),
                        'unrealized_plpc': float(pos.unrealized_plpc),
                        'dte': dte,
                        'needs_close': dte is not None and dte < CLOSE_BEFORE_DTE,
                    })
            return options_positions
        except Exception as e:
            logger.error(f"Failed to get options positions: {e}")
            return []

    def close_position(self, symbol: str) -> dict:
        """Close an options position by symbol."""
        self.client._rate_limit()
        try:
            self.trading.close_position(symbol)
            logger.info(f"Closed options position: {symbol}")
            return {'status': 'closed', 'symbol': symbol}
        except Exception as e:
            logger.error(f"Failed to close {symbol}: {e}")
            return {'status': 'failed', 'symbol': symbol, 'error': str(e)}

    def close_expiring_positions(self) -> list:
        """Close any options positions within CLOSE_BEFORE_DTE days of expiry."""
        results = []
        for pos in self.get_positions():
            if pos.get('needs_close'):
                result = self.close_position(pos['symbol'])
                results.append(result)
                logger.warning(
                    f"Auto-closing expiring option {pos['symbol']} "
                    f"(DTE={pos['dte']})"
                )
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _estimate_dte_from_symbol(occ_symbol: str) -> Optional[int]:
        """Extract expiration from OCC symbol format and compute DTE.

        OCC format: SYMBOL + YYMMDD + C/P + STRIKE (8 digits)
        Example: AAPL240119C00150000 -> 2024-01-19
        """
        try:
            # Strip underlying (variable length), last 9 chars are C/P + strike
            # Date is 6 chars before that
            date_str = occ_symbol[-15:-9]
            exp = datetime.strptime(date_str, '%y%m%d').date()
            return (exp - datetime.now().date()).days
        except (ValueError, IndexError):
            return None
