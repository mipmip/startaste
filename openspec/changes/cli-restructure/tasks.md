## 1. Bug fix

- [x] 1.1 Fix `json_items["saved_stories"]` → `json_items["saved_comments"]` on line 291 (bean startaste-1r78)

## 2. Project structure

- [x] 2.1 Restructure `hn2json.py` into a package with a `startaste` entrypoint
- [x] 2.2 Set up argparse with subcommand dispatch (`sync`, `export`)
- [x] 2.3 Update `flake.nix` to install `startaste` as a binary

## 3. Sync command

- [x] 3.1 Extract sync logic from `main()` into sync subcommand handler
- [x] 3.2 Implement auto-detection: full sync when DB is empty, incremental otherwise
- [x] 3.3 Implement incremental stop condition: stop scraping when all IDs on a page are already known
- [x] 3.4 Remove `-n` (number of pages) flag — sync always does the right thing

## 4. Export command

- [x] 4.1 Extract export logic into export subcommand handler
- [x] 4.2 Add `--format` flag with `json` as default
- [x] 4.3 Add `-s` flag to filter by story/comment/both
- [x] 4.4 Add `-f` flag for file output, default to stdout
- [x] 4.5 Ensure JSON output uses separate `saved_stories` and `saved_comments` keys

## 5. Documentation

- [x] 5.1 Update README with new CLI usage (`startaste sync`, `startaste export`)
