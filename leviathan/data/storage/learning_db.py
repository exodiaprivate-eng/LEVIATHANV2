"""Learning database for AI self-improvement - stores trade outcomes, patterns, and analysis."""
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger('leviathan.learning')


class LearningDatabase:
    """Central knowledge store for AI learning from trading experience."""

    def __init__(self, db_path: str = "leviathan_learning.db"):
        self.db_path = Path(db_path)
        self._init_schema()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        conn = self._conn()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trade_outcomes (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL,
            entry_date TIMESTAMP, exit_date TIMESTAMP, entry_price REAL, exit_price REAL,
            position_size_pct REAL, position_size_dollars REAL, side TEXT,
            profit_loss REAL, profit_loss_pct REAL, hold_duration_hours REAL,
            signal_confidence REAL, technical_score REAL, sentiment_score REAL,
            ml_prediction REAL, rsi_at_entry REAL, macd_at_entry REAL,
            bb_position_at_entry REAL, volume_ratio_at_entry REAL,
            vix_at_entry REAL, market_trend TEXT, performance_tier TEXT,
            account_value_at_entry REAL, cumulative_pnl_at_entry REAL,
            strategy_used TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS best_practices (
            id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL,
            condition_key TEXT NOT NULL, optimal_value REAL, confidence_score REAL,
            sample_size INT, avg_outcome REAL, last_updated TIMESTAMP,
            UNIQUE(category, condition_key)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS strategy_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, strategy_name TEXT NOT NULL,
            market_condition TEXT, time_period TEXT, total_trades INT,
            winning_trades INT, losing_trades INT, total_profit REAL,
            avg_profit_per_trade REAL, sharpe_ratio REAL, max_drawdown REAL,
            last_updated TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS learned_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pattern_name TEXT,
            pattern_description TEXT, indicator_conditions TEXT,
            success_rate REAL, avg_profit_when_followed REAL,
            avg_loss_when_ignored REAL, occurrences INT,
            last_seen TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS self_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT, analysis_date TIMESTAMP,
            period_analyzed TEXT, performance_summary TEXT,
            identified_issues TEXT, proposed_adjustments TEXT,
            llm_reasoning TEXT, adjustments_applied BOOLEAN DEFAULT FALSE,
            outcome_after_adjustment REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS training_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_type TEXT,
            trigger_reason TEXT, data_start_date TIMESTAMP, data_end_date TIMESTAMP,
            records_used INT, model_type TEXT, previous_metrics TEXT,
            new_metrics TEXT, improvement_pct REAL, model_path TEXT,
            approved BOOLEAN DEFAULT FALSE, deployed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS opus_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP,
            symbol TEXT, ml_signal TEXT, decision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS position_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, position_pct REAL,
            confidence REAL, win_rate REAL, drawdown REAL,
            profit_loss REAL, timestamp TIMESTAMP
        )''')
        conn.commit()
        conn.close()

    def record_trade_outcome(self, trade_data: dict):
        conn = self._conn()
        fields = [
            'symbol', 'entry_date', 'exit_date', 'entry_price', 'exit_price',
            'position_size_pct', 'position_size_dollars', 'side', 'profit_loss',
            'profit_loss_pct', 'hold_duration_hours', 'signal_confidence',
            'technical_score', 'sentiment_score', 'ml_prediction', 'rsi_at_entry',
            'macd_at_entry', 'bb_position_at_entry', 'volume_ratio_at_entry',
            'vix_at_entry', 'market_trend', 'performance_tier',
            'account_value_at_entry', 'cumulative_pnl_at_entry', 'strategy_used', 'notes',
        ]
        placeholders = ', '.join(['?'] * len(fields))
        cols = ', '.join(fields)
        values = tuple(trade_data.get(f) for f in fields)
        conn.execute(f"INSERT INTO trade_outcomes ({cols}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        self._update_best_practices()

    def query_best_position_size(self, confidence: float, win_rate: float,
                                  drawdown: float) -> float:
        conn = self._conn()
        rows = conn.execute('''SELECT position_size_pct, profit_loss_pct FROM trade_outcomes
            WHERE signal_confidence BETWEEN ? AND ? AND profit_loss_pct > -0.10
            ORDER BY profit_loss_pct DESC LIMIT 100''',
            (confidence - 0.1, confidence + 0.1)).fetchall()
        conn.close()
        if len(rows) < 10:
            return None
        profitable = [r for r in rows if r[1] > 0]
        return sum(r[0] for r in profitable) / len(profitable) if profitable else None

    def get_strategy_performance(self, strategy_name: str, market_condition: str = None) -> dict:
        conn = self._conn()
        if market_condition:
            row = conn.execute("SELECT * FROM strategy_performance WHERE strategy_name=? AND market_condition=?",
                               (strategy_name, market_condition)).fetchone()
        else:
            row = conn.execute("SELECT * FROM strategy_performance WHERE strategy_name=?",
                               (strategy_name,)).fetchone()
        conn.close()
        return row

    def query_similar_trades(self, symbol: str = None, signal_confidence: float = 0.5,
                             technical_score: float = 0, limit: int = 5) -> list:
        conn = self._conn()
        rows = conn.execute('''SELECT * FROM trade_outcomes
            WHERE signal_confidence BETWEEN ? AND ?
            ORDER BY created_at DESC LIMIT ?''',
            (signal_confidence - 0.15, signal_confidence + 0.15, limit)).fetchall()
        conn.close()
        cols = ['trade_id', 'symbol', 'entry_date', 'exit_date', 'entry_price', 'exit_price',
                'position_size_pct', 'position_size_dollars', 'side', 'profit_loss', 'profit_loss_pct']
        return [{cols[i]: row[i] for i in range(min(len(cols), len(row)))} for row in rows]

    def log_opus_decision(self, timestamp, symbol, ml_signal, decision):
        conn = self._conn()
        conn.execute("INSERT INTO opus_decisions (timestamp, symbol, ml_signal, decision) VALUES (?, ?, ?, ?)",
                     (timestamp.isoformat(), symbol, json.dumps(ml_signal), json.dumps(decision)))
        conn.commit()
        conn.close()

    def get_performance_stats(self) -> dict:
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) FROM trade_outcomes").fetchone()[0]
        wins = conn.execute("SELECT COUNT(*) FROM trade_outcomes WHERE profit_loss > 0").fetchone()[0]
        total_pnl = conn.execute("SELECT COALESCE(SUM(profit_loss), 0) FROM trade_outcomes").fetchone()[0]
        decisions = conn.execute("SELECT COUNT(*) FROM opus_decisions").fetchone()[0]
        conn.close()
        return {
            'total_trades': total, 'wins': wins, 'losses': total - wins,
            'win_rate': wins / total if total > 0 else 0,
            'total_return_pct': total_pnl, 'total_decisions': decisions,
            'total_api_cost': decisions * 0.08,
        }

    def get_recent_trades(self, days: int = None, hours: int = None) -> list:
        conn = self._conn()
        if hours:
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        else:
            cutoff = (datetime.now() - timedelta(days=days or 1)).isoformat()
        rows = conn.execute("SELECT * FROM trade_outcomes WHERE entry_date > ? ORDER BY entry_date DESC",
                            (cutoff,)).fetchall()
        conn.close()
        return [{'profit_loss': r[9], 'profit_loss_pct': r[10], 'symbol': r[1]} for r in rows]

    def start_training_session(self, session_type: str, trigger_reason: str) -> int:
        conn = self._conn()
        c = conn.execute("INSERT INTO training_sessions (session_type, trigger_reason, created_at) VALUES (?, ?, ?)",
                         (session_type, trigger_reason, datetime.now().isoformat()))
        conn.commit()
        sid = c.lastrowid
        conn.close()
        return sid

    def complete_training_session(self, session_id: int, records_used: int,
                                   previous_metrics: dict, new_metrics: dict, improvement_pct: float):
        conn = self._conn()
        conn.execute('''UPDATE training_sessions SET records_used=?, previous_metrics=?,
            new_metrics=?, improvement_pct=? WHERE id=?''',
            (records_used, json.dumps(previous_metrics), json.dumps(new_metrics), improvement_pct, session_id))
        conn.commit()
        conn.close()

    def fail_training_session(self, session_id: int, error: str):
        conn = self._conn()
        conn.execute("UPDATE training_sessions SET trigger_reason = trigger_reason || ' ERROR: ' || ? WHERE id=?",
                     (error, session_id))
        conn.commit()
        conn.close()

    def mark_session_deployed(self, session_id: int):
        conn = self._conn()
        conn.execute("UPDATE training_sessions SET deployed=TRUE WHERE id=?", (session_id,))
        conn.commit()
        conn.close()

    def count_historical_trades(self) -> int:
        conn = self._conn()
        count = conn.execute("SELECT COUNT(*) FROM trade_outcomes").fetchone()[0]
        conn.close()
        return count

    def store_historical_trade(self, **kwargs):
        self.record_trade_outcome(kwargs)

    def get_top_patterns(self, by='win_rate', limit=10) -> list:
        conn = self._conn()
        rows = conn.execute(f"SELECT * FROM learned_patterns ORDER BY success_rate DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return rows

    def get_best_entry_conditions(self) -> dict:
        """Analyze winning trades to find optimal entry indicator values."""
        conn = self._conn()
        try:
            # Get average indicator values for profitable trades (last 90 days)
            rows = conn.execute('''
                SELECT
                    AVG(rsi_at_entry) as avg_rsi,
                    AVG(macd_at_entry) as avg_macd,
                    AVG(bb_position_at_entry) as avg_bb,
                    AVG(volume_ratio_at_entry) as avg_vol_ratio,
                    AVG(signal_confidence) as avg_confidence,
                    AVG(technical_score) as avg_tech_score,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) as sample_size,
                    AVG(profit_loss_pct) as avg_return
                FROM trade_outcomes
                WHERE profit_loss > 0
                AND entry_date > datetime('now', '-90 days')
            ''').fetchone()

            if not rows or rows[7] == 0:  # sample_size
                return {}

            result = {
                'optimal_rsi_entry': rows[0],
                'optimal_macd_entry': rows[1],
                'optimal_bb_position': rows[2],
                'optimal_volume_ratio': rows[3],
                'optimal_confidence': rows[4],
                'optimal_technical_score': rows[5],
                'optimal_sentiment_score': rows[6],
                'sample_size': rows[7],
                'avg_winner_return': rows[8],
            }

            # Also get best entry conditions from best_practices table
            bp_rows = conn.execute('''
                SELECT condition_key, optimal_value, confidence_score, sample_size
                FROM best_practices
                WHERE category = 'position_sizing'
                ORDER BY avg_outcome DESC LIMIT 10
            ''').fetchall()

            if bp_rows:
                result['best_practices'] = [
                    {'condition': json.loads(r[0]) if r[0] else {},
                     'optimal_value': r[1], 'confidence': r[2], 'samples': r[3]}
                    for r in bp_rows
                ]

            return {k: v for k, v in result.items() if v is not None}
        except Exception as e:
            logger.error(f"get_best_entry_conditions failed: {e}")
            return {}
        finally:
            conn.close()

    def get_optimal_hold_duration(self) -> float:
        conn = self._conn()
        row = conn.execute("SELECT AVG(hold_duration_hours) FROM trade_outcomes WHERE profit_loss > 0").fetchone()
        conn.close()
        return row[0] if row and row[0] else 72.0

    def get_best_strategy(self) -> str:
        conn = self._conn()
        row = conn.execute("SELECT strategy_name FROM strategy_performance ORDER BY avg_profit_per_trade DESC LIMIT 1").fetchone()
        conn.close()
        return row[0] if row else 'rsi_mean_reversion'

    def analyze_by_market_condition(self) -> dict:
        """Break down trade performance by market condition (bullish/bearish/sideways)."""
        conn = self._conn()
        try:
            rows = conn.execute('''
                SELECT
                    market_trend,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                    AVG(profit_loss_pct) as avg_return,
                    SUM(profit_loss) as total_pnl,
                    AVG(signal_confidence) as avg_confidence,
                    AVG(hold_duration_hours) as avg_hold_hours
                FROM trade_outcomes
                WHERE market_trend IS NOT NULL
                GROUP BY market_trend
                ORDER BY total_pnl DESC
            ''').fetchall()

            if not rows:
                return {}

            result = {}
            for row in rows:
                trend = row[0] or 'unknown'
                total = row[1]
                wins = row[2]
                result[trend] = {
                    'total_trades': total,
                    'wins': wins,
                    'losses': total - wins,
                    'win_rate': wins / total if total > 0 else 0,
                    'avg_return_pct': row[3],
                    'total_pnl': row[4],
                    'avg_confidence': row[5],
                    'avg_hold_hours': row[6],
                }
            return result
        except Exception as e:
            logger.error(f"analyze_by_market_condition failed: {e}")
            return {}
        finally:
            conn.close()

    def record_position_outcome(self, **kwargs):
        conn = self._conn()
        conn.execute("INSERT INTO position_outcomes (position_pct, confidence, win_rate, drawdown, profit_loss, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                     (kwargs.get('position_pct'), kwargs.get('confidence'), kwargs.get('win_rate'),
                      kwargs.get('drawdown'), kwargs.get('profit_loss'), kwargs.get('timestamp', datetime.now()).isoformat()))
        conn.commit()
        conn.close()

    def _update_best_practices(self):
        try:
            conn = self._conn()
            rows = conn.execute('''SELECT ROUND(signal_confidence, 1) as cb,
                AVG(CASE WHEN profit_loss > 0 THEN position_size_pct END) as ws,
                COUNT(*) as ss, AVG(profit_loss_pct) as ao
                FROM trade_outcomes WHERE entry_date > datetime('now', '-90 days')
                GROUP BY ROUND(signal_confidence, 1) HAVING COUNT(*) >= 5''').fetchall()
            for row in rows:
                cb, ws, ss, ao = row
                if ws:
                    conn.execute('''INSERT OR REPLACE INTO best_practices
                        (category, condition_key, optimal_value, confidence_score, sample_size, avg_outcome, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        ('position_sizing', json.dumps({'confidence_bucket': cb}),
                         ws, min(ss / 50, 1.0), ss, ao, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Best practices update failed: {e}")
