"""Cryptocurrency trading module - 24/7, PDT-exempt."""
import logging
import numpy as np
import pandas as pd
import pandas_ta as ta

logger = logging.getLogger('leviathan.crypto')


class CryptoTrader:
    """Crypto trading with faster indicators and 24/7 operation."""

    # Complete list of Alpaca-supported cryptocurrencies
    SUPPORTED_CRYPTOS = [
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD',
        'AVAX/USD', 'DOT/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD',
        'LTC/USD', 'BCH/USD', 'SHIB/USD', 'PEPE/USD', 'XTZ/USD',
        'BAT/USD', 'CRV/USD', 'GRT/USD', 'SUSHI/USD', 'YFI/USD',
        'SKY/USD', 'TRUMP/USD', 'USDC/USD', 'USDT/USD', 'USDG/USD',
    ]

    # Tradeable (non-stablecoin) cryptos for AI scanning
    SCANNABLE_CRYPTOS = [
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD',
        'AVAX/USD', 'DOT/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD',
        'LTC/USD', 'BCH/USD', 'SHIB/USD', 'PEPE/USD', 'XTZ/USD',
        'BAT/USD', 'CRV/USD', 'GRT/USD', 'SUSHI/USD', 'YFI/USD',
        'SKY/USD', 'TRUMP/USD',
    ]

    def __init__(self, alpaca_client, opus_brain=None):
        self.alpaca = alpaca_client
        self.opus = opus_brain
        self.is_running = False

    def get_crypto_opportunities(self) -> list:
        """Scan all tradeable cryptos for signals."""
        opportunities = []
        for symbol in self.SCANNABLE_CRYPTOS:
            try:
                data = self.alpaca.get_crypto_bars(symbol, timeframe='1Hour', limit=100)
                if data is None or len(data) < 20:
                    continue
                signal = self._analyze_crypto(symbol, data)
                if signal['strength'] > 0.6:
                    opportunities.append(signal)
            except Exception as e:
                logger.warning(f"Failed to analyze {symbol}: {e}")
        return sorted(opportunities, key=lambda x: x['strength'], reverse=True)

    def _analyze_crypto(self, symbol: str, data: pd.DataFrame) -> dict:
        """Crypto-specific analysis with faster indicators."""
        rsi = ta.rsi(data['close'], length=7)
        macd = ta.macd(data['close'], fast=8, slow=21, signal=5)
        strength = 0.0
        direction = 'neutral'

        if rsi is not None and len(rsi) > 0:
            r = rsi.iloc[-1]
            if r < 25:
                strength += 0.4
            elif r > 75:
                strength -= 0.4

        if macd is not None:
            cols = [c for c in macd.columns if 'MACD_' in c and 's' not in c.lower()]
            sig_cols = [c for c in macd.columns if 'MACDs' in c]
            if cols and sig_cols:
                if macd[cols[0]].iloc[-1] > macd[sig_cols[0]].iloc[-1]:
                    strength += 0.3
                else:
                    strength -= 0.2

        vol_ratio = 1.0
        if len(data) >= 20:
            vol_mean = data['volume'].rolling(20).mean().iloc[-1]
            if vol_mean > 0:
                vol_ratio = data['volume'].iloc[-1] / vol_mean
                if vol_ratio > 2.0:
                    strength += 0.2

        if strength > 0:
            direction = 'long'
        elif strength < 0:
            direction = 'short'

        return {
            'symbol': symbol,
            'strength': abs(strength),
            'direction': direction,
            'rsi': float(rsi.iloc[-1]) if rsi is not None and len(rsi) > 0 else 50,
            'volume_ratio': float(vol_ratio),
        }

    def buy_crypto(self, symbol: str, notional: float):
        """Buy crypto with a notional USD amount."""
        return self.alpaca.submit_crypto_order(symbol=symbol, notional=notional, side='buy')

    def sell_crypto(self, symbol: str, qty: float):
        """Sell a specific quantity of crypto."""
        return self.alpaca.submit_crypto_order(symbol=symbol, qty=qty, side='sell')

    def swap_crypto(self, from_crypto: str, to_crypto: str, amount: float):
        """Execute a multi-hop swap between two cryptos."""
        from leviathan.crypto.swap_optimizer import CryptoSwapOptimizer
        optimizer = CryptoSwapOptimizer(self.alpaca)
        return optimizer.execute_swap(from_crypto, to_crypto, amount, self.opus)
