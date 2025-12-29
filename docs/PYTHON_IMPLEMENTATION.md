# Script Generation: Python Implementation

While [tuxmate](https://github.com/abusoww/tuxmate) (the web app) uses TypeScript for browser-based script generation, **tuxmate-cli** implements the same logic in Python for Linux terminal usage.

## Why Python Instead of TypeScript?

### Tuxmate's Context
- Web application running in browsers
- Must use JavaScript/TypeScript (browser constraint)
- Generates scripts for download
- User copies/downloads script to run on their system

### Our Context
- Terminal application running on Linux systems
- Python is pre-installed on all Linux distributions
- No Node.js dependency required
- Scripts execute directly on the system
- Better integration with Linux ecosystem (subprocess, os modules)
- Native terminal experience with rich formatting

## Design Philosophy

Both implementations achieve the same goal: generate distro-specific installation scripts. The choice of language is driven by the execution environment:
- **Web → TypeScript** (runs in browser)
- **Terminal → Python** (native to Linux)

## Script Generation Approach

We follow tuxmate's patterns from [`src/lib/scripts/`](https://github.com/abusoww/tuxmate/tree/main/src/lib/scripts):

### Implemented Features

1. **Per-Distro Generators** - Modular script generation for each package manager
2. **AUR Automation** - Auto-install yay helper on Arch
3. **Package Categorization** - Native, AUR, Flatpak, Snap detection
4. **Parallel Installation** - Concurrent Flatpak package installation with `&` and `wait`
5. **User-Friendly Output** - Colored output and banners
6. **Basic Error Handling** - Script exits on errors with `set -e`
7. **Snap Classic Flag** - Automatic `--classic` for VS Code, Sublime, etc.
8. **Package Manager Commands** - apt, pacman, dnf, zypper, nix-env support

### Pending Features (From Tuxmate)

These production-grade features from tuxmate are documented for future implementation:

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

## Code Comparison

### TypeScript (Tuxmate Web)
```typescript
export function generateUbuntuScript(packages: string[]): string {
  return `#!/bin/bash
sudo apt update
sudo apt install -y ${packages.join(' ')}
`;
}
```

### Python (Tuxmate CLI)
```python
def generate_ubuntu_script(packages: list[str]) -> str:
    return f"""#!/bin/bash
sudo apt update
sudo apt install -y {' '.join(packages)}
"""
```

Same logic, different language - each optimized for its runtime environment.

## Benefits of Python Implementation

1. **No Additional Dependencies**: Python ships with every Linux distro
2. **Direct System Integration**: Native subprocess handling for script execution
3. **Rich Terminal UI**: Easy integration with `rich` library for beautiful output
4. **Consistent Tooling**: Single language for entire CLI application
5. **Easier Packaging**: Standard Python packaging (pip, PyPI)
