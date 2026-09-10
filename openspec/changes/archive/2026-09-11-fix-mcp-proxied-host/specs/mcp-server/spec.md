## ADDED Requirements

### Requirement: The server accepts requests proxied under its public hostname
The MCP transport validates the `Host` header to defend against DNS rebinding.
That defence SHALL be configurable, so a server reached through an HTTPS reverse
proxy accepts the public hostname clients actually send, while still rejecting
hosts nobody declared.

The operator SHALL be able to declare one or more allowed hostnames. Loopback
SHALL always be allowed so that local probing and health checks work without
configuration. Declaring a hostname SHALL also allow it as a request origin, over
both HTTP and HTTPS, with or without a port.

Rebinding protection SHALL remain enabled — the fix is to widen the allowed set to
what the deployment actually serves, never to switch the defence off.

#### Scenario: Request proxied under the declared hostname
- **WHEN** a request arrives at the MCP endpoint carrying a `Host` header equal to
  a declared hostname, as an HTTPS reverse proxy forwards it
- **THEN** it SHALL be processed, not rejected as an invalid host

#### Scenario: Undeclared host is still refused
- **WHEN** a request arrives carrying a `Host` header that was not declared and is
  not loopback
- **THEN** it SHALL be refused, so the rebinding defence still holds

#### Scenario: Loopback needs no configuration
- **WHEN** the server is probed on loopback with no hostname declared
- **THEN** the request SHALL be processed

#### Scenario: Hostname with or without a port
- **WHEN** a declared hostname arrives either bare or with a port
- **THEN** both SHALL be accepted, since a proxy may or may not include the port

#### Scenario: Declared hostname is also an allowed origin
- **WHEN** a request carries an `Origin` header for a declared hostname
- **THEN** it SHALL be accepted over both `http` and `https`
