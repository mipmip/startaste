## 1. Bug fix

- [ ] 1.1 Fix `json_items["saved_stories"]` → `json_items["saved_comments"]` on line 291 (bean startaste-1r78)

## 2. Project structure

- [ ] 2.1 Restructure `hn2json.py` into a package with a `startaste` entrypoint
- [ ] 2.2 Set up argparse with subcommand dispatch (`sync`, `export`)
- [ ] 2.3 Update `flake.nix` to install `startaste` as a binary

## 3. Sync command

- [ ] 3.1 Extract sync logic from `main()` into sync subcommand handler
- [ ] 3.2 Implement auto-detection: full sync when DB is empty, incremental otherwise
- [ ] 3.3 Implement incremental stop condition: stop scraping when all IDs on a page are already known
- [ ] 3.4 Remove `-n` (number of pages) flag — sync always does the right thing

## 4. Export command

- [ ] 4.1 Extract export logic into export subcommand handler
- [ ] 4.2 Add `--format` flag with `json` as default
- [ ] 4.3 Add `-s` flag to filter by story/comment/both
- [ ] 4.4 Add `-f` flag for file output, default to stdout
- [ ] 4.5 Ensure JSON output uses separate `saved_stories` and `saved_comments` keys

## 5. Documentation

- [ ] 5.1 Update README with new CLI usage (`startaste sync`, `startaste export`)
