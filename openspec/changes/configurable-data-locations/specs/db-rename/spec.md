## ADDED Requirements

### Requirement: Automatic database file rename
The system SHALL automatically rename `hn.db` to `startaste.db` on first run after upgrade.

#### Scenario: Old file exists at data directory
- **WHEN** `hn.db` exists in the data directory and `startaste.db` does not
- **THEN** `hn.db` is renamed to `startaste.db`

#### Scenario: Old file exists in cwd (legacy)
- **WHEN** `hn.db` exists in the current working directory and no database exists at the XDG path
- **THEN** `hn.db` is moved to the XDG data directory as `startaste.db`

#### Scenario: New file already exists
- **WHEN** `startaste.db` already exists at the data directory
- **THEN** no migration is performed, any old `hn.db` is left untouched

#### Scenario: Data preserved
- **WHEN** the file is renamed or moved
- **THEN** all existing data is preserved
