## ADDED Requirements

### Requirement: GitHub authentication via token
The GitHub source SHALL authenticate using a personal access token from the `GITHUB_TOKEN` env var.

#### Scenario: Token is set
- **WHEN** `GITHUB_TOKEN` is set in the environment
- **THEN** `is_configured()` returns `True`

#### Scenario: Token is missing
- **WHEN** `GITHUB_TOKEN` is not set
- **THEN** `is_configured()` returns `False` and sync exits with a clear error if attempted

### Requirement: Sync starred repositories
The GitHub source SHALL fetch all starred repositories for the authenticated user via the GitHub REST API.

#### Scenario: Full sync with no existing data
- **WHEN** sync runs and the `github_star` table is empty
- **THEN** all starred repos are fetched by paginating `GET /user/starred` until an empty page

#### Scenario: Incremental sync with existing data
- **WHEN** sync runs and the `github_star` table has items
- **THEN** sync stops when all repos on a page are already known

### Requirement: Star metadata storage
Each starred repo SHALL be stored with its GitHub repo ID as `_id`, the full API response as `body`, and `starred_at` as timestamp.

#### Scenario: Star stored in database
- **WHEN** a starred repo is fetched from the API
- **THEN** it is stored in `github_star` with `_id` = repo ID, `body` = full JSON, `timestamp` = starred_at date

### Requirement: Rate limiting
The GitHub source SHALL respect rate limits by adding a delay between API requests.

#### Scenario: Delay between requests
- **WHEN** multiple pages are fetched
- **THEN** a delay of at least 0.2 seconds is added between requests
