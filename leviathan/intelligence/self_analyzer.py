"""AI self-analysis - the system reasons about its own performance."""
import json
import logging
import sqlite3
from datetime import datetime

from anthropic import Anthropic

logger = logging.getLogger('leviathan.self_analyzer')


class SelfAnalyzer:
    """Uses LLM to analyze trading performance and suggest improvements."""

    def __init__(self, learning_db, anthropic_key: str = None):
        self.db = learning_db
        self.client = Anthropic(api_key=anthropic_key) if anthropic_key else None

    def run_daily_analysis(self) -> dict:
        today = self.db.get_recent_trades(days=1)
        week = self.db.get_recent_trades(days=7)
        if not today:
            return {'status': 'no_trades'}

        prompt = self._build_prompt(today, week)
        if self.client:
            resp = self.client.messages.create(
                model='claude-sonnet-4-20250514', max_tokens=2000,
                messages=[{'role': 'user', 'content': prompt}])
            analysis = resp.content[0].text
        else:
            analysis = self._rule_based(today, week)

        result = self._parse(analysis)
        self._store(result)
        return result

    def _build_prompt(self, today, week):
        ts = self._summarize(today)
        ws = self._summarize(week)
        return f"""Analyze your trading performance as Leviathan AI.

TODAY: {json.dumps(ts)}
WEEK: {json.dumps(ws)}

Respond ONLY with JSON:
{{"performance_assessment": "...", "identified_issues": [...], "what_worked": [...],
  "proposed_adjustments": [...], "confidence_adjustment": 0, "reasoning": "..."}}"""

    def _summarize(self, trades):
        if not trades:
            return {}
        wins = sum(1 for t in trades if t.get('profit_loss', 0) > 0)
        return {'count': len(trades), 'wins': wins,
                'win_rate': wins / len(trades) if trades else 0,
                'total_pnl': sum(t.get('profit_loss', 0) for t in trades)}

    def _rule_based(self, today, week):
        wr = sum(1 for t in week if t.get('profit_loss', 0) > 0) / max(len(week), 1)
        issues = []
        adj = []
        if wr < 0.45:
            issues.append("Win rate below 45%")
            adj.append("Increase confidence threshold")
        return json.dumps({'performance_assessment': f"WR: {wr:.1%}",
                           'identified_issues': issues, 'what_worked': [],
                           'proposed_adjustments': adj, 'confidence_adjustment': -1 if wr < 0.45 else 0,
                           'reasoning': 'Rule-based analysis'})

    def _parse(self, text):
        try:
            clean = text.strip()
            if clean.startswith('```'):
                clean = clean.split('```')[1]
                if clean.startswith('json'):
                    clean = clean[4:]
            return json.loads(clean)
        except Exception:
            return {'performance_assessment': 'Parse error', 'identified_issues': [],
                    'proposed_adjustments': [], 'confidence_adjustment': 0, 'reasoning': text[:500]}

    def _store(self, result):
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.execute('''INSERT INTO self_analysis (analysis_date, period_analyzed,
                performance_summary, identified_issues, proposed_adjustments, llm_reasoning)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (datetime.now().isoformat(), 'daily', result.get('performance_assessment', ''),
                 json.dumps(result.get('identified_issues', [])),
                 json.dumps(result.get('proposed_adjustments', [])),
                 result.get('reasoning', '')))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")

    def apply_learned_adjustments(self, config: dict) -> dict:
        """Read the most recent self-analysis and apply proposed adjustments to config."""
        import sqlite3 as _sqlite3

        adjusted = dict(config)
        try:
            conn = _sqlite3.connect(self.db.db_path)
            row = conn.execute('''
                SELECT proposed_adjustments, confidence_adjustment, llm_reasoning
                FROM self_analysis
                WHERE adjustments_applied = FALSE
                ORDER BY analysis_date DESC LIMIT 1
            ''').fetchone()
            conn.close()

            if not row:
                return adjusted

            proposed_raw = row[0]
            confidence_adj = row[1] if row[1] else 0

            try:
                proposed = json.loads(proposed_raw) if isinstance(proposed_raw, str) else proposed_raw
            except (json.JSONDecodeError, TypeError):
                proposed = []

            if not isinstance(proposed, list):
                proposed = [proposed] if proposed else []

            # Apply adjustments within safe bounds
            for adj in proposed:
                adj_lower = str(adj).lower() if adj else ''

                if 'confidence threshold' in adj_lower or 'increase confidence' in adj_lower:
                    current = adjusted.get('min_signal_confidence', 0.6)
                    adjusted['min_signal_confidence'] = min(current + 0.05, 0.90)
                    logger.info("Adjustment: min_signal_confidence -> %.2f", adjusted['min_signal_confidence'])

                elif 'decrease confidence' in adj_lower or 'lower threshold' in adj_lower:
                    current = adjusted.get('min_signal_confidence', 0.6)
                    adjusted['min_signal_confidence'] = max(current - 0.05, 0.40)
                    logger.info("Adjustment: min_signal_confidence -> %.2f", adjusted['min_signal_confidence'])

                elif 'reduce position' in adj_lower or 'smaller position' in adj_lower:
                    current = adjusted.get('max_position_pct', 0.30)
                    adjusted['max_position_pct'] = max(current - 0.05, 0.05)
                    logger.info("Adjustment: max_position_pct -> %.2f", adjusted['max_position_pct'])

                elif 'increase position' in adj_lower or 'larger position' in adj_lower:
                    current = adjusted.get('max_position_pct', 0.30)
                    adjusted['max_position_pct'] = min(current + 0.05, 0.30)
                    logger.info("Adjustment: max_position_pct -> %.2f", adjusted['max_position_pct'])

                elif 'tighter stop' in adj_lower:
                    current = adjusted.get('default_stop_loss_pct', 0.03)
                    adjusted['default_stop_loss_pct'] = max(current - 0.005, 0.01)
                    logger.info("Adjustment: default_stop_loss_pct -> %.3f", adjusted['default_stop_loss_pct'])

                elif 'wider stop' in adj_lower or 'looser stop' in adj_lower:
                    current = adjusted.get('default_stop_loss_pct', 0.03)
                    adjusted['default_stop_loss_pct'] = min(current + 0.005, 0.08)
                    logger.info("Adjustment: default_stop_loss_pct -> %.3f", adjusted['default_stop_loss_pct'])

            # Apply confidence_adjustment from analysis (integer offset)
            if isinstance(confidence_adj, (int, float)) and confidence_adj != 0:
                current = adjusted.get('min_signal_confidence', 0.6)
                delta = confidence_adj * 0.02  # Each unit = 2% shift
                adjusted['min_signal_confidence'] = max(0.40, min(0.90, current + delta))

            # Mark this analysis as applied
            try:
                conn = _sqlite3.connect(self.db.db_path)
                conn.execute('''
                    UPDATE self_analysis SET adjustments_applied = TRUE
                    WHERE adjustments_applied = FALSE
                    AND id = (SELECT id FROM self_analysis WHERE adjustments_applied = FALSE
                              ORDER BY analysis_date DESC LIMIT 1)
                ''')
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to mark adjustment applied: {e}")

            logger.info("Applied learned adjustments from self-analysis")
        except Exception as e:
            logger.error(f"apply_learned_adjustments failed: {e}")

        return adjusted
