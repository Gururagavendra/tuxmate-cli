# [WIP] TuxMate CLI - Comprehensive Test Plan

## Overview
This document outlines all test scenarios for tuxmate-cli to ensure production-grade quality. Tests are organized from high-level integration tests to low-level unit tests.

---

## 1. High-Level Integration Tests

### 1.1 End-to-End Installation Workflows

#### TC-E2E-001: Fresh Installation (Ubuntu)
**Objective**: Verify complete installation flow on Ubuntu system
- **Preconditions**: Clean Ubuntu system, no cache
- **Steps**:
  1. Run `tuxmate-cli install firefox neovim git`
  2. Verify script generation
  3. Execute script
  4. Verify packages installed via `dpkg -l`
- **Expected**: All packages installed successfully
- **Priority**: Critical

#### TC-E2E-002: Fresh Installation (Arch Linux)
**Objective**: Verify installation with native + AUR packages
- **Preconditions**: Clean Arch system
- **Steps**:
  1. Run `tuxmate-cli install firefox brave-bin discord`
  2. Verify yay auto-installation if missing
  3. Verify AUR packages installed
- **Expected**: Native and AUR packages both installed
- **Priority**: Critical

#### TC-E2E-003: Fresh Installation (Fedora)
**Objective**: Verify installation on Fedora system
- **Preconditions**: Clean Fedora system
- **Steps**:
  1. Run `tuxmate-cli install firefox neovim`
  2. Verify dnf commands in script
- **Expected**: Packages installed via dnf
- **Priority**: High

#### TC-E2E-004: Mixed Package Sources
**Objective**: Install packages from multiple sources
- **Steps**:
  1. Run `tuxmate-cli install firefox spotify --flatpak --snap`
  2. Verify native, Flatpak, and Snap packages categorized
  3. Execute generated script
- **Expected**: All packages installed from appropriate sources
- **Priority**: High

#### TC-E2E-005: Large Batch Installation
**Objective**: Stress test with 50+ packages
- **Steps**:
  1. Install 50+ packages in one command
  2. Monitor memory usage and execution time
- **Expected**: No crashes, reasonable performance
- **Priority**: Medium

---

## 2. Data Fetching & Parsing Tests

### 2.1 TuxmateDataFetcher Tests

#### TC-DATA-001: Fresh Data Fetch (No Cache)
**Objective**: Verify default behavior fetches fresh data
- **Steps**:
  1. Delete cache if exists
  2. Initialize `TuxmateDataFetcher(use_cache=False)`
  3. Verify HTTP request to GitHub
- **Expected**: Data fetched from GitHub, cache not created
- **Priority**: Critical

#### TC-DATA-002: Cache Hit
**Objective**: Verify cache usage when enabled
- **Steps**:
  1. Run `tuxmate-cli update`
  2. Run `tuxmate-cli list --cache`
  3. Verify no HTTP request
- **Expected**: Data loaded from cache file
- **Priority**: High

#### TC-DATA-003: Cache Expiry
**Objective**: Verify 24-hour cache expiry
- **Steps**:
  1. Create cache file with mtime > 24 hours old
  2. Run `TuxmateDataFetcher(use_cache=True)`
- **Expected**: Cache invalidated, fresh data fetched
- **Priority**: High

#### TC-DATA-004: Corrupted Cache Handling
**Objective**: Handle invalid JSON cache gracefully
- **Steps**:
  1. Write invalid JSON to cache file
  2. Run `TuxmateDataFetcher(use_cache=True)`
- **Expected**: Re-fetch from GitHub, overwrite cache
- **Priority**: High

#### TC-DATA-005: Network Failure with Valid Cache
**Objective**: Fallback to stale cache on network error
- **Steps**:
  1. Create valid cache
  2. Disconnect network
  3. Run `TuxmateDataFetcher(use_cache=False)`
- **Expected**: Load from stale cache with warning
- **Priority**: Medium

#### TC-DATA-006: Network Failure without Cache
**Objective**: Fail gracefully when no cache available
- **Steps**:
  1. Delete cache
  2. Disconnect network
  3. Run any CLI command
- **Expected**: Clear error message, exit code 1
- **Priority**: High

#### TC-DATA-007: GitHub API Rate Limiting
**Objective**: Handle rate limit errors
- **Steps**:
  1. Simulate rate limit response (403)
  2. Run CLI command
- **Expected**: Informative error, suggest using cache
- **Priority**: Medium

#### TC-DATA-008: Malformed data.ts
**Objective**: Handle unexpected data.ts structure
- **Steps**:
  1. Mock data.ts with invalid TypeScript
  2. Test parsing
- **Expected**: Clear error message
- **Priority**: High

#### TC-DATA-009: JavaScript Evaluation Security
**Objective**: Ensure dukpy doesn't execute malicious code
- **Steps**:
  1. Test with data.ts containing file system access attempts
  2. Verify sandboxing
- **Expected**: No file system access
- **Priority**: Critical

#### TC-DATA-010: Large data.ts (10,000+ Apps)
**Objective**: Stress test parser with large datasets
- **Steps**:
  1. Generate data.ts with 10,000 apps
  2. Measure parsing time and memory
- **Expected**: Completes within 5 seconds, < 500MB RAM
- **Priority**: Low

---

### 2.2 Distro Array Parsing Tests

#### TC-DISTRO-001: Parse All Distros
**Objective**: Verify all distros from data.ts are loaded
- **Steps**:
  1. Fetch data
  2. Verify `fetcher.distros` contains expected distros
