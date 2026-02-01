"""
LEVIATHAN - Autonomous AI Trading System
Main entry point - launches the GUI application.
"""
import os
import sys
from dotenv import load_dotenv


def main():
    load_dotenv()

    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    if not all([alpaca_key, alpaca_secret, anthropic_key]):
        print("ERROR: Missing API keys. Check your .env file.")
        print("Required: ALPACA_API_KEY, ALPACA_SECRET_KEY, ANTHROPIC_API_KEY")
        sys.exit(1)

    paper_mode = os.getenv('PAPER_MODE', 'true').lower() == 'true'
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
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
    ╚═══════════════════════════════════════════════════════════════╝

    Mode: {'PAPER TRADING' if paper_mode else 'LIVE TRADING'}
    Starting Capital: ${starting_capital:,.2f}
    Debug: {debug}
    """)

    print("Initializing components...")

    from data.storage.learning_db import LearningDatabase
    from data.storage.state_db import StateManager
    from data.ingestion.alpaca_client import AlpacaClient
    from risk.risk_manager import RiskManager
    from intelligence.opus_brain import OpusTradingBrain
    from strategy.signals import SignalGenerator
    from execution.stock_exit_manager import StockExitManager
    from execution.autonomous_executor import AutonomousExecutor
    from core.orchestrator import Orchestrator
    from gui.app import launch_gui

    learning_db = LearningDatabase()
    state_db = StateManager()

    alpaca = AlpacaClient(api_key=alpaca_key, secret_key=alpaca_secret, paper=paper_mode)
    risk_manager = RiskManager(account_value=starting_capital)
    opus_brain = OpusTradingBrain(api_key=anthropic_key, learning_db=learning_db, risk_manager=risk_manager)
    signal_gen = SignalGenerator()
    exit_manager = StockExitManager(alpaca, state_db)
    executor = AutonomousExecutor(alpaca, opus_brain, risk_manager, learning_db)

    trading_engine = Orchestrator(
        alpaca_client=alpaca, opus_brain=opus_brain, risk_manager=risk_manager,
        signal_generator=signal_gen, learning_db=learning_db, state_db=state_db,
        exit_manager=exit_manager, executor=executor, paper_mode=paper_mode,
    )

    print("Components initialized!")
    print("Launching GUI...")

    launch_gui(trading_engine=trading_engine, learning_db=learning_db,
               state_db=state_db, debug=debug)


if __name__ == "__main__":
    main()
