"""
Credential management - loads API keys from environment variables.
Never hardcode keys here. Use .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Required
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Paper mode (default True for safety)
ALPACA_PAPER = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

# Optional
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')

# Email notifications
SMTP_EMAIL = os.getenv('SMTP_EMAIL', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# Live trading guard
LEVIATHAN_LIVE = os.getenv('LEVIATHAN_LIVE', 'false').lower() == 'true'


def validate_required_keys() -> tuple[bool, list[str]]:
    """Check that all required API keys are set."""
    missing = []
    if not ALPACA_API_KEY:
        missing.append('ALPACA_API_KEY')
    if not ALPACA_SECRET_KEY:
        missing.append('ALPACA_SECRET_KEY')
    if not ANTHROPIC_API_KEY:
        missing.append('ANTHROPIC_API_KEY')
    return len(missing) == 0, missing
