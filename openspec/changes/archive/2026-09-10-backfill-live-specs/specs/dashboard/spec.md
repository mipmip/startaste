## Purpose

The local web dashboard: how it is served and what its pages show. It is a
read-only view over the collection with no authentication of its own.

## ADDED Requirements

### Requirement: The dashboard is served locally on a configurable bind
The `serve` subcommand SHALL start a web server on a configurable address and port, defaulting to loopback, and SHALL shut down cleanly on interrupt.

#### Scenario: Defaults
- **WHEN** `startaste serve` is run with no arguments
- **THEN** the dashboard is reachable on loopback at its default port

#### Scenario: Configured bind
- **WHEN** a host and port are given
- **THEN** the dashboard listens on exactly those

#### Scenario: Interrupt
- **WHEN** the process is interrupted
- **THEN** it shuts down without a traceback

### Requirement: The dashboard never writes
The dashboard SHALL only read. Loading any page MUST NOT modify stored data.

#### Scenario: Loading pages
- **WHEN** any dashboard page is loaded
- **THEN** no stored item is created, changed or deleted

### Requirement: The dashboard has no authentication
The dashboard SHALL NOT implement authentication, and its default bind SHALL therefore be loopback so that exposing it is always a deliberate act.

#### Scenario: Reachable without credentials
- **WHEN** the dashboard is reached on its bind
- **THEN** it serves pages without asking for credentials

#### Scenario: Exposure is deliberate
- **WHEN** a wider bind is not configured
- **THEN** the dashboard is reachable only from the local machine

### Requirement: An overview page shows every source
The dashboard SHALL show a card per source with its item counts and when it last had new data, including sources with nothing stored.

#### Scenario: Source with data
- **WHEN** a source has items
- **THEN** its card shows the count per item type and the last timestamp

#### Scenario: Source with no data
- **WHEN** a source has nothing
- **THEN** its card shows zero counts rather than being absent

### Requirement: Each source has listing pages
The dashboard SHALL list HN upvoted stories, HN upvoted comments and GitHub stars on their own pages, each paginated.

#### Scenario: Stories
- **WHEN** the HN stories page is opened
- **THEN** stories are listed with their title, link, score, author and date

#### Scenario: Comments
- **WHEN** the HN comments page is opened
- **THEN** comments are listed with their text, author and date

#### Scenario: Stars
- **WHEN** the GitHub page is opened
- **THEN** repositories are listed with owner and name, description, language and when they were starred

#### Scenario: Pagination
- **WHEN** a listing has more items than fit on a page
- **THEN** pagination controls are shown and a page can be selected by query parameter
