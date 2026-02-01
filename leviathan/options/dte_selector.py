"""DTE selection for optimal options expiration."""
from datetime import datetime


class DTESelector:
    """Select optimal expiration date for options trades."""
    MIN_DTE = 21
    MAX_DTE = 45
    IDEAL_DTE = 35

    @staticmethod
    def select_expiration(chain: dict, strategy: str) -> dict:
        available = chain.get('expirations', [])
        today = datetime.now().date()
        valid = []
        for exp in available:
            exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
            dte = (exp_date - today).days
            if DTESelector.MIN_DTE <= dte <= DTESelector.MAX_DTE:
                valid.append({'expiration': exp, 'dte': dte,
                              'score': DTESelector._score(dte, strategy)})
        if not valid:
            return {'error': 'No valid expirations in 21-45 DTE range'}
        valid.sort(key=lambda x: x['score'], reverse=True)
        return valid[0]

    @staticmethod
    def _score(dte: int, strategy: str) -> float:
        base = 1.0 - abs(dte - DTESelector.IDEAL_DTE) / 30
        if strategy in ('credit_spread', 'iron_condor') and 30 <= dte <= 45:
            base += 0.1
        elif strategy == 'debit_spread' and 21 <= dte <= 35:
            base += 0.1
        return base
