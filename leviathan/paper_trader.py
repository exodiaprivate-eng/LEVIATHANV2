"""CLI paper trading runner - no GUI."""
import os
import sys
import argparse
from dotenv import load_dotenv


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Leviathan Paper Trader (CLI)')
    parser.add_argument('--interval', type=int, default=60, help='Seconds between cycles')
    args = parser.parse_args()

    from data.storage.learning_db import LearningDatabase
    from data.storage.state_db import StateManager
    from data.ingestion.alpaca_client import AlpacaClient
    from risk.risk_manager import RiskManager
    from intelligence.opus_brain import OpusTradingBrain
    from strategy.signals import SignalGenerator
    from core.orchestrator import Orchestrator

    alpaca = AlpacaClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), paper=True)
    learning_db = LearningDatabase()
    state_db = StateManager()
    risk = RiskManager(account_value=float(os.getenv('STARTING_CAPITAL', '500')))
    opus = OpusTradingBrain(os.getenv('ANTHROPIC_API_KEY'), learning_db, risk)

    engine = Orchestrator(alpaca, opus, risk, SignalGenerator(), learning_db, state_db, paper_mode=True)
    print("Paper trading started. Press Ctrl+C to stop.")
    try:
        engine.run(interval_seconds=args.interval)
    except KeyboardInterrupt:
        engine.stop()
        print("Stopped.")


if __name__ == "__main__":
    main()
