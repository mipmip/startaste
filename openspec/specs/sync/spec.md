# sync Specification

## Purpose
Sync orchestration across sources: which sources run, how a source reports what
it needs, and what a sync run may and may not do. How an individual source
walks its own listings belongs to that source's capability.

## Requirements

### Requirement: Only configured sources are synced
A sync run SHALL sync every configured source, and SHALL skip sources whose credentials are absent rather than failing.

#### Scenario: One of two sources configured
- **WHEN** only one source's credentials are set and `startaste sync` runs
- **THEN** that source is synced and the other is skipped

#### Scenario: Nothing configured
- **WHEN** no source's credentials are set
- **THEN** the run exits with an error saying no sources are configured

#### Scenario: A named source that is not configured
- **WHEN** a specific source is named but its credentials are absent
- **THEN** the run exits with an error listing the variables that source needs

### Requirement: Sync mode is determined automatically
A sync run SHALL decide by itself whether to fetch everything or only what is new, without a flag.

#### Scenario: First run
- **WHEN** a source has no stored items
- **THEN** everything available is fetched

#### Scenario: Later runs
- **WHEN** a source already has stored items
- **THEN** only new items are fetched, and the run stops early once it reaches items it already knows

### Requirement: Metadata is fetched only for items that lack it
A sync run SHALL fetch an item's metadata only when the item has no stored body, so an interrupted run resumes rather than restarting.

#### Scenario: Item without metadata
- **WHEN** a stored item has no body
- **THEN** its metadata is fetched and stored

#### Scenario: Item that already has metadata
- **WHEN** a stored item already has a body
- **THEN** no request is made for it

#### Scenario: Resuming after an interruption
- **WHEN** a run is interrupted while fetching metadata and is run again
- **THEN** it fetches only the items still missing a body

### Requirement: Sync writes to the database only
A sync run SHALL write to the database only. It MUST NOT produce file output.

#### Scenario: Running sync
- **WHEN** a sync run completes
- **THEN** progress is logged, and no export file is written

### Requirement: Sync reports progress and failures on its own exit status
A sync run SHALL log what it is doing and SHALL exit non-zero when it fails, so a scheduler can tell success from failure.

#### Scenario: Successful run
- **WHEN** a run completes
- **THEN** it logs completion and exits zero

#### Scenario: Failed run
- **WHEN** a run cannot complete
- **THEN** it exits non-zero and the reason is in the log
