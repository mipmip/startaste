## ADDED Requirements

### Requirement: Serve command starts local web server
The `startaste serve` command SHALL start a local Flask web server serving the dashboard.

#### Scenario: Default port
- **WHEN** user runs `startaste serve`
- **THEN** server starts on `http://localhost:8421`

#### Scenario: Custom port
- **WHEN** user runs `startaste serve --port 9000`
- **THEN** server starts on `http://localhost:9000`

#### Scenario: Server shutdown
- **WHEN** user presses Ctrl+C
- **THEN** server shuts down gracefully

### Requirement: Dashboard is read-only
The dashboard SHALL only read from the database. No write operations.

#### Scenario: No data modification
- **WHEN** any dashboard page is loaded
- **THEN** no database writes occur
