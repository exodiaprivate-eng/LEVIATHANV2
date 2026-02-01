# LEVIATHAN: AI-Powered Swing Trading Platform

## Project Overview

You are building **Leviathan**, an AI-powered automated trading application that integrates with the Alpaca brokerage API. The system executes swing trades on a weekly basis (2-5 day holds) to avoid Pattern Day Trader restrictions. The user has $500+ starting capital and runs Windows 11 Pro.

**Primary Constraints:**
- Never execute same-day buy/sell (triggers PDT violation)
- Maximum 3 day trades per rolling 5-day window as safety buffer
- All trading logic must respect current buying power
- Paper trading must be fully functional before any live code is written

---

## Recommended Agent Structure

For efficient parallel development, organize work across **8 specialized agents**:

### Agent 1: Data Infrastructure
**Responsibility:** Historical data acquisition, storage, and real-time streaming
- Build data ingestion from Alpaca API and backup sources
- Implement Parquet storage for historical OHLCV
- Create Redis caching layer for real-time data
- Handle WebSocket connections for live price feeds
- Implement economic calendar integration
- Implement earnings calendar integration

### Agent 2: ML Pipeline
**Responsibility:** Feature engineering, model training, and prediction
- Engineer technical indicators (RSI, MACD, Bollinger Bands, ATR)
- Implement LSTM, N-BEATS, and LightGBM models
- Build walk-forward validation framework
- Create model serialization and loading system
- Multi-timeframe analysis module

### Agent 3: Sentiment Analysis
**Responsibility:** News and social media sentiment processing
- Integrate FinBERT for financial text classification
- Connect news APIs (Finnhub, Alpha Vantage)
- Build sentiment scoring and decay functions
- Create sentiment aggregation pipeline

### Agent 4: Trading Engine
**Responsibility:** Strategy execution, order management, and Alpaca integration
- Build Alpaca API adapter (REST + WebSocket)
- Implement order types (market, limit, stop, bracket)
- Create position tracking and P&L calculation
- Handle order state management and fills
- Implement slippage estimator
- Build autonomous executor

### Agent 5: Risk Management & Orchestration
**Responsibility:** Risk controls, system coordination, and state management
- Implement circuit breakers and daily loss limits
- Build PDT tracking and prevention
- Create state persistence and crash recovery
- Coordinate message passing between all modules
- Portfolio correlation analysis
- Market regime detection

### Agent 6: Learning & Self-Improvement System
**Responsibility:** Database, self-analysis, automatic training, and adaptation
- Build the learning database (trade outcomes, best practices, patterns)
- Implement Opus brain integration (decision making, exit management)
- Create automatic training triggers and retraining pipeline
- Build dynamic position sizing based on performance tiers
- Implement historical data training system
- Create manual training interface for human intervention

### Agent 7: GUI & User Interface (Split into 7A + 7B for parallel development)

**The GUI uses PyWebView + HTML/CSS/JavaScript to match the Figma design exactly.**

**Design Reference:**
- Figma: https://www.figma.com/community/file/1522238618706669989/dark-finance-crypto-dashboard-ui-design
- Prototype: https://www.figma.com/proto/zh1yF465p1YnQ4JGmtcXtQ/...

#### Agent 7A: Frontend Developer (HTML/CSS/JS)
**Responsibility:** Build the web-based UI that runs inside PyWebView
- Create index.html main dashboard matching Figma design
- Implement Tailwind CSS configuration with exact color palette
- Build reusable CSS components (cards, buttons, badges, inputs)
- Implement JavaScript application logic (app.js)
- Create Python bridge wrapper (api.js) for pywebview.api calls
- Configure ApexCharts for portfolio performance graphs
- Build all HTML pages: training.html, settings.html, crypto_swap.html, analytics.html
- Create SVG icons for sidebar navigation
- Implement CSS animations (pulse, hover effects, transitions)
- Ensure responsive layout and proper styling

#### Agent 7B: Python Backend for GUI (PyWebView + API)
**Responsibility:** Python side of the desktop application
- Build PyWebView app launcher (gui/app.py)
- Implement LeviathanAPI class (gui/api.py) with all JS-callable methods
- Create start_trading() / stop_trading() methods
- Implement get_dashboard_data() returning all portfolio/position data
- Build activity logging system for frontend display
- Create window management for modals (settings, training, etc.)
- Handle background trading thread management
- Implement real-time data refresh for frontend polling

### Agent 8: Extended Features
**Responsibility:** Crypto, options, notifications, reports, and compliance
- Build cryptocurrency trading module (24/7, PDT-exempt)
- Implement options trading module (spreads, iron condors)
- Create notification system (email, desktop)
- Build PDF report generator
- Implement wash sale tracker for tax compliance
- Create backup and recovery system
- Build watchlist management

**Parallel Execution Strategy:**
- Agents 1, 2, 3 can work simultaneously (no dependencies on each other initially)
- Agent 4 depends on Agent 1 completing data infrastructure
- Agent 5 integrates all components and should begin after Agents 1-4 have core functionality
- Agent 6 can start in parallel with Agents 2-3, but needs Agent 5's state management for full integration
- Agent 7A (Frontend) can start immediately - only needs the Figma design reference
- Agent 7B (Python Backend) should start once Agent 5 has basic orchestration working
- Agent 7A and 7B work in parallel, integrate when both have core functionality
- Agent 8 can work independently on extended features, integrates last

**Estimated Time Savings:** 
- Sequential development: 14-16 weeks
- 9-agent parallel development (7 split into 7A+7B): 4-5 weeks

---

## Technology Stack

Use these specific technologies. Do not substitute without explicit approval.

```
Language:           Python 3.11+
ML Framework:       PyTorch 2.x + LightGBM
Data Processing:    Polars (primary), Pandas (ML compatibility)
Technical Analysis: pandas-ta (primary), TA-Lib (candlestick patterns)
Backtesting:        VectorBT
Sentiment:          transformers (HuggingFace) + ProsusAI/finbert
Brokerage API:      alpaca-py (official SDK)
Database:           SQLite (state), Parquet files (historical), Redis (cache)
Async:              asyncio + aiohttp
GUI Framework:      PyWebView + HTML/CSS/JavaScript (Tailwind CSS + ApexCharts)
Environment:        Native Windows 11 (fallback to WSL2 if package issues)
Package Manager:    pip or uv
```

**Installation Command:**
```bash
pip install alpaca-py torch lightgbm polars pandas pandas-ta vectorbt transformers redis aiohttp sqlalchemy anthropic pywebview python-dotenv schedule reportlab win10toast cryptography
```

**Optional for enhanced features:**
```bash
# For TA-Lib candlestick patterns (Windows wheel required)
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl

# For PDF reports
pip install reportlab pillow

# For desktop notifications on Windows
pip install win10toast

# For encrypted credential storage
pip install cryptography keyring
```

**Required API Keys (store in .env file):**
```
# Required
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ANTHROPIC_API_KEY=your_anthropic_key_for_opus

# Optional (for enhanced features)
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key

# Email notifications (optional)
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Live trading (DO NOT SET unless ready)
# LEVIATHAN_LIVE=true
```

For TA-Lib on Windows (optional, for candlestick patterns):
```bash
# Download wheel from https://github.com/cgohlke/talib-build/releases
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

---

## Directory Structure

Create this exact structure:

```
leviathan/
├── config/
│   ├── settings.py          # All configuration constants
│   ├── credentials.py       # API keys (gitignored)
│   ├── logging_config.py    # Logging setup
│   └── llm_config.py        # LLM usage settings and budgets
├── data/
│   ├── ingestion/
│   │   ├── alpaca_client.py     # Alpaca data fetching
│   │   ├── news_client.py       # News API integration
│   │   └── websocket_stream.py  # Real-time data streaming
│   ├── storage/
│   │   ├── parquet_manager.py   # Historical data storage
│   │   ├── redis_cache.py       # Real-time caching
│   │   ├── state_db.py          # SQLite state persistence
│   │   └── learning_db.py       # Learning database for AI memory
│   ├── features/
│   │   ├── technical.py         # Technical indicator calculation
│   │   └── sentiment.py         # Sentiment feature engineering
│   ├── fetcher/
│   │   └── auto_fetcher.py      # Automatic data fetching for learning
│   ├── economic_calendar.py     # Economic events tracking
│   └── earnings_calendar.py     # Earnings dates tracking
├── models/
│   ├── lstm_model.py        # LSTM implementation
│   ├── nbeats_model.py      # N-BEATS implementation
│   ├── lgbm_model.py        # LightGBM implementation
│   ├── ensemble.py          # Model combination/stacking
│   ├── saved/               # Saved model weights
│   └── training/
│       ├── trainer.py       # Training loop
│       ├── validation.py    # Walk-forward validation
│       ├── hyperopt.py      # Hyperparameter tuning
│       └── auto_trainer.py  # Automatic retraining system
├── intelligence/
│   ├── opus_brain.py        # Opus 4.5 decision-making brain
│   ├── self_analyzer.py     # AI self-analysis and reasoning
│   ├── regime_detector.py   # Market regime detection
│   ├── llm_reasoner.py      # LLM integration utilities
│   └── pattern_learner.py   # Pattern recognition and storage
├── sentiment/
│   ├── finbert.py           # FinBERT wrapper
│   ├── news_processor.py    # News text processing
│   └── aggregator.py        # Sentiment score aggregation
├── strategy/
│   ├── signals.py           # Signal generation
│   ├── position_sizer.py    # Basic Kelly criterion sizing
│   ├── dynamic_position_sizer.py  # Performance-based dynamic sizing
│   ├── multi_timeframe.py   # Multi-timeframe analysis
│   ├── watchlist.py         # Watchlist management
│   └── filters.py           # Trade filters (volume, spread, etc.)
├── execution/
│   ├── alpaca_adapter.py    # Order submission and management
│   ├── autonomous_executor.py   # Autonomous trade execution
│   ├── order_manager.py     # Order state tracking
│   ├── fill_handler.py      # Fill processing
│   ├── slippage_estimator.py    # Slippage estimation
│   ├── stock_exit_manager.py    # Stock exit rules (stop loss, take profit, time stops)
│   └── options_exit_manager.py  # Options exit rules (DTE, profit targets)
├── risk/
│   ├── risk_manager.py      # Pre-trade risk checks
│   ├── pdt_tracker.py       # Pattern day trader monitoring
│   ├── circuit_breaker.py   # Emergency stop logic
│   ├── portfolio.py         # Portfolio-level risk metrics
│   ├── portfolio_analyzer.py    # Correlation and concentration analysis
│   └── drawdown_scaler.py   # Drawdown-based position scaling
├── portfolio/
│   ├── autopilot.py         # Long-term portfolio autopilot (auto-diversify, rotate)
│   ├── advisor.py           # Opus portfolio advisor integration
│   └── diversification.py   # Diversification templates and strategies
├── crypto/
│   ├── crypto_trader.py     # Cryptocurrency trading module
│   ├── crypto_strategies.py # Crypto-specific strategies
│   ├── swap_optimizer.py    # Multi-hop crypto swap path finder
│   └── portfolio_rebalancer.py  # Crypto portfolio rebalancing

**CLAUDE CODE INSTRUCTIONS FOR CRYPTO MODULE:**
```
When building the crypto/ module, implement these features in order:

1. crypto_trader.py
   - CryptoTrader class: Main interface for crypto operations
   - Methods: buy_crypto(), sell_crypto(), swap_crypto(), get_opportunities()
   - Must integrate with swap_optimizer for crypto-to-crypto swaps
   - 24/7 operation - no market hours checks needed

2. swap_optimizer.py (CRITICAL FEATURE)
   - CryptoSwapOptimizer class: Finds best path between any two cryptos
   - Build a graph of all 56+ trading pairs
   - Use BFS to find shortest path (fewest hops = lowest fees)
   - Methods: find_best_path(), calculate_swap_amount(), execute_swap()
   - Handle multi-hop swaps (e.g., DOGE → USD → ETH requires 2 orders)
   - Wait for each order to fill before proceeding to next hop

3. portfolio_rebalancer.py
   - CryptoPortfolioManager class: Manages multi-crypto holdings
   - Methods: get_holdings(), rebalance_portfolio(), auto_optimize()
   - Uses swap_optimizer to execute rebalancing trades

4. crypto_strategies.py
   - Crypto-specific trading strategies
   - Faster indicators (7-period RSI, faster MACD)
   - Higher volatility tolerance than stocks

KEY IMPLEMENTATION DETAILS:
- Alpaca crypto symbol format: "BTC/USD" (with slash)
- Only 3 order types supported: market, limit, stop_limit
- Only 2 time_in_force options: gtc, ioc
- Minimum order: $1 notional
- Fees: 0.25% taker (use this for calculations)
- No margin, no shorting
```
├── options/
│   ├── options_trader.py    # Options trading module
│   ├── spreads.py           # Credit/debit spread logic
│   ├── greeks.py            # Options Greeks calculations
│   ├── dte_selector.py      # DTE selection for optimal expiration dates
│   └── intelligence.py      # Options Intelligence Engine (IV analysis, flow, max pain)
├── tax/
│   └── wash_sale_tracker.py # Wash sale tracking for taxes
├── notifications/
│   └── notifier.py          # Email/desktop notifications
├── reports/
│   ├── report_generator.py  # PDF report generation
│   └── generated/           # Generated report files
├── backtest/
│   ├── engine.py            # Backtesting engine
│   ├── metrics.py           # Performance metrics
│   └── reports.py           # Backtest report generation
├── core/
│   ├── events.py            # Event definitions
│   ├── message_bus.py       # Inter-module communication
│   ├── orchestrator.py      # Main application loop
│   └── backup_manager.py    # Backup and recovery
├── frontend/                    # Web frontend for PyWebView GUI
│   ├── index.html              # Main dashboard HTML
│   ├── training.html           # Training interface
│   ├── settings.html           # Settings modal
│   ├── crypto_swap.html        # Crypto swap interface
│   ├── analytics.html          # Analytics dashboard
│   ├── css/
│   │   ├── main.css            # Custom styles (colors, typography)
│   │   └── components.css      # Component library
│   ├── js/
│   │   ├── app.js              # Main application logic
│   │   ├── api.js              # Python bridge wrapper
│   │   ├── charts.js           # ApexCharts configurations
│   │   └── components.js       # Reusable UI components
│   └── assets/
│       ├── icons/              # SVG icons for sidebar
│       └── images/             # Logo, backgrounds
├── gui/
│   ├── __init__.py
│   ├── app.py               # PyWebView app launcher
│   ├── api.py               # Python API class for JS bridge
│   └── windows/             # Window manager classes
│       ├── __init__.py
│       ├── main_window.py   # Main dashboard window config
│       └── modal_manager.py # Modal/popup management
├── utils/
│   ├── logging.py           # Logging utilities
│   ├── time_utils.py        # Market hours, timezone handling
│   ├── encryption.py        # API key encryption
│   └── validators.py        # Input validation
├── tests/
│   ├── test_data/
│   ├── test_models/
│   ├── test_execution/
│   ├── test_risk/
│   └── test_learning/       # Tests for learning system
├── logs/                    # Application logs
├── backups/                 # Automatic backups
├── main.py                  # Application entry point (launches GUI)
├── paper_trader.py          # Paper trading runner (CLI mode)
├── backtester.py            # Backtesting runner
├── manual_trainer.py        # Manual training interface CLI
├── requirements.txt
└── .env                     # API keys (gitignored)
```

---

## Alpaca API Integration Specifications

### Authentication Setup

```python
# config/credentials.py (add to .gitignore)
ALPACA_API_KEY = "your_api_key"
ALPACA_SECRET_KEY = "your_secret_key"
ALPACA_PAPER = True  # ALWAYS True until explicitly approved for live

# Base URLs
PAPER_BASE_URL = "https://paper-api.alpaca.markets"
LIVE_BASE_URL = "https://api.alpaca.markets"
DATA_BASE_URL = "https://data.alpaca.markets"
```

### Core Client Implementation

```python
# data/ingestion/alpaca_client.py
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

class AlpacaClient:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        
    def get_account(self):
        """Returns account info including buying_power and daytrade_count"""
        return self.trading_client.get_account()
    
    def get_buying_power(self) -> float:
        """Returns available buying power as float"""
        account = self.get_account()
        return float(account.buying_power)
    
    def get_positions(self):
        """Returns all open positions"""
        return self.trading_client.get_all_positions()
    
    def get_historical_bars(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """Fetch historical daily bars"""
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=days),
            end=datetime.now()
        )
        bars = self.data_client.get_stock_bars(request)
        return bars.df
    
    def submit_market_order(self, symbol: str, qty: float, side: str):
        """Submit market order. Side is 'buy' or 'sell'"""
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        return self.trading_client.submit_order(request)
    
    def submit_bracket_order(self, symbol: str, qty: float, side: str, 
                            take_profit: float, stop_loss: float):
        """Submit bracket order with take-profit and stop-loss"""
        # Implementation here
        pass
```

### WebSocket Streaming

```python
# data/ingestion/websocket_stream.py
from alpaca.data.live import StockDataStream
import asyncio

class MarketDataStream:
    def __init__(self, api_key: str, secret_key: str):
        self.stream = StockDataStream(api_key, secret_key)
        self.callbacks = []
        
    def register_callback(self, callback):
        self.callbacks.append(callback)
        
    async def handle_bar(self, bar):
        """Process incoming bar data"""
        for callback in self.callbacks:
            await callback(bar)
    
    def subscribe(self, symbols: list):
        """Subscribe to real-time bars for symbols"""
        self.stream.subscribe_bars(self.handle_bar, *symbols)
        
    def run(self):
        """Start the stream (blocking)"""
        self.stream.run()
```

### Rate Limits
- Free tier: 200 requests/minute
- Respect rate limits with exponential backoff
- Implement request queuing for burst protection

---

## Machine Learning Specifications

### Feature Engineering

Generate these features for each symbol:

```python
# data/features/technical.py
import pandas_ta as ta

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: DataFrame with columns [open, high, low, close, volume]
    Output: DataFrame with all technical features added
    """
    # Trend Indicators
    df['sma_20'] = ta.sma(df['close'], length=20)
    df['sma_50'] = ta.sma(df['close'], length=50)
    df['ema_12'] = ta.ema(df['close'], length=12)
    df['ema_26'] = ta.ema(df['close'], length=26)
    
    # Momentum Indicators
    df['rsi_14'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    
    # Volatility Indicators
    bbands = ta.bbands(df['close'], length=20, std=2)
    df = pd.concat([df, bbands], axis=1)
    df['atr_14'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    # Volume Indicators
    df['volume_sma_20'] = ta.sma(df['volume'], length=20)
    df['volume_ratio'] = df['volume'] / df['volume_sma_20']
    
    # Price-based Features
    df['returns_1d'] = df['close'].pct_change(1)
    df['returns_5d'] = df['close'].pct_change(5)
    df['returns_20d'] = df['close'].pct_change(20)
    df['high_low_range'] = (df['high'] - df['low']) / df['close']
    
    # Target Variable (for training)
    df['target'] = (df['close'].shift(-5) > df['close']).astype(int)  # 5-day forward return direction
    
    return df.dropna()
```

### Model Implementations

#### LSTM Model
```python
# models/lstm_model.py
import torch
import torch.nn as nn

class LSTMPredictor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, 
                 num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 3)  # Buy, Hold, Sell
        )
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])
```

#### LightGBM Model
```python
# models/lgbm_model.py
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit

class LGBMPredictor:
    def __init__(self):
        self.model = None
        self.params = {
            'objective': 'multiclass',
            'num_class': 3,
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        
    def train(self, X_train, y_train, X_val, y_val):
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=1000,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(50)]
        )
        
    def predict(self, X):
        return self.model.predict(X)
```

#### Ensemble Combination
```python
# models/ensemble.py
class EnsemblePredictor:
    def __init__(self, models: list, weights: list = None):
        self.models = models
        self.weights = weights or [1/len(models)] * len(models)
        
    def predict(self, X):
        predictions = []
        for model, weight in zip(self.models, self.weights):
            pred = model.predict(X)
            predictions.append(pred * weight)
        return sum(predictions)
```

### Walk-Forward Validation

```python
# models/training/validation.py
def walk_forward_validation(model_class, data: pd.DataFrame, 
                           train_window: int = 252,  # 1 year
                           test_window: int = 21,    # 1 month
                           step: int = 21):          # Step 1 month
    """
    CRITICAL: Never use random train/test splits for time series.
    Always use walk-forward to prevent look-ahead bias.
    """
    results = []
    
    for i in range(0, len(data) - train_window - test_window, step):
        train_end = i + train_window
        test_end = train_end + test_window
        
        train_data = data.iloc[i:train_end]
        test_data = data.iloc[train_end:test_end]
        
        model = model_class()
        model.train(train_data)
        
        predictions = model.predict(test_data)
        metrics = calculate_metrics(predictions, test_data['target'])
        results.append(metrics)
        
    return aggregate_results(results)
```

---

## Sentiment Analysis Specifications

### FinBERT Integration

```python
# sentiment/finbert.py
from transformers import BertForSequenceClassification, BertTokenizer, pipeline
import torch

class FinBERTAnalyzer:
    def __init__(self):
        self.model = BertForSequenceClassification.from_pretrained(
            'ProsusAI/finbert', 
            num_labels=3
        )
        self.tokenizer = BertTokenizer.from_pretrained('ProsusAI/finbert')
        self.pipeline = pipeline(
            "sentiment-analysis", 
            model=self.model, 
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
    def analyze(self, texts: list) -> list:
        """
        Returns list of dicts with 'label' and 'score'
        Labels: positive, negative, neutral
        """
        results = self.pipeline(texts, truncation=True, max_length=512)
        return results
    
    def get_sentiment_score(self, text: str) -> float:
        """
        Returns single float: -1 (negative) to +1 (positive)
        """
        result = self.analyze([text])[0]
        if result['label'] == 'positive':
            return result['score']
        elif result['label'] == 'negative':
            return -result['score']
        return 0.0
```

### News API Integration

```python
# data/ingestion/news_client.py
import aiohttp
from datetime import datetime, timedelta

class NewsClient:
    def __init__(self, finnhub_key: str):
        self.finnhub_key = finnhub_key
        self.base_url = "https://finnhub.io/api/v1"
        
    async def get_company_news(self, symbol: str, days: int = 7) -> list:
        """Fetch recent news for a symbol"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/company-news"
        params = {
            'symbol': symbol,
            'from': start_date,
            'to': end_date,
            'token': self.finnhub_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()
```

### Sentiment Decay Function

```python
# sentiment/aggregator.py
import math
from datetime import datetime

def apply_sentiment_decay(sentiment_score: float, 
                         published_time: datetime,
                         half_life_hours: float = 6.0) -> float:
    """
    Apply exponential decay to sentiment scores.
    News older than ~24 hours has minimal impact.
    """
    hours_old = (datetime.now() - published_time).total_seconds() / 3600
    decay_factor = math.exp(-0.693 * hours_old / half_life_hours)
    return sentiment_score * decay_factor

def aggregate_sentiment(news_items: list, analyzer: FinBERTAnalyzer) -> float:
    """
    Aggregate multiple news items into single sentiment score.
    """
    if not news_items:
        return 0.0
        
    weighted_scores = []
    for item in news_items:
        score = analyzer.get_sentiment_score(item['headline'])
        published = datetime.fromtimestamp(item['datetime'])
        decayed_score = apply_sentiment_decay(score, published)
        weighted_scores.append(decayed_score)
        
    return sum(weighted_scores) / len(weighted_scores)
```

---

## Risk Management Specifications

### Core Risk Manager

```python
# risk/risk_manager.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class RiskLimits:
    max_position_pct: float = 0.20      # Max 20% in single position
    max_daily_loss_pct: float = 0.03    # Stop trading at 3% daily loss
    max_total_exposure_pct: float = 0.80 # Max 80% capital deployed
    max_trades_per_day: int = 50
    min_position_size: float = 1.0      # Minimum $1 position

class RiskManager:
    def __init__(self, account_value: float, limits: RiskLimits = None):
        self.account_value = account_value
        self.limits = limits or RiskLimits()
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.circuit_breaker_active = False
        
    def update_account_value(self, new_value: float):
        self.account_value = new_value
        
    def record_trade(self, pnl: float):
        self.daily_pnl += pnl
        self.trades_today += 1
        self._check_circuit_breaker()
        
    def _check_circuit_breaker(self):
        if self.daily_pnl <= -self.account_value * self.limits.max_daily_loss_pct:
            self.circuit_breaker_active = True
            
    def reset_daily(self):
        """Call at market open each day"""
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.circuit_breaker_active = False
        
    def pre_trade_check(self, order) -> tuple[bool, Optional[str]]:
        """
        Returns (approved: bool, rejection_reason: str or None)
        """
        if self.circuit_breaker_active:
            return False, "Circuit breaker active - daily loss limit reached"
            
        if self.trades_today >= self.limits.max_trades_per_day:
            return False, f"Max daily trades ({self.limits.max_trades_per_day}) reached"
            
        position_value = order.qty * order.price
        if position_value > self.account_value * self.limits.max_position_pct:
            return False, f"Position exceeds {self.limits.max_position_pct*100}% limit"
            
        if position_value < self.limits.min_position_size:
            return False, f"Position below minimum ${self.limits.min_position_size}"
            
        return True, None
```

### PDT Tracker

```python
# risk/pdt_tracker.py
from datetime import datetime, timedelta
from collections import deque

class PDTTracker:
    """
    Tracks day trades to prevent PDT violation.
    A day trade = buying and selling same security same day.
    PDT rule = 4+ day trades in 5 business days on margin account < $25k
    """
    
    def __init__(self, max_day_trades: int = 3):  # Use 3 for safety buffer
        self.max_day_trades = max_day_trades
        self.day_trades = deque()  # List of (datetime, symbol) tuples
        
    def _clean_old_trades(self):
        """Remove day trades older than 5 business days"""
        cutoff = datetime.now() - timedelta(days=7)  # 7 calendar days ≈ 5 business
        while self.day_trades and self.day_trades[0][0] < cutoff:
            self.day_trades.popleft()
            
    def record_day_trade(self, symbol: str):
        self._clean_old_trades()
        self.day_trades.append((datetime.now(), symbol))
        
    def get_day_trade_count(self) -> int:
        self._clean_old_trades()
        return len(self.day_trades)
        
    def can_day_trade(self) -> bool:
        """Returns True if another day trade is allowed"""
        return self.get_day_trade_count() < self.max_day_trades
        
    def would_be_day_trade(self, symbol: str, positions: dict) -> bool:
        """
        Check if selling this symbol today would constitute a day trade.
        positions = dict of {symbol: purchase_date}
        """
        if symbol not in positions:
            return False
        purchase_date = positions[symbol]
        return purchase_date.date() == datetime.now().date()
```

### Position Sizing (Kelly Criterion)

```python
# strategy/position_sizer.py

def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Calculate optimal position size using Kelly Criterion.
    Returns fraction of capital to risk.
    
    Formula: K = W - (1-W)/R
    Where: W = win rate, R = win/loss ratio
    """
    if avg_loss == 0:
        return 0
    win_loss_ratio = avg_win / avg_loss
    kelly = win_rate - (1 - win_rate) / win_loss_ratio
    return max(0, kelly)

def calculate_position_size(account_value: float, 
                           signal_confidence: float,
                           win_rate: float = 0.55,
                           avg_win: float = 0.03,
                           avg_loss: float = 0.02,
                           max_position_pct: float = 0.20) -> float:
    """
    Calculate position size in dollars.
    Uses Half-Kelly for safety, scaled by signal confidence.
    """
    full_kelly = kelly_criterion(win_rate, avg_win, avg_loss)
    half_kelly = full_kelly / 2  # More conservative
    
    # Scale by confidence (0.5 to 1.0 range)
    confidence_multiplier = 0.5 + (signal_confidence * 0.5)
    adjusted_kelly = half_kelly * confidence_multiplier
    
    # Apply maximum position constraint
    position_pct = min(adjusted_kelly, max_position_pct)
    
    return account_value * position_pct

### Dynamic Position Sizing System

**CRITICAL REQUIREMENT:** Position sizing must be entirely dynamic based on performance and confidence. As the AI proves itself profitable, it should automatically scale up risk. As it loses, it should scale down.

```python
# strategy/dynamic_position_sizer.py
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

@dataclass
class PerformanceTier:
    name: str
    min_profit_pct: float      # Cumulative profit threshold
    min_win_rate: float        # Required win rate
    min_trades: int            # Minimum trades to qualify
    base_position_pct: float   # Base position size for this tier
    max_position_pct: float    # Maximum allowed at this tier
    confidence_multiplier: float  # How much confidence affects sizing

class DynamicPositionSizer:
    """
    Automatically adjusts position sizes based on:
    1. Cumulative P&L performance
    2. Recent win rate
    3. Signal confidence
    4. Current drawdown
    5. AI's learned optimal sizing from database
    """
    
    def __init__(self, starting_capital: float, db_connection):
        self.starting_capital = starting_capital
        self.db = db_connection
        
        # Define performance tiers - AI graduates to higher tiers as it proves itself
        self.tiers = [
            PerformanceTier(
                name="LEARNING",
                min_profit_pct=-999,  # Default starting tier
                min_win_rate=0.0,
                min_trades=0,
                base_position_pct=0.05,   # 5% positions while learning
                max_position_pct=0.10,
                confidence_multiplier=0.5
            ),
            PerformanceTier(
                name="CAUTIOUS",
                min_profit_pct=0.0,   # Must be profitable
                min_win_rate=0.45,
                min_trades=10,
                base_position_pct=0.08,
                max_position_pct=0.15,
                confidence_multiplier=0.7
            ),
            PerformanceTier(
                name="CONFIDENT",
                min_profit_pct=5.0,   # 5% cumulative profit
                min_win_rate=0.52,
                min_trades=25,
                base_position_pct=0.12,
                max_position_pct=0.20,
                confidence_multiplier=0.85
            ),
            PerformanceTier(
                name="AGGRESSIVE",
                min_profit_pct=15.0,  # 15% cumulative profit
                min_win_rate=0.55,
                min_trades=50,
                base_position_pct=0.15,
                max_position_pct=0.25,
                confidence_multiplier=1.0
            ),
            PerformanceTier(
                name="MAXIMUM",
                min_profit_pct=30.0,  # 30% cumulative profit
                min_win_rate=0.58,
                min_trades=100,
                base_position_pct=0.20,
                max_position_pct=0.30,
                confidence_multiplier=1.2
            )
        ]
        
    def get_current_tier(self, performance_stats: dict) -> PerformanceTier:
        """Determine which tier the AI currently qualifies for"""
        current_tier = self.tiers[0]  # Default to LEARNING
        
        for tier in self.tiers:
            if (performance_stats['cumulative_profit_pct'] >= tier.min_profit_pct and
                performance_stats['win_rate'] >= tier.min_win_rate and
                performance_stats['total_trades'] >= tier.min_trades):
                current_tier = tier
                
        return current_tier
    
    def calculate_dynamic_size(self, 
                               account_value: float,
                               signal_confidence: float,
                               performance_stats: dict,
                               current_drawdown_pct: float) -> dict:
        """
        Calculate position size with full dynamic adjustment.
        
        Returns dict with:
        - position_pct: Percentage of account to use
        - position_dollars: Dollar amount
        - tier: Current performance tier
        - reasoning: Explanation of sizing decision
        """
        tier = self.get_current_tier(performance_stats)
        
        # Start with base position for this tier
        base_pct = tier.base_position_pct
        
        # Adjust for signal confidence
        confidence_adjustment = signal_confidence * tier.confidence_multiplier
        adjusted_pct = base_pct * (0.5 + confidence_adjustment)
        
        # Scale DOWN if in drawdown (protect capital)
        if current_drawdown_pct > 5:
            drawdown_multiplier = max(0.3, 1 - (current_drawdown_pct / 20))
            adjusted_pct *= drawdown_multiplier
            
        # Scale UP if on a winning streak (let winners run)
        recent_wins = performance_stats.get('last_5_trades_wins', 0)
        if recent_wins >= 4:
            adjusted_pct *= 1.2  # 20% boost on hot streak
            
        # Query database for historically optimal sizing for similar conditions
        historical_optimal = self._get_historical_optimal_size(
            signal_confidence, 
            performance_stats['win_rate'],
            current_drawdown_pct
        )
        if historical_optimal:
            # Blend current calculation with historical best practice
            adjusted_pct = (adjusted_pct * 0.7) + (historical_optimal * 0.3)
        
        # Apply tier maximum
        final_pct = min(adjusted_pct, tier.max_position_pct)
        
        # Never go below minimum viable position
        final_pct = max(final_pct, 0.02)  # 2% minimum
        
        return {
            'position_pct': final_pct,
            'position_dollars': account_value * final_pct,
            'tier': tier.name,
            'reasoning': f"Tier={tier.name}, Base={base_pct:.1%}, Confidence={signal_confidence:.2f}, "
                        f"Drawdown={current_drawdown_pct:.1f}%, Final={final_pct:.1%}"
        }
    
    def _get_historical_optimal_size(self, confidence: float, win_rate: float, 
                                     drawdown: float) -> float:
        """Query learning database for historically best position sizes"""
        # Round to buckets for database lookup
        conf_bucket = round(confidence, 1)
        wr_bucket = round(win_rate, 1)
        dd_bucket = round(drawdown / 5) * 5  # 5% buckets
        
        result = self.db.query_best_position_size(conf_bucket, wr_bucket, dd_bucket)
        return result if result else None
    
    def record_outcome(self, position_pct: float, signal_confidence: float,
                       win_rate: float, drawdown: float, trade_result: float):
        """Record trade outcome for learning - called after every trade"""
        self.db.record_position_outcome(
            position_pct=position_pct,
            confidence=signal_confidence,
            win_rate=win_rate,
            drawdown=drawdown,
            profit_loss=trade_result,
            timestamp=datetime.now()
        )
```

### Drawdown-Based Scaling

```python
# risk/drawdown_scaler.py

class DrawdownScaler:
    """
    Automatically reduces position sizes during drawdowns,
    increases during equity growth periods.
    """
    
    def __init__(self):
        self.high_water_mark = 0
        self.scaling_rules = [
            # (drawdown_threshold, position_multiplier)
            (0.00, 1.00),   # No drawdown = full size
            (0.03, 0.85),   # 3% drawdown = 85% size
            (0.05, 0.70),   # 5% drawdown = 70% size
            (0.08, 0.50),   # 8% drawdown = 50% size
            (0.10, 0.30),   # 10% drawdown = 30% size
            (0.15, 0.10),   # 15% drawdown = minimal trading
        ]
        
    def update_high_water_mark(self, current_equity: float):
        self.high_water_mark = max(self.high_water_mark, current_equity)
        
    def get_current_drawdown(self, current_equity: float) -> float:
        if self.high_water_mark == 0:
            return 0
        return (self.high_water_mark - current_equity) / self.high_water_mark
        
    def get_position_multiplier(self, current_equity: float) -> float:
        drawdown = self.get_current_drawdown(current_equity)
        
        for threshold, multiplier in reversed(self.scaling_rules):
            if drawdown >= threshold:
                return multiplier
        return 1.0
```
```

---

## Signal Generation Specifications

### Combined Signal Logic

```python
# strategy/signals.py
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2

@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    confidence: float  # 0.0 to 1.0
    technical_score: float
    sentiment_score: float
    ml_prediction: float
    reasoning: str

class SignalGenerator:
    def __init__(self, technical_weight: float = 0.4,
                 sentiment_weight: float = 0.3,
                 ml_weight: float = 0.3):
        self.weights = {
            'technical': technical_weight,
            'sentiment': sentiment_weight,
            'ml': ml_weight
        }
        
    def generate_signal(self, symbol: str,
                       technical_indicators: dict,
                       sentiment_score: float,
                       ml_prediction: float) -> TradingSignal:
        """
        Combine all inputs into a single trading signal.
        
        technical_indicators: dict with rsi, macd, bb_position, etc.
        sentiment_score: -1 to +1
        ml_prediction: probability of price increase (0 to 1)
        """
        # Calculate technical score (-1 to +1)
        tech_score = self._calculate_technical_score(technical_indicators)
        
        # Normalize ML prediction to -1 to +1 scale
        ml_score = (ml_prediction - 0.5) * 2
        
        # Weighted combination
        combined_score = (
            tech_score * self.weights['technical'] +
            sentiment_score * self.weights['sentiment'] +
            ml_score * self.weights['ml']
        )
        
        # Determine signal type and confidence
        signal_type, confidence = self._score_to_signal(combined_score)
        
        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence,
            technical_score=tech_score,
            sentiment_score=sentiment_score,
            ml_prediction=ml_prediction,
            reasoning=self._generate_reasoning(technical_indicators, sentiment_score, ml_prediction)
        )
        
    def _calculate_technical_score(self, indicators: dict) -> float:
        """Convert technical indicators to -1 to +1 score"""
        score = 0.0
        
        # RSI component
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            score += 0.3  # Oversold = bullish
        elif rsi > 70:
            score -= 0.3  # Overbought = bearish
            
        # MACD component
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            score += 0.3
        else:
            score -= 0.3
            
        # Moving average component
        price = indicators.get('close', 0)
        sma_50 = indicators.get('sma_50', price)
        if price > sma_50:
            score += 0.2
        else:
            score -= 0.2
            
        # Bollinger Band position
        bb_lower = indicators.get('bb_lower', price)
        bb_upper = indicators.get('bb_upper', price)
        if price < bb_lower:
            score += 0.2  # Below lower band = potential bounce
        elif price > bb_upper:
            score -= 0.2  # Above upper band = potential pullback
            
        return max(-1, min(1, score))  # Clamp to [-1, 1]
        
    def _score_to_signal(self, score: float) -> tuple[SignalType, float]:
        """Convert combined score to signal type and confidence"""
        confidence = abs(score)
        
        if score >= 0.6:
            return SignalType.STRONG_BUY, confidence
        elif score >= 0.2:
            return SignalType.BUY, confidence
        elif score <= -0.6:
            return SignalType.STRONG_SELL, confidence
        elif score <= -0.2:
            return SignalType.SELL, confidence
        else:
            return SignalType.HOLD, confidence
```

---

## State Management Specifications

### SQLite State Persistence

```python
# data/storage/state_db.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class StateManager:
    def __init__(self, db_path: str = "leviathan_state.db"):
        self.db_path = Path(db_path)
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                order_type TEXT NOT NULL,
                status TEXT NOT NULL,
                submitted_at TIMESTAMP,
                filled_at TIMESTAMP,
                filled_price REAL,
                metadata TEXT
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                qty REAL NOT NULL,
                avg_entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL,
                entry_date TIMESTAMP,
                last_updated TIMESTAMP
            )
        ''')
        
        # Trades table (for P&L tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL,
                realized_pnl REAL,
                executed_at TIMESTAMP,
                signal_data TEXT
            )
        ''')
        
        # System state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_order(self, order_data: dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (order_id, symbol, side, qty, order_type, status, submitted_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['order_id'],
            order_data['symbol'],
            order_data['side'],
            order_data['qty'],
            order_data['order_type'],
            order_data['status'],
            datetime.now().isoformat(),
            json.dumps(order_data.get('metadata', {}))
        ))
        conn.commit()
        conn.close()
        
    def get_open_orders(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE status IN (?, ?)', 
                      ('pending', 'submitted'))
        orders = cursor.fetchall()
        conn.close()
        return orders
        
    def save_system_state(self, key: str, value: any):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO system_state (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, json.dumps(value), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
    def get_system_state(self, key: str) -> any:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM system_state WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return json.loads(result[0]) if result else None

---

## Learning Database & Self-Improvement System

**CRITICAL REQUIREMENT:** The AI must maintain a comprehensive learning database that stores outcomes, best practices, and learned patterns. The system must be capable of:
1. Automatically recording every decision and outcome
2. Querying historical data to inform current decisions
3. Self-analyzing to identify what works and what doesn't
4. Automatic retraining based on new data
5. Manual training intervention when needed
6. "Talking to itself" - using LLM reasoning to analyze its own performance

### Learning Database Schema

```python
# data/storage/learning_db.py
import sqlite3
from datetime import datetime
import json

class LearningDatabase:
    """
    Central knowledge store for the AI to learn from its experiences.
    Records every trade, decision, market condition, and outcome.
    """
    
    def __init__(self, db_path: str = "leviathan_learning.db"):
        self.db_path = db_path
        self._init_schema()
        
    def _init_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trade outcomes - what happened on each trade
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_outcomes (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                entry_date TIMESTAMP,
                exit_date TIMESTAMP,
                entry_price REAL,
                exit_price REAL,
                position_size_pct REAL,
                position_size_dollars REAL,
                side TEXT,
                profit_loss REAL,
                profit_loss_pct REAL,
                hold_duration_hours REAL,
                
                -- Signal data at entry
                signal_confidence REAL,
                technical_score REAL,
                sentiment_score REAL,
                ml_prediction REAL,
                
                -- Market conditions at entry
                rsi_at_entry REAL,
                macd_at_entry REAL,
                bb_position_at_entry REAL,
                volume_ratio_at_entry REAL,
                vix_at_entry REAL,
                market_trend TEXT,  -- 'bull', 'bear', 'sideways'
                
                -- Performance tier at time of trade
                performance_tier TEXT,
                account_value_at_entry REAL,
                cumulative_pnl_at_entry REAL,
                
                -- Metadata
                strategy_used TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Best practices - learned optimal parameters
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS best_practices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,  -- 'position_sizing', 'entry_timing', 'exit_timing', etc.
                condition_key TEXT NOT NULL,  -- JSON of conditions this applies to
                optimal_value REAL,
                confidence_score REAL,  -- How confident we are in this practice
                sample_size INT,  -- Number of trades this is based on
                avg_outcome REAL,  -- Average P&L when following this practice
                last_updated TIMESTAMP,
                UNIQUE(category, condition_key)
            )
        ''')
        
        # Strategy performance - track which strategies work in which conditions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                market_condition TEXT,  -- 'trending_up', 'trending_down', 'ranging', 'volatile'
                time_period TEXT,  -- 'morning', 'midday', 'afternoon', 'week_start', 'week_end'
                total_trades INT,
                winning_trades INT,
                losing_trades INT,
                total_profit REAL,
                avg_profit_per_trade REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                last_updated TIMESTAMP
            )
        ''')
        
        # Pattern recognition - store identified patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                pattern_description TEXT,
                indicator_conditions TEXT,  -- JSON of indicator ranges
                success_rate REAL,
                avg_profit_when_followed REAL,
                avg_loss_when_ignored REAL,
                occurrences INT,
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Self-analysis logs - AI's reasoning about its performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TIMESTAMP,
                period_analyzed TEXT,  -- 'daily', 'weekly', 'monthly'
                performance_summary TEXT,
                identified_issues TEXT,  -- JSON list of problems found
                proposed_adjustments TEXT,  -- JSON list of changes to make
                llm_reasoning TEXT,  -- Full LLM analysis output
                adjustments_applied BOOLEAN DEFAULT FALSE,
                outcome_after_adjustment REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training sessions - manual and automatic
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT,  -- 'automatic', 'manual', 'scheduled'
                trigger_reason TEXT,  -- Why training was triggered
                data_start_date TIMESTAMP,
                data_end_date TIMESTAMP,
                records_used INT,
                model_type TEXT,
                previous_metrics TEXT,  -- JSON of metrics before training
                new_metrics TEXT,  -- JSON of metrics after training
                improvement_pct REAL,
                model_path TEXT,  -- Where the new model is saved
                approved BOOLEAN DEFAULT FALSE,  -- Manual approval for deployment
                deployed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_trade_outcome(self, trade_data: dict):
        """Record complete trade data for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_outcomes (
                symbol, entry_date, exit_date, entry_price, exit_price,
                position_size_pct, position_size_dollars, side, profit_loss, profit_loss_pct,
                hold_duration_hours, signal_confidence, technical_score, sentiment_score,
                ml_prediction, rsi_at_entry, macd_at_entry, bb_position_at_entry,
                volume_ratio_at_entry, vix_at_entry, market_trend, performance_tier,
                account_value_at_entry, cumulative_pnl_at_entry, strategy_used, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['symbol'], trade_data['entry_date'], trade_data['exit_date'],
            trade_data['entry_price'], trade_data['exit_price'], trade_data['position_size_pct'],
            trade_data['position_size_dollars'], trade_data['side'], trade_data['profit_loss'],
            trade_data['profit_loss_pct'], trade_data['hold_duration_hours'],
            trade_data['signal_confidence'], trade_data['technical_score'],
            trade_data['sentiment_score'], trade_data['ml_prediction'],
            trade_data['rsi_at_entry'], trade_data['macd_at_entry'],
            trade_data['bb_position_at_entry'], trade_data['volume_ratio_at_entry'],
            trade_data.get('vix_at_entry'), trade_data.get('market_trend'),
            trade_data['performance_tier'], trade_data['account_value_at_entry'],
            trade_data['cumulative_pnl_at_entry'], trade_data['strategy_used'],
            trade_data.get('notes')
        ))
        
        conn.commit()
        conn.close()
        
        # Trigger learning update
        self._update_best_practices()
        
    def query_best_position_size(self, confidence: float, win_rate: float, 
                                  drawdown: float) -> float:
        """Find historically optimal position size for given conditions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query trades with similar conditions
        cursor.execute('''
            SELECT position_size_pct, profit_loss_pct
            FROM trade_outcomes
            WHERE signal_confidence BETWEEN ? AND ?
            AND profit_loss_pct > -0.10  -- Exclude catastrophic trades
            ORDER BY profit_loss_pct DESC
            LIMIT 100
        ''', (confidence - 0.1, confidence + 0.1))
        
        results = cursor.fetchall()
        conn.close()
        
        if len(results) < 10:
            return None  # Not enough data
            
        # Find position size that maximized returns
        profitable_trades = [r for r in results if r[1] > 0]
        if profitable_trades:
            avg_winning_size = sum(r[0] for r in profitable_trades) / len(profitable_trades)
            return avg_winning_size
        return None
    
    def get_strategy_performance(self, strategy_name: str, 
                                  market_condition: str = None) -> dict:
        """Get historical performance for a strategy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if market_condition:
            cursor.execute('''
                SELECT * FROM strategy_performance 
                WHERE strategy_name = ? AND market_condition = ?
            ''', (strategy_name, market_condition))
        else:
            cursor.execute('''
                SELECT * FROM strategy_performance WHERE strategy_name = ?
            ''', (strategy_name,))
            
        result = cursor.fetchone()
        conn.close()
        return result
    
    def _update_best_practices(self):
        """Automatically update best practices based on recent outcomes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update optimal position sizes by confidence level
        cursor.execute('''
            SELECT 
                ROUND(signal_confidence, 1) as conf_bucket,
                AVG(CASE WHEN profit_loss > 0 THEN position_size_pct END) as winning_size,
                COUNT(*) as sample_size,
                AVG(profit_loss_pct) as avg_outcome
            FROM trade_outcomes
            WHERE entry_date > datetime('now', '-90 days')
            GROUP BY ROUND(signal_confidence, 1)
            HAVING COUNT(*) >= 5
        ''')
        
        for row in cursor.fetchall():
            conf_bucket, winning_size, sample_size, avg_outcome = row
            if winning_size:
                cursor.execute('''
                    INSERT OR REPLACE INTO best_practices 
                    (category, condition_key, optimal_value, confidence_score, sample_size, avg_outcome, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'position_sizing',
                    json.dumps({'confidence_bucket': conf_bucket}),
                    winning_size,
                    min(sample_size / 50, 1.0),  # Confidence based on sample size
                    sample_size,
                    avg_outcome,
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
```

### Self-Analysis System (AI Talks to Itself)

```python
# intelligence/self_analyzer.py
from anthropic import Anthropic
import json
from datetime import datetime, timedelta

class SelfAnalyzer:
    """
    Uses LLM to analyze trading performance and suggest improvements.
    The AI literally reasons about its own behavior and outcomes.
    """
    
    def __init__(self, learning_db: LearningDatabase, anthropic_key: str = None):
        self.db = learning_db
        self.client = Anthropic(api_key=anthropic_key) if anthropic_key else None
        
    def run_daily_analysis(self) -> dict:
        """
        AI analyzes today's performance and suggests adjustments.
        Called automatically at end of each trading day.
        """
        # Gather today's data
        today_trades = self._get_recent_trades(days=1)
        week_trades = self._get_recent_trades(days=7)
        
        if not today_trades:
            return {"status": "no_trades", "analysis": None}
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(today_trades, week_trades)
        
        # AI reasons about its performance
        if self.client:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",  # Use Sonnet for cost efficiency
                max_tokens=2000,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            llm_analysis = response.content[0].text
        else:
            llm_analysis = self._rule_based_analysis(today_trades, week_trades)
        
        # Parse and store analysis
        analysis_result = self._parse_analysis(llm_analysis)
        self._store_analysis(analysis_result)
        
        return analysis_result
    
    def _build_analysis_prompt(self, today_trades: list, week_trades: list) -> str:
        """Build prompt for self-analysis"""
        
        today_summary = self._summarize_trades(today_trades)
        week_summary = self._summarize_trades(week_trades)
        
        return f"""You are analyzing your own trading performance as an AI trading system called Leviathan.

