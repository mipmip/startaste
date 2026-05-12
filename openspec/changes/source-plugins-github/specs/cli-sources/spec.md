## ADDED Requirements

### Requirement: Sync accepts optional source argument
The `startaste sync` command SHALL accept an optional source name to sync only that source.

#### Scenario: Sync all sources
- **WHEN** user runs `startaste sync` with no argument
- **THEN** all configured sources are synced

#### Scenario: Sync specific source
- **WHEN** user runs `startaste sync github`
- **THEN** only the GitHub source is synced

#### Scenario: Sync unconfigured source
- **WHEN** user runs `startaste sync github` but `GITHUB_TOKEN` is not set
- **THEN** system exits with an error listing the required env vars

#### Scenario: Sync unknown source
- **WHEN** user runs `startaste sync unknown`
- **THEN** system exits with an error listing available sources

### Requirement: Export accepts source and type filters
The `startaste export` command SHALL accept `--source` and `--type` flags for filtering.

#### Scenario: Export all
- **WHEN** user runs `startaste export`
- **THEN** all items from all sources are exported

#### Scenario: Export by source
- **WHEN** user runs `startaste export --source hn`
- **THEN** only HN items are exported

#### Scenario: Export by type
- **WHEN** user runs `startaste export --type star`
- **THEN** only star items from any source are exported

#### Scenario: Export by source and type
- **WHEN** user runs `startaste export --source github --type star`
- **THEN** only GitHub stars are exported