- **Expected**: All distros present (ubuntu, debian, arch, fedora, opensuse, nix, flatpak, snap)
- **Priority**: Critical

#### TC-DISTRO-002: Dynamic Distro Addition
**Objective**: Handle new distros added to tuxmate
- **Steps**:
  1. Mock data.ts with new distro "alpine"
  2. Parse data
- **Expected**: Alpine distro loaded dynamically
- **Priority**: High

#### TC-DISTRO-003: Missing Distro Fields
**Objective**: Handle incomplete distro definitions
- **Steps**:
  1. Mock distro without `installPrefix`
  2. Test parsing
- **Expected**: Graceful error or default value
- **Priority**: Medium

---

### 2.3 Apps Array Parsing Tests

#### TC-APP-001: Parse Simple App
**Objective**: Parse app with basic fields
- **Steps**:
  1. Mock app: `{ id: 'test', name: 'Test', category: 'Test', targets: { ubuntu: 'test-pkg' } }`
  2. Parse and verify
- **Expected**: AppData object created correctly
- **Priority**: Critical

#### TC-APP-002: Parse App with Icon Functions
**Objective**: Handle JavaScript function calls in icon field
- **Steps**:
  1. Mock app with `icon: si('firefox', '#FF7139')`
  2. Parse data
- **Expected**: Icon URL generated correctly
- **Priority**: High

#### TC-APP-003: Parse App with Missing Fields
**Objective**: Handle optional fields (description, unavailableReason)
- **Steps**:
  1. Mock app without description
  2. Parse and verify defaults
- **Expected**: Empty string or None for missing fields
- **Priority**: Medium

#### TC-APP-004: Parse App with All Targets
**Objective**: App available on all distros
- **Steps**:
  1. Mock app with targets for all distros
  2. Verify targets dict
- **Expected**: All distros in targets
- **Priority**: High

#### TC-APP-005: Parse App with Complex Targets
**Objective**: Handle multi-word package names, special chars
- **Steps**:
  1. Mock app: `{ ubuntu: 'lib-foo-bar-dev' }`
  2. Parse and verify
- **Expected**: Package name preserved exactly
- **Priority**: Medium

---

## 3. Distro Detection Tests

### 3.1 detect_distro() Function Tests

#### TC-DETECT-001: Ubuntu Detection
**Objective**: Detect Ubuntu and derivatives
- **Test Cases**:
  - Pure Ubuntu (ID=ubuntu)
  - Pop!_OS (ID=pop, ID_LIKE=ubuntu)
  - Linux Mint (ID=linuxmint, ID_LIKE=ubuntu)
  - Elementary OS (ID=elementary, ID_LIKE=ubuntu)
- **Expected**: Returns "ubuntu"
- **Priority**: Critical

#### TC-DETECT-002: Debian Detection
**Objective**: Detect Debian
- **Test Cases**:
  - Pure Debian (ID=debian)
  - Debian-based without ubuntu in ID_LIKE
- **Expected**: Returns "debian"
- **Priority**: Critical

#### TC-DETECT-003: Arch Detection
**Objective**: Detect Arch and derivatives
- **Test Cases**:
  - Pure Arch (ID=arch)
  - Manjaro (ID=manjaro, ID_LIKE=arch)
  - EndeavourOS (ID=endeavouros, ID_LIKE=arch)
  - Garuda (ID=garuda, ID_LIKE=arch)
- **Expected**: Returns "arch"
- **Priority**: Critical

#### TC-DETECT-004: Fedora Detection
**Objective**: Detect Fedora and derivatives
- **Test Cases**:
  - Pure Fedora (ID=fedora)
  - Fedora-based (ID_LIKE=fedora)
- **Expected**: Returns "fedora"
- **Priority**: Critical

#### TC-DETECT-005: openSUSE Detection
**Objective**: Detect openSUSE variants
- **Test Cases**:
  - openSUSE Leap (ID=opensuse-leap)
  - openSUSE Tumbleweed (ID=opensuse-tumbleweed)
  - Generic (ID=opensuse)
- **Expected**: Returns "opensuse"
- **Priority**: High

#### TC-DETECT-006: Missing /etc/os-release
**Objective**: Handle systems without os-release file
- **Steps**:
  1. Mock missing file
  2. Call detect_distro()
- **Expected**: Returns None
- **Priority**: High

#### TC-DETECT-007: Malformed os-release
**Objective**: Handle invalid os-release format
- **Steps**:
  1. Mock os-release with no ID field
  2. Call detect_distro()
- **Expected**: Returns None or best guess
- **Priority**: Medium

#### TC-DETECT-008: Unsupported Distro
**Objective**: Handle unknown distributions
- **Steps**:
  1. Mock os-release: ID=gentoo
  2. Call detect_distro()
- **Expected**: Returns None
- **Priority**: Medium

---

## 4. CLI Command Tests

### 4.1 List Command Tests

#### TC-CLI-LIST-001: List All Packages
**Objective**: Display all packages
- **Steps**: `tuxmate-cli list`
- **Expected**: Table with 50+ packages (truncated)
- **Priority**: Critical

#### TC-CLI-LIST-002: List with Category Filter
**Objective**: Filter by category
- **Steps**: `tuxmate-cli list --category "Web Browsers"`
- **Expected**: Only browser packages shown
- **Priority**: High

