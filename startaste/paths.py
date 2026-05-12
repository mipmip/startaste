from __future__ import annotations

import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


def get_data_dir() -> Path:
    if env := os.getenv("STARTASTE_DATA"):
        return Path(env)
    xdg = os.getenv("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(xdg) / "startaste"


def get_state_dir() -> Path:
    if env := os.getenv("STARTASTE_STATE"):
        return Path(env)
    xdg = os.getenv("XDG_STATE_HOME", str(Path.home() / ".local" / "state"))
    return Path(xdg) / "startaste"


def get_db_path() -> Path:
    if env := os.getenv("STARTASTE_DB"):
        return Path(env)
    return get_data_dir() / "startaste.db"


def get_log_path() -> Path:
    if env := os.getenv("STARTASTE_LOG"):
        return Path(env)
    return get_state_dir() / "startaste.log"


def ensure_dirs() -> None:
    get_data_dir().mkdir(parents=True, exist_ok=True)
    get_state_dir().mkdir(parents=True, exist_ok=True)


def migrate_db_file() -> None:
    db_path = get_db_path()

    # Check for hn.db in the data directory
    old_in_data = db_path.parent / "hn.db"
    if old_in_data.exists() and not db_path.exists():
        log.info(f"Migrating database: {old_in_data} → {db_path}")
        old_in_data.rename(db_path)
        return

    # Check for hn.db in cwd (legacy location)
    old_in_cwd = Path.cwd() / "hn.db"
    if old_in_cwd.exists() and not db_path.exists() and old_in_cwd != old_in_data:
        log.info(f"Moving legacy database: {old_in_cwd} → {db_path}")
        old_in_cwd.rename(db_path)
