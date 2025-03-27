# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## Upcoming Releases

### Added

### Changed

### Fixed

### Removed

### Deprecated

### Security


## [v1.1.3] - 2025-03-27

### Fixed
- Make ModBot don't auto-approve duplicated content from new-user-content.

### Security
- Solve security vulnerability.


## [v1.1.2] - 2025-01-15

### Changed
- Replace Envkey with Infisical.

### Security
- Solve security vulneravility by updating Django.


## [v1.1.1] - 2024-10-29

### Added
- Explicitly mark message as NEW USER CONTENT
- Cut message if it's too long to post

### Changed
- Include new-user-content channel in /current-count command
- Include new-user-content channel in "oldest unmoderated piece of content"

### Fixed
- Add channel ids to envkey to fix conversations.list API rate limit error.


## [v1.1.0] - 2024-10-10

### Added
- Add justfile, changelog and pre-commit hooks.
- Add content pre-approval for new users.

### Changed
- Use slack_bolt library instead of old implementation and remove unused code.
- Use envkey in local development environment (not only in prod), to simplify local setup.


## [v1.0.0] - 2024-08-30

### Added
- Previous 8 years of work!
