# mcp-server Specification

## Purpose
The MCP surface over the collected data: how a client connects, how it is
authenticated, which tools it may call, and the read-only guarantee that makes
the endpoint safe to expose beyond the local machine.

## Requirements

### Requirement: The collection is served over MCP streamable HTTP
The system SHALL serve the collection to MCP clients over the streamable HTTP transport, so a remote client can reach it through an HTTPS reverse proxy.

#### Scenario: Client connects and lists tools
- **WHEN** an authenticated MCP client connects to the MCP endpoint
- **THEN** it receives the tool list, and each tool has a description stating what it returns

#### Scenario: Long-lived stream
- **WHEN** a client holds the connection open across several tool calls
- **THEN** the connection is not closed between calls

#### Scenario: Bind is configurable
- **WHEN** an address and port are supplied
- **THEN** the server listens on exactly that address and port, defaulting to loopback

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

### Requirement: Tokens are stored hashed and compared in constant time
Token records SHALL be stored as hashes, never as recoverable values, and a presented token SHALL be compared against every record in constant time so that timing does not reveal which record matched.

#### Scenario: Records hold hashes
- **WHEN** the token file is read
- **THEN** each record carries a name and a hash of the token, and the raw token is not recoverable from the file

#### Scenario: Comparison does not early-exit
- **WHEN** a presented token is checked against several records
- **THEN** every record is compared before a result is returned

#### Scenario: Malformed record
- **WHEN** a record in the file is malformed
- **THEN** it never authenticates anything, and the server still serves the valid records

#### Scenario: Minting a token
- **WHEN** an operator mints a new token
- **THEN** they receive a token with at least 256 bits of entropy and the record to add to the file, and the raw token is shown only at that moment

#### Scenario: No token file
- **WHEN** the server starts with no readable token file
- **THEN** it exits with a clear error rather than serving unauthenticated

### Requirement: Tools cover retrieval and aggregation over both sources
The tool set SHALL let a client find individual items, fetch one in full, and ask what the collection is mostly about, across both GitHub stars and Hacker News upvotes.

#### Scenario: Searching stars
- **WHEN** a client searches stars by text, and optionally filters by language or topic
- **THEN** it receives matching repositories with the fields needed to identify and judge them

#### Scenario: Searching upvotes
- **WHEN** a client searches upvotes by text, optionally restricted to stories or comments
- **THEN** it receives matching items

#### Scenario: Fetching one item
- **WHEN** a client asks for a single item by source and id
- **THEN** it receives that item's stored record

#### Scenario: Unknown item
- **WHEN** a client asks for an id that is not stored
- **THEN** it receives a clear not-found result rather than an error that ends the conversation

#### Scenario: Asking what the collection is about
- **WHEN** a client asks for the most common topics, languages, or upvoted domains
- **THEN** it receives them ordered by frequency with counts, limited to the requested number

#### Scenario: Overview
- **WHEN** a client asks for an overview
- **THEN** it receives per-source item counts and when each source last had new data

#### Scenario: Results are bounded
- **WHEN** a query would match more items than the requested limit
- **THEN** only that many are returned, and the client can tell that the result was truncated

#### Scenario: Empty collection
- **WHEN** any tool is called against a database with no items
- **THEN** it returns an empty result rather than failing

### Requirement: The MCP server never writes to the database
The MCP server SHALL open the database read-only. It is the only surface reachable from outside the local network, and no tool has a reason to modify the collection.

#### Scenario: No write path
- **WHEN** the MCP server is running
- **THEN** no tool it exposes can create, modify or delete stored data

#### Scenario: A write is refused by the database itself
- **WHEN** a write is attempted on the MCP server's connection
- **THEN** the database refuses it, rather than the refusal depending on application code

#### Scenario: Missing database
- **WHEN** the server starts and no database exists yet
- **THEN** it exits with an error telling the operator to run a sync first, and does not create an empty database

#### Scenario: Reading while a sync writes
- **WHEN** a tool is called while a sync run holds a write transaction
- **THEN** the read succeeds

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