#### TC-CLI-LIST-003: List with Distro Filter
**Objective**: Filter by distro availability
- **Steps**: `tuxmate-cli list --distro arch`
- **Expected**: Only packages available on Arch
- **Priority**: High

#### TC-CLI-LIST-004: List with Cache Flag
**Objective**: Use cached data
- **Steps**: `tuxmate-cli list --cache`
- **Expected**: Loads from cache, no network request
- **Priority**: Medium

#### TC-CLI-LIST-005: List with No Results
**Objective**: Handle empty results
- **Steps**: `tuxmate-cli list --category "NonExistent"`
- **Expected**: "No packages found" message
- **Priority**: Low

---

### 4.2 Search Command Tests

#### TC-CLI-SEARCH-001: Search by Name
**Objective**: Find packages by name
- **Steps**: `tuxmate-cli search firefox`
- **Expected**: Firefox and related browsers
- **Priority**: Critical

#### TC-CLI-SEARCH-002: Search by Description
**Objective**: Search in description field
- **Steps**: `tuxmate-cli search "code editor"`
- **Expected**: VS Code, Neovim, etc.
- **Priority**: High

#### TC-CLI-SEARCH-003: Case-Insensitive Search
**Objective**: Search is case-insensitive
- **Steps**: `tuxmate-cli search FIREFOX`
- **Expected**: Same results as lowercase
- **Priority**: Medium

#### TC-CLI-SEARCH-004: Partial Match Search
**Objective**: Match substrings
- **Steps**: `tuxmate-cli search fire`
- **Expected**: Firefox, Firewall packages
- **Priority**: High

#### TC-CLI-SEARCH-005: Search with Distro Filter
**Objective**: Combine search and distro filter
- **Steps**: `tuxmate-cli search editor --distro ubuntu`
- **Expected**: Only editors available on Ubuntu
- **Priority**: Medium

#### TC-CLI-SEARCH-006: Search No Results
**Objective**: Handle no matches
- **Steps**: `tuxmate-cli search xyz123nonexistent`
- **Expected**: "No packages found" message
- **Priority**: Low

---

### 4.3 Info Command Tests

#### TC-CLI-INFO-001: Display Package Info
**Objective**: Show detailed package information
- **Steps**: `tuxmate-cli info firefox`
- **Expected**: Name, description, category, availability table
- **Priority**: Critical

#### TC-CLI-INFO-002: Show Unavailable Reason
**Objective**: Display unavailableReason if present
- **Steps**: `tuxmate-cli info <unavailable-pkg>`
- **Expected**: Yellow note with reason
- **Priority**: High

#### TC-CLI-INFO-003: Package Not Found
**Objective**: Handle non-existent package
- **Steps**: `tuxmate-cli info nonexistent`
- **Expected**: Error message, exit code 1
- **Priority**: High

#### TC-CLI-INFO-004: Info with Cache
**Objective**: Use cached data
- **Steps**: `tuxmate-cli info firefox --cache`
- **Expected**: Info from cache
- **Priority**: Low

---

### 4.4 Install Command Tests

#### TC-CLI-INSTALL-001: Install Single Package
**Objective**: Basic installation
- **Steps**: `tuxmate-cli install firefox`
- **Expected**: Script generated and executed
- **Priority**: Critical

#### TC-CLI-INSTALL-002: Install Multiple Packages
**Objective**: Batch installation
- **Steps**: `tuxmate-cli install firefox neovim git`
- **Expected**: All packages installed
- **Priority**: Critical

#### TC-CLI-INSTALL-003: Install with Dry Run
**Objective**: Show script without executing
- **Steps**: `tuxmate-cli install firefox --dry-run`
- **Expected**: Script displayed, not executed
- **Priority**: High

#### TC-CLI-INSTALL-004: Install with Output File
**Objective**: Save script to file
- **Steps**: `tuxmate-cli install firefox -o install.sh`
- **Expected**: Script saved, not executed
- **Priority**: High

#### TC-CLI-INSTALL-005: Install with Flatpak Fallback
**Objective**: Use Flatpak for unavailable packages
- **Steps**: `tuxmate-cli install <pkg-not-on-distro> --flatpak`
- **Expected**: Flatpak used as fallback
- **Priority**: High

#### TC-CLI-INSTALL-006: Install with Snap Fallback
**Objective**: Use Snap for unavailable packages
- **Steps**: `tuxmate-cli install <pkg-not-on-distro> --snap`
- **Expected**: Snap used as fallback
- **Priority**: Medium

#### TC-CLI-INSTALL-007: Install Package Not Found
**Objective**: Handle non-existent package
- **Steps**: `tuxmate-cli install nonexistent`
- **Expected**: Error message, continue with found packages if any
- **Priority**: High

#### TC-CLI-INSTALL-008: Install with Fuzzy Match
**Objective**: Auto-correct package names
- **Steps**: `tuxmate-cli install fire` (assuming firefox exists)
- **Expected**: Suggests firefox, asks for confirmation or auto-installs
- **Priority**: Medium

#### TC-CLI-INSTALL-009: Install on Unsupported Distro
**Objective**: Handle distro without packages
- **Steps**: Install on distro where package unavailable
- **Expected**: "No packages available" message
- **Priority**: High

#### TC-CLI-INSTALL-010: Install with Keyboard Interrupt
**Objective**: Handle Ctrl+C gracefully
- **Steps**: Press Ctrl+C during installation
- **Expected**: "Installation cancelled" message, exit code 130
- **Priority**: Medium

