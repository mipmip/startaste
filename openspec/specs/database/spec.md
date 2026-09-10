# database Specification

## Purpose
How startaste opens its SQLite database — the journal mode and lock-wait
behaviour that let a reader and a writer use the same database at the same time.

## Requirements

### Requirement: The database is opened in WAL journal mode
The database SHALL be opened in write-ahead-log journal mode, so that a reader is not blocked by a writer holding a transaction. In rollback-journal mode a reader arriving during a write fails with a locked database, which makes it impossible to run a sync alongside a second process that reads.

#### Scenario: Fresh database
- **WHEN** a database is created on first run
- **THEN** its journal mode is WAL

#### Scenario: Database created before this change
- **WHEN** a database that was created in rollback-journal mode is opened
- **THEN** it is converted to WAL, and stays WAL for later connections

#### Scenario: Reading while a write transaction is open
- **WHEN** one connection holds an open write transaction and another connection reads
- **THEN** the read succeeds instead of failing with a locked database

#### Scenario: Every connection uses the configured mode
- **WHEN** any part of the application opens the database
- **THEN** it gets the same journal mode, without each call site configuring it

### Requirement: A contended database is waited on, not failed on
The database SHALL be opened with a busy timeout, so a connection that finds the database locked waits for it rather than failing immediately.

#### Scenario: Busy timeout is configured
- **WHEN** the database is opened
- **THEN** a non-zero busy timeout is in effect for that connection

#### Scenario: Two writers
- **WHEN** a second connection attempts to write while another holds the write lock
- **THEN** it waits for the lock up to the timeout instead of raising at once

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
