# Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TUXMATE-CLI ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────────┐
                                    │   User Commands     │
                                    │  tuxmate-cli ...    │
                                    └──────────┬──────────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    │              CLI Interface (cli.py)                  │
                    │  • list    • search   • info     • install           │
                    │  • distros • script   • oneliner • categories        │
                    └──────────────────────────┬──────────────────────────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    │         TuxmateDataFetcher (data.py)                 │
                    │  ┌────────────────────────────────────────────────┐  │
                    │  │  Cache Check: use_cache=True? (opt-in)        │  │
                    │  └────────┬───────────────────────┬────────────────┘  │
                    │           │ YES (--cache)         │ NO (default)      │
                    │           ▼                       ▼                   │
                    │  ┌────────────────┐    ┌─────────────────────────┐  │
                    │  │ ~/.cache/...   │    │  GitHub API Request     │  │
                    │  │ data.json      │    │  raw.githubusercontent  │  │
                    │  │ (24h expiry)   │    │  ↓                       │  │
                    │  └────────┬───────┘    │  Fetch data.ts          │  │
                    │           │            └──────────┬───────────────┘  │
                    │           └────────────────┬──────┘                  │
                    │                            ▼                         │
                    │              ┌──────────────────────────┐            │
                    │              │  dukpy JavaScript Engine │            │
                    │              │  Evaluate: apps[], distros[] │        │
                    │              │  Handle: si(), lo(), mdi()   │        │
                    │              └──────────┬───────────────────┘        │
                    │                         ▼                            │
                    │              ┌──────────────────────────┐            │
                    │              │   Python Objects         │            │
                    │              │   • AppData (dataclass)  │            │
                    │              │   • Distro (dataclass)   │            │
                    │              └──────────┬───────────────┘            │
                    └──────────────────────────┼──────────────────────────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    │          ScriptGenerator (generator.py)              │
                    │                                                      │
                    │  ┌──────────────────────────────────────────────┐  │
                    │  │  Distro Detection: /etc/os-release           │  │
                    │  │  → ubuntu, arch, fedora, debian, opensuse... │  │
                    │  └──────────────────┬───────────────────────────┘  │
                    │                     ▼                               │
                    │  ┌──────────────────────────────────────────────┐  │
                    │  │  Package Categorization                      │  │
                    │  │  • Native (apt/pacman/dnf/zypper/nix)        │  │
                    │  │  • AUR (-bin, -git, known packages)          │  │
                    │  │  • Flatpak (fallback)                        │  │
                    │  │  • Snap (fallback)                           │  │
                    │  └──────────────────┬───────────────────────────┘  │
                    │                     ▼                               │
                    │  ┌──────────────────────────────────────────────┐  │
                    │  │  Bash Script Generation                      │  │
                    │  │  • Shebang, colors, error handling           │  │
                    │  │  • Package manager commands                  │  │
                    │  │  • AUR helper (yay) auto-install             │  │
                    │  │  • Parallel Flatpak installs                 │  │
                    │  │  • Summary and completion banner             │  │
                    │  └──────────────────┬───────────────────────────┘  │
                    └─────────────────────┼────────────────────────────┘
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │              Output Layer                        │
                    │  ┌───────────────┐  ┌────────────────────────┐  │
                    │  │ Rich Tables   │  │  Bash Install Script   │  │
                    │  │ • list        │  │  • install.sh          │  │
                    │  │ • search      │  │  • stdout/file         │  │
                    │  │ • distros     │  │  • execute directly    │  │
                    │  └───────────────┘  └────────────────────────┘  │
                    └─────────────────────────────────────────────────┘
                                          ▼
                              ┌─────────────────────────┐
                              │   System Installation    │
                              │   📦 Packages Installed  │
                              └─────────────────────────┘
