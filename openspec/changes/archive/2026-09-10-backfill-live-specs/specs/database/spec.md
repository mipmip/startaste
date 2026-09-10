## ADDED Requirements

### Requirement: Tables are migrated automatically on startup
The system SHALL rename tables from an earlier naming scheme to the namespaced one when it finds them, preserving their contents, so an existing database keeps working without manual steps.

#### Scenario: Old tables present
- **WHEN** the database holds tables under the pre-namespace names and not the namespaced ones
- **THEN** they are renamed to the namespaced names

#### Scenario: Already migrated
- **WHEN** the namespaced tables are already present
- **THEN** no rename is attempted

#### Scenario: Fresh database
- **WHEN** the database has no tables
- **THEN** the namespaced tables are created directly, with no migration

#### Scenario: Data survives
- **WHEN** a rename happens
- **THEN** every row in the renamed table is preserved

### Requirement: The database file is migrated automatically from earlier locations
The system SHALL move a database left at an earlier path to the current one when no database exists there yet, preserving its contents.

#### Scenario: Old file beside the new one
- **WHEN** a database under the previous name sits in the data directory and no current one exists
- **THEN** it is renamed to the current name

#### Scenario: Old file in the working directory
- **WHEN** a database under the previous name sits in the working directory and none exists at the current path
- **THEN** it is moved to the data directory under the current name

#### Scenario: A current database already exists
- **WHEN** a database already exists at the current path
- **THEN** nothing is moved and any older file is left untouched

#### Scenario: Data survives
- **WHEN** a file is renamed or moved
- **THEN** its contents are preserved