#### TC-CLI-INSTALL-011: Install with Failed Script
**Objective**: Handle script execution failure
- **Steps**: Mock script failure (exit code 1)
- **Expected**: Error message with exit code
- **Priority**: High

---

### 4.5 Update Command Tests

#### TC-CLI-UPDATE-001: Update Cache
**Objective**: Force refresh and save cache
- **Steps**: `tuxmate-cli update`
- **Expected**: Fresh data fetched, cache saved
- **Priority**: High

#### TC-CLI-UPDATE-002: Update Network Failure
**Objective**: Handle network errors during update
- **Steps**: Disconnect network, run `tuxmate-cli update`
- **Expected**: Clear error message
- **Priority**: Medium

---

### 4.6 Categories Command Tests

#### TC-CLI-CAT-001: List All Categories
**Objective**: Display all categories with counts
- **Steps**: `tuxmate-cli categories`
- **Expected**: Table with all categories
- **Priority**: Medium

#### TC-CLI-CAT-002: Categories with Cache
**Objective**: Use cached data
- **Steps**: `tuxmate-cli categories --cache`
- **Expected**: Categories from cache
- **Priority**: Low

---

### 4.7 Distros Command Tests

#### TC-CLI-DISTRO-001: List Supported Distros
**Objective**: Display all supported distributions
- **Steps**: `tuxmate-cli distros`
- **Expected**: Table with all distros
- **Priority**: High

#### TC-CLI-DISTRO-002: Highlight Detected Distro
**Objective**: Show current distro with arrow
- **Steps**: `tuxmate-cli distros` on Ubuntu
- **Expected**: "← Detected" next to Ubuntu
- **Priority**: Medium

---

### 4.8 Script Command Tests

#### TC-CLI-SCRIPT-001: Generate Script to Stdout
**Objective**: Output script without execution
- **Steps**: `tuxmate-cli script firefox neovim`
- **Expected**: Script printed to stdout
- **Priority**: High

#### TC-CLI-SCRIPT-002: Pipe Script to Bash
**Objective**: Direct execution via pipe
- **Steps**: `tuxmate-cli script firefox | bash`
- **Expected**: Script executed directly
- **Priority**: High

#### TC-CLI-SCRIPT-003: Script with Distro Override
**Objective**: Generate for different distro
- **Steps**: `tuxmate-cli script firefox --distro arch`
- **Expected**: Arch-specific script
- **Priority**: Medium

---

### 4.9 Oneliner Command Tests

#### TC-CLI-ONELINER-001: Generate One-liner (Ubuntu)
**Objective**: Create single-line install command
- **Steps**: `tuxmate-cli oneliner firefox neovim`
- **Expected**: `sudo apt update && sudo apt install -y firefox neovim`
- **Priority**: High

#### TC-CLI-ONELINER-002: Generate One-liner (Arch)
**Objective**: Arch-specific one-liner
- **Steps**: `tuxmate-cli oneliner firefox --distro arch`
- **Expected**: `sudo pacman -Syu --needed --noconfirm firefox`
- **Priority**: High

#### TC-CLI-ONELINER-003: One-liner with No Packages
**Objective**: Handle empty package list
- **Steps**: `tuxmate-cli oneliner nonexistent`
- **Expected**: Error message
- **Priority**: Low

---

## 5. Script Generation Tests

### 5.1 ScriptGenerator Tests

#### TC-GEN-001: Initialize with Auto-Detect
**Objective**: Auto-detect distro on init
- **Steps**: `ScriptGenerator()`
- **Expected**: Distro detected from system
- **Priority**: Critical

#### TC-GEN-002: Initialize with Distro Override
**Objective**: Use specified distro
- **Steps**: `ScriptGenerator(distro='arch')`
- **Expected**: Generator uses Arch
- **Priority**: High

#### TC-GEN-003: Initialize on Unsupported Distro
**Objective**: Handle unknown distro
- **Steps**: Mock unknown distro, init generator
- **Expected**: ValueError with message
- **Priority**: High

---

### 5.2 Package Categorization Tests

#### TC-CAT-001: Categorize Native Package (Ubuntu)
**Objective**: Identify Ubuntu native package
- **Steps**: App with `targets: { ubuntu: 'firefox' }`
- **Expected**: Added to native_packages list
- **Priority**: Critical

#### TC-CAT-002: Categorize Native Package (Arch)
**Objective**: Identify Arch native package
- **Steps**: App with `targets: { arch: 'firefox' }`
- **Expected**: Added to native_packages list
- **Priority**: Critical

#### TC-CAT-003: Categorize AUR Package
**Objective**: Identify AUR package by suffix
- **Steps**: App with `targets: { arch: 'brave-bin' }`
- **Expected**: Added to aur_packages list
- **Priority**: Critical

#### TC-CAT-004: Categorize AUR Package (Known List)
**Objective**: Identify AUR package from hardcoded list
- **Steps**: App with `targets: { arch: 'spotify' }`
- **Expected**: Added to aur_packages list
- **Priority**: High

#### TC-CAT-005: Categorize Flatpak Fallback
**Objective**: Use Flatpak when native unavailable
- **Steps**: App without ubuntu target, with flatpak target, `include_flatpak=True`
- **Expected**: Added to flatpak_packages list
- **Priority**: High

#### TC-CAT-006: Categorize Snap Fallback
**Objective**: Use Snap when native unavailable
- **Steps**: App without ubuntu target, with snap target, `include_snap=True`
- **Expected**: Added to snap_packages list
- **Priority**: Medium

