# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-29

### Added
- **Already-installed detection**: Scripts now check if packages are already installed and skip them with visual feedback for all package managers (apt, pacman, rpm, flatpak, snap)
- **Network retry logic**: Data fetcher now retries failed requests 3 times with exponential backoff (5s, 10s, 20s delays) and falls back to cache
- **Package manager lock detection**: Scripts wait for apt, pacman, and zypper locks to be released before proceeding
- **Enhanced security features**:
  - Advanced shell escaping for package names to prevent command injection
  - Stricter package name validation with comprehensive character checks
  - Root user prevention checks in all generated scripts
  - Package manager availability checks for flatpak and snap

### Fixed
- Infinite recursion risk in cache fallback logic when both network and cache fail
- Flatpak `is_installed()` function now uses exact match to prevent substring false positives
- Exponential backoff timing now correctly implements all 3 delays (5s, 10s, 20s)

### Changed
- Moved `time` import to module level for cleaner code organization
- Removed unused `escape_shell_string()` function to eliminate dead code

### Security
- All "Must have" security features from roadmap now implemented
- Safe command execution with proper escaping throughout
- Network error detection with smart retry logic

## [1.0.1] - 2024-XX-XX

### Initial Release
- Multi-distro support (Ubuntu, Debian, Arch, Fedora, openSUSE, Nix)
- Flatpak & Snap universal package support
- 150+ curated applications across 15 categories
- Smart AUR detection & yay auto-installation
- Script generation capabilities
- Offline cache support

[1.1.0]: https://github.com/Gururagavendra/tuxmate-cli/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Gururagavendra/tuxmate-cli/releases/tag/v1.0.1
