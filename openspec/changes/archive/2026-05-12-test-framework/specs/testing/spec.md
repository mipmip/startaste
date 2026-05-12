## ADDED Requirements

### Requirement: Export tests use real SQLite with no mocks
Export tests SHALL use an in-memory SQLite database with real data. No HTTP mocking or monkey-patching is used for export tests.

#### Scenario: Export with data
- **WHEN** the database contains stories and comments
- **THEN** `run_export` returns JSON with both `saved_stories` and `saved_comments` populated

#### Scenario: Export empty database
- **WHEN** the database is empty
- **THEN** `run_export` returns JSON with empty arrays

#### Scenario: Export filtered by story
- **WHEN** `run_export` is called with `select=["story"]`
- **THEN** output contains `saved_stories` populated and `saved_comments` as empty array

#### Scenario: Export filtered by comment
- **WHEN** `run_export` is called with `select=["comment"]`
- **THEN** output contains `saved_comments` populated and `saved_stories` as empty array

#### Scenario: Export to file
- **WHEN** `run_export` is called with a file path
- **THEN** the file is created with the JSON content

#### Scenario: Export to stdout
- **WHEN** `run_export` is called without a file path
- **THEN** JSON is printed to stdout

### Requirement: Scraper tests use mocked HTTP with HTML fixtures
Scraper tests SHALL use the `responses` library to intercept HTTP calls. The `Req` class runs unmodified.

#### Scenario: Login success
- **WHEN** the mock returns a 200 response containing the username
- **THEN** `req.login()` succeeds without raising

#### Scenario: Login failure — bad credentials
- **WHEN** the mock returns a response containing "Bad login"
- **THEN** `req.login()` raises an exception

#### Scenario: Scrape stories from HTML
- **WHEN** a mock returns HTML with `<td class="subtext">` containing `item?id=` links
- **THEN** `get_upvoted_stories` returns the expected list of IDs

#### Scenario: Scrape comments from HTML
- **WHEN** a mock returns HTML with `<td class="default">` containing `item?id=` links
- **THEN** `get_upvoted_comments` returns the expected list of IDs

#### Scenario: Pagination stops on empty page
- **WHEN** a mock returns HTML with no matching elements
- **THEN** the scraper stops and returns only IDs from previous pages

#### Scenario: Get item from API
- **WHEN** a mock returns a JSON item for the Firebase API URL
- **THEN** `get_item` returns the parsed dict

### Requirement: Sync integration tests combine mocked HTTP with real database
Sync integration tests SHALL use the `responses` library for HTTP and an in-memory SQLite database. The full sync flow runs end-to-end.

#### Scenario: Full sync with empty database
- **WHEN** the database is empty and mocked HTTP returns story and comment pages
- **THEN** `run_sync` populates the database with all scraped IDs and their metadata

#### Scenario: Incremental sync with existing data
- **WHEN** the database already contains items and mocked HTTP returns pages with a mix of known and new IDs
- **THEN** `run_sync` adds only the new items

#### Scenario: Incremental stop condition
- **WHEN** the database already contains items and mocked HTTP returns a page where all IDs are already known
- **THEN** `run_sync` stops scraping that type

### Requirement: Test isolation
Each test SHALL run against a fresh database and clean HTTP mock state.

#### Scenario: Database isolation
- **WHEN** a test inserts data into the database
- **THEN** the next test starts with an empty database

#### Scenario: No real network calls
- **WHEN** any test runs
- **THEN** no actual HTTP requests are made to HN or Firebase

### Requirement: Sleep is patched in tests
All tests SHALL run with `time.sleep` patched to a no-op to avoid artificial delays.

#### Scenario: Test speed
- **WHEN** the full test suite runs
- **THEN** no 0.5s or 0.2s sleeps occur between scrape/API calls

### Requirement: Coverage reporting
The test suite SHALL support coverage reporting via `pytest-cov`.

#### Scenario: Running with coverage
- **WHEN** user runs `pytest --cov=startaste --cov-report=term-missing`
- **THEN** coverage report is displayed showing line-by-line coverage for the `startaste` package
