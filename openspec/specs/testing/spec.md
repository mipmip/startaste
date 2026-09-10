# testing Specification

## Purpose
How the test suite is built: what is real, what is mocked, and how tests stay
independent of each other and of the network.

## Requirements

### Requirement: Tests never reach the network
No test SHALL make a real network request. Every external service SHALL be mocked at the HTTP layer.

#### Scenario: Running the suite offline
- **WHEN** the suite runs with no network access
- **THEN** every test still passes

#### Scenario: An unmocked request
- **WHEN** code under test would make a request that no mock covers
- **THEN** the test fails rather than reaching the network

### Requirement: Database tests use a real database
Tests that exercise storage SHALL use a real SQLite database rather than a mocked one, so that queries and migrations are actually executed.

#### Scenario: Storage behaviour
- **WHEN** a test stores and reads items
- **THEN** it does so through a real database

#### Scenario: Behaviour that needs a file
- **WHEN** a test covers something an in-memory database cannot express, such as journal mode
- **THEN** it uses a file-backed database

### Requirement: Scraped pages are covered by recorded fixtures
Tests for a source that scrapes HTML SHALL drive it with fixtures that reflect the real markup, including the elements the scraper depends on.

#### Scenario: Fixture fidelity
- **WHEN** a fixture stands in for a real page
- **THEN** it carries the structures the scraper relies on, so a page shape the code cannot handle fails the suite

### Requirement: Tests are isolated from each other and from the machine
Each test SHALL start from a clean database, and SHALL NOT read or write the developer's real data directories. Isolation SHALL be enforced for every test by default, not left to each test to arrange, so that a test which configures nothing still cannot reach a real path.

#### Scenario: Order independence
- **WHEN** tests run in any order
- **THEN** each behaves the same, because none inherits another's data

#### Scenario: Real data is untouched
- **WHEN** the suite runs
- **THEN** the machine's real database, log and credentials are neither read nor written

#### Scenario: A test that configures nothing
- **WHEN** a test exercises code that resolves the data, state, database or log location without having overridden any of them
- **THEN** it still resolves to a temporary location for that test

#### Scenario: Nothing is created outside the temporary locations
- **WHEN** the suite runs against a home directory that has never held startaste data
- **THEN** no startaste data, state or log directory is created under it

#### Scenario: Tests of the default locations still work
- **WHEN** a test asserts what a location defaults to with no override set
- **THEN** it can clear the overrides and observe the default, because the default is computed rather than created

### Requirement: Deliberate delays do not slow the suite
Pacing delays used against real services SHALL be neutralised in tests.

#### Scenario: A paced walk
- **WHEN** code under test paces its requests
- **THEN** the test does not wait for those delays

### Requirement: Coverage is measurable
The suite SHALL support coverage reporting over the application package.

#### Scenario: Running with coverage
- **WHEN** the suite is run with coverage enabled
- **THEN** a per-module report is produced for the application package
