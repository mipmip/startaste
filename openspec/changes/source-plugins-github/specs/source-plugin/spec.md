## ADDED Requirements

### Requirement: Source protocol
Each source SHALL implement a common interface with name, item types, models, env help, configuration check, and sync method.

#### Scenario: Source provides metadata
- **WHEN** a source is instantiated
- **THEN** it exposes `name`, `item_types`, `models`, and `env_help` attributes

#### Scenario: Source reports configuration status
- **WHEN** `source.is_configured()` is called
- **THEN** it returns `True` if all required env vars are set, `False` otherwise

#### Scenario: Source syncs data
- **WHEN** `source.sync()` is called and the source is configured
- **THEN** it fetches data from the external service and stores it in the database

### Requirement: Source discovery
Sources SHALL be discoverable via a registry in `startaste/sources/__init__.py`.

#### Scenario: List all sources
- **WHEN** `get_sources()` is called
- **THEN** it returns all known source instances

#### Scenario: List configured sources
- **WHEN** `get_configured_sources()` is called
- **THEN** it returns only sources whose env vars are set

#### Scenario: Get source by name
- **WHEN** `get_source("hn")` is called
- **THEN** it returns the HN source instance

#### Scenario: Unknown source name
- **WHEN** `get_source("unknown")` is called
- **THEN** it raises an error

### Requirement: Source models use namespaced tables
Each source's database models SHALL use table names prefixed with the source name.

#### Scenario: HN models
- **WHEN** HnStory and HnComment models are defined
- **THEN** their table names are `hn_story` and `hn_comment`

#### Scenario: GitHub models
- **WHEN** GithubStar model is defined
- **THEN** its table name is `github_star`