#### TC-CAT-007: Prioritize Native Over Flatpak
**Objective**: Native package preferred over Flatpak
- **Steps**: App with both ubuntu and flatpak targets, `include_flatpak=True`
- **Expected**: Only native package used
- **Priority**: High

---

### 5.3 AUR Detection Tests

#### TC-AUR-001: Detect -bin Suffix
**Objective**: Identify AUR package by -bin
- **Steps**: `_is_aur_package('brave-bin')`
- **Expected**: Returns True
- **Priority**: High

#### TC-AUR-002: Detect -git Suffix
**Objective**: Identify AUR package by -git
- **Steps**: `_is_aur_package('neovim-git')`
- **Expected**: Returns True
- **Priority**: High

#### TC-AUR-003: Detect -appimage Suffix
**Objective**: Identify AUR package by -appimage
- **Steps**: `_is_aur_package('joplin-appimage')`
- **Expected**: Returns True
- **Priority**: Medium

#### TC-AUR-004: Detect Known AUR Package
**Objective**: Identify from hardcoded list
- **Steps**: `_is_aur_package('spotify')`
- **Expected**: Returns True
- **Priority**: High

#### TC-AUR-005: Reject Native Package
**Objective**: Native packages not flagged as AUR
- **Steps**: `_is_aur_package('firefox')`
- **Expected**: Returns False
- **Priority**: High

---

### 5.4 Script Content Tests

#### TC-SCRIPT-001: Header and Colors
**Objective**: Verify script preamble
- **Expected**: Shebang, colors defined, `set -e`
- **Priority**: Medium

#### TC-SCRIPT-002: Banner Output
**Objective**: Verify TuxMate banner
- **Expected**: Colorful ASCII banner with distro name
- **Priority**: Low

#### TC-SCRIPT-003: Package Count Display
**Objective**: Show total package count
- **Expected**: "Installing X packages..." message
- **Priority**: Low

#### TC-SCRIPT-004: Ubuntu Install Commands
**Objective**: Verify apt commands
- **Expected**: `sudo apt update && sudo apt install -y <packages>`
- **Priority**: Critical

#### TC-SCRIPT-005: Arch Install Commands
**Objective**: Verify pacman commands
- **Expected**: `sudo pacman -Sy && sudo pacman -S --needed --noconfirm <packages>`
- **Priority**: Critical

#### TC-SCRIPT-006: Fedora Install Commands
**Objective**: Verify dnf commands
- **Expected**: `sudo dnf install -y <packages>`
- **Priority**: High

#### TC-SCRIPT-007: openSUSE Install Commands
**Objective**: Verify zypper commands
- **Expected**: `sudo zypper install -y <packages>`
- **Priority**: High

#### TC-SCRIPT-008: Nix Install Commands
**Objective**: Verify nix-env commands
- **Expected**: `nix-env -iA nixpkgs.<package>` for each
- **Priority**: Medium

#### TC-SCRIPT-009: AUR Install with Yay Check
**Objective**: Verify yay installation and usage
- **Expected**: Check for yay, install if missing, then `yay -S --needed --noconfirm <packages>`
- **Priority**: Critical

#### TC-SCRIPT-010: Flatpak Install Commands
**Objective**: Verify Flatpak setup and install
- **Expected**: Add flathub remote, install with `&` for parallel, `wait`
- **Priority**: High

#### TC-SCRIPT-011: Snap Install Commands
**Objective**: Verify Snap install commands
- **Expected**: `sudo snap install <package>`, `--classic` for known snaps
- **Priority**: Medium

#### TC-SCRIPT-012: Snap Classic Flag
**Objective**: Verify --classic for specific snaps
- **Steps**: Generate script for `code` (VS Code)
- **Expected**: `sudo snap install code --classic`
- **Priority**: High

#### TC-SCRIPT-013: Summary Section
**Objective**: Verify completion summary
- **Expected**: Green banner, package counts by type
- **Priority**: Low

#### TC-SCRIPT-014: Empty Package List
**Objective**: Handle no packages to install
- **Steps**: Generate with empty app list
- **Expected**: Minimal script or error
- **Priority**: Medium

---

### 5.5 One-liner Generation Tests

#### TC-ONELINER-001: Ubuntu One-liner
**Objective**: Generate apt one-liner
- **Expected**: `sudo apt update && sudo apt install -y <packages>`
- **Priority**: High

#### TC-ONELINER-002: Arch One-liner
**Objective**: Generate pacman one-liner
- **Expected**: `sudo pacman -Syu --needed --noconfirm <packages>`
- **Priority**: High

#### TC-ONELINER-003: Fedora One-liner
**Objective**: Generate dnf one-liner
- **Expected**: `sudo dnf install -y <packages>`
- **Priority**: High

#### TC-ONELINER-004: Nix One-liner
**Objective**: Generate nix-env one-liner
- **Expected**: `nix-env -iA nixpkgs.pkg1 nixpkgs.pkg2 ...`
- **Priority**: Medium

#### TC-ONELINER-005: Unsupported Distro One-liner
**Objective**: Handle unknown distro
- **Expected**: `# Unknown distribution` comment
- **Priority**: Low

---

## 6. Bash Wrapper Tests (tuxmate-cli.sh)

### 6.1 Dependency Checks

#### TC-WRAP-001: Python Version Check (Valid)
**Objective**: Detect Python 3.10+
- **Steps**: Mock Python 3.11, run script
- **Expected**: Passes check
- **Priority**: Critical

