# Design: test-framework

## Architecture

```
  Test tiers:

  1. Export (no mocks)          2. Scraper (mocked HTTP)       3. Sync (integration)
  ┌──────────────────┐          ┌──────────────────────┐       ┌─────────────────────┐
  │ test_export.py   │          │ test_scraper.py      │       │ test_sync.py        │
  │                  │          │                      │       │                     │
  │ Real SQLite      │          │ responses library    │       │ responses library   │
  │ (:memory:)       │          │ + HTML/JSON fixtures │       │ + Real SQLite       │
  │                  │          │                      │       │ (:memory:)          │
  │ No network       │          │ No network           │       │ No network          │
  │ No mocks         │          │ Full Req class runs  │       │ Full sync flow      │
  └──────────────────┘          └──────────────────────┘       └─────────────────────┘
```

## Database isolation

Peewee's `SqliteDatabase` is created at module import time in `db.py`. Tests re-initialize it to `:memory:` using peewee's `database.init()`:

```python
@pytest.fixture(autouse=True)
def tmp_database():
    from startaste.db import database, create_tables
    database.init(":memory:")
    create_tables()
    yield
    database.close()
```

This runs before every test, giving each test a fresh empty database. No env var tricks needed.

## HTTP mocking with `responses`

The `responses` library patches `requests.Session` at the transport level. The `Req` class runs unmodified — session creation, headers, retries all execute as normal, but actual HTTP calls are intercepted.

```python
@responses.activate
def test_scrape_stories():
    responses.get(
        "https://news.ycombinator.com/upvoted?id=testuser&p=1",
        body=open("tests/fixtures/hn_stories_page1.html").read(),
    )
    responses.get(
        "https://news.ycombinator.com/upvoted?id=testuser&p=2",
        body=open("tests/fixtures/hn_stories_empty.html").read(),
    )
    req = Req()
    ids = req.get_upvoted_stories("testuser", max_page=10)
    assert ids == ["11111", "22222", "33333"]
```

## HTML fixtures

Hand-crafted minimal HTML that matches HN's structure. Only the elements BeautifulSoup needs:

**Stories** — `<td class="subtext">` with `<a href="item?id=...">`:
```html
<html><body><table>
  <tr><td class="subtext">
    <span class="score" id="score_11111">42 points</span>
    <a href="user?id=someone">someone</a>
    <a href="item?id=11111">13 comments</a>
  </td></tr>
</table></body></html>
```

**Comments** — `<td class="default">` with `<a href="item?id=...">`:
```html
<html><body><table>
  <tr><td class="default">
    <a href="item?id=44444">link</a>
  </td></tr>
</table></body></html>
```

**Empty page** — valid HTML with no matching elements (triggers pagination stop).

**Login success** — response containing the username string.

**Login failure** — response containing "Bad login".

## JSON fixtures for HN API

Minimal item objects matching what `get_item` returns:

```json
{
  "id": 11111,
  "type": "story",
  "by": "testuser",
  "time": 1700000000,
  "title": "Test Story",
  "url": "https://example.com",
  "score": 42,
  "descendants": 13
}
```

## Sleep patching

`time.sleep` is patched globally in conftest to avoid 0.5s/0.2s waits:

```python
@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
```

## Coverage

Run with: `pytest --cov=startaste --cov-report=term-missing`

No minimum threshold enforced initially — the goal is visibility, not a gate.

## Dependencies

Add to dev dependencies (not runtime):
- `pytest`
- `responses`
- `pytest-cov`
