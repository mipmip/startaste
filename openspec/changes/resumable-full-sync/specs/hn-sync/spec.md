## MODIFIED Requirements

### Requirement: A listing's IDs are stored atomically
The HN source SHALL store the IDs of a listing only once its scrape has finished, so an interrupted scrape leaves no partial listing behind and a listing's rows never appear before its walk completed. What keeps the incremental stop condition sound is the listing's completion record, specified in the `sync-state` capability; this requirement is about not exposing rows for a walk that never finished.

#### Scenario: Scrape interrupted
- **WHEN** a full sync fails or is interrupted part-way through walking a listing
- **THEN** none of that listing's IDs are stored, and the listing is not recorded as complete

#### Scenario: Scrape completes
- **WHEN** a listing has been walked to its last page
- **THEN** every collected ID is stored, the listing is recorded as complete, and metadata is then fetched for the IDs that have none

#### Scenario: Interrupted metadata fetch resumes
- **WHEN** sync is interrupted while fetching metadata, after the IDs were stored
- **THEN** the next run fetches metadata only for the stored IDs that still have no body

## ADDED Requirements

### Requirement: HN listings are named for completion tracking
The HN source SHALL track its upvoted stories and upvoted comments as two separately named listings, so that each records its own completion and takes its own sync mode.

#### Scenario: Stories complete, comments not yet walked
- **WHEN** the stories listing has been walked to its last page and the comments listing has not been walked at all
- **THEN** the next run walks stories incrementally and comments in full

#### Scenario: Comments walk interrupted
- **WHEN** the comments listing's walk is interrupted after the stories listing completed
- **THEN** the next run walks comments in full and stories incrementally
