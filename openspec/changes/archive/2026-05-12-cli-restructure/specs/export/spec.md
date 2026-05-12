## ADDED Requirements

### Requirement: Export reads from database only
The `startaste export` command SHALL read from SQLite and produce output. It MUST NOT make any network calls.

#### Scenario: Export without prior sync
- **WHEN** user runs `startaste export` and the database is empty
- **THEN** system outputs an empty structure in the requested format

#### Scenario: Export after sync
- **WHEN** user runs `startaste export` and the database has items
- **THEN** system outputs all items ordered by timestamp descending

### Requirement: JSON format as default
The export command SHALL default to JSON format via the `--format` flag.

#### Scenario: Default format
- **WHEN** user runs `startaste export` without `--format`
- **THEN** system outputs JSON

#### Scenario: Explicit JSON format
- **WHEN** user runs `startaste export --format=json`
- **THEN** system outputs JSON

### Requirement: Filter by item type
The export command SHALL support filtering by item type via the `-s` flag.

#### Scenario: Export stories only
- **WHEN** user runs `startaste export -s story`
- **THEN** output contains only stories

#### Scenario: Export comments only
- **WHEN** user runs `startaste export -s comment`
- **THEN** output contains only comments

#### Scenario: Export both (default)
- **WHEN** user runs `startaste export` without `-s`
- **THEN** output contains both stories and comments

### Requirement: Output to file or stdout
The export command SHALL write to a file when `-f` is specified, otherwise to stdout.

#### Scenario: Output to file
- **WHEN** user runs `startaste export -f output.json`
- **THEN** system writes the output to `output.json`

#### Scenario: Output to stdout
- **WHEN** user runs `startaste export` without `-f`
- **THEN** system writes the output to stdout

### Requirement: JSON structure separates stories and comments
The JSON output SHALL use separate keys for stories and comments.

#### Scenario: JSON with both types
- **WHEN** user exports both stories and comments as JSON
- **THEN** output has `saved_stories` and `saved_comments` as separate arrays