TODAY'S PERFORMANCE:
{json.dumps(today_summary, indent=2)}

THIS WEEK'S PERFORMANCE:
{json.dumps(week_summary, indent=2)}

RECENT TRADE DETAILS:
{json.dumps([self._trade_to_dict(t) for t in today_trades[-10:]], indent=2)}

Analyze your performance and respond with a JSON object containing:
1. "performance_assessment": Brief assessment of today (1-2 sentences)
2. "identified_issues": List of specific problems you notice (be honest and critical)
3. "what_worked": List of things that went well
4. "proposed_adjustments": List of specific parameter changes to make
5. "confidence_adjustment": Should you trade more aggressively, less aggressively, or stay the same? (-1, 0, or 1)
6. "reasoning": Your detailed reasoning process

Be specific. Don't give vague advice. If RSI entries at 32 lost money but entries at 28 made money, say that specifically.

Respond ONLY with valid JSON."""

    def _rule_based_analysis(self, today_trades: list, week_trades: list) -> str:
        """Fallback analysis without LLM"""
        issues = []
        adjustments = []
        
        # Analyze win rate
        wins = sum(1 for t in week_trades if t['profit_loss'] > 0)
        win_rate = wins / len(week_trades) if week_trades else 0
        
        if win_rate < 0.45:
            issues.append("Win rate below 45% - signals may be too aggressive")
            adjustments.append("Increase signal confidence threshold from 0.6 to 0.7")
            
        # Analyze average loss vs average win
        avg_win = sum(t['profit_loss'] for t in week_trades if t['profit_loss'] > 0) / max(wins, 1)
        losses = [t for t in week_trades if t['profit_loss'] < 0]
        avg_loss = sum(t['profit_loss'] for t in losses) / max(len(losses), 1)
        
        if abs(avg_loss) > avg_win:
            issues.append(f"Average loss (${abs(avg_loss):.2f}) exceeds average win (${avg_win:.2f})")
            adjustments.append("Tighten stop losses by 0.5%")
            
        return json.dumps({
            "performance_assessment": f"Win rate: {win_rate:.1%}, Avg win: ${avg_win:.2f}, Avg loss: ${avg_loss:.2f}",
            "identified_issues": issues,
            "what_worked": [],
            "proposed_adjustments": adjustments,
            "confidence_adjustment": -1 if win_rate < 0.45 else 0,
            "reasoning": "Rule-based analysis (no LLM available)"
        })
    
    def apply_learned_adjustments(self, strategy_config: dict) -> dict:
        """
        Apply learned improvements to strategy configuration.
        Called before each trading session.
        """
        # Get most recent successful analysis
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT proposed_adjustments, confidence_adjustment
            FROM self_analysis
            WHERE adjustments_applied = FALSE
            ORDER BY created_at DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        
        if result:
            adjustments = json.loads(result[0])
            conf_adj = result[1]
            
            # Apply adjustments to config
            for adj in adjustments:
                strategy_config = self._apply_adjustment(strategy_config, adj)
                
            # Mark as applied
            cursor.execute('''
                UPDATE self_analysis SET adjustments_applied = TRUE
                WHERE id = (SELECT id FROM self_analysis ORDER BY created_at DESC LIMIT 1)
            ''')
            conn.commit()
            
        conn.close()
        return strategy_config
```

### Automatic Training System

```python
# models/training/auto_trainer.py
import schedule
from datetime import datetime, timedelta

class AutoTrainer:
    """
    Automatically retrains models based on:
    1. Scheduled intervals (weekly)
    2. Performance degradation detection
    3. Significant market regime changes
    4. Manual trigger
    """
    
    def __init__(self, learning_db: LearningDatabase, model_manager):
        self.db = learning_db
        self.model_manager = model_manager
        self.performance_threshold = 0.20  # Trigger retrain if Sharpe drops 20%
        
    def setup_schedules(self):
        """Set up automatic training schedules"""
        # Weekly full retrain on weekends
        schedule.every().saturday.at("02:00").do(self.scheduled_retrain)
        
        # Daily performance check
        schedule.every().day.at("17:00").do(self.check_performance_degradation)
        
        # Hourly lightweight update (online learning)
        schedule.every().hour.do(self.incremental_update)
        
    def scheduled_retrain(self):
        """Full model retrain on schedule"""
        self._run_training_session(
            session_type='scheduled',
            trigger_reason='Weekly scheduled retrain',
            lookback_days=365
        )
        
    def check_performance_degradation(self):
        """Check if model performance has degraded significantly"""
        # Get recent performance
        recent_sharpe = self._calculate_recent_sharpe(days=14)
        baseline_sharpe = self._calculate_recent_sharpe(days=90)
        
        if baseline_sharpe > 0 and recent_sharpe < baseline_sharpe * (1 - self.performance_threshold):
            self._run_training_session(
                session_type='automatic',
                trigger_reason=f'Performance degradation detected: Sharpe dropped from {baseline_sharpe:.2f} to {recent_sharpe:.2f}',
                lookback_days=180
            )
            
    def incremental_update(self):
        """Lightweight online learning update"""
        # Get last 24 hours of trades
        recent_trades = self.db.get_recent_trades(hours=24)
        
        if len(recent_trades) >= 3:
            # Update model weights slightly based on recent outcomes
            self.model_manager.online_update(recent_trades)
            
    def manual_retrain(self, lookback_days: int = 365, 
                       specific_model: str = None,
                       custom_params: dict = None):
        """
        Trigger manual retraining with custom parameters.
        Called via CLI or dashboard.
        """
        self._run_training_session(
            session_type='manual',
            trigger_reason=f'Manual trigger with params: {custom_params}',
            lookback_days=lookback_days,
            specific_model=specific_model,
            custom_params=custom_params
        )
        
    def _run_training_session(self, session_type: str, trigger_reason: str,
                              lookback_days: int, specific_model: str = None,
                              custom_params: dict = None):
        """Execute a training session"""
        
        # Record session start
        session_id = self.db.start_training_session(session_type, trigger_reason)
        
        try:
            # Fetch training data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            training_data = self._fetch_training_data(start_date, end_date)
            
            # Get current model metrics for comparison
            current_metrics = self.model_manager.evaluate_current_models()
            
            # Train new models
            if specific_model:
                new_models = {specific_model: self.model_manager.train_model(
                    specific_model, training_data, custom_params
                )}
            else:
                new_models = self.model_manager.train_all_models(training_data)
            
            # Evaluate new models
            new_metrics = self.model_manager.evaluate_models(new_models, training_data)
            
            # Calculate improvement
            improvement = self._calculate_improvement(current_metrics, new_metrics)
            
            # Record results
            self.db.complete_training_session(
                session_id=session_id,
                records_used=len(training_data),
                previous_metrics=current_metrics,
                new_metrics=new_metrics,
                improvement_pct=improvement
            )
            
            # Auto-deploy if improvement is significant
            if improvement > 0.05:  # 5% improvement threshold
                if session_type == 'automatic':
                    # Wait for manual approval for auto-triggered retrains
                    self._notify_for_approval(session_id, improvement)
                else:
                    # Deploy immediately for manual/scheduled
                    self.model_manager.deploy_models(new_models)
                    self.db.mark_session_deployed(session_id)
                    
        except Exception as e:
            self.db.fail_training_session(session_id, str(e))
            raise
```

### Data Fetching for Self-Learning

```python
# data/fetcher/auto_fetcher.py

class AutoDataFetcher:
    """
    AI fetches its own data for learning and analysis.
    Runs independently to keep learning database current.
    """
    
    def __init__(self, alpaca_client, news_client, learning_db):
        self.alpaca = alpaca_client
        self.news = news_client
        self.db = learning_db
        
    async def fetch_learning_data(self, symbols: list):
        """
        Automatically fetch all data needed for learning:
        - Historical prices
        - News and sentiment
        - Market indicators (VIX, etc.)
        - Economic calendar
        """
        tasks = [
            self._fetch_price_data(symbols),
            self._fetch_news_data(symbols),
            self._fetch_market_indicators(),
            self._fetch_economic_events()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Store in learning database
        self._store_learning_data(results)
        
    async def _fetch_price_data(self, symbols: list):
        """Fetch latest price data for all tracked symbols"""
        data = {}
        for symbol in symbols:
            bars = self.alpaca.get_historical_bars(symbol, days=30)
            data[symbol] = bars
        return {'type': 'prices', 'data': data}
        
    async def _fetch_news_data(self, symbols: list):
        """Fetch and process news for sentiment"""
        all_news = []
        for symbol in symbols:
            news = await self.news.get_company_news(symbol, days=7)
            all_news.extend(news)
        return {'type': 'news', 'data': all_news}
        
    def run_continuous(self, interval_minutes: int = 15):
        """Run data fetching on continuous loop"""
        while True:
            try:
                asyncio.run(self.fetch_learning_data(self.get_watchlist()))
            except Exception as e:
                logging.error(f"Data fetch failed: {e}")
            time.sleep(interval_minutes * 60)
```

---

## AI Architecture: Opus 4.5 Hybrid Brain

**CRITICAL REQUIREMENT:** Leviathan operates fully autonomously. The user presses "Start" and the AI handles everything — scanning, analyzing, deciding, and executing trades. No human approval required for individual trades.

### Hybrid Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LEVIATHAN HYBRID BRAIN                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  LAYER 1: ML Signal Generation (Instant, Free)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │    LSTM     │  │  LightGBM   │  │   N-BEATS   │                 │
│  │  (Patterns) │  │  (Features) │  │ (Forecast)  │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         └────────────────┼────────────────┘                         │
│                          ▼                                          │
│              ┌───────────────────────┐                              │
│              │   Ensemble Signal     │                              │
│              │   + Confidence Score  │                              │
│              └───────────┬───────────┘                              │
│                          ▼                                          │
│  LAYER 2: Opus 4.5 Decision Brain (Final Authority)                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                              │  │
│  │   Opus receives:                                             │  │
│  │   • ML signal + confidence                                   │  │
│  │   • Current market data                                      │  │
│  │   • News sentiment summary                                   │  │
│  │   • Portfolio state                                          │  │
│  │   • Historical context from learning database                │  │
│  │   • Risk parameters                                          │  │
│  │                                                              │  │
│  │   Opus decides:                                              │  │
│  │   • EXECUTE / REJECT / MODIFY the trade                      │  │
│  │   • Position size (within dynamic limits)                    │  │
│  │   • Entry price / order type                                 │  │
│  │   • Stop loss and take profit levels                         │  │
│  │   • Reasoning (logged to database)                           │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          ▼                                          │
│  LAYER 3: Autonomous Execution                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │   If Opus says EXECUTE → Order sent to Alpaca immediately    │  │
│  │   No human confirmation required                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Opus Brain Implementation

```python
# intelligence/opus_brain.py
from anthropic import Anthropic
from datetime import datetime
import json

class OpusTradingBrain:
    """
    Opus 4.5 is the final decision maker for all trades.
    It receives ML signals and context, then decides autonomously.
    """
    
    def __init__(self, api_key: str, learning_db, risk_manager):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-opus-4-5-20250101"  # Opus 4.5
        self.db = learning_db
        self.risk = risk_manager
        self.daily_calls = 0
        self.daily_cost = 0.0
        
    def make_trade_decision(self, 
                           symbol: str,
                           ml_signal: dict,
                           market_data: dict,
                           sentiment: dict,
                           portfolio: dict,
                           account_value: float) -> dict:
        """
        Opus analyzes all inputs and makes the final trade decision.
        Returns a complete trade instruction or rejection.
        """
        
        # Gather historical context from learning database
        historical_context = self._get_historical_context(symbol, ml_signal)
        
        # Build the decision prompt
        prompt = self._build_decision_prompt(
            symbol=symbol,
            ml_signal=ml_signal,
            market_data=market_data,
            sentiment=sentiment,
            portfolio=portfolio,
            account_value=account_value,
            historical_context=historical_context
        )
        
        # Get Opus decision
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            system=self._get_system_prompt()
        )
        
        # Track costs (~$0.05-0.10 per decision)
        self.daily_calls += 1
        self.daily_cost += 0.08  # Approximate
        
        # Parse and validate decision
        decision = self._parse_decision(response.content[0].text)
        
        # Log decision to database
        self._log_decision(symbol, ml_signal, decision)
        
        return decision
    
    def _get_system_prompt(self) -> str:
        return """You are Opus, the trading brain of Leviathan - an autonomous AI trading system.

Your role is to make final trading decisions. You receive signals from ML models and must decide whether to execute trades.

CRITICAL RULES:
1. You have FULL AUTHORITY to execute trades autonomously. No human approval needed.
2. Always respect risk limits provided in the context.
3. Never exceed the maximum position size allowed.
4. Always set stop losses and take profits.
5. If uncertain, REJECT the trade. Capital preservation is paramount.
6. Learn from historical context - what worked before in similar conditions?

You must respond with a JSON object containing your decision. No other text."""

    def _build_decision_prompt(self, symbol: str, ml_signal: dict, 
                               market_data: dict, sentiment: dict,
                               portfolio: dict, account_value: float,
                               historical_context: dict) -> str:
        
        return f"""TRADE DECISION REQUIRED

=== SYMBOL: {symbol} ===

ML SIGNAL:
- Direction: {ml_signal['direction']}  (BUY/SELL/HOLD)
- Confidence: {ml_signal['confidence']:.2%}
- Technical Score: {ml_signal['technical_score']:.2f}
- LSTM Prediction: {ml_signal['lstm_pred']:.2%} price change
- LightGBM Probability: {ml_signal['lgbm_prob']:.2%}

CURRENT MARKET DATA:
- Price: ${market_data['price']:.2f}
- Daily Change: {market_data['daily_change']:.2%}
- RSI(14): {market_data['rsi']:.1f}
- MACD: {market_data['macd']:.4f}
- Volume vs Avg: {market_data['volume_ratio']:.1f}x
- ATR(14): ${market_data['atr']:.2f}
- 50-day MA: ${market_data['sma_50']:.2f}
- 200-day MA: ${market_data['sma_200']:.2f}

SENTIMENT:
- News Score: {sentiment['news_score']:.2f} (-1 to +1)
- Social Score: {sentiment['social_score']:.2f} (-1 to +1)
- Recent Headlines: {sentiment['headlines'][:3]}

PORTFOLIO STATE:
- Account Value: ${account_value:.2f}
- Buying Power: ${portfolio['buying_power']:.2f}
- Current Positions: {len(portfolio['positions'])}
- Already holding {symbol}: {symbol in portfolio['positions']}
- Today's P&L: ${portfolio['daily_pnl']:.2f}
- Day Trades Used: {portfolio['day_trades_used']}/3

RISK LIMITS:
- Max Position Size: ${portfolio['max_position_dollars']:.2f}
- Current Performance Tier: {portfolio['performance_tier']}
- Dynamic Position Range: {portfolio['min_position_pct']:.1%} - {portfolio['max_position_pct']:.1%}
- Current Drawdown: {portfolio['current_drawdown']:.1%}

HISTORICAL CONTEXT (Similar Past Trades):
{json.dumps(historical_context, indent=2)}

=== YOUR DECISION ===

Respond with ONLY a JSON object:
{{
    "action": "EXECUTE" | "REJECT" | "MODIFY",
    "side": "buy" | "sell" | null,
    "position_size_dollars": <number or null>,
    "position_size_pct": <percentage as decimal>,
    "order_type": "market" | "limit",
    "limit_price": <number or null>,
    "stop_loss_price": <number>,
    "take_profit_price": <number>,
    "reasoning": "<your detailed reasoning>",
    "confidence": <0.0 to 1.0>,
    "risk_assessment": "<brief risk assessment>"
}}

If REJECT, set side and prices to null but explain reasoning."""

    def _get_historical_context(self, symbol: str, ml_signal: dict) -> dict:
        """Query learning database for similar past situations"""
        
        similar_trades = self.db.query_similar_trades(
            symbol=symbol,
            signal_confidence=ml_signal['confidence'],
            technical_score=ml_signal['technical_score'],
            limit=5
        )
        
        if not similar_trades:
            return {"note": "No similar historical trades found"}
            
        # Summarize historical performance
        wins = sum(1 for t in similar_trades if t['profit_loss'] > 0)
        avg_profit = sum(t['profit_loss_pct'] for t in similar_trades) / len(similar_trades)
        
        return {
            "similar_trades_found": len(similar_trades),
            "win_rate_in_similar": f"{wins/len(similar_trades):.0%}",
            "avg_outcome": f"{avg_profit:.2%}",
            "best_outcome": f"{max(t['profit_loss_pct'] for t in similar_trades):.2%}",
            "worst_outcome": f"{min(t['profit_loss_pct'] for t in similar_trades):.2%}",
            "sample_trades": [
                {
                    "date": t['entry_date'],
                    "entry": t['entry_price'],
                    "exit": t['exit_price'],
                    "result": f"{t['profit_loss_pct']:.2%}"
                }
                for t in similar_trades[:3]
            ]
        }
    
    def _parse_decision(self, response_text: str) -> dict:
        """Parse Opus response into structured decision"""
        try:
            # Clean response if it has markdown code blocks
            clean = response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            
            decision = json.loads(clean)
            
            # Validate required fields
            required = ['action', 'reasoning', 'confidence']
            for field in required:
                if field not in decision:
                    raise ValueError(f"Missing required field: {field}")
                    
            return decision
            
        except Exception as e:
            # If parsing fails, reject trade for safety
            return {
                "action": "REJECT",
                "reasoning": f"Failed to parse Opus response: {e}",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _log_decision(self, symbol: str, ml_signal: dict, decision: dict):
        """Log every decision to learning database"""
        self.db.log_opus_decision(
            timestamp=datetime.now(),
            symbol=symbol,
            ml_signal=ml_signal,
            decision=decision
        )


class OpusExitManager:
    """
    Opus also decides when to exit positions.
    Runs periodically to evaluate all open positions.
    """
    
    def __init__(self, opus_brain: OpusTradingBrain):
        self.brain = opus_brain
        
    def evaluate_exits(self, positions: list, market_data: dict) -> list:
        """
        Evaluate all open positions and decide which to exit.
        Returns list of exit instructions.
        """
        exit_instructions = []
        
        for position in positions:
            decision = self._evaluate_single_position(position, market_data)
            if decision['action'] == 'EXIT':
                exit_instructions.append(decision)
                
        return exit_instructions
    
    def _evaluate_single_position(self, position: dict, market_data: dict) -> dict:
        """Ask Opus whether to exit a specific position"""
        
        prompt = f"""POSITION EXIT EVALUATION

Symbol: {position['symbol']}
Entry Price: ${position['entry_price']:.2f}
Current Price: ${market_data[position['symbol']]['price']:.2f}
Unrealized P&L: {position['unrealized_pnl_pct']:.2%}
Days Held: {position['days_held']}
Original Stop Loss: ${position['stop_loss']:.2f}
Original Take Profit: ${position['take_profit']:.2f}

Current Indicators:
- RSI: {market_data[position['symbol']]['rsi']:.1f}
- MACD: {market_data[position['symbol']]['macd']:.4f}
- Price vs Entry: {((market_data[position['symbol']]['price'] / position['entry_price']) - 1) * 100:.2f}%

Should we EXIT this position now, HOLD, or ADJUST stop/target?

