# hn-sync Specification

## Purpose
Defines how the Hacker News source walks a user's upvoted listings — how those
pages are paginated, how far traversal may go, and when scraped IDs are
committed to the database.

## Requirements

### Requirement: Upvoted listings paginate by following the More link
The HN source SHALL walk upvoted listings by following the `More` link that Hacker News puts at the foot of the page, and MUST NOT rely on a `p=<n>` query parameter. Hacker News ignores `p=` on `/upvoted` and returns the first page for every value, so a page counter never advances.

#### Scenario: More link present
- **WHEN** a scraped upvoted page contains a `More` link
- **THEN** the next request is that link's href, carrying its `next`, `n` and `time` cursor values

#### Scenario: More link absent
- **WHEN** a scraped upvoted page contains no `More` link
- **THEN** scraping of that listing stops and the collected IDs are returned

#### Scenario: Listing with a single page
- **WHEN** the upvoted comments listing returns one page with no `More` link
- **THEN** that page's IDs are stored and scraping stops without further requests

#### Scenario: Full sync terminates
- **WHEN** a full sync runs against an account with more upvotes than fit on one page
- **THEN** it walks every page exactly once and completes, rather than re-reading the first page

### Requirement: Bounded page traversal
The HN source SHALL stop after a bounded number of pages per listing and SHALL log when that bound is reached, so a future change to Hacker News cannot make sync loop indefinitely.

#### Scenario: Bound reached
- **WHEN** the page bound is reached before the `More` link runs out
- **THEN** scraping stops and a warning names the bound and the number of IDs collected so far

#### Scenario: Bound not reached
- **WHEN** the listing ends before the bound
- **THEN** no warning is logged

### Requirement: A listing's IDs are stored atomically
The HN source SHALL store the IDs of a listing only once its scrape has finished, so an interrupted scrape leaves no partial listing behind. A partially stored listing would make the database non-empty, sending the next run down the incremental path where it stops on the first page of known IDs and silently abandons the rest of the listing.

#### Scenario: Scrape interrupted
- **WHEN** a full sync fails or is interrupted part-way through walking a listing
- **THEN** none of that listing's IDs are stored, and the next run still takes the full-sync path

#### Scenario: Scrape completes
- **WHEN** a listing has been walked to its last page
- **THEN** every collected ID is stored, and metadata is then fetched for the ones that have none

#### Scenario: Interrupted metadata fetch resumes
- **WHEN** sync is interrupted while fetching metadata, after the IDs were stored
- **THEN** the next run fetches metadata only for the stored IDs that still have no body
