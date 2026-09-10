# nixos-service Specification

## Purpose
How startaste is consumed as a NixOS service: the flake attributes a host
imports, the option surface it configures, the units that run sync and the
dashboard, where state lives, and how credentials reach the units.

## Requirements

### Requirement: The flake exposes a module and an overlay
The flake SHALL expose a NixOS module and an overlay, so a host configuration can import the service and obtain its package without packaging startaste itself.

#### Scenario: Host imports the module
- **WHEN** a NixOS configuration imports the flake's NixOS module attribute
- **THEN** a `services.startaste` option set becomes available

#### Scenario: Overlay provides the package
- **WHEN** the flake's default overlay is applied to a nixpkgs instance
- **THEN** the startaste package is available as an attribute of that instance, and is the module's default package

#### Scenario: Package option can be overridden
- **WHEN** a host sets the module's package option explicitly
- **THEN** that package is used instead of the overlay's

### Requirement: Packages and shells are provided for more than one system
The flake SHALL enumerate its supported systems and provide `packages` and `devShells` for each, rather than binding a single hardcoded system.

#### Scenario: Building on a supported system
- **WHEN** the default package is built on any enumerated system
- **THEN** the build succeeds without editing the flake

#### Scenario: Existing consumers keep working
- **WHEN** an existing user builds `packages.x86_64-linux.default` or runs `nix develop`
- **THEN** both still work as before

### Requirement: Sync runs as a scheduled unit, not an application loop
The module SHALL provide sync as a oneshot unit driven by a timer, with a configurable interval. The application MUST NOT gain an interval loop for this purpose.

#### Scenario: Interval is configurable
- **WHEN** a host sets the sync interval option
- **THEN** the timer fires at that interval

#### Scenario: A run is still in progress
- **WHEN** the timer elapses while the previous run has not finished
- **THEN** a second concurrent run is not started

#### Scenario: Catching up after downtime
- **WHEN** the host boots after being off past a scheduled time
- **THEN** a run is scheduled shortly after boot rather than waiting a full interval

#### Scenario: A failing run is visible
- **WHEN** a sync run exits non-zero
- **THEN** the failure is recorded in the journal and does not prevent the next scheduled run

#### Scenario: Sync can be enabled without the dashboard
- **WHEN** a host enables scheduled sync only
- **THEN** no dashboard unit is created

### Requirement: The dashboard is a separately enabled unit with a configurable bind
The module SHALL provide the dashboard as its own long-running unit, whose listen address and port are configurable, and which defaults to loopback so a host must opt in to a wider bind.

#### Scenario: Default bind
- **WHEN** the dashboard is enabled with no address configured
- **THEN** it listens on loopback only

#### Scenario: Configured bind
- **WHEN** a host sets a listen address and port
- **THEN** the dashboard listens on exactly that address and port

#### Scenario: Dashboard can be enabled without sync
- **WHEN** a host enables the dashboard only
- **THEN** no sync timer is created

### Requirement: State lives under /var/lib by default
Data, database and log locations SHALL default under a startaste directory in `/var/lib`, the module SHALL create them, and they SHALL be writable by the service while the rest of the filesystem is not.

#### Scenario: Default locations
- **WHEN** no paths are configured
- **THEN** the database, data directory and log all resolve under `/var/lib/startaste`

#### Scenario: Directories exist before first start
- **WHEN** a unit starts for the first time on a host that has never run startaste
- **THEN** its state directories already exist with the service user as owner, so the unit does not fail while setting up its namespace

#### Scenario: Units share one database
- **WHEN** both the sync timer and the dashboard are enabled
- **THEN** they operate on the same database file

#### Scenario: Writable paths are limited to state
- **WHEN** a unit runs
- **THEN** only the configured state locations are writable

### Requirement: Credentials reach the units only as a file path
Source credentials SHALL be supplied as a path to a file read at unit start, never as an option value, so that no credential is written into the world-readable Nix store. A `.env` file SHALL NOT be relied upon.

#### Scenario: Credentials configured
- **WHEN** a host points the module at a credentials file
- **THEN** the sync unit receives those variables in its environment

#### Scenario: No credential value in the store
- **WHEN** the configuration is evaluated
- **THEN** no credential value appears in any option or in any generated store path

#### Scenario: A .env is not reachable anyway
- **WHEN** a unit runs with the home directory protected
- **THEN** a `.env` in a user's home cannot be read, so credentials must come from the configured file

#### Scenario: Missing credentials
- **WHEN** the sync unit runs with no credentials available for any source
- **THEN** it exits with the existing clear error rather than a traceback

### Requirement: Units run hardened as a dedicated system user
The module SHALL create a system user and group for the service and SHALL apply a hardened systemd profile to its units.

#### Scenario: Dedicated user
- **WHEN** the service is enabled without a user configured
- **THEN** a system user and group are created for it and the units run as that user

#### Scenario: Hardened profile
- **WHEN** a unit runs
- **THEN** the filesystem is protected apart from its writable state, the home directory is protected, no new privileges may be acquired, and capabilities are dropped

#### Scenario: Restart on failure
- **WHEN** a long-running unit exits unexpectedly
- **THEN** systemd restarts it

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
