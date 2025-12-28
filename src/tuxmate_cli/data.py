"""
Data fetcher module - Downloads and parses tuxmate's package database.

Fetches the latest data.ts from tuxmate's GitHub repository and parses it
into Python data structures for use by the CLI.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import requests

# GitHub raw URL for tuxmate's data.ts
TUXMATE_DATA_URL = (
    "https://raw.githubusercontent.com/abusoww/tuxmate/main/src/lib/data.ts"
)

# Local cache path
CACHE_DIR = Path.home() / ".cache" / "tuxmate-cli"
CACHE_FILE = CACHE_DIR / "apps.json"
CACHE_EXPIRY_HOURS = 24


@dataclass
class AppData:
    """Represents an application from tuxmate's database."""

    id: str
    name: str
    description: str
    category: str
    targets: dict[str, str]  # distro_id -> package_name
    unavailable_reason: Optional[str] = None


@dataclass
class Distro:
    """Represents a supported Linux distribution."""

    id: str
    name: str
    install_prefix: str


# Supported distributions with their install commands
DISTROS: dict[str, Distro] = {
    "ubuntu": Distro("ubuntu", "Ubuntu", "sudo apt install -y"),
    "debian": Distro("debian", "Debian", "sudo apt install -y"),
    "arch": Distro("arch", "Arch Linux", "sudo pacman -S --needed --noconfirm"),
    "fedora": Distro("fedora", "Fedora", "sudo dnf install -y"),
    "opensuse": Distro("opensuse", "openSUSE", "sudo zypper install -y"),
    "nix": Distro("nix", "Nix", "nix-env -iA nixpkgs."),
    "flatpak": Distro("flatpak", "Flatpak", "flatpak install flathub -y"),
    "snap": Distro("snap", "Snap", "sudo snap install"),
}