```

## Data Flow

```
GitHub (data.ts) → dukpy (JS eval) → Python Objects → Local JSON Cache → CLI Commands
```

1. **Data Fetching (`data.py`)**:
   - Fetches `data.ts` (TypeScript file) from tuxmate's GitHub repository
   - Uses `dukpy` (JavaScript interpreter) to evaluate both `apps` and `distros` arrays
   - **Default: Always fetch fresh data** (no caching)
   - **Optional cache**: Use `--cache` flag for faster performance (24-hour expiry)
   - Cache is opt-in via `use_cache=True` parameter or `--cache` CLI flag
   - **All data is dynamic** - no hardcoded distros or packages

2. **CLI Interface (`cli.py`)**:
   - Loads cached or fresh data via `TuxmateDataFetcher`
   - Provides commands: list, search, info, install, distros, etc.
   - Detects Linux distribution automatically from `/etc/os-release`

3. **Script Generation (`generator.py`)**:
   - Takes selected apps and generates distro-specific shell scripts
   - Categorizes packages: native, AUR (Arch), Flatpak, Snap
   - Implements tuxmate's production-grade script logic in Python

## Script Generation: Python Implementation

While [tuxmate](https://github.com/abusoww/tuxmate) (the web app) uses TypeScript for browser-based script generation, **tuxmate-cli** implements the same logic in Python for Linux terminal usage.

### Why Python Instead of TypeScript?

**Tuxmate's Context:**
- Web application running in browsers
- Must use JavaScript/TypeScript (browser constraint)
- Generates scripts for download

**Our Context:**
- Terminal application running on Linux systems
- Python is pre-installed on all Linux distributions
- No Node.js dependency required
- Scripts execute directly on the system
- Better integration with Linux ecosystem

### Script Generation Approach

We follow tuxmate's patterns from [`src/lib/scripts/`](https://github.com/abusoww/tuxmate/tree/main/src/lib/scripts):

#### Implemented Features

1. **Per-Distro Generators** - Modular script generation for each package manager
2. **AUR Automation** - Auto-install yay helper on Arch
3. **Package Categorization** - Native, AUR, Flatpak, Snap detection
4. **Parallel Installation** - Concurrent Flatpak package installation with `&` and `wait`
5. **User-Friendly Output** - Colored output and banners
6. **Basic Error Handling** - Script exits on errors with `set -e`
7. **Snap Classic Flag** - Automatic `--classic` for VS Code, Sublime, etc.
8. **Package Manager Commands** - apt, pacman, dnf, zypper, nix-env support

#### Pending Features (From Tuxmate)

1. **Progress Tracking** - Real-time progress bars with ETA calculations
2. **Network Resilience** - Exponential backoff retry logic for network failures  
3. **Package Manager Locks** - Wait for apt/pacman locks instead of failing
4. **Already-Installed Detection** - Skip packages already on the system
5. **Error Recovery** - Automatic dependency fixing (Ubuntu/Debian)
6. **Per-Package Timing** - Show install duration for each package
7. **Shell Escaping Security** - Prevent injection attacks from package names
8. **Graceful Interrupt Handling** - Trap Ctrl+C for clean exit
9. **Detailed Error Messages** - Package not found, signature issues, etc.
10. **RPM Fusion Auto-Enable** - For Fedora multimedia packages
11. **Success/Failed/Skipped Tracking** - Comprehensive summary reports


## Why dukpy?

The `data.ts` file contains JavaScript function calls like `si('firefox', '#FF7139')` for icon URLs. Simple regex or JSON parsers fail on these. `dukpy` evaluates the actual JavaScript, handling:
- Function calls (`si()`, `lo()`, `mdi()`, etc.)
- Template literals and expressions
- Object shorthand syntax
- Trailing commas

## Key Components

- `TuxmateDataFetcher`: Handles data retrieval, JS evaluation, and caching
- `ScriptGenerator`: Creates installation scripts with distro-specific commands
- `AppData`: Dataclass representing package information (id, name, targets, etc.)
- `Distro`: Dataclass for supported distributions (loaded dynamically from tuxmate)

## Caching Strategy

### Design Decision: Opt-in Cache

**Default Behavior**: Always fetch fresh data from GitHub
- Ensures users always get latest package versions and security updates
- Aligns with real-world usage: installations are infrequent, network call is negligible (~1-2s)
- Simpler mental model: no cache invalidation bugs

**Opt-in Caching**: Use `--cache` flag when needed
- **Development/Testing**: Faster repeated commands during development
- **Offline Scenarios**: Work without internet after running `tuxmate-cli update`
- **CI/CD Pipelines**: Speed up repeated runs in automated workflows

### Implementation Details

- Cache stored in `~/.cache/tuxmate-cli/data.json`
- Default expiry: 24 hours
- `TuxmateDataFetcher(use_cache=False)` by default
- `update` command forces refresh and saves cache

## Installation and Usage

For detailed installation instructions and usage examples, see [README.md](README.md).

### Quick Links
- [Installation](README.md#installation)
- [Usage Examples](README.md#usage)
- [Available Commands](README.md#usage)</content>
<parameter name="filePath">/home/guru/guru/tuxmate-cli/ARCHITECTURE.md
