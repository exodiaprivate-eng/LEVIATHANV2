"""Options intelligence - IV analysis, flow detection, max pain, earnings, AI recs."""
import logging
import math
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger('leviathan.options_intel')


class OptionsIntelligence:
    """Advanced options analytics combining Greeks, flow, technicals, and AI."""

    def __init__(self, alpaca_client=None, anthropic_client=None, config: dict = None):
        """
        Args:
            alpaca_client: AlpacaClient for market data.
            anthropic_client: Anthropic SDK client for AI recommendations.
            config: Project config dict.
        """
        self.alpaca = alpaca_client
        self.ai = anthropic_client
        self.config = config or {}

    # ------------------------------------------------------------------
    # 1. Volatility analysis
    # ------------------------------------------------------------------
    def analyze_volatility(self, symbol: str, chain: dict) -> dict:
        """Compute IV rank, IV percentile, and vol skew from a chain.

        Returns dict with iv_rank, iv_percentile, current_iv, historical_iv,
        skew, recommendation.
        """
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])
        all_contracts = calls + puts

        if not all_contracts:
            return {'symbol': symbol, 'iv_rank': 0, 'iv_percentile': 0,
                    'recommendation': 'insufficient_data'}

        ivs = [c['implied_volatility'] for c in all_contracts
               if c.get('implied_volatility', 0) > 0]
        if not ivs:
            return {'symbol': symbol, 'iv_rank': 0, 'iv_percentile': 0,
                    'recommendation': 'no_iv_data'}

        current_iv = sum(ivs) / len(ivs)

        # Approximate historical IV from chain spread (ATM options)
        historical_iv = self._estimate_historical_iv(symbol)

        # IV Rank: where current IV sits vs 52-week range
        iv_high = max(historical_iv) if historical_iv else current_iv
        iv_low = min(historical_iv) if historical_iv else current_iv
        iv_range = iv_high - iv_low
        iv_rank = ((current_iv - iv_low) / iv_range * 100) if iv_range > 0 else 50

        # IV Percentile: % of days IV was below current
        iv_percentile = (sum(1 for h in historical_iv if h <= current_iv)
                         / len(historical_iv) * 100) if historical_iv else 50

        # Skew: compare OTM put IV to OTM call IV
        put_ivs = [c['implied_volatility'] for c in puts
                   if c.get('implied_volatility', 0) > 0]
        call_ivs = [c['implied_volatility'] for c in calls
                    if c.get('implied_volatility', 0) > 0]
        avg_put_iv = sum(put_ivs) / len(put_ivs) if put_ivs else 0
        avg_call_iv = sum(call_ivs) / len(call_ivs) if call_ivs else 0
        skew = round(avg_put_iv - avg_call_iv, 4)

        # Recommendation
        if iv_rank > 60:
            rec = 'sell_premium'
        elif iv_rank < 30:
            rec = 'buy_premium'
        else:
            rec = 'neutral'

        return {
            'symbol': symbol,
            'current_iv': round(current_iv, 4),
            'iv_rank': round(iv_rank, 1),
            'iv_percentile': round(iv_percentile, 1),
            'iv_high_52w': round(iv_high, 4),
            'iv_low_52w': round(iv_low, 4),
            'put_iv_avg': round(avg_put_iv, 4),
            'call_iv_avg': round(avg_call_iv, 4),
            'skew': skew,
            'recommendation': rec,
        }

    # ------------------------------------------------------------------
    # 2. Options flow / unusual activity
    # ------------------------------------------------------------------
    def analyze_options_flow(self, symbol: str, chain: Optional[dict] = None) -> dict:
        """Detect unusual options activity from volume/OI ratios.

        Returns dict with flow signals, volume anomalies, put/call ratio.
        """
        if chain is None:
            return {'symbol': symbol, 'flow_signals': [],
                    'error': 'No chain provided'}

        calls = chain.get('calls', [])
        puts = chain.get('puts', [])

        total_call_vol = sum(c.get('volume', 0) for c in calls)
        total_put_vol = sum(c.get('volume', 0) for c in puts)
        total_call_oi = sum(c.get('open_interest', 0) for c in calls)
        total_put_oi = sum(c.get('open_interest', 0) for c in puts)

        pc_ratio = (total_put_vol / total_call_vol
                    if total_call_vol > 0 else 0)

        # Find unusual strikes (vol > 3x OI)
        unusual_strikes = []
        for c in calls + puts:
            vol = c.get('volume', 0)
            oi = c.get('open_interest', 0)
            if oi > 0 and vol > 3 * oi:
                unusual_strikes.append({
                    'strike': c['strike'],
                    'expiration': c.get('expiration', ''),
                    'type': c.get('contract_type', 'unknown'),
                    'volume': vol,
                    'open_interest': oi,
                    'vol_oi_ratio': round(vol / oi, 1),
                })

        # Flow sentiment
        if pc_ratio > 1.5:
            sentiment = 'very_bearish'
        elif pc_ratio > 1.0:
            sentiment = 'bearish'
        elif pc_ratio < 0.5:
            sentiment = 'very_bullish'
        elif pc_ratio < 0.7:
            sentiment = 'bullish'
        else:
            sentiment = 'neutral'

        return {
            'symbol': symbol,
            'total_call_volume': total_call_vol,
            'total_put_volume': total_put_vol,
            'total_call_oi': total_call_oi,
            'total_put_oi': total_put_oi,
            'put_call_ratio': round(pc_ratio, 2),
            'flow_sentiment': sentiment,
            'unusual_strikes': unusual_strikes,
            'has_unusual_activity': len(unusual_strikes) > 0,
        }

    # ------------------------------------------------------------------
    # 3. Max pain
    # ------------------------------------------------------------------
    def calculate_max_pain(self, chain: dict) -> dict:
        """Calculate the max-pain strike (price causing maximum loss to holders).

        For each candidate strike, compute total dollar value that would be
        lost by all outstanding call and put holders if the stock closed there.
        The strike with the highest total pain is the max-pain price.
        """
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])

        if not calls and not puts:
            return {'max_pain': 0, 'error': 'Empty chain'}

        all_strikes = sorted(set(
            c['strike'] for c in calls + puts
        ))

        if not all_strikes:
            return {'max_pain': 0}

        pain_by_strike = {}
        for test_price in all_strikes:
            call_pain = 0
            for c in calls:
                if test_price > c['strike']:
                    # Calls are ITM -> holders profit, writers lose
                    call_pain += (test_price - c['strike']) * c.get('open_interest', 0) * 100
            put_pain = 0
            for p in puts:
                if test_price < p['strike']:
                    put_pain += (p['strike'] - test_price) * p.get('open_interest', 0) * 100

            pain_by_strike[test_price] = call_pain + put_pain

        # Max pain = strike where total ITM value is MINIMIZED (holders lose most)
        max_pain_strike = min(pain_by_strike, key=pain_by_strike.get)

        return {
            'max_pain': max_pain_strike,
            'pain_by_strike': {str(k): round(v, 2)
                               for k, v in sorted(pain_by_strike.items())},
            'total_call_oi': sum(c.get('open_interest', 0) for c in calls),
            'total_put_oi': sum(p.get('open_interest', 0) for p in puts),
        }

    # ------------------------------------------------------------------
    # 4. Greeks summary
    # ------------------------------------------------------------------
    def get_greeks_summary(self, chain: dict) -> dict:
        """Aggregate Greeks across the chain for overall exposure picture."""
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])

        def _agg(contracts):
            n = len(contracts) or 1
            return {
                'avg_delta': round(sum(c.get('delta', 0) for c in contracts) / n, 4),
                'avg_gamma': round(sum(c.get('gamma', 0) for c in contracts) / n, 4),
                'avg_theta': round(sum(c.get('theta', 0) for c in contracts) / n, 4),
                'avg_vega': round(sum(c.get('vega', 0) for c in contracts) / n, 4),
                'avg_iv': round(sum(c.get('implied_volatility', 0)
                                    for c in contracts) / n, 4),
                'count': len(contracts),
            }

        return {
            'calls': _agg(calls),
            'puts': _agg(puts),
            'net_delta': round(
                sum(c.get('delta', 0) for c in calls) +
                sum(c.get('delta', 0) for c in puts), 4
            ),
            'total_theta': round(
                sum(c.get('theta', 0) for c in calls + puts), 4
            ),
            'total_vega': round(
                sum(c.get('vega', 0) for c in calls + puts), 4
            ),
        }

    # ------------------------------------------------------------------
    # 5. Earnings proximity check
    # ------------------------------------------------------------------
    def check_earnings_proximity(self, symbol: str) -> dict:
        """Check if earnings are near, which inflates IV.

        Uses Alpaca calendar/news or a simple heuristic.
        Returns days to earnings and a warning flag.
        """
        # Attempt to detect via Alpaca news endpoint
        try:
            if self.alpaca:
                self.alpaca._rate_limit()
                from alpaca.data.requests import NewsRequest
                request = NewsRequest(
                    symbols=[symbol],
                    start=datetime.now() - timedelta(days=7),
                    end=datetime.now() + timedelta(days=30),
                    limit=20,
                )
                news = self.alpaca.data_client.get_news(request)
                for article in news.news if hasattr(news, 'news') else []:
                    headline = (article.headline or '').lower()
                    if any(kw in headline for kw in
                           ['earnings', 'quarterly results', 'q1', 'q2', 'q3', 'q4',
                            'revenue', 'eps', 'guidance']):
                        return {
                            'symbol': symbol,
                            'earnings_nearby': True,
                            'headline': article.headline,
                            'date': str(article.created_at.date()
                                        if article.created_at else ''),
                            'warning': 'IV likely elevated due to upcoming earnings',
                        }
        except Exception as e:
            logger.debug(f"Earnings check via news failed: {e}")

        return {
            'symbol': symbol,
            'earnings_nearby': False,
            'warning': None,
        }

    # ------------------------------------------------------------------
    # 6. Technical context
    # ------------------------------------------------------------------
    def get_technical_context(self, symbol: str) -> dict:
        """Pull basic technical indicators for options decision context."""
        try:
            if not self.alpaca:
                return {'symbol': symbol, 'error': 'No data client'}

            df = self.alpaca.get_historical_bars(symbol, days=60)
            if df.empty:
                return {'symbol': symbol, 'error': 'No price data'}

            close = df['close']
            current = float(close.iloc[-1])

            # SMA
            sma20 = float(close.rolling(20).mean().iloc[-1])
            sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20

            # RSI(14)
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss.replace(0, float('nan'))
            rsi = float(100 - 100 / (1 + rs.iloc[-1])) if not rs.empty else 50

            # Bollinger Bands
            bb_mid = sma20
            bb_std = float(close.rolling(20).std().iloc[-1])
            bb_upper = bb_mid + 2 * bb_std
            bb_lower = bb_mid - 2 * bb_std

            # Trend
            if current > sma20 > sma50:
                trend = 'bullish'
            elif current < sma20 < sma50:
                trend = 'bearish'
            else:
                trend = 'mixed'

            return {
                'symbol': symbol,
                'price': round(current, 2),
                'sma20': round(sma20, 2),
                'sma50': round(sma50, 2),
                'rsi': round(rsi, 1),
                'bb_upper': round(bb_upper, 2),
                'bb_lower': round(bb_lower, 2),
                'trend': trend,
            }
        except Exception as e:
            logger.error(f"Technical context failed for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    # ------------------------------------------------------------------
    # 7. Sentiment context
    # ------------------------------------------------------------------
    def get_sentiment_context(self, symbol: str) -> dict:
        """Gather recent news sentiment for options context."""
        try:
            if not self.alpaca:
                return {'symbol': symbol, 'sentiment': 'unknown'}

            self.alpaca._rate_limit()
            from alpaca.data.requests import NewsRequest
            request = NewsRequest(
                symbols=[symbol],
                start=datetime.now() - timedelta(days=3),
                end=datetime.now(),
                limit=10,
            )
            news = self.alpaca.data_client.get_news(request)
            articles = news.news if hasattr(news, 'news') else []

            headlines = [a.headline for a in articles if a.headline]

            # Simple keyword sentiment
            bullish_kw = ['upgrade', 'beat', 'surge', 'rally', 'bullish',
                          'outperform', 'buy', 'record', 'growth']
            bearish_kw = ['downgrade', 'miss', 'crash', 'plunge', 'bearish',
                          'underperform', 'sell', 'decline', 'loss']

            bull_count = sum(1 for h in headlines
                            for kw in bullish_kw if kw in h.lower())
            bear_count = sum(1 for h in headlines
                            for kw in bearish_kw if kw in h.lower())

            if bull_count > bear_count + 1:
                sentiment = 'bullish'
            elif bear_count > bull_count + 1:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'

            return {
                'symbol': symbol,
                'sentiment': sentiment,
                'bullish_signals': bull_count,
                'bearish_signals': bear_count,
                'article_count': len(headlines),
                'recent_headlines': headlines[:5],
            }
        except Exception as e:
            logger.debug(f"Sentiment fetch failed for {symbol}: {e}")
            return {'symbol': symbol, 'sentiment': 'unknown', 'error': str(e)}

    # ------------------------------------------------------------------
    # 8. AI recommendation
    # ------------------------------------------------------------------
    def get_ai_recommendation(self, symbol: str, analysis: dict) -> dict:
        """Use Claude to synthesise all analysis into a trading recommendation."""
        if not self.ai:
            return self._rule_based_recommendation(symbol, analysis)

        prompt = (
            f"You are an expert options trader. Given the following analysis for "
            f"{symbol}, provide a concise trading recommendation.\n\n"
            f"Volatility: {analysis.get('volatility', {})}\n"
            f"Flow: {analysis.get('flow', {})}\n"
            f"Max Pain: {analysis.get('max_pain', {})}\n"
            f"Greeks: {analysis.get('greeks', {})}\n"
            f"Earnings: {analysis.get('earnings', {})}\n"
            f"Technicals: {analysis.get('technicals', {})}\n"
            f"Sentiment: {analysis.get('sentiment', {})}\n\n"
            f"Respond with JSON: {{\"action\": \"buy_calls|buy_puts|sell_puts|"
            f"sell_calls|iron_condor|no_trade\", \"confidence\": 0-100, "
            f"\"reasoning\": \"...\", \"strategy\": \"...\", \"target_dte\": int, "
            f"\"target_delta\": float}}"
        )

        try:
            response = self.ai.messages.create(
                model=self.config.get('decision_model', 'claude-opus-4-5-20250101'),
                max_tokens=500,
                messages=[{'role': 'user', 'content': prompt}],
            )
            import json
            text = response.content[0].text
            # Try to parse JSON from response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                rec = json.loads(text[start:end])
                rec['source'] = 'ai'
                return rec
        except Exception as e:
            logger.warning(f"AI recommendation failed: {e}")

        return self._rule_based_recommendation(symbol, analysis)

    # ------------------------------------------------------------------
    # 9. Complete analysis orchestrator
    # ------------------------------------------------------------------
    def get_complete_analysis(self, symbol: str,
                              chain: Optional[dict] = None) -> dict:
        """Run all analysis methods and return a unified report."""
        result = {'symbol': symbol, 'timestamp': datetime.now().isoformat()}

        # Fetch chain if not provided
        if chain is None:
            result['error'] = 'No options chain provided'
            return result

        result['volatility'] = self.analyze_volatility(symbol, chain)
        result['flow'] = self.analyze_options_flow(symbol, chain)
        result['max_pain'] = self.calculate_max_pain(chain)
        result['greeks'] = self.get_greeks_summary(chain)
        result['earnings'] = self.check_earnings_proximity(symbol)
        result['technicals'] = self.get_technical_context(symbol)
        result['sentiment'] = self.get_sentiment_context(symbol)
        result['recommendation'] = self.get_ai_recommendation(symbol, result)

        # Overall score (0-100)
        result['overall_score'] = self._compute_overall_score(result)

        logger.info(
            f"Complete options analysis for {symbol}: "
            f"score={result['overall_score']}, "
            f"rec={result['recommendation'].get('action', 'none')}"
        )
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _estimate_historical_iv(self, symbol: str) -> list:
        """Estimate historical IV from price data using close-to-close vol."""
        try:
            if not self.alpaca:
                return []
            df = self.alpaca.get_historical_bars(symbol, days=365)
            if df.empty or len(df) < 30:
                return []
            returns = df['close'].pct_change().dropna()
            # Rolling 20-day realized vol annualised as IV proxy
            rolling_vol = returns.rolling(20).std() * math.sqrt(252)
            return [round(float(v), 4) for v in rolling_vol.dropna().tolist()]
        except Exception:
            return []

    @staticmethod
    def _rule_based_recommendation(symbol: str, analysis: dict) -> dict:
        """Fallback rule-based recommendation when AI is unavailable."""
        vol = analysis.get('volatility', {})
        flow = analysis.get('flow', {})
        tech = analysis.get('technicals', {})

        iv_rank = vol.get('iv_rank', 50)
        flow_sentiment = flow.get('flow_sentiment', 'neutral')
        trend = tech.get('trend', 'mixed')
        rsi = tech.get('rsi', 50)

        # Decision matrix
        if iv_rank > 60:
            # High IV -> sell premium
            if trend == 'bullish' and flow_sentiment in ('bullish', 'very_bullish'):
                action = 'sell_puts'
            elif trend == 'bearish' and flow_sentiment in ('bearish', 'very_bearish'):
                action = 'sell_calls'
            else:
                action = 'iron_condor'
        elif iv_rank < 30:
            # Low IV -> buy premium
            if trend == 'bullish' or rsi < 35:
                action = 'buy_calls'
            elif trend == 'bearish' or rsi > 65:
                action = 'buy_puts'
            else:
                action = 'no_trade'
        else:
            if trend == 'bullish':
                action = 'buy_calls'
            elif trend == 'bearish':
                action = 'buy_puts'
            else:
                action = 'no_trade'

        confidence = 40 if action == 'no_trade' else 55
        return {
            'action': action,
            'confidence': confidence,
            'reasoning': f'Rule-based: IV rank {iv_rank:.0f}, trend {trend}, '
                         f'flow {flow_sentiment}, RSI {rsi:.0f}',
            'strategy': 'single' if action.startswith('buy') else 'spread',
            'target_dte': 30,
            'target_delta': 0.40 if action.startswith('buy') else 0.20,
            'source': 'rules',
        }

    @staticmethod
    def _compute_overall_score(analysis: dict) -> int:
        """Compute a 0-100 conviction score from all sub-analyses."""
        score = 50  # baseline

        vol = analysis.get('volatility', {})
        flow = analysis.get('flow', {})
        tech = analysis.get('technicals', {})
        rec = analysis.get('recommendation', {})
        earnings = analysis.get('earnings', {})

        # IV alignment bonus
        iv_rank = vol.get('iv_rank', 50)
        action = rec.get('action', '')
        if 'sell' in action and iv_rank > 60:
            score += 10
        elif 'buy' in action and iv_rank < 30:
            score += 10

        # Flow alignment
        flow_sent = flow.get('flow_sentiment', 'neutral')
        if action in ('buy_calls', 'sell_puts') and flow_sent in ('bullish', 'very_bullish'):
            score += 10
        elif action in ('buy_puts', 'sell_calls') and flow_sent in ('bearish', 'very_bearish'):
            score += 10

        # Technical alignment
        trend = tech.get('trend', 'mixed')
        if action in ('buy_calls', 'sell_puts') and trend == 'bullish':
            score += 10
        elif action in ('buy_puts', 'sell_calls') and trend == 'bearish':
            score += 10

        # Earnings penalty (IV crush risk)
        if earnings.get('earnings_nearby'):
            score -= 15

        # Unusual activity bonus
        if flow.get('has_unusual_activity'):
            score += 5

        # Clamp
        return max(0, min(100, score))