Respond with JSON:
{{
    "action": "EXIT" | "HOLD" | "ADJUST",
    "exit_type": "market" | "limit" | null,
    "new_stop_loss": <number or null>,
    "new_take_profit": <number or null>,
    "reasoning": "<explanation>"
}}"""

        response = self.brain.client.messages.create(
            model=self.brain.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self.brain._parse_decision(response.content[0].text)
```

### Autonomous Execution Engine

```python
# execution/autonomous_executor.py

class AutonomousExecutor:
    """
    Executes Opus decisions without human intervention.
    This is the component that actually places trades.
    """
    
    def __init__(self, alpaca_client, opus_brain: OpusTradingBrain, 
                 risk_manager, learning_db):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        self.risk = risk_manager
        self.db = learning_db
        self.is_running = False
        
    def execute_decision(self, decision: dict, symbol: str) -> dict:
        """
        Execute an Opus trading decision.
        No human approval required - fully autonomous.
        """
        
        if decision['action'] == 'REJECT':
            return {"status": "rejected", "reason": decision['reasoning']}
            
        if decision['action'] not in ['EXECUTE', 'MODIFY']:
            return {"status": "invalid_action", "decision": decision}
        
        # Final risk check (redundant safety)
        risk_check = self.risk.pre_trade_check({
            'symbol': symbol,
            'qty': decision['position_size_dollars'],
            'side': decision['side']
        })
        
        if not risk_check[0]:
            return {"status": "risk_rejected", "reason": risk_check[1]}
        
        # Calculate quantity from dollar amount
        current_price = self.alpaca.get_latest_price(symbol)
        qty = decision['position_size_dollars'] / current_price
        
        # Submit the order
        try:
            if decision['order_type'] == 'market':
                order = self.alpaca.submit_bracket_order(
                    symbol=symbol,
                    qty=qty,
                    side=decision['side'],
                    take_profit=decision['take_profit_price'],
                    stop_loss=decision['stop_loss_price']
                )
            else:
                order = self.alpaca.submit_limit_bracket_order(
                    symbol=symbol,
                    qty=qty,
                    side=decision['side'],
                    limit_price=decision['limit_price'],
                    take_profit=decision['take_profit_price'],
                    stop_loss=decision['stop_loss_price']
                )
                
            # Log execution
            self.db.log_execution(
                symbol=symbol,
                decision=decision,
                order=order,
                timestamp=datetime.now()
            )
            
            return {
                "status": "executed",
                "order_id": order.id,
                "symbol": symbol,
                "qty": qty,
                "side": decision['side'],
                "reasoning": decision['reasoning']
            }
            
        except Exception as e:
            return {
                "status": "execution_failed",
                "error": str(e),
                "decision": decision
            }
```

### Cost Management for Opus

```python
# config/llm_config.py

LLM_CONFIG = {
    # Opus 4.5 for all trading decisions
    'decision_model': 'claude-opus-4-5-20250101',
    
    # Sonnet for less critical tasks (summaries, reports)
    'utility_model': 'claude-sonnet-4-20250514',
    
    # Budget limits
    'daily_budget_usd': 5.00,  # Max $5/day on API calls
    'max_opus_calls_per_day': 50,  # ~$4/day at $0.08/call
    
    # Estimated costs per call
    'opus_cost_per_call': 0.08,
    'sonnet_cost_per_call': 0.01,
    
    # When to use which model
    'use_opus_for': [
        'trade_decisions',
        'exit_decisions', 
        'position_sizing',
        'daily_analysis'
    ],
    'use_sonnet_for': [
        'trade_logging',
        'report_generation',
        'simple_summaries'
    ]
}

# Monthly cost estimate at different activity levels:
# Low activity (10 Opus calls/day):   ~$24/month
# Medium activity (25 Opus calls/day): ~$60/month  
# High activity (50 Opus calls/day):   ~$120/month
```

### Historical Data Training System

```python
# training/historical_trainer.py

class HistoricalTrainer:
    """
    Trains the system using historical data.
    Teaches Opus what good entries and exits look like.
    """
    
    def __init__(self, learning_db, data_client):
        self.db = learning_db
        self.data = data_client
        
    def train_from_historical(self, symbols: list, years: int = 5):
        """
        Process historical data to build the learning database.
        This teaches the AI what patterns led to good outcomes.
        """
        
        for symbol in symbols:
            print(f"Training on {symbol}...")
            
            # Fetch historical data
            df = self.data.get_historical_bars(symbol, days=years*365)
            
            # Calculate all indicators
            df = self._add_all_indicators(df)
            
            # Identify historical "perfect" entries and exits
            trades = self._identify_historical_trades(df)
            
            # Store in learning database
            for trade in trades:
                self.db.store_historical_trade(
                    symbol=symbol,
                    entry_date=trade['entry_date'],
                    exit_date=trade['exit_date'],
                    entry_price=trade['entry_price'],
                    exit_price=trade['exit_price'],
                    profit_loss_pct=trade['profit_pct'],
                    indicators_at_entry=trade['entry_indicators'],
                    indicators_at_exit=trade['exit_indicators'],
                    hold_duration=trade['hold_days'],
                    trade_type=trade['type']  # 'swing_long', 'swing_short', etc.
                )
                
        print(f"Training complete. {self.db.count_historical_trades()} trades in database.")
    
    def _identify_historical_trades(self, df: pd.DataFrame) -> list:
        """
        Identify what would have been good trades historically.
        Uses multiple strategies to find optimal entries/exits.
        """
        trades = []
        
        # Strategy 1: RSI Mean Reversion entries
        trades.extend(self._find_rsi_trades(df))
        
        # Strategy 2: MACD Crossover entries  
        trades.extend(self._find_macd_trades(df))
        
        # Strategy 3: Bollinger Band bounces
        trades.extend(self._find_bb_trades(df))
        
        # Strategy 4: Moving Average crosses
        trades.extend(self._find_ma_trades(df))
        
        # Filter for profitable trades only (we want to learn from winners)
        profitable = [t for t in trades if t['profit_pct'] > 0]
        
        # Also keep some losers to learn what NOT to do
        losers = [t for t in trades if t['profit_pct'] < -0.02][:len(profitable)//4]
        
        return profitable + losers
    
    def _find_rsi_trades(self, df: pd.DataFrame) -> list:
        """Find historical RSI mean reversion opportunities"""
        trades = []
        
        i = 0
        while i < len(df) - 10:
            # Entry: RSI crosses above 30 from below
            if df['rsi'].iloc[i-1] < 30 and df['rsi'].iloc[i] >= 30:
                entry_date = df.index[i]
                entry_price = df['close'].iloc[i]
                entry_indicators = self._get_indicators_at(df, i)
                
                # Find exit (RSI > 65 or 5 days max)
                for j in range(i+1, min(i+6, len(df))):
                    if df['rsi'].iloc[j] > 65 or j == i+5:
                        exit_date = df.index[j]
                        exit_price = df['close'].iloc[j]
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': exit_date,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_pct': (exit_price - entry_price) / entry_price,
                            'entry_indicators': entry_indicators,
                            'exit_indicators': self._get_indicators_at(df, j),
                            'hold_days': j - i,
                            'type': 'rsi_mean_reversion'
                        })
                        i = j
                        break
            i += 1
            
        return trades
    
    def generate_training_report(self) -> dict:
        """Generate summary of what the AI has learned"""
        
        return {
            'total_historical_trades': self.db.count_historical_trades(),
            'profitable_patterns': self.db.get_top_patterns(by='win_rate', limit=10),
            'best_entry_conditions': self.db.get_best_entry_conditions(),
            'optimal_hold_duration': self.db.get_optimal_hold_duration(),
            'best_performing_strategy': self.db.get_best_strategy(),
            'market_conditions_analysis': self.db.analyze_by_market_condition()
        }
```
```

---

## Trading Strategies to Implement

### Strategy 1: RSI Mean Reversion (Primary)

**Entry Conditions (Long):**
- RSI(14) crosses above 30 from below
- Price is above 200-day SMA (confirming uptrend)
- Volume > 1.5x 20-day average
- Sentiment score > -0.3

**Exit Conditions:**
- Take profit: RSI reaches 65 OR price gains 5%
- Stop loss: Price drops 3% OR RSI drops below 25
- Time stop: Exit after 5 days regardless

**Position Size:** 10-15% of portfolio per trade

### Strategy 2: MACD Momentum (Secondary)

**Entry Conditions (Long):**
- MACD crosses above signal line
- MACD histogram increasing for 2+ days
- Price above 50-day SMA
- ADX > 20 (trending market)

**Exit Conditions:**
- Take profit: MACD crosses below signal OR 7% gain
- Stop loss: 4% decline
- Time stop: Exit after 7 days

**Position Size:** 10% of portfolio per trade

### Strategy 3: Bollinger Band Squeeze (Breakout)

**Entry Conditions:**
- Bollinger Band width at 20-day low (squeeze)
- Price breaks above upper band with volume
- RSI between 50-70

**Exit Conditions:**
- Take profit: 2x ATR from entry
- Stop loss: Below middle band (20 SMA)
- Time stop: Exit after 5 days

**Position Size:** 8% of portfolio per trade

---

## Holding Periods & Exit Management

### CRITICAL: Stocks vs Options Expiration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXPIRATION RULES BY ASSET                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STOCKS & CRYPTO:  NO EXPIRATION                                            │
│  ─────────────────────────────────────────                                  │
│  • You own shares/coins until YOU decide to sell                            │
│  • AI uses EXIT RULES to decide when to close                               │
│  • Can hold for minutes, days, weeks, or years                              │
│                                                                             │
│  OPTIONS:  HAVE EXPIRATION DATES                                            │
│  ─────────────────────────────────                                          │
│  • You MUST choose expiration when opening position                         │
│  • AI targets 21-45 DTE (days to expiration) sweet spot                     │
│  • AI closes positions before expiration (< 7 DTE)                          │
│  • If not closed, options expire worthless or get exercised                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stock Exit Management (OpusExitManager)

```python
# execution/exit_manager.py

class StockExitManager:
    """
    Manages exits for stock positions.
    Stocks have NO expiration - AI decides when to exit based on rules.
    """
    
    def __init__(self, alpaca_client, opus_brain):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        
        # Default exit parameters (can be overridden per trade)
        self.default_take_profit_pct = 0.05    # +5% take profit
        self.default_stop_loss_pct = 0.03      # -3% stop loss
        self.default_time_stop_days = 5        # Exit after 5 days
        self.trailing_stop_pct = 0.02          # 2% trailing stop
        
    def check_all_positions(self) -> list:
        """
        Check all open positions for exit conditions.
        Called every minute during market hours.
        """
        positions = self.alpaca.get_all_positions()
        exit_signals = []
        
        for pos in positions:
            if '/' in pos['symbol']:  # Skip crypto (handled separately)
                continue
                
            exit_check = self._evaluate_position(pos)
            if exit_check['should_exit']:
                exit_signals.append(exit_check)
                
        return exit_signals
    
    def _evaluate_position(self, position: dict) -> dict:
        """
        Evaluate if a position should be exited.
        Checks multiple exit conditions in priority order.
        """
        symbol = position['symbol']
        entry_price = float(position['avg_entry_price'])
        current_price = float(position['current_price'])
        qty = float(position['qty'])
        unrealized_pnl_pct = float(position['unrealized_plpc'])
        
        # Get position metadata from database
        trade_info = self.db.get_trade_info(symbol)
        entry_time = trade_info.get('entry_time')
        take_profit = trade_info.get('take_profit_price', entry_price * 1.05)
        stop_loss = trade_info.get('stop_loss_price', entry_price * 0.97)
        time_stop_days = trade_info.get('time_stop_days', self.default_time_stop_days)
        highest_price = trade_info.get('highest_price_since_entry', current_price)
        
        # Update highest price for trailing stop
        if current_price > highest_price:
            highest_price = current_price
            self.db.update_highest_price(symbol, highest_price)
        
        # Calculate days held
        days_held = (datetime.now() - entry_time).days if entry_time else 0
        
        # EXIT CONDITION CHECKS (in priority order)
        
        # 1. STOP LOSS - Highest priority, protect capital
        if current_price <= stop_loss:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'STOP_LOSS',
                'details': f'Price ${current_price:.2f} hit stop loss ${stop_loss:.2f}',
                'urgency': 'HIGH',
                'order_type': 'market'  # Use market order for stops
            }
        
        # 2. TRAILING STOP - Lock in profits
        trailing_stop_price = highest_price * (1 - self.trailing_stop_pct)
        if current_price <= trailing_stop_price and unrealized_pnl_pct > 0.02:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'TRAILING_STOP',
                'details': f'Price ${current_price:.2f} dropped {self.trailing_stop_pct:.0%} from high ${highest_price:.2f}',
                'urgency': 'HIGH',
                'order_type': 'market'
            }
        
        # 3. TAKE PROFIT - Target reached
        if current_price >= take_profit:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'TAKE_PROFIT',
                'details': f'Price ${current_price:.2f} hit target ${take_profit:.2f} (+{unrealized_pnl_pct:.1%})',
                'urgency': 'MEDIUM',
                'order_type': 'limit'  # Can use limit for take profits
            }
        
        # 4. TIME STOP - Don't hold losers too long
        if days_held >= time_stop_days:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'TIME_STOP',
                'details': f'Position held for {days_held} days (max {time_stop_days})',
                'urgency': 'LOW',
                'order_type': 'limit'
            }
        
        # 5. TECHNICAL REVERSAL - Let Opus decide
        technical_exit = self._check_technical_exit(symbol, position)
        if technical_exit['should_exit']:
            return technical_exit
        
        # No exit needed
        return {
            'symbol': symbol,
            'should_exit': False,
            'days_held': days_held,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'distance_to_stop': (current_price - stop_loss) / current_price,
            'distance_to_target': (take_profit - current_price) / current_price
        }
    
    def _check_technical_exit(self, symbol: str, position: dict) -> dict:
        """
        Check if technical indicators suggest exiting.
        """
        # Get current indicators
        data = self.alpaca.get_historical_bars(symbol, timeframe='1D', limit=50)
        
        rsi = self._calculate_rsi(data['close'], 14)
        macd, signal, histogram = self._calculate_macd(data['close'])
        
        # Check for technical exit signals
        exit_reasons = []
        
        # RSI overbought (if we're long and profitable)
        if rsi > 70 and float(position['unrealized_plpc']) > 0.02:
            exit_reasons.append(f'RSI overbought ({rsi:.0f})')
            
        # MACD bearish crossover
        if macd < signal and histogram < 0:
            exit_reasons.append('MACD bearish crossover')
            
        # Price broke below key moving average
        sma_20 = data['close'].rolling(20).mean().iloc[-1]
        if float(position['current_price']) < sma_20 * 0.98:
            exit_reasons.append(f'Price broke below 20 SMA')
        
        if exit_reasons:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'TECHNICAL_REVERSAL',
                'details': '; '.join(exit_reasons),
                'urgency': 'MEDIUM',
                'order_type': 'limit'
            }
            
        return {'should_exit': False}
    
    def execute_exit(self, exit_signal: dict) -> dict:
        """Execute an exit order"""
        symbol = exit_signal['symbol']
        position = self.alpaca.get_position(symbol)
        qty = float(position['qty'])
        
        if exit_signal['order_type'] == 'market':
            order = self.alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
        else:
            # Limit order slightly below current price for quick fill
            current_price = float(position['current_price'])
            limit_price = current_price * 0.999  # 0.1% below
            
            order = self.alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='limit',
                limit_price=limit_price,
                time_in_force='day'
            )
        
        # Log the exit
        self.db.log_exit(
            symbol=symbol,
            exit_reason=exit_signal['reason'],
            exit_price=float(position['current_price']),
            exit_time=datetime.now()
        )
        
        return {
            'status': 'submitted',
            'order_id': order.id,
            'symbol': symbol,
            'reason': exit_signal['reason']
        }


class OptionsExitManager:
    """
    Manages exits for options positions.
    Options HAVE expiration dates - must close before expiry.
    """
    
    def __init__(self, alpaca_client, opus_brain):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        
        # Options-specific exit rules
        self.profit_target_pct = 0.50      # Close at 50% of max profit
        self.stop_loss_multiplier = 2.0    # Close if loss > 2x credit received
        self.min_dte_to_hold = 7           # Close if < 7 days to expiration
        self.theta_decay_threshold = 0.70  # Close if captured 70% of theta
        
    def check_all_options(self) -> list:
        """Check all options positions for exit conditions"""
        positions = self.alpaca.get_options_positions()
        exit_signals = []
        
        for pos in positions:
            exit_check = self._evaluate_options_position(pos)
            if exit_check['should_exit']:
                exit_signals.append(exit_check)
                
        return exit_signals
    
    def _evaluate_options_position(self, position: dict) -> dict:
        """
        Evaluate if an options position should be closed.
        
        Key considerations:
        1. Profit target reached (close early, don't be greedy)
        2. Stop loss hit (cut losses)
        3. Approaching expiration (avoid gamma risk)
        4. Theta captured (time decay harvested)
        """
        symbol = position['symbol']
        current_value = float(position['market_value'])
        cost_basis = float(position['cost_basis'])
        
        # Calculate current P&L
        if cost_basis < 0:  # Credit received (sold premium)
            credit_received = abs(cost_basis)
            current_cost_to_close = abs(current_value)
            pnl = credit_received - current_cost_to_close
            pnl_pct = pnl / credit_received if credit_received > 0 else 0
            max_profit = credit_received
        else:  # Debit paid (bought options)
            pnl = current_value - cost_basis
            pnl_pct = pnl / cost_basis if cost_basis > 0 else 0
            max_profit = position.get('max_profit', cost_basis * 2)
        
        # Get days to expiration
        expiration = position.get('expiration_date')
        if expiration:
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            dte = (exp_date - datetime.now()).days
        else:
            dte = 999
        
        # EXIT CHECKS
        
        # 1. PROFIT TARGET - Take profits early (50% of max)
        if pnl_pct >= self.profit_target_pct:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'PROFIT_TARGET',
                'details': f'Captured {pnl_pct:.0%} of max profit (target {self.profit_target_pct:.0%})',
                'pnl': pnl,
                'dte': dte
            }
        
        # 2. STOP LOSS - Limit losses
        if cost_basis < 0:  # For credit spreads
            max_acceptable_loss = credit_received * self.stop_loss_multiplier
            if current_cost_to_close > credit_received + max_acceptable_loss:
                return {
                    'symbol': symbol,
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'details': f'Loss exceeds {self.stop_loss_multiplier}x credit received',
                    'pnl': pnl,
                    'dte': dte
                }
        else:  # For debit spreads
            if pnl_pct <= -0.50:  # 50% loss on debit
                return {
                    'symbol': symbol,
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'details': f'Lost {abs(pnl_pct):.0%} of debit paid',
                    'pnl': pnl,
                    'dte': dte
                }
        
        # 3. EXPIRATION APPROACHING - Avoid gamma risk
        if dte <= self.min_dte_to_hold:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'EXPIRATION_APPROACHING',
                'details': f'Only {dte} days to expiration (min {self.min_dte_to_hold})',
                'pnl': pnl,
                'dte': dte
            }
        
        # 4. THETA CAPTURED - Time decay harvested
        original_dte = position.get('original_dte', 45)
        time_elapsed_pct = 1 - (dte / original_dte)
        if time_elapsed_pct >= self.theta_decay_threshold and pnl > 0:
            return {
                'symbol': symbol,
                'should_exit': True,
                'reason': 'THETA_CAPTURED',
                'details': f'{time_elapsed_pct:.0%} of time elapsed, take profits',
                'pnl': pnl,
                'dte': dte
            }
        
        return {
            'symbol': symbol,
            'should_exit': False,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'dte': dte
        }
```

### Options DTE (Days to Expiration) Selection

```python
# options/dte_selector.py

class DTESelector:
    """
    Selects optimal expiration date for options trades.
    
    DTE SWEET SPOTS:
    ────────────────
    < 7 days:   DANGEROUS - Gamma risk explodes, avoid
    7-21 days:  HIGH RISK - Fast theta decay but volatile
    21-45 days: SWEET SPOT - Best theta/gamma balance ← TARGET THIS
    45-60 days: MODERATE - Slower decay, more capital
    > 60 days:  SLOW - Too much time, capital inefficient
    """
    
    # Target DTE range
    MIN_DTE = 21
    MAX_DTE = 45
    IDEAL_DTE = 35  # Optimal for credit spreads
    
    @staticmethod
    def select_expiration(chain: dict, strategy: str) -> dict:
        """
        Select the best expiration date for a given strategy.
        
        Args:
            chain: Options chain data
            strategy: 'credit_spread', 'iron_condor', 'debit_spread', etc.
        """
        available_expirations = chain.get('expirations', [])
        today = datetime.now().date()
        
        # Filter to valid DTE range
        valid_expirations = []
        for exp in available_expirations:
            exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
            dte = (exp_date - today).days
            
            if DTESelector.MIN_DTE <= dte <= DTESelector.MAX_DTE:
                valid_expirations.append({
                    'expiration': exp,
                    'dte': dte,
                    'score': DTESelector._score_dte(dte, strategy)
                })
        
        if not valid_expirations:
            return {'error': 'No valid expirations in 21-45 DTE range'}
        
        # Sort by score (highest first)
        valid_expirations.sort(key=lambda x: x['score'], reverse=True)
        
        return valid_expirations[0]
    
    @staticmethod
    def _score_dte(dte: int, strategy: str) -> float:
        """Score a DTE based on strategy type"""
        
        # Base score - prefer ~35 DTE
        distance_from_ideal = abs(dte - DTESelector.IDEAL_DTE)
        base_score = 1.0 - (distance_from_ideal / 30)
        
        # Strategy adjustments
        if strategy in ['credit_spread', 'iron_condor']:
            # Credit strategies: prefer slightly longer DTE for more premium
            if 30 <= dte <= 45:
                base_score += 0.1
        elif strategy in ['debit_spread']:
            # Debit strategies: prefer slightly shorter DTE for faster moves
            if 21 <= dte <= 35:
                base_score += 0.1
        
        # Avoid weekly expirations (Fridays) - wider spreads
        # Prefer monthly expirations (3rd Friday)
        # This would require calendar logic
        
        return base_score
```

### Holding Period Summary by Asset Type

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HOLDING PERIODS BY ASSET CLASS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SWING TRADES (Stocks):                                                     │
│  ──────────────────────                                                     │
│  Target Hold:     2-5 days (strategy dependent)                             │
│  Maximum Hold:    5-7 days (time stop)                                      │
│  Exit Triggers:   Take profit, stop loss, time stop, technical reversal    │
│  NO EXPIRATION - AI decides when to sell                                    │
│                                                                             │
│  PORTFOLIO AUTOPILOT (Long-term Stocks):                                    │
│  ───────────────────────────────────────                                    │
│  Target Hold:     Weeks to months                                           │
│  Exit Triggers:   Bearish signals, rotation to stronger stocks              │
│  NO EXPIRATION - Hold until fundamentals change                             │
│                                                                             │
│  CRYPTO:                                                                    │
│  ───────                                                                    │
│  Target Hold:     Hours to days (24/7 trading)                              │
│  Exit Triggers:   Same as stocks + higher volatility tolerance              │
│  NO EXPIRATION - AI decides when to sell                                    │
│                                                                             │
│  OPTIONS:                                                                   │
│  ────────                                                                   │
│  Entry DTE:       21-45 days (sweet spot)                                   │
│  Target Hold:     Until 50% profit OR 7 DTE (whichever first)              │
│  Exit Triggers:   Profit target, stop loss, DTE < 7, theta captured         │
│  HAS EXPIRATION - MUST close before expiry or get assigned                 │
│                                                                             │
│  EXIT PRIORITY (highest to lowest):                                         │
│  ──────────────────────────────────                                         │
│  1. Stop Loss Hit      → EXIT IMMEDIATELY (market order)                    │
│  2. Trailing Stop Hit  → EXIT IMMEDIATELY (market order)                    │
│  3. Take Profit Hit    → EXIT (can use limit order)                         │
│  4. DTE < 7 (options)  → EXIT (avoid gamma risk)                            │
│  5. Time Stop          → EXIT (don't hold losers)                           │
│  6. Technical Reversal → EXIT (Opus decision)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Backtesting Requirements

### Minimum Validation Standards

Before deploying any strategy:

1. **Walk-forward backtest** over minimum 3 years of data
2. **Out-of-sample testing** on most recent 6 months
3. **Paper trading** for minimum 4 weeks
4. **Performance metrics must exceed:**
   - Sharpe Ratio > 1.0
   - Win Rate > 50%
   - Profit Factor > 1.3
   - Max Drawdown < 20%

### Backtest Output Format

```python
@dataclass
class BacktestResults:
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float  # days
    avg_win: float
    avg_loss: float
    equity_curve: pd.Series
    trade_log: pd.DataFrame
```

---

## Configuration Constants

```python
# config/settings.py

# Account Constraints
STARTING_CAPITAL = 500.0
MIN_TRADE_SIZE = 1.0  # Alpaca minimum for fractional shares

# PDT Protection
MAX_DAY_TRADES_PER_WEEK = 3  # Safety buffer below 4
HOLD_PERIOD_DAYS = 2  # Minimum hold to avoid day trade

# Risk Limits (these are MAXIMUM limits - dynamic sizing will usually be lower)
MAX_POSITION_PCT = 0.30  # Absolute maximum, only reached at MAXIMUM tier
MAX_DAILY_LOSS_PCT = 0.03
MAX_TOTAL_EXPOSURE_PCT = 0.80

# Dynamic Position Sizing Tiers
POSITION_TIERS = {
    'LEARNING': {'base': 0.05, 'max': 0.10, 'min_profit': -999, 'min_trades': 0},
    'CAUTIOUS': {'base': 0.08, 'max': 0.15, 'min_profit': 0, 'min_trades': 10},
    'CONFIDENT': {'base': 0.12, 'max': 0.20, 'min_profit': 5, 'min_trades': 25},
    'AGGRESSIVE': {'base': 0.15, 'max': 0.25, 'min_profit': 15, 'min_trades': 50},
    'MAXIMUM': {'base': 0.20, 'max': 0.30, 'min_profit': 30, 'min_trades': 100},
}

# Drawdown Scaling
DRAWDOWN_SCALING = [
    (0.00, 1.00),  # No drawdown = full size
    (0.03, 0.85),  # 3% drawdown = 85% size
    (0.05, 0.70),  # 5% drawdown = 70% size
    (0.08, 0.50),  # 8% drawdown = 50% size
    (0.10, 0.30),  # 10% drawdown = 30% size
    (0.15, 0.10),  # 15% drawdown = minimal trading
]

# Trading Hours (Eastern Time)
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
EXTENDED_OPEN = "04:00"
EXTENDED_CLOSE = "20:00"

# ML Model Settings
LSTM_SEQUENCE_LENGTH = 20
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

# Learning System Settings
LEARNING_DB_PATH = "leviathan_learning.db"
STATE_DB_PATH = "leviathan_state.db"
MINIMUM_TRADES_FOR_LEARNING = 5  # Don't query best practices until this many trades
SELF_ANALYSIS_TIME = "17:00"  # Run daily self-analysis at market close
PERFORMANCE_DEGRADATION_THRESHOLD = 0.20  # Trigger retrain if Sharpe drops 20%
AUTO_RETRAIN_LOOKBACK_DAYS = 180

# LLM Settings (Opus 4.5 is the trading brain)
LLM_DECISION_MODEL = "claude-opus-4-5-20250101"  # For trade decisions
LLM_UTILITY_MODEL = "claude-sonnet-4-20250514"  # For summaries/reports
LLM_DAILY_BUDGET_USD = 5.00  # Higher budget for Opus
LLM_MAX_OPUS_CALLS_PER_DAY = 50
OPUS_COST_PER_CALL = 0.08  # Approximate
USE_OPUS_FOR_TRADE_DECISIONS = True  # Opus makes ALL final trade decisions
```

---

## GUI Application Specification

**REQUIREMENT:** Modern, professional-looking GUI that matches high-end fintech dashboards. User presses "Start" and Leviathan handles everything else. The UI should look **exactly** like the reference Figma design.

### Design Reference

**FIGMA PROTOTYPE (USE THIS AS THE DESIGN SPEC):**
- Community File: https://www.figma.com/community/file/1522238618706669989/dark-finance-crypto-dashboard-ui-design
- Interactive Prototype: https://www.figma.com/proto/zh1yF465p1YnQ4JGmtcXtQ/%F0%9F%A7%BE-Dark-Finance---Crypto-Dashboard-%E2%80%93-UI-Design--Community-?node-id=2-539&t=eRz7gczlnE7qSKQB-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1

Open the Figma file, duplicate it to your drafts, and use Dev Mode (press D) to extract exact colors, spacing, border-radius, and font specifications.

### GUI Framework: PyWebView + HTML/CSS/JavaScript

**WHY PyWebView:** To achieve pixel-perfect recreation of the Figma design, we use web technologies (HTML/CSS/JS) wrapped in a native desktop window. This gives us:
- Exact color matching
- Custom border-radius and shadows
- Smooth animations
- Professional charts with ApexCharts
- Responsive layouts with Tailwind CSS
- Full design control

```bash
pip install pywebview
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEVIATHAN GUI ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     PYWEBVIEW WINDOW                                 │  │
│   │   ┌─────────────────────────────────────────────────────────────┐   │  │
│   │   │                                                             │   │  │
│   │   │              HTML + CSS + JAVASCRIPT                        │   │  │
│   │   │              (Beautiful Frontend UI)                        │   │  │
│   │   │                                                             │   │  │
│   │   │   • Tailwind CSS for styling                                │   │  │
│   │   │   • ApexCharts for portfolio graphs                         │   │  │
│   │   │   • Custom components matching Figma                        │   │  │
│   │   │   • Real-time updates via JavaScript                        │   │  │
│   │   │                                                             │   │  │
│   │   └─────────────────────────────────────────────────────────────┘   │  │
│   │                              ↕                                       │  │
│   │                    JS ↔ Python Bridge                               │  │
│   │                      (pywebview.api)                                │  │
│   │                              ↕                                       │  │
│   │   ┌─────────────────────────────────────────────────────────────┐   │  │
│   │   │                                                             │   │  │
│   │   │              PYTHON BACKEND (API Class)                     │   │  │
│   │   │              (All Trading Logic)                            │   │  │
│   │   │                                                             │   │  │
│   │   │   • TradingEngine                                           │   │  │
│   │   │   • OpusBrain (Claude API)                                  │   │  │
│   │   │   • AlpacaClient                                            │   │  │
│   │   │   • RiskManager                                             │   │  │
│   │   │   • LearningDatabase                                        │   │  │
│   │   │                                                             │   │  │
│   │   └─────────────────────────────────────────────────────────────┘   │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Color Palette (Extract from Figma)

```css
/* Design System Colors - Dark Finance Theme */
:root {
    /* Backgrounds */
    --bg-primary: #0a0a0f;           /* Main app background */
    --bg-secondary: #12121a;         /* Card backgrounds */
    --bg-tertiary: #1a1a24;          /* Elevated cards, hover states */
    --bg-quaternary: #22222e;        /* Input fields, borders */
    
    /* Accent Colors */
    --accent-purple: #8b5cf6;        /* Primary accent (buttons, highlights) */
    --accent-purple-hover: #7c3aed;  /* Button hover */
    --accent-blue: #3b82f6;          /* Secondary accent */
    --accent-cyan: #06b6d4;          /* Tertiary accent */
    
    /* Status Colors */
    --success: #22c55e;              /* Profit, positive, running */
    --success-bg: rgba(34, 197, 94, 0.1);
    --danger: #ef4444;               /* Loss, negative, stopped */
    --danger-bg: rgba(239, 68, 68, 0.1);
    --warning: #f59e0b;              /* Caution, pending */
    --warning-bg: rgba(245, 158, 11, 0.1);
    
    /* Text Colors */
    --text-primary: #ffffff;         /* Main text */
    --text-secondary: #9ca3af;       /* Muted text, labels */
    --text-tertiary: #6b7280;        /* Disabled, placeholder */
    
    /* Border & Dividers */
    --border-color: #2d2d3a;         /* Card borders, dividers */
    --border-hover: #3d3d4a;         /* Border hover state */
    
    /* Gradients */
    --gradient-purple: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    --gradient-green: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    --gradient-card: linear-gradient(180deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%);
}
```

### Typography

```css
/* Font Stack */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Type Scale */
.text-display { font-size: 2.5rem; font-weight: 700; line-height: 1.2; }  /* 40px - Portfolio value */
.text-h1 { font-size: 1.5rem; font-weight: 600; line-height: 1.3; }       /* 24px - Section titles */
.text-h2 { font-size: 1.25rem; font-weight: 600; line-height: 1.4; }      /* 20px - Card titles */
.text-h3 { font-size: 1rem; font-weight: 600; line-height: 1.5; }         /* 16px - Subheadings */
.text-body { font-size: 0.875rem; font-weight: 400; line-height: 1.5; }   /* 14px - Body text */
.text-small { font-size: 0.75rem; font-weight: 400; line-height: 1.5; }   /* 12px - Labels, captions */
.text-tiny { font-size: 0.625rem; font-weight: 500; line-height: 1.5; }   /* 10px - Badges */
```

### Component Specifications

```css
/* Card Component */
.card {
    background: var(--bg-secondary);
    border-radius: 16px;
    border: 1px solid var(--border-color);
    padding: 24px;
    transition: all 0.2s ease;
}
.card:hover {
    border-color: var(--border-hover);
    background: var(--bg-tertiary);
}

/* Button Component */
.btn-primary {
    background: var(--gradient-purple);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4);
}
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
}

.btn-success {
    background: var(--gradient-green);
    box-shadow: 0 4px 14px rgba(34, 197, 94, 0.4);
}

.btn-danger {
    background: var(--danger);
    box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
}

/* Input Component */
.input {
    background: var(--bg-quaternary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px 16px;
    color: var(--text-primary);
    font-size: 14px;
    width: 100%;
    transition: all 0.2s ease;
}
.input:focus {
    outline: none;
    border-color: var(--accent-purple);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
}

/* Badge Component */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}
.badge-success {
    background: var(--success-bg);
    color: var(--success);
}
.badge-danger {
    background: var(--danger-bg);
    color: var(--danger);
}

/* Stat Card */
.stat-card {
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid var(--border-color);
}
.stat-card .label {
    color: var(--text-secondary);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.stat-card .value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
}
.stat-card .change {
    font-size: 14px;
    font-weight: 500;
    margin-top: 4px;
}
```

### Main Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌──────────┐  ┌──────────────────────────────────────────────────────────────┐│
│  │          │  │                                                              ││
│  │  SIDEBAR │  │                      MAIN CONTENT AREA                       ││
│  │          │  │                                                              ││
│  │  ┌────┐  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ ││
│  │  │ 🏠 │  │  │  │ Portfolio   │ │ Today's P&L │ │ Opus Brain  │ │ Status │ ││
│  │  │Home│  │  │  │ $523.47     │ │ +$12.34     │ │ 7 decisions │ │●RUNNING│ ││
│  │  └────┘  │  │  │ ▲ +4.7%     │ │ ▲ +2.4%     │ │ $0.56 cost  │ │        │ ││
│  │          │  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ ││
│  │  ┌────┐  │  │                                                              ││
│  │  │ 📊 │  │  │  ┌──────────────────────────────────────────────────────┐   ││
│  │  │Ana-│  │  │  │                                                      │   ││
│  │  │lyti│  │  │  │              PORTFOLIO PERFORMANCE CHART             │   ││
│  │  │cs  │  │  │  │                    (ApexCharts)                      │   ││
│  │  └────┘  │  │  │         ╭────────────────────────╮                   │   ││
│  │          │  │  │  $550 ──│                   ╭────╯                   │   ││
│  │  ┌────┐  │  │  │  $525 ──│              ╭────╯                        │   ││
│  │  │ 💰 │  │  │  │  $500 ──├──────────────╯                             │   ││
│  │  │Cryp│  │  │  │         Mon   Tue   Wed   Thu   Fri                  │   ││
│  │  │to  │  │  │  │                                                      │   ││
│  │  └────┘  │  │  └──────────────────────────────────────────────────────┘   ││
│  │          │  │                                                              ││
│  │  ┌────┐  │  │  ┌────────────────────────┐  ┌────────────────────────────┐ ││
│  │  │ 🔄 │  │  │  │   OPEN POSITIONS       │  │   RECENT ACTIVITY          │ ││
│  │  │Swap│  │  │  │                        │  │                            │ ││
│  │  └────┘  │  │  │  AAPL  $181.20 ▲+1.51% │  │  10:34 AAPL BUY executed  │ ││
│  │          │  │  │  MSFT  $415.80 ▲+0.92% │  │  10:22 NVDA REJECTED 42%  │ ││
│  │  ┌────┐  │  │  │  BTC   $67,450 ▼-0.34% │  │  09:45 MSFT signal gen'd  │ ││
│  │  │ ⚙️ │  │  │  │                        │  │  09:30 Market opened      │ ││
│  │  │Set-│  │  │  │                        │  │                            │ ││
│  │  │ting│  │  │  └────────────────────────┘  └────────────────────────────┘ ││
│  │  └────┘  │  │                                                              ││
│  │          │  │  ┌──────────────────────────────────────────────────────┐   ││
│  │ ┌──────┐ │  │  │  ╭───────────╮    ╭───────────╮                      │   ││
│  │ │START │ │  │  │  │   START   │    │   STOP    │    Mode: PAPER      │   ││
│  │ │Btn  │ │  │  │  ╰───────────╯    ╰───────────╯                      │   ││
│  │ └──────┘ │  │  └──────────────────────────────────────────────────────┘   ││
│  └──────────┘  └──────────────────────────────────────────────────────────────┘│
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### GUI Implementation

### Directory Structure for Frontend

```
leviathan/
├── frontend/                    # All web frontend files
│   ├── index.html              # Main dashboard HTML
│   ├── css/
│   │   ├── main.css            # Custom styles
│   │   └── components.css      # Component library
│   ├── js/
│   │   ├── app.js              # Main application logic
│   │   ├── api.js              # Python bridge wrapper
│   │   ├── charts.js           # Chart configurations
│   │   └── components.js       # UI components
│   └── assets/
│       ├── icons/              # SVG icons
│       └── images/             # Logo, etc.
├── gui/
│   ├── __init__.py
│   ├── app.py                  # PyWebView app launcher
│   ├── api.py                  # Python API class for JS bridge
│   └── windows/
│       ├── __init__.py
│       ├── main_window.py      # Main dashboard window
│       ├── settings_window.py  # Settings modal
│       ├── training_window.py  # Training interface
│       ├── crypto_swap_window.py
│       └── analytics_window.py
└── main.py                     # Entry point
```

### Main HTML Template (index.html)

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LEVIATHAN - AI Trading System</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- ApexCharts for graphs -->
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    
    <!-- Custom Tailwind Config -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'bg-primary': '#0a0a0f',
                        'bg-secondary': '#12121a',
                        'bg-tertiary': '#1a1a24',
                        'bg-quaternary': '#22222e',
                        'accent-purple': '#8b5cf6',
                        'accent-purple-hover': '#7c3aed',
                        'accent-blue': '#3b82f6',
                        'accent-cyan': '#06b6d4',
                        'border-color': '#2d2d3a',
                        'border-hover': '#3d3d4a',
                    },
                    fontFamily: {
                        'inter': ['Inter', 'sans-serif'],
                    },
                    borderRadius: {
                        'xl': '12px',
                        '2xl': '16px',
                        '3xl': '20px',
                    },
                    boxShadow: {
                        'glow-purple': '0 4px 14px rgba(139, 92, 246, 0.4)',
                        'glow-green': '0 4px 14px rgba(34, 197, 94, 0.4)',
                        'glow-red': '0 4px 14px rgba(239, 68, 68, 0.4)',
                    }
                }
            }
        }
    </script>
    
    <style>
        /* Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0a0a0f;
            color: #ffffff;
            overflow: hidden;
        }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #12121a;
        }
        ::-webkit-scrollbar-thumb {
            background: #3d3d4a;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #4d4d5a;
        }
        
        /* Animations */
        @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
            50% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        }
        .pulse-running {
            animation: pulse-green 2s infinite;
        }
        
        /* Card hover effect */
        .card-hover {
            transition: all 0.2s ease;
        }
        .card-hover:hover {
            transform: translateY(-2px);
            border-color: #3d3d4a;
        }
        
        /* Gradient text */
        .gradient-text {
            background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body class="bg-bg-primary min-h-screen">
    <div class="flex h-screen">
        
        <!-- Sidebar -->
        <aside class="w-20 bg-bg-secondary border-r border-border-color flex flex-col items-center py-6">
            <!-- Logo -->
            <div class="mb-8">
                <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-accent-purple to-accent-cyan flex items-center justify-center">
                    <span class="text-xl font-bold">L</span>
                </div>
            </div>
            
            <!-- Navigation -->
            <nav class="flex flex-col gap-4 flex-1">
                <button onclick="showPage('dashboard')" class="nav-btn active" title="Dashboard">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                    </svg>
                </button>
                <button onclick="showPage('analytics')" class="nav-btn" title="Analytics">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>
                </button>
                <button onclick="showPage('crypto')" class="nav-btn" title="Crypto">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </button>
                <button onclick="showPage('options')" class="nav-btn" title="Options">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
                    </svg>
                </button>
                <button onclick="showPage('training')" class="nav-btn" title="Training">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                    </svg>
                </button>
            </nav>
            
            <!-- Settings at bottom -->
            <button onclick="openSettings()" class="nav-btn" title="Settings">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
            </button>
        </aside>
        
        <!-- Main Content -->
        <main class="flex-1 overflow-y-auto p-6">
            <!-- Header -->
            <header class="flex justify-between items-center mb-6">
                <div>
                    <h1 class="text-2xl font-bold gradient-text">LEVIATHAN</h1>
                    <p class="text-gray-500 text-sm">Autonomous AI Trading System</p>
                </div>
                <div class="flex items-center gap-4">
                    <!-- Status Badge -->
                    <div id="status-badge" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-bg-secondary border border-border-color">
                        <span id="status-dot" class="w-2 h-2 rounded-full bg-gray-500"></span>
                        <span id="status-text" class="text-sm font-medium">STOPPED</span>
                    </div>
                    <!-- Mode Toggle -->
                    <div class="flex items-center gap-2 px-4 py-2 rounded-xl bg-bg-secondary border border-border-color">
                        <span class="text-sm text-gray-400">Mode:</span>
                        <span id="mode-text" class="text-sm font-medium text-yellow-500">PAPER</span>
                    </div>
                </div>
            </header>
            
            <!-- Stats Cards Row -->
            <div class="grid grid-cols-4 gap-4 mb-6">
                <!-- Portfolio Value -->
                <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color card-hover">
                    <p class="text-gray-500 text-xs uppercase tracking-wide mb-2">Portfolio Value</p>
                    <h2 id="portfolio-value" class="text-3xl font-bold">$0.00</h2>
                    <div class="flex items-center gap-2 mt-2">
                        <span id="portfolio-change" class="text-sm font-medium text-green-500">+0.00%</span>
                        <span class="text-xs text-gray-500">all time</span>
                    </div>
                </div>
                
                <!-- Today's P&L -->
                <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color card-hover">
                    <p class="text-gray-500 text-xs uppercase tracking-wide mb-2">Today's P&L</p>
                    <h2 id="today-pnl" class="text-3xl font-bold">$0.00</h2>
                    <div class="flex items-center gap-2 mt-2">
                        <span id="today-pnl-pct" class="text-sm font-medium text-green-500">+0.00%</span>
                        <span class="text-xs text-gray-500">today</span>
                    </div>
                </div>
                
                <!-- Opus Brain -->
                <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color card-hover">
                    <p class="text-gray-500 text-xs uppercase tracking-wide mb-2">Opus Brain</p>
                    <h2 id="opus-decisions" class="text-3xl font-bold">0</h2>
                    <div class="flex items-center gap-2 mt-2">
                        <span class="text-sm text-gray-400">decisions</span>
                        <span class="text-xs text-gray-500">•</span>
                        <span id="opus-cost" class="text-sm text-gray-400">$0.00 cost</span>
                    </div>
                </div>
                
                <!-- Win Rate -->
                <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color card-hover">
                    <p class="text-gray-500 text-xs uppercase tracking-wide mb-2">Win Rate</p>
                    <h2 id="win-rate" class="text-3xl font-bold">0%</h2>
                    <div class="flex items-center gap-2 mt-2">
                        <span id="win-loss" class="text-sm text-gray-400">0W / 0L</span>
                    </div>
                </div>
            </div>
            
            <!-- Chart & Positions Row -->
            <div class="grid grid-cols-3 gap-4 mb-6">
                <!-- Performance Chart -->
                <div class="col-span-2 bg-bg-secondary rounded-2xl p-5 border border-border-color">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-semibold">Portfolio Performance</h3>
                        <div class="flex gap-2">
                            <button class="px-3 py-1 text-xs rounded-lg bg-accent-purple/20 text-accent-purple">1W</button>
                            <button class="px-3 py-1 text-xs rounded-lg hover:bg-bg-tertiary text-gray-400">1M</button>
                            <button class="px-3 py-1 text-xs rounded-lg hover:bg-bg-tertiary text-gray-400">3M</button>
                            <button class="px-3 py-1 text-xs rounded-lg hover:bg-bg-tertiary text-gray-400">ALL</button>
                        </div>
                    </div>
                    <div id="performance-chart" class="h-64"></div>
                </div>
                
                <!-- Open Positions -->
                <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color">
                    <h3 class="text-lg font-semibold mb-4">Open Positions</h3>
                    <div id="positions-list" class="space-y-3 max-h-64 overflow-y-auto">
                        <div class="text-gray-500 text-sm text-center py-8">No open positions</div>
                    </div>
                </div>
            </div>
            
            <!-- Activity & Controls Row -->
            <div class="grid grid-cols-3 gap-4">
                <!-- Recent Activity -->
                <div class="col-span-2 bg-bg-secondary rounded-2xl p-5 border border-border-color">
                    <h3 class="text-lg font-semibold mb-4">Recent Activity</h3>
                    <div id="activity-log" class="space-y-2 max-h-48 overflow-y-auto">
                        <div class="text-gray-500 text-sm text-center py-4">No recent activity</div>
                    </div>
                </div>
                
                <!-- Controls -->
                <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color">
                    <h3 class="text-lg font-semibold mb-4">Controls</h3>
                    <div class="space-y-3">
                        <button id="start-btn" onclick="startTrading()" class="w-full py-4 rounded-xl bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold text-lg shadow-glow-green hover:shadow-lg transition-all hover:-translate-y-0.5">
                            ▶ START
                        </button>
                        <button id="stop-btn" onclick="stopTrading()" disabled class="w-full py-4 rounded-xl bg-bg-quaternary text-gray-500 font-semibold text-lg cursor-not-allowed">
                            ⏹ STOP
                        </button>
                        <div class="grid grid-cols-2 gap-2 mt-4">
                            <button onclick="openCryptoSwap()" class="py-2 rounded-lg bg-bg-tertiary hover:bg-bg-quaternary text-sm font-medium transition-colors">
                                🔄 Swap
                            </button>
                            <button onclick="openAutopilot()" class="py-2 rounded-lg bg-bg-tertiary hover:bg-bg-quaternary text-sm font-medium transition-colors">
                                🤖 Autopilot
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <style>
        /* Navigation Button Styles */
        .nav-btn {
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            color: #6b7280;
            transition: all 0.2s ease;
            border: none;
            background: transparent;
            cursor: pointer;
        }
        .nav-btn:hover {
            background: #1a1a24;
            color: #ffffff;
        }
        .nav-btn.active {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(6, 182, 212, 0.1) 100%);
            color: #8b5cf6;
        }
    </style>
    
    <script>
        // ============================================
        // PYTHON BRIDGE - Communication with backend
        // ============================================
        
        async function callPython(method, ...args) {
            try {
                const result = await window.pywebview.api[method](...args);
                return typeof result === 'string' ? JSON.parse(result) : result;
            } catch (error) {
                console.error(`Error calling ${method}:`, error);
                return null;
            }
        }
        
        // ============================================
        // TRADING CONTROLS
        // ============================================
        
        async function startTrading() {
            const result = await callPython('start_trading');
            if (result && result.status === 'running') {
                updateStatus('running');
                document.getElementById('start-btn').disabled = true;
                document.getElementById('start-btn').className = 'w-full py-4 rounded-xl bg-bg-quaternary text-gray-500 font-semibold text-lg cursor-not-allowed';
                document.getElementById('stop-btn').disabled = false;
                document.getElementById('stop-btn').className = 'w-full py-4 rounded-xl bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold text-lg shadow-glow-red hover:shadow-lg transition-all hover:-translate-y-0.5';
                addActivity('SYSTEM', 'Trading started - Opus brain active');
            }
        }
        
        async function stopTrading() {
            const result = await callPython('stop_trading');
            if (result && result.status === 'stopped') {
                updateStatus('stopped');
                document.getElementById('start-btn').disabled = false;
                document.getElementById('start-btn').className = 'w-full py-4 rounded-xl bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold text-lg shadow-glow-green hover:shadow-lg transition-all hover:-translate-y-0.5';
                document.getElementById('stop-btn').disabled = true;
                document.getElementById('stop-btn').className = 'w-full py-4 rounded-xl bg-bg-quaternary text-gray-500 font-semibold text-lg cursor-not-allowed';
                addActivity('SYSTEM', 'Trading stopped - all orders cancelled');
            }
        }
        
        // ============================================
        // UI UPDATE FUNCTIONS
        // ============================================
        
        function updateStatus(status) {
            const dot = document.getElementById('status-dot');
            const text = document.getElementById('status-text');
            const badge = document.getElementById('status-badge');
            
            if (status === 'running') {
                dot.className = 'w-2 h-2 rounded-full bg-green-500 pulse-running';
                text.textContent = 'RUNNING';
                text.className = 'text-sm font-medium text-green-500';
            } else {
                dot.className = 'w-2 h-2 rounded-full bg-gray-500';
                text.textContent = 'STOPPED';
                text.className = 'text-sm font-medium text-gray-400';
            }
        }
        
        function updatePortfolio(data) {
            document.getElementById('portfolio-value').textContent = `$${data.balance.toFixed(2)}`;
            
            const changeEl = document.getElementById('portfolio-change');
            changeEl.textContent = `${data.total_pnl_pct >= 0 ? '+' : ''}${data.total_pnl_pct.toFixed(2)}%`;
            changeEl.className = `text-sm font-medium ${data.total_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`;
            
            document.getElementById('today-pnl').textContent = `$${data.today_pnl.toFixed(2)}`;
            
            const todayPctEl = document.getElementById('today-pnl-pct');
            todayPctEl.textContent = `${data.today_pnl_pct >= 0 ? '+' : ''}${data.today_pnl_pct.toFixed(2)}%`;
            todayPctEl.className = `text-sm font-medium ${data.today_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`;
            
            document.getElementById('opus-decisions').textContent = data.opus_decisions;
            document.getElementById('opus-cost').textContent = `$${data.opus_cost.toFixed(2)} cost`;
            document.getElementById('win-rate').textContent = `${data.win_rate.toFixed(0)}%`;
            document.getElementById('win-loss').textContent = `${data.wins}W / ${data.losses}L`;
        }
        
        function updatePositions(positions) {
            const container = document.getElementById('positions-list');
            
            if (!positions || positions.length === 0) {
                container.innerHTML = '<div class="text-gray-500 text-sm text-center py-8">No open positions</div>';
                return;
            }
            
            container.innerHTML = positions.map(p => `
                <div class="flex items-center justify-between p-3 rounded-xl bg-bg-tertiary">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                            <span class="text-xs font-bold text-accent-purple">${p.symbol.slice(0, 2)}</span>
                        </div>
                        <div>
                            <p class="font-medium">${p.symbol}</p>
                            <p class="text-xs text-gray-500">${p.qty} shares</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-medium">$${p.current_price.toFixed(2)}</p>
                        <p class="text-xs ${p.pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}">
                            ${p.pnl_pct >= 0 ? '▲' : '▼'} ${Math.abs(p.pnl_pct).toFixed(2)}%
                        </p>
                    </div>
                </div>
            `).join('');
        }
        
        function addActivity(type, message) {
            const container = document.getElementById('activity-log');
            const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            
            const typeColors = {
                'SYSTEM': 'text-blue-400',
                'OPUS': 'text-purple-400',
                'TRADE': 'text-green-400',
                'ERROR': 'text-red-400',
                'WARNING': 'text-yellow-400'
            };
            
            const entry = document.createElement('div');
            entry.className = 'flex items-start gap-3 p-2 rounded-lg hover:bg-bg-tertiary';
            entry.innerHTML = `
                <span class="text-xs text-gray-500 whitespace-nowrap">${now}</span>
                <span class="text-xs font-medium ${typeColors[type] || 'text-gray-400'}">${type}</span>
                <span class="text-sm text-gray-300">${message}</span>
            `;
            
            // Remove "no activity" placeholder if present
            const placeholder = container.querySelector('.text-center');
            if (placeholder) placeholder.remove();
            
            container.insertBefore(entry, container.firstChild);
            
            // Keep only last 50 entries
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }
        
        // ============================================
        // CHARTS
        // ============================================
        
        let performanceChart = null;
        
        function initChart() {
            const options = {
                series: [{
                    name: 'Portfolio Value',
                    data: []
                }],
                chart: {
                    type: 'area',
                    height: 256,
                    background: 'transparent',
                    toolbar: { show: false },
                    zoom: { enabled: false },
                    animations: {
                        enabled: true,
                        easing: 'easeinout',
                        speed: 800
                    }
                },
                colors: ['#8b5cf6'],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shadeIntensity: 1,
                        opacityFrom: 0.4,
                        opacityTo: 0.05,
                        stops: [0, 100]
                    }
                },
                stroke: {
                    curve: 'smooth',
                    width: 3
                },
                dataLabels: { enabled: false },
                grid: {
                    borderColor: '#2d2d3a',
                    strokeDashArray: 4,
                    xaxis: { lines: { show: false } },
                    yaxis: { lines: { show: true } }
                },
                xaxis: {
                    type: 'datetime',
                    labels: {
                        style: { colors: '#6b7280' }
                    },
                    axisBorder: { show: false },
                    axisTicks: { show: false }
                },
                yaxis: {
                    labels: {
                        style: { colors: '#6b7280' },
                        formatter: (val) => `$${val.toFixed(0)}`
                    }
                },
                tooltip: {
                    theme: 'dark',
                    x: { format: 'MMM dd, HH:mm' },
                    y: { formatter: (val) => `$${val.toFixed(2)}` }
                }
            };
            
            performanceChart = new ApexCharts(document.getElementById('performance-chart'), options);
            performanceChart.render();
        }
        
        function updateChart(data) {
            if (performanceChart && data.length > 0) {
                performanceChart.updateSeries([{
                    name: 'Portfolio Value',
                    data: data.map(d => ({ x: new Date(d.timestamp), y: d.value }))
                }]);
            }
        }
        
        // ============================================
        // DATA REFRESH LOOP
        // ============================================
        
        async function refreshData() {
            try {
                const data = await callPython('get_dashboard_data');
                if (data) {
                    updatePortfolio(data.portfolio);
                    updatePositions(data.positions);
                    updateChart(data.chart_data);
                    
                    // Update status based on trading state
                    updateStatus(data.is_running ? 'running' : 'stopped');
                }
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        // ============================================
        // NAVIGATION & MODALS
        // ============================================
        
        function showPage(page) {
            // Update nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            // In a full implementation, this would switch between different page views
            console.log('Navigate to:', page);
        }
        
        function openSettings() {
            callPython('open_settings');
        }
        
        function openCryptoSwap() {
            callPython('open_crypto_swap');
        }
        
        function openAutopilot() {
            callPython('open_autopilot');
        }
        
        // ============================================
        // INITIALIZATION
        // ============================================
        
        document.addEventListener('DOMContentLoaded', () => {
            initChart();
            refreshData();
            
            // Refresh data every 5 seconds
            setInterval(refreshData, 5000);
        });
    </script>
</body>
</html>
```

### Python Backend API (gui/api.py)

```python
# gui/api.py
"""
Python API class for PyWebView JS bridge.
All methods here can be called from JavaScript via window.pywebview.api.methodName()
"""

import json
from datetime import datetime, timedelta
from typing import Optional
import threading

class LeviathanAPI:
    """
    API class that exposes Python functions to the JavaScript frontend.
    This is the bridge between the beautiful UI and the trading engine.
    """
    
    def __init__(self, trading_engine, learning_db, state_db):
        self.engine = trading_engine
        self.learning_db = learning_db
        self.state_db = state_db
        self.is_running = False
        self.trading_thread: Optional[threading.Thread] = None
        self._activity_log = []
        
    # ============================================
    # TRADING CONTROLS
    # ============================================
    
    def start_trading(self) -> str:
        """Start autonomous trading"""
        if self.is_running:
            return json.dumps({'status': 'already_running'})
        
        self.is_running = True
        self._log_activity('SYSTEM', 'Trading started - Opus brain initializing...')
        
        # Start trading loop in background thread
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        
        return json.dumps({'status': 'running'})
    
    def stop_trading(self) -> str:
        """Stop autonomous trading"""
        if not self.is_running:
            return json.dumps({'status': 'already_stopped'})
        
        self.is_running = False
        self._log_activity('SYSTEM', 'Stopping trading - cancelling open orders...')
        
        # Cancel any open orders
        try:
            self.engine.cancel_all_orders()
            self._log_activity('SYSTEM', 'All open orders cancelled successfully')
        except Exception as e:
            self._log_activity('ERROR', f'Failed to cancel orders: {str(e)}')
        
        return json.dumps({'status': 'stopped'})
    
    def _trading_loop(self):
        """Main trading loop (runs in background thread)"""
        import time
        
        self._log_activity('OPUS', 'Opus brain active - scanning for opportunities...')
        
        while self.is_running:
            try:
                # Run one trading cycle
                result = self.engine.run_cycle()
                
                if result:
                    if result.get('trade_executed'):
                        self._log_activity('TRADE', 
                            f"{result['action']} {result['symbol']} - {result['reason']}")
                    elif result.get('signal_generated'):
                        self._log_activity('OPUS', 
                            f"Signal for {result['symbol']} - confidence {result['confidence']}%")
                
            except Exception as e:
                self._log_activity('ERROR', f'Trading cycle error: {str(e)}')
            
            # Sleep between cycles (60 seconds default)
            time.sleep(60)
    
    # ============================================
    # DASHBOARD DATA
    # ============================================
    
    def get_dashboard_data(self) -> str:
        """Get all data needed for the dashboard"""
        try:
            # Get account info
            account = self.engine.alpaca.get_account()
            
            # Get positions
            positions = self.engine.alpaca.get_positions()
            positions_data = []
            for p in positions:
                positions_data.append({
                    'symbol': p.symbol,
                    'qty': float(p.qty),
                    'entry_price': float(p.avg_entry_price),
                    'current_price': float(p.current_price),
                    'pnl': float(p.unrealized_pl),
                    'pnl_pct': float(p.unrealized_plpc) * 100
                })
            
            # Get performance stats
            stats = self.learning_db.get_performance_stats()
            
            # Get chart data (last 7 days)
            chart_data = self.state_db.get_portfolio_history(days=7)
            
            return json.dumps({
                'portfolio': {
                    'balance': float(account.equity),
                    'buying_power': float(account.buying_power),
                    'today_pnl': float(account.equity) - float(account.last_equity),
                    'today_pnl_pct': ((float(account.equity) / float(account.last_equity)) - 1) * 100 if float(account.last_equity) > 0 else 0,
                    'total_pnl_pct': stats.get('total_return_pct', 0),
                    'opus_decisions': stats.get('total_decisions', 0),
                    'opus_cost': stats.get('total_api_cost', 0),
                    'win_rate': stats.get('win_rate', 0),
                    'wins': stats.get('wins', 0),
                    'losses': stats.get('losses', 0)
                },
                'positions': positions_data,
                'chart_data': chart_data,
                'is_running': self.is_running,
                'mode': 'PAPER' if self.engine.paper_mode else 'LIVE'
            })
            
        except Exception as e:
            return json.dumps({
                'error': str(e),
                'portfolio': {
                    'balance': 0, 'buying_power': 0, 'today_pnl': 0,
                    'today_pnl_pct': 0, 'total_pnl_pct': 0, 'opus_decisions': 0,
                    'opus_cost': 0, 'win_rate': 0, 'wins': 0, 'losses': 0
                },
                'positions': [],
                'chart_data': [],
                'is_running': self.is_running,
                'mode': 'PAPER'
            })
    
    def get_activity_log(self) -> str:
        """Get recent activity entries"""
        return json.dumps(self._activity_log[-50:])  # Last 50 entries
    
    # ============================================
    # WINDOWS & MODALS
    # ============================================
    
    def open_settings(self):
        """Open settings window"""
        # This will be implemented with a separate webview window
        self._log_activity('SYSTEM', 'Settings window opened')
        return json.dumps({'status': 'opened'})
    
    def open_crypto_swap(self):
        """Open crypto swap window"""
        self._log_activity('SYSTEM', 'Crypto swap window opened')
        return json.dumps({'status': 'opened'})
    
    def open_autopilot(self):
        """Open portfolio autopilot window"""
        self._log_activity('SYSTEM', 'Portfolio autopilot window opened')
        return json.dumps({'status': 'opened'})
    
    def open_training(self):
        """Open training window"""
        self._log_activity('SYSTEM', 'Training window opened')
        return json.dumps({'status': 'opened'})
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _log_activity(self, activity_type: str, message: str):
        """Add entry to activity log"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'message': message
        }
        self._activity_log.append(entry)
        
        # Keep only last 100 entries in memory
        if len(self._activity_log) > 100:
            self._activity_log = self._activity_log[-100:]
