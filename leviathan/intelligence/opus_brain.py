"""
OpusTradingBrain and OpusExitManager - Claude Opus 4.5 powered trading intelligence.

Opus serves as the final decision maker for all trades, receiving ML signals,
market data, sentiment, and portfolio context to make autonomous trading decisions.
"""

import json
import logging
import re
from datetime import datetime
from typing import Optional

from anthropic import Anthropic

from leviathan.config.llm_config import LLM_CONFIG, LLMBudgetTracker

logger = logging.getLogger(__name__)


class OpusTradingBrain:
    """
    Opus 4.5 is the final decision maker for all trades.
    It receives ML signals and context, then decides autonomously.
    """

    def __init__(self, config: dict, learning_db):
        """
        Initialize the Opus Trading Brain.

        Args:
            config: Configuration dict containing at minimum 'api_key'.
                    May also contain 'model', 'max_tokens', etc.
            learning_db: Learning database instance for historical context and logging.
        """
        api_key = config.get('api_key') or config.get('anthropic_api_key', '')
        self.client = Anthropic(api_key=api_key)
        self.model = config.get('model', LLM_CONFIG['decision_model'])
        self.max_tokens = config.get('max_tokens', 1000)
        self.db = learning_db
        self.budget_tracker = LLMBudgetTracker()
        logger.info(f"OpusTradingBrain initialized with model={self.model}")

    def make_trade_decision(
        self,
        symbol: str,
        analysis_data: dict,
        current_positions: dict,
    ) -> dict:
        """
        Opus analyzes all inputs and makes the final trade decision.

        Args:
            symbol: Ticker symbol (e.g. 'AAPL').
            analysis_data: Dict containing ml_signal, market_data, sentiment,
                           account_value, and any other analytical context.
            current_positions: Dict describing current portfolio positions and state.

        Returns:
            Structured decision dict with action, sizing, stops, reasoning, etc.
        """
        if not self.budget_tracker.can_call_opus():
            logger.warning("Opus daily budget exhausted - rejecting trade decision request")
            return {
                "action": "REJECT",
                "reasoning": "Daily Opus API budget exhausted",
                "confidence": 0.0,
            }

        try:
            # Gather historical context from learning database
            historical_context = self._get_historical_context(symbol, analysis_data)

            # Build the decision prompt
            prompt = self._build_decision_prompt(
                symbol=symbol,
                analysis_data=analysis_data,
                current_positions=current_positions,
                historical_context=historical_context,
            )

            # Get Opus decision
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": prompt}],
            )

            # Track costs
            self.budget_tracker.record_call(self.model)

            # Parse and validate decision
            response_text = response.content[0].text
            decision = self._parse_decision(response_text)

            # Log decision to database
            self._log_decision(symbol, decision, decision.get("reasoning", ""))

            logger.info(
                f"Opus decision for {symbol}: {decision.get('action')} "
                f"(confidence={decision.get('confidence', 0):.2f})"
            )
            return decision

        except Exception as e:
            logger.error(f"Error in make_trade_decision for {symbol}: {e}", exc_info=True)
            return {
                "action": "REJECT",
                "reasoning": f"Error during Opus decision: {e}",
                "confidence": 0.0,
                "error": str(e),
            }

    def _get_system_prompt(self) -> str:
        """Return the system prompt that defines Opus's trading persona and rules."""
        return (
            "You are Opus, the trading brain of Leviathan - an autonomous AI trading system.\n"
            "\n"
            "Your role is to make final trading decisions. You receive signals from ML models "
            "and must decide whether to execute trades.\n"
            "\n"
            "CRITICAL RULES:\n"
            "1. You have FULL AUTHORITY to execute trades autonomously. No human approval needed.\n"
            "2. Always respect risk limits provided in the context.\n"
            "3. Never exceed the maximum position size allowed.\n"
            "4. Always set stop losses and take profits.\n"
            "5. If uncertain, REJECT the trade. Capital preservation is paramount.\n"
            "6. Learn from historical context - what worked before in similar conditions?\n"
            "7. Consider correlation risk - avoid over-concentration in similar assets.\n"
            "8. Factor in current market regime (trending, ranging, volatile).\n"
            "9. Account for liquidity - larger positions need more liquid instruments.\n"
            "10. Be decisive. Provide clear reasoning for every decision.\n"
            "\n"
            "You must respond with a JSON object containing your decision. No other text outside the JSON."
        )

    def _build_decision_prompt(
        self,
        symbol: str,
        analysis_data: dict,
        current_positions: dict,
        historical_context: Optional[dict] = None,
    ) -> str:
        """
        Format all available data into a structured prompt for the LLM.

        Args:
            symbol: Ticker symbol.
            analysis_data: All analytical data (ml_signal, market_data, sentiment, etc.).
            current_positions: Portfolio state and positions.
            historical_context: Past similar trade outcomes from learning DB.

        Returns:
            Formatted prompt string.
        """
        ml_signal = analysis_data.get("ml_signal", {})
        market_data = analysis_data.get("market_data", {})
        sentiment = analysis_data.get("sentiment", {})
        account_value = analysis_data.get("account_value", 0.0)

        # Safely format ML signal section
        ml_section = "ML SIGNAL:\n"
        ml_section += f"- Direction: {ml_signal.get('direction', 'UNKNOWN')}\n"
        ml_section += f"- Confidence: {ml_signal.get('confidence', 0):.2%}\n"
        ml_section += f"- Technical Score: {ml_signal.get('technical_score', 0):.2f}\n"
        if 'lstm_pred' in ml_signal:
            ml_section += f"- LSTM Prediction: {ml_signal['lstm_pred']:.2%} price change\n"
        if 'lgbm_prob' in ml_signal:
            ml_section += f"- LightGBM Probability: {ml_signal['lgbm_prob']:.2%}\n"

        # Market data section
        mkt_section = "CURRENT MARKET DATA:\n"
        mkt_section += f"- Price: ${market_data.get('price', 0):.2f}\n"
        mkt_section += f"- Daily Change: {market_data.get('daily_change', 0):.2%}\n"
        mkt_section += f"- RSI(14): {market_data.get('rsi', 50):.1f}\n"
        mkt_section += f"- MACD: {market_data.get('macd', 0):.4f}\n"
        mkt_section += f"- Volume vs Avg: {market_data.get('volume_ratio', 1.0):.1f}x\n"
        mkt_section += f"- ATR(14): ${market_data.get('atr', 0):.2f}\n"
        mkt_section += f"- 50-day MA: ${market_data.get('sma_50', 0):.2f}\n"
        mkt_section += f"- 200-day MA: ${market_data.get('sma_200', 0):.2f}\n"

        # Sentiment section
        sent_section = "SENTIMENT:\n"
        sent_section += f"- News Score: {sentiment.get('news_score', 0):.2f} (-1 to +1)\n"
        sent_section += f"- Social Score: {sentiment.get('social_score', 0):.2f} (-1 to +1)\n"
        headlines = sentiment.get('headlines', [])
        if headlines:
            sent_section += f"- Recent Headlines: {headlines[:3]}\n"

        # Portfolio section
        port_section = "PORTFOLIO STATE:\n"
        port_section += f"- Account Value: ${account_value:.2f}\n"
        port_section += f"- Buying Power: ${current_positions.get('buying_power', 0):.2f}\n"
        port_section += f"- Current Positions: {len(current_positions.get('positions', {}))}\n"
        positions_dict = current_positions.get('positions', {})
        port_section += f"- Already holding {symbol}: {symbol in positions_dict}\n"
        port_section += f"- Today's P&L: ${current_positions.get('daily_pnl', 0):.2f}\n"
        port_section += f"- Day Trades Used: {current_positions.get('day_trades_used', 0)}/3\n"

        # Risk limits section
        risk_section = "RISK LIMITS:\n"
        risk_section += f"- Max Position Size: ${current_positions.get('max_position_dollars', 0):.2f}\n"
        risk_section += f"- Current Performance Tier: {current_positions.get('performance_tier', 'standard')}\n"
        min_pct = current_positions.get('min_position_pct', 0.02)
        max_pct = current_positions.get('max_position_pct', 0.10)
        risk_section += f"- Dynamic Position Range: {min_pct:.1%} - {max_pct:.1%}\n"
        risk_section += f"- Current Drawdown: {current_positions.get('current_drawdown', 0):.1%}\n"

        # Historical context
        hist_section = "HISTORICAL CONTEXT (Similar Past Trades):\n"
        hist_section += json.dumps(historical_context or {"note": "No historical data available"}, indent=2)

        prompt = (
            f"TRADE DECISION REQUIRED\n\n"
            f"=== SYMBOL: {symbol} ===\n\n"
            f"{ml_section}\n"
            f"{mkt_section}\n"
            f"{sent_section}\n"
            f"{port_section}\n"
            f"{risk_section}\n"
            f"{hist_section}\n\n"
            f"=== YOUR DECISION ===\n\n"
            f"Respond with ONLY a JSON object:\n"
            f"{{\n"
            f'    "action": "EXECUTE" | "REJECT" | "MODIFY",\n'
            f'    "side": "buy" | "sell" | null,\n'
            f'    "position_size_dollars": <number or null>,\n'
            f'    "position_size_pct": <percentage as decimal>,\n'
            f'    "order_type": "market" | "limit",\n'
            f'    "limit_price": <number or null>,\n'
            f'    "stop_loss_price": <number>,\n'
            f'    "take_profit_price": <number>,\n'
            f'    "reasoning": "<your detailed reasoning>",\n'
            f'    "confidence": <0.0 to 1.0>,\n'
            f'    "risk_assessment": "<brief risk assessment>"\n'
            f"}}\n\n"
            f"If REJECT, set side and prices to null but explain reasoning."
        )

        return prompt

    def _parse_decision(self, response_text: str) -> dict:
        """
        Extract structured decision from LLM response text.

        Handles markdown code blocks, extra whitespace, and partial JSON.

        Args:
            response_text: Raw text response from Claude.

        Returns:
            Parsed decision dict. Falls back to REJECT on parse failure.
        """
        try:
            clean = response_text.strip()

            # Strip markdown code fences
            if clean.startswith("```"):
                # Extract content between first pair of ```
                parts = clean.split("```")
                if len(parts) >= 3:
                    clean = parts[1]
                else:
                    clean = parts[1] if len(parts) > 1 else clean
                # Remove optional language identifier
                if clean.startswith("json"):
                    clean = clean[4:]
                clean = clean.strip()

            # Try to find JSON object via braces if still not clean
            if not clean.startswith("{"):
                match = re.search(r'\{.*\}', clean, re.DOTALL)
                if match:
                    clean = match.group(0)

            decision = json.loads(clean)

            # Validate required fields
            required = ["action", "reasoning", "confidence"]
            for field in required:
                if field not in decision:
                    raise ValueError(f"Missing required field: {field}")

            # Normalize action to uppercase
            decision["action"] = decision["action"].upper()

            # Clamp confidence to [0, 1]
            decision["confidence"] = max(0.0, min(1.0, float(decision["confidence"])))

            return decision

        except Exception as e:
            logger.error(f"Failed to parse Opus response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            return {
                "action": "REJECT",
                "reasoning": f"Failed to parse Opus response: {e}",
                "confidence": 0.0,
                "error": str(e),
            }

    def _log_decision(self, symbol: str, decision: dict, reasoning: str):
        """
        Log every decision to the learning database for future reference.

        Args:
            symbol: Ticker symbol.
            decision: The parsed decision dict.
            reasoning: The reasoning string from the decision.
        """
        try:
            self.db.log_opus_decision(
                timestamp=datetime.now(),
                symbol=symbol,
                decision=decision,
                reasoning=reasoning,
            )
        except Exception as e:
            logger.error(f"Failed to log decision for {symbol}: {e}")

    def _get_historical_context(self, symbol: str, analysis_data: dict) -> dict:
        """
        Query learning database for similar past trade situations.

        Args:
            symbol: Ticker symbol.
            analysis_data: Current analysis data to find similar past trades.

        Returns:
            Summary dict of similar historical trades and their outcomes.
        """
        try:
            ml_signal = analysis_data.get("ml_signal", {})
            similar_trades = self.db.query_similar_trades(
                symbol=symbol,
                signal_confidence=ml_signal.get("confidence", 0),
                technical_score=ml_signal.get("technical_score", 0),
                limit=5,
            )

            if not similar_trades:
                return {"note": "No similar historical trades found"}

            wins = sum(1 for t in similar_trades if t.get("profit_loss", 0) > 0)
            pnl_pcts = [t.get("profit_loss_pct", 0) for t in similar_trades]
            avg_profit = sum(pnl_pcts) / len(pnl_pcts)

            return {
                "similar_trades_found": len(similar_trades),
                "win_rate_in_similar": f"{wins / len(similar_trades):.0%}",
                "avg_outcome": f"{avg_profit:.2%}",
                "best_outcome": f"{max(pnl_pcts):.2%}",
                "worst_outcome": f"{min(pnl_pcts):.2%}",
                "sample_trades": [
                    {
                        "date": t.get("entry_date", "unknown"),
                        "entry": t.get("entry_price", 0),
                        "exit": t.get("exit_price", 0),
                        "result": f"{t.get('profit_loss_pct', 0):.2%}",
                    }
                    for t in similar_trades[:3]
                ],
            }

        except Exception as e:
            logger.warning(f"Could not retrieve historical context for {symbol}: {e}")
            return {"note": f"Historical context unavailable: {e}"}

    def get_budget_stats(self) -> dict:
        """Return current budget/usage statistics."""
        return self.budget_tracker.get_stats()


