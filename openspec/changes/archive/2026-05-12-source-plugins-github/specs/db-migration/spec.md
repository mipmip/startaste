## ADDED Requirements

### Requirement: Automatic table migration on startup
The system SHALL automatically rename old table names to namespaced names on first run after upgrade.

#### Scenario: Old tables exist
- **WHEN** the database has `story` and `comment` tables but no `hn_story` or `hn_comment`
- **THEN** system renames `story` → `hn_story` and `comment` → `hn_comment`

#### Scenario: Already migrated
- **WHEN** the database already has `hn_story` and `hn_comment` tables
- **THEN** no migration is performed

#### Scenario: Fresh database
- **WHEN** the database has no tables
- **THEN** new namespaced tables are created directly (no migration needed)

#### Scenario: Data preserved
- **WHEN** migration renames tables
- **THEN** all existing data is preserved (ALTER TABLE RENAME preserves data)
