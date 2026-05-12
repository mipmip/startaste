# Design: local-dashboard

## Goals

- Browse synced data in a clean local web UI
- Separate data queries from presentation for future API reuse
- Minimal dependencies (Flask + Jinja, no JS frameworks)
- Tangled.org-inspired aesthetic: clean, neutral, content-first

## Non-goals

- REST API (future work — service layer prepares for it)
- Authentication (local-only, no auth needed)
- Write operations (dashboard is read-only)
- Real-time updates / WebSocket (just refresh the page)

## Architecture

```
startaste/dashboard/
├── __init__.py         ← Flask app factory: create_app()
├── views.py            ← HTML routes → call services → render templates
├── services.py         ← data queries → return dicts
├── templates/
│   ├── base.html       ← layout: header, nav, content slot
│   ├── index.html      ← overview of all sources
│   ├── hn.html         ← HN stories + comments listing
│   └── github.html     ← GitHub stars listing
└── static/
    └── style.css       ← minimal CSS, system fonts, tangled-inspired
```

## Service layer

Functions return plain dicts. Views render them as HTML. Future API returns them as JSON.

```python
# services.py

def get_overview() -> dict:
    # {sources: [{name, configured, story_count, comment_count, star_count, last_sync}]}

def get_hn_stories(page=1, per_page=50) -> dict:
    # {items: [...], total: N, page: N, per_page: N, pages: N}

def get_hn_comments(page=1, per_page=50) -> dict:
    # {items: [...], total: N, page: N, per_page: N, pages: N}

def get_github_stars(page=1, per_page=50) -> dict:
    # {items: [...], total: N, page: N, per_page: N, pages: N}
```

## Routes

```
GET /                → index.html    (overview cards per source)
GET /hn              → hn.html       (stories listing, paginated)
GET /hn/comments     → hn.html       (comments listing, paginated)
GET /github          → github.html   (stars listing, paginated)
```

Pagination via query params: `?page=2`

## Page content

### / (index)

Source cards showing:
- Source name + icon/emoji
- Configured status
- Item counts (e.g. "423 stories, 89 comments")
- Last synced timestamp (from most recent item)

### /hn

- Stats header: total stories, total comments
- Story listing table/cards:
  - Title (linked to HN item)
  - URL domain
  - Score, author, date
  - Comment count

### /hn/comments

- Comment listing:
  - Comment text (truncated)
  - Parent story link
  - Author, date

### /github

- Stats header: total starred repos
- Repo listing:
  - owner/repo (linked to GitHub)
  - Description
  - Language badge
  - Star count
  - Starred date

## Styling

Tangled.org-inspired: system font stack, generous whitespace, subtle borders, neutral palette with light/dark via `prefers-color-scheme`. No CSS framework — a single `style.css` of ~150 lines.

## CLI command

```
startaste serve [--port PORT]
```

- Default port: 8421
- Starts Flask development server
- Opens on `http://localhost:8421`
- Ctrl+C to stop

## Flask app factory

```python
def create_app():
    app = Flask(__name__)
    from startaste.dashboard.views import bp
    app.register_blueprint(bp)
    return app
```

The app factory pattern allows testing the Flask app without starting a server.

## Database access

The dashboard reads from the same SQLite database via the existing peewee models. `init_database()` is called before creating the Flask app. Flask runs in the same process — no connection pooling needed.
