## Purpose

Records whether each source's listing has been walked all the way to its last
page, and makes the full-versus-incremental sync decision follow that record
instead of being inferred from how many rows a table happens to hold.

## ADDED Requirements

### Requirement: Listing completion is recorded
Sync SHALL record, for every source and every named listing it walks, whether that listing's walk reached the last page. A listing SHALL be marked complete only after its walk finished and its IDs were stored, and MUST NOT be marked complete when the walk stopped early for any other reason.

#### Scenario: Walk reaches the last page
- **WHEN** a listing is walked to its last page and its IDs are stored
- **THEN** that listing is recorded as complete

#### Scenario: Walk interrupted or fails
- **WHEN** a listing's walk is interrupted, or fails with an error, before its last page
- **THEN** that listing is not recorded as complete

#### Scenario: Walk stopped by the page bound
- **WHEN** a listing's walk stops because it hit the page bound rather than the end of the listing
- **THEN** that listing is not recorded as complete

#### Scenario: Listings are recorded independently
- **WHEN** one of a source's listings completes and another does not
- **THEN** only the completed listing is recorded as complete

### Requirement: Sync mode follows the completion record
Sync SHALL choose a listing's mode from its completion record and MUST NOT infer the mode from the number of rows already stored. A listing with no record, or one recorded as incomplete, SHALL be walked in full; a listing recorded as complete SHALL be walked incrementally.

#### Scenario: No record yet
- **WHEN** a listing has no completion record
- **THEN** it is walked in full

#### Scenario: Recorded incomplete
- **WHEN** a listing is recorded as incomplete
- **THEN** it is walked in full, even though the database already holds rows for it

#### Scenario: Recorded complete
- **WHEN** a listing is recorded as complete
- **THEN** it is walked incrementally, stopping on the first page whose IDs are all known

#### Scenario: A new listing in a populated database
- **WHEN** a source gains a listing that has never been walked, in a database that already holds rows for its other listings
- **THEN** the new listing is walked in full

### Requirement: A full walk runs to the end of the listing
A full walk SHALL continue to the end of the listing regardless of how many of a page's IDs are already known, so that a listing left incomplete by an earlier run is finished rather than truncated.

#### Scenario: Resuming an incomplete listing
- **WHEN** a listing recorded as incomplete already holds the IDs from its first pages
- **THEN** the walk covers every page to the end of the listing, and the already-known IDs are stored again without creating duplicates

#### Scenario: Known page during a full walk
- **WHEN** every ID on a page is already known during a full walk
- **THEN** the walk continues to the next page instead of stopping

### Requirement: Existing databases are seeded on first run
On the first run against a database that predates completion records, sync SHALL seed the record for each listing that already holds rows as complete, so that upgrading does not trigger an unexpected full walk.

#### Scenario: Upgrading a fully synced database
- **WHEN** sync runs against a database that holds rows for a listing but has no completion records
- **THEN** that listing is seeded as complete and is walked incrementally

#### Scenario: Upgrading an empty database
- **WHEN** sync runs against a database that holds no rows for a listing and has no completion records
- **THEN** that listing is not seeded, and is walked in full

#### Scenario: Seeding happens once
- **WHEN** sync runs again after seeding
- **THEN** the seeded records are used as they are, and are not re-derived from row counts

### Requirement: Completion records are not user data
Completion records SHALL be excluded from `startaste export` output and from the dashboard, which present only items collected from sources.

#### Scenario: Export output
- **WHEN** `startaste export` runs against a database with completion records
- **THEN** the output contains only source items, in the same shape as before

#### Scenario: Dashboard listings
- **WHEN** the dashboard renders its source cards and listings
- **THEN** completion records are not shown as items and do not affect item counts
