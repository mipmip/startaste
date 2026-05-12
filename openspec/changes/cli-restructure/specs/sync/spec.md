## ADDED Requirements

### Requirement: Sync fetches stories and comments
The `startaste sync` command SHALL always fetch both upvoted stories and upvoted comments from Hacker News and store them in SQLite.

#### Scenario: Running sync
- **WHEN** user runs `startaste sync`
- **THEN** system fetches both stories and comments without requiring any flags

### Requirement: Auto-detect full vs incremental sync
The sync command SHALL automatically determine the sync mode based on database state. No mode flag is needed.

#### Scenario: First sync with empty database
- **WHEN** user runs `startaste sync` and the database has no items
- **THEN** system performs a full sync, scraping all pages until HN returns an empty page

#### Scenario: Subsequent sync with existing data
- **WHEN** user runs `startaste sync` and the database already has items
- **THEN** system performs an incremental sync, stopping when it hits known items

### Requirement: Incremental sync stop condition
During incremental sync, the system SHALL stop scraping a type when all IDs on a page are already known in the database.

#### Scenario: Page with all known IDs
- **WHEN** system scrapes a page and every ID on that page already exists in the database
- **THEN** system stops scraping that type and moves on

#### Scenario: Page with mix of new and known IDs
- **WHEN** system scrapes a page containing both new and known IDs
- **THEN** system saves the new IDs and continues to the next page

### Requirement: Fetch API metadata only for new items
The system SHALL only fetch HN API metadata for items that have no body stored in the database.

#### Scenario: New item without metadata
- **WHEN** an item ID exists in the database with a NULL body
- **THEN** system fetches its metadata from the HN API and stores it

#### Scenario: Existing item with metadata
- **WHEN** an item ID already has a body in the database
- **THEN** system skips the API call for that item

### Requirement: Sync writes to database only
The sync command SHALL write to SQLite only. It MUST NOT produce any file output.

#### Scenario: Sync output
- **WHEN** user runs `startaste sync`
- **THEN** system logs progress to stdout but does not write any export files
