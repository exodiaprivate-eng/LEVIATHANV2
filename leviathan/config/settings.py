"""
LEVIATHAN Configuration Settings
All application constants and configuration values.
"""

# Account Constraints
STARTING_CAPITAL = 500.0
MIN_TRADE_SIZE = 1.0

# PDT Protection
MAX_DAY_TRADES_PER_WEEK = 3
HOLD_PERIOD_DAYS = 2

# Risk Limits
MAX_POSITION_PCT = 0.30
MAX_DAILY_LOSS_PCT = 0.03
MAX_TOTAL_EXPOSURE_PCT = 0.80
MAX_TRADES_PER_DAY = 50
MIN_POSITION_SIZE = 1.0

# Dynamic Position Sizing Tiers
POSITION_TIERS = {
    'LEARNING': {'base': 0.05, 'max': 0.10, 'min_profit': -999, 'min_trades': 0, 'min_win_rate': 0.0, 'confidence_mult': 0.5},
    'CAUTIOUS': {'base': 0.08, 'max': 0.15, 'min_profit': 0, 'min_trades': 10, 'min_win_rate': 0.45, 'confidence_mult': 0.7},
    'CONFIDENT': {'base': 0.12, 'max': 0.20, 'min_profit': 5, 'min_trades': 25, 'min_win_rate': 0.52, 'confidence_mult': 0.85},
    'AGGRESSIVE': {'base': 0.15, 'max': 0.25, 'min_profit': 15, 'min_trades': 50, 'min_win_rate': 0.55, 'confidence_mult': 1.0},
    'MAXIMUM': {'base': 0.20, 'max': 0.30, 'min_profit': 30, 'min_trades': 100, 'min_win_rate': 0.58, 'confidence_mult': 1.2},
}

# Drawdown Scaling
DRAWDOWN_SCALING = [
    (0.00, 1.00),
    (0.03, 0.85),
    (0.05, 0.70),
    (0.08, 0.50),
    (0.10, 0.30),
    (0.15, 0.10),
]

# Trading Hours (Eastern Time)
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
EXTENDED_OPEN = "04:00"
EXTENDED_CLOSE = "20:00"
MARKET_TIMEZONE = "US/Eastern"

# ML Model Settings
LSTM_SEQUENCE_LENGTH = 20
LSTM_HIDDEN_SIZE = 64
LSTM_NUM_LAYERS = 2
LSTM_DROPOUT = 0.2
TRAIN_WINDOW_DAYS = 252
TEST_WINDOW_DAYS = 21
RETRAIN_FREQUENCY_DAYS = 30

# Signal Weights
TECHNICAL_WEIGHT = 0.40
SENTIMENT_WEIGHT = 0.30
ML_WEIGHT = 0.30

# News Settings
NEWS_LOOKBACK_DAYS = 3
SENTIMENT_DECAY_HALF_LIFE_HOURS = 6.0

# API Rate Limits
ALPACA_REQUESTS_PER_MINUTE = 200
NEWS_REQUESTS_PER_MINUTE = 60

# Alpaca URLs
PAPER_BASE_URL = "https://paper-api.alpaca.markets"
LIVE_BASE_URL = "https://api.alpaca.markets"
DATA_BASE_URL = "https://data.alpaca.markets"

# Database Paths
LEARNING_DB_PATH = "leviathan_learning.db"
STATE_DB_PATH = "leviathan_state.db"

# Learning System
MINIMUM_TRADES_FOR_LEARNING = 5
SELF_ANALYSIS_TIME = "17:00"
PERFORMANCE_DEGRADATION_THRESHOLD = 0.20
AUTO_RETRAIN_LOOKBACK_DAYS = 180

# Backtest Requirements
MIN_SHARPE_RATIO = 1.0
MIN_WIN_RATE = 0.50
MIN_PROFIT_FACTOR = 1.3
MAX_DRAWDOWN = 0.20

# Watchlist - Default symbols to scan
DEFAULT_WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
    'AMD', 'INTC', 'CRM', 'NFLX', 'PYPL', 'SQ', 'SHOP',
    'SPY', 'QQQ', 'IWM', 'DIA',
]

# Crypto Watchlist
DEFAULT_CRYPTO_WATCHLIST = [
    'BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD',
    'AVAX/USD', 'DOT/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD',
]
