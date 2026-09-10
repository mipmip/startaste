## ADDED Requirements

### Requirement: The MCP unit can declare the hostname it is served under
A host fronting the MCP server with a reverse proxy SHALL be able to declare the
public hostname clients reach it by, so the transport accepts the `Host` header
the proxy forwards.

#### Scenario: Public hostname configured
- **WHEN** a host sets the MCP unit's public hostname option
- **THEN** the server is started with that hostname allowed, and requests proxied
  under it are served

#### Scenario: Not configured
- **WHEN** no public hostname is set
- **THEN** the unit still starts and remains reachable on loopback and on its bind
  address, so a mesh-only deployment needs no extra configuration

#### Scenario: Bind address is always accepted
- **WHEN** a request reaches the server directly on the address and port it was
  told to bind
- **THEN** it SHALL be accepted without the operator declaring that address
