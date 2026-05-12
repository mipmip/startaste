# Test Framework with HN Website Mockups

**Bean:** startaste-iapd

## Summary

Add a pytest test suite with three tiers: export tests against real SQLite (no mocks), scraper tests with mocked HTTP using the `responses` library and hand-crafted HTML fixtures, and sync integration tests combining mocked HTTP with a real in-memory database. Include coverage reporting via `pytest-cov`.

## Why

- No tests exist — changes to the scraper or sync logic can't be verified without hitting real HN
- HN's HTML structure is fragile — a markup change could silently break parsing
- The sync auto-detection (full vs incremental) has subtle stop conditions that need regression coverage
- The recent `saved_stories`/`saved_comments` bug (startaste-1r78) would have been caught by export tests

## What changes

- Add `tests/` directory with conftest, fixtures, and test modules
- Add hand-crafted HTML fixtures mimicking HN's upvoted pages
- Add JSON fixtures for HN API item responses
- Add `responses` and `pytest-cov` to dev dependencies
- Patch `time.sleep` in tests for speed

## Scope

```
  tests/
  ├── conftest.py              ← in-memory DB, sleep patch, shared helpers
  ├── fixtures/
  │   ├── hn_stories_page1.html
  │   ├── hn_stories_page2.html
  │   ├── hn_stories_empty.html
  │   ├── hn_comments_page1.html
  │   ├── hn_login_success.html
  │   ├── hn_login_failure.html
  │   └── hn_item_*.json
  ├── test_export.py           ← real SQLite, no mocks
  ├── test_scraper.py          ← responses library, HTML fixtures
  └── test_sync.py             ← responses + real SQLite, integration
```

## Capabilities

- **testing** — pytest suite with HTTP fixtures, coverage reporting, test isolation

## Non-goals

- Testing against live HN (that's manual/smoke testing)
- Testing the flake.nix packaging
- E2E tests with real credentials
- CI/CD integration (local-only for now)
