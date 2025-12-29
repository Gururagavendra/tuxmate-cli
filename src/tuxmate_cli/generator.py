"""
Script generator module - Generates distro-specific installation scripts.

Creates shell scripts based on tuxmate's script generation logic with support
for all major package managers and smart features like AUR handling.
"""

import re
import shlex
from dataclasses import dataclass
from typing import Optional
from .data import AppData, DISTROS, detect_distro


# Security: Package name validation pattern
# Allows alphanumeric, dash, underscore, dot, plus, colon (for arch groups)
PACKAGE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._+-]*$")


def validate_package_name(name: str) -> bool:
    """
    Validate package name to prevent command injection.

    Requirements:
    - Length: 1-256 characters
    - Must start with alphanumeric
    - Can contain: alphanumeric, dot, dash, underscore, plus
    - No special shell characters: $ ` \\ ; & | < > ( ) { } [ ] * ? !
    """
    if not name:
        return False
    if len(name) < 1 or len(name) > 256:
        return False
    if not PACKAGE_NAME_PATTERN.match(name):
        return False
    # Additional checks for suspicious patterns
    dangerous_chars = [
        "$",
        "`",
        "\\",
        ";",
        "&",
        "|",
        "<",
        ">",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "*",
        "?",
        "!",
    ]
    if any(char in name for char in dangerous_chars):
        return False
    return True


def sanitize_packages(packages: list[str]) -> list[str]:
    """
    Validate and sanitize package names. Raises ValueError on invalid input.

    Security measures:
    - Validates against injection patterns
    - Checks length constraints (1-256 chars)
    - Escapes with shlex.quote for safe shell execution
    """
    sanitized = []
    for pkg in packages:
        if not validate_package_name(pkg):
            raise ValueError(
                f"Invalid package name: '{pkg}'. "
                "Package names must be 1-256 characters, start with alphanumeric, "
                "and contain only: letters, numbers, dots, dashes, underscores, plus signs. "
                "Special shell characters are not allowed."
            )
        # Additional safety: shell escape even valid names
        sanitized.append(shlex.quote(pkg))
    return sanitized


@dataclass
class InstallScript:
    """Generated installation script."""

    distro: str
    script: str
    package_count: int
    aur_packages: list[str]
    flatpak_packages: list[str]
    snap_packages: list[str]


