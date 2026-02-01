"""Backup and recovery for databases and state."""
import shutil
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('leviathan.backup')

BACKUP_DIR = Path(__file__).parent.parent / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)


class BackupManager:
    """Automatic backup of databases."""

    def __init__(self, db_paths: list = None, max_backups: int = 30):
        self.db_paths = db_paths or ['leviathan_state.db', 'leviathan_learning.db']
        self.max_backups = max_backups

    def backup_databases(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        for db in self.db_paths:
            src = Path(db)
            if src.exists():
                dst = BACKUP_DIR / f"{src.stem}_{ts}{src.suffix}"
                shutil.copy2(src, dst)
                logger.info(f"Backed up {src} -> {dst}")
        self._cleanup()

    def restore_from_backup(self, backup_name: str):
        src = BACKUP_DIR / backup_name
        if not src.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")
        # Determine original name
        parts = src.stem.rsplit('_', 2)
        original = parts[0] + src.suffix
        shutil.copy2(src, original)
        logger.info(f"Restored {src} -> {original}")

    def _cleanup(self):
        backups = sorted(BACKUP_DIR.glob('*.db'), key=lambda p: p.stat().st_mtime)
        while len(backups) > self.max_backups:
            old = backups.pop(0)
            old.unlink()
            logger.info(f"Removed old backup: {old}")

    def list_backups(self) -> list:
        return sorted([p.name for p in BACKUP_DIR.glob('*.db')])
