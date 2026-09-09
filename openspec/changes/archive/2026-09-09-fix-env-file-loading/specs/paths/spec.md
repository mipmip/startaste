## MODIFIED Requirements

### Requirement: .env loading is cwd-only
The `.env` file SHALL be discovered from the current working directory (or the nearest parent directory containing one) and from nowhere else, and SHALL be loaded once at CLI startup before any subcommand or source reads its configuration.

#### Scenario: .env in cwd
- **WHEN** a `.env` file exists in the current working directory
- **THEN** it is loaded for credentials

#### Scenario: .env in a parent of cwd
- **WHEN** no `.env` exists in the current working directory but one exists in a parent directory
- **THEN** the nearest parent `.env` is loaded for credentials

#### Scenario: No .env in XDG dirs
- **WHEN** a `.env` file exists in the XDG data or config directory
- **THEN** it is NOT loaded

#### Scenario: Installed binary outside the project tree
- **WHEN** `startaste` runs from an installed location (e.g. a nix store path or a virtualenv) and a `.env` exists in the current working directory
- **THEN** that `.env` is loaded, independent of where the package files themselves live

#### Scenario: Loaded for every subcommand
- **WHEN** any subcommand runs (`sync`, `export`, `serve`)
- **THEN** the `.env` values are present in the environment before the subcommand reads configuration

#### Scenario: Loaded regardless of source import order
- **WHEN** only one source is used (e.g. `startaste sync github`)
- **THEN** the `.env` values are loaded without depending on another source's module being imported

#### Scenario: No .env present
- **WHEN** no `.env` file is found
- **THEN** existing environment variables are used and no error is raised

#### Scenario: Environment takes precedence
- **WHEN** a variable is already set in the environment and also present in `.env`
- **THEN** the value from the environment is used
