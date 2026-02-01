"""SQLite state persistence for orders, positions, trades, and system state."""
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('leviathan.state')


class StateManager:
    """Persistent state storage using SQLite."""

    def __init__(self, db_path: str = "leviathan_state.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._conn()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY, symbol TEXT NOT NULL, side TEXT NOT NULL,
            qty REAL NOT NULL, order_type TEXT NOT NULL, status TEXT NOT NULL,
            submitted_at TIMESTAMP, filled_at TIMESTAMP, filled_price REAL, metadata TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY, qty REAL NOT NULL, avg_entry_price REAL NOT NULL,
            current_price REAL, unrealized_pnl REAL, entry_date TIMESTAMP,
            last_updated TIMESTAMP, stop_loss REAL, take_profit REAL,
            highest_price_since_entry REAL, time_stop_days INTEGER DEFAULT 5
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL,
            side TEXT NOT NULL, qty REAL NOT NULL, price REAL NOT NULL,
            realized_pnl REAL, executed_at TIMESTAMP, signal_data TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_state (
            key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP,
            equity REAL, buying_power REAL, daily_pnl REAL
        )''')
        conn.commit()
        conn.close()

    def save_order(self, order_data: dict):
        conn = self._conn()
        conn.execute('''INSERT OR REPLACE INTO orders
            (order_id, symbol, side, qty, order_type, status, submitted_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (order_data['order_id'], order_data['symbol'], order_data['side'],
             order_data['qty'], order_data['order_type'], order_data['status'],
             datetime.now().isoformat(), json.dumps(order_data.get('metadata', {}))))
        conn.commit()
        conn.close()

    def get_open_orders(self) -> list:
        conn = self._conn()
        rows = conn.execute("SELECT * FROM orders WHERE status IN ('pending','submitted')").fetchall()
        conn.close()
        return rows

    def save_position(self, symbol: str, qty: float, entry_price: float,
                      stop_loss: float = None, take_profit: float = None):
        conn = self._conn()
        conn.execute('''INSERT OR REPLACE INTO positions
            (symbol, qty, avg_entry_price, entry_date, last_updated,
             stop_loss, take_profit, highest_price_since_entry, time_stop_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (symbol, qty, entry_price, datetime.now().isoformat(),
             datetime.now().isoformat(), stop_loss, take_profit, entry_price, 5))
        conn.commit()
        conn.close()

    def get_trade_info(self, symbol: str) -> dict:
        conn = self._conn()
        row = conn.execute("SELECT * FROM positions WHERE symbol = ?", (symbol,)).fetchone()
        conn.close()
        if not row:
            return {}
        return {
            'symbol': row[0], 'qty': row[1], 'avg_entry_price': row[2],
            'entry_time': datetime.fromisoformat(row[5]) if row[5] else None,
            'stop_loss_price': row[7], 'take_profit_price': row[8],
            'highest_price_since_entry': row[9], 'time_stop_days': row[10],
        }

    def update_highest_price(self, symbol: str, price: float):
        conn = self._conn()
        conn.execute("UPDATE positions SET highest_price_since_entry = ? WHERE symbol = ?",
                     (price, symbol))
        conn.commit()
        conn.close()

    def record_portfolio_snapshot(self, equity: float, buying_power: float, daily_pnl: float):
        conn = self._conn()
        conn.execute("INSERT INTO portfolio_history (timestamp, equity, buying_power, daily_pnl) VALUES (?, ?, ?, ?)",
                     (datetime.now().isoformat(), equity, buying_power, daily_pnl))
        conn.commit()
        conn.close()

    def get_portfolio_history(self, days: int = 7) -> list:
        conn = self._conn()
        rows = conn.execute(
            "SELECT timestamp, equity FROM portfolio_history ORDER BY timestamp DESC LIMIT ?",
            (days * 24,)).fetchall()
        conn.close()
        return [{'timestamp': r[0], 'value': r[1]} for r in reversed(rows)]

    def save_system_state(self, key: str, value):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, ?)",
                     (key, json.dumps(value), datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_system_state(self, key: str):
        conn = self._conn()
        row = conn.execute("SELECT value FROM system_state WHERE key = ?", (key,)).fetchone()
        conn.close()
        return json.loads(row[0]) if row else None

    def log_exit(self, symbol: str, exit_reason: str, exit_price: float, exit_time: datetime):
        conn = self._conn()
        conn.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
        conn.commit()
        conn.close()
        logger.info(f"Position closed: {symbol} @ {exit_price} reason={exit_reason}")
