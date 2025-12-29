# TuxMate CLI

A command-line interface for installing Linux packages using [tuxmate's](https://github.com/abusoww/tuxmate) curated package database.

## Features

- **150+ curated packages** - Access tuxmate's comprehensive package database
- **Multi-distro support** - Ubuntu, Debian, Arch, Fedora, openSUSE, Nix, Flatpak, Snap
- **Auto distro detection** - Automatically detects your Linux distribution
- **Smart script generation** - AUR helper auto-install, progress bars, retry logic
- **Always updated** - Syncs with tuxmate's latest package data

## Installation

```bash
pip install tuxmate-cli --upgrade
```

## Development

```bash
git clone https://github.com/Gururagavendra/tuxmate-cli.git
cd tuxmate-cli
uv sync
uv run tuxmate-cli --help
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

## Why Python for Script Generation?

While [tuxmate](https://github.com/abusoww/tuxmate) is a web application (TypeScript/SvelteKit running in browsers), **tuxmate-cli** is designed specifically for Linux terminal usage. We implement the same production-grade script generation logic from tuxmate, but in Python because:

- **Native to Linux** - Python is pre-installed on all Linux distributions
- **No extra dependencies** - No Node.js or npm required
- **CLI ecosystem** - Better integration with system tools and package managers
- **Direct execution** - Scripts run immediately on the system, not just downloaded
- **Automation-friendly** - Perfect for dotfile managers and provisioning tools

For technical details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Supported Distributions & Packages

For the complete list of supported distributions and package catalog, visit [tuxmate.com](https://tuxmate.com/)

## Integration with TuxSync

tuxmate-cli is designed to work seamlessly with [TuxSync](https://github.com/Gururagavendra/tuxsync) for profile syncing:

```bash
# TuxSync uses tuxmate-cli for package restoration
tuxsync restore --source github:user/gist-id
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- Package database from [tuxmate](https://github.com/abusoww/tuxmate) by [@abusoww](https://github.com/abusoww)
- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
