<div align="center">
  <h1>TuxMate CLI</h1>
  <p><strong>THE TUXMATE COMPANION FOR YOUR TERMINAL</strong></p>

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
[![PyPI](https://img.shields.io/pypi/v/tuxmate-cli?style=for-the-badge)](https://pypi.org/project/tuxmate-cli/)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/tuxmate-cli/)
[![License](https://img.shields.io/badge/license-GPL--3.0-yellow?style=for-the-badge)](LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green?style=for-the-badge)]()

</div>

## The CLI-Mate you need for your linux setup

A command-line interface for installing Linux packages using [tuxmate's](https://github.com/abusoww/tuxmate) curated package database. Perfect for setting up a fresh Linux system or bulk-installing your favorite apps.

## Features

```bash
# List and search packages
tuxmate-cli list
tuxmate-cli search firefox

# Install packages directly
tuxmate-cli install firefox neovim git

# Generate install scripts
tuxmate-cli oneliner vscode spotify
```

- **150+ curated packages** across browsers, dev tools, terminals, media, and more
- **Multi-distro support** - Ubuntu, Debian, Arch (AUR), Fedora, openSUSE, Nix, Flatpak, Snap
- **Smart script generation** - Distro-specific scripts with error handling
- **Always updated** - Syncs with tuxmate's latest package data

See [Usage](#usage) section below for detailed commands.

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

## Development

```bash
git clone https://github.com/Gururagavendra/tuxmate-cli.git
cd tuxmate-cli
uv sync
uv run tuxmate-cli --help
```


For technical details, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Supported Distributions & Packages

For the complete list of supported distributions and package catalog, visit [tuxmate.com](https://tuxmate.com/)

## Future Integration

tuxmate-cli is designed to integrate with **TuxSync** (coming soon),
a profile sync tool for Linux configurations. TuxSync will use tuxmate-cli
to restore your application list across machines.

```bash
# TuxSync uses tuxmate-cli for package restoration
tuxsync restore --source github:user/gist-id
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

GPL-3.0 License - see [LICENSE](LICENSE) for details.

## Credits

- Package database from [tuxmate](https://github.com/abusoww/tuxmate) by [@abusoww](https://github.com/abusoww)
- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
