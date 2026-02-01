"""Pattern recognition and storage for learning."""
import json
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger('leviathan.patterns')


class PatternLearner:
    """Identify and store recurring profitable patterns."""

    def __init__(self, learning_db):
        self.db = learning_db

    def identify_patterns(self, trade_history: list) -> list:
        patterns = []
        # Group by indicator conditions at entry
        for trade in trade_history:
            rsi = trade.get('rsi_at_entry', 50)
            profit = trade.get('profit_loss_pct', 0)
            if rsi < 30 and profit > 0:
                patterns.append({'name': 'rsi_oversold_bounce', 'rsi': rsi, 'profit': profit})
            elif rsi > 70 and profit < 0:
                patterns.append({'name': 'rsi_overbought_reversal', 'rsi': rsi, 'profit': profit})
        return patterns

    def store_pattern(self, name: str, description: str, conditions: dict,
                      success_rate: float, avg_profit: float, occurrences: int):
        conn = sqlite3.connect(self.db.db_path)
        conn.execute('''INSERT OR REPLACE INTO learned_patterns
            (pattern_name, pattern_description, indicator_conditions,
             success_rate, avg_profit_when_followed, occurrences, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (name, description, json.dumps(conditions), success_rate,
             avg_profit, occurrences, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def query_patterns(self, min_success_rate: float = 0.55) -> list:
        conn = sqlite3.connect(self.db.db_path)
        rows = conn.execute("SELECT * FROM learned_patterns WHERE success_rate >= ? ORDER BY success_rate DESC",
                            (min_success_rate,)).fetchall()
        conn.close()
        return rows

    def get_pattern_success_rate(self, name: str) -> float:
        conn = sqlite3.connect(self.db.db_path)
        row = conn.execute("SELECT success_rate FROM learned_patterns WHERE pattern_name = ?", (name,)).fetchone()
        conn.close()
        return row[0] if row else 0.0