```

### Main Application Entry Point (gui/app.py)

```python
# gui/app.py
"""
Main PyWebView application launcher.
Creates the desktop window and loads the frontend.
"""

import webview
import os
import sys
from pathlib import Path

from gui.api import LeviathanAPI

class LeviathanApp:
    """Main application class"""
    
    def __init__(self, trading_engine, learning_db, state_db, debug=False):
        self.trading_engine = trading_engine
        self.learning_db = learning_db
        self.state_db = state_db
        self.debug = debug
        
        # Create API instance
        self.api = LeviathanAPI(trading_engine, learning_db, state_db)
        
        # Get frontend path
        self.frontend_path = self._get_frontend_path()
        
    def _get_frontend_path(self) -> str:
        """Get the path to the frontend HTML file"""
        # When running from source
        base_path = Path(__file__).parent.parent
        frontend_path = base_path / 'frontend' / 'index.html'
        
        if frontend_path.exists():
            return str(frontend_path)
        
        # When running as packaged exe
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            frontend_path = base_path / 'frontend' / 'index.html'
            if frontend_path.exists():
                return str(frontend_path)
        
        raise FileNotFoundError("Frontend HTML file not found")
    
    def run(self):
        """Launch the application"""
        # Window settings
        window = webview.create_window(
            title='LEVIATHAN - AI Trading System',
            url=self.frontend_path,
            js_api=self.api,
            width=1400,
            height=900,
            min_size=(1200, 700),
            background_color='#0a0a0f',
            text_select=False,
            confirm_close=True
        )
        
        # Start webview
        webview.start(
            debug=self.debug,
            http_server=True  # Needed for loading local files
        )


def launch_gui(trading_engine, learning_db, state_db, debug=False):
    """
    Convenience function to launch the GUI.
    Called from main.py
    """
    app = LeviathanApp(
        trading_engine=trading_engine,
        learning_db=learning_db,
        state_db=state_db,
        debug=debug
    )
    app.run()
```

### Updated Main Entry Point (main.py)

```python
# main.py
"""
LEVIATHAN - Autonomous AI Trading System
Main entry point
"""

