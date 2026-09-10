## MODIFIED Requirements

### Requirement: The MCP endpoint requires a bearer token and the health endpoint does not
The MCP endpoint SHALL require a valid bearer token. A health endpoint SHALL be
reachable without credentials so that a reverse proxy and monitoring can probe
the service.

Authentication SHALL apply to the MCP endpoint, not to the whole server. A
request for a path the server does not serve SHALL be answered as not found, and
SHALL NOT be answered as unauthorized. Rejections SHALL NOT carry a
`WWW-Authenticate` challenge.

Both matter for clients that follow the MCP authorization flow. A `401` carrying
a `WWW-Authenticate: Bearer` challenge tells a client the endpoint is
OAuth-protected, so it looks for protected-resource metadata under
`/.well-known/`. If those paths also answer `401`, the client can neither
complete discovery nor conclude that there is none, and it gives up before
using the static token it was configured with. A bare `Bearer` challenge carries
no realm or metadata pointer, so it tells the client nothing it can act on while
triggering that dead end.

#### Scenario: Valid token
- **WHEN** a request carries `Authorization: Bearer` with a token whose record is present
- **THEN** the request is served

#### Scenario: No token
- **WHEN** a request to the MCP endpoint carries no authorization header
- **THEN** it is rejected

#### Scenario: Health check needs nothing
- **WHEN** the health endpoint is requested with no credentials
- **THEN** it responds, and its body does not disclose collection contents

#### Scenario: Failures are indistinguishable
- **WHEN** a token is missing, malformed, unknown, or belongs to a revoked record
- **THEN** the rejection is identical in every case, disclosing nothing about which

#### Scenario: An unserved path is not found, not unauthorized
- **WHEN** an unauthenticated request asks for a path the server does not serve,
  such as `/.well-known/oauth-protected-resource`
- **THEN** it SHALL be answered `404`, so a client can conclude the server offers
  no OAuth metadata and fall back to its configured token

#### Scenario: Rejection carries no authentication challenge
- **WHEN** a request to the MCP endpoint is rejected
- **THEN** the response SHALL NOT include a `WWW-Authenticate` header

#### Scenario: An unserved path is still not a way in
- **WHEN** an unserved path is requested
- **THEN** the response SHALL disclose nothing about the collection, exactly as
  before — it is not found, not served
