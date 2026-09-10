## MODIFIED Requirements

### Requirement: Authentication uses a personal access token
The GitHub source SHALL authenticate with a personal access token from the environment, SHALL report itself unconfigured when the token is absent, and SHALL report a rejected token as a credential problem naming the variable — distinguishably from a rate limit or an unreachable API.

#### Scenario: Token present
- **WHEN** the token variable is set
- **THEN** the source reports itself configured

#### Scenario: Token absent
- **WHEN** the token variable is not set
- **THEN** the source reports itself unconfigured, and a sync attempt exits with a clear error

#### Scenario: Token rejected
- **WHEN** the API rejects the token as unauthorized
- **THEN** the failure is reported as a rejected credential, naming the variable, with no traceback

#### Scenario: Forbidden because of rate limiting
- **WHEN** the API refuses a request because the rate limit is exhausted
- **THEN** the failure is reported as rate limiting rather than as a rejected token

#### Scenario: API unreachable
- **WHEN** the API cannot be reached at all
- **THEN** the failure is reported as a connection problem rather than as a credential problem
