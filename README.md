<div align="center">
  <h1>TuxMate CLI</h1>
  <p><strong>Install Linux packages across distros with one command</strong></p>

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
[![PyPI](https://img.shields.io/pypi/v/tuxmate-cli?style=for-the-badge)](https://pypi.org/project/tuxmate-cli/)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/tuxmate-cli/)
[![License](https://img.shields.io/badge/license-GPL--3.0-yellow?style=for-the-badge)](LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green?style=for-the-badge)]()

</div>

## Why TuxMate CLI?

Setting up a fresh Linux install means hunting through package managers, PPAs, Flatpak, Snap, and AUR. **TuxMate CLI simplifies this** with a curated database of 150+ popular applications that work across distros.

**One command. Multiple distros. No hassle.**

```bash
# Works on Ubuntu, Debian, Arch, Fedora, openSUSE, Nix
tuxmate-cli install firefox vscode spotify discord
```

**Perfect for:**
- Fresh Linux installations
- Distro hopping (same apps, different distro)
- Sharing your setup with others
- Automated system provisioning

Built on [tuxmate's](https://github.com/abusoww/tuxmate) curated package database with smart fallbacks to Flatpak/Snap when native packages aren't available.

## Quick Start

```bash
# Install
pip install tuxmate-cli

# Search for packages
tuxmate-cli search browser

# Install your favorites
tuxmate-cli install firefox brave chromium

# Generate a setup script
tuxmate-cli script firefox neovim git docker > setup.sh
```

## Key Features

- **150+ curated packages** - Browsers, dev tools, terminals, media apps, and more
- **Multi-distro support** - Ubuntu, Debian, Arch (AUR), Fedora, openSUSE, Nix
- **Smart fallbacks** - Auto-fallback to Flatpak/Snap when native packages unavailable
- **Already-installed detection** - Skips packages already on your system
- **Script generation** - Create reusable install scripts for team sharing
- **Secure by default** - Root prevention, input validation, proper escaping

## Real-World Examples

## Real-World Examples

### Fresh Ubuntu Install
```bash
# Developer setup
tuxmate-cli install vscode git docker nodejs python3

# Browser collection
tuxmate-cli install firefox brave chromium

# Media & communication
tuxmate-cli install vlc spotify discord slack --flatpak
```

### Arch Linux Setup
```bash
# AUR packages detected automatically
tuxmate-cli install visual-studio-code-bin spotify brave-bin

# Generate script for later
tuxmate-cli script neovim tmux zsh > dotfiles-setup.sh
```

### Share Your Setup
```bash
# Create a setup script anyone can run
tuxmate-cli script firefox vscode git docker neovim -o my-setup.sh

# Others run it on their distro
bash my-setup.sh  # Works on any supported distro
```

## Installation

```bash
pip install tuxmate-cli --upgrade
```

## Usage

### List available packages

```bash
tuxmate-cli list
tuxmate-cli list --category "Dev: Editors"
tuxmate-cli list --distro arch
```

### Search packages

```bash
tuxmate-cli search firefox
tuxmate-cli search editor --distro ubuntu
```

### Get package info

```bash
tuxmate-cli info neovim
tuxmate-cli info vscode
```

### Install packages

```bash
# Install directly
tuxmate-cli install firefox neovim git

# With Flatpak fallbacks
tuxmate-cli install vscode spotify --flatpak

# Dry run (show script without executing)
tuxmate-cli install firefox --dry-run

# Save script to file
tuxmate-cli install firefox neovim -o install.sh
```

### Generate scripts

```bash
# One-liner command
tuxmate-cli oneliner firefox neovim git

# Full script to stdout (pipe to bash)
tuxmate-cli script firefox neovim | bash

# Save to file
tuxmate-cli script firefox neovim > install.sh
```

### Other commands

```bash
# Update package database
tuxmate-cli update

# List categories
tuxmate-cli categories

# List supported distros
tuxmate-cli distros
```
## Supported Distributions & Packages

For the complete list of supported distributions and package catalog, visit [tuxmate.com](https://tuxmate.com/)

## Requirements
- **Python 3.10+** with pip
- **[uv](https://docs.astral.sh/uv/)** (recommended) or standard pip/venv
- **Git** - For cloning the repository

## Development

```bash
git clone https://github.com/Gururagavendra/tuxmate-cli.git
cd tuxmate-cli
uv sync
uv run tuxmate-cli --help
```

For technical details, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Security

- **Trusted Source**: Package data is fetched from tuxmate.com
- **Script Review**: Use `--dry-run` to review commands before execution
- **Sudo Required**: Installations require root privileges - review scripts carefully
- **Sandboxing**: JavaScript data parsing is sandboxed via dukpy


## Roadmap

### ✅ Implemented Features

✓ Multi-distro support (Ubuntu, Debian, Arch, Fedora, openSUSE, Nix)  
✓ Flatpak & Snap universal package support  
✓ 150+ applications across 15 categories  
✓ Smart AUR detection & yay auto-installation  
✓ Package categorization (native, AUR, Flatpak, Snap)  
✓ Parallel Flatpak installation  
✓ Colored terminal output with rich formatting  
✓ Basic error handling with `set -e`  
✓ Snap classic flag auto-detection  
✓ Script generation (one-liner, full script, dry-run)  
✓ Offline cache support (24h expiry)  
✓ Package search & filtering  
✓ Input validation & security fixes

### 🔮 Planned Features

> Features are prioritized using [MoSCoW method](https://en.wikipedia.org/wiki/MoSCoW_method) (Must have, Should have, Could have, Won't have). Priorities are flexible and may change based on user feedback.

**High Priority:**
- [x] Already-installed detection (skip packages on system) — **Must have**
- [x] Network retry logic with exponential backoff (3 retries, 5s delay) — **Must have**
- [ ] Progress bars with ETA calculations (percentage, timing, remaining) — **Should have**
- [ ] Migrate to PythonMonkey (modern SpiderMonkey-based JS engine) — **Should have**
- [ ] Comprehensive test coverage (unit + integration tests) — **Should have**

**Script Generation Features (from tuxmate):**
- [x] Package manager lock detection & wait loop (apt, pacman, zypper) — **Must have**
- [ ] Real-time progress indicators with package count (1/10, 2/10...) — **Should have**
- [ ] Per-package install timing (shows seconds for each package) — **Should have**
- [ ] Graceful interrupt handling with Ctrl+C traps — **Should have**
- [ ] Success/Failed/Skipped tracking with final summary report — **Should have**
- [ ] Adaptive ETA calculation (learns average time as it installs) — **Could have**
- [ ] Colored output with status symbols (✓ ✗ ! ○) — **Could have**

**Error Handling & Recovery:**
- [x] Network error detection with smart retry logic — **Must have**
- [x] Safe command execution (no eval, proper escaping) — **Must have**
- [ ] Automatic dependency fixing (Ubuntu/Debian `apt-get --fix-broken`) — **Should have**
- [ ] Detailed error messages (package not found, signature issues, network errors) — **Should have**
- [ ] RPM Fusion auto-enable for Fedora multimedia packages — **Could have**
- [ ] Parallel Flatpak installation (3+ packages installed concurrently) — **Could have**

**Security & Robustness:**
- [x] Shell string escaping (basic implementation with shlex.quote)
- [x] Advanced shell escaping (escape $, `, \, !, like tuxmate's escapeShellString) — **Must have**
- [x] Validate package names before script generation — **Must have**
- [x] Check for root user and prevent execution as root — **Should have**
- [x] Verify package manager availability before installation — **Should have**

See [docs/TEST_PLAN.md](docs/TEST_PLAN.md) and [docs/PYTHON_IMPLEMENTATION.md](docs/PYTHON_IMPLEMENTATION.md) for technical details.

## Future Integration

tuxmate-cli is designed to integrate with **TuxSync** (coming soon),
a profile sync tool for Linux configurations. TuxSync will use tuxmate-cli
to restore your application list across machines.

```bash
# TuxSync uses tuxmate-cli for package restoration
tuxsync restore --source github:user/gist-id
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a Pull Request.

## License

GPL-3.0 License - see [LICENSE](LICENSE) for details.

## Credits

- Package database from [tuxmate](https://github.com/abusoww/tuxmate) by [@abusoww](https://github.com/abusoww)
- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
