## Purpose

The shared query layer over stored items. Both the dashboard and the MCP server
read through it, so it returns plain data with no presentation or transport
concerns of its own.

## ADDED Requirements

### Requirement: Queries return plain data
Query functions SHALL return plain dictionaries and lists, with stored JSON bodies already parsed, so that any consumer can render or serialise them without knowing about the database.

#### Scenario: Overview
- **WHEN** the overview query is called
- **THEN** it returns each source's name, whether it is configured, its item counts, and when it last had new data

#### Scenario: Stored bodies are parsed
- **WHEN** a query returns items whose body is stored as JSON text
- **THEN** the body is returned as parsed data, not as a string

#### Scenario: An unparseable body does not fail the query
- **WHEN** a stored body cannot be parsed
- **THEN** that item is still returned or skipped without raising

### Requirement: The layer is shared, not owned by one consumer
The query functions SHALL live outside any single surface's package, so that adding a consumer does not require moving them.

#### Scenario: Two consumers, one implementation
- **WHEN** the dashboard and the MCP server both need the same query
- **THEN** they call the same function, and neither imports the other

### Requirement: Listings are paginated
Listing queries SHALL take a page and a page size and report enough to render pagination.

#### Scenario: A middle page
- **WHEN** a listing is asked for page 2 with 50 per page and 120 items exist
- **THEN** it returns 50 items with the total, the current page, the page size and the number of pages

#### Scenario: The last page
- **WHEN** the last page is requested and it is not full
- **THEN** it returns only the remaining items

#### Scenario: A page beyond the end
- **WHEN** a page past the last is requested
- **THEN** it is clamped to the last page rather than returning an error

### Requirement: Searches are bounded and report what they matched
Search queries SHALL take a limit, return no more than that many items, and report the total matched so a caller can tell a complete answer from a partial one.

#### Scenario: More matches than the limit
- **WHEN** a search matches more items than the limit
- **THEN** it returns the limit, the total matched, and a flag saying the result was truncated

#### Scenario: Fewer matches than the limit
- **WHEN** a search matches fewer items than the limit
- **THEN** the truncation flag is false

#### Scenario: No matches
- **WHEN** nothing matches
- **THEN** an empty result is returned rather than an error

### Requirement: Aggregations rank by frequency and ignore absent values
Aggregation queries SHALL return values ordered by how often they occur, with counts, and SHALL skip items that do not carry the field rather than counting them as a value.

#### Scenario: Ranked by count
- **WHEN** an aggregation is requested
- **THEN** values are returned most frequent first, each with its count and the number of distinct values

#### Scenario: Items missing the field
- **WHEN** some items have no value for the aggregated field
- **THEN** they are skipped, and no empty or null value appears in the result

#### Scenario: Limit applies
- **WHEN** a limit is given
- **THEN** no more than that many values are returned
