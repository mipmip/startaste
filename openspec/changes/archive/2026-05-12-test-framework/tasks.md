## 1. Dependencies

- [x] 1.1 Add `pytest`, `responses`, and `pytest-cov` to dev dependencies in `requirements.txt`

## 2. Test infrastructure

- [x] 2.1 Create `tests/conftest.py` with in-memory DB fixture (`database.init(":memory:")`)
- [x] 2.2 Add `time.sleep` monkeypatch fixture (autouse)
- [x] 2.3 Add fixture helper to load files from `tests/fixtures/`

## 3. HTML/JSON fixtures

- [x] 3.1 Create `tests/fixtures/hn_stories_page1.html` — 3 stories with known IDs
- [x] 3.2 Create `tests/fixtures/hn_stories_page2.html` — 2 more stories
- [x] 3.3 Create `tests/fixtures/hn_stories_empty.html` — empty page (no matching elements)
- [x] 3.4 Create `tests/fixtures/hn_comments_page1.html` — 2 comments with known IDs
- [x] 3.5 Create `tests/fixtures/hn_login_success.html` — response containing username
- [x] 3.6 Create `tests/fixtures/hn_login_failure.html` — response containing "Bad login"
- [x] 3.7 Create `tests/fixtures/hn_item_11111.json` — story item
- [x] 3.8 Create `tests/fixtures/hn_item_44444.json` — comment item

## 4. Export tests

- [x] 4.1 Create `tests/test_export.py` with tests for: data, empty DB, story filter, comment filter, file output, stdout output

## 5. Scraper tests

- [x] 5.1 Create `tests/test_scraper.py` with tests for: login success, login failure, scrape stories, scrape comments, pagination stop, get_item

## 6. Sync integration tests

- [x] 6.1 Create `tests/test_sync.py` with tests for: full sync, incremental sync, incremental stop condition

## 7. Verify

- [x] 7.1 Run full test suite and verify all tests pass
- [x] 7.2 Run with coverage and verify report is generated
