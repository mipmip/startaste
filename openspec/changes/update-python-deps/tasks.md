## 1. Phase 1: Safe upgrades

- [x] 1.1 Update minor/patch versions in `requirements.txt` (beautifulsoup4, certifi, charset-normalizer, idna, python-dotenv, requests, soupsieve, urllib3)
- [x] 1.2 Pin dev dependencies (pytest==9.0.3, responses==0.26.0, pytest-cov==7.1.0)
- [x] 1.3 Run tests and verify all pass

## 2. Phase 2: Peewee major upgrade

- [x] 2.1 Review peewee 4.x changelog for breaking changes (none affect our code)
- [x] 2.2 Update peewee version in `requirements.txt`
- [x] 2.3 Fix any breaking changes in `startaste/db.py`, `startaste/sync.py`, `startaste/export.py` (none needed)
- [x] 2.4 Run tests and verify all pass

## 3. Nix flake

- [x] 3.1 Run `nix flake update` to refresh `flake.lock`
- [x] 3.2 Verify `nix develop` shell works with updated deps

## 4. Final verification

- [x] 4.1 Run full test suite with coverage