class OpusExitManager:
    """
    Opus also decides when to exit positions.
    Runs periodically to evaluate all open positions.
    """

    def __init__(self, opus_brain: OpusTradingBrain):
        """
        Initialize exit manager with a reference to the trading brain.

        Args:
            opus_brain: An initialized OpusTradingBrain instance.
        """
        self.brain = opus_brain

    def analyze_exit(self, position: dict, market_data: dict) -> dict:
        """
        Use Claude to decide if a single position should be exited.

        Args:
            position: Dict with symbol, entry_price, unrealized_pnl_pct,
                      days_held, stop_loss, take_profit, etc.
            market_data: Dict keyed by symbol containing price, rsi, macd, etc.

        Returns:
            Decision dict with action (EXIT/HOLD/ADJUST), reasoning, etc.
        """
        if not self.brain.budget_tracker.can_call_opus():
            logger.warning("Opus budget exhausted - defaulting to HOLD for exit evaluation")
            return {
                "action": "HOLD",
                "reasoning": "Daily Opus API budget exhausted - defaulting to hold",
                "exit_type": None,
                "new_stop_loss": None,
                "new_take_profit": None,
            }

        try:
            prompt = self._build_exit_prompt(position, market_data)

            response = self.brain.client.messages.create(
                model=self.brain.model,
                max_tokens=500,
                system=(
                    "You are Opus, the exit manager of Leviathan. "
                    "Evaluate whether open positions should be exited, held, or adjusted. "
                    "Protect profits and cut losses. Respond with JSON only."
                ),
                messages=[{"role": "user", "content": prompt}],
            )

            self.brain.budget_tracker.record_call(self.brain.model)
            decision = self.brain._parse_decision(response.content[0].text)

            symbol = position.get("symbol", "UNKNOWN")
            logger.info(
                f"Exit evaluation for {symbol}: {decision.get('action')} - "
                f"{decision.get('reasoning', '')[:80]}"
            )
            return decision

        except Exception as e:
            logger.error(f"Error in exit analysis: {e}", exc_info=True)
            return {
                "action": "HOLD",
                "reasoning": f"Error during exit evaluation: {e}",
                "exit_type": None,
                "new_stop_loss": None,
                "new_take_profit": None,
            }

    def _build_exit_prompt(self, position: dict, market_data: dict) -> str:
        """
        Build the exit evaluation prompt for a single position.

        Args:
            position: Position details dict.
            market_data: Market data dict keyed by symbol.

        Returns:
            Formatted prompt string.
        """
        symbol = position.get("symbol", "UNKNOWN")
        sym_data = market_data.get(symbol, {})

        entry_price = position.get("entry_price", 0)
        current_price = sym_data.get("price", entry_price)
        pnl_pct = position.get(
            "unrealized_pnl_pct",
            ((current_price / entry_price) - 1) if entry_price else 0,
        )
        price_vs_entry = ((current_price / entry_price) - 1) * 100 if entry_price else 0

        prompt = (
            f"POSITION EXIT EVALUATION\n\n"
            f"Symbol: {symbol}\n"
            f"Entry Price: ${entry_price:.2f}\n"
            f"Current Price: ${current_price:.2f}\n"
            f"Unrealized P&L: {pnl_pct:.2%}\n"
            f"Days Held: {position.get('days_held', 0)}\n"
            f"Original Stop Loss: ${position.get('stop_loss', 0):.2f}\n"
            f"Original Take Profit: ${position.get('take_profit', 0):.2f}\n"
            f"\n"
            f"Current Indicators:\n"
            f"- RSI: {sym_data.get('rsi', 50):.1f}\n"
            f"- MACD: {sym_data.get('macd', 0):.4f}\n"
            f"- Price vs Entry: {price_vs_entry:.2f}%\n"
            f"\n"
            f"Should we EXIT this position now, HOLD, or ADJUST stop/target?\n\n"
            f"Respond with JSON:\n"
            f"{{\n"
            f'    "action": "EXIT" | "HOLD" | "ADJUST",\n'
            f'    "exit_type": "market" | "limit" | null,\n'
            f'    "new_stop_loss": <number or null>,\n'
            f'    "new_take_profit": <number or null>,\n'
            f'    "reasoning": "<explanation>",\n'
            f'    "confidence": <0.0 to 1.0>\n'
            f"}}"
        )

        return prompt

    def evaluate_all_positions(self, positions: list, market_data: dict) -> list:
        """
        Evaluate all open positions and return exit instructions.

        Args:
            positions: List of position dicts.
            market_data: Market data dict keyed by symbol.

        Returns:
            List of exit/adjust instruction dicts (excludes HOLDs).
        """
        instructions = []
        for position in positions:
            decision = self.analyze_exit(position, market_data)
            if decision.get("action") in ("EXIT", "ADJUST"):
                decision["symbol"] = position.get("symbol", "UNKNOWN")
                instructions.append(decision)
        return instructions
