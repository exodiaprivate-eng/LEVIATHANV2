"""LLM integration utilities wrapping Anthropic API."""
import json
import logging
from config.llm_config import LLMBudgetTracker, LLM_CONFIG

from anthropic import Anthropic

logger = logging.getLogger('leviathan.llm')


class LLMReasoner:
    """Utility wrapper for LLM API calls with budget tracking."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.budget = LLMBudgetTracker()

    def query_opus(self, prompt: str, system: str = None, max_tokens: int = 1000) -> str:
        if not self.budget.can_call_opus():
            logger.warning("Opus budget exceeded, falling back to Sonnet")
            return self.query_sonnet(prompt, system, max_tokens)
        msgs = [{'role': 'user', 'content': prompt}]
        kwargs = {'model': LLM_CONFIG['decision_model'], 'max_tokens': max_tokens, 'messages': msgs}
        if system:
            kwargs['system'] = system
        resp = self.client.messages.create(**kwargs)
        self.budget.record_call(LLM_CONFIG['decision_model'])
        return resp.content[0].text

    def query_sonnet(self, prompt: str, system: str = None, max_tokens: int = 1000) -> str:
        msgs = [{'role': 'user', 'content': prompt}]
        kwargs = {'model': LLM_CONFIG['utility_model'], 'max_tokens': max_tokens, 'messages': msgs}
        if system:
            kwargs['system'] = system
        resp = self.client.messages.create(**kwargs)
        self.budget.record_call(LLM_CONFIG['utility_model'])
        return resp.content[0].text

    def parse_json_response(self, text: str) -> dict:
        clean = text.strip()
        if clean.startswith('```'):
            clean = clean.split('```')[1]
            if clean.startswith('json'):
                clean = clean[4:]
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {'error': 'parse_failed', 'raw': text[:500]}