class ScriptGenerator:
    """Generates installation scripts for different distributions."""

    # Terminal colors for script output
    COLORS = """
# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color
BOLD='\\033[1m'
"""

    def __init__(self, distro: Optional[str] = None):
        """Initialize with optional distro override."""
        self.distro = distro or detect_distro()
        if not self.distro:
            raise ValueError(
                "Could not detect distribution. Please specify with --distro"
            )

    def generate(
        self,
        apps: list[AppData],
        include_flatpak: bool = False,
        include_snap: bool = False,
    ) -> InstallScript:
        """Generate installation script for the given apps."""

        # Categorize packages
        native_packages = []
        aur_packages = []
        flatpak_packages = []
        snap_packages = []

        for app in apps:
            # Check native package first
            if self.distro in app.targets:
                pkg = app.targets[self.distro]
                if self.distro == "arch" and self._is_aur_package(pkg):
                    aur_packages.append(pkg)
                else:
                    native_packages.append(pkg)
            # Fallback to flatpak/snap if requested
            elif include_flatpak and "flatpak" in app.targets:
                flatpak_packages.append(app.targets["flatpak"])
            elif include_snap and "snap" in app.targets:
                snap_packages.append(app.targets["snap"])

        # Generate the script
        script = self._generate_script(
            native_packages, aur_packages, flatpak_packages, snap_packages
        )

        return InstallScript(
            distro=self.distro,
            script=script,
            package_count=len(native_packages)
            + len(aur_packages)
            + len(flatpak_packages)
            + len(snap_packages),
            aur_packages=aur_packages,
            flatpak_packages=flatpak_packages,
            snap_packages=snap_packages,
        )

    def _is_aur_package(self, package: str) -> bool:
        """Check if an Arch package is from AUR (heuristic)."""
        aur_suffixes = ["-bin", "-git", "-appimage"]
        aur_packages = [
            "brave-bin",
            "google-chrome",
            "spotify",
            "discord",
            "slack-desktop",
            "visual-studio-code-bin",
            "vscodium-bin",
            "cursor-bin",
            "vesktop-bin",
            "heroic-games-launcher-bin",
            "protonup-qt-bin",
            "localsend-bin",
            "ab-download-manager-bin",
            "freedownloadmanager-bin",
            "hoppscotch-bin",
            "zen-browser-bin",
            "librewolf-bin",
            "onlyoffice-bin",
            "obsidian",
            "logseq-desktop-bin",
            "joplin-appimage",
            "imhex-bin",
            "orcaslicer-bin",
            "superfile",
            "ghostty",
            "mullvad-vpn-bin",
            "proton-vpn-gtk-app",
            "bruno-bin",
            "postman-bin",
            "dbeaver",
            "dropbox",
            "prismlauncher",
            "stremio",
            "helium-browser-bin",
        ]

        if any(package.endswith(suffix) for suffix in aur_suffixes):
            return True
        if package in aur_packages:
            return True
        return False

    def _generate_script(
        self, native: list[str], aur: list[str], flatpak: list[str], snap: list[str]
    ) -> str:
        """Generate the complete installation script."""
        lines = [
            "#!/bin/bash",
            "# Generated by tuxmate-cli",
            "# https://github.com/Gururagavendra/tuxmate-cli",
            "",
            "set -e",
            "",
            self.COLORS,
            "",
            "# Security: Prevent execution as root user",
            '[ "$EUID" -eq 0 ] && {',
            '    echo -e "${RED}${BOLD}Error: Do not run this script as root!${NC}"',
            '    echo -e "${YELLOW}Run as a regular user. The script will use sudo when needed.${NC}"',
            "    exit 1",
            "}",
            "",
            'echo -e "${BOLD}${CYAN}╔════════════════════════════════════════╗${NC}"',
            'echo -e "${BOLD}${CYAN}║      TuxMate CLI Package Installer     ║${NC}"',
            f'echo -e "${{BOLD}}${{CYAN}}║  Distro: {self.distro.capitalize():^28} ║${{NC}}"',
            'echo -e "${BOLD}${CYAN}╚════════════════════════════════════════╝${NC}"',
            "",
        ]

        total_packages = len(native) + len(aur) + len(flatpak) + len(snap)
        lines.append(
            f'echo -e "\\n${{BLUE}}Installing {total_packages} packages...${{NC}}\\n"'
        )
        lines.append("")

        # Generate distro-specific installation
        if native:
            lines.extend(self._generate_native_install(native))

        if aur:
            lines.extend(self._generate_aur_install(aur))

        if flatpak:
            lines.extend(self._generate_flatpak_install(flatpak))

        if snap:
            lines.extend(self._generate_snap_install(snap))

        # Summary
        lines.extend(
            [
                "",
                'echo -e "\\n${BOLD}${GREEN}╔════════════════════════════════════════╗${NC}"',
                'echo -e "${BOLD}${GREEN}║         Installation Complete!         ║${NC}"',
                'echo -e "${BOLD}${GREEN}╚════════════════════════════════════════╝${NC}"',
                f'echo -e "${{GREEN}}✓ Installed {total_packages} packages${{NC}}"',
            ]
        )

        if aur:
            lines.append(f'echo -e "${{YELLOW}}  - {len(aur)} AUR packages${{NC}}"')
        if flatpak:
            lines.append(
                f'echo -e "${{BLUE}}  - {len(flatpak)} Flatpak packages${{NC}}"'
            )
        if snap:
            lines.append(f'echo -e "${{CYAN}}  - {len(snap)} Snap packages${{NC}}"')

        return "\n".join(lines)

    def _generate_native_install(self, packages: list[str]) -> list[str]:
        """Generate native package manager installation commands."""
        lines = ['echo -e "${YELLOW}Installing native packages...${NC}"', ""]

        distro = DISTROS.get(self.distro)
        if not distro:
            return lines

        # Security: Validate and sanitize all package names
        safe_packages = sanitize_packages(packages)

        if self.distro in ["ubuntu", "debian"]:
            lines.extend(
                [
                    "# Wait for apt lock to be released",
                    "while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || fuser /var/lib/dpkg/lock >/dev/null 2>&1; do",
                    '    echo -e "${YELLOW}Waiting for package manager lock...${NC}"',
                    "    sleep 2",
                    "done",
                    "",
                    "# Update package lists",
                    "sudo apt update",
                    "",
                    "# Function to check if package is installed",
                    "is_installed() {",
                    '    dpkg -l "$1" 2>/dev/null | grep -q "^ii"',
                    "}",
                    "",
                    "# Install packages (skip if already installed)",
                    'echo -e "${CYAN}Checking and installing packages...${NC}"',
                    "INSTALLED=0",
                    "SKIPPED=0",
                    "for pkg in " + " ".join(safe_packages) + "; do",
                    "    if is_installed $pkg; then",
                    '        echo -e "${DIM}○${NC} $pkg ${DIM}(already installed)${NC}"',
                    "        SKIPPED=$((SKIPPED + 1))",
                    "    else",
                    '        echo -e "${BLUE}→${NC} Installing $pkg..."',
                    "        if sudo apt install -y $pkg >/dev/null 2>&1; then",
                    '            echo -e "${GREEN}✓${NC} $pkg installed"',
                    "            INSTALLED=$((INSTALLED + 1))",
                    "        else",
                    '            echo -e "${RED}✗${NC} $pkg failed"',
                    "        fi",
                    "    fi",
                    "done",
                    "",
                    '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
                ]
            )

        elif self.distro == "arch":
            lines.extend(
                [
                    "# Wait for pacman lock to be released",
                    "while [ -f /var/lib/pacman/db.lck ]; do",
                    '    echo -e "${YELLOW}Waiting for pacman lock...${NC}"',
                    "    sleep 2",
                    "done",
                    "",
                    "# Update package database",
                    "sudo pacman -Sy",
                    "",
                    "# Function to check if package is installed",
                    "is_installed() {",
                    '    pacman -Qi "$1" &>/dev/null',
                    "}",
                    "",
                    "# Install packages (skip if already installed)",
                    'echo -e "${CYAN}Checking and installing packages...${NC}"',
                    "INSTALLED=0",
                    "SKIPPED=0",
                    "for pkg in " + " ".join(safe_packages) + "; do",
                    "    if is_installed $pkg; then",
                    '        echo -e "${DIM}○${NC} $pkg ${DIM}(already installed)${NC}"',
                    "        SKIPPED=$((SKIPPED + 1))",
                    "    else",
                    '        echo -e "${BLUE}→${NC} Installing $pkg..."',
                    "        if sudo pacman -S --needed --noconfirm $pkg >/dev/null 2>&1; then",
                    '            echo -e "${GREEN}✓${NC} $pkg installed"',
                    "            INSTALLED=$((INSTALLED + 1))",
                    "        else",
                    '            echo -e "${RED}✗${NC} $pkg failed"',
                    "        fi",
                    "    fi",
                    "done",
                    "",
                    '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
                ]
            )

        elif self.distro == "fedora":
            lines.extend(
                [
                    "# Function to check if package is installed",
                    "is_installed() {",
                    '    rpm -q "$1" &>/dev/null',
                    "}",
                    "",
                    "# Install packages (skip if already installed)",
                    'echo -e "${CYAN}Checking and installing packages...${NC}"',
                    "INSTALLED=0",
                    "SKIPPED=0",
                    "for pkg in " + " ".join(safe_packages) + "; do",
                    "    if is_installed $pkg; then",
                    '        echo -e "${DIM}○${NC} $pkg ${DIM}(already installed)${NC}"',
                    "        SKIPPED=$((SKIPPED + 1))",
                    "    else",
                    '        echo -e "${BLUE}→${NC} Installing $pkg..."',
                    "        if sudo dnf install -y $pkg >/dev/null 2>&1; then",
                    '            echo -e "${GREEN}✓${NC} $pkg installed"',
                    "            INSTALLED=$((INSTALLED + 1))",
                    "        else",
                    '            echo -e "${RED}✗${NC} $pkg failed"',
                    "        fi",
                    "    fi",
                    "done",
                    "",
                    '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
                ]
            )

        elif self.distro == "opensuse":
            lines.extend(
                [
                    "# Wait for zypper lock to be released",
                    "while [ -f /var/run/zypp.pid ]; do",
                    '    echo -e "${YELLOW}Waiting for zypper lock...${NC}"',
                    "    sleep 2",
                    "done",
                    "",
                    "# Function to check if package is installed",
                    "is_installed() {",
                    '    rpm -q "$1" &>/dev/null',
                    "}",
                    "",
                    "# Install packages (skip if already installed)",
                    'echo -e "${CYAN}Checking and installing packages...${NC}"',
                    "INSTALLED=0",
                    "SKIPPED=0",
                    "for pkg in " + " ".join(safe_packages) + "; do",
                    "    if is_installed $pkg; then",
                    '        echo -e "${DIM}○${NC} $pkg ${DIM}(already installed)${NC}"',
                    "        SKIPPED=$((SKIPPED + 1))",
                    "    else",
                    '        echo -e "${BLUE}→${NC} Installing $pkg..."',
                    "        if sudo zypper install -y $pkg >/dev/null 2>&1; then",
                    '            echo -e "${GREEN}✓${NC} $pkg installed"',
                    "            INSTALLED=$((INSTALLED + 1))",
                    "        else",
                    '            echo -e "${RED}✗${NC} $pkg failed"',
                    "        fi",
                    "    fi",
                    "done",
                    "",
                    '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
                ]
            )

        elif self.distro == "nix":
            lines.extend(
                [
                    "# Function to check if package is installed",
                    "is_installed() {",
                    '    nix-env -q 2>/dev/null | grep -q "$1"',
                    "}",
                    "",
                    "# Install packages (skip if already installed)",
                    'echo -e "${CYAN}Checking and installing packages...${NC}"',
                    "INSTALLED=0",
                    "SKIPPED=0",
                ]
            )
            for pkg in safe_packages:
                lines.extend(
                    [
                        f"if is_installed {pkg}; then",
                        f'    echo -e "${{DIM}}○${{NC}} {pkg} ${{DIM}}(already installed)${{NC}}"',
                        "    SKIPPED=$((SKIPPED + 1))",
                        "else",
                        f'    echo -e "${{BLUE}}→${{NC}} Installing {pkg}..."',
                        f"    if nix-env -iA nixpkgs.{pkg} >/dev/null 2>&1; then",
                        f'        echo -e "${{GREEN}}✓${{NC}} {pkg} installed"',
                        "        INSTALLED=$((INSTALLED + 1))",
                        "    else",
                        f'        echo -e "${{RED}}✗${{NC}} {pkg} failed"',
                        "    fi",
                        "fi",
                    ]
                )
            lines.extend(
                [
                    "",
                    '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
                ]
            )

        lines.append("")
        return lines

    def _generate_aur_install(self, packages: list[str]) -> list[str]:
        """Generate AUR installation commands using yay."""
        # Security: Validate and sanitize all package names
        safe_packages = sanitize_packages(packages)

        return [
            'echo -e "${YELLOW}Installing AUR packages...${NC}"',
            "",
            "# Check if yay is installed, install if not",
            "if ! command -v yay &> /dev/null; then",
            '    echo -e "${CYAN}Installing yay AUR helper...${NC}"',
            "    sudo pacman -S --needed --noconfirm git base-devel",
            "    git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin",
            "    cd /tmp/yay-bin && makepkg -si --noconfirm",
            "    cd - > /dev/null",
            "    rm -rf /tmp/yay-bin",
            "fi",
            "",
            "# Install AUR packages",
            f"yay -S --needed --noconfirm {' '.join(safe_packages)}",
            "",
        ]

    def _generate_flatpak_install(self, packages: list[str]) -> list[str]:
        """Generate Flatpak installation commands."""
        # Security: Validate and sanitize all package names
        safe_packages = sanitize_packages(packages)

        lines = [
            'echo -e "${BLUE}Installing Flatpak packages...${NC}"',
            "",
            "# Check if flatpak is available",
            "if ! command -v flatpak &> /dev/null; then",
            '    echo -e "${RED}Error: flatpak is not installed${NC}"',
            '    echo -e "${YELLOW}Please install flatpak first for your distribution${NC}"',
            "    exit 1",
            "fi",
            "",
            "# Ensure Flathub is added",
            "flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo",
            "",
            "# Function to check if flatpak is installed",
            "is_installed() {",
            "    flatpak list --app 2>/dev/null | awk '{print $2}' | grep -Fxq \"$1\"",
            "}",
            "",
            "# Install packages with already-installed detection",
            'echo -e "${CYAN}Checking and installing packages...${NC}"',
            "INSTALLED=0",
            "SKIPPED=0",
            "for pkg in " + " ".join(safe_packages) + "; do",
            "    if is_installed $pkg; then",
            '        echo -e "${DIM}○${NC} $pkg ${DIM}(already installed)${NC}"',
            "        SKIPPED=$((SKIPPED + 1))",
            "    else",
            '        echo -e "${BLUE}→${NC} Installing $pkg..."',
            "        if flatpak install flathub -y $pkg >/dev/null 2>&1; then",
            '            echo -e "${GREEN}✓${NC} $pkg installed"',
            "            INSTALLED=$((INSTALLED + 1))",
            "        else",
            '            echo -e "${RED}✗${NC} $pkg failed"',
            "        fi",
            "    fi",
            "done",
            "",
            '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
            "",
        ]

        return lines

    def _generate_snap_install(self, packages: list[str]) -> list[str]:
        """Generate Snap installation commands."""
        # Security: Validate and sanitize all package names
        safe_packages = sanitize_packages(packages)

        lines = [
            'echo -e "${CYAN}Installing Snap packages...${NC}"',
            "",
            "# Check if snap is available",
            "if ! command -v snap &> /dev/null; then",
            '    echo -e "${RED}Error: snap is not installed${NC}"',
            '    echo -e "${YELLOW}Please install snapd first for your distribution${NC}"',
            "    exit 1",
            "fi",
            "",
            "# Function to check if snap is installed",
            "is_installed() {",
            "    local snap_name=$(echo \"$1\" | awk '{print $1}')",
            '    snap list 2>/dev/null | grep -q "^$snap_name "',
            "}",
            "",
            "# Install packages with already-installed detection",
            'echo -e "${CYAN}Checking and installing packages...${NC}"',
            "INSTALLED=0",
            "SKIPPED=0",
        ]

        # Classic snaps that require --classic flag
        classic_snaps = [
            "code",
            "sublime-text",
            "slack",
            "skype",
            "pycharm-community",
            "intellij-idea-community",
        ]

        for i, pkg in enumerate(safe_packages):
            # Use original package name for classic check, sanitized for command
            classic_flag = " --classic" if packages[i] in classic_snaps else ""
            lines.extend(
                [
                    f"if is_installed {pkg}; then",
                    f'    echo -e "${{DIM}}○${{NC}} {pkg} ${{DIM}}(already installed)${{NC}}"',
                    "    SKIPPED=$((SKIPPED + 1))",
                    "else",
                    f'    echo -e "${{BLUE}}→${{NC}} Installing {pkg}..."',
                    f"    if sudo snap install {pkg}{classic_flag} >/dev/null 2>&1; then",
                    f'        echo -e "${{GREEN}}✓${{NC}} {pkg} installed"',
                    "        INSTALLED=$((INSTALLED + 1))",
                    "    else",
                    f'        echo -e "${{RED}}✗${{NC}} {pkg} failed"',
                    "    fi",
                    "fi",
                ]
            )

        lines.extend(
            [
                "",
                '[ $SKIPPED -gt 0 ] && echo -e "${DIM}Skipped $SKIPPED already installed packages${NC}"',
            ]
        )

        lines.append("")
        return lines

    def generate_one_liner(self, apps: list[AppData]) -> str:
        """Generate a one-liner command for quick installation."""
        packages = []
        for app in apps:
            if self.distro in app.targets:
                packages.append(app.targets[self.distro])

        if not packages:
            return "# No packages available for this distribution"

        distro = DISTROS.get(self.distro)
        if not distro:
            return "# Unknown distribution"

        # Security: Validate and sanitize all package names
        safe_packages = sanitize_packages(packages)

        if self.distro in ["ubuntu", "debian"]:
            return f"sudo apt update && sudo apt install -y {' '.join(safe_packages)}"
        elif self.distro == "arch":
            return f"sudo pacman -Syu --needed --noconfirm {' '.join(safe_packages)}"
        elif self.distro == "fedora":
            return f"sudo dnf install -y {' '.join(safe_packages)}"
        elif self.distro == "opensuse":
            return f"sudo zypper install -y {' '.join(safe_packages)}"
        elif self.distro == "nix":
            return f"nix-env -iA {' '.join(f'nixpkgs.{p}' for p in safe_packages)}"

        return f"# Install: {' '.join(safe_packages)}"