#### TC-WRAP-002: Python Version Check (Invalid)
**Objective**: Reject Python < 3.10
- **Steps**: Mock Python 3.9, run script
- **Expected**: Error message, exit
- **Priority**: Critical

#### TC-WRAP-003: Python Not Installed
**Objective**: Handle missing Python
- **Steps**: Mock no python3 command
- **Expected**: Error with install suggestion
- **Priority**: High

#### TC-WRAP-004: UV Installation Check
**Objective**: Detect uv package manager
- **Steps**: Mock uv present, run script
- **Expected**: Skips uv installation
- **Priority**: Medium

#### TC-WRAP-005: UV Auto-Install
**Objective**: Install uv if missing
- **Steps**: Mock no uv, run script
- **Expected**: Installs uv via curl script
- **Priority**: High

---

### 6.2 Virtual Environment Setup

#### TC-WRAP-006: Venv Creation
**Objective**: Create .venv on first run
- **Steps**: Delete .venv, run script
- **Expected**: `uv sync` executed, .venv created
- **Priority**: High

#### TC-WRAP-007: Venv Reuse
**Objective**: Reuse existing .venv
- **Steps**: .venv exists, run script
- **Expected**: Skips `uv sync`
- **Priority**: Medium

---

### 6.3 Wrapper Execution

#### TC-WRAP-008: Run with Arguments
**Objective**: Pass arguments to CLI
- **Steps**: `./tuxmate-cli.sh list`
- **Expected**: Executes `uv run python -m tuxmate_cli.cli list`
- **Priority**: Critical

#### TC-WRAP-009: Run without Arguments
**Objective**: Show help when no args
- **Steps**: `./tuxmate-cli.sh`
- **Expected**: Prints banner and `--help` output
- **Priority**: High

#### TC-WRAP-010: Banner Display
**Objective**: Show TuxMate banner
- **Steps**: `./tuxmate-cli.sh`
- **Expected**: Colorful ASCII banner
- **Priority**: Low

---

## 7. Error Handling Tests

### 7.1 Network Errors

#### TC-ERR-001: Connection Timeout
**Objective**: Handle slow/no network
- **Steps**: Mock 30s timeout on GitHub request
- **Expected**: Error after 30s, try cache fallback
- **Priority**: High

#### TC-ERR-002: DNS Failure
**Objective**: Handle DNS resolution errors
- **Steps**: Mock DNS failure
- **Expected**: Clear error message
- **Priority**: Medium

#### TC-ERR-003: HTTP 404 Error
**Objective**: Handle missing data.ts
- **Steps**: Mock 404 response
- **Expected**: Error message
- **Priority**: Medium

#### TC-ERR-004: HTTP 500 Error
**Objective**: Handle GitHub server errors
- **Steps**: Mock 500 response
- **Expected**: Error message, retry suggestion
- **Priority**: Medium

---

### 7.2 File System Errors

#### TC-ERR-005: Cache Directory Permission Denied
**Objective**: Handle read-only cache dir
- **Steps**: Mock permission error on cache creation
- **Expected**: Error or fallback to temp cache
- **Priority**: Medium

#### TC-ERR-006: Disk Full
**Objective**: Handle out-of-disk-space
- **Steps**: Mock disk full error
- **Expected**: Clear error message
- **Priority**: Low

---

### 7.3 Input Validation Errors

#### TC-ERR-007: Invalid Category Name
**Objective**: Handle non-existent category
- **Steps**: `tuxmate-cli list --category "InvalidCat"`
- **Expected**: "No packages found" (graceful)
- **Priority**: Low

#### TC-ERR-008: Invalid Distro Name
**Objective**: Handle unsupported distro
- **Steps**: `tuxmate-cli install firefox --distro invalid`
- **Expected**: Error message listing valid distros
- **Priority**: Medium

#### TC-ERR-009: Invalid Package ID
**Objective**: Handle typo in package name
- **Steps**: `tuxmate-cli install firefoxx`
- **Expected**: "Package not found" or suggest correction
- **Priority**: Medium

---

### 7.4 Script Execution Errors

#### TC-ERR-010: Permission Denied (sudo)
**Objective**: Handle sudo failure
- **Steps**: Run install without sudo rights
- **Expected**: Clear error about sudo requirement
- **Priority**: High

#### TC-ERR-011: Package Manager Not Found
**Objective**: Handle missing package manager
- **Steps**: Mock distro without apt/pacman/etc.
- **Expected**: Error message
- **Priority**: Medium

#### TC-ERR-012: Package Not Found in Repo
**Objective**: Handle package unavailable in distro repo
- **Steps**: Install package not in repositories
- **Expected**: Package manager error (not CLI crash)
- **Priority**: Medium

---

## 8. Performance Tests

### 8.1 Benchmark Tests

#### TC-PERF-001: Data Fetch Time
**Objective**: Measure GitHub fetch time
- **Target**: < 3 seconds on good network
- **Priority**: Medium

#### TC-PERF-002: Data Parse Time
**Objective**: Measure dukpy parsing time
- **Target**: < 2 seconds for full data.ts
- **Priority**: Medium

#### TC-PERF-003: Cache Load Time
**Objective**: Measure cache read time
- **Target**: < 0.5 seconds
- **Priority**: Low

#### TC-PERF-004: Search Performance
**Objective**: Search 150+ apps quickly
- **Target**: < 0.1 seconds
- **Priority**: Low

