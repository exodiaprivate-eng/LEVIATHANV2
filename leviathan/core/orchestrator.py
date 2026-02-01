"""Main application orchestrator - coordinates all trading modules."""
import logging
import time
import traceback
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger('leviathan.orchestrator')


class Orchestrator:
    """Coordinates the complete trading pipeline."""

    def __init__(self, alpaca_client, opus_brain, risk_manager,
                 signal_generator, learning_db, state_db,
                 exit_manager=None, executor=None, ensemble=None,
                 sentiment_analyzer=None, feature_engine=None,
                 watchlist=None, paper_mode=True):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        self.risk = risk_manager
        self.signals = signal_generator
        self.learning_db = learning_db
        self.state_db = state_db
        self.exit_manager = exit_manager
        self.executor = executor
        self.ensemble = ensemble
        self.sentiment = sentiment_analyzer
        self.features = feature_engine
        self.watchlist = watchlist or [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
            "AMD", "JPM", "V", "MA", "UNH", "HD", "PG", "JNJ",
        ]
        self.paper_mode = paper_mode
        self.is_running = False
        self._cycle_count = 0

    def run_cycle(self) -> dict:
        """
        Run one complete trading cycle.

        Pipeline:
        1. Get account info and positions
        2. Check existing positions for exits
        3. Scan watchlist symbols
        4. For each symbol: features → ensemble → sentiment → risk check
        5. If signal strong enough → ask Opus brain
        6. If Opus approves → submit order
        7. Log everything
        """
        self._cycle_count += 1
        cycle_start = datetime.now()
        result = {
            'cycle': self._cycle_count,
            'trade_executed': False,
            'signals_generated': 0,
            'symbols_scanned': 0,
            'exits': [],
            'entries': [],
            'errors': [],
        }

        try:
            # ─── 1. Account & Positions ────────────────────────
            account = self.alpaca.get_account()
            buying_power = float(account.buying_power)
            account_value = float(account.equity)
            positions = self._get_current_positions()

            self.risk.update_account(account_value, positions)

            logger.info(
                "Cycle %d | Account=$%.2f | Buying Power=$%.2f | Positions=%d",
                self._cycle_count, account_value, buying_power, len(positions)
            )

            # ─── 2. Check Exits ────────────────────────────────
            if self.exit_manager and positions:
                try:
                    exits = self.exit_manager.check_all_positions()
                    for exit_signal in exits:
                        symbol = exit_signal.get('symbol', '')
                        reason = exit_signal.get('reason', 'exit signal')
                        logger.info("EXIT SIGNAL: %s - %s", symbol, reason)

                        self.exit_manager.execute_exit(exit_signal)
                        result['exits'].append({
                            'symbol': symbol,
                            'reason': reason,
                        })
                        result['trade_executed'] = True

                        # Log to learning DB
                        if self.learning_db:
                            self.learning_db.log_trade_exit(
                                symbol=symbol,
                                reason=reason,
                                timestamp=datetime.now().isoformat(),
                            )
                except Exception as e:
                    logger.error("Exit check error: %s", e)
                    result['errors'].append(f"Exit check: {e}")

            # ─── 3. Scan Watchlist for New Entries ─────────────
            if buying_power < 100:
                logger.info("Insufficient buying power ($%.2f), skipping scan", buying_power)
                return result

            for symbol in self.watchlist:
                # Skip if already in a position
                if symbol in positions:
                    continue

                result['symbols_scanned'] += 1

                try:
                    analysis = self._analyze_symbol(symbol)
                    if analysis is None:
                        continue

                    signal = analysis.get('signal', 'HOLD')
                    confidence = analysis.get('confidence', 0.0)

                    if signal == 'HOLD' or confidence < 0.6:
                        continue

                    result['signals_generated'] += 1
                    logger.info(
                        "Signal: %s %s (confidence=%.2f)",
                        signal, symbol, confidence
                    )

                    # ─── 4. Risk Check ─────────────────────────
                    est_price = analysis.get('price', 0)
                    est_qty = self._calculate_position_size(
                        account_value, est_price, confidence
                    )
                    if est_qty <= 0:
                        continue

                    approved, reason = self.risk.pre_trade_check(
                        symbol=symbol,
                        side=signal,
                        qty=est_qty,
                        price=est_price,
                    )
                    if not approved:
                        logger.info("Risk rejected %s %s: %s", signal, symbol, reason)
                        continue

                    # ─── 5. Ask Opus Brain ─────────────────────
                    if self.opus:
                        try:
                            decision = self.opus.make_trade_decision(
                                symbol=symbol,
                                analysis_data=analysis,
                                current_positions=positions,
                            )
                            opus_action = decision.get('action', 'SKIP')
                            opus_confidence = decision.get('confidence', 0.0)

                            if opus_action == 'SKIP' or opus_confidence < 0.5:
                                logger.info(
                                    "Opus rejected %s: action=%s conf=%.2f",
                                    symbol, opus_action, opus_confidence
                                )
                                continue

                            # Use Opus-adjusted quantity if provided
                            if 'quantity' in decision:
                                est_qty = decision['quantity']

                        except Exception as e:
                            logger.error("Opus brain error for %s: %s", symbol, e)
                            continue

                    # ─── 6. Execute Trade ──────────────────────
                    if self.executor:
                        try:
                            order = self.executor.submit_order(
                                symbol=symbol,
                                qty=est_qty,
                                side=signal.lower(),
                                price=est_price,
                            )
                            if order:
                                result['trade_executed'] = True
                                result['entries'].append({
                                    'symbol': symbol,
                                    'side': signal,
                                    'qty': est_qty,
                                    'price': est_price,
                                    'confidence': confidence,
                                })

                                self.risk.record_trade(
                                    symbol, signal, est_qty, est_price
                                )

                                # Log to learning DB
                                if self.learning_db:
                                    self.learning_db.log_trade_entry(
                                        symbol=symbol,
                                        side=signal,
                                        qty=est_qty,
                                        price=est_price,
                                        confidence=confidence,
                                        analysis=analysis,
                                        timestamp=datetime.now().isoformat(),
                                    )

                                logger.info(
                                    "ORDER SUBMITTED: %s %s x%d @ $%.2f",
                                    signal, symbol, est_qty, est_price
                                )
                        except Exception as e:
                            logger.error("Order submission error for %s: %s", symbol, e)
                            result['errors'].append(f"Order {symbol}: {e}")

                except Exception as e:
                    logger.error("Analysis error for %s: %s", symbol, e)
                    result['errors'].append(f"Analysis {symbol}: {e}")

        except Exception as e:
            logger.error("Trading cycle error: %s\n%s", e, traceback.format_exc())
            result['errors'].append(str(e))

        elapsed = (datetime.now() - cycle_start).total_seconds()
        logger.info(
            "Cycle %d complete in %.1fs | Scanned=%d | Signals=%d | "
            "Exits=%d | Entries=%d | Errors=%d",
            self._cycle_count, elapsed, result['symbols_scanned'],
            result['signals_generated'], len(result['exits']),
            len(result['entries']), len(result['errors'])
        )
        return result

    def _analyze_symbol(self, symbol: str) -> Optional[dict]:
        """Run full analysis pipeline for a symbol."""
        analysis = {'symbol': symbol}

        try:
            # Get latest price
            quote = self.alpaca.get_latest_price(symbol)
            if not quote:
                return None
            analysis['price'] = quote

            # Ensemble prediction
            if self.ensemble:
                prediction = self.ensemble.predict_with_confidence(symbol)
                if prediction:
                    analysis['signal'] = prediction.get('signal', 'HOLD')
                    analysis['confidence'] = prediction.get('confidence', 0.0)
                    analysis['model_signals'] = prediction.get('model_signals', {})
                else:
                    analysis['signal'] = 'HOLD'
                    analysis['confidence'] = 0.0
            else:
                # Fallback: use signal generator
                if self.signals:
                    sig = self.signals.generate(symbol)
                    analysis['signal'] = sig.get('signal', 'HOLD')
                    analysis['confidence'] = sig.get('confidence', 0.0)
                else:
                    return None

            # Sentiment analysis
            if self.sentiment:
                try:
                    sent = self.sentiment.analyze(symbol)
                    analysis['sentiment'] = sent
                    # Boost or dampen confidence based on sentiment alignment
                    sent_score = sent.get('score', 0.0)
                    if analysis['signal'] == 'BUY' and sent_score > 0.3:
                        analysis['confidence'] = min(1.0, analysis['confidence'] * 1.1)
                    elif analysis['signal'] == 'BUY' and sent_score < -0.3:
                        analysis['confidence'] *= 0.8
                except Exception as e:
                    logger.debug("Sentiment analysis skipped for %s: %s", symbol, e)

            return analysis

        except Exception as e:
            logger.error("Analysis failed for %s: %s", symbol, e)
            return None

    def _calculate_position_size(self, account_value: float, price: float,
                                  confidence: float) -> int:
        """Calculate shares to buy based on account value and confidence."""
        if price <= 0 or account_value <= 0:
            return 0

        # Base: 5% of account per position
        base_value = account_value * 0.05
        # Scale by confidence (0.6-1.0 maps to 0.5-1.0 of base)
        scale = 0.5 + (confidence - 0.6) * 1.25  # 0.6→0.5, 1.0→1.0
        scale = max(0.25, min(1.0, scale))

        # Apply drawdown scaler from risk manager
        qty = int((base_value * scale) / price)
        qty = self.risk.get_adjusted_quantity(qty, price)

        return max(1, qty) if qty > 0 else 0

    def _get_current_positions(self) -> Dict[str, dict]:
        """Get current positions as dict."""
        try:
            positions = self.alpaca.get_all_positions()
            return {
                p.symbol: {
                    'qty': float(p.qty),
                    'avg_entry': float(p.avg_entry_price),
                    'current_price': float(p.current_price),
                    'market_value': float(p.market_value),
                    'unrealized_pnl': float(p.unrealized_pl),
                    'side': p.side,
                }
                for p in positions
            }
        except Exception as e:
            logger.error("Failed to get positions: %s", e)
            return {}

    def start(self):
        self.is_running = True
        logger.info("Orchestrator started (paper=%s)", self.paper_mode)

    def stop(self):
        self.is_running = False
        logger.info("Orchestrator stopped")

    def cancel_all_orders(self):
        try:
            self.alpaca.cancel_all_orders()
        except Exception as e:
            logger.error("Failed to cancel orders: %s", e)

    def run(self, interval_seconds: int = 60):
        """Main loop - run cycles at interval."""
        self.start()
        while self.is_running:
            self.run_cycle()
            time.sleep(interval_seconds)
