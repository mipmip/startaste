# Design: configurable-data-locations

## Goals

- XDG-compliant default paths for CLI tool usage
- All paths overridable via env vars for daemon/service deployment
- Automatic migration from `hn.db` to `startaste.db`
- Directories created automatically on first use

## Non-goals

- Daemon/service mode implementation (future work — this just prepares the path system)
- Config file (env vars + .env is sufficient for now)
- Moving existing user's database files to XDG paths (just rename, don't relocate)

## Path resolution chain

```
Env var override         → Default (XDG CLI)              → Daemon example
─────────────────────────────────────────────────────────────────────────────
STARTASTE_DATA           → $XDG_DATA_HOME/startaste       → /var/lib/startaste
                           (~/.local/share/startaste)

STARTASTE_STATE          → $XDG_STATE_HOME/startaste      → /var/log/startaste
                           (~/.local/state/startaste)

STARTASTE_DB             → $STARTASTE_DATA/startaste.db   → /var/lib/startaste/startaste.db

STARTASTE_LOG            → $STARTASTE_STATE/startaste.log  → /var/log/startaste/startaste.log
```

## paths.py module

```python
def get_data_dir() -> Path:
    if env := os.getenv("STARTASTE_DATA"):
        return Path(env)
    xdg = os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")
    return Path(xdg) / "startaste"

def get_state_dir() -> Path:
    if env := os.getenv("STARTASTE_STATE"):
        return Path(env)
    xdg = os.getenv("XDG_STATE_HOME", Path.home() / ".local" / "state")
    return Path(xdg) / "startaste"

def get_db_path() -> Path:
    if env := os.getenv("STARTASTE_DB"):
        return Path(env)
    return get_data_dir() / "startaste.db"

def get_log_path() -> Path:
    if env := os.getenv("STARTASTE_LOG"):
        return Path(env)
    return get_state_dir() / "startaste.log"

def ensure_dirs():
    get_data_dir().mkdir(parents=True, exist_ok=True)
    get_state_dir().mkdir(parents=True, exist_ok=True)
```

## Database file migration

On startup, before opening the database, check for `hn.db` at the resolved data directory and rename:

```python
def migrate_db_file():
    db_path = get_db_path()
    old_path = db_path.parent / "hn.db"
    if old_path.exists() and not db_path.exists():
        old_path.rename(db_path)
```

Also check cwd for a stale `hn.db` if the new XDG path doesn't have a DB yet — this handles the transition from "everything in cwd" to XDG paths.

## .env loading

Unchanged — `load_dotenv()` in `sources/hn/scraper.py` loads from cwd. No `.env` files in XDG dirs.

## Backward compatibility

If `STARTASTE_DB` is explicitly set (e.g. to `hn.db` or an absolute path), the old behavior is preserved. The migration only runs when using default paths.