#### TC-PERF-005: Script Generation Time
**Objective**: Generate script for 50 packages
- **Target**: < 1 second
- **Priority**: Low

---

### 8.2 Memory Tests

#### TC-MEM-001: Memory Usage (Normal)
**Objective**: Measure baseline memory
- **Target**: < 100MB for typical usage
- **Priority**: Low

#### TC-MEM-002: Memory Usage (Large Dataset)
**Objective**: Handle 10,000+ apps
- **Target**: < 500MB
- **Priority**: Low

---

## 9. Security Tests

### 9.1 Input Sanitization

#### TC-SEC-001: SQL Injection in Search
**Objective**: Prevent SQL-like attacks (not applicable but test)
- **Steps**: `tuxmate-cli search "'; DROP TABLE--"`
- **Expected**: Treated as literal string
- **Priority**: Low

#### TC-SEC-002: Command Injection in Package Names
**Objective**: Prevent shell injection via package names
- **Steps**: Mock package with name `firefox; rm -rf /`
- **Expected**: Escaped or rejected
- **Priority**: Critical

#### TC-SEC-003: Path Traversal in Output File
**Objective**: Prevent writing to arbitrary paths
- **Steps**: `tuxmate-cli install firefox -o ../../etc/passwd`
- **Expected**: Reject or sanitize path
- **Priority**: High

---

### 9.2 Sandbox Tests

#### TC-SEC-004: JavaScript Sandbox (File Read)
**Objective**: Ensure dukpy cannot read files
- **Steps**: Mock data.ts with `require('fs')`
- **Expected**: Error or no file access
- **Priority**: Critical

#### TC-SEC-005: JavaScript Sandbox (Network)
**Objective**: Ensure dukpy cannot make network requests
- **Steps**: Mock data.ts with fetch/http
- **Expected**: Error or no network access
- **Priority**: Critical

---

## 10. Compatibility Tests

### 10.1 Python Version Compatibility

#### TC-COMPAT-001: Python 3.10
**Objective**: Works on Python 3.10
- **Priority**: Critical

#### TC-COMPAT-002: Python 3.11
**Objective**: Works on Python 3.11
- **Priority**: Critical

#### TC-COMPAT-003: Python 3.12
**Objective**: Works on Python 3.12
- **Priority**: Critical

#### TC-COMPAT-004: Python 3.13
**Objective**: Works on Python 3.13
- **Priority**: High

---

### 10.2 Distro Compatibility

#### TC-COMPAT-005: Ubuntu 24.04 LTS
**Objective**: Full functionality on Ubuntu 24.04
- **Priority**: Critical

#### TC-COMPAT-006: Ubuntu 22.04 LTS
**Objective**: Full functionality on Ubuntu 22.04
- **Priority**: Critical

#### TC-COMPAT-007: Debian 12
**Objective**: Full functionality on Debian 12
- **Priority**: High

#### TC-COMPAT-008: Arch Linux (Latest)
**Objective**: Full functionality on rolling Arch
- **Priority**: Critical

#### TC-COMPAT-009: Manjaro (Latest)
**Objective**: Full functionality on Manjaro
- **Priority**: High

#### TC-COMPAT-010: Fedora 40
**Objective**: Full functionality on Fedora 40
- **Priority**: High

#### TC-COMPAT-011: openSUSE Tumbleweed
**Objective**: Full functionality on Tumbleweed
- **Priority**: Medium

#### TC-COMPAT-012: Pop!_OS 22.04
**Objective**: Detects as Ubuntu, works correctly
- **Priority**: High

---

### 10.3 Terminal Compatibility

#### TC-COMPAT-013: GNOME Terminal
**Objective**: Rich output renders correctly
- **Priority**: High

#### TC-COMPAT-014: Alacritty
**Objective**: Colors and tables work
- **Priority**: Medium

#### TC-COMPAT-015: Kitty
**Objective**: Full rendering support
- **Priority**: Medium

#### TC-COMPAT-016: Non-Color Terminal
**Objective**: Graceful fallback without colors
- **Steps**: Export `NO_COLOR=1`, run CLI
- **Expected**: Plain text output
- **Priority**: Low

---

## 11. Edge Cases & Stress Tests

### 11.1 Edge Cases

#### TC-EDGE-001: Empty Package List
**Objective**: Handle zero packages
- **Steps**: `tuxmate-cli list` when data.ts is empty
- **Expected**: "No packages found"
- **Priority**: Low

#### TC-EDGE-002: Single App in Database
**Objective**: Works with minimal data
- **Priority**: Low

#### TC-EDGE-003: App with No Targets
**Objective**: Handle app unavailable on all distros
- **Steps**: Mock app with empty targets dict
- **Expected**: Skipped or marked unavailable
- **Priority**: Medium

#### TC-EDGE-004: Unicode in Package Names
**Objective**: Handle non-ASCII characters
- **Steps**: Mock app with name "Firefox 中文"
- **Expected**: Displays correctly
- **Priority**: Low

#### TC-EDGE-005: Very Long Package Name
**Objective**: Handle 100+ char names
- **Priority**: Low

#### TC-EDGE-006: Very Long Description
**Objective**: Handle 1000+ char descriptions
- **Expected**: Truncated or wrapped
- **Priority**: Low

---

### 11.2 Stress Tests

#### TC-STRESS-001: Install 100 Packages
**Objective**: Stress test batch install
- **Steps**: `tuxmate-cli install <100 packages>`
- **Expected**: Completes without crash
- **Priority**: Medium

