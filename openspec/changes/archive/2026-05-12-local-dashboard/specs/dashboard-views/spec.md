## ADDED Requirements

### Requirement: Overview page shows all sources
The index page SHALL display a card for each source with item counts and sync status.

#### Scenario: Source with data
- **WHEN** HN source has synced stories and comments
- **THEN** the HN card shows story count, comment count, and last sync timestamp

#### Scenario: Source with no data
- **WHEN** GitHub source has no synced data
- **THEN** the GitHub card shows zero counts

### Requirement: HN dashboard shows stories and comments
The HN page SHALL list upvoted stories with metadata, paginated.

#### Scenario: Stories listing
- **WHEN** user visits `/hn`
- **THEN** stories are listed with title, URL, score, author, date, comment count

#### Scenario: Comments listing
- **WHEN** user visits `/hn/comments`
- **THEN** comments are listed with text, parent link, author, date

#### Scenario: Pagination
- **WHEN** there are more items than `per_page`
- **THEN** pagination controls are shown and `?page=N` navigates between pages

### Requirement: GitHub dashboard shows starred repos
The GitHub page SHALL list starred repositories with metadata, paginated.

#### Scenario: Stars listing
- **WHEN** user visits `/github`
- **THEN** repos are listed with owner/repo, description, language, star count, starred date

### Requirement: Clean minimal design
The dashboard SHALL use a tangled.org-inspired aesthetic: system fonts, generous whitespace, subtle borders, light/dark mode via `prefers-color-scheme`.

#### Scenario: Dark mode
- **WHEN** user's OS is set to dark mode
- **THEN** the dashboard renders with a dark color scheme

#### Scenario: Light mode
- **WHEN** user's OS is set to light mode
- **THEN** the dashboard renders with a light color scheme
