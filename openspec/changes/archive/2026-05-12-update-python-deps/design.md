# Design: update-python-deps

## Upgrade strategy

Update in two phases to isolate risk:

```
Phase 1: Safe upgrades (minor/patch)        Phase 2: Peewee major upgrade
┌─────────────────────────────────┐          ┌─────────────────────────────┐
│ beautifulsoup4  4.12.2 → 4.14.3│          │ peewee  3.17.0 → 4.0.5     │
│ certifi     2023.11.17→2026.4.22│         │                             │
│ charset-normalizer 3.3.2→ 3.4.7│          │ Check breaking changes:     │
│ idna              3.6  → 3.14  │          │ - Model API                 │
│ python-dotenv     1.0.0→ 1.2.2 │          │ - Query syntax              │
│ requests          2.31.0→2.34.0│          │ - Database context manager   │
│ soupsieve         2.5  → 2.8.3 │          │ - create_tables behavior    │
│ urllib3           2.1.0→ 2.7.0 │          │                             │
│                                 │          │ Run tests after each change │
│ Pin dev deps:                   │          └─────────────────────────────┘
│ pytest==9.0.3                   │
│ responses==0.26.0               │
│ pytest-cov==7.1.0               │
└─────────────────────────────────┘
```

## Peewee 3→4 assessment

Key areas to check in peewee 4.x changelog:
- `Model.create()`, `Model.save()`, `Model.update()` — any signature changes
- `SqliteDatabase` constructor and `connect()` / `close()` behavior
- `create_tables()` — already changed from `with database:` wrapper
- `IntegrityError` import path
- Query API: `.where()`, `.select()`, `.dicts()`, `.order_by()`

If peewee 4.x introduces breaking changes to any of these, fix them in `db.py` and `sync.py`.

## Flake lock

After updating `requirements.txt`, run `nix flake update` to refresh `flake.lock`. The nix flake reads `requirements.txt` via `pyproject-nix`, so version changes propagate automatically.

## Verification

Run the full test suite after each phase:
```sh
pytest tests/ -v
pytest tests/ --cov=startaste --cov-report=term-missing
```
