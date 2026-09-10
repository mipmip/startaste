## ADDED Requirements

### Requirement: One source failing does not abort the others
A sync run over several sources SHALL attempt every configured source. A source that fails SHALL be reported and skipped, and the remaining sources SHALL still be synced.

#### Scenario: One of several sources fails
- **WHEN** two sources are configured and the first fails
- **THEN** the failure is reported and the second is still synced

#### Scenario: A single named source fails
- **WHEN** one source is named and it fails
- **THEN** the failure is reported

#### Scenario: Failures are summarised at the end
- **WHEN** a run finishes with at least one source having failed
- **THEN** the run says which sources failed, rather than leaving that to be inferred from the log

## MODIFIED Requirements

### Requirement: Sync reports progress and failures on its own exit status
A sync run SHALL log what it is doing and SHALL exit non-zero when it fails, so a scheduler can tell success from failure. A run in which some sources succeeded and others failed SHALL be treated as a failure.

#### Scenario: Successful run
- **WHEN** a run completes
- **THEN** it logs completion and exits zero

#### Scenario: Failed run
- **WHEN** a run cannot complete
- **THEN** it exits non-zero and the reason is in the log

#### Scenario: Partial failure
- **WHEN** at least one source failed and at least one succeeded
- **THEN** the run exits non-zero, and the work the successful sources did is kept
