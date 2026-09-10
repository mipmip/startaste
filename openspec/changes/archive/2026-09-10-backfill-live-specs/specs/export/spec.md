## Purpose

Reading the collection back out: what `startaste export` produces, how it is
filtered, where it goes, and the shape of the JSON.

## ADDED Requirements

### Requirement: Export reads the database and makes no network calls
The export command SHALL read stored items only. It MUST NOT contact any source.

#### Scenario: Export with an empty database
- **WHEN** the database has no items
- **THEN** an empty structure is written in the requested format

#### Scenario: Export after a sync
- **WHEN** the database has items
- **THEN** they are written, ordered by timestamp descending

#### Scenario: No credentials needed
- **WHEN** export runs with no source credentials set
- **THEN** it still succeeds, because it contacts nothing

### Requirement: JSON is the default format
The export command SHALL default to JSON, selectable explicitly with `--format`.

#### Scenario: Default
- **WHEN** no format is given
- **THEN** the output is JSON

#### Scenario: Explicit
- **WHEN** `--format json` is given
- **THEN** the output is JSON

### Requirement: Output goes to a file or to stdout
The export command SHALL write to the path given with `-f`/`--file`, and to stdout when none is given.

#### Scenario: To a file
- **WHEN** a file path is given
- **THEN** the output is written there

#### Scenario: To stdout
- **WHEN** no file path is given
- **THEN** the output is written to stdout

### Requirement: JSON is nested by source and item type
The JSON output SHALL nest items under their source name and then their item type, so sources cannot collide and a new source needs no format change.

#### Scenario: Several sources
- **WHEN** both HN and GitHub have items
- **THEN** the structure is `{"hn": {"stories": [...], "comments": [...]}, "github": {"stars": [...]}}`

#### Scenario: Filtered by source
- **WHEN** one source is selected
- **THEN** only that source's key is present

#### Scenario: A source with no items
- **WHEN** a source has nothing stored
- **THEN** its item types are present as empty arrays

#### Scenario: Item type keys are plural
- **WHEN** a source declares an item type
- **THEN** its key in the output is the plural of that type
