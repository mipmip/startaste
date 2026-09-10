## ADDED Requirements

### Requirement: A refused login is reported as a credential problem
The HN source SHALL report a refused login as a credential problem naming the variables it uses, with no traceback, and SHALL distinguish it from a login attempt that could not be completed.

#### Scenario: Credentials refused
- **WHEN** Hacker News refuses the account and password
- **THEN** the failure is reported as rejected credentials, naming the variables, with no traceback

#### Scenario: Logged in but the account is not shown
- **WHEN** the login response does not confirm the account is signed in
- **THEN** the failure is reported as a credential problem rather than as an unexpected error

#### Scenario: Login could not be attempted
- **WHEN** the login request cannot be completed because the site is unreachable
- **THEN** the failure is reported as a connection problem rather than as rejected credentials
