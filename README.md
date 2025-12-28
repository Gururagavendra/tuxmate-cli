# TuxMate CLI

A command-line interface for installing Linux packages using [tuxmate's](https://github.com/abusoww/tuxmate) curated package database.

## Features

- **150+ curated packages** - Access tuxmate's comprehensive package database
- **Multi-distro support** - Ubuntu, Debian, Arch, Fedora, openSUSE, Nix, Flatpak, Snap
- **Auto distro detection** - Automatically detects your Linux distribution
- **Smart script generation** - Generates optimized install scripts with:
  - AUR helper (yay) auto-installation for Arch
  - Progress bars and colored output
  - Retry logic with exponential backoff
  - Parallel Flatpak installation
- **Always updated** - Syncs with tuxmate's latest package data

## Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/Gururagavendra/tuxmate-cli.git
cd tuxmate-cli
chmod +x tuxmate-cli.sh
./tuxmate-cli.sh --help
```

### Using uv

```bash
git clone https://github.com/Gururagavendra/tuxmate-cli.git
cd tuxmate-cli
uv sync
uv run tuxmate-cli --help
```

### Using pip

```bash
pip install tuxmate-cli
tuxmate-cli --help
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

## Supported Distributions

| Distribution | Package Manager | Auto-Detected |
|--------------|-----------------|---------------|
| Ubuntu       | apt             | ✓             |
| Debian       | apt             | ✓             |
| Pop!_OS      | apt (as Ubuntu) | ✓             |
| Linux Mint   | apt (as Ubuntu) | ✓             |
| Arch Linux   | pacman + AUR    | ✓             |
| Manjaro      | pacman + AUR    | ✓             |
| Fedora       | dnf             | ✓             |
| openSUSE     | zypper          | ✓             |
| Nix          | nix-env         | ✓             |
| Flatpak      | flatpak         | Manual        |
| Snap         | snap            | Manual        |

## Integration with TuxSync

tuxmate-cli is designed to work seamlessly with [TuxSync](https://github.com/Gururagavendra/tuxsync) for profile syncing:

```bash
# TuxSync uses tuxmate-cli for package restoration
tuxsync restore --source github:user/gist-id
```

## Package Database

tuxmate-cli automatically syncs with tuxmate's package database, which includes:

- **Web Browsers**: Firefox, Chrome, Brave, LibreWolf, Zen, etc.
- **Communication**: Discord, Telegram, Signal, Slack, Zoom
- **Dev Languages**: Python, Node.js, Go, Rust, Ruby, PHP
- **Dev Editors**: VS Code, Neovim, Helix, Zed, Cursor
- **Dev Tools**: Git, Docker, Podman, kubectl, Vagrant
- **Terminal**: Zsh, Fish, Alacritty, Kitty, WezTerm, Ghostty
- **CLI Tools**: btop, htop, fzf, ripgrep, bat, eza
- **Media**: VLC, mpv, Spotify, OBS, Kdenlive
- **Gaming**: Steam, Lutris, Heroic, MangoHud
- And many more...

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- Package database from [tuxmate](https://github.com/abusoww/tuxmate) by [@abusoww](https://github.com/abusoww)
- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
