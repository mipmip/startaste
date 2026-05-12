## ADDED Requirements

### Requirement: Service functions return plain dicts
All data query functions SHALL return plain Python dicts, not ORM objects or HTML.

#### Scenario: Overview data
- **WHEN** `get_overview()` is called
- **THEN** it returns a dict with source names, item counts, and last sync timestamps

#### Scenario: Paginated listing
- **WHEN** `get_hn_stories(page=2, per_page=50)` is called
- **THEN** it returns a dict with `items`, `total`, `page`, `per_page`, and `pages` keys

### Requirement: Service layer is reusable
The service functions SHALL be usable by both HTML views and a future API without modification.

#### Scenario: Same function, different consumer
- **WHEN** a view calls `get_github_stars()`
- **THEN** it gets the same dict structure that a future API route would use

### Requirement: Pagination support
All listing functions SHALL support `page` and `per_page` parameters.

#### Scenario: First page
- **WHEN** `get_hn_stories(page=1, per_page=50)` is called with 120 total stories
- **THEN** it returns 50 items, `total=120`, `pages=3`

#### Scenario: Last page
- **WHEN** `get_hn_stories(page=3, per_page=50)` is called with 120 total stories
- **THEN** it returns 20 items
