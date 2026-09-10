## MODIFIED Requirements

### Requirement: Credentials come from the environment or a .env file
The system SHALL read each source's credentials from environment variables, falling back to a `.env` file discovered from the working directory, and SHALL exit with a clear message naming what is missing. A credential that is present but rejected by the source SHALL be reported in the same shape as one that is absent — naming the variable, saying it was rejected, and showing no traceback.

#### Scenario: Credentials in the environment
- **WHEN** a source's variables are set in the environment
- **THEN** they are used

#### Scenario: Credentials in a .env file
- **WHEN** a `.env` file in the working directory defines them
- **THEN** they are loaded and used, with the environment taking precedence

#### Scenario: Missing credentials
- **WHEN** a source's credentials are absent
- **THEN** the error names the variables that source needs, and no traceback is shown

#### Scenario: Rejected credentials
- **WHEN** a source rejects the credentials it was given
- **THEN** the error names the variable whose value was rejected and says how to renew it, and no traceback is shown

#### Scenario: A failure that is not about credentials
- **WHEN** a source cannot be reached, or refuses because of rate limiting
- **THEN** the error says so, and does not blame the credentials
