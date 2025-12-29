# Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                  TUXMATE-CLI ARCHITECTURE                        │
└──────────────────────────────────────────────────────────────────┘

                         User Command
                    tuxmate-cli [command]
                              ↓
                ┌─────────────────────────────┐
                │     CLI Interface           │
                │       (cli.py)              │
                │                             │
                │  • list      • search       │
                │  • info      • install      │
                │  • distros   • oneliner     │
                └──────────────┬──────────────┘
                               ↓
                ┌─────────────────────────────┐
                │    Data Fetcher             │
                │      (data.py)              │
                │                             │
                │  ┌─────────────────────┐   │
                │  │ GitHub data.ts      │   │
                │  │        ↓            │   │
                │  │ dukpy JS eval       │   │
                │  │        ↓            │   │
                │  │ Python objects      │   │
                │  └─────────────────────┘   │
                │                             │
                │  Optional: ~/.cache/        │
                │  tuxmate-cli/data.json      │
                └──────────────┬──────────────┘
                               ↓
                ┌─────────────────────────────┐
                │   Script Generator          │
                │     (generator.py)          │
                │                             │
                │  • Detect distro            │
                │  • Categorize packages      │
                │    - Native (apt/pacman)    │
                │    - AUR / Flatpak / Snap   │
                │  • Generate bash script     │
                │    - Error handling         │
                │    - Colored output         │
                │    - AUR helper install     │
                └──────────────┬──────────────┘
                               ↓
                  ┌────────────────────────┐
                  │  Output / Execution    │
                  │                        │
                  │  • Rich tables         │
                  │  • Bash scripts        │
                  │  • Direct install      │
                  └────────────┬───────────┘
                               ↓
                       📦 System Packages
```

## Data Flow

```
GitHub (data.ts) → dukpy (JS eval) → Python Objects → Local JSON Cache → CLI Commands
```

1. **Data Fetching (`data.py`)**:
   - Fetches `data.ts` (TypeScript file) from tuxmate's GitHub repository
   - Uses `dukpy` (JavaScript interpreter) to evaluate both `apps` and `distros` arrays - [Why dukpy?](WHY_DUKPY.md)
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
   - Implements tuxmate's production-grade script logic in Python - [Why Python instead of TypeScript?](PYTHON_IMPLEMENTATION.md)

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

## Documentation

- [Why dukpy?](WHY_DUKPY.md) - Technical explanation of JavaScript evaluation
- [Python Implementation](PYTHON_IMPLEMENTATION.md) - Why Python instead of TypeScript
- [Test Plan](TEST_PLAN.md) - Comprehensive testing strategy

## Installation and Usage

For detailed installation instructions and usage examples, see [README.md](../README.md).

### Quick Links
- [Installation](../README.md#installation)
- [Usage Examples](../README.md#usage)
- [Available Commands](../README.md#usage)
