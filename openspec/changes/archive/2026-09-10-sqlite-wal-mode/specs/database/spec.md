## Purpose

How startaste opens its SQLite database — the journal mode and lock-wait
behaviour that let a reader and a writer use the same database at the same time.

## ADDED Requirements

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
