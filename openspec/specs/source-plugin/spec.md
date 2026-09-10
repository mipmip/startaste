# source-plugin Specification

## Purpose
The contract a source implements and how sources are discovered, so that adding
a source is a matter of adding a module rather than editing the CLI, the export
or the dashboard.

## Requirements

### Requirement: A source implements a common interface
Each source SHALL expose its name, the item types it produces, its database models, help text for the environment variables it needs, a check for whether it is configured, and a sync method.

#### Scenario: Metadata
- **WHEN** a source is instantiated
- **THEN** it exposes its name, item types, models and environment help

#### Scenario: Configuration check
- **WHEN** a source is asked whether it is configured
- **THEN** it answers true only when every variable it needs is set

#### Scenario: Syncing
- **WHEN** a configured source is asked to sync
- **THEN** it fetches from its service and stores what it finds

### Requirement: Sources are discoverable through a registry
Sources SHALL be reachable through a registry, so consumers never import a source module directly.

#### Scenario: All sources
- **WHEN** the registry is asked for every source
- **THEN** it returns each known source

#### Scenario: Configured sources only
- **WHEN** the registry is asked for configured sources
- **THEN** it returns only those whose variables are set

#### Scenario: By name
- **WHEN** the registry is asked for a source by name
- **THEN** it returns that source

#### Scenario: Unknown name
- **WHEN** an unknown name is requested
- **THEN** it fails with an error listing the available names

### Requirement: Each source's tables are namespaced
A source's models SHALL use table names prefixed with the source name, so two sources cannot collide.

#### Scenario: Table names
- **WHEN** a source declares models
- **THEN** each table name begins with that source's name

### Requirement: Adding a source requires no changes to shared surfaces
Registering a source SHALL be enough for it to appear in sync, export and the dashboard.

#### Scenario: A newly registered source
- **WHEN** a source is added to the registry
- **THEN** its tables are created, its items are exported under its own key, and it appears in the overview without editing those surfaces
