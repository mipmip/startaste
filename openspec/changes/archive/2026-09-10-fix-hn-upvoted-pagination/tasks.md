## 1. Implementation

- [x] 1.1 In `startaste/sources/hn/scraper.py`, replace the `p=<n>` page counter
      in `scrape_ids` with cursor traversal: parse the `More` link from each
      page and request its href; stop when no `More` link is present
- [x] 1.3 Apply the same cursor traversal to `_scrape_incremental` in
      `startaste/sources/hn/__init__.py`, keeping its stop-when-all-known
      behaviour
- [x] 1.4 Keep ID storage atomic per listing (`model.save_ids` after the scrape
      returns) — verification showed per-page saving silently truncates the
      sync, see the note below
- [x] 1.5 Replace `VERY_HIGH_PAGE = 10000` with a real bound and log a warning
      when it is hit
- [x] 1.6 Re-record the HN fixtures so they match real pages: a `More` link with
      `next`/`n`/`time` on `hn_stories_page1.html`, a last page without one, and
      the real comment markup (`span.age` permalink plus `parent` / `context` /
      `on:` links) in `hn_comments_page1.html` (the current fixtures are 847 and
      317 byte miniatures with none of it)
- [x] 1.7 Update `tests/test_scraper.py` and `tests/test_sync.py` to mock the
      cursor URLs instead of `?p=1/2/3`, and add regression tests: traversal
      stops when no `More` link is present, the page bound warns, context links
      yield no `#` IDs, and a failure mid-walk stores nothing

## 2. Verification

- [x] 2.1 Full sync into a throwaway database (`STARTASTE_DB=…`) completes
      instead of looping: `startaste sync hn` terminates, and `hn_story` /
      `hn_comment` row counts are non-zero
- [x] 2.2 Assert stored IDs are well formed: no `_id` in `hn_story` /
      `hn_comment` contains a `#`, and each table's IDs are distinct
- [x] 2.3 Second run of `startaste sync hn` on the populated database performs
      an incremental sync and stops on the first page of known IDs
- [x] 2.4 `pytest tests/ -v` passes, including the new regression tests
- [x] 2.5 Interrupt a full sync mid-scrape and confirm the database is left
      empty, so the next run still takes the full path

## Notes

- Schema source: https://github.com/speclib/openspec-tinychange-schema
- Diagnosis: HN returns byte-identical content for `/upvoted?id=<user>&p=1`,
  `&p=2` and `&p=233` (39567 bytes, same first item). `scrape_ids` only exits on
  an empty page, which therefore never happens, and `save_ids` runs after the
  loop — so a full sync spins to `VERY_HIGH_PAGE` and stores nothing. Real
  pagination is the `More` href:
  `upvoted?id=<user>&next=<id>&n=31&time=<token>`; following it yielded 30 IDs
  with zero overlap with page 1.
- Comment ID extraction is NOT broken, contrary to an earlier reading of the
  page: the production loop breaks after the first `item?` link per row, so a
  real page yields 26 IDs for 26 comments, all unique, none malformed, exactly
  matching the `tr.athing` row ids. (The 104-ID count came from a probe script
  that omitted that `break`.) The rewritten extractor must preserve this, which
  is why the re-recorded comment fixture keeps the `parent` / `context` / `on:`
  links and a test pins one ID per row.
- The existing tests mock `?p=1`, `?p=2`, `?p=3` and terminate on a fixture
  named `hn_stories_empty.html`, so all 65 tests pass against pagination
  behaviour Hacker News does not have. Fixing the fixtures is part of the fix,
  not a follow-up.
- Provenance — this is a StarTaste regression, not an HN change. `?p=` still
  paginates public listings (`/news`, `/news?p=2`, `/news?p=3` return three
  different pages), but user-private listings like `/upvoted` have always used
  the `More` cursor: the 2012 original (`d2bba23`, `hn2pin.py`) explicitly
  skipped that link. The `p=`-based loop came from the 2023 rewrite
  (`29533fd`), where `-n/--number` defaulted to 1 page, so re-requesting page 1
  never happened and the wrong mechanism stayed invisible. `d20584e`
  (cli restructure) replaced that count with `VERY_HIGH_PAGE = 10000`, turning a
  latent bug into a hang. The page bound in task 1.5 is what would have made
  this fail loudly instead.
- Per-page persistence (the original task 1.4) was implemented, verified, and
  then reversed: interrupting a full sync after 9 of 77 pages left 270 rows, and
  because the database was then non-empty the next run took the incremental
  path, stopped on page 1 as all-known, and left the remaining 2018 items
  permanently unfetched. Atomic per-listing storage keeps the incremental stop
  condition sound. The scrape is ~40s of the sync, so little is lost; the long
  metadata phase already resumes on its own via `list_empty`. A completion
  marker would allow both, but that needs new state and is out of scope here.
- New capability `hn-sync`: HN scraping requirements live in the archived
  `sync` capability (`2026-05-12-cli-restructure`), whose text predates the
  source-plugin split and is stale in ways this change should not have to
  reconcile. Pagination behaviour is specified here instead.
