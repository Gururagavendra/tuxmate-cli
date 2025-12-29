# Architecture Overview

## Data Flow

```
GitHub (data.ts) → dukpy (JS eval) → Python Objects → Local JSON Cache → CLI Commands
```

1. **Data Fetching (`data.py`)**:
   - Fetches `data.ts` (TypeScript file) from tuxmate's GitHub repository
   - Uses `dukpy` (JavaScript interpreter) to evaluate both `apps` and `distros` arrays
   - Caches parsed data locally in JSON format for 24 hours
   - **All data is dynamic** - no hardcoded distros or packages

2. **CLI Interface (`cli.py`)**:
   - Loads cached or fresh data via `TuxmateDataFetcher`
   - Provides commands: list, search, info, install, distros, etc.
   - Detects Linux distribution automatically from `/etc/os-release`

3. **Script Generation (`generator.py`)**:
   - Takes selected apps and generates distro-specific shell scripts
   - Categorizes packages: native, AUR (Arch), Flatpak, Snap
   - Includes smart features: progress bars, retry logic, parallel installs

## Why dukpy?

The `data.ts` file contains JavaScript function calls like `si('firefox', '#FF7139')` for icon URLs. Simple regex or JSON parsers fail on these. `dukpy` evaluates the actual JavaScript, handling:
- Function calls (`si()`, `lo()`, `mdi()`, etc.)
- Template literals and expressions
- Object shorthand syntax
- Trailing commas

## Regex Usage (Minimal)

- **Array Extraction**: Single regex each to extract `apps` and `distros` arrays
- **Distro Detection**: Parses `/etc/os-release` for ID and ID_LIKE fields

## Key Components

- `TuxmateDataFetcher`: Handles data retrieval, JS evaluation, and caching
- `ScriptGenerator`: Creates installation scripts with distro-specific commands
- `AppData`: Dataclass representing package information (id, name, targets, etc.)
- `Distro`: Dataclass for supported distributions (loaded dynamically from tuxmate)</content>
<parameter name="filePath">/home/guru/guru/tuxmate-cli/ARCHITECTURE.md
