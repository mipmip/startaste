## ADDED Requirements

### Requirement: Export JSON is nested by source and type
The JSON export SHALL use a nested structure with source names as top-level keys and item types as second-level keys.

#### Scenario: Export with multiple sources
- **WHEN** both HN and GitHub data exist and user runs `startaste export`
- **THEN** output has structure `{"hn": {"stories": [...], "comments": [...]}, "github": {"stars": [...]}}`

#### Scenario: Export filtered by source
- **WHEN** user runs `startaste export --source hn`
- **THEN** output has structure `{"hn": {"stories": [...], "comments": [...]}}`

#### Scenario: Export empty source
- **WHEN** a source has no data
- **THEN** its types are present as empty arrays
