"""Logging configuration for Leviathan."""
import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(level='INFO'):