import os
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    # Validate keys
    if not all([alpaca_key, alpaca_secret, anthropic_key]):
        print("ERROR: Missing API keys. Please check your .env file.")
        print("Required: ALPACA_API_KEY, ALPACA_SECRET_KEY, ANTHROPIC_API_KEY")
        sys.exit(1)
    
    # Import components (after env vars loaded)
    from core.alpaca_client import AlpacaClient
    from core.opus_brain import OpusTradingBrain
    from core.risk_manager import RiskManager
    from core.trading_engine import TradingEngine
    from data.learning_database import LearningDatabase
    from data.state_manager import StateManager
    from gui.app import launch_gui
    
    # Configuration
    paper_mode = os.getenv('PAPER_MODE', 'true').lower() == 'true'
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    starting_capital = float(os.getenv('STARTING_CAPITAL', '500'))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     ██╗     ███████╗██╗   ██╗██╗ █████╗ ████████╗██╗  ██╗    ║
    ║     ██║     ██╔════╝██║   ██║██║██╔══██╗╚══██╔══╝██║  ██║    ║
    ║     ██║     █████╗  ██║   ██║██║███████║   ██║   ███████║    ║
    ║     ██║     ██╔══╝  ╚██╗ ██╔╝██║██╔══██║   ██║   ██╔══██║    ║
    ║     ███████╗███████╗ ╚████╔╝ ██║██║  ██║   ██║   ██║  ██║    ║
    ║     ╚══════╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ║
    ║                                                               ║
    ║              Autonomous AI Trading System                     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    Mode: {'PAPER TRADING' if paper_mode else '🔴 LIVE TRADING'}
    Starting Capital: ${starting_capital:,.2f}
    Debug: {debug_mode}
    """)
    
    # Create component instances
    print("Initializing components...")
    
    learning_db = LearningDatabase()
    state_db = StateManager()
    
    alpaca = AlpacaClient(
        api_key=alpaca_key,
        secret_key=alpaca_secret,
        paper=paper_mode
    )
    
    risk_manager = RiskManager(starting_capital=starting_capital)
    
    opus_brain = OpusTradingBrain(
        api_key=anthropic_key,
        learning_db=learning_db,
        risk_manager=risk_manager
    )
    
    trading_engine = TradingEngine(
        alpaca_client=alpaca,
        opus_brain=opus_brain,
        risk_manager=risk_manager,
        learning_db=learning_db,
        state_db=state_db,
        paper_mode=paper_mode
    )
    
    print("Components initialized successfully!")
    print("Launching GUI...")
    
    # Launch GUI
    launch_gui(
        trading_engine=trading_engine,
        learning_db=learning_db,
        state_db=state_db,
        debug=debug_mode
    )

if __name__ == "__main__":
    main()
```

### Requirements Update

Add to requirements.txt:
```
pywebview>=4.4.0
```

### Building as Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name="Leviathan" \
    --windowed \
    --icon=frontend/assets/icons/logo.ico \
    --add-data="frontend;frontend" \
    --hidden-import=webview \
    --hidden-import=clr \
    main.py
```

### Additional GUI Windows (HTML Templates)

The following additional windows use the same PyWebView + HTML/CSS approach:

**Training Window (frontend/training.html):**
- Historical data training controls
- Manual training input
- Model retraining buttons
- Learning database statistics
- Training history view

**Crypto Swap Window (frontend/crypto_swap.html):**
- From/To crypto selectors
- Amount input
- Optimal path finder
- Fee estimation display
- Execute swap button with status

**Settings Window (frontend/settings.html):**
- API key configuration
- Risk management settings
- Trading preferences
- Paper/Live mode toggle
- Notification settings

**Analytics Window (frontend/analytics.html):**
- Detailed performance charts
- Trade history table
- Win/loss analysis
- Sector breakdown
- Opus decision log

All windows follow the same design system colors, typography, and component styles defined above.

### Icon Assets

Create SVG icons for the sidebar navigation. Store in `frontend/assets/icons/`:
- home.svg
- analytics.svg
- crypto.svg
- options.svg
- training.svg
- settings.svg

Use consistent 24x24 viewBox with currentColor for dynamic coloring.

### Notes for Claude Code Implementation

1. **Start with the main dashboard** - Get the core HTML/CSS/JS working first
2. **Use Tailwind CDN initially** - Can compile later for production
3. **Test the Python bridge** - Ensure JS ↔ Python communication works
4. **Add charts incrementally** - Start with static data, then add real-time updates
5. **Match the Figma exactly** - Use the prototype as the visual spec

---

## Additional Features for Ultimate Trading Platform

### 1. Cryptocurrency Trading Module (24/7, PDT-Exempt)

**CRITICAL:** Crypto is exempt from PDT rules. This lets small accounts day trade freely. Must be a core feature.

**SUPPORTED CRYPTOCURRENCIES (26 total):**
- **Major:** BTC, ETH, SOL, XRP, DOGE, LTC, BCH
- **DeFi/Altcoins:** LINK, UNI, AAVE, AVAX, DOT, ATOM, ALGO
- **Meme coins:** SHIB, PEPE
- **Stablecoins:** USDC, USDT, USDG
- **Others:** XLM, XTZ, FIL, ETC, MANA, SAND, MKR

**AVAILABLE TRADING PAIRS (56+):**
- **USD pairs (25):** BTC/USD, ETH/USD, SOL/USD, DOGE/USD, XRP/USD, etc.
- **USDC pairs (18):** BTC/USDC, ETH/USDC, AVAX/USDC, DOT/USDC, etc.
- **USDT pairs (10):** BTC/USDT, ETH/USDT, LINK/USDT, UNI/USDT, etc.
- **BTC pairs (4):** ETH/BTC, BCH/BTC, LTC/BTC, UNI/BTC

```python
# crypto/crypto_trader.py

class CryptoTrader:
    """
    Cryptocurrency trading module.
    - 24/7 trading (no market hours restrictions)
    - PDT exempt (unlimited day trades)
    - Higher volatility = more opportunities
    """
    
    SUPPORTED_CRYPTOS = [
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'SHIB/USD',
        'AVAX/USD', 'DOT/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD',
        'LTC/USD', 'BCH/USD', 'XLM/USD', 'ALGO/USD', 'ATOM/USD',
        'FIL/USD', 'ETC/USD', 'XTZ/USD', 'MANA/USD', 'SAND/USD'
    ]
    
    def __init__(self, alpaca_client, opus_brain):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        
    def get_crypto_opportunities(self) -> list:
        """Scan all cryptos for trading opportunities"""
        opportunities = []
        
        for symbol in self.SUPPORTED_CRYPTOS:
            data = self.alpaca.get_crypto_bars(symbol, timeframe='1Hour', limit=100)
            signal = self._analyze_crypto(symbol, data)
            if signal['strength'] > 0.6:
                opportunities.append(signal)
                
        return sorted(opportunities, key=lambda x: x['strength'], reverse=True)
    
    def _analyze_crypto(self, symbol: str, data: pd.DataFrame) -> dict:
        """
        Crypto-specific analysis.
        Higher volatility tolerance, momentum-focused.
        """
        # Crypto moves faster - use shorter timeframes
        rsi = ta.rsi(data['close'], length=7)  # Faster RSI
        macd = ta.macd(data['close'], fast=8, slow=21, signal=5)  # Faster MACD
        
        # Volatility is normal in crypto - embrace it
        volatility = data['close'].pct_change().std() * np.sqrt(24)  # Daily vol
        
        signal_strength = 0.0
        
        # RSI extremes (works well in crypto)
        if rsi.iloc[-1] < 25:
            signal_strength += 0.4
        elif rsi.iloc[-1] > 75:
            signal_strength -= 0.4
            
        # MACD crossover
        if macd['MACD_8_21_5'].iloc[-1] > macd['MACDs_8_21_5'].iloc[-1]:
            signal_strength += 0.3
            
        # Volume spike
        volume_ratio = data['volume'].iloc[-1] / data['volume'].rolling(20).mean().iloc[-1]
        if volume_ratio > 2.0:
            signal_strength += 0.2
            
        return {
            'symbol': symbol,
            'strength': abs(signal_strength),
            'direction': 'long' if signal_strength > 0 else 'short',
            'volatility': volatility,
            'rsi': rsi.iloc[-1],
            'volume_ratio': volume_ratio
        }


class CryptoSwapOptimizer:
    """
    Finds the optimal path to swap between any two cryptocurrencies.
    
    Example: User has DOGE, wants ETH
    - Direct path: DOGE/ETH (doesn't exist)
    - Optimal path: DOGE → USD → ETH (2 trades)
    - Alternative: DOGE → BTC → ETH (2 trades, compare fees)
    
    The optimizer calculates the best route based on:
    1. Number of hops (fewer = better)
    2. Total fees
    3. Slippage estimates
    4. Available liquidity
    """
    
    # All available trading pairs on Alpaca
    TRADING_PAIRS = {
        # USD pairs
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD', 'LTC/USD',
        'BCH/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD', 'AVAX/USD', 'DOT/USD',
        'ATOM/USD', 'ALGO/USD', 'SHIB/USD', 'PEPE/USD', 'XLM/USD', 'XTZ/USD',
        'FIL/USD', 'ETC/USD', 'MANA/USD', 'SAND/USD', 'MKR/USD', 'USDC/USD', 'USDT/USD',
        # USDC pairs
        'BTC/USDC', 'ETH/USDC', 'SOL/USDC', 'AVAX/USDC', 'DOT/USDC', 'LINK/USDC',
        'UNI/USDC', 'AAVE/USDC', 'ATOM/USDC', 'ALGO/USDC', 'XLM/USDC', 'XTZ/USDC',
        'FIL/USDC', 'ETC/USDC', 'MANA/USDC', 'SAND/USDC', 'MKR/USDC', 'LTC/USDC',
        # USDT pairs
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'LINK/USDT', 'UNI/USDT', 
        'AVAX/USDT', 'DOT/USDT', 'ATOM/USDT', 'XLM/USDT', 'LTC/USDT',
        # BTC pairs (crypto-to-crypto)
        'ETH/BTC', 'BCH/BTC', 'LTC/BTC', 'UNI/BTC'
    }
    
    # Bridge currencies for routing (most liquid)
    BRIDGE_CURRENCIES = ['USD', 'USDC', 'USDT', 'BTC']
    
    def __init__(self, alpaca_client):
        self.alpaca = alpaca_client
        self.pair_graph = self._build_pair_graph()
        self.fee_rate = 0.0025  # 0.25% taker fee (conservative estimate)
        
    def _build_pair_graph(self) -> dict:
        """
        Build a graph of all possible swaps.
        Each node is a currency, edges are trading pairs.
        """
        graph = {}
        
        for pair in self.TRADING_PAIRS:
            base, quote = pair.split('/')
            
            # Add both directions
            if base not in graph:
                graph[base] = {}
            if quote not in graph:
                graph[quote] = {}
                
            graph[base][quote] = {'pair': pair, 'direction': 'sell'}
            graph[quote][base] = {'pair': pair, 'direction': 'buy'}
            
        return graph
    
    def find_optimal_path(self, from_crypto: str, to_crypto: str, 
                          amount: float) -> dict:
        """
        Find the best path to swap from one crypto to another.
        
        Args:
            from_crypto: Source cryptocurrency (e.g., 'DOGE')
            to_crypto: Destination cryptocurrency (e.g., 'ETH')
            amount: Amount of source crypto to swap
            
        Returns:
            dict with optimal path, estimated output, fees, and execution plan
        """
        from_crypto = from_crypto.upper()
        to_crypto = to_crypto.upper()
        
        if from_crypto == to_crypto:
            return {'error': 'Source and destination are the same'}
            
        # Find all possible paths (max 3 hops to prevent crazy routes)
        all_paths = self._find_all_paths(from_crypto, to_crypto, max_hops=3)
        
        if not all_paths:
            return {
                'error': f'No trading path found between {from_crypto} and {to_crypto}',
                'suggestion': 'This crypto may not be supported or no valid pairs exist'
            }
        
        # Evaluate each path for cost/efficiency
        evaluated_paths = []
        for path in all_paths:
            evaluation = self._evaluate_path(path, amount)
            evaluated_paths.append(evaluation)
            
        # Sort by estimated output (highest = best)
        evaluated_paths.sort(key=lambda x: x['estimated_output'], reverse=True)
        
        best_path = evaluated_paths[0]
        
        return {
            'from': from_crypto,
            'to': to_crypto,
            'input_amount': amount,
            'optimal_path': best_path,
            'alternative_paths': evaluated_paths[1:3],  # Show top 3 alternatives
            'execution_plan': self._generate_execution_plan(best_path, amount)
        }
    
    def _find_all_paths(self, start: str, end: str, max_hops: int = 3) -> list:
        """
        BFS to find all paths between two currencies.
        """
        if start not in self.pair_graph or end not in self.pair_graph:
            return []
            
        paths = []
        queue = [(start, [start])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_hops + 1:
                continue
                
            if current == end and len(path) > 1:
                paths.append(path)
                continue
                
            for neighbor in self.pair_graph.get(current, {}):
                if neighbor not in path:  # Avoid cycles
                    queue.append((neighbor, path + [neighbor]))
                    
        return paths
    
    def _evaluate_path(self, path: list, amount: float) -> dict:
        """
        Evaluate a path's cost and estimated output.
        """
        current_amount = amount
        total_fees = 0
        trades = []
        
        for i in range(len(path) - 1):
            from_curr = path[i]
            to_curr = path[i + 1]
            
            edge = self.pair_graph[from_curr][to_curr]
            pair = edge['pair']
            direction = edge['direction']
            
            # Get current price
            price = self._get_price(pair)
            
            if price is None:
                return {'path': path, 'estimated_output': 0, 'error': f'Could not get price for {pair}'}
            
            # Calculate trade
            if direction == 'sell':
                # Selling base currency for quote
                output = current_amount * price
            else:
                # Buying base currency with quote
                output = current_amount / price
                
            # Apply fee
            fee = output * self.fee_rate
            output_after_fee = output - fee
            total_fees += fee
            
            trades.append({
                'pair': pair,
                'direction': direction,
                'input': current_amount,
                'output': output_after_fee,
                'price': price,
                'fee': fee
            })
            
            current_amount = output_after_fee
            
        return {
            'path': path,
            'path_string': ' → '.join(path),
            'num_hops': len(path) - 1,
            'trades': trades,
            'estimated_output': current_amount,
            'total_fees_usd': total_fees,  # Approximate
            'efficiency': current_amount / amount if amount > 0 else 0
        }
    
    def _get_price(self, pair: str) -> float:
        """Get current price for a trading pair"""
        try:
            quote = self.alpaca.get_crypto_quote(pair)
            return (quote['bid'] + quote['ask']) / 2  # Mid price
        except:
            return None
    
    def _generate_execution_plan(self, path_eval: dict, amount: float) -> list:
        """
        Generate step-by-step execution plan for Opus to follow.
        """
        plan = []
        
        for i, trade in enumerate(path_eval['trades']):
            plan.append({
                'step': i + 1,
                'action': 'SELL' if trade['direction'] == 'sell' else 'BUY',
                'pair': trade['pair'],
                'amount': trade['input'],
                'expected_output': trade['output'],
                'order_type': 'market',  # Use market for speed in swaps
                'note': f"Step {i+1} of {len(path_eval['trades'])}"
            })
            
        return plan
    
    def execute_swap(self, from_crypto: str, to_crypto: str, 
                     amount: float, opus_brain) -> dict:
        """
        Execute a multi-hop crypto swap.
        Opus oversees each step and can abort if something goes wrong.
        """
        # Find optimal path
        path_result = self.find_optimal_path(from_crypto, to_crypto, amount)
        
        if 'error' in path_result:
            return path_result
            
        execution_plan = path_result['execution_plan']
        results = []
        current_amount = amount
        
        for step in execution_plan:
            # Ask Opus to approve each step
            approval = opus_brain.approve_swap_step(step, current_amount, path_result)
            
            if not approval['approved']:
                return {
                    'status': 'aborted',
                    'reason': approval['reason'],
                    'completed_steps': results,
                    'remaining_amount': current_amount
                }
            
            # Execute the trade
            try:
                if step['action'] == 'SELL':
                    order = self.alpaca.submit_crypto_order(
                        symbol=step['pair'],
                        qty=current_amount,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                else:
                    order = self.alpaca.submit_crypto_order(
                        symbol=step['pair'],
                        notional=current_amount,  # Buy with notional amount
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                    )
                
                # Wait for fill
                filled_order = self._wait_for_fill(order.id)
                
                results.append({
                    'step': step['step'],
                    'order_id': order.id,
                    'status': 'filled',
                    'filled_qty': filled_order.filled_qty,
                    'filled_avg_price': filled_order.filled_avg_price
                })
                
                # Update current amount for next step
                current_amount = float(filled_order.filled_qty)
                
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'failed_step': step,
                    'completed_steps': results,
                    'remaining_amount': current_amount
                }
        
        return {
            'status': 'completed',
            'from': from_crypto,
            'to': to_crypto,
            'input_amount': amount,
            'output_amount': current_amount,
            'path': path_result['optimal_path']['path_string'],
            'steps_completed': len(results),
            'total_fees_paid': sum(r.get('fee', 0) for r in results)
        }
    
    def _wait_for_fill(self, order_id: str, timeout: int = 30) -> dict:
        """Wait for order to fill with timeout"""
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            order = self.alpaca.get_order(order_id)
            if order.status == 'filled':
                return order
            elif order.status in ['cancelled', 'expired', 'rejected']:
                raise Exception(f"Order {order_id} failed with status: {order.status}")
            time.sleep(0.5)
            
        raise Exception(f"Order {order_id} timed out after {timeout} seconds")


class CryptoPortfolioRebalancer:
    """
    Automatically rebalance crypto portfolio to target allocations.
    Uses the swap optimizer for efficient rebalancing.
    """
    
    def __init__(self, swap_optimizer: CryptoSwapOptimizer, opus_brain):
        self.optimizer = swap_optimizer
        self.opus = opus_brain
        
    def calculate_rebalance_trades(self, current_holdings: dict, 
                                    target_allocations: dict,
                                    total_value_usd: float) -> list:
        """
        Calculate trades needed to rebalance to target allocations.
        
        Args:
            current_holdings: {'BTC': 0.01, 'ETH': 0.5, 'USD': 100}
            target_allocations: {'BTC': 0.4, 'ETH': 0.4, 'SOL': 0.2}  # Must sum to 1.0
            total_value_usd: Total portfolio value in USD
            
        Returns:
            List of trades to execute
        """
        # Calculate current allocations
        current_values = {}
        for crypto, amount in current_holdings.items():
            if crypto == 'USD':
                current_values[crypto] = amount
            else:
                price = self._get_usd_price(crypto)
                current_values[crypto] = amount * price
                
        current_total = sum(current_values.values())
        current_allocations = {k: v/current_total for k, v in current_values.items()}
        
        # Calculate target values
        target_values = {k: v * total_value_usd for k, v in target_allocations.items()}
        
        # Calculate differences
        trades_needed = []
        
        for crypto, target_value in target_values.items():
            current_value = current_values.get(crypto, 0)
            diff = target_value - current_value
            
            if abs(diff) > 1:  # Only trade if difference > $1
                trades_needed.append({
                    'crypto': crypto,
                    'current_value': current_value,
                    'target_value': target_value,
                    'difference_usd': diff,
                    'action': 'buy' if diff > 0 else 'sell'
                })
        
        # Sort: sells first (to free up capital), then buys
        trades_needed.sort(key=lambda x: (x['action'] == 'buy', abs(x['difference_usd'])))
        
        return trades_needed
    
    def execute_rebalance(self, trades: list) -> dict:
        """Execute the rebalancing trades"""
        results = []
        
        for trade in trades:
            if trade['action'] == 'sell':
                # Sell to USD first
                result = self.optimizer.execute_swap(
                    trade['crypto'], 
                    'USD', 
                    abs(trade['difference_usd']) / self._get_usd_price(trade['crypto']),
                    self.opus
                )
            else:
                # Buy from USD
                result = self.optimizer.execute_swap(
                    'USD',
                    trade['crypto'],
                    trade['difference_usd'],
                    self.opus
                )
            results.append(result)
            
        return {
            'status': 'completed',
            'trades_executed': len(results),
            'results': results
        }
    
    def _get_usd_price(self, crypto: str) -> float:
        """Get USD price for a crypto"""
        pair = f"{crypto}/USD"
        quote = self.optimizer.alpaca.get_crypto_quote(pair)
        return (quote['bid'] + quote['ask']) / 2
```

### 2. Options Trading Module

**ALPACA OPTIONS CAPABILITIES:**
- Options Levels 1-3 available
- Supports: Single leg, spreads, iron condors
- Order types: Market, Limit, Stop-Limit
- Exercise: American style (can exercise anytime)
- Settlement: T+1

**STRATEGIES FOR SMALL ACCOUNTS (Defined Risk Only):**
- Bull Put Spread (bullish, collect premium)
- Bear Call Spread (bearish, collect premium)
- Iron Condor (neutral, profit from low volatility)
- Long Calls/Puts (directional bets, limited risk)
- Debit Spreads (directional with capped risk)

**NOT RECOMMENDED for small accounts:**
- Naked calls (unlimited risk)
- Naked puts (high risk)
- Straddles/Strangles without hedging

```python
# options/options_trader.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class OptionsTrader:
    """
    AI-powered options trading module.
    Opus analyzes and executes options strategies autonomously.
    
    Focus on DEFINED-RISK strategies only for capital preservation.
    """
    
    def __init__(self, alpaca_client, opus_brain, learning_db):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        self.db = learning_db
        
        # Strategy parameters
        self.min_dte = 21          # Minimum days to expiration
        self.max_dte = 45          # Maximum days to expiration (sweet spot)
        self.min_credit = 0.25     # Minimum credit to collect ($25 per contract)
        self.max_spread_width = 5  # Maximum spread width ($500 max risk per spread)
        self.target_pop = 0.65     # Target probability of profit (65%+)
        
    def scan_for_opportunities(self, symbols: list, 
                               market_regime: str) -> list:
        """
        Scan symbols for options opportunities based on market regime.
        Returns ranked list of opportunities for Opus to evaluate.
        """
        opportunities = []
        
        for symbol in symbols:
            try:
                # Get underlying data
                stock_data = self.alpaca.get_historical_bars(symbol, days=60)
                current_price = stock_data['close'].iloc[-1]
                
                # Get options chain
                chain = self.alpaca.get_options_chain(symbol)
                
                if not chain:
                    continue
                
                # Calculate implied volatility rank
                iv_rank = self._calculate_iv_rank(symbol)
                
                # Find opportunities based on market regime
                if market_regime in ['BULL_TRENDING', 'RANGING']:
                    # Bullish strategies
                    spreads = self._find_bull_put_spreads(symbol, chain, current_price)
                    opportunities.extend(spreads)
                    
                if market_regime in ['BEAR_TRENDING', 'RANGING']:
                    # Bearish strategies  
                    spreads = self._find_bear_call_spreads(symbol, chain, current_price)
                    opportunities.extend(spreads)
                    
                if market_regime == 'RANGING' and iv_rank > 50:
                    # Iron condors work best in ranging, high IV environments
                    condors = self._find_iron_condors(symbol, chain, current_price, stock_data)
                    opportunities.extend(condors)
                    
                if market_regime in ['BULL_TRENDING', 'BEAR_TRENDING']:
                    # Directional plays with debit spreads
                    debits = self._find_debit_spreads(symbol, chain, current_price, market_regime)
                    opportunities.extend(debits)
                    
            except Exception as e:
                continue
                
        # Rank by expected value
        opportunities.sort(key=lambda x: x.get('expected_value', 0), reverse=True)
        
        return opportunities[:20]  # Return top 20
    
    def _find_bull_put_spreads(self, symbol: str, chain: dict, 
                               current_price: float) -> list:
        """
        Find bull put spread opportunities (BULLISH strategy).
        
        Structure:
        - SELL put at higher strike (collect premium)
        - BUY put at lower strike (protection)
        
        Profit: If price stays above short strike at expiration
        Max Profit: Credit received
        Max Loss: Spread width - Credit
        """
        spreads = []
        
        # Filter puts by DTE
        puts = [opt for opt in chain.get('puts', []) 
                if self.min_dte <= opt.get('dte', 0) <= self.max_dte]
        
        if not puts:
            return []
            
        # Group by expiration
        by_expiry = {}
        for put in puts:
            exp = put['expiration']
            if exp not in by_expiry:
                by_expiry[exp] = []
            by_expiry[exp].append(put)
        
        for expiry, exp_puts in by_expiry.items():
            # Sort by strike
            exp_puts.sort(key=lambda x: x['strike'])
            
            for i, short_put in enumerate(exp_puts):
                # Short put should be OTM (below current price)
                if short_put['strike'] >= current_price:
                    continue
                    
                # Calculate delta (want ~0.30 delta for good probability)
                if abs(short_put.get('delta', 0)) > 0.40:
                    continue  # Too close to the money
                    
                # Find long put (lower strike)
                for long_put in exp_puts[:i]:
                    width = short_put['strike'] - long_put['strike']
                    
                    if width <= 0 or width > self.max_spread_width:
                        continue
                        
                    # Calculate credit
                    credit = short_put.get('bid', 0) - long_put.get('ask', 0)
                    
                    if credit < self.min_credit:
                        continue
                        
                    max_loss = width - credit
                    return_on_risk = (credit / max_loss) * 100 if max_loss > 0 else 0
                    
                    # Estimate probability of profit
                    pop = self._estimate_probability_of_profit(
                        current_price, short_put['strike'], 
                        short_put.get('dte', 30), short_put.get('iv', 0.3)
                    )
                    
                    if pop < self.target_pop:
                        continue
                        
                    spreads.append({
                        'symbol': symbol,
                        'strategy': 'BULL_PUT_SPREAD',
                        'direction': 'bullish',
                        'expiration': expiry,
                        'dte': short_put.get('dte', 0),
                        'short_strike': short_put['strike'],
                        'short_option': short_put['symbol'],
                        'long_strike': long_put['strike'],
                        'long_option': long_put['symbol'],
                        'credit': credit,
                        'max_loss': max_loss,
                        'max_profit': credit,
                        'width': width,
                        'return_on_risk': return_on_risk,
                        'probability_of_profit': pop,
                        'breakeven': short_put['strike'] - credit,
                        'expected_value': (credit * pop) - (max_loss * (1 - pop)),
                        'greeks': {
                            'delta': short_put.get('delta', 0) - long_put.get('delta', 0),
                            'theta': short_put.get('theta', 0) - long_put.get('theta', 0),
                            'vega': short_put.get('vega', 0) - long_put.get('vega', 0)
                        }
                    })
                    
        return spreads
    
    def _find_bear_call_spreads(self, symbol: str, chain: dict,
                                current_price: float) -> list:
        """
        Find bear call spread opportunities (BEARISH strategy).
        
        Structure:
        - SELL call at lower strike (collect premium)
        - BUY call at higher strike (protection)
        
        Profit: If price stays below short strike at expiration
        """
        spreads = []
        
        calls = [opt for opt in chain.get('calls', [])
                 if self.min_dte <= opt.get('dte', 0) <= self.max_dte]
        
        if not calls:
            return []
            
        # Group by expiration
        by_expiry = {}
        for call in calls:
            exp = call['expiration']
            if exp not in by_expiry:
                by_expiry[exp] = []
            by_expiry[exp].append(call)
        
        for expiry, exp_calls in by_expiry.items():
            exp_calls.sort(key=lambda x: x['strike'])
            
            for i, short_call in enumerate(exp_calls):
                # Short call should be OTM (above current price)
                if short_call['strike'] <= current_price:
                    continue
                    
                if abs(short_call.get('delta', 0)) > 0.40:
                    continue
                    
                # Find long call (higher strike)
                for long_call in exp_calls[i+1:]:
                    width = long_call['strike'] - short_call['strike']
                    
                    if width <= 0 or width > self.max_spread_width:
                        continue
                        
                    credit = short_call.get('bid', 0) - long_call.get('ask', 0)
                    
                    if credit < self.min_credit:
                        continue
                        
                    max_loss = width - credit
                    return_on_risk = (credit / max_loss) * 100 if max_loss > 0 else 0
                    
                    pop = self._estimate_probability_of_profit(
                        current_price, short_call['strike'],
                        short_call.get('dte', 30), short_call.get('iv', 0.3),
                        direction='below'
                    )
                    
                    if pop < self.target_pop:
                        continue
                        
                    spreads.append({
                        'symbol': symbol,
                        'strategy': 'BEAR_CALL_SPREAD',
                        'direction': 'bearish',
                        'expiration': expiry,
                        'dte': short_call.get('dte', 0),
                        'short_strike': short_call['strike'],
                        'short_option': short_call['symbol'],
                        'long_strike': long_call['strike'],
                        'long_option': long_call['symbol'],
                        'credit': credit,
                        'max_loss': max_loss,
                        'max_profit': credit,
                        'width': width,
                        'return_on_risk': return_on_risk,
                        'probability_of_profit': pop,
                        'breakeven': short_call['strike'] + credit,
                        'expected_value': (credit * pop) - (max_loss * (1 - pop)),
                        'greeks': {
                            'delta': short_call.get('delta', 0) - long_call.get('delta', 0),
                            'theta': short_call.get('theta', 0) - long_call.get('theta', 0),
                            'vega': short_call.get('vega', 0) - long_call.get('vega', 0)
                        }
                    })
                    
        return spreads
    
    def _find_iron_condors(self, symbol: str, chain: dict,
                          current_price: float, stock_data: pd.DataFrame) -> list:
        """
        Find iron condor opportunities (NEUTRAL strategy).
        
        Structure (4 legs):
        - SELL OTM put (collect premium)
        - BUY further OTM put (protection)
        - SELL OTM call (collect premium)
        - BUY further OTM call (protection)
        
        Profit: If price stays between short strikes at expiration
        Best when: High IV, range-bound market
        """
        condors = []
        
        # Check if stock is range-bound
        atr = self._calculate_atr(stock_data, 14)
        price_range = stock_data['high'].max() - stock_data['low'].min()
        
        # Get both puts and calls
        puts = [opt for opt in chain.get('puts', [])
                if self.min_dte <= opt.get('dte', 0) <= self.max_dte]
        calls = [opt for opt in chain.get('calls', [])
                 if self.min_dte <= opt.get('dte', 0) <= self.max_dte]
        
        if not puts or not calls:
            return []
            
        # Find matching expirations
        put_expiries = set(p['expiration'] for p in puts)
        call_expiries = set(c['expiration'] for c in calls)
        common_expiries = put_expiries & call_expiries
        
        for expiry in common_expiries:
            exp_puts = sorted([p for p in puts if p['expiration'] == expiry], 
                            key=lambda x: x['strike'])
            exp_calls = sorted([c for c in calls if c['expiration'] == expiry],
                             key=lambda x: x['strike'])
            
            # Find put spread (lower side)
            for i, short_put in enumerate(exp_puts):
                if short_put['strike'] >= current_price * 0.95:  # At least 5% OTM
                    continue
                    
                for long_put in exp_puts[:i]:
                    put_width = short_put['strike'] - long_put['strike']
                    if put_width <= 0 or put_width > self.max_spread_width:
                        continue
                        
                    put_credit = short_put.get('bid', 0) - long_put.get('ask', 0)
                    
                    # Find call spread (upper side)
                    for j, short_call in enumerate(exp_calls):
                        if short_call['strike'] <= current_price * 1.05:  # At least 5% OTM
                            continue
                            
                        for long_call in exp_calls[j+1:]:
                            call_width = long_call['strike'] - short_call['strike']
                            if call_width <= 0 or call_width > self.max_spread_width:
                                continue
                                
                            call_credit = short_call.get('bid', 0) - long_call.get('ask', 0)
                            
                            total_credit = put_credit + call_credit
                            max_loss = max(put_width, call_width) - total_credit
                            
                            if total_credit < self.min_credit * 2:  # Need good credit for 4 legs
                                continue
                                
                            # Probability both sides expire worthless
                            put_pop = self._estimate_probability_of_profit(
                                current_price, short_put['strike'],
                                short_put.get('dte', 30), short_put.get('iv', 0.3)
                            )
                            call_pop = self._estimate_probability_of_profit(
                                current_price, short_call['strike'],
                                short_call.get('dte', 30), short_call.get('iv', 0.3),
                                direction='below'
                            )
                            
                            # Combined probability
                            combined_pop = put_pop * call_pop
                            
                            if combined_pop < 0.50:  # Need at least 50% POP for condors
                                continue
                                
                            condors.append({
                                'symbol': symbol,
                                'strategy': 'IRON_CONDOR',
                                'direction': 'neutral',
                                'expiration': expiry,
                                'dte': short_put.get('dte', 0),
                                # Put spread (lower)
                                'put_short_strike': short_put['strike'],
                                'put_short_option': short_put['symbol'],
                                'put_long_strike': long_put['strike'],
                                'put_long_option': long_put['symbol'],
                                'put_width': put_width,
                                # Call spread (upper)
                                'call_short_strike': short_call['strike'],
                                'call_short_option': short_call['symbol'],
                                'call_long_strike': long_call['strike'],
                                'call_long_option': long_call['symbol'],
                                'call_width': call_width,
                                # P&L
                                'total_credit': total_credit,
                                'max_loss': max_loss,
                                'max_profit': total_credit,
                                'return_on_risk': (total_credit / max_loss) * 100,
                                'probability_of_profit': combined_pop,
                                'profit_range': (short_put['strike'], short_call['strike']),
                                'expected_value': (total_credit * combined_pop) - (max_loss * (1 - combined_pop))
                            })
                            
        return condors
    
    def _find_debit_spreads(self, symbol: str, chain: dict,
                           current_price: float, market_regime: str) -> list:
        """
        Find debit spread opportunities (DIRECTIONAL strategy).
        
        Bull Call Spread: Buy lower call, sell higher call (bullish)
        Bear Put Spread: Buy higher put, sell lower put (bearish)
        
        Pay debit upfront, profit if move in your direction.
        """
        spreads = []
        
        if market_regime == 'BULL_TRENDING':
            # Bull call spreads
            calls = [opt for opt in chain.get('calls', [])
                     if self.min_dte <= opt.get('dte', 0) <= self.max_dte]
            
            for expiry in set(c['expiration'] for c in calls):
                exp_calls = sorted([c for c in calls if c['expiration'] == expiry],
                                  key=lambda x: x['strike'])
                
                for i, long_call in enumerate(exp_calls):
                    # Long call should be ATM or slightly ITM
                    if abs(long_call['strike'] - current_price) > current_price * 0.03:
                        continue
                        
                    for short_call in exp_calls[i+1:]:
                        width = short_call['strike'] - long_call['strike']
                        if width <= 0 or width > self.max_spread_width:
                            continue
                            
                        debit = long_call.get('ask', 0) - short_call.get('bid', 0)
                        max_profit = width - debit
                        
                        if max_profit <= 0 or debit <= 0:
                            continue
                            
                        spreads.append({
                            'symbol': symbol,
                            'strategy': 'BULL_CALL_SPREAD',
                            'direction': 'bullish',
                            'expiration': expiry,
                            'dte': long_call.get('dte', 0),
                            'long_strike': long_call['strike'],
                            'long_option': long_call['symbol'],
                            'short_strike': short_call['strike'],
                            'short_option': short_call['symbol'],
                            'debit': debit,
                            'max_loss': debit,
                            'max_profit': max_profit,
                            'width': width,
                            'return_on_risk': (max_profit / debit) * 100,
                            'breakeven': long_call['strike'] + debit
                        })
                        
        elif market_regime == 'BEAR_TRENDING':
            # Bear put spreads
            puts = [opt for opt in chain.get('puts', [])
                    if self.min_dte <= opt.get('dte', 0) <= self.max_dte]
            
            for expiry in set(p['expiration'] for p in puts):
                exp_puts = sorted([p for p in puts if p['expiration'] == expiry],
                                 key=lambda x: x['strike'])
                
                for i, long_put in enumerate(exp_puts):
                    if abs(long_put['strike'] - current_price) > current_price * 0.03:
                        continue
                        
                    for short_put in exp_puts[:i]:
                        width = long_put['strike'] - short_put['strike']
                        if width <= 0 or width > self.max_spread_width:
                            continue
                            
                        debit = long_put.get('ask', 0) - short_put.get('bid', 0)
                        max_profit = width - debit
                        
                        if max_profit <= 0 or debit <= 0:
                            continue
                            
                        spreads.append({
                            'symbol': symbol,
                            'strategy': 'BEAR_PUT_SPREAD',
                            'direction': 'bearish',
                            'expiration': expiry,
                            'dte': long_put.get('dte', 0),
                            'long_strike': long_put['strike'],
                            'long_option': long_put['symbol'],
                            'short_strike': short_put['strike'],
                            'short_option': short_put['symbol'],
                            'debit': debit,
                            'max_loss': debit,
                            'max_profit': max_profit,
                            'width': width,
                            'return_on_risk': (max_profit / debit) * 100,
                            'breakeven': long_put['strike'] - debit
                        })
                        
        return spreads
    
    def _estimate_probability_of_profit(self, current_price: float, 
                                        strike: float, dte: int,
                                        iv: float, direction: str = 'above') -> float:
        """
        Estimate probability that price stays above/below strike.
        Uses simplified Black-Scholes probability calculation.
        """
        from scipy.stats import norm
        import math
        
        if iv <= 0 or dte <= 0:
            return 0.5
            
        # Time to expiration in years
        t = dte / 365.0
        
        # Calculate d2 (probability component)
        d2 = (math.log(current_price / strike) + (-0.5 * iv**2) * t) / (iv * math.sqrt(t))
        
        if direction == 'above':
            # Probability price > strike (for puts)
            return norm.cdf(d2)
        else:
            # Probability price < strike (for calls)
            return norm.cdf(-d2)
    
    def _calculate_iv_rank(self, symbol: str) -> float:
        """Calculate IV rank (0-100) comparing current IV to past year"""
        # This would typically come from options data
        # Simplified version
        return 50.0  # Placeholder
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]


class OpusOptionsAdvisor:
    """
    Opus-powered options trading decisions.
    Analyzes opportunities and decides which to execute.
    """
    
    def __init__(self, opus_brain, options_trader: OptionsTrader):
        self.opus = opus_brain
        self.trader = options_trader
        
    def evaluate_and_execute(self, opportunities: list, 
                            account_value: float,
                            max_options_allocation: float = 0.20) -> list:
        """
        Opus evaluates options opportunities and decides which to execute.
        
        Args:
            opportunities: List of options opportunities from scanner
            account_value: Total account value
            max_options_allocation: Max % of account in options (default 20%)
        """
        if not opportunities:
            return []
            
        max_capital = account_value * max_options_allocation
        
        # Build prompt for Opus
        prompt = f"""You are an options trading expert. Evaluate these opportunities and decide which to execute.

ACCOUNT INFO:
Total Account Value: ${account_value:.2f}
Max Options Capital: ${max_capital:.2f} ({max_options_allocation:.0%} of account)
Current Options Positions: [would be populated with current positions]

OPTIONS OPPORTUNITIES (ranked by expected value):
"""
        
        for i, opp in enumerate(opportunities[:10]):  # Top 10
            prompt += f"""
{i+1}. {opp['symbol']} - {opp['strategy']}
   Direction: {opp['direction']}
   Expiration: {opp['expiration']} ({opp['dte']} DTE)
   Credit/Debit: ${opp.get('credit', opp.get('debit', 0)):.2f}
   Max Profit: ${opp['max_profit']:.2f}
   Max Loss: ${opp['max_loss']:.2f}
   Return on Risk: {opp['return_on_risk']:.1f}%
   Probability of Profit: {opp.get('probability_of_profit', 0):.0%}
   Expected Value: ${opp.get('expected_value', 0):.2f}
"""

        prompt += """

INSTRUCTIONS:
1. Select up to 3 best opportunities to execute
2. Consider: probability of profit, risk/reward, diversification, capital efficiency
3. Reject opportunities that are too risky or have poor expected value
4. Ensure total capital deployed doesn't exceed max allocation

Respond with JSON:
{
    "analysis": "Your overall assessment",
    "selected_trades": [
        {
            "rank": 1,
            "symbol": "ticker",
            "strategy": "strategy name",
            "contracts": 1,
            "capital_required": 500.00,
            "reasoning": "why this trade"
        }
    ],
    "rejected_reasons": {
        "symbol": "reason for rejection"
    },
    "total_capital_to_deploy": 1500.00,
    "confidence": 0.0-1.0
}

If no opportunities are good enough, return empty selected_trades."""

        response = self.opus.client.messages.create(
            model=self.opus.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        decision = self._parse_decision(response.content[0].text)
        
        # Execute selected trades
        executed = []
        for trade in decision.get('selected_trades', []):
            # Find the opportunity
            opp = next((o for o in opportunities 
                       if o['symbol'] == trade['symbol'] and o['strategy'] == trade['strategy']), None)
            
            if opp:
                result = self._execute_options_trade(opp, trade['contracts'])
                executed.append(result)
                
        return executed
    
    def _execute_options_trade(self, opportunity: dict, contracts: int) -> dict:
        """Execute an options trade based on strategy"""
        
        strategy = opportunity['strategy']
        
        if strategy in ['BULL_PUT_SPREAD', 'BEAR_CALL_SPREAD']:
            # Credit spread - 2 legs
            return self._execute_credit_spread(opportunity, contracts)
            
        elif strategy == 'IRON_CONDOR':
            # Iron condor - 4 legs
            return self._execute_iron_condor(opportunity, contracts)
            
        elif strategy in ['BULL_CALL_SPREAD', 'BEAR_PUT_SPREAD']:
            # Debit spread - 2 legs
            return self._execute_debit_spread(opportunity, contracts)
            
        else:
            return {'status': 'error', 'message': f'Unknown strategy: {strategy}'}
    
    def _execute_credit_spread(self, opp: dict, contracts: int) -> dict:
        """Execute a credit spread (2 legs)"""
        try:
            # Submit as a spread order
            order = self.trader.alpaca.submit_options_order(
                legs=[
                    {
                        'symbol': opp['short_option'],
                        'side': 'sell',
                        'qty': contracts
                    },
                    {
                        'symbol': opp['long_option'],
                        'side': 'buy',
                        'qty': contracts
                    }
                ],
                order_type='limit',
                limit_price=opp['credit'],
                time_in_force='day'
            )
            
            return {
                'status': 'submitted',
                'order_id': order.id,
                'strategy': opp['strategy'],
                'symbol': opp['symbol'],
                'contracts': contracts,
                'credit': opp['credit'] * contracts * 100,
                'max_loss': opp['max_loss'] * contracts * 100
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _execute_iron_condor(self, opp: dict, contracts: int) -> dict:
        """Execute an iron condor (4 legs)"""
        try:
            order = self.trader.alpaca.submit_options_order(
                legs=[
                    # Put spread (lower)
                    {'symbol': opp['put_short_option'], 'side': 'sell', 'qty': contracts},
                    {'symbol': opp['put_long_option'], 'side': 'buy', 'qty': contracts},
                    # Call spread (upper)
                    {'symbol': opp['call_short_option'], 'side': 'sell', 'qty': contracts},
                    {'symbol': opp['call_long_option'], 'side': 'buy', 'qty': contracts}
                ],
                order_type='limit',
                limit_price=opp['total_credit'],
                time_in_force='day'
            )
            
            return {
                'status': 'submitted',
                'order_id': order.id,
                'strategy': 'IRON_CONDOR',
                'symbol': opp['symbol'],
                'contracts': contracts,
                'credit': opp['total_credit'] * contracts * 100,
                'max_loss': opp['max_loss'] * contracts * 100,
                'profit_range': opp['profit_range']
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _execute_debit_spread(self, opp: dict, contracts: int) -> dict:
        """Execute a debit spread (2 legs)"""
        try:
            order = self.trader.alpaca.submit_options_order(
                legs=[
                    {
                        'symbol': opp['long_option'],
                        'side': 'buy',
                        'qty': contracts
                    },
                    {
                        'symbol': opp['short_option'],
                        'side': 'sell',
                        'qty': contracts
                    }
                ],
                order_type='limit',
                limit_price=opp['debit'],
                time_in_force='day'
            )
            
            return {
                'status': 'submitted',
                'order_id': order.id,
                'strategy': opp['strategy'],
                'symbol': opp['symbol'],
                'contracts': contracts,
                'debit': opp['debit'] * contracts * 100,
                'max_profit': opp['max_profit'] * contracts * 100
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _parse_decision(self, response_text: str) -> dict:
        try:
            import json
            clean = response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except:
            return {"selected_trades": [], "analysis": "Failed to parse"}


class OptionsPositionManager:
    """
    Manage existing options positions.
    - Monitor for exit conditions
    - Roll positions if needed
    - Close at profit targets or stop losses
    """
    
    def __init__(self, alpaca_client, opus_brain):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        
        # Exit rules
        self.profit_target_pct = 0.50  # Close at 50% of max profit
        self.stop_loss_pct = 2.0       # Close if loss exceeds 2x credit received
        self.days_to_expiry_close = 7  # Close if <7 DTE
        
    def evaluate_positions(self) -> list:
        """Evaluate all options positions for potential exit"""
        positions = self.alpaca.get_options_positions()
        
        actions = []
        
        for pos in positions:
            action = self._evaluate_single_position(pos)
            if action['recommendation'] != 'HOLD':
                actions.append(action)
                
        return actions
    
    def _evaluate_single_position(self, position: dict) -> dict:
        """Evaluate a single options position"""
        symbol = position['symbol']
        current_value = float(position['market_value'])
        cost_basis = float(position['cost_basis'])
        
        # Calculate P&L
        pnl = current_value - cost_basis
        pnl_pct = (pnl / abs(cost_basis)) * 100 if cost_basis != 0 else 0
        
        # Get DTE
        expiration = position.get('expiration_date')
        if expiration:
            dte = (datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days
        else:
            dte = 999
            
        # Determine action
        recommendation = 'HOLD'
        reason = ''
        
        # Check profit target
        if pnl_pct >= self.profit_target_pct * 100:
            recommendation = 'CLOSE'
            reason = f'Profit target reached ({pnl_pct:.0f}%)'
            
        # Check stop loss
        elif pnl_pct <= -self.stop_loss_pct * 100:
            recommendation = 'CLOSE'
            reason = f'Stop loss triggered ({pnl_pct:.0f}%)'
            
        # Check DTE
        elif dte <= self.days_to_expiry_close:
            recommendation = 'CLOSE'
            reason = f'Approaching expiration ({dte} DTE)'
            
        return {
            'symbol': symbol,
            'current_value': current_value,
            'cost_basis': cost_basis,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'dte': dte,
            'recommendation': recommendation,
            'reason': reason
        }
    
    def close_position(self, symbol: str, reason: str) -> dict:
        """Close an options position"""
        try:
            order = self.alpaca.close_options_position(symbol)
            
            return {
                'status': 'closed',
                'symbol': symbol,
                'reason': reason,
                'order_id': order.id
            }
        except Exception as e:
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e)
            }
```

### Options Greeks Calculator

```python
# options/greeks.py

import math
from scipy.stats import norm

class GreeksCalculator:
    """
    Calculate options Greeks for risk analysis.
    """
    
    @staticmethod
    def calculate_all_greeks(S: float, K: float, T: float, r: float, 
                            sigma: float, option_type: str = 'call') -> dict:
        """
        Calculate all Greeks for an option.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Implied volatility
            option_type: 'call' or 'put'
        """
        if T <= 0 or sigma <= 0:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
            
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        if option_type == 'call':
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) 
                    - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
            rho = K * T * math.exp(-r * T) * norm.cdf(d2) / 100
        else:
            delta = norm.cdf(d1) - 1
            theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
                    + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365
            rho = -K * T * math.exp(-r * T) * norm.cdf(-d2) / 100
            
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T) / 100
        
        return {
            'delta': round(delta, 4),
            'gamma': round(gamma, 4),
            'theta': round(theta, 4),
            'vega': round(vega, 4),
            'rho': round(rho, 4)
        }
    
    @staticmethod
    def calculate_spread_greeks(leg1_greeks: dict, leg2_greeks: dict,
                               leg1_qty: int, leg2_qty: int) -> dict:
        """Calculate net Greeks for a spread position"""
        return {
            'delta': leg1_greeks['delta'] * leg1_qty + leg2_greeks['delta'] * leg2_qty,
            'gamma': leg1_greeks['gamma'] * leg1_qty + leg2_greeks['gamma'] * leg2_qty,
            'theta': leg1_greeks['theta'] * leg1_qty + leg2_greeks['theta'] * leg2_qty,
            'vega': leg1_greeks['vega'] * leg1_qty + leg2_greeks['vega'] * leg2_qty
        }
```

---

## Options Intelligence Module (CRITICAL FOR AI OPTIONS TRADING)

**PURPOSE:** This module provides the AI with all the data and analysis tools that professional options traders use to make decisions. Without this intelligence, the AI would be trading blind.

### What Professional Options Traders Use

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PROFESSIONAL OPTIONS TRADING DATA SOURCES                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. VOLATILITY ANALYSIS                                                     │
│     • Implied Volatility (IV) - Market's expectation of future movement    │
│     • IV Rank - Current IV vs 52-week range (0-100%)                        │
│     • IV Percentile - How often IV has been lower in past year             │
│     • Historical Volatility (HV) - Actual past price movement              │
│     • IV vs HV comparison - Is IV overpriced or underpriced?               │
│                                                                             │
│  2. OPTIONS FLOW (Institutional Activity)                                   │
│     • Unusual Options Activity - Volume spikes vs normal                   │
│     • Sweep Orders - Large orders split across exchanges (urgency)         │
│     • Block Trades - Single large institutional trades                      │
│     • Put/Call Ratio - Sentiment indicator                                  │
│     • Open Interest Changes - New positions being opened                    │
│                                                                             │
│  3. DARK POOL DATA                                                          │
│     • Large block trades executed privately                                 │
│     • Institutional accumulation/distribution                               │
│     • Price levels where institutions are buying/selling                    │
│                                                                             │
│  4. MAX PAIN ANALYSIS                                                       │
│     • Strike where most options expire worthless                            │
│     • Price magnet near expiration                                          │
│     • Support/resistance from open interest concentration                   │
│                                                                             │
│  5. GREEKS                                                                  │
│     • Delta - Price sensitivity                                             │
│     • Gamma - Rate of delta change (acceleration)                           │
│     • Theta - Time decay (how much value lost per day)                      │
│     • Vega - Volatility sensitivity                                         │
│     • Rho - Interest rate sensitivity                                       │
│                                                                             │
│  6. EARNINGS & EVENTS                                                       │
│     • Earnings calendar with expected dates                                 │
│     • Historical earnings moves (how much stock moved)                      │
│     • IV Crush prediction - How much IV will drop after event              │
│     • Expected Move vs Implied Move analysis                                │
│                                                                             │
│  7. TECHNICAL ANALYSIS (Same as stocks)                                     │
│     • RSI, MACD, Bollinger Bands, Moving Averages                          │
│     • Support/Resistance levels                                             │
│     • Trend direction                                                       │
│                                                                             │
│  8. NEWS & SENTIMENT                                                        │
│     • Headlines affecting the underlying                                    │
│     • Social sentiment                                                      │
│     • Analyst ratings changes                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Options Intelligence Engine

```python
# options/intelligence.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from scipy.stats import norm
import math

class OptionsIntelligence:
    """
    Comprehensive options intelligence gathering.
    This is how the AI knows whether to go long/short on options.
    
    Combines all data sources professional traders use:
    - Volatility analysis (IV Rank, IV Percentile)
    - Options flow (unusual activity, sweeps)
    - Max pain calculation
    - Greeks analysis
    - Earnings/event awareness
    - Technical analysis
    - News/sentiment
    """
    
    def __init__(self, alpaca_client, news_analyzer, sentiment_analyzer):
        self.alpaca = alpaca_client
        self.news = news_analyzer
        self.sentiment = sentiment_analyzer
        
        # Historical IV data storage
        self.iv_history = {}  # symbol -> list of daily IV values
        
    def get_complete_analysis(self, symbol: str) -> dict:
        """
        Get complete options intelligence for a symbol.
        This is what Opus uses to decide on options trades.
        """
        # Get all data
        chain = self.alpaca.get_options_chain(symbol)
        stock_data = self.alpaca.get_historical_bars(symbol, days=252)
        current_price = stock_data['close'].iloc[-1]
        
        analysis = {
            'symbol': symbol,
            'current_price': current_price,
            'timestamp': datetime.now().isoformat(),
            
            # 1. Volatility Analysis
            'volatility': self._analyze_volatility(symbol, chain, stock_data),
            
            # 2. Options Flow
            'options_flow': self._analyze_options_flow(symbol, chain),
            
            # 3. Max Pain
            'max_pain': self._calculate_max_pain(chain, current_price),
            
            # 4. Greeks Summary
            'greeks_summary': self._summarize_greeks(chain, current_price),
            
            # 5. Earnings/Events
            'events': self._check_upcoming_events(symbol),
            
            # 6. Technical Analysis
            'technicals': self._analyze_technicals(stock_data),
            
            # 7. Sentiment
            'sentiment': self._analyze_sentiment(symbol),
            
            # 8. AI Recommendation
            'recommendation': None  # Filled in by Opus
        }
        
        # Generate AI recommendation based on all data
        analysis['recommendation'] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _analyze_volatility(self, symbol: str, chain: dict, 
                           stock_data: pd.DataFrame) -> dict:
        """
        Comprehensive volatility analysis.
        
        KEY INSIGHT: 
        - HIGH IV = Sell premium (credit spreads, iron condors)
        - LOW IV = Buy options (debit spreads, long calls/puts)
        """
        # Calculate current IV (average of ATM options)
        current_price = stock_data['close'].iloc[-1]
        current_iv = self._get_atm_iv(chain, current_price)
        
        # Calculate Historical Volatility (HV)
        returns = stock_data['close'].pct_change().dropna()
        hv_20 = returns.tail(20).std() * np.sqrt(252)  # 20-day HV
        hv_60 = returns.tail(60).std() * np.sqrt(252)  # 60-day HV
        
        # Get IV history for rank/percentile calculation
        iv_history = self._get_iv_history(symbol)
        
        # IV Rank: Where is current IV relative to 52-week high/low?
        # (Current IV - 52wk Low) / (52wk High - 52wk Low) * 100
        if iv_history and len(iv_history) > 0:
            iv_52wk_high = max(iv_history)
            iv_52wk_low = min(iv_history)
            if iv_52wk_high != iv_52wk_low:
                iv_rank = (current_iv - iv_52wk_low) / (iv_52wk_high - iv_52wk_low) * 100
            else:
                iv_rank = 50
            
            # IV Percentile: What % of days had lower IV?
            days_lower = sum(1 for iv in iv_history if iv < current_iv)
            iv_percentile = (days_lower / len(iv_history)) * 100
        else:
            iv_rank = 50
            iv_percentile = 50
        
        # IV vs HV comparison
        iv_hv_ratio = current_iv / hv_20 if hv_20 > 0 else 1.0
        
        # Determine volatility regime
        if iv_rank > 70:
            vol_regime = 'HIGH_IV'
            strategy_bias = 'SELL_PREMIUM'
        elif iv_rank < 30:
            vol_regime = 'LOW_IV'
            strategy_bias = 'BUY_OPTIONS'
        else:
            vol_regime = 'NORMAL_IV'
            strategy_bias = 'NEUTRAL'
        
        return {
            'current_iv': round(current_iv * 100, 2),  # As percentage
            'iv_rank': round(iv_rank, 1),
            'iv_percentile': round(iv_percentile, 1),
            'hv_20': round(hv_20 * 100, 2),
            'hv_60': round(hv_60 * 100, 2),
            'iv_hv_ratio': round(iv_hv_ratio, 2),
            'iv_52wk_high': round(iv_52wk_high * 100, 2) if iv_history else None,
            'iv_52wk_low': round(iv_52wk_low * 100, 2) if iv_history else None,
            'vol_regime': vol_regime,
            'strategy_bias': strategy_bias,
            'interpretation': self._interpret_volatility(iv_rank, iv_hv_ratio)
        }
    
    def _analyze_options_flow(self, symbol: str, chain: dict) -> dict:
        """
        Analyze options flow for institutional activity signals.
        
        KEY INSIGHT:
        - Unusual call volume = Bullish institutional bet
        - Unusual put volume = Bearish institutional bet
        - Sweep orders = High urgency, strong conviction
        """
        # Calculate total call and put volume
        total_call_volume = sum(opt.get('volume', 0) for opt in chain.get('calls', []))
        total_put_volume = sum(opt.get('volume', 0) for opt in chain.get('puts', []))
        
        # Calculate total call and put open interest
        total_call_oi = sum(opt.get('open_interest', 0) for opt in chain.get('calls', []))
        total_put_oi = sum(opt.get('open_interest', 0) for opt in chain.get('puts', []))
        
        # Put/Call Ratio (volume-based)
        pc_ratio_volume = total_put_volume / total_call_volume if total_call_volume > 0 else 1.0
        
        # Put/Call Ratio (open interest-based)
        pc_ratio_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        
        # Find unusual activity (volume > 5x open interest or > 3x average)
        unusual_calls = []
        unusual_puts = []
        
        for call in chain.get('calls', []):
            vol = call.get('volume', 0)
            oi = call.get('open_interest', 1)
            if vol > 0 and (vol / oi > 5 or vol > 1000):
                unusual_calls.append({
                    'strike': call['strike'],
                    'expiration': call['expiration'],
                    'volume': vol,
                    'open_interest': oi,
                    'vol_oi_ratio': round(vol / oi, 2) if oi > 0 else vol,
                    'premium_traded': vol * call.get('last', 0) * 100
                })
        
        for put in chain.get('puts', []):
            vol = put.get('volume', 0)
            oi = put.get('open_interest', 1)
            if vol > 0 and (vol / oi > 5 or vol > 1000):
                unusual_puts.append({
                    'strike': put['strike'],
                    'expiration': put['expiration'],
                    'volume': vol,
                    'open_interest': oi,
                    'vol_oi_ratio': round(vol / oi, 2) if oi > 0 else vol,
                    'premium_traded': vol * put.get('last', 0) * 100
                })
        
        # Sort by premium traded (biggest bets first)
        unusual_calls.sort(key=lambda x: x['premium_traded'], reverse=True)
        unusual_puts.sort(key=lambda x: x['premium_traded'], reverse=True)
        
        # Determine flow sentiment
        if pc_ratio_volume < 0.7:
            flow_sentiment = 'BULLISH'
        elif pc_ratio_volume > 1.3:
            flow_sentiment = 'BEARISH'
        else:
            flow_sentiment = 'NEUTRAL'
        
        # Check for sweep activity (would require real-time data)
        # For now, high volume/OI ratio serves as proxy
        has_unusual_call_activity = len(unusual_calls) > 0 and unusual_calls[0]['premium_traded'] > 100000
        has_unusual_put_activity = len(unusual_puts) > 0 and unusual_puts[0]['premium_traded'] > 100000
        
        return {
            'total_call_volume': total_call_volume,
            'total_put_volume': total_put_volume,
            'total_call_oi': total_call_oi,
            'total_put_oi': total_put_oi,
            'pc_ratio_volume': round(pc_ratio_volume, 2),
            'pc_ratio_oi': round(pc_ratio_oi, 2),
            'flow_sentiment': flow_sentiment,
            'unusual_calls': unusual_calls[:5],  # Top 5
            'unusual_puts': unusual_puts[:5],
            'has_unusual_call_activity': has_unusual_call_activity,
            'has_unusual_put_activity': has_unusual_put_activity,
            'interpretation': self._interpret_flow(pc_ratio_volume, unusual_calls, unusual_puts)
        }
    
    def _calculate_max_pain(self, chain: dict, current_price: float) -> dict:
        """
        Calculate max pain - the strike where most options expire worthless.
        
        KEY INSIGHT:
        - Price tends to gravitate toward max pain near expiration
        - Use as support/resistance level
        - More reliable for less liquid stocks
        """
        # Get nearest expiration
        expirations = set()
        for opt in chain.get('calls', []) + chain.get('puts', []):
            expirations.add(opt.get('expiration'))
        
        if not expirations:
            return {'max_pain': current_price, 'error': 'No options data'}
        
        # Sort expirations and get nearest
        sorted_exps = sorted(expirations)
        nearest_exp = sorted_exps[0]
        
        # Filter to nearest expiration
        calls = [c for c in chain.get('calls', []) if c.get('expiration') == nearest_exp]
        puts = [p for p in chain.get('puts', []) if p.get('expiration') == nearest_exp]
        
        # Get all strikes
        strikes = sorted(set([c['strike'] for c in calls] + [p['strike'] for p in puts]))
        
        if not strikes:
            return {'max_pain': current_price, 'error': 'No strikes found'}
        
        # Calculate pain at each strike
        pain_by_strike = {}
        
        for test_price in strikes:
            total_pain = 0
            
            # Calculate call pain (calls ITM when price > strike)
            for call in calls:
                if test_price > call['strike']:
                    intrinsic = test_price - call['strike']
                    pain = intrinsic * call.get('open_interest', 0) * 100
                    total_pain += pain
            
            # Calculate put pain (puts ITM when price < strike)
            for put in puts:
                if test_price < put['strike']:
                    intrinsic = put['strike'] - test_price
                    pain = intrinsic * put.get('open_interest', 0) * 100
                    total_pain += pain
            
            pain_by_strike[test_price] = total_pain
        
        # Find strike with minimum pain (max pain point)
        max_pain_strike = min(pain_by_strike, key=pain_by_strike.get)
        
        # Distance from current price
        distance_pct = ((max_pain_strike - current_price) / current_price) * 100
        
        return {
            'max_pain': max_pain_strike,
            'expiration': nearest_exp,
            'current_price': current_price,
            'distance_to_max_pain': round(distance_pct, 2),
            'direction_to_max_pain': 'UP' if max_pain_strike > current_price else 'DOWN',
            'pain_by_strike': dict(sorted(pain_by_strike.items())[-10:]),  # Top 10 strikes
            'interpretation': f"Max pain at ${max_pain_strike}. Price may gravitate {distance_pct:.1f}% {'up' if distance_pct > 0 else 'down'} toward this level by {nearest_exp}."
        }
    
    def _summarize_greeks(self, chain: dict, current_price: float) -> dict:
        """
        Summarize Greeks across the options chain.
        
        KEY INSIGHT:
        - High gamma near ATM = Explosive moves possible
        - High theta = Time decay accelerating
        - High vega = Very sensitive to IV changes
        """
        # Find ATM options
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])
        
        if not calls or not puts:
            return {'error': 'No options data'}
        
        # Find nearest ATM call and put
        atm_call = min(calls, key=lambda x: abs(x['strike'] - current_price))
        atm_put = min(puts, key=lambda x: abs(x['strike'] - current_price))
        
        return {
            'atm_call': {
                'strike': atm_call['strike'],
                'delta': atm_call.get('delta', 0.5),
                'gamma': atm_call.get('gamma', 0),
                'theta': atm_call.get('theta', 0),
                'vega': atm_call.get('vega', 0)
            },
            'atm_put': {
                'strike': atm_put['strike'],
                'delta': atm_put.get('delta', -0.5),
                'gamma': atm_put.get('gamma', 0),
                'theta': atm_put.get('theta', 0),
                'vega': atm_put.get('vega', 0)
            },
            'gamma_risk': 'HIGH' if atm_call.get('gamma', 0) > 0.05 else 'NORMAL',
            'theta_decay': abs(atm_call.get('theta', 0)) + abs(atm_put.get('theta', 0)),
            'vega_sensitivity': atm_call.get('vega', 0) + atm_put.get('vega', 0)
        }
    
    def _check_upcoming_events(self, symbol: str) -> dict:
        """
        Check for upcoming earnings and other events.
        
        KEY INSIGHT:
        - NEVER buy options right before earnings (IV crush risk)
        - SELL premium before earnings (high IV)
        - Be aware of Fed meetings, CPI, etc.
        """
        # This would integrate with an earnings calendar API
        # For now, return structure
        
        return {
            'has_earnings_soon': False,  # Would check calendar
            'earnings_date': None,
            'days_to_earnings': None,
            'historical_earnings_move': None,  # Average % move on earnings
            'implied_move': None,  # What options are pricing
            'iv_crush_risk': 'LOW',
            'fed_meeting_soon': False,
            'other_events': [],
            'recommendation': 'No major events detected. Normal trading conditions.'
        }
    
    def _analyze_technicals(self, stock_data: pd.DataFrame) -> dict:
        """
        Technical analysis of the underlying stock.
        Same indicators as stock trading.
        """
        close = stock_data['close']
        high = stock_data['high']
        low = stock_data['low']
        volume = stock_data['volume']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        # Moving Averages
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1]
        sma_200 = close.rolling(200).mean().iloc[-1]
        
        current_price = close.iloc[-1]
        
        # Trend determination
        if current_price > sma_50 > sma_200:
            trend = 'UPTREND'
        elif current_price < sma_50 < sma_200:
            trend = 'DOWNTREND'
        else:
            trend = 'SIDEWAYS'
        
        # Bollinger Bands
        bb_middle = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_upper = bb_middle + (2 * bb_std)
        bb_lower = bb_middle - (2 * bb_std)
        
        # BB position
        bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        return {
            'rsi': round(rsi, 1),
            'macd': round(macd.iloc[-1], 4),
            'macd_signal': round(signal.iloc[-1], 4),
            'macd_histogram': round(histogram.iloc[-1], 4),
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2),
            'sma_200': round(sma_200, 2),
            'trend': trend,
            'bb_upper': round(bb_upper.iloc[-1], 2),
            'bb_lower': round(bb_lower.iloc[-1], 2),
            'bb_position': round(bb_position, 2),  # 0 = at lower, 1 = at upper
            'volume_trend': 'ABOVE_AVG' if volume.iloc[-1] > volume.mean() else 'BELOW_AVG'
        }
    
    def _analyze_sentiment(self, symbol: str) -> dict:
        """
        News and social sentiment analysis.
        """
        # Would integrate with news and sentiment APIs
        news_score = self.news.get_sentiment_score(symbol) if self.news else 0
        social_score = self.sentiment.get_social_sentiment(symbol) if self.sentiment else 0
        
        combined = (news_score + social_score) / 2
        
        if combined > 0.3:
            sentiment = 'BULLISH'
        elif combined < -0.3:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'news_score': round(news_score, 2),
            'social_score': round(social_score, 2),
            'combined_score': round(combined, 2),
            'sentiment': sentiment
        }
    
    def _generate_recommendation(self, analysis: dict) -> dict:
        """
        Generate AI recommendation based on all analysis.
        This is what tells Opus whether to go LONG or SHORT options.
        """
        vol = analysis['volatility']
        flow = analysis['options_flow']
        technicals = analysis['technicals']
        sentiment = analysis['sentiment']
        max_pain = analysis['max_pain']
        
        # Score each factor
        scores = {
            'volatility': 0,
            'flow': 0,
            'technicals': 0,
            'sentiment': 0
        }
        
        # Volatility score
        if vol['iv_rank'] > 70:
            scores['volatility'] = -1  # Favor selling premium
        elif vol['iv_rank'] < 30:
            scores['volatility'] = 1   # Favor buying options
        
        # Flow score
        if flow['flow_sentiment'] == 'BULLISH':
            scores['flow'] = 1
        elif flow['flow_sentiment'] == 'BEARISH':
            scores['flow'] = -1
        
        # Technical score
        if technicals['trend'] == 'UPTREND' and technicals['rsi'] < 70:
            scores['technicals'] = 1
        elif technicals['trend'] == 'DOWNTREND' and technicals['rsi'] > 30:
            scores['technicals'] = -1
        
        # Sentiment score
        if sentiment['sentiment'] == 'BULLISH':
            scores['sentiment'] = 0.5
        elif sentiment['sentiment'] == 'BEARISH':
            scores['sentiment'] = -0.5
        
        # Combined score
        total_score = sum(scores.values())
        
        # Determine direction
        if total_score >= 1.5:
            direction = 'BULLISH'
            confidence = min(abs(total_score) / 3, 1.0)
        elif total_score <= -1.5:
            direction = 'BEARISH'
            confidence = min(abs(total_score) / 3, 1.0)
        else:
            direction = 'NEUTRAL'
            confidence = 0.5
        
        # Determine strategy based on IV and direction
        if vol['iv_rank'] > 60:  # High IV - sell premium
            if direction == 'BULLISH':
                strategy = 'BULL_PUT_SPREAD'
                reasoning = 'High IV favors selling premium. Bullish bias suggests bull put spread.'
            elif direction == 'BEARISH':
                strategy = 'BEAR_CALL_SPREAD'
                reasoning = 'High IV favors selling premium. Bearish bias suggests bear call spread.'
            else:
                strategy = 'IRON_CONDOR'
                reasoning = 'High IV + neutral bias = ideal for iron condor to collect premium.'
        else:  # Low IV - buy options
            if direction == 'BULLISH':
                strategy = 'BULL_CALL_SPREAD'
                reasoning = 'Low IV makes options cheap. Bullish bias suggests bull call spread.'
            elif direction == 'BEARISH':
                strategy = 'BEAR_PUT_SPREAD'
                reasoning = 'Low IV makes options cheap. Bearish bias suggests bear put spread.'
            else:
                strategy = 'HOLD'
                reasoning = 'Low IV + neutral direction = wait for clearer signal.'
        
        return {
            'direction': direction,
            'confidence': round(confidence, 2),
            'recommended_strategy': strategy,
            'reasoning': reasoning,
            'scores': scores,
            'total_score': round(total_score, 2),
            'factors': {
                'iv_rank': f"{vol['iv_rank']:.0f}% ({vol['vol_regime']})",
                'flow': f"{flow['flow_sentiment']} (P/C: {flow['pc_ratio_volume']:.2f})",
                'trend': technicals['trend'],
                'rsi': f"{technicals['rsi']:.0f}",
                'sentiment': sentiment['sentiment']
            }
        }
    
    def _get_atm_iv(self, chain: dict, current_price: float) -> float:
        """Get implied volatility of ATM options"""
        calls = chain.get('calls', [])
        if not calls:
            return 0.25  # Default 25%
        
        atm_call = min(calls, key=lambda x: abs(x['strike'] - current_price))
        return atm_call.get('iv', 0.25)
    
    def _get_iv_history(self, symbol: str) -> list:
        """Get historical IV data for IV Rank/Percentile calculation"""
        # Would store and retrieve from database
        # Return empty list if not available
        return self.iv_history.get(symbol, [])
    
    def _interpret_volatility(self, iv_rank: float, iv_hv_ratio: float) -> str:
        """Generate human-readable volatility interpretation"""
        if iv_rank > 70:
            rank_text = "IV is HIGH relative to its 52-week range. Options are expensive."
        elif iv_rank < 30:
            rank_text = "IV is LOW relative to its 52-week range. Options are cheap."
        else:
            rank_text = "IV is in the middle of its 52-week range. Normal pricing."
        
        if iv_hv_ratio > 1.2:
            ratio_text = "IV is elevated vs historical volatility - options may be overpriced."
        elif iv_hv_ratio < 0.8:
            ratio_text = "IV is below historical volatility - options may be underpriced."
        else:
            ratio_text = "IV is in line with historical volatility."
        
        return f"{rank_text} {ratio_text}"
    
    def _interpret_flow(self, pc_ratio: float, unusual_calls: list, 
                       unusual_puts: list) -> str:
        """Generate human-readable flow interpretation"""
        if pc_ratio < 0.7:
            ratio_text = "Put/Call ratio indicates BULLISH sentiment (more calls than puts)."
        elif pc_ratio > 1.3:
            ratio_text = "Put/Call ratio indicates BEARISH sentiment (more puts than calls)."
        else:
            ratio_text = "Put/Call ratio is neutral."
        
        activity_text = ""
        if unusual_calls and unusual_calls[0]['premium_traded'] > 100000:
            activity_text += f" Large call activity detected: {unusual_calls[0]['strike']} strike with ${unusual_calls[0]['premium_traded']:,.0f} traded."
        if unusual_puts and unusual_puts[0]['premium_traded'] > 100000:
            activity_text += f" Large put activity detected: {unusual_puts[0]['strike']} strike with ${unusual_puts[0]['premium_traded']:,.0f} traded."
        
        return ratio_text + activity_text


class OpusOptionsDecisionEngine:
    """
    Opus uses the Options Intelligence to make trading decisions.
    This is the brain that decides WHAT options trade to make.
    """
    
    def __init__(self, opus_brain, options_intelligence: OptionsIntelligence):
        self.opus = opus_brain
        self.intel = options_intelligence
        
    def analyze_and_decide(self, symbol: str, account_value: float) -> dict:
        """
        Complete analysis and decision for options trading on a symbol.
        """
        # Get complete intelligence
        analysis = self.intel.get_complete_analysis(symbol)
        
        # Build prompt for Opus
        prompt = f"""You are an expert options trader. Analyze this data and decide on a trade.

SYMBOL: {symbol}
CURRENT PRICE: ${analysis['current_price']:.2f}

=== VOLATILITY ANALYSIS ===
IV Rank: {analysis['volatility']['iv_rank']:.0f}% (0-100 scale)
IV Percentile: {analysis['volatility']['iv_percentile']:.0f}%
Current IV: {analysis['volatility']['current_iv']:.1f}%
Historical Volatility (20d): {analysis['volatility']['hv_20']:.1f}%
IV/HV Ratio: {analysis['volatility']['iv_hv_ratio']:.2f}
Volatility Regime: {analysis['volatility']['vol_regime']}
Strategy Bias: {analysis['volatility']['strategy_bias']}

=== OPTIONS FLOW ===
Put/Call Ratio: {analysis['options_flow']['pc_ratio_volume']:.2f}
Flow Sentiment: {analysis['options_flow']['flow_sentiment']}
Unusual Call Activity: {analysis['options_flow']['has_unusual_call_activity']}
Unusual Put Activity: {analysis['options_flow']['has_unusual_put_activity']}

=== MAX PAIN ===
Max Pain Strike: ${analysis['max_pain']['max_pain']}
Distance to Max Pain: {analysis['max_pain']['distance_to_max_pain']:.1f}%
Direction: {analysis['max_pain']['direction_to_max_pain']}

=== TECHNICALS ===
Trend: {analysis['technicals']['trend']}
RSI: {analysis['technicals']['rsi']:.0f}
MACD: {analysis['technicals']['macd']:.4f}
BB Position: {analysis['technicals']['bb_position']:.2f} (0=lower, 1=upper)

=== SENTIMENT ===
News: {analysis['sentiment']['news_score']:.2f}
Social: {analysis['sentiment']['social_score']:.2f}
Overall: {analysis['sentiment']['sentiment']}

=== AI PRE-RECOMMENDATION ===
Direction: {analysis['recommendation']['direction']}
Confidence: {analysis['recommendation']['confidence']:.0%}
Suggested Strategy: {analysis['recommendation']['recommended_strategy']}
Reasoning: {analysis['recommendation']['reasoning']}

=== YOUR TASK ===
Based on all this data, decide:
1. Should we trade options on this symbol? (YES/NO)
2. If YES, what strategy? (BULL_PUT_SPREAD, BEAR_CALL_SPREAD, IRON_CONDOR, BULL_CALL_SPREAD, BEAR_PUT_SPREAD, or NONE)
3. What DTE to target? (21-45 days recommended)
4. What delta for short strikes? (0.20-0.35 typical)
5. Position size recommendation?

ACCOUNT VALUE: ${account_value:.2f}
MAX OPTIONS ALLOCATION: 20% = ${account_value * 0.20:.2f}

Respond with JSON:
{{
    "trade": true | false,
    "strategy": "strategy name",
    "direction": "BULLISH" | "BEARISH" | "NEUTRAL",
    "target_dte": 30,
    "short_delta": 0.30,
    "position_size_pct": 0.05,
    "confidence": 0.75,
    "reasoning": "detailed reasoning",
    "key_factors": ["factor1", "factor2"],
    "risks": ["risk1", "risk2"]
}}
"""
        
        response = self.opus.client.messages.create(
            model=self.opus.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_decision(response.content[0].text, analysis)
    
    def _parse_decision(self, response_text: str, analysis: dict) -> dict:
        """Parse Opus response"""
        try:
            import json
            clean = response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            decision = json.loads(clean)
            decision['analysis'] = analysis
            return decision
        except:
            return {
                'trade': False,
                'reasoning': 'Failed to parse Opus response',
                'analysis': analysis
            }
```

### Options Intelligence Data Sources

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              DATA SOURCES FOR OPTIONS INTELLIGENCE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FROM ALPACA API:                                                           │
│  ────────────────                                                           │
│  • Options chains (strikes, expirations, prices)                            │
│  • Greeks (delta, gamma, theta, vega)                                       │
│  • Open interest                                                            │
│  • Volume                                                                   │
│  • Historical stock data (for HV calculation)                               │
│                                                                             │
│  CALCULATED INTERNALLY:                                                     │
│  ──────────────────────                                                     │
│  • IV Rank (requires storing historical IV)                                 │
│  • IV Percentile                                                            │
│  • Max Pain                                                                 │
│  • Put/Call Ratios                                                          │
│  • Unusual Activity Detection                                               │
│  • Technical Indicators                                                     │
│                                                                             │
│  FROM NEWS/SENTIMENT MODULE:                                                │
│  ────────────────────────────                                               │
│  • News sentiment                                                           │
│  • Social sentiment                                                         │
│  • Earnings calendar (would need external API)                              │
│                                                                             │
│  OPTIONAL EXTERNAL SOURCES (for enhanced intelligence):                     │
│  ─────────────────────────────────────────────────────                      │
│  • Unusual Whales API - Options flow data                                   │
│  • FlowAlgo - Sweep detection                                               │
│  • Cheddar Flow - Dark pool data                                            │
│  • WhaleStream - Institutional activity                                     │
│  • Earnings Whispers - Earnings calendar                                    │
│  • NOTE: These are paid services, start without them                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How the AI Decides Long vs Short on Options

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           AI OPTIONS DECISION FLOWCHART                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  START: Get Options Intelligence for Symbol                                 │
│                         ↓                                                   │
│  ┌─────────────────────────────────────────┐                               │
│  │   CHECK VOLATILITY (IV Rank)            │                               │
│  │   ─────────────────────────             │                               │
│  │   IV Rank > 60%? → SELL PREMIUM         │                               │
│  │   IV Rank < 40%? → BUY OPTIONS          │                               │
│  └─────────────────────────────────────────┘                               │
│                         ↓                                                   │
│  ┌─────────────────────────────────────────┐                               │
│  │   DETERMINE DIRECTION                   │                               │
│  │   ──────────────────────                │                               │
│  │   Options Flow Bullish?  (+1)           │                               │
│  │   Options Flow Bearish?  (-1)           │                               │
│  │   Trend Uptrend?         (+1)           │                               │
│  │   Trend Downtrend?       (-1)           │                               │
│  │   RSI Oversold?          (+0.5)         │                               │
│  │   RSI Overbought?        (-0.5)         │                               │
│  │   Sentiment Bullish?     (+0.5)         │                               │
│  │   Sentiment Bearish?     (-0.5)         │                               │
│  │                                         │                               │
│  │   Score > +1.5 → BULLISH                │                               │
│  │   Score < -1.5 → BEARISH                │                               │
│  │   Else        → NEUTRAL                 │                               │
│  └─────────────────────────────────────────┘                               │
│                         ↓                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    STRATEGY SELECTION                                │   │
│  │   ─────────────────────────────────────────────────────────────────  │   │
│  │                                                                      │   │
│  │   HIGH IV + BULLISH    → Bull Put Spread (sell put spread)          │   │
│  │   HIGH IV + BEARISH    → Bear Call Spread (sell call spread)        │   │
│  │   HIGH IV + NEUTRAL    → Iron Condor (sell both)                    │   │
│  │                                                                      │   │
│  │   LOW IV + BULLISH     → Bull Call Spread (buy call spread)         │   │
│  │   LOW IV + BEARISH     → Bear Put Spread (buy put spread)           │   │
│  │   LOW IV + NEUTRAL     → Wait / No Trade                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                         ↓                                                   │
│  ┌─────────────────────────────────────────┐                               │
│  │   OPUS FINAL REVIEW                     │                               │
│  │   ─────────────────────                 │                               │
│  │   • Confirms or modifies recommendation │                               │
│  │   • Sets specific strikes and DTE       │                               │
│  │   • Sizes position appropriately        │                               │
│  │   • Logs reasoning for learning         │                               │
│  └─────────────────────────────────────────┘                               │
│                         ↓                                                   │
│                    EXECUTE TRADE                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Advanced Professional Options Trading Features

These are the features that separate professional options traders from amateurs. The AI MUST use these to make informed decisions.

### 1. Gamma Exposure (GEX) Calculator

**WHY THIS MATTERS:** Gamma Exposure tells you how market makers will hedge, which creates support/resistance levels and affects volatility.

```python
# options/gamma_exposure.py

from datetime import datetime
from typing import Dict, List
import numpy as np
import pandas as pd

class GammaExposureCalculator:
    """
    Calculate Gamma Exposure (GEX) to understand dealer positioning.
    
    KEY INSIGHTS:
    ─────────────
    • POSITIVE GEX = Dealers buy dips, sell rallies → DAMPENED VOLATILITY
    • NEGATIVE GEX = Dealers buy rallies, sell dips → AMPLIFIED VOLATILITY
    • GEX FLIP LEVEL = Price where gamma goes from + to - (key inflection)
    • PUT WALLS = Support levels from put gamma concentration
    • CALL WALLS = Resistance levels from call gamma concentration
    
    This is how professional traders predict volatility and price magnets.
    """
    
    def __init__(self, alpaca_client):
        self.alpaca = alpaca_client
        
    def calculate_gex(self, symbol: str, chain: dict) -> dict:
        """
        Calculate complete Gamma Exposure analysis for a symbol.
        
        Returns:
            - Net GEX (positive = stable, negative = volatile)
            - GEX by strike (where are the gamma walls?)
            - GEX flip level (where does volatility behavior change?)
            - Put/Call walls (support/resistance levels)
        """
        current_price = self.alpaca.get_current_price(symbol)
        
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])
        
        if not calls or not puts:
            return {'error': 'No options data'}
        
        # Calculate GEX for each strike
        gex_by_strike = {}
        total_call_gex = 0
        total_put_gex = 0
        
        for call in calls:
            strike = call['strike']
            gamma = call.get('gamma', 0)
            oi = call.get('open_interest', 0)
            
            # GEX = Gamma × Open Interest × 100 × Spot Price
            # Multiply by 100 for contract multiplier
            call_gex = gamma * oi * 100 * current_price
            
            if strike not in gex_by_strike:
                gex_by_strike[strike] = {'call_gex': 0, 'put_gex': 0, 'net_gex': 0}
            
            gex_by_strike[strike]['call_gex'] = call_gex
            total_call_gex += call_gex
        
        for put in puts:
            strike = put['strike']
            gamma = put.get('gamma', 0)
            oi = put.get('open_interest', 0)
            
            # Puts have negative GEX (dealers are typically short puts)
            put_gex = -gamma * oi * 100 * current_price
            
            if strike not in gex_by_strike:
                gex_by_strike[strike] = {'call_gex': 0, 'put_gex': 0, 'net_gex': 0}
            
            gex_by_strike[strike]['put_gex'] = put_gex
            total_put_gex += put_gex
        
        # Calculate net GEX per strike
        for strike in gex_by_strike:
            gex_by_strike[strike]['net_gex'] = (
                gex_by_strike[strike]['call_gex'] + 
                gex_by_strike[strike]['put_gex']
            )
        
        # Net GEX for entire chain
        net_gex = total_call_gex + total_put_gex
        
        # Find GEX flip level (where net GEX changes sign)
        gex_flip = self._find_gex_flip_level(gex_by_strike, current_price)
        
        # Find put and call walls
        put_wall, call_wall = self._find_gamma_walls(gex_by_strike, current_price)
        
        # Determine volatility forecast
        if net_gex > 0:
            vol_forecast = 'LOW_VOLATILITY'
            vol_explanation = 'Positive GEX - dealers will dampen moves by buying dips and selling rallies'
        else:
            vol_forecast = 'HIGH_VOLATILITY'
            vol_explanation = 'Negative GEX - dealers will amplify moves by chasing price'
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'net_gex': net_gex,
            'total_call_gex': total_call_gex,
            'total_put_gex': total_put_gex,
            'gex_flip_level': gex_flip,
            'put_wall': put_wall,  # Support level
            'call_wall': call_wall,  # Resistance level
            'volatility_forecast': vol_forecast,
            'volatility_explanation': vol_explanation,
            'gex_by_strike': dict(sorted(gex_by_strike.items())),
            'position_relative_to_flip': 'ABOVE' if current_price > gex_flip else 'BELOW',
            'trading_implications': self._get_trading_implications(
                net_gex, current_price, gex_flip, put_wall, call_wall
            )
        }
    
    def _find_gex_flip_level(self, gex_by_strike: dict, current_price: float) -> float:
        """Find the price level where GEX flips from positive to negative"""
        strikes = sorted(gex_by_strike.keys())
        
        # Start from ATM and look for sign change
        atm_idx = min(range(len(strikes)), key=lambda i: abs(strikes[i] - current_price))
        
        # Look downward for flip
        for i in range(atm_idx, 0, -1):
            if (gex_by_strike[strikes[i]]['net_gex'] > 0 and 
                gex_by_strike[strikes[i-1]]['net_gex'] < 0):
                return (strikes[i] + strikes[i-1]) / 2
        
        # Look upward for flip
        for i in range(atm_idx, len(strikes) - 1):
            if (gex_by_strike[strikes[i]]['net_gex'] > 0 and 
                gex_by_strike[strikes[i+1]]['net_gex'] < 0):
                return (strikes[i] + strikes[i+1]) / 2
        
        # No flip found, return current price
        return current_price
    
    def _find_gamma_walls(self, gex_by_strike: dict, 
                          current_price: float) -> tuple:
        """
        Find put wall (support) and call wall (resistance).
        These are strikes with highest gamma concentration.
        """
        strikes_below = {k: v for k, v in gex_by_strike.items() if k < current_price}
        strikes_above = {k: v for k, v in gex_by_strike.items() if k > current_price}
        
        # Put wall = highest put gamma below current price
        put_wall = None
        max_put_gex = 0
        for strike, gex in strikes_below.items():
            if abs(gex['put_gex']) > max_put_gex:
                max_put_gex = abs(gex['put_gex'])
                put_wall = strike
        
        # Call wall = highest call gamma above current price
        call_wall = None
        max_call_gex = 0
        for strike, gex in strikes_above.items():
            if gex['call_gex'] > max_call_gex:
                max_call_gex = gex['call_gex']
                call_wall = strike
        
        return put_wall, call_wall
    
    def _get_trading_implications(self, net_gex: float, current_price: float,
                                  gex_flip: float, put_wall: float, 
                                  call_wall: float) -> dict:
        """Generate actionable trading insights from GEX data"""
        implications = {
            'volatility_expectation': None,
            'support_level': put_wall,
            'resistance_level': call_wall,
            'recommended_strategies': [],
            'warnings': []
        }
        
        if net_gex > 0:
            implications['volatility_expectation'] = 'LOW - Price likely to stay range-bound'
            implications['recommended_strategies'] = [
                'Iron Condors (benefit from low vol)',
                'Credit Spreads (collect premium in stable market)',
                'Sell Strangles (if approved for naked options)'
            ]
        else:
            implications['volatility_expectation'] = 'HIGH - Expect larger price swings'
            implications['recommended_strategies'] = [
                'Long Straddles (benefit from big moves)',
                'Debit Spreads (directional plays)',
                'Avoid selling premium'
            ]
        
        # Warn if price is near gamma walls
        if put_wall and abs(current_price - put_wall) / current_price < 0.02:
            implications['warnings'].append(
                f'Price near put wall at ${put_wall} - potential support'
            )
        if call_wall and abs(current_price - call_wall) / current_price < 0.02:
            implications['warnings'].append(
                f'Price near call wall at ${call_wall} - potential resistance'
            )
        
        return implications
```

### 2. Expected Move Calculator

**WHY THIS MATTERS:** The Expected Move tells you what the options market thinks the stock will do. If you think it will move MORE, buy options. If LESS, sell options.

```python
# options/expected_move.py

import math
from datetime import datetime
from typing import Dict, Optional

class ExpectedMoveCalculator:
    """
    Calculate the Expected Move - what the options market predicts.
    
    KEY INSIGHT:
    ────────────
    Expected Move = 85% × ATM Straddle Price
    
    OR more precisely:
    Expected Move = 60% × ATM Straddle + 30% × 1-strike Strangle + 10% × 2-strike Strangle
    
    USE CASES:
    ──────────
    1. EARNINGS TRADES: Compare expected move to historical earnings moves
       - If historical > expected → Options are CHEAP → BUY straddles
       - If historical < expected → Options are EXPENSIVE → SELL straddles
       
    2. STRIKE SELECTION: Set strikes outside expected move for credit spreads
    
    3. PROFIT TARGETS: Use expected move as realistic target
    """
    
    def calculate_expected_move(self, symbol: str, chain: dict, 
                                current_price: float, days_to_expiration: int) -> dict:
        """
        Calculate expected move using multiple methods.
        """
        # Method 1: Simple (85% of ATM straddle)
        atm_straddle = self._get_atm_straddle_price(chain, current_price)
        simple_em = atm_straddle * 0.85
        
        # Method 2: Weighted (more accurate)
        weighted_em = self._calculate_weighted_expected_move(chain, current_price)
        
        # Method 3: From IV (theoretical)
        iv = self._get_atm_iv(chain, current_price)
        iv_based_em = self._calculate_from_iv(current_price, iv, days_to_expiration)
        
        # Use weighted as primary
        expected_move = weighted_em if weighted_em > 0 else simple_em
        
        # Calculate range
        expected_high = current_price + expected_move
        expected_low = current_price - expected_move
        expected_pct = (expected_move / current_price) * 100
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'expected_move_dollars': round(expected_move, 2),
            'expected_move_pct': round(expected_pct, 2),
            'expected_high': round(expected_high, 2),
            'expected_low': round(expected_low, 2),
            'days_to_expiration': days_to_expiration,
            'atm_straddle_price': round(atm_straddle, 2),
            'atm_iv': round(iv * 100, 1),
            'calculation_methods': {
                'simple_85pct': round(simple_em, 2),
                'weighted': round(weighted_em, 2),
                'iv_based': round(iv_based_em, 2)
            },
            'interpretation': self._interpret_expected_move(expected_pct, iv)
        }
    
    def _get_atm_straddle_price(self, chain: dict, current_price: float) -> float:
        """Get the price of the ATM straddle"""
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])
        
        if not calls or not puts:
            return 0
        
        # Find ATM strike
        atm_call = min(calls, key=lambda x: abs(x['strike'] - current_price))
        atm_put = min(puts, key=lambda x: abs(x['strike'] - current_price))
        
        # Straddle = Call price + Put price (use mid prices)
        call_price = (atm_call.get('bid', 0) + atm_call.get('ask', 0)) / 2
        put_price = (atm_put.get('bid', 0) + atm_put.get('ask', 0)) / 2
        
        return call_price + put_price
    
    def _calculate_weighted_expected_move(self, chain: dict, 
                                          current_price: float) -> float:
        """
        More accurate expected move calculation:
        60% ATM Straddle + 30% 1-Strike Strangle + 10% 2-Strike Strangle
        """
        calls = sorted(chain.get('calls', []), key=lambda x: x['strike'])
        puts = sorted(chain.get('puts', []), key=lambda x: x['strike'])
        
        if len(calls) < 3 or len(puts) < 3:
            return 0
        
        # Find ATM index
        atm_idx = min(range(len(calls)), 
                     key=lambda i: abs(calls[i]['strike'] - current_price))
        
        # ATM straddle (60%)
        atm_call = calls[atm_idx]
        atm_put = puts[atm_idx]
        atm_straddle = self._get_mid_price(atm_call) + self._get_mid_price(atm_put)
        
        # 1-strike OTM strangle (30%)
        strangle_1 = 0
        if atm_idx + 1 < len(calls) and atm_idx - 1 >= 0:
            otm_call_1 = calls[atm_idx + 1]
            otm_put_1 = puts[atm_idx - 1]
            strangle_1 = self._get_mid_price(otm_call_1) + self._get_mid_price(otm_put_1)
        
        # 2-strike OTM strangle (10%)
        strangle_2 = 0
        if atm_idx + 2 < len(calls) and atm_idx - 2 >= 0:
            otm_call_2 = calls[atm_idx + 2]
            otm_put_2 = puts[atm_idx - 2]
            strangle_2 = self._get_mid_price(otm_call_2) + self._get_mid_price(otm_put_2)
        
        expected_move = (0.60 * atm_straddle + 
                        0.30 * strangle_1 + 
                        0.10 * strangle_2)
        
        return expected_move
    
    def _calculate_from_iv(self, price: float, iv: float, dte: int) -> float:
        """Calculate expected move from IV (1 standard deviation)"""
        # 1 SD move = Price × IV × sqrt(DTE/365)
        return price * iv * math.sqrt(dte / 365)
    
    def _get_atm_iv(self, chain: dict, current_price: float) -> float:
        """Get ATM implied volatility"""
        calls = chain.get('calls', [])
        if not calls:
            return 0.25
        atm_call = min(calls, key=lambda x: abs(x['strike'] - current_price))
        return atm_call.get('iv', 0.25)
    
    def _get_mid_price(self, option: dict) -> float:
        """Get mid price of an option"""
        bid = option.get('bid', 0)
        ask = option.get('ask', bid)
        return (bid + ask) / 2 if bid > 0 else option.get('last', 0)
    
    def _interpret_expected_move(self, expected_pct: float, iv: float) -> str:
        """Generate interpretation of expected move"""
        if expected_pct > 10:
            return f"HIGH expected move ({expected_pct:.1f}%). Market expects major price action. Consider if this is justified."
        elif expected_pct > 5:
            return f"ELEVATED expected move ({expected_pct:.1f}%). Moderate volatility expected. Check for upcoming events."
        else:
            return f"NORMAL expected move ({expected_pct:.1f}%). Market expects typical price action."


class EarningsExpectedMoveAnalyzer:
    """
    Specialized analyzer for earnings events.
    Compares implied move to historical earnings moves.
    """
    
    def __init__(self, alpaca_client, expected_move_calc: ExpectedMoveCalculator):
        self.alpaca = alpaca_client
        self.em_calc = expected_move_calc
        
    def analyze_earnings_opportunity(self, symbol: str, chain: dict,
                                    earnings_date: str) -> dict:
        """
        Analyze if options are over/underpriced for earnings.
        
        THIS IS HOW PROS TRADE EARNINGS:
        1. Calculate what market expects (implied move)
        2. Look at historical earnings moves
        3. If historical > implied → Buy straddles (options are cheap)
        4. If historical < implied → Sell straddles (options are expensive)
        """
        current_price = self.alpaca.get_current_price(symbol)
        
        # Get historical earnings moves
        historical_moves = self._get_historical_earnings_moves(symbol)
        avg_historical_move = sum(historical_moves) / len(historical_moves) if historical_moves else 0
        
        # Calculate current expected move
        days_to_earnings = self._days_until(earnings_date)
        em = self.em_calc.calculate_expected_move(symbol, chain, current_price, days_to_earnings)
        implied_move_pct = em['expected_move_pct']
        
        # Compare implied vs historical
        if avg_historical_move > 0:
            implied_vs_historical = implied_move_pct / avg_historical_move
        else:
            implied_vs_historical = 1.0
        
        # Generate recommendation
        if implied_vs_historical < 0.8:
            # Options are cheap relative to historical
            recommendation = 'BUY_STRADDLE'
            reasoning = f"Implied move ({implied_move_pct:.1f}%) is below historical average ({avg_historical_move:.1f}%). Options may be underpriced."
        elif implied_vs_historical > 1.2:
            # Options are expensive relative to historical
            recommendation = 'SELL_STRADDLE'
            reasoning = f"Implied move ({implied_move_pct:.1f}%) is above historical average ({avg_historical_move:.1f}%). Options may be overpriced."
        else:
            recommendation = 'NO_EDGE'
            reasoning = f"Implied move ({implied_move_pct:.1f}%) is in line with historical ({avg_historical_move:.1f}%). No clear edge."
        
        return {
            'symbol': symbol,
            'earnings_date': earnings_date,
            'days_to_earnings': days_to_earnings,
            'current_price': current_price,
            'implied_move_pct': implied_move_pct,
            'implied_move_dollars': em['expected_move_dollars'],
            'historical_moves': historical_moves[-8:],  # Last 8 quarters
            'avg_historical_move': round(avg_historical_move, 2),
            'max_historical_move': max(historical_moves) if historical_moves else 0,
            'min_historical_move': min(historical_moves) if historical_moves else 0,
            'implied_vs_historical_ratio': round(implied_vs_historical, 2),
            'recommendation': recommendation,
            'reasoning': reasoning,
            'iv_crush_warning': self._estimate_iv_crush(em['atm_iv']),
            'strategies': self._get_earnings_strategies(recommendation, em)
        }
    
    def _get_historical_earnings_moves(self, symbol: str) -> list:
        """Get historical price moves on earnings days"""
        # Would integrate with earnings API
        # For now, return placeholder
        # Real implementation would fetch from financial data API
        return []  # List of % moves
    
    def _days_until(self, date_str: str) -> int:
        """Calculate days until a date"""
        target = datetime.strptime(date_str, '%Y-%m-%d')
        return (target - datetime.now()).days
    
    def _estimate_iv_crush(self, current_iv: float) -> dict:
        """Estimate how much IV will drop after earnings"""
        # IV typically drops 30-50% after earnings
        estimated_crush_low = current_iv * 0.30
        estimated_crush_high = current_iv * 0.50
        
        return {
            'current_iv': round(current_iv * 100, 1),
            'estimated_post_earnings_iv_low': round((current_iv - estimated_crush_high) * 100, 1),
            'estimated_post_earnings_iv_high': round((current_iv - estimated_crush_low) * 100, 1),
            'warning': 'IV will likely crush 30-50% after earnings. Avoid buying premium unless expecting large move.'
        }
    
    def _get_earnings_strategies(self, recommendation: str, em: dict) -> list:
        """Get specific strategy recommendations"""
        if recommendation == 'BUY_STRADDLE':
            return [
                {
                    'strategy': 'Long Straddle',
                    'description': 'Buy ATM call + ATM put',
                    'breakeven_up': em['expected_high'] * 1.05,
                    'breakeven_down': em['expected_low'] * 0.95,
                    'max_loss': 'Premium paid',
                    'max_gain': 'Unlimited'
                },
                {
                    'strategy': 'Long Strangle',
                    'description': 'Buy OTM call + OTM put (cheaper)',
                    'note': 'Requires larger move but costs less'
                }
            ]
        elif recommendation == 'SELL_STRADDLE':
            return [
                {
                    'strategy': 'Iron Condor',
                    'description': 'Sell OTM put spread + OTM call spread',
                    'short_strikes': f"Put at ${em['expected_low']:.0f}, Call at ${em['expected_high']:.0f}",
                    'note': 'Defined risk, benefits from IV crush'
                },
                {
                    'strategy': 'Short Strangle (if approved)',
                    'description': 'Sell OTM call + OTM put',
                    'warning': 'Undefined risk - requires approval and margin'
                }
            ]
        return []
```

### 3. Earnings Intelligence Module

**WHY THIS MATTERS:** NEVER trade options blind around earnings. The AI must know when earnings are, what the market expects, and historical moves.

```python
# options/earnings_intelligence.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

class EarningsIntelligence:
    """
    Complete earnings awareness for options trading.
    
    CRITICAL RULES:
    ───────────────
    1. NEVER buy long options right before earnings (IV crush risk)
    2. IV typically peaks 1-2 days before earnings
    3. IV crushes 30-50% immediately after announcement
    4. Sell premium when IV is high (before earnings)
    5. Buy premium when IV is low (after earnings settles)
    """
    
    def __init__(self, alpaca_client, earnings_api=None):
        self.alpaca = alpaca_client
        self.earnings_api = earnings_api  # Would use Earnings Whispers, Yahoo Finance, etc.
        
        # Store historical earnings data
        self.earnings_history = {}
        
    def get_earnings_analysis(self, symbol: str) -> dict:
        """
        Get complete earnings intelligence for a symbol.
        """
        # Get next earnings date
        next_earnings = self._get_next_earnings_date(symbol)
        
        # Get historical earnings moves
        historical_moves = self._get_historical_earnings_moves(symbol)
        
        # Calculate statistics
        if historical_moves:
            avg_move = sum(abs(m) for m in historical_moves) / len(historical_moves)
            max_move = max(abs(m) for m in historical_moves)
            min_move = min(abs(m) for m in historical_moves)
            beat_rate = sum(1 for m in historical_moves if m > 0) / len(historical_moves)
        else:
            avg_move = max_move = min_move = 0
            beat_rate = 0.5
        
        # Calculate days to earnings
        if next_earnings:
            days_to_earnings = (next_earnings - datetime.now()).days
        else:
            days_to_earnings = None
        
        # Determine trading implications
        implications = self._get_earnings_implications(days_to_earnings)
        
        return {
            'symbol': symbol,
            'next_earnings_date': next_earnings.strftime('%Y-%m-%d') if next_earnings else None,
            'days_to_earnings': days_to_earnings,
            'historical_moves': historical_moves[-12:],  # Last 12 quarters
            'avg_earnings_move_pct': round(avg_move, 2),
            'max_earnings_move_pct': round(max_move, 2),
            'min_earnings_move_pct': round(min_move, 2),
            'beat_rate': round(beat_rate * 100, 1),
            'earnings_time': 'AMC',  # After Market Close / BMO / Unknown
            'trading_implications': implications,
            'iv_behavior': self._get_iv_behavior_around_earnings(days_to_earnings)
        }
    
    def _get_next_earnings_date(self, symbol: str) -> Optional[datetime]:
        """Get next earnings date from API"""
        # Would integrate with earnings calendar API
        # Placeholder - real implementation needed
        return None
    
    def _get_historical_earnings_moves(self, symbol: str) -> list:
        """
        Get historical price moves on earnings days.
        Returns list of % moves (positive = beat, negative = miss)
        """
        # Would fetch from financial data API
        # Returns list like [5.2, -3.1, 7.8, -2.2, ...] representing % moves
        return []
    
    def _get_earnings_implications(self, days_to_earnings: Optional[int]) -> dict:
        """Generate trading implications based on earnings proximity"""
        if days_to_earnings is None:
            return {
                'status': 'NO_EARNINGS_DATA',
                'recommendation': 'Trade normally - no known earnings date',
                'iv_status': 'NORMAL',
                'warnings': []
            }
        
        if days_to_earnings <= 0:
            return {
                'status': 'EARNINGS_PASSED',
                'recommendation': 'IV crush has occurred. Safe to buy options if IV has normalized.',
                'iv_status': 'POST_CRUSH',
                'warnings': []
            }
        
        if days_to_earnings <= 2:
            return {
                'status': 'EARNINGS_IMMINENT',
                'recommendation': 'DO NOT buy options. IV is at peak. Only sell premium if experienced.',
                'iv_status': 'PEAK_IV',
                'warnings': [
                    '⚠️ IV CRUSH WARNING: Options will lose 30-50% of value after earnings',
                    '⚠️ Only sell credit spreads if you have a directional view',
                    '⚠️ Consider sitting out this trade entirely'
                ]
            }
        
        if days_to_earnings <= 7:
            return {
                'status': 'EARNINGS_WEEK',
                'recommendation': 'IV is elevated. Favor selling premium over buying.',
                'iv_status': 'ELEVATED_IV',
                'warnings': [
                    'IV will continue rising into earnings',
                    'Long options may lose money even if direction is correct'
                ]
            }
        
        if days_to_earnings <= 14:
            return {
                'status': 'EARNINGS_APPROACHING',
                'recommendation': 'IV starting to build. Consider earnings plays.',
                'iv_status': 'BUILDING_IV',
                'warnings': []
            }
        
        return {
            'status': 'NORMAL',
            'recommendation': 'Earnings far enough away. Trade normally.',
            'iv_status': 'NORMAL',
            'warnings': []
        }
    
    def _get_iv_behavior_around_earnings(self, days_to_earnings: Optional[int]) -> dict:
        """Describe typical IV behavior pattern around earnings"""
        return {
            'typical_pattern': {
                '14_days_out': 'IV begins gradual rise',
                '7_days_out': 'IV acceleration begins',
                '2_days_out': 'IV at or near peak',
                '1_day_out': 'IV at peak (best time to sell)',
                'announcement': 'IV peaks then crashes',
                'next_day': 'IV crushed 30-50% from peak'
            },
            'current_phase': self._get_iv_phase(days_to_earnings),
            'strategy_by_phase': {
                'NORMAL': 'Any strategy appropriate',
                'BUILDING_IV': 'Consider buying pre-earnings if expecting IV ramp',
                'ELEVATED_IV': 'Sell premium, avoid buying options',
                'PEAK_IV': 'Only sell premium, expect crush',
                'POST_CRUSH': 'Safe to buy options again'
            }
        }
    
    def _get_iv_phase(self, days: Optional[int]) -> str:
        """Determine current IV phase"""
        if days is None:
            return 'NORMAL'
        if days <= 0:
            return 'POST_CRUSH'
        if days <= 2:
            return 'PEAK_IV'
        if days <= 7:
            return 'ELEVATED_IV'
        if days <= 14:
            return 'BUILDING_IV'
        return 'NORMAL'


class EventCalendar:
    """
    Track all events that affect IV and options pricing.
    Not just earnings - Fed meetings, CPI, etc.
    """
    
    MAJOR_EVENTS = {
        'FOMC': 'Federal Reserve interest rate decision',
        'CPI': 'Consumer Price Index inflation data',
        'NFP': 'Non-Farm Payrolls jobs report',
        'GDP': 'Gross Domestic Product',
        'EARNINGS': 'Company earnings announcement',
        'EX_DIVIDEND': 'Ex-dividend date (affects options pricing)',
        'OPEX': 'Options expiration (monthly/weekly)'
    }
    
    def __init__(self):
        self.events = []
        
    def get_upcoming_events(self, symbol: str, days_ahead: int = 14) -> list:
        """Get all events that could affect options pricing"""
        upcoming = []
        
        # Would fetch from economic calendar API
        # Returns list of events affecting this symbol or the market
        
        return upcoming
    
    def should_trade_options(self, symbol: str) -> dict:
        """
        Determine if it's safe to trade options given upcoming events.
        """
        events = self.get_upcoming_events(symbol, days_ahead=7)
        
        blocking_events = [e for e in events if e.get('impact') == 'HIGH']
        
        if blocking_events:
            return {
                'safe_to_trade': False,
                'reason': f"High-impact event coming: {blocking_events[0]['name']}",
                'events': blocking_events,
                'recommendation': 'Wait until after event or adjust for IV'
            }
        
        return {
            'safe_to_trade': True,
            'reason': 'No high-impact events in next 7 days',
            'events': events,
            'recommendation': 'Normal options trading appropriate'
        }
```

### Summary: What the AI Uses to Decide Options Trades

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           COMPLETE OPTIONS INTELLIGENCE STACK                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  VOLATILITY (Is premium expensive or cheap?)                                │
│  ───────────────────────────────────────────                                │
│  ✓ IV Rank (0-100%) - Where is IV vs its 52-week range?                     │
│  ✓ IV Percentile - How often has IV been lower?                             │
│  ✓ IV vs HV - Is implied higher than realized?                              │
│  → HIGH IV = Sell premium | LOW IV = Buy options                            │
│                                                                             │
│  FLOW (What are institutions doing?)                                        │
│  ────────────────────────────────────                                       │
│  ✓ Put/Call Ratio - Bullish or bearish sentiment                            │
│  ✓ Unusual Options Activity - Big bets being placed                         │
│  ✓ Volume vs Open Interest - New positions being opened                     │
│  → Follow smart money, don't fight it                                       │
│                                                                             │
│  GAMMA EXPOSURE (How will dealers move the market?)                         │
│  ──────────────────────────────────────────────────                         │
│  ✓ Net GEX - Positive = low vol, Negative = high vol                        │
│  ✓ Put/Call Walls - Support and resistance from options                     │
│  ✓ GEX Flip Level - Where volatility behavior changes                       │
│  → Trade with dealer flow, not against it                                   │
│                                                                             │
│  EXPECTED MOVE (What does the market predict?)                              │
│  ─────────────────────────────────────────────                              │
│  ✓ ATM Straddle × 85% = Expected range                                      │
│  ✓ Compare to historical moves                                              │
│  ✓ If actual > expected → Options were cheap                                │
│  → Set strikes outside expected move for credit spreads                     │
│                                                                             │
│  EARNINGS/EVENTS (What's coming that changes everything?)                   │
│  ────────────────────────────────────────────────────────                   │
│  ✓ Days to earnings - Determines IV phase                                   │
│  ✓ Historical earnings moves - What usually happens                         │
│  ✓ IV Crush prediction - How much premium will evaporate                    │
│  → NEVER buy options right before earnings                                  │
│                                                                             │
│  TECHNICALS (What direction is the stock going?)                            │
│  ───────────────────────────────────────────────                            │
│  ✓ Trend (uptrend/downtrend/sideways)                                       │
│  ✓ RSI, MACD, Bollinger Bands                                               │
│  ✓ Support/Resistance levels                                                │
│  → Determines bullish/bearish/neutral bias                                  │
│                                                                             │
│  NEWS/SENTIMENT (What's the story?)                                         │
│  ──────────────────────────────────                                         │
│  ✓ Recent headlines                                                         │
│  ✓ Social sentiment                                                         │
│  ✓ Analyst ratings                                                          │
│  → Confirms or contradicts technical view                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

THE AI DECISION PROCESS:
────────────────────────
1. Check earnings calendar → Is there an event that changes everything?
2. Analyze IV Rank → Are options expensive or cheap?
3. Calculate GEX → Will volatility be high or low?
4. Check options flow → What are institutions betting on?
5. Calculate expected move → What's the market predicting?
6. Analyze technicals → What direction is the stock going?
7. Read sentiment → Does news confirm or contradict?
8. COMBINE ALL FACTORS → Generate recommendation
9. Opus reviews and approves/modifies → Final decision
10. Execute trade with proper sizing → Risk management
```

```python
# intelligence/regime_detector.py

class MarketRegimeDetector:
    """
    Detect current market regime to adjust strategies.
    Different strategies work in different conditions.
    """
    
    REGIMES = ['BULL_TRENDING', 'BEAR_TRENDING', 'RANGING', 'HIGH_VOLATILITY', 'CRASH']
    
    def __init__(self):
        self.current_regime = None
        self.regime_history = []
        
    def detect_regime(self, spy_data: pd.DataFrame, vix_data: pd.DataFrame) -> dict:
        """
        Analyze SPY and VIX to determine market regime.
        """
        # Trend analysis
        sma_50 = spy_data['close'].rolling(50).mean().iloc[-1]
        sma_200 = spy_data['close'].rolling(200).mean().iloc[-1]
        current_price = spy_data['close'].iloc[-1]
        
        # Volatility analysis
        current_vix = vix_data['close'].iloc[-1]
        vix_sma = vix_data['close'].rolling(20).mean().iloc[-1]
        
        # ADX for trend strength
        adx = ta.adx(spy_data['high'], spy_data['low'], spy_data['close'])
        trend_strength = adx['ADX_14'].iloc[-1]
        
        # Determine regime
        if current_vix > 35:
            regime = 'CRASH'
        elif current_vix > 25:
            regime = 'HIGH_VOLATILITY'
        elif trend_strength < 20:
            regime = 'RANGING'
        elif current_price > sma_50 > sma_200:
            regime = 'BULL_TRENDING'
        elif current_price < sma_50 < sma_200:
            regime = 'BEAR_TRENDING'
        else:
            regime = 'RANGING'
            
        # Strategy adjustments based on regime
        strategy_adjustments = self._get_strategy_adjustments(regime)
        
        self.current_regime = regime
        self.regime_history.append({
            'timestamp': datetime.now(),
            'regime': regime,
            'vix': current_vix,
            'trend_strength': trend_strength
        })
        
        return {
            'regime': regime,
            'confidence': self._calculate_regime_confidence(spy_data, vix_data),
            'vix': current_vix,
            'trend_strength': trend_strength,
            'strategy_adjustments': strategy_adjustments
        }
    
    def _get_strategy_adjustments(self, regime: str) -> dict:
        """Return strategy parameters based on regime"""
        adjustments = {
            'BULL_TRENDING': {
                'bias': 'long',
                'position_size_multiplier': 1.2,
                'stop_loss_multiplier': 1.0,
                'preferred_strategies': ['momentum', 'breakout'],
                'avoid_strategies': ['mean_reversion_short']
            },
            'BEAR_TRENDING': {
                'bias': 'short',
                'position_size_multiplier': 0.8,
                'stop_loss_multiplier': 0.8,  # Tighter stops
                'preferred_strategies': ['mean_reversion', 'fade_rallies'],
                'avoid_strategies': ['breakout_long']
            },
            'RANGING': {
                'bias': 'neutral',
                'position_size_multiplier': 1.0,
                'stop_loss_multiplier': 1.0,
                'preferred_strategies': ['mean_reversion', 'iron_condor'],
                'avoid_strategies': ['momentum', 'breakout']
            },
            'HIGH_VOLATILITY': {
                'bias': 'cautious',
                'position_size_multiplier': 0.5,  # Half size
                'stop_loss_multiplier': 1.5,  # Wider stops
                'preferred_strategies': ['premium_selling'],
                'avoid_strategies': ['momentum', 'all_directional']
            },
            'CRASH': {
                'bias': 'cash',
                'position_size_multiplier': 0.25,  # Minimal exposure
                'stop_loss_multiplier': 2.0,
                'preferred_strategies': ['cash', 'hedge'],
                'avoid_strategies': ['all_long']
            }
        }
        return adjustments.get(regime, adjustments['RANGING'])
```

### 4. Portfolio Correlation & Risk Analysis

```python
# risk/portfolio_analyzer.py

class PortfolioAnalyzer:
    """
    Analyze portfolio-level risk including correlations.
    Prevent over-concentration in correlated assets.
    """
    
    def __init__(self, learning_db):
        self.db = learning_db
        
    def analyze_portfolio(self, positions: list, market_data: dict) -> dict:
        """
        Comprehensive portfolio analysis.
        """
        if not positions:
            return {'status': 'empty'}
            
        symbols = [p['symbol'] for p in positions]
        
        # Get correlation matrix
        correlation_matrix = self._calculate_correlations(symbols, market_data)
        
        # Sector exposure
        sector_exposure = self._calculate_sector_exposure(positions)
        
        # Beta exposure (market risk)
        portfolio_beta = self._calculate_portfolio_beta(positions, market_data)
        
        # Concentration risk
        concentration = self._calculate_concentration(positions)
        
        # Value at Risk (VaR)
        var_95 = self._calculate_var(positions, market_data, confidence=0.95)
        
        return {
            'correlation_matrix': correlation_matrix,
            'highly_correlated_pairs': self._find_correlated_pairs(correlation_matrix),
            'sector_exposure': sector_exposure,
            'portfolio_beta': portfolio_beta,
            'concentration_risk': concentration,
            'var_95': var_95,
            'diversification_score': self._calculate_diversification_score(correlation_matrix),
            'warnings': self._generate_warnings(correlation_matrix, sector_exposure, concentration)
        }
    
    def _find_correlated_pairs(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> list:
        """Find pairs with correlation above threshold"""
        pairs = []
        for i, sym1 in enumerate(corr_matrix.columns):
            for j, sym2 in enumerate(corr_matrix.columns):
                if i < j and abs(corr_matrix.loc[sym1, sym2]) > threshold:
                    pairs.append({
                        'pair': (sym1, sym2),
                        'correlation': corr_matrix.loc[sym1, sym2]
                    })
        return pairs
    
    def _generate_warnings(self, corr_matrix, sector_exposure, concentration) -> list:
        """Generate risk warnings for Opus to consider"""
        warnings = []
        
        # High correlation warning
        correlated_pairs = self._find_correlated_pairs(corr_matrix, 0.8)
        if correlated_pairs:
            warnings.append({
                'type': 'HIGH_CORRELATION',
                'message': f"Highly correlated positions: {correlated_pairs}",
                'severity': 'medium'
            })
            
        # Sector concentration
        for sector, pct in sector_exposure.items():
            if pct > 0.4:  # More than 40% in one sector
                warnings.append({
                    'type': 'SECTOR_CONCENTRATION',
                    'message': f"{sector} exposure at {pct:.0%}",
                    'severity': 'high'
                })
                
        # Single position concentration
        if concentration['max_position_pct'] > 0.3:
            warnings.append({
                'type': 'POSITION_CONCENTRATION',
                'message': f"Largest position is {concentration['max_position_pct']:.0%} of portfolio",
                'severity': 'high'
            })
            
        return warnings
```

### 5. Multi-Timeframe Analysis

```python
# strategy/multi_timeframe.py

class MultiTimeframeAnalyzer:
    """
    Analyze multiple timeframes for confluence.
    Higher timeframe = more weight.
    """
    
    TIMEFRAMES = ['1D', '4H', '1H', '15Min']
    WEIGHTS = {'1D': 0.4, '4H': 0.3, '1H': 0.2, '15Min': 0.1}
    
    def analyze(self, symbol: str, data_by_timeframe: dict) -> dict:
        """
        Get signal confluence across timeframes.
        """
        signals = {}
        
        for tf in self.TIMEFRAMES:
            if tf in data_by_timeframe:
                signals[tf] = self._analyze_timeframe(data_by_timeframe[tf])
                
        # Calculate weighted confluence
        confluence_score = sum(
            signals[tf]['score'] * self.WEIGHTS[tf] 
            for tf in signals
        )
        
        # All timeframes must agree for high confidence
        all_bullish = all(s['direction'] == 'bullish' for s in signals.values())
        all_bearish = all(s['direction'] == 'bearish' for s in signals.values())
        
        return {
            'symbol': symbol,
            'timeframe_signals': signals,
            'confluence_score': confluence_score,
            'direction': 'bullish' if confluence_score > 0.3 else 'bearish' if confluence_score < -0.3 else 'neutral',
            'alignment': 'full' if (all_bullish or all_bearish) else 'partial',
            'confidence': abs(confluence_score) if (all_bullish or all_bearish) else abs(confluence_score) * 0.6
        }
```

### 6. Wash Sale Tracker

```python
# tax/wash_sale_tracker.py

class WashSaleTracker:
    """
    Track wash sales to avoid tax issues.
    Wash sale = sell at loss, rebuy within 30 days before/after.
    """
    
    def __init__(self, state_db):
        self.db = state_db
        self.wash_sale_window = 30  # days
        
    def check_wash_sale_risk(self, symbol: str, side: str) -> dict:
        """
        Check if a trade would trigger wash sale.
        """
        if side != 'buy':
            return {'risk': False}
            
        # Get recent sales of this symbol at a loss
        recent_loss_sales = self.db.get_loss_sales(
            symbol=symbol,
            days=self.wash_sale_window
        )
        
        if recent_loss_sales:
            total_disallowed_loss = sum(s['loss'] for s in recent_loss_sales)
            return {
                'risk': True,
                'disallowed_loss': total_disallowed_loss,
                'wash_sales': recent_loss_sales,
                'warning': f"Buying {symbol} would trigger wash sale. "
                          f"${total_disallowed_loss:.2f} loss would be disallowed."
            }
            
        return {'risk': False}
    
    def record_sale(self, symbol: str, quantity: float, 
                   sale_price: float, cost_basis: float):
        """Record a sale for wash sale tracking"""
        profit_loss = (sale_price - cost_basis) * quantity
        
        self.db.record_sale({
            'symbol': symbol,
            'quantity': quantity,
            'sale_price': sale_price,
            'cost_basis': cost_basis,
            'profit_loss': profit_loss,
            'is_loss': profit_loss < 0,
            'date': datetime.now(),
            'wash_sale_window_end': datetime.now() + timedelta(days=30)
        })
        
    def get_wash_sale_report(self, year: int = None) -> dict:
        """Generate wash sale report for tax purposes"""
        year = year or datetime.now().year
        
        wash_sales = self.db.get_wash_sales(year)
        
        return {
            'year': year,
            'total_wash_sales': len(wash_sales),
            'total_disallowed_losses': sum(ws['disallowed_loss'] for ws in wash_sales),
            'affected_symbols': list(set(ws['symbol'] for ws in wash_sales)),
            'details': wash_sales
        }
```

### 7. Notification System

```python
# notifications/notifier.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationSystem:
    """
    Send notifications for important events.
    """
    
    def __init__(self, config: dict):
        self.email_enabled = config.get('email_enabled', False)
        self.email_address = config.get('email_address')
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_password = config.get('smtp_password')
        
        # Desktop notifications
        self.desktop_enabled = config.get('desktop_enabled', True)
        
    def notify_trade_executed(self, trade: dict):
        """Notify when a trade is executed"""
        message = f"""
        🎯 TRADE EXECUTED
        
        Symbol: {trade['symbol']}
        Side: {trade['side'].upper()}
        Quantity: {trade['quantity']}
        Price: ${trade['price']:.2f}
        Stop Loss: ${trade['stop_loss']:.2f}
        Take Profit: ${trade['take_profit']:.2f}
        
        Opus Reasoning: {trade['reasoning']}
        """
        
        self._send_notification("Trade Executed", message)
        
    def notify_position_closed(self, position: dict):
        """Notify when a position is closed"""
        emoji = "✅" if position['profit_loss'] > 0 else "❌"
        
        message = f"""
        {emoji} POSITION CLOSED
        
        Symbol: {position['symbol']}
        P&L: ${position['profit_loss']:.2f} ({position['profit_loss_pct']:.1%})
        Hold Time: {position['hold_duration']}
        Exit Reason: {position['exit_reason']}
        """
        
        self._send_notification("Position Closed", message)
        
    def notify_daily_summary(self, summary: dict):
        """Send daily performance summary"""
        message = f"""
        📊 DAILY SUMMARY - {summary['date']}
        
        Starting Balance: ${summary['starting_balance']:.2f}
        Ending Balance: ${summary['ending_balance']:.2f}
        Day P&L: ${summary['day_pnl']:.2f} ({summary['day_pnl_pct']:.1%})
        
        Trades: {summary['trades_executed']}
        Wins: {summary['wins']} | Losses: {summary['losses']}
        Win Rate: {summary['win_rate']:.0%}
        
        Opus API Cost: ${summary['opus_cost']:.2f}
        Performance Tier: {summary['tier']}
        """
        
        self._send_notification("Daily Summary", message)
        
    def notify_circuit_breaker(self, reason: str):
        """URGENT: Circuit breaker triggered"""
        message = f"""
        🚨 CIRCUIT BREAKER ACTIVATED
        
        Reason: {reason}
        Time: {datetime.now()}
        
        All trading has been halted.
        Open orders have been cancelled.
        
        Manual intervention may be required.
        """
        
        self._send_notification("⚠️ CIRCUIT BREAKER", message, urgent=True)
        
    def _send_notification(self, title: str, message: str, urgent: bool = False):
        """Send via all enabled channels"""
        
        if self.desktop_enabled:
            self._send_desktop(title, message)
            
        if self.email_enabled:
            self._send_email(title, message)
            
    def _send_desktop(self, title: str, message: str):
        """Windows desktop notification"""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message[:256], duration=10)
        except:
            pass  # Fail silently if not available
            
    def _send_email(self, subject: str, body: str):
        """Send email notification"""
        if not all([self.email_address, self.smtp_password]):
            return
            
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.email_address
        msg['Subject'] = f"Leviathan: {subject}"
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.smtp_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Email notification failed: {e}")
```

### 8. Economic Calendar Integration

```python
# data/economic_calendar.py

class EconomicCalendar:
    """
    Track economic events that move markets.
    Avoid trading during high-impact events.
    """
    
    HIGH_IMPACT_EVENTS = [
        'FOMC', 'NFP', 'CPI', 'GDP', 'Retail Sales',
        'Unemployment', 'Fed Chair Speech', 'ECB Decision'
    ]
    
    def __init__(self, api_client):
        self.api = api_client
        
    def get_upcoming_events(self, days: int = 7) -> list:
        """Get upcoming economic events"""
        events = self.api.fetch_economic_calendar(days)
        
        return [{
            'date': e['date'],
            'time': e['time'],
            'event': e['event'],
            'impact': e['impact'],  # low, medium, high
            'forecast': e.get('forecast'),
            'previous': e.get('previous'),
            'is_high_impact': e['event'] in self.HIGH_IMPACT_EVENTS or e['impact'] == 'high'
        } for e in events]
    
    def should_avoid_trading(self) -> dict:
        """
        Check if we should avoid trading right now.
        Returns True 30 mins before/after high-impact events.
        """
        now = datetime.now()
        events = self.get_upcoming_events(days=1)
        
        for event in events:
            if not event['is_high_impact']:
                continue
                
            event_time = datetime.combine(event['date'], event['time'])
            time_to_event = (event_time - now).total_seconds() / 60  # minutes
            
            # Avoid 30 mins before and after
            if -30 <= time_to_event <= 30:
                return {
                    'avoid': True,
                    'reason': f"High-impact event: {event['event']} at {event['time']}",
                    'resume_at': event_time + timedelta(minutes=30)
                }
                
        return {'avoid': False}
```

### 9. Earnings Calendar Integration

```python
# data/earnings_calendar.py

class EarningsCalendar:
    """
    Track earnings dates - huge volatility risk.
    """
    
    def __init__(self, api_client):
        self.api = api_client
        
    def get_earnings_dates(self, symbols: list) -> dict:
        """Get next earnings date for each symbol"""
        earnings = {}
        
        for symbol in symbols:
            try:
                data = self.api.get_earnings_calendar(symbol)
                if data:
                    earnings[symbol] = {
                        'date': data['date'],
                        'time': data['time'],  # 'BMO' (before market) or 'AMC' (after close)
                        'estimate': data.get('eps_estimate'),
                        'days_until': (data['date'] - datetime.now().date()).days
                    }
            except:
                pass
                
        return earnings
    
    def check_earnings_risk(self, symbol: str) -> dict:
        """
        Check if symbol has earnings soon.
        Risky to hold through earnings without planning for it.
        """
        earnings = self.get_earnings_dates([symbol])
        
        if symbol not in earnings:
            return {'risk': 'unknown', 'message': 'Earnings date not found'}
            
        days_until = earnings[symbol]['days_until']
        
        if days_until <= 0:
            return {
                'risk': 'high',
                'message': f"Earnings TODAY ({earnings[symbol]['time']})",
                'recommendation': 'Consider closing position or accepting volatility'
            }
        elif days_until <= 3:
            return {
                'risk': 'medium',
                'message': f"Earnings in {days_until} days",
                'recommendation': 'Set wider stops or reduce position size'
            }
        elif days_until <= 7:
            return {
                'risk': 'low',
                'message': f"Earnings in {days_until} days",
                'recommendation': 'Monitor closely'
            }
        else:
            return {'risk': 'none', 'days_until': days_until}
```

### 10. Performance Report Generator

```python
# reports/report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ReportGenerator:
    """
    Generate professional PDF performance reports.
    """
    
    def __init__(self, learning_db):
        self.db = learning_db
        
    def generate_weekly_report(self, week_start: datetime) -> str:
        """Generate weekly performance PDF"""
        
        # Gather data
        trades = self.db.get_trades_in_range(week_start, week_start + timedelta(days=7))
        metrics = self._calculate_metrics(trades)
        
        # Create PDF
        filename = f"leviathan_report_{week_start.strftime('%Y%m%d')}.pdf"
        filepath = f"reports/{filename}"
        
        c = canvas.Canvas(filepath, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 750, "LEVIATHAN")
        c.setFont("Helvetica", 14)
        c.drawString(50, 730, f"Weekly Performance Report")
        c.drawString(50, 710, f"Week of {week_start.strftime('%B %d, %Y')}")
        
        # Summary metrics
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 670, "Summary")
        
        c.setFont("Helvetica", 12)
        y = 650
        summaries = [
            f"Starting Balance: ${metrics['starting_balance']:.2f}",
            f"Ending Balance: ${metrics['ending_balance']:.2f}",
            f"Week P&L: ${metrics['week_pnl']:.2f} ({metrics['week_pnl_pct']:.1%})",
            f"Total Trades: {metrics['total_trades']}",
            f"Win Rate: {metrics['win_rate']:.0%}",
            f"Profit Factor: {metrics['profit_factor']:.2f}",
            f"Sharpe Ratio: {metrics['sharpe']:.2f}",
            f"Max Drawdown: {metrics['max_drawdown']:.1%}",
        ]
        
        for line in summaries:
            c.drawString(50, y, line)
            y -= 20
            
        # Trade log
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y - 20, "Trade Log")
        
        y -= 50
        c.setFont("Helvetica", 10)
        
        for trade in trades[:20]:  # First 20 trades
            line = f"{trade['symbol']:6} | {trade['side']:4} | ${trade['profit_loss']:+.2f} | {trade['reasoning'][:40]}..."
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = 750
                
        c.save()
        return filepath
    
    def generate_tax_report(self, year: int) -> str:
        """Generate tax-ready report with all trades"""
        trades = self.db.get_trades_in_year(year)
        
        # Create detailed CSV for tax software
        csv_path = f"reports/leviathan_trades_{year}.csv"
        
        with open(csv_path, 'w') as f:
            f.write("Date,Symbol,Side,Quantity,Price,Proceeds,Cost Basis,Gain/Loss,Wash Sale,Term\n")
            
            for trade in trades:
                term = 'Short' if trade['hold_days'] < 365 else 'Long'
                f.write(f"{trade['date']},{trade['symbol']},{trade['side']},{trade['quantity']},"
                       f"{trade['price']},{trade['proceeds']},{trade['cost_basis']},"
                       f"{trade['gain_loss']},{trade.get('wash_sale', 'No')},{term}\n")
                       
        return csv_path
```

### 11. Backup & Recovery System

```python
# core/backup_manager.py
import shutil
import zipfile
from datetime import datetime

class BackupManager:
    """
    Automatic backup of all critical data.
    """
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self) -> str:
        """Create full backup of all databases and config"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"leviathan_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Databases
            zipf.write("leviathan_learning.db")
            zipf.write("leviathan_state.db")
            
            # Config (not credentials)
            zipf.write("config/settings.py")
            
            # Models
            for model_file in Path("models/saved").glob("*.pt"):
                zipf.write(model_file)
                
            # Logs
            for log_file in Path("logs").glob("*.log"):
                zipf.write(log_file)
                
        # Keep only last 30 backups
        self._cleanup_old_backups(keep=30)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str):
        """Restore from a backup file"""
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(".")
            
    def schedule_backups(self):
        """Schedule automatic daily backups"""
        import schedule
        schedule.every().day.at("03:00").do(self.create_backup)
        
    def _cleanup_old_backups(self, keep: int = 30):
        """Remove old backups, keeping only recent ones"""
        backups = sorted(self.backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        
        for old_backup in backups[:-keep]:
            old_backup.unlink()
```

### 12. Watchlist Management

```python
# strategy/watchlist.py

class WatchlistManager:
    """
    Manage symbol watchlists for scanning.
    """
    
    def __init__(self, state_db):
        self.db = state_db
        
    def create_watchlist(self, name: str, symbols: list, criteria: dict = None):
        """Create a new watchlist"""
        self.db.save_watchlist({
            'name': name,
            'symbols': symbols,
            'criteria': criteria or {},
            'created_at': datetime.now()
        })
        
    def get_watchlist(self, name: str) -> list:
        """Get symbols in a watchlist"""
        return self.db.get_watchlist(name)
        
    def auto_generate_watchlist(self, criteria: dict) -> list:
        """
        Auto-generate watchlist based on criteria.
        Example: top volume, top gainers, sector rotation, etc.
        """
        symbols = []
        
        if criteria.get('type') == 'top_volume':
            symbols = self._get_top_volume(criteria.get('limit', 50))
        elif criteria.get('type') == 'top_gainers':
            symbols = self._get_top_gainers(criteria.get('limit', 20))
        elif criteria.get('type') == 'sector':
            symbols = self._get_sector_symbols(criteria.get('sector'))
        elif criteria.get('type') == 'sp500':
            symbols = self._get_sp500_symbols()
            
        return symbols
    
    # Default watchlists
    DEFAULT_WATCHLISTS = {
        'mega_caps': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B'],
        'tech_leaders': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'CRM', 'ADBE', 'INTC'],
        'high_beta': ['TSLA', 'NVDA', 'AMD', 'COIN', 'MARA', 'RIOT', 'SOFI'],
        'dividend_kings': ['JNJ', 'PG', 'KO', 'PEP', 'MMM', 'EMR', 'GPC', 'ITW'],
        'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLE', 'XLK', 'ARKK'],
    }
