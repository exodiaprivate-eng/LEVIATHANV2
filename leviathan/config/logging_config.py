"""Logging configuration for Leviathan."""
import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(level='INFO'):
    """Configure root and leviathan loggers with console + rotating file handlers."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates on re-init
    root.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(numeric_level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # Rotating file handler - 5 MB per file, keep 5 backups
    log_file = LOG_DIR / 'leviathan.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Error-only file handler for quick diagnosis
    error_file = LOG_DIR / 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root.addHandler(error_handler)

    # Quieten noisy third-party loggers
    for noisy in ('urllib3', 'httpcore', 'httpx', 'alpaca', 'websockets'):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger('leviathan').info("Logging initialised at %s level", level)
