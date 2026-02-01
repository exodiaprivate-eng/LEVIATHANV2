"""LLM usage settings and budget management."""

LLM_CONFIG = {
    'decision_model': 'claude-opus-4-5-20250514',
    'utility_model': 'claude-sonnet-4-20250514',
    'daily_budget_usd': 5.00,
    'max_opus_calls_per_day': 50,
    'opus_cost_per_call': 0.08,
    'sonnet_cost_per_call': 0.01,
    'use_opus_for': ['trade_decisions', 'exit_decisions', 'position_sizing', 'daily_analysis'],
    'use_sonnet_for': ['trade_logging', 'report_generation', 'simple_summaries'],
}


class LLMBudgetTracker:
    """Track daily LLM API spending."""

    def __init__(self):
        self.daily_calls = 0
        self.daily_cost = 0.0
        self.opus_calls = 0
        self.sonnet_calls = 0

    def record_call(self, model: str, estimated_cost: float = None):
        if 'opus' in model.lower():
            cost = estimated_cost or LLM_CONFIG['opus_cost_per_call']
            self.opus_calls += 1
        else:
            cost = estimated_cost or LLM_CONFIG['sonnet_cost_per_call']
            self.sonnet_calls += 1
        self.daily_calls += 1
        self.daily_cost += cost

    def can_call_opus(self) -> bool:
        return (self.opus_calls < LLM_CONFIG['max_opus_calls_per_day']
                and self.daily_cost < LLM_CONFIG['daily_budget_usd'])

    def reset_daily(self):
        self.daily_calls = 0
        self.daily_cost = 0.0
        self.opus_calls = 0
        self.sonnet_calls = 0

    def get_stats(self) -> dict:
        return {
            'daily_calls': self.daily_calls,
            'daily_cost': self.daily_cost,
            'opus_calls': self.opus_calls,
            'sonnet_calls': self.sonnet_calls,
            'budget_remaining': LLM_CONFIG['daily_budget_usd'] - self.daily_cost,
            'opus_calls_remaining': LLM_CONFIG['max_opus_calls_per_day'] - self.opus_calls,
        }