```

### 13. Slippage Estimator

```python
# execution/slippage_estimator.py

class SlippageEstimator:
    """
    Estimate likely slippage before executing trades.
    Adjust position sizes for illiquid symbols.
    """
    
    def estimate_slippage(self, symbol: str, quantity: float, 
                         side: str, market_data: dict) -> dict:
        """
        Estimate slippage based on:
        - Bid-ask spread
        - Order size vs average volume
        - Current volatility
        """
        spread = market_data['ask'] - market_data['bid']
        spread_pct = spread / market_data['mid']
        
        avg_volume = market_data['avg_volume']
        order_pct_of_volume = (quantity * market_data['price']) / (avg_volume * market_data['price'])
        
        # Base slippage is half the spread
        base_slippage = spread_pct / 2
        
        # Add impact for large orders
        if order_pct_of_volume > 0.01:  # More than 1% of daily volume
            impact_slippage = order_pct_of_volume * 0.1  # 10% of order size in extra slippage
        else:
            impact_slippage = 0
            
        # Add volatility component
        volatility_slippage = market_data.get('current_volatility', 0.02) * 0.1
        
        total_slippage = base_slippage + impact_slippage + volatility_slippage
        
        return {
            'estimated_slippage_pct': total_slippage,
            'estimated_slippage_dollars': total_slippage * quantity * market_data['price'],
            'spread_pct': spread_pct,
            'order_vs_volume': order_pct_of_volume,
            'recommendation': self._get_recommendation(total_slippage, spread_pct)
        }
    
    def _get_recommendation(self, slippage: float, spread: float) -> str:
        if slippage > 0.02:  # More than 2%
            return "HIGH_SLIPPAGE: Consider smaller position or limit order"
        elif slippage > 0.01:
            return "MODERATE_SLIPPAGE: Use limit order recommended"
        elif spread > 0.005:
            return "WIDE_SPREAD: Use limit order at mid price"
        else:
            return "LOW_SLIPPAGE: Market order acceptable"
