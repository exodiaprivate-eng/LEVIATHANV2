"""Historical data storage using Parquet files via Polars."""
import logging
from pathlib import Path
from datetime import datetime

import polars as pl

logger = logging.getLogger('leviathan.parquet')

DATA_DIR = Path(__file__).parent.parent.parent / 'data_files'
DATA_DIR.mkdir(exist_ok=True)


class ParquetManager:
    """Manage historical OHLCV data in Parquet format."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or DATA_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, symbol: str) -> Path:
        return self.base_dir / f"{symbol.replace('/', '_')}.parquet"

    def save_bars(self, symbol: str, df):
        """Save DataFrame (pandas or polars) to parquet."""
        path = self._path(symbol)
        if hasattr(df, 'to_pandas'):
            pldf = pl.from_pandas(df.reset_index() if hasattr(df.index, 'names') else df)
        elif isinstance(df, pl.DataFrame):
            pldf = df
        else:
            pldf = pl.from_pandas(df)
        pldf.write_parquet(path)
        logger.info(f"Saved {len(pldf)} bars for {symbol}")

    def load_bars(self, symbol: str) -> pl.DataFrame:
        path = self._path(symbol)
        if not path.exists():
            logger.warning(f"No data for {symbol}")
            return pl.DataFrame()
        return pl.read_parquet(path)

    def update_bars(self, symbol: str, new_bars):
        """Append new bars, deduplicate by timestamp."""
        existing = self.load_bars(symbol)
        if hasattr(new_bars, 'to_pandas'):
            new_pl = pl.from_pandas(new_bars.reset_index() if hasattr(new_bars.index, 'names') else new_bars)
        elif isinstance(new_bars, pl.DataFrame):
            new_pl = new_bars
        else:
            new_pl = pl.from_pandas(new_bars)

        if existing.is_empty():
            combined = new_pl
        else:
            combined = pl.concat([existing, new_pl]).unique(subset=['timestamp'] if 'timestamp' in existing.columns else None)
        self.save_bars(symbol, combined)

    def get_available_symbols(self) -> list[str]:
        return [p.stem.replace('_', '/') for p in self.base_dir.glob('*.parquet')]

    def delete_symbol(self, symbol: str):
        path = self._path(symbol)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted data for {symbol}")
