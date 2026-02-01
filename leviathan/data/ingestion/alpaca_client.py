"""Alpaca brokerage API client for trading and market data."""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, StopLimitOrderRequest,
    GetOrdersRequest, ClosePositionRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame

logger = logging.getLogger('leviathan.alpaca')


class AlpacaClient:
    """Unified Alpaca client for trading and data access."""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.paper = paper
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        self.crypto_client = CryptoHistoricalDataClient(api_key, secret_key)
        self._last_request_time = 0
        self._min_request_interval = 0.3  # ~200 req/min
        logger.info(f"Alpaca client initialized (paper={paper})")

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    # === Account ===
    def get_account(self):
        self._rate_limit()
        return self.trading_client.get_account()

    def get_buying_power(self) -> float:
        return float(self.get_account().buying_power)

    # === Positions ===
    def get_positions(self):
        self._rate_limit()
        return self.trading_client.get_all_positions()

    def get_position(self, symbol: str):
        self._rate_limit()
        return self.trading_client.get_open_position(symbol)

    # === Market Data ===
    def get_historical_bars(self, symbol: str, days: int = 365,
                            timeframe=None) -> pd.DataFrame:
        self._rate_limit()
        tf = timeframe or TimeFrame.Day
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=datetime.now() - timedelta(days=days),
            end=datetime.now(),
        )
        bars = self.data_client.get_stock_bars(request)
        return bars.df

    def get_latest_price(self, symbol: str) -> float:
        self._rate_limit()
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.data_client.get_stock_latest_quote(request)
            q = quote[symbol]
            return float(q.ask_price + q.bid_price) / 2
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return 0.0

    # === Stock Orders ===
    def submit_market_order(self, symbol: str, qty: float, side: str):
        self._rate_limit()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        request = MarketOrderRequest(
            symbol=symbol, qty=qty, side=order_side,
            time_in_force=TimeInForce.DAY,
        )
        order = self.trading_client.submit_order(request)
        logger.info(f"Market order submitted: {side} {qty} {symbol} -> {order.id}")
        return order

    def submit_limit_order(self, symbol: str, qty: float, side: str,
                           limit_price: float):
        self._rate_limit()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        request = LimitOrderRequest(
            symbol=symbol, qty=qty, side=order_side,
            limit_price=limit_price, time_in_force=TimeInForce.DAY,
        )
        order = self.trading_client.submit_order(request)
        logger.info(f"Limit order: {side} {qty} {symbol} @ {limit_price} -> {order.id}")
        return order

    def submit_bracket_order(self, symbol: str, qty: float, side: str,
                             take_profit: float, stop_loss: float):
        self._rate_limit()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        from alpaca.trading.requests import OrderRequest
        request = MarketOrderRequest(
            symbol=symbol, qty=qty, side=order_side,
            time_in_force=TimeInForce.DAY,
            order_class='bracket',
            take_profit={'limit_price': take_profit},
            stop_loss={'stop_price': stop_loss},
        )
        order = self.trading_client.submit_order(request)
        logger.info(f"Bracket order: {side} {qty} {symbol} TP={take_profit} SL={stop_loss}")
        return order

    def cancel_order(self, order_id: str):
        self._rate_limit()
        self.trading_client.cancel_order_by_id(order_id)
        logger.info(f"Cancelled order {order_id}")

    def cancel_all_orders(self):
        self._rate_limit()
        self.trading_client.cancel_orders()
        logger.info("All open orders cancelled")

    def get_orders(self, status: str = 'open'):
        self._rate_limit()
        request = GetOrdersRequest(status=status)
        return self.trading_client.get_orders(request)

    # === Crypto ===
    def get_crypto_bars(self, symbol: str, timeframe: str = '1Hour',
                        limit: int = 100) -> pd.DataFrame:
        self._rate_limit()
        tf_map = {'1Min': TimeFrame.Minute, '1Hour': TimeFrame.Hour, '1Day': TimeFrame.Day}
        tf = tf_map.get(timeframe, TimeFrame.Hour)
        request = CryptoBarsRequest(
            symbol_or_symbols=symbol, timeframe=tf,
            start=datetime.now() - timedelta(hours=limit),
        )
        bars = self.crypto_client.get_crypto_bars(request)
        return bars.df

    def get_crypto_quote(self, symbol: str) -> dict:
        self._rate_limit()
        from alpaca.data.requests import CryptoLatestQuoteRequest
        request = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = self.crypto_client.get_crypto_latest_quote(request)
        q = quote[symbol]
        return {'bid': float(q.bid_price), 'ask': float(q.ask_price)}

    def submit_crypto_order(self, symbol: str, qty: float = None,
                            notional: float = None, side: str = 'buy',
                            type: str = 'market', time_in_force: str = 'gtc',
                            limit_price: float = None):
        self._rate_limit()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        tif = TimeInForce.GTC if time_in_force == 'gtc' else TimeInForce.IOC

        if type == 'market':
            if notional:
                request = MarketOrderRequest(
                    symbol=symbol, notional=notional, side=order_side,
                    time_in_force=tif,
                )
            else:
                request = MarketOrderRequest(
                    symbol=symbol, qty=qty, side=order_side,
                    time_in_force=tif,
                )
        else:
            request = LimitOrderRequest(
                symbol=symbol, qty=qty, side=order_side,
                limit_price=limit_price, time_in_force=tif,
            )
        order = self.trading_client.submit_order(request)
        logger.info(f"Crypto order: {side} {symbol} qty={qty} notional={notional}")
        return order