```

### 14. Long-Term Portfolio Autopilot (AI-Managed Holdings)

**PURPOSE:** Automatically manage a long-term investment portfolio. The AI diversifies holdings, detects when positions turn bearish, auto-rotates into stronger stocks, and keeps the portfolio healthy without manual intervention.

**This is DIFFERENT from swing trading:**
- Swing trading = short-term (2-5 days), active trading, frequent moves
- Portfolio Autopilot = long-term (weeks to months), defensive, buy-and-hold with smart rotation

```python
# portfolio/autopilot.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class PortfolioAutopilot:
    """
    AI-managed long-term portfolio that automatically:
    1. Diversifies across sectors and asset classes
    2. Detects bearish signals on holdings
    3. Rotates out of weak positions into stronger ones
    4. Maintains target allocations
    5. Rebalances periodically
    
    Think of this as an AI financial advisor managing your investments 24/7.
    """
    
    def __init__(self, alpaca_client, opus_brain, learning_db, 
                 risk_tolerance: str = 'moderate'):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        self.db = learning_db
        self.risk_tolerance = risk_tolerance  # 'conservative', 'moderate', 'aggressive'
        
        # Configure based on risk tolerance
        self.config = self._get_risk_config(risk_tolerance)
        
    def _get_risk_config(self, tolerance: str) -> dict:
        """Configuration based on risk tolerance"""
        configs = {
            'conservative': {
                'max_single_position': 0.10,      # Max 10% in one stock
                'min_positions': 10,               # At least 10 positions
                'max_sector_exposure': 0.25,       # Max 25% in one sector
                'cash_buffer': 0.10,               # Keep 10% cash
                'rebalance_threshold': 0.05,       # Rebalance if 5% off target
                'bearish_sensitivity': 'high',     # Quick to detect problems
                'preferred_assets': ['SPY', 'QQQ', 'BND', 'dividend_stocks'],
                'volatility_cap': 0.25,            # Avoid stocks with >25% annual vol
            },
            'moderate': {
                'max_single_position': 0.15,
                'min_positions': 8,
                'max_sector_exposure': 0.30,
                'cash_buffer': 0.05,
                'rebalance_threshold': 0.07,
                'bearish_sensitivity': 'medium',
                'preferred_assets': ['growth', 'value', 'etfs'],
                'volatility_cap': 0.40,
            },
            'aggressive': {
                'max_single_position': 0.20,
                'min_positions': 5,
                'max_sector_exposure': 0.40,
                'cash_buffer': 0.02,
                'rebalance_threshold': 0.10,
                'bearish_sensitivity': 'low',
                'preferred_assets': ['growth', 'momentum', 'crypto'],
                'volatility_cap': 0.60,
            }
        }
        return configs.get(tolerance, configs['moderate'])
    
    def analyze_portfolio_health(self) -> dict:
        """
        Comprehensive health check of current portfolio.
        Called daily by Opus to assess if any action needed.
        """
        positions = self.alpaca.get_all_positions()
        account = self.alpaca.get_account()
        
        if not positions:
            return {
                'status': 'empty',
                'action_needed': True,
                'recommendation': 'Portfolio is empty. Consider initial diversification.'
            }
        
        # Analyze each position
        position_analysis = []
        total_value = float(account.portfolio_value)
        
        for pos in positions:
            analysis = self._analyze_single_position(pos)
            position_analysis.append(analysis)
        
        # Calculate portfolio metrics
        sector_exposure = self._calculate_sector_exposure(positions)
        correlation_matrix = self._calculate_correlations(positions)
        overall_health = self._calculate_portfolio_health_score(position_analysis)
        
        # Find problematic positions
        bearish_positions = [p for p in position_analysis if p['signal'] == 'BEARISH']
        weak_positions = [p for p in position_analysis if p['signal'] == 'WEAK']
        strong_positions = [p for p in position_analysis if p['signal'] == 'STRONG']
        
        # Determine if action needed
        action_needed = (
            len(bearish_positions) > 0 or
            any(exp > self.config['max_sector_exposure'] for exp in sector_exposure.values()) or
            overall_health < 0.6
        )
        
        return {
            'status': 'analyzed',
            'total_value': total_value,
            'positions_count': len(positions),
            'position_analysis': position_analysis,
            'sector_exposure': sector_exposure,
            'correlation_risk': self._assess_correlation_risk(correlation_matrix),
            'overall_health_score': overall_health,
            'bearish_positions': bearish_positions,
            'weak_positions': weak_positions,
            'strong_positions': strong_positions,
            'action_needed': action_needed,
            'recommended_actions': self._generate_recommendations(
                position_analysis, sector_exposure, overall_health
            )
        }
    
    def _analyze_single_position(self, position: dict) -> dict:
        """
        Analyze a single position for bearish/bullish signals.
        Uses multiple timeframes and indicators.
        """
        symbol = position['symbol']
        
        # Get historical data
        daily_data = self.alpaca.get_historical_bars(symbol, timeframe='1D', limit=200)
        weekly_data = self.alpaca.get_historical_bars(symbol, timeframe='1W', limit=52)
        
        # Calculate indicators
        current_price = float(position['current_price'])
        entry_price = float(position['avg_entry_price'])
        unrealized_pnl_pct = float(position['unrealized_plpc'])
        
        # Moving averages
        sma_50 = daily_data['close'].rolling(50).mean().iloc[-1]
        sma_200 = daily_data['close'].rolling(200).mean().iloc[-1]
        ema_21 = daily_data['close'].ewm(span=21).mean().iloc[-1]
        
        # Trend analysis
        price_vs_sma50 = (current_price - sma_50) / sma_50
        price_vs_sma200 = (current_price - sma_200) / sma_200
        sma50_vs_sma200 = (sma_50 - sma_200) / sma_200  # Golden/Death cross
        
        # Momentum indicators
        rsi = self._calculate_rsi(daily_data['close'], 14)
        macd, signal, histogram = self._calculate_macd(daily_data['close'])
        
        # Volatility
        atr = self._calculate_atr(daily_data, 14)
        volatility = daily_data['close'].pct_change().std() * np.sqrt(252)
        
        # Volume analysis
        volume_trend = daily_data['volume'].iloc[-5:].mean() / daily_data['volume'].iloc[-20:].mean()
        
        # Weekly trend (longer-term confirmation)
        weekly_sma_10 = weekly_data['close'].rolling(10).mean().iloc[-1]
        weekly_trend = 'up' if current_price > weekly_sma_10 else 'down'
        
        # Determine signal
        bearish_signals = 0
        bullish_signals = 0
        
        # Check bearish conditions
        if current_price < sma_50:
            bearish_signals += 1
        if current_price < sma_200:
            bearish_signals += 2  # Weighted more heavily
        if sma_50 < sma_200:  # Death cross
            bearish_signals += 2
        if rsi < 40:
            bearish_signals += 1
        if histogram < 0 and histogram < self._calculate_macd(daily_data['close'].iloc[:-1])[2]:
            bearish_signals += 1  # MACD histogram declining
        if weekly_trend == 'down':
            bearish_signals += 2
        if unrealized_pnl_pct < -0.15:  # Down more than 15%
            bearish_signals += 1
            
        # Check bullish conditions
        if current_price > sma_50:
            bullish_signals += 1
        if current_price > sma_200:
            bullish_signals += 2
        if sma_50 > sma_200:  # Golden cross
            bullish_signals += 2
        if rsi > 50:
            bullish_signals += 1
        if histogram > 0:
            bullish_signals += 1
        if weekly_trend == 'up':
            bullish_signals += 2
        if unrealized_pnl_pct > 0.10:  # Up more than 10%
            bullish_signals += 1
        
        # Determine overall signal
        signal_score = bullish_signals - bearish_signals
        
        if signal_score <= -4:
            signal = 'BEARISH'
            action = 'SELL'
        elif signal_score <= -2:
            signal = 'WEAK'
            action = 'REDUCE'
        elif signal_score >= 4:
            signal = 'STRONG'
            action = 'HOLD_OR_ADD'
        elif signal_score >= 2:
            signal = 'BULLISH'
            action = 'HOLD'
        else:
            signal = 'NEUTRAL'
            action = 'HOLD'
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'entry_price': entry_price,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'market_value': float(position['market_value']),
            'signal': signal,
            'signal_score': signal_score,
            'recommended_action': action,
            'indicators': {
                'price_vs_sma50': price_vs_sma50,
                'price_vs_sma200': price_vs_sma200,
                'sma50_vs_sma200': sma50_vs_sma200,
                'rsi': rsi,
                'macd_histogram': histogram,
                'volatility': volatility,
                'volume_trend': volume_trend,
                'weekly_trend': weekly_trend
            },
            'bearish_signals': bearish_signals,
            'bullish_signals': bullish_signals
        }
    
    def find_replacement_candidates(self, selling_symbol: str, 
                                    amount_to_invest: float) -> list:
        """
        Find strong stocks to rotate into when selling a weak position.
        Considers sector diversification, momentum, and fundamentals.
        """
        current_positions = [p['symbol'] for p in self.alpaca.get_all_positions()]
        current_sectors = self._get_position_sectors(current_positions)
        
        # Get universe of potential stocks
        candidates = self._get_stock_universe()
        
        scored_candidates = []
        
        for symbol in candidates:
            if symbol in current_positions:
                continue  # Skip stocks we already own
                
            try:
                # Get data and analyze
                data = self.alpaca.get_historical_bars(symbol, timeframe='1D', limit=100)
                
                # Calculate momentum score
                momentum = self._calculate_momentum_score(data)
                
                # Calculate trend score
                trend = self._calculate_trend_score(data)
                
                # Check sector (favor diversification)
                sector = self._get_sector(symbol)
                sector_bonus = 0.1 if sector not in current_sectors else 0
                
                # Volatility check
                vol = data['close'].pct_change().std() * np.sqrt(252)
                if vol > self.config['volatility_cap']:
                    continue  # Skip too volatile
                
                # Combine scores
                total_score = (momentum * 0.4) + (trend * 0.4) + sector_bonus + (0.2 * (1 - vol))
                
                scored_candidates.append({
                    'symbol': symbol,
                    'score': total_score,
                    'momentum': momentum,
                    'trend': trend,
                    'sector': sector,
                    'volatility': vol,
                    'current_price': data['close'].iloc[-1]
                })
                
            except Exception as e:
                continue  # Skip if data unavailable
        
        # Sort by score and return top candidates
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates[:10]
    
    def execute_rotation(self, sell_symbol: str, buy_symbol: str, 
                        reason: str) -> dict:
        """
        Execute a rotation: sell weak position, buy strong replacement.
        Opus oversees the entire process.
        """
        # Get current position info
        position = self.alpaca.get_position(sell_symbol)
        sell_qty = float(position['qty'])
        sell_value = float(position['market_value'])
        
        # Ask Opus to approve the rotation
        approval = self.opus.approve_rotation(
            sell_symbol=sell_symbol,
            buy_symbol=buy_symbol,
            sell_value=sell_value,
            reason=reason
        )
        
        if not approval['approved']:
            return {
                'status': 'rejected',
                'reason': approval['reason']
            }
        
        # Execute sell
        sell_order = self.alpaca.submit_order(
            symbol=sell_symbol,
            qty=sell_qty,
            side='sell',
            type='market',
            time_in_force='day'
        )
        
        # Wait for sell to fill
        filled_sell = self._wait_for_fill(sell_order.id)
        proceeds = float(filled_sell.filled_qty) * float(filled_sell.filled_avg_price)
        
        # Execute buy with proceeds (minus small buffer for price movement)
        buy_amount = proceeds * 0.99
        
        buy_order = self.alpaca.submit_order(
            symbol=buy_symbol,
            notional=buy_amount,
            side='buy',
            type='market',
            time_in_force='day'
        )
        
        filled_buy = self._wait_for_fill(buy_order.id)
        
        # Log the rotation
        self.db.log_rotation({
            'timestamp': datetime.now(),
            'sold_symbol': sell_symbol,
            'sold_qty': sell_qty,
            'sold_price': float(filled_sell.filled_avg_price),
            'bought_symbol': buy_symbol,
            'bought_qty': float(filled_buy.filled_qty),
            'bought_price': float(filled_buy.filled_avg_price),
            'reason': reason,
            'opus_reasoning': approval.get('reasoning', '')
        })
        
        return {
            'status': 'completed',
            'sold': {
                'symbol': sell_symbol,
                'qty': sell_qty,
                'price': float(filled_sell.filled_avg_price),
                'proceeds': proceeds
            },
            'bought': {
                'symbol': buy_symbol,
                'qty': float(filled_buy.filled_qty),
                'price': float(filled_buy.filled_avg_price),
                'cost': buy_amount
            },
            'reason': reason
        }
    
    def auto_diversify(self, total_investment: float, 
                      strategy: str = 'balanced') -> dict:
        """
        Automatically build a diversified portfolio from scratch or 
        additional capital.
        
        Strategies:
        - 'balanced': Mix of growth, value, dividend, bonds
        - 'growth': Focus on growth stocks and tech
        - 'income': Focus on dividends and bonds
        - 'all_weather': Ray Dalio style all-weather portfolio
        """
        allocations = self._get_diversification_template(strategy)
        
        orders = []
        for asset_class, allocation in allocations.items():
            amount = total_investment * allocation['percentage']
            symbols = allocation['symbols']
            
            # Distribute evenly within asset class
            per_symbol = amount / len(symbols)
            
            for symbol in symbols:
                if per_symbol < 1:  # Minimum $1 order
                    continue
                    
                order = self.alpaca.submit_order(
                    symbol=symbol,
                    notional=per_symbol,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
                orders.append({
                    'symbol': symbol,
                    'asset_class': asset_class,
                    'amount': per_symbol,
                    'order_id': order.id
                })
        
        return {
            'status': 'submitted',
            'strategy': strategy,
            'total_invested': total_investment,
            'orders': orders,
            'allocation_used': allocations
        }
    
    def _get_diversification_template(self, strategy: str) -> dict:
        """Pre-built diversification templates"""
        templates = {
            'balanced': {
                'us_large_cap': {
                    'percentage': 0.30,
                    'symbols': ['SPY', 'VOO']  # S&P 500
                },
                'us_growth': {
                    'percentage': 0.15,
                    'symbols': ['QQQ', 'VGT']  # Nasdaq/Tech
                },
                'us_value': {
                    'percentage': 0.10,
                    'symbols': ['VTV', 'SCHV']  # Value stocks
                },
                'international': {
                    'percentage': 0.15,
                    'symbols': ['VXUS', 'EFA']  # International
                },
                'bonds': {
                    'percentage': 0.15,
                    'symbols': ['BND', 'AGG']  # Bonds
                },
                'alternatives': {
                    'percentage': 0.10,
                    'symbols': ['GLD', 'VNQ']  # Gold, REITs
                },
                'cash': {
                    'percentage': 0.05,
                    'symbols': ['SHV']  # Short-term treasuries
                }
            },
            'growth': {
                'us_large_cap_growth': {
                    'percentage': 0.35,
                    'symbols': ['QQQ', 'VUG', 'MGK']
                },
                'tech_focused': {
                    'percentage': 0.25,
                    'symbols': ['VGT', 'XLK', 'ARKK']
                },
                'us_mid_cap_growth': {
                    'percentage': 0.15,
                    'symbols': ['IJH', 'VO']
                },
                'international_growth': {
                    'percentage': 0.15,
                    'symbols': ['EFG', 'VIGI']
                },
                'speculative': {
                    'percentage': 0.10,
                    'symbols': ['ARKK', 'ARKG']
                }
            },
            'income': {
                'dividend_stocks': {
                    'percentage': 0.30,
                    'symbols': ['VYM', 'SCHD', 'HDV']
                },
                'bonds': {
                    'percentage': 0.30,
                    'symbols': ['BND', 'AGG', 'LQD']
                },
                'reits': {
                    'percentage': 0.15,
                    'symbols': ['VNQ', 'SCHH']
                },
                'preferred_stocks': {
                    'percentage': 0.10,
                    'symbols': ['PFF', 'PFFD']
                },
                'high_yield': {
                    'percentage': 0.10,
                    'symbols': ['HYG', 'JNK']
                },
                'treasury': {
                    'percentage': 0.05,
                    'symbols': ['TLT', 'IEF']
                }
            },
            'all_weather': {
                # Ray Dalio's All Weather Portfolio
                'stocks': {
                    'percentage': 0.30,
                    'symbols': ['VTI', 'SPY']
                },
                'long_term_bonds': {
                    'percentage': 0.40,
                    'symbols': ['TLT', 'VGLT']
                },
                'intermediate_bonds': {
                    'percentage': 0.15,
                    'symbols': ['IEF', 'VGIT']
                },
                'gold': {
                    'percentage': 0.075,
                    'symbols': ['GLD', 'IAU']
                },
                'commodities': {
                    'percentage': 0.075,
                    'symbols': ['DBC', 'PDBC']
                }
            }
        }
        return templates.get(strategy, templates['balanced'])
    
    def run_daily_checkup(self) -> dict:
        """
        Daily portfolio health check. Called automatically.
        Opus analyzes and decides if any rotations needed.
        """
        # Analyze current portfolio
        health = self.analyze_portfolio_health()
        
        if not health['action_needed']:
            return {
                'status': 'healthy',
                'health_score': health['overall_health_score'],
                'message': 'Portfolio looks good. No action needed.',
                'positions_checked': health['positions_count']
            }
        
        # Ask Opus to decide what to do
        opus_decision = self.opus.analyze_portfolio_and_decide(
            portfolio_health=health,
            risk_tolerance=self.risk_tolerance,
            config=self.config
        )
        
        actions_taken = []
        
        # Execute Opus decisions
        for action in opus_decision.get('actions', []):
            if action['type'] == 'ROTATE':
                result = self.execute_rotation(
                    sell_symbol=action['sell'],
                    buy_symbol=action['buy'],
                    reason=action['reason']
                )
                actions_taken.append(result)
                
            elif action['type'] == 'REDUCE':
                result = self._reduce_position(
                    symbol=action['symbol'],
                    reduce_pct=action['reduce_pct'],
                    reason=action['reason']
                )
                actions_taken.append(result)
                
            elif action['type'] == 'REBALANCE':
                result = self._rebalance_to_targets(action['targets'])
                actions_taken.append(result)
        
        return {
            'status': 'actions_taken',
            'health_score': health['overall_health_score'],
            'bearish_positions': [p['symbol'] for p in health['bearish_positions']],
            'opus_decision': opus_decision,
            'actions_taken': actions_taken
        }
    
    def _calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """Calculate momentum score (0-1)"""
        returns_1m = (data['close'].iloc[-1] / data['close'].iloc[-21]) - 1
        returns_3m = (data['close'].iloc[-1] / data['close'].iloc[-63]) - 1 if len(data) > 63 else returns_1m
        
        # Normalize to 0-1 range
        score = (returns_1m * 0.6 + returns_3m * 0.4 + 0.3) / 0.6  # Assuming max 30% return
        return max(0, min(1, score))
    
    def _calculate_trend_score(self, data: pd.DataFrame) -> float:
        """Calculate trend score based on moving averages"""
        close = data['close'].iloc[-1]
        sma_20 = data['close'].rolling(20).mean().iloc[-1]
        sma_50 = data['close'].rolling(50).mean().iloc[-1]
        
        score = 0.5  # Neutral baseline
        
        if close > sma_20:
            score += 0.2
        if close > sma_50:
            score += 0.2
        if sma_20 > sma_50:
            score += 0.1
            
        return score
    
    def _get_stock_universe(self) -> list:
        """Get universe of stocks to consider for rotation"""
        # Combination of major indices and ETFs
        return [
            # Large cap leaders
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
            'JPM', 'V', 'JNJ', 'UNH', 'HD', 'PG', 'MA', 'DIS', 'ADBE', 'CRM',
            # Growth
            'AMD', 'NFLX', 'PYPL', 'SQ', 'SHOP', 'SNOW', 'DDOG', 'NET',
            # Value/Dividend
            'KO', 'PEP', 'WMT', 'MCD', 'ABBV', 'MRK', 'PFE', 'XOM', 'CVX',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VGT', 'XLF', 'XLE',
            'XLK', 'XLV', 'XLY', 'XLP', 'VYM', 'SCHD', 'BND', 'TLT', 'GLD'
        ]


class OpusPortfolioAdvisor:
    """
    Opus-powered portfolio decision making.
    Acts as an AI financial advisor for long-term holdings.
    """
    
    def __init__(self, opus_brain):
        self.opus = opus_brain
        
    def analyze_portfolio_and_decide(self, portfolio_health: dict,
                                     risk_tolerance: str,
                                     config: dict) -> dict:
        """
        Opus analyzes the portfolio and decides what actions to take.
        """
        prompt = f"""You are an AI portfolio manager. Analyze this portfolio and decide what actions to take.

PORTFOLIO HEALTH REPORT:
========================
Overall Health Score: {portfolio_health['overall_health_score']:.2f}/1.0
Total Value: ${portfolio_health['total_value']:.2f}
Number of Positions: {portfolio_health['positions_count']}

BEARISH POSITIONS (consider selling):
{self._format_positions(portfolio_health['bearish_positions'])}

WEAK POSITIONS (consider reducing):
{self._format_positions(portfolio_health['weak_positions'])}

STRONG POSITIONS (consider holding/adding):
{self._format_positions(portfolio_health['strong_positions'])}

SECTOR EXPOSURE:
{portfolio_health['sector_exposure']}

CORRELATION RISK: {portfolio_health['correlation_risk']}

INVESTOR PROFILE:
Risk Tolerance: {risk_tolerance}
Max Single Position: {config['max_single_position']:.0%}
Max Sector Exposure: {config['max_sector_exposure']:.0%}

INSTRUCTIONS:
1. For BEARISH positions, recommend rotating into stronger alternatives
2. For WEAK positions, recommend reducing size
3. Check for over-concentration in any sector
4. Ensure adequate diversification
5. Be conservative - only recommend action if clearly beneficial

Respond with JSON:
{{
    "analysis": "Your overall assessment",
    "actions": [
        {{
            "type": "ROTATE" | "REDUCE" | "REBALANCE" | "NONE",
            "symbol": "ticker if applicable",
            "sell": "ticker to sell (for ROTATE)",
            "buy": "ticker to buy (for ROTATE)",
            "reduce_pct": 0.5 (for REDUCE, e.g., sell 50%),
            "reason": "explanation",
            "urgency": "high" | "medium" | "low"
        }}
    ],
    "overall_recommendation": "Summary of what to do",
    "confidence": 0.0-1.0
}}

If portfolio is healthy, return empty actions array."""

        response = self.opus.client.messages.create(
            model=self.opus.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_decision(response.content[0].text)
    
    def approve_rotation(self, sell_symbol: str, buy_symbol: str,
                        sell_value: float, reason: str) -> dict:
        """Opus approves or rejects a proposed rotation"""
        prompt = f"""ROTATION APPROVAL REQUEST

Proposed Action: Sell {sell_symbol}, Buy {buy_symbol}
Value: ${sell_value:.2f}
Reason: {reason}

Should this rotation be approved?

Consider:
1. Is the sell signal valid?
2. Is the buy candidate strong?
3. Are there tax implications?
4. Is now a good time to execute?

Respond with JSON:
{{
    "approved": true | false,
    "reasoning": "Your reasoning",
    "modifications": "Any suggested modifications" | null
}}"""

        response = self.opus.client.messages.create(
            model=self.opus.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_decision(response.content[0].text)
    
    def _format_positions(self, positions: list) -> str:
        if not positions:
            return "None"
        return "\n".join([
            f"  - {p['symbol']}: {p['unrealized_pnl_pct']:.1%} P&L, Signal Score: {p['signal_score']}"
            for p in positions
        ])
    
    def _parse_decision(self, response_text: str) -> dict:
        try:
            import json
            clean = response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except:
            return {"approved": False, "reasoning": "Failed to parse response", "actions": []}
```

### GUI Integration for Portfolio Autopilot (PyWebView + HTML)

The Portfolio Autopilot window uses the same PyWebView + HTML/CSS/JavaScript approach as the main dashboard.

**File: frontend/autopilot.html**

```html
<!-- frontend/autopilot.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Portfolio Autopilot - LEVIATHAN</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'bg-primary': '#0a0a0f',
                        'bg-secondary': '#12121a',
                        'bg-tertiary': '#1a1a24',
                        'accent-purple': '#8b5cf6',
                        'border-color': '#2d2d3a',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-bg-primary text-white font-inter p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
        <div>
            <h1 class="text-2xl font-bold">🤖 Portfolio Autopilot</h1>
            <p class="text-gray-500 text-sm">Automated portfolio management</p>
        </div>
        <div id="health-score" class="px-4 py-2 rounded-xl bg-bg-secondary border border-border-color">
            <span class="text-gray-400 text-sm">Health Score:</span>
            <span id="health-value" class="text-xl font-bold ml-2">--</span>
        </div>
    </div>
    
    <!-- Status Card -->
    <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color mb-6">
        <h3 class="text-lg font-semibold mb-4">Autopilot Status</h3>
        <div class="flex items-center gap-4">
            <div id="status-indicator" class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-gray-500"></span>
                <span class="text-gray-400">Disabled</span>
            </div>
            <label class="flex items-center gap-2 cursor-pointer ml-auto">
                <input type="checkbox" id="autopilot-toggle" class="sr-only" onchange="toggleAutopilot()">
                <div class="w-11 h-6 bg-bg-tertiary rounded-full relative">
                    <div class="toggle-dot absolute left-1 top-1 w-4 h-4 bg-gray-500 rounded-full transition-all"></div>
                </div>
                <span class="text-sm">Enable Daily Auto-Checkup</span>
            </label>
        </div>
    </div>
    
    <!-- Risk Tolerance -->
    <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color mb-6">
        <h3 class="text-lg font-semibold mb-4">Risk Tolerance</h3>
        <div class="flex gap-4">
            <button onclick="setRiskTolerance('conservative')" id="risk-conservative" 
                    class="risk-btn flex-1 py-3 rounded-xl bg-bg-tertiary hover:bg-accent-purple/20 transition-colors">
                <span class="block text-lg">🛡️</span>
                <span class="text-sm">Conservative</span>
            </button>
            <button onclick="setRiskTolerance('moderate')" id="risk-moderate"
                    class="risk-btn flex-1 py-3 rounded-xl bg-accent-purple/20 border border-accent-purple transition-colors">
                <span class="block text-lg">⚖️</span>
                <span class="text-sm">Moderate</span>
            </button>
            <button onclick="setRiskTolerance('aggressive')" id="risk-aggressive"
                    class="risk-btn flex-1 py-3 rounded-xl bg-bg-tertiary hover:bg-accent-purple/20 transition-colors">
                <span class="block text-lg">🚀</span>
                <span class="text-sm">Aggressive</span>
            </button>
        </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="grid grid-cols-3 gap-4 mb-6">
        <button onclick="analyzePortfolio()" class="py-4 rounded-xl bg-accent-purple hover:bg-accent-purple-hover text-white font-semibold transition-colors">
            🔍 Analyze Portfolio
        </button>
        <button onclick="runCheckup()" class="py-4 rounded-xl bg-bg-secondary border border-border-color hover:border-accent-purple text-white font-semibold transition-colors">
            🔄 Run Checkup Now
        </button>
        <button onclick="openDiversifyDialog()" class="py-4 rounded-xl bg-bg-secondary border border-border-color hover:border-accent-purple text-white font-semibold transition-colors">
            📊 Auto-Diversify
        </button>
    </div>
    
    <!-- Holdings Table -->
    <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color mb-6">
        <h3 class="text-lg font-semibold mb-4">Current Holdings</h3>
        <div id="holdings-table" class="space-y-2 max-h-64 overflow-y-auto">
            <div class="text-gray-500 text-center py-4">Loading holdings...</div>
        </div>
    </div>
    
    <!-- Recent Actions Log -->
    <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color">
        <h3 class="text-lg font-semibold mb-4">Recent Actions</h3>
        <div id="actions-log" class="space-y-2 max-h-32 overflow-y-auto">
            <div class="text-gray-500 text-center py-4">No recent actions</div>
        </div>
    </div>
    
    <script>
        let currentRisk = 'moderate';
        
        async function callPython(method, ...args) {
            const result = await window.pywebview.api[method](...args);
            return typeof result === 'string' ? JSON.parse(result) : result;
        }
        
        function setRiskTolerance(level) {
            currentRisk = level;
            document.querySelectorAll('.risk-btn').forEach(btn => {
                btn.classList.remove('bg-accent-purple/20', 'border', 'border-accent-purple');
                btn.classList.add('bg-bg-tertiary');
            });
            document.getElementById(`risk-${level}`).classList.remove('bg-bg-tertiary');
            document.getElementById(`risk-${level}`).classList.add('bg-accent-purple/20', 'border', 'border-accent-purple');
            callPython('set_risk_tolerance', level);
        }
        
        async function analyzePortfolio() {
            const data = await callPython('analyze_portfolio');
            if (data) {
                document.getElementById('health-value').textContent = `${(data.overall_health_score * 100).toFixed(0)}%`;
                updateHoldingsTable(data.position_analysis);
            }
        }
        
        async function runCheckup() {
            const result = await callPython('run_checkup');
            addActionLog(`Checkup completed: ${result.status}`);
            if (result.actions_taken) {
                result.actions_taken.forEach(action => addActionLog(`  → ${action}`));
            }
        }
        
        function updateHoldingsTable(positions) {
            const container = document.getElementById('holdings-table');
            if (!positions || positions.length === 0) {
                container.innerHTML = '<div class="text-gray-500 text-center py-4">No holdings</div>';
                return;
            }
            
            const signalColors = {
                'BEARISH': 'text-red-500', 'WEAK': 'text-orange-500',
                'NEUTRAL': 'text-gray-400', 'BULLISH': 'text-green-500', 'STRONG': 'text-green-400'
            };
            
            container.innerHTML = positions.map(p => `
                <div class="flex items-center justify-between p-3 rounded-xl bg-bg-tertiary">
                    <div class="flex items-center gap-3">
                        <span class="font-medium">${p.symbol}</span>
                        <span class="${signalColors[p.signal] || 'text-gray-400'}">${p.signal}</span>
                    </div>
                    <div class="text-right">
                        <span class="${p.unrealized_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}">
                            ${(p.unrealized_pnl_pct * 100).toFixed(1)}%
                        </span>
                        <span class="text-gray-400 ml-2">$${p.market_value.toFixed(2)}</span>
                    </div>
                </div>
            `).join('');
        }
        
        function addActionLog(message) {
            const container = document.getElementById('actions-log');
            const placeholder = container.querySelector('.text-center');
            if (placeholder) placeholder.remove();
            
            const time = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            const entry = document.createElement('div');
            entry.className = 'text-sm text-gray-300 p-2 rounded bg-bg-tertiary';
            entry.textContent = `[${time}] ${message}`;
            container.insertBefore(entry, container.firstChild);
        }
        
        function toggleAutopilot() {
            const enabled = document.getElementById('autopilot-toggle').checked;
            callPython('toggle_autopilot', enabled);
        }
        
        function openDiversifyDialog() {
            callPython('open_diversify_dialog');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', analyzePortfolio);
    </script>
</body>
</html>
```

**Python API Methods for Autopilot (add to gui/api.py):**

```python
# Add these methods to the LeviathanAPI class in gui/api.py

def analyze_portfolio(self) -> str:
    """Analyze portfolio health for Autopilot window"""
    try:
        health = self.autopilot.analyze_portfolio_health()
        return json.dumps(health)
    except Exception as e:
        return json.dumps({'error': str(e), 'overall_health_score': 0, 'position_analysis': []})

def run_checkup(self) -> str:
    """Run portfolio checkup immediately"""
    try:
        result = self.autopilot.run_daily_checkup()
        self._log_activity('AUTOPILOT', f"Checkup completed: {result['status']}")
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'status': 'error', 'error': str(e)})

def set_risk_tolerance(self, level: str) -> str:
    """Set risk tolerance level"""
    self.autopilot.risk_tolerance = level
    self._log_activity('AUTOPILOT', f'Risk tolerance set to {level}')
    return json.dumps({'status': 'updated', 'level': level})

def toggle_autopilot(self, enabled: bool) -> str:
    """Enable/disable daily auto-checkup"""
    self.autopilot.enabled = enabled
    status = 'enabled' if enabled else 'disabled'
    self._log_activity('AUTOPILOT', f'Daily auto-checkup {status}')
    return json.dumps({'status': status})

def open_diversify_dialog(self) -> str:
    """Open the auto-diversify dialog"""
    # In a full implementation, this would open a new webview window
    self._log_activity('AUTOPILOT', 'Auto-diversify dialog opened')
    return json.dumps({'status': 'opened'})
```

---

## Execution Order

Build the system in this sequence:

### Phase 1: Foundation (Agent 1 + 5)
1. Set up project structure and configuration
2. Implement Alpaca client with authentication
3. Build state persistence (SQLite)
4. Create logging infrastructure
5. Implement API key encryption

### Phase 2: Data Pipeline (Agent 1)
6. Historical data fetching and storage
7. Real-time WebSocket streaming
8. Technical indicator calculation
9. Data validation and cleaning
10. Economic calendar integration
11. Earnings calendar integration

### Phase 3: Intelligence (Agent 2 + 3)
12. Feature engineering pipeline
13. LSTM model implementation
14. LightGBM model implementation
15. Ensemble combination
16. FinBERT sentiment analysis
17. News API integration
18. Multi-timeframe analysis module
19. Market regime detection

### Phase 4: Learning System (Agent 6)
20. Learning database schema and implementation
21. Trade outcome recording system
22. Best practices tracking and querying
23. Dynamic position sizing with performance tiers
24. Self-analysis system (Opus integration)
25. Automatic training triggers and pipeline
26. Manual training interface
27. Auto data fetcher for continuous learning

### Phase 5: Opus Brain Integration (Agent 6 + 4)
28. Opus trading brain implementation
29. Decision prompt engineering
30. Historical context retrieval for Opus
31. Autonomous executor (no human approval needed)
32. Exit manager for open positions
33. Cost tracking and budget management

### Phase 6: Risk & Portfolio Management (Agent 5)
34. Signal generation with dynamic sizing integration
35. Position sizing using learned optimal values
36. Order management
37. PDT tracking
38. Risk management with drawdown scaling
39. Circuit breakers
40. Portfolio correlation analysis
41. Slippage estimator

### Phase 7: Historical Training System (Agent 6)
42. Historical trade identifier (find past good entries/exits)
43. Pattern extraction from historical data
44. Training data generation
45. Populate learning database with historical examples

### Phase 8: Extended Features (Agent 8)
46. Cryptocurrency trading module (24/7, PDT-exempt, all 26 supported coins)
47. **Crypto swap optimizer (find optimal path between any two cryptos)**
48. **Crypto portfolio rebalancer (automatic allocation to target percentages)**
49. **Long-term Portfolio Autopilot (auto-diversify, detect bearish, rotate)**
50. **Opus Portfolio Advisor (AI financial advisor for holdings)**
51. Options trading module (credit spreads, iron condors)
52. Notification system (email, desktop)
53. PDF report generator
54. Wash sale tracker
55. Backup and recovery system
56. Watchlist management

### Phase 9: GUI Development (Agent 7A + 7B in parallel)

**Agent 7A - Frontend (can start immediately with Figma design):**
57. Set up frontend/ directory structure
58. Create index.html with Tailwind CSS configuration
59. Implement color palette matching Figma design
60. Build sidebar navigation with SVG icons
61. Create stat cards (Portfolio Value, P&L, Opus Brain, Win Rate)
62. Integrate ApexCharts for portfolio performance graph
63. Build positions list and activity log components
64. Implement START/STOP controls with state management
65. Create training.html, settings.html, crypto_swap.html, analytics.html, autopilot.html
66. Add CSS animations (pulse, hover, transitions)

**Agent 7B - Python Backend (needs Agent 5 orchestration):**
67. Build gui/app.py PyWebView launcher
68. Implement LeviathanAPI class in gui/api.py
69. Create start_trading() / stop_trading() methods
70. Build get_dashboard_data() for frontend polling
71. Implement activity logging system
72. Create all Autopilot API methods
73. Handle background threading for trading loop

### Phase 10: Integration (Agent 5 + All)
67. Event-driven message bus
68. Main orchestration loop
69. Crash recovery logic
70. GUI integration with trading engine
71. Learning system hooks into all modules
72. Self-improvement feedback loops
73. All calendar integrations feeding into Opus decisions
74. **Crypto swap optimizer integration with Opus brain**
75. **Portfolio Autopilot integration with daily scheduler**
76. **Opus Portfolio Advisor integration**

### Phase 11: Validation & Testing
77. Unit tests for all modules
78. Integration tests
79. Backtest runner with full strategy suite
80. Paper trading validation (4 weeks minimum)
81. Verify learning database is recording correctly
82. Test automatic retraining triggers
83. Test full autonomous cycle (GUI Start → Trade → Exit)
84. Verify Opus reasoning quality
85. Test crypto 24/7 trading
86. **Test crypto swap optimizer (multi-hop paths: DOGE → USD → ETH)**
87. **Test crypto portfolio rebalancer**
88. **Test Portfolio Autopilot bearish detection**
89. **Test Portfolio Autopilot auto-rotation (sell weak → buy strong)**
90. **Test auto-diversification templates (balanced, growth, income)**
91. Test options order execution
92. Verify notification delivery
93. Test backup/restore functionality
94. Tax report generation test

---

## Critical Reminders

### Trading Safety
1. **NEVER execute live trades until paper trading shows consistent profitability for 4+ weeks**
2. **ALWAYS check buying power before submitting orders**
3. **NEVER submit market orders for illiquid securities** — use slippage estimator first
4. **ALWAYS implement graceful shutdown that cancels open orders**
5. **Start with ONE strategy** — Get RSI Mean Reversion working perfectly before adding others

### Data & Logging
6. **LOG EVERYTHING** — Every signal, every order, every decision for debugging and tax records
7. **Reconcile state with Alpaca on every startup** — Local state may be stale after crashes
8. **RECORD EVERY TRADE OUTCOME TO LEARNING DATABASE** — This is how the AI improves. No exceptions.
9. **Backup database daily** — Use the automatic backup system

### Risk Management
10. **Position sizing MUST be dynamic** — The AI should risk more as it proves profitable, less when losing
11. **Check portfolio correlation before new trades** — Avoid over-concentration in correlated assets
12. **Respect circuit breakers** — When triggered, ALL trading stops immediately
13. **Track wash sales from day one** — Critical for tax compliance
14. **Check earnings calendar before entry** — Avoid surprise volatility

### AI & Learning
15. **Learning database is CRITICAL** — The AI must be able to query its own history to make better decisions
16. **Self-analysis should run daily** — End of each trading day, Opus analyzes performance
17. **Automatic retraining must have human approval for deployment** — Don't auto-deploy without verification
18. **The AI should get BETTER over time** — If performance isn't improving after 3+ months, debug the learning system

### Market Awareness
19. **Check economic calendar before trading** — Avoid high-impact events (FOMC, NFP, CPI)
20. **Detect market regime daily** — Adjust strategies based on BULL/BEAR/RANGING/VOLATILE
21. **Use multi-timeframe analysis** — Higher timeframes should confirm lower timeframe signals
22. **Crypto is PDT-exempt** — Use this for day trading when needed

### Cost Management
23. **Budget Opus API calls carefully** — ~$0.08/decision, set daily limits
24. **Track API costs in real-time** — Display in GUI, stop if budget exceeded
25. **Use Sonnet for non-critical tasks** — Reports, summaries, logging explanations

### Testing & Validation
26. **Test failure modes** — What happens when API is down? WebSocket disconnects? Order rejected?
27. **Paper trade in parallel with live** — Always have paper running to compare
28. **Backtest every strategy change** — No untested code goes live
29. **Test the full autonomous cycle** — GUI Start → Signal → Opus Decision → Trade → Exit

### Security
30. **Encrypt API keys** — Never store plaintext credentials
31. **Paper trading by default** — Live mode requires explicit environment variable
32. **Rate limit all API calls** — Respect Alpaca's 200/minute limit


---

## Claude Code Feature Checklist

**This is the master list of features to build. Check off each one as completed.**

### Core Trading Engine
- [ ] Alpaca API client (stocks, crypto, options)
- [ ] Order management (market, limit, stop, bracket orders)
- [ ] Position tracking and P&L calculation
- [ ] PDT tracker (max 3 day trades per 5-day window)
- [ ] Circuit breakers (stop trading on 3% daily loss)

### AI Brain (Opus 4.5)
- [ ] Opus decision-making brain
- [ ] Autonomous trade execution (no human approval needed)
- [ ] **Stock Exit Manager**
  - [ ] Stop loss monitoring (exit immediately when hit)
  - [ ] Trailing stop (lock in profits)
  - [ ] Take profit targets
  - [ ] Time stops (exit after X days)
  - [ ] Technical reversal detection
- [ ] **Options Exit Manager**
  - [ ] Profit target (close at 50% of max profit)
  - [ ] DTE monitoring (close when < 7 days to expiration)
  - [ ] Stop loss for options
  - [ ] Theta decay tracking
- [ ] Historical context retrieval for decisions
- [ ] Cost tracking and daily budget enforcement

### Machine Learning Pipeline
- [ ] LSTM model for sequential patterns
- [ ] LightGBM model for tabular features
- [ ] N-BEATS model for time series forecasting
- [ ] Ensemble combiner (stacking)
- [ ] Walk-forward validation
- [ ] Automatic retraining triggers

### Cryptocurrency Module (CRITICAL)
- [ ] CryptoTrader class - buy/sell crypto
- [ ] **CryptoSwapOptimizer - swap ANY crypto to ANY other crypto**
  - [ ] Build graph of all 56+ trading pairs
  - [ ] BFS pathfinding for optimal route
  - [ ] Multi-hop swap execution (DOGE → USD → ETH)
  - [ ] Fee calculation per hop
- [ ] CryptoPortfolioRebalancer - auto-rebalance to target allocation
- [ ] 24/7 trading support
- [ ] Crypto-specific strategies (faster indicators)

### Long-Term Portfolio Autopilot (CRITICAL)
- [ ] **PortfolioAutopilot class - AI-managed long-term holdings**
  - [ ] Risk tolerance configuration (conservative/moderate/aggressive)
  - [ ] Daily portfolio health analysis
  - [ ] Bearish signal detection on holdings
  - [ ] Weak position identification
  - [ ] Strong stock candidate finder
- [ ] **Auto-rotation feature**
  - [ ] Detect bearish holdings
  - [ ] Find replacement candidates (momentum, trend, diversification)
  - [ ] Execute rotation (sell weak → buy strong)
  - [ ] Log all rotations with reasoning
- [ ] **Auto-diversification**
  - [ ] Balanced template (30% large cap, 15% growth, 15% intl, 15% bonds, etc.)
  - [ ] Growth template (tech-heavy)
  - [ ] Income template (dividends, bonds)
  - [ ] All-Weather template (Ray Dalio style)
- [ ] **OpusPortfolioAdvisor - AI financial advisor**
  - [ ] Portfolio analysis and decision making
  - [ ] Rotation approval
  - [ ] Rebalancing recommendations
- [ ] Daily autopilot checkup scheduler
- [ ] GUI: Autopilot window with status, analysis, controls

### Learning System
- [ ] Learning database (SQLite)
- [ ] Trade outcome recording
- [ ] Best practices tracking
- [ ] Dynamic position sizing (5 tiers based on performance)
- [ ] Self-analysis (daily at market close)
- [ ] Historical training from past data
- [ ] Manual training interface

### Risk Management
- [ ] Pre-trade risk checks
- [ ] Portfolio correlation analysis
- [ ] Drawdown-based position scaling
- [ ] Slippage estimator
- [ ] Wash sale tracker

### Market Intelligence
- [ ] Market regime detection (BULL/BEAR/RANGING/VOLATILE)
- [ ] Multi-timeframe analysis
- [ ] Economic calendar integration
- [ ] Earnings calendar integration
- [ ] FinBERT sentiment analysis
- [ ] News API integration

### GUI Application (PyWebView + HTML/CSS/JS)

**Design Reference:**
- Figma Community: https://www.figma.com/community/file/1522238618706669989/dark-finance-crypto-dashboard-ui-design
- Figma Prototype: https://www.figma.com/proto/zh1yF465p1YnQ4JGmtcXtQ/%F0%9F%A7%BE-Dark-Finance---Crypto-Dashboard-%E2%80%93-UI-Design--Community-?node-id=2-539&t=eRz7gczlnE7qSKQB-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1

**Frontend (frontend/):**
- [ ] index.html - Main dashboard with Tailwind CSS
- [ ] Color palette matching Figma (--bg-primary: #0a0a0f, etc.)
- [ ] Typography (Inter font, proper type scale)
- [ ] Sidebar navigation with icons
- [ ] Stat cards (Portfolio Value, Today's P&L, Opus Brain, Win Rate)
- [ ] Portfolio performance chart (ApexCharts)
- [ ] Open positions list component
- [ ] Activity log component
- [ ] START/STOP control buttons with proper states
- [ ] Status badge (RUNNING/STOPPED with pulse animation)
- [ ] training.html - Training interface
- [ ] settings.html - Settings modal
- [ ] crypto_swap.html - Crypto swap interface
- [ ] analytics.html - Analytics dashboard
- [ ] js/app.js - Main application logic
- [ ] js/api.js - Python bridge wrapper (pywebview.api)
- [ ] js/charts.js - ApexCharts configurations
- [ ] CSS animations (pulse-running, card-hover, etc.)
- [ ] SVG icons for sidebar navigation

**Python Backend (gui/):**
- [ ] gui/app.py - PyWebView launcher
- [ ] gui/api.py - LeviathanAPI class for JS bridge
- [ ] start_trading() - Start autonomous trading
- [ ] stop_trading() - Stop trading and cancel orders
- [ ] get_dashboard_data() - All data for dashboard refresh
- [ ] get_activity_log() - Recent activity entries
- [ ] open_settings() / open_training() / open_crypto_swap() / open_autopilot()
- [ ] _trading_loop() - Background thread for trading cycles
- [ ] _log_activity() - Activity logging for frontend

**Windows & Modals:**
- [ ] **Crypto swap window (select from/to, show path, execute)**
- [ ] **Portfolio Autopilot window**
  - [ ] Risk tolerance selector (conservative/moderate/aggressive)
  - [ ] Portfolio health score display
  - [ ] Holdings table with bearish/bullish signals
  - [ ] Analyze Portfolio button
  - [ ] Run Checkup Now button
  - [ ] Auto-Diversify dialog
  - [ ] Enable/Disable daily auto-checkup toggle
  - [ ] Recent actions log
- [ ] Training window
- [ ] Settings window
- [ ] Analytics dashboard

### Extended Features
- [ ] **Options Trading Module**
  - [ ] OptionsTrader class - scanner + strategy logic
  - [ ] Bull put spreads, bear call spreads (credit spreads)
  - [ ] Iron condors (4-leg neutral strategy)
  - [ ] Bull call spreads, bear put spreads (debit spreads)
  - [ ] GreeksCalculator - Delta, Gamma, Theta, Vega, Rho
  - [ ] DTESelector - optimal expiration selection (21-45 DTE)
  - [ ] Multi-leg order execution via Alpaca
- [ ] **Options Intelligence Module (CRITICAL)**
  - [ ] OptionsIntelligence class - comprehensive analysis engine
  - [ ] **Volatility Analysis:**
    - [ ] IV Rank calculation (current IV vs 52-week range)
    - [ ] IV Percentile calculation
    - [ ] Historical Volatility (HV) 20-day and 60-day
    - [ ] IV vs HV comparison ratio
    - [ ] Volatility regime detection (HIGH_IV, LOW_IV, NORMAL)
  - [ ] **Options Flow Analysis:**
    - [ ] Put/Call ratio (volume and open interest)
    - [ ] Unusual options activity detection
    - [ ] Large premium detection (institutional bets)
    - [ ] Flow sentiment determination (BULLISH/BEARISH/NEUTRAL)
  - [ ] **Max Pain Calculation:**
    - [ ] Calculate max pain strike for each expiration
    - [ ] Distance to max pain from current price
    - [ ] Pain distribution across strikes
  - [ ] **Greeks Summary:**
    - [ ] ATM call/put Greeks
    - [ ] Gamma risk assessment
    - [ ] Theta decay tracking
  - [ ] **Events Awareness:**
    - [ ] Earnings calendar integration
    - [ ] IV crush risk detection
    - [ ] Event-based strategy adjustment
  - [ ] **AI Recommendation Engine:**
    - [ ] Multi-factor scoring (volatility, flow, technicals, sentiment)
    - [ ] Direction determination (BULLISH/BEARISH/NEUTRAL)
    - [ ] Strategy selection based on IV + direction
    - [ ] Confidence scoring
  - [ ] OpusOptionsDecisionEngine - Opus makes final call on trades
- [ ] Email/desktop notifications
- [ ] PDF report generator
- [ ] Tax report export (CSV for TurboTax)
- [ ] Automatic daily backups
- [ ] Watchlist management

### Testing Requirements
- [ ] Unit tests for all modules
- [ ] Integration tests
- [ ] Backtest with 3+ years data
- [ ] Paper trading 4+ weeks
- [ ] Test crypto swap multi-hop paths
- [ ] Test full autonomous cycle

---

**END OF LEVIATHAN PROJECT SPECIFICATION**
**Version: 1.0**
**Last Updated: January 2026**
**Ready for Claude Code Implementation**

