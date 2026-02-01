"""Options Greeks calculations using Black-Scholes."""
import math
import logging
from scipy.stats import norm

logger = logging.getLogger('leviathan.greeks')


class GreeksCalculator:
    """Calculate options Greeks."""

    @staticmethod
    def _d1(S, K, T, r, sigma):
        return (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))

    @staticmethod
    def _d2(S, K, T, r, sigma):
        return GreeksCalculator._d1(S, K, T, r, sigma) - sigma * math.sqrt(T)

    @staticmethod
    def delta(S, K, T, r, sigma, option_type='call'):
        d1 = GreeksCalculator._d1(S, K, T, r, sigma)
        if option_type == 'call':
            return norm.cdf(d1)
        return norm.cdf(d1) - 1

    @staticmethod
    def gamma(S, K, T, r, sigma):
        d1 = GreeksCalculator._d1(S, K, T, r, sigma)
        return norm.pdf(d1) / (S * sigma * math.sqrt(T))

    @staticmethod
    def theta(S, K, T, r, sigma, option_type='call'):
        d1 = GreeksCalculator._d1(S, K, T, r, sigma)
        d2 = GreeksCalculator._d2(S, K, T, r, sigma)
        term1 = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
        if option_type == 'call':
            return (term1 - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
        return (term1 + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365

    @staticmethod
    def vega(S, K, T, r, sigma):
        d1 = GreeksCalculator._d1(S, K, T, r, sigma)
        return S * norm.pdf(d1) * math.sqrt(T) / 100
