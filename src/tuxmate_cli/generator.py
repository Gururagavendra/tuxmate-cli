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
    """Validate package name to prevent command injection."""
    if not name or len(name) > 256:
        return False
    return bool(PACKAGE_NAME_PATTERN.match(name))


def sanitize_packages(packages: list[str]) -> list[str]:
    """Validate and sanitize package names. Raises ValueError on invalid input."""
    sanitized = []
    for pkg in packages:
        if not validate_package_name(pkg):
            raise ValueError(
                f"Invalid package name: '{pkg}'. "
                "Package names must be alphanumeric with only .-_+ allowed."
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
                    "# Update package lists",
                    "sudo apt update",
                    "",
                    "# Install packages",
                    f"sudo apt install -y {' '.join(safe_packages)}",
                ]
            )

        elif self.distro == "arch":
            lines.extend(
                [
                    "# Update package database",
                    "sudo pacman -Sy",
                    "",
                    "# Install packages",
                    f"sudo pacman -S --needed --noconfirm {' '.join(safe_packages)}",
                ]
            )

        elif self.distro == "fedora":
            lines.extend(
                [
                    "# Install packages",
                    f"sudo dnf install -y {' '.join(safe_packages)}",
                ]
            )

        elif self.distro == "opensuse":
            lines.extend(
                [
                    "# Install packages",
                    f"sudo zypper install -y {' '.join(safe_packages)}",
                ]
            )

        elif self.distro == "nix":
            for pkg in safe_packages:
                lines.append(f"nix-env -iA nixpkgs.{pkg}")

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
            "# Ensure Flathub is added",
            "flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo",
            "",
            "# Install packages (parallel)",
        ]

        # Install in parallel batches
        for pkg in safe_packages:
            lines.append(f"flatpak install flathub -y {pkg} &")

        lines.extend(
            [
                "wait",
                "",
            ]
        )

        return lines

    def _generate_snap_install(self, packages: list[str]) -> list[str]:
        """Generate Snap installation commands."""
        # Security: Validate and sanitize all package names
        safe_packages = sanitize_packages(packages)

        lines = [
            'echo -e "${CYAN}Installing Snap packages...${NC}"',
            "",
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
            if packages[i] in classic_snaps:
                lines.append(f"sudo snap install {pkg} --classic")
            else:
                lines.append(f"sudo snap install {pkg}")

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
