<!-- Epic: .beans/startaste-h46w--resumable-full-sync-via-a-completion-marker.md -->

> **PARKED 2026-09-10 — do not apply.** Measurement after planning showed the
> payoff is smaller than the bean assumed: the ~13-minute metadata phase already
> resumes on its own (an interrupted run re-reported `Fetching metadata for 2245
> stories`, skipping the 43 already fetched), and only the ~40s listing walk is
> exposed. With re-walk-from-the-top as the chosen resume strategy, that 40s is
> re-spent either way, so this change buys robustness rather than speed. The
> artifacts are kept because the implicit coupling they remove
> (`is_full = story_count == 0 and comment_count == 0`) is a real fragility and a
> prerequisite for cursor resume or per-page persistence. Unpark when a listing
> walk becomes long enough to matter (~1600 pages for a 50k-item account), or
> when something else needs per-page persistence.

## Why

Tracks bean [startaste-h46w](../../../.beans/startaste-h46w--resumable-full-sync-via-a-completion-marker.md).

Sync decides between a full and an incremental walk by inferring it from the
data: `is_full = story_count == 0 and comment_count == 0` in the HN source, and
`GithubStar.count_all() == 0` in the GitHub source. Nothing records whether a
listing was ever walked to its last page, so the mode is guessed from a side
effect rather than known.

That inference is currently correct only because two unrelated properties hold
at the same time: a listing's IDs are stored atomically, so an interrupted walk
leaves no partial listing behind, and an incremental walk over an empty table
can never satisfy its stop condition, so it happens to walk to the end. Remove
either property — persist IDs per page, add a second listing to a source, add a
source whose first listing lands in a database that already has rows — and the
incremental walk stops on its first page of known IDs and silently abandons the
rest of the listing. That failure mode was observed while fixing
`fix-hn-upvoted-pagination`: 270 rows stored from 9 of 77 pages, next run walked
1 page, 2018 items left permanently unfetched.

Two measurements set the scope honestly, against a 2288-item HN account:

- The expensive phase already resumes. Interrupting the metadata fetch and
  re-running logged `Fetching metadata for 2245 stories` — the 43 rows that
  already had a body were skipped. Roughly 13 of the ~14 minutes are protected
  today.
- The exposed phase is the listing walk, ~40s (77 pages at 0.5s). Interrupting
  it stores nothing, so that time is re-spent.

This change therefore buys robustness, not speed: with re-walk-from-the-top as
the chosen resume strategy the ~40s is re-spent either way. What it removes is
the implicit coupling, so the sync mode is recorded rather than inferred, and
per-page persistence or cursor resume become safe to add later for accounts
where the walk itself is long.

## What Changes

- Record, per source and listing, whether its walk reached the last page.
- Decide the sync mode from that record instead of from row counts: a listing
  with no record, or one marked incomplete, gets a full walk; a listing marked
  complete gets an incremental walk.
- A full walk ignores the all-known stop condition and runs to the end of the
  listing (or to the page bound), so a partially walked listing is completed
  rather than truncated.
- Mark a listing complete only after its walk finished and its IDs were stored.
- Apply this to both sources: HN `stories` and `comments`, and GitHub `stars`.
- Keep per-listing atomic ID storage. Under re-walk resume, per-page
  persistence buys nothing, and atomic storage keeps a listing's rows from
  appearing before its walk finished.
- Existing databases are seeded on first run: a listing whose table already has
  rows is marked complete, preserving today's behaviour instead of forcing a
  surprise full walk on upgrade.
- The new state is not user data and MUST NOT appear in `startaste export`
  output or the dashboard.

## Capabilities

### New Capabilities
- `sync-state`: how sync records that a listing was walked to completion, and
  how the full-vs-incremental decision is derived from that record rather than
  from stored row counts. Source-agnostic — it governs HN and GitHub alike.

### Modified Capabilities
- `hn-sync`: its atomic-storage requirement currently carries the reasoning
  that atomicity is what keeps the incremental stop condition sound. That
  reasoning moves to `sync-state`; the requirement itself stays, restated
  without it, plus HN listings now record completion.

## Impact

- `startaste/db.py`: new model for the state, registered so
  `create_tables()`/`migrate_tables()` cover it; the seeding step for existing
  databases.
- `startaste/sources/base.py`: the `Source` protocol gains the notion of named
  listings, so the state can be keyed per listing rather than per source.
- `startaste/sources/hn/__init__.py`: `_sync_type` takes its mode from the
  state; `_scrape_all` / `_scrape_incremental` selection and the completion
  write.
- `startaste/sources/github/__init__.py`: same, replacing
  `is_full = GithubStar.count_all() == 0`.
- `startaste/export.py` and the dashboard service layer: must keep iterating
  source models only, so the state table stays out of exports and views.
- `tests/`: mode selection per listing, completion written only on a finished
  walk, a full walk not stopping on known pages, seeding of an existing
  database, and export output unchanged.
- No CLI surface change, no new dependency. Not breaking: `startaste sync`
  behaves the same on a complete database and on a fresh one.