class TuxmateDataFetcher:
    """Fetches and parses tuxmate's package database."""

    def __init__(self, force_refresh: bool = False):
        self.force_refresh = force_refresh
        self.apps: list[AppData] = []
        self._load_data()

    def _load_data(self) -> None:
        """Load data from cache or fetch from GitHub."""
        if not self.force_refresh and self._cache_valid():
            self._load_from_cache()
        else:
            self._fetch_and_parse()
            self._save_to_cache()

    def _cache_valid(self) -> bool:
        """Check if cache exists and is not expired."""
        if not CACHE_FILE.exists():
            return False

        import time

        cache_age = time.time() - CACHE_FILE.stat().st_mtime
        return cache_age < (CACHE_EXPIRY_HOURS * 3600)

    def _load_from_cache(self) -> None:
        """Load apps from local cache."""
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                self.apps = [
                    AppData(
                        id=app["id"],
                        name=app["name"],
                        description=app["description"],
                        category=app["category"],
                        targets=app["targets"],
                        unavailable_reason=app.get("unavailable_reason"),
                    )
                    for app in data
                ]
        except (json.JSONDecodeError, KeyError):
            self._fetch_and_parse()
            self._save_to_cache()

    def _fetch_and_parse(self) -> None:
        """Fetch data.ts from GitHub and parse it."""
        try:
            response = requests.get(TUXMATE_DATA_URL, timeout=30)
            response.raise_for_status()
            content = response.text
            self.apps = self._parse_typescript(content)
        except requests.RequestException as e:
            # Try to use cache even if expired
            if CACHE_FILE.exists():
                self._load_from_cache()
            else:
                raise RuntimeError(f"Failed to fetch tuxmate data: {e}")

    def _parse_typescript(self, content: str) -> list[AppData]:
        """Parse TypeScript data.ts file into Python objects."""
        apps = []

        # Find the apps array in the TypeScript file
        apps_match = re.search(
            r"export const apps:\s*AppData\[\]\s*=\s*\[(.*?)\];", content, re.DOTALL
        )
        if not apps_match:
            return apps

        apps_content = apps_match.group(1)

        # Split by app entries - look for { id: patterns
        # Use a more flexible approach
        app_blocks = re.split(r"},\s*(?=\{)", apps_content)

        for block in app_blocks:
            block = block.strip()
            if not block:
                continue

            # Clean up the block
            if not block.startswith("{"):
                block = "{" + block
            if not block.endswith("}"):
                block = block + "}"

            # Extract fields
            id_match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", block)
            name_match = re.search(r"name:\s*['\"]([^'\"]+)['\"]", block)
            desc_match = re.search(r"description:\s*['\"]([^'\"]+)['\"]", block)
            cat_match = re.search(r"category:\s*['\"]([^'\"]+)['\"]", block)

            if not all([id_match, name_match, desc_match, cat_match]):
                continue

            app_id = id_match.group(1)
            name = name_match.group(1)
            description = desc_match.group(1)
            category = cat_match.group(1)

            # Parse targets
            targets = {}
            targets_match = re.search(r"targets:\s*\{([^}]+)\}", block)
            if targets_match:
                targets_str = targets_match.group(1)
                # Match key: 'value' or key: "value"
                for match in re.finditer(r"(\w+):\s*['\"]([^'\"]+)['\"]", targets_str):
                    distro, package = match.groups()
                    targets[distro] = package

            # Parse unavailableReason if present
            unavail_match = re.search(
                r"unavailableReason:\s*['\"]([^'\"]*)['\"]", block
            )
            unavail = unavail_match.group(1) if unavail_match else None

            apps.append(
                AppData(
                    id=app_id,
                    name=name,
                    description=description,
                    category=category,
                    targets=targets,
                    unavailable_reason=unavail if unavail else None,
                )
            )

        return apps

    def _save_to_cache(self) -> None:
        """Save parsed apps to local cache."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        data = [
            {
                "id": app.id,
                "name": app.name,
                "description": app.description,
                "category": app.category,
                "targets": app.targets,
                "unavailable_reason": app.unavailable_reason,
            }
            for app in self.apps
        ]

        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def get_apps(self) -> list[AppData]:
        """Return all apps."""
        return self.apps

    def get_app(self, app_id: str) -> Optional[AppData]:
        """Get a specific app by ID."""
        for app in self.apps:
            if app.id == app_id:
                return app
        return None

    def search_apps(self, query: str) -> list[AppData]:
        """Search apps by name, description, or ID."""
        query = query.lower()
        return [
            app
            for app in self.apps
            if query in app.id.lower()
            or query in app.name.lower()
            or query in app.description.lower()
        ]

    def get_apps_by_category(self, category: str) -> list[AppData]:
        """Get apps in a specific category."""
        return [app for app in self.apps if app.category.lower() == category.lower()]

    def get_categories(self) -> list[str]:
        """Get all unique categories."""
        return sorted(set(app.category for app in self.apps))

    def get_available_apps(self, distro: str) -> list[AppData]:
        """Get apps available for a specific distro."""
        return [app for app in self.apps if distro in app.targets]


def detect_distro() -> Optional[str]:
    """Detect the current Linux distribution."""
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return None

    content = os_release.read_text()

    # Check ID and ID_LIKE
    id_match = re.search(r"^ID=(.+)$", content, re.MULTILINE)
    id_like_match = re.search(r"^ID_LIKE=(.+)$", content, re.MULTILINE)

    distro_id = id_match.group(1).strip("\"'") if id_match else ""
    id_like = id_like_match.group(1).strip("\"'") if id_like_match else ""

    # Map distro ID to our supported distros
    distro_id_lower = distro_id.lower()

    if distro_id_lower in ["ubuntu", "pop", "linuxmint", "elementary", "zorin"]:
        return "ubuntu"
    elif distro_id_lower == "debian":
        return "debian"
    elif distro_id_lower in ["arch", "manjaro", "endeavouros", "garuda"]:
        return "arch"
    elif distro_id_lower == "fedora":
        return "fedora"
    elif distro_id_lower in ["opensuse", "opensuse-leap", "opensuse-tumbleweed"]:
        return "opensuse"
    elif "ubuntu" in id_like or "debian" in id_like:
        return "ubuntu"
    elif "arch" in id_like:
        return "arch"
    elif "fedora" in id_like:
        return "fedora"

    return None
