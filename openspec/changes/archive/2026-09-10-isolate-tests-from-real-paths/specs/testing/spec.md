## MODIFIED Requirements

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