#### TC-STRESS-002: Rapid Repeated Commands
**Objective**: Run list/search 1000 times
- **Expected**: No memory leaks or crashes
- **Priority**: Low

#### TC-STRESS-003: Concurrent Executions
**Objective**: Run multiple instances simultaneously
- **Steps**: Start 10 parallel `tuxmate-cli list` commands
- **Expected**: All complete successfully
- **Priority**: Low

---

## 12. User Experience Tests

### 12.1 Output Readability

#### TC-UX-001: Table Alignment
**Objective**: Tables are properly aligned
- **Priority**: Low

#### TC-UX-002: Color Consistency
**Objective**: Colors match semantics (green=success, red=error)
- **Priority**: Low

#### TC-UX-003: Progress Indicators
**Objective**: Spinner shows during data fetch
- **Priority**: Low

---

### 12.2 Help & Documentation

#### TC-UX-004: Help Command
**Objective**: `--help` shows useful info
- **Steps**: `tuxmate-cli --help`
- **Expected**: Clear command descriptions
- **Priority**: High

#### TC-UX-005: Subcommand Help
**Objective**: `tuxmate-cli install --help`
- **Expected**: Command-specific help
- **Priority**: High

#### TC-UX-006: Version Command
**Objective**: `--version` shows version
- **Steps**: `tuxmate-cli --version`
- **Expected**: "tuxmate-cli, version 0.1.0"
- **Priority**: Medium

---

### 12.3 Error Messages

#### TC-UX-007: Clear Error on Package Not Found
**Objective**: Helpful message for missing packages
- **Expected**: "Package 'xyz' not found. Did you mean: <suggestions>?"
- **Priority**: High

#### TC-UX-008: Clear Error on Unsupported Distro
**Objective**: Helpful message for auto-detect failure
- **Expected**: List supported distros, suggest --distro flag
- **Priority**: High

---

## 13. Regression Tests

### 13.1 Fixed Bugs (Future)

#### TC-REG-001: [Placeholder for future bug fixes]
**Objective**: Ensure previously fixed bugs don't reappear
- **Priority**: Varies

---

## 14. Integration with TuxSync

### 14.1 Profile Restoration

#### TC-INTEG-001: TuxSync Calls tuxmate-cli
**Objective**: Verify TuxSync can invoke tuxmate-cli
- **Steps**: Mock TuxSync calling `tuxmate-cli install <packages>`
- **Expected**: Packages installed
- **Priority**: High

#### TC-INTEG-002: Package List from TuxSync
**Objective**: Handle package list from config file
- **Steps**: Pass 50+ packages from TuxSync profile
- **Expected**: All installed
- **Priority**: High

---

## 15. Documentation Tests

### 15.1 README Accuracy

#### TC-DOC-001: README Examples Work
**Objective**: All README code examples execute successfully
- **Steps**: Copy-paste each example from README.md, run
- **Expected**: No errors
- **Priority**: High

#### TC-DOC-002: Installation Instructions
**Objective**: Fresh install following README
- **Steps**: Follow quick install steps on clean system
- **Expected**: Works without issues
- **Priority**: Critical

---

### 15.2 Architecture Documentation

#### TC-DOC-003: ARCHITECTURE.md Accuracy
**Objective**: ARCHITECTURE.md reflects actual code
- **Steps**: Review architecture doc against codebase
- **Expected**: No major discrepancies
- **Priority**: Medium

---

## Test Execution Plan

### Phase 1: Critical Path (Week 1)
- All **Critical** priority tests
- Focus: data fetching, distro detection, basic install

### Phase 2: Core Functionality (Week 2)
- All **High** priority tests
- Focus: CLI commands, script generation

### Phase 3: Edge Cases (Week 3)
- All **Medium** priority tests
- Focus: error handling, edge cases

### Phase 4: Polish (Week 4)
- All **Low** priority tests
- Focus: UX, performance, compatibility

---

## Test Automation Strategy

### Unit Tests (pytest)
- `data.py` functions
- `generator.py` functions
- Regex patterns

### Integration Tests (pytest)
- CLI commands via `click.testing.CliRunner`
- Mock GitHub responses

### End-to-End Tests (Bash + Docker)
- Test on real distros in Docker containers
- Verify actual package installations

### CI/CD (GitHub Actions)
- Run unit + integration tests on PR
- Monthly E2E tests on all distros
- Cache performance benchmarks

---

## Coverage Goals

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: All CLI commands
- **E2E Tests**: All supported distros

---

## Test Environment Setup

### Required Tools
- Python 3.10, 3.11, 3.12
- Docker (for multi-distro E2E tests)
- pytest, pytest-cov, pytest-mock
- responses (mock requests)

### Mock Data
- Sample `data.ts` with 10-20 apps
- Mock `/etc/os-release` files for each distro

---

## Defect Tracking

Use GitHub Issues with labels:
- `bug`: Production bugs
- `test-failure`: Test failures
- `regression`: Regressions from test suite

---

## Sign-off Criteria

Before v1.0 release:
- ✅ All Critical and High priority tests pass
- ✅ 80%+ code coverage
- ✅ E2E tests pass on Ubuntu, Arch, Fedora
- ✅ README examples verified
- ✅ No P0/P1 bugs outstanding

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-29 | Initial comprehensive test plan |

---

**Total Test Cases**: 200+
**Estimated Test Development Time**: 4 weeks
**Estimated Execution Time**: ~30 minutes (automated), ~4 hours (manual E2E)
