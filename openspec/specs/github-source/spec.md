# github-source Specification

## Purpose
How the GitHub source authenticates, fetches starred repositories, and stores
them.

## Requirements

### Requirement: Authentication uses a personal access token
The GitHub source SHALL authenticate with a personal access token from the environment, and SHALL report itself unconfigured when the token is absent.

#### Scenario: Token present
- **WHEN** the token variable is set
- **THEN** the source reports itself configured

#### Scenario: Token absent
- **WHEN** the token variable is not set
- **THEN** the source reports itself unconfigured, and a sync attempt exits with a clear error

### Requirement: Starred repositories are fetched by page
The GitHub source SHALL fetch the authenticated user's starred repositories through the API's own pagination, requesting pages until one comes back empty.

#### Scenario: First sync
- **WHEN** nothing is stored yet
- **THEN** every page is requested until an empty page ends the walk

#### Scenario: Later sync
- **WHEN** items are already stored
- **THEN** the walk stops once every repository on a page is already known

### Requirement: Each star is stored with its full API record
A starred repository SHALL be stored under its GitHub repository id, with the full API response as its body and the starred timestamp as its time.

#### Scenario: Storing a star
- **WHEN** a starred repository is fetched
- **THEN** it is stored with the repository id as its identifier, the response as its body, and the starred date as its timestamp

### Requirement: Requests are paced to respect rate limits
The GitHub source SHALL pace its requests, leaving a delay between them.

#### Scenario: Several pages
- **WHEN** more than one page is fetched
- **THEN** consecutive requests are separated by a delay of at least 0.2 seconds
