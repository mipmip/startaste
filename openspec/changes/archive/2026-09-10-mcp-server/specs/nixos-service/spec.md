## ADDED Requirements

### Requirement: The MCP server is a separately enabled unit
The module SHALL provide the MCP server as its own unit, enabled independently of sync and the dashboard, with a configurable bind and a path to its token file.

#### Scenario: Enabled with a token file
- **WHEN** a host enables the MCP unit and points it at a token file
- **THEN** the unit starts and serves on the configured address and port

#### Scenario: Default bind
- **WHEN** no address is configured
- **THEN** the MCP server listens on loopback only, so exposing it is deliberate

#### Scenario: Token file is a path, never a value
- **WHEN** the module is configured
- **THEN** the token file is supplied as a path, and no token value appears in any option or in the Nix store

#### Scenario: Enabled alone
- **WHEN** a host enables the MCP unit without sync or the dashboard
- **THEN** only that unit is created

#### Scenario: Runs hardened as the service user
- **WHEN** the MCP unit runs
- **THEN** it runs under the same hardened profile and service user as the other units, and is restarted on failure

#### Scenario: Ports do not collide
- **WHEN** the MCP server and the dashboard are both enabled
- **THEN** they listen on different ports
