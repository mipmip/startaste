## 1. State model

- [ ] 1.1 Add a `SyncState` model in `startaste/db.py` keyed by `source` +
      `listing` with `complete` and `updated_at`, unique on the pair, and
      register it for creation in `_get_all_models()` without adding it to any
      source's `models`; verify `startaste export` output on a synced database
      is byte-identical to the same export before the change
- [ ] 1.2 Add read/write helpers (`is_complete(source, listing)`,
      `mark_complete(source, listing)`) and verify with a unit test that
      marking is idempotent and that an unknown pair reads as not complete

## 2. Listings on the source protocol

- [ ] 2.1 Add `listings` to `Source` in `startaste/sources/base.py` as the
      listing names paired with the model each fills, keeping it separate from
      `item_types`; verify both sources expose it and that `item_types` is
      untouched (export tests still pass)
- [ ] 2.2 Declare `["stories", "comments"]` on the HN source and `["stars"]` on
      the GitHub source; verify a test asserts every declared listing maps to a
      model the source owns

## 3. Mode selection and completion

- [ ] 3.1 Replace HN's `is_full = story_count == 0 and comment_count == 0` with
      a per-listing lookup, and write the completion record after the IDs are
      stored; verify tests covering stories-complete/comments-unwalked and
      comments-interrupted-after-stories-complete from the `hn-sync` delta
- [ ] 3.2 Make a full walk ignore the all-known stop condition and run to the
      end of the listing; verify a test where a listing recorded incomplete
      already holds its first page's IDs walks every page and stores no
      duplicates
- [ ] 3.3 Replace GitHub's `is_full = GithubStar.count_all() == 0` with the same
      lookup and completion write; verify a test that a `stars` listing
      recorded incomplete is re-paged in full
- [ ] 3.4 Ensure no completion record is written when a walk raises or stops at
      the page bound; verify a test that injects a failure mid-walk and asserts
      the listing is still not complete

## 4. Seeding existing databases

- [ ] 4.1 In `migrate_tables()`, when the state table is empty, seed
      `complete = 1` for every listing whose model already has rows, before any
      source reads the state; verify a test that a pre-change database with rows
      and no records is seeded complete and then walks incrementally
- [ ] 4.2 Verify a test that a pre-change database with no rows is not seeded
      and walks in full, and that a second run does not re-derive seeded records
      from row counts

## 5. Verification

- [ ] 5.1 `pytest tests/ -v` passes and `nix build .#default` succeeds
- [ ] 5.2 Live check against the real HN account into a throwaway
      `STARTASTE_DB`: interrupt the stories walk, confirm the listing is not
      recorded complete and no rows were stored, then re-run and confirm it
      walks in full to the end and is recorded complete
- [ ] 5.3 Live check that a completed database walks 1 page on the next run
      (incremental), and that `startaste export` and `startaste serve` show no
      trace of the state table
- [ ] 5.4 Update CHANGELOG.md under Unreleased, including the one-line SQL to
      reset a listing (`update sync_state set complete = 0 where source = '…'`)
      as the documented way to force a re-walk
