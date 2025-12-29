"""
Data fetcher module - Downloads and parses tuxmate's package database.

Fetches the latest data.ts from tuxmate's GitHub repository and parses it
into Python data structures for use by the CLI. Uses dukpy (JavaScript interpreter)
to evaluate the TypeScript array directly.
"""

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import requests
import dukpy

# GitHub raw URL for tuxmate's data.ts
TUXMATE_DATA_URL = (
    "https://raw.githubusercontent.com/abusoww/tuxmate/main/src/lib/data.ts"
)

# Local cache path
CACHE_DIR = Path.home() / ".cache" / "tuxmate-cli"
CACHE_FILE = CACHE_DIR / "data.json"


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


# Global distros dict - populated by TuxmateDataFetcher
DISTROS: dict[str, Distro] = {}


class TuxmateDataFetcher:
    """Fetches and parses tuxmate's package database."""

    def __init__(
        self,
        force_refresh: bool = False,
        use_cache: bool = False,
        cache_expiry_hours: int = 24,
    ):
        self.force_refresh = force_refresh
        self.use_cache = use_cache
        self.cache_expiry_hours = cache_expiry_hours
        self.apps: list[AppData] = []
        self.distros: dict[str, Distro] = {}
        self._load_data()
        # Update global DISTROS for backward compatibility
        global DISTROS
        DISTROS.update(self.distros)

    def _load_data(self) -> None:
        """Load data from cache or fetch from GitHub."""
        if self.use_cache and not self.force_refresh and self._cache_valid():
            self._load_from_cache()
        else:
            self._fetch_and_parse()
            if self.use_cache:  # Only save cache if caching is enabled
                self._save_to_cache()

    def _cache_valid(self) -> bool:
        """Check if cache exists and is not expired."""
        if not CACHE_FILE.exists():
            return False

        cache_age = time.time() - CACHE_FILE.stat().st_mtime
        return cache_age < (self.cache_expiry_hours * 3600)

    def _load_from_cache(self, allow_fetch: bool = True) -> None:
        """Load apps and distros from local cache.

        Args:
            allow_fetch: If True, fetch from network if cache is corrupted.
                        If False, raise an exception instead to prevent recursion.
        """
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
                    for app in data.get("apps", [])
                ]
                self.distros = {
                    d["id"]: Distro(
                        id=d["id"],
                        name=d["name"],
                        install_prefix=d["install_prefix"],
                    )
                    for d in data.get("distros", [])
                }
        except (json.JSONDecodeError, KeyError) as e:
            # Cache is corrupted
            if allow_fetch:
                # Re-fetch and save only if caching is enabled
                self._fetch_and_parse()
                if self.use_cache:
                    self._save_to_cache()
            else:
                # Don't fetch to prevent infinite recursion
                raise RuntimeError(f"Cache is corrupted and fetch is disabled: {e}")

    def _fetch_and_parse(self) -> None:
        """Fetch data.ts from GitHub and parse it with retry logic."""
        max_attempts = 3
        initial_delay = 5

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(TUXMATE_DATA_URL, timeout=30)
                response.raise_for_status()
                content = response.text
                self.apps, self.distros = self._parse_typescript(content)
                return  # Success, exit the function
            except requests.RequestException as e:
                if attempt < max_attempts:
                    # Exponential backoff: 5s, 10s, 20s
                    delay = initial_delay * (2 ** (attempt - 1))
                    print(f"Network error (attempt {attempt}/{max_attempts}): {e}")
                    print(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    # Final attempt failed, try cache as fallback
                    if CACHE_FILE.exists():
                        try:
                            print("Using cached data as fallback...")
                            # Use allow_fetch=False to prevent infinite recursion
                            self._load_from_cache(allow_fetch=False)
                            return
                        except Exception:
                            raise RuntimeError(
                                f"Failed to fetch tuxmate data after {max_attempts} attempts and cache is invalid: {e}"
                            )
                    else:
                        raise RuntimeError(
                            f"Failed to fetch tuxmate data after {max_attempts} attempts: {e}"
                        )

    def _parse_typescript(
        self, content: str
    ) -> tuple[list[AppData], dict[str, Distro]]:
        """Parse TypeScript data.ts file using JavaScript interpreter."""
        apps = []
        distros = {}

        # Build JavaScript code with helper functions from data.ts
        js_code = """
        // Define helper functions from data.ts
        var icon = function(set, name, color) {
            return 'https://api.iconify.design/' + set + '/' + name + '.svg' + (color ? '?color=' + encodeURIComponent(color) : '');
        };
        var si = function(name, color) { return icon('simple-icons', name, color); };
        var lo = function(name) { return icon('logos', name); };
        var dev = function(name) { return icon('devicon', name); };
        var sk = function(name) { return icon('skill-icons', name); };
        var vs = function(name) { return icon('vscode-icons', name); };
        var mdi = function(name, color) { return icon('mdi', name, color); };
        var def = si('linux', '#FCC624');
        """

        # Extract distros array
        distros_match = re.search(
            r"export\s+const\s+distros:\s*Distro\[\]\s*=\s*(\[[\s\S]*?\]);",
            content,
            re.DOTALL,
        )
        if distros_match:
            distros_str = distros_match.group(1)
            try:
                parsed_distros = dukpy.evaljs(
                    js_code + f"\nvar distros = {distros_str};\ndistros;"
                )
                for d in parsed_distros:
                    distros[d["id"]] = Distro(
                        id=d["id"],
                        name=d["name"],
                        install_prefix=d["installPrefix"],
                    )
            except Exception as e:
                import warnings

                warnings.warn(f"Failed to parse distros from data.ts: {e}")

        # Extract apps array
        apps_match = re.search(
            r"export\s+const\s+apps:\s*AppData\[\]\s*=\s*(\[[\s\S]*?\]);",
            content,
            re.DOTALL,
        )
        if not apps_match:
            return apps, distros

        array_str = apps_match.group(1)

        try:
            parsed_apps = dukpy.evaljs(js_code + f"\nvar apps = {array_str};\napps;")

            for app in parsed_apps:
                apps.append(
                    AppData(
                        id=app.get("id", ""),
                        name=app.get("name", ""),
                        description=app.get("description", ""),
                        category=app.get("category", ""),
                        targets=app.get("targets", {}),
                        unavailable_reason=app.get("unavailableReason"),
                    )
                )
        except Exception as e:
            raise RuntimeError(f"Failed to parse data.ts: {e}")

        return apps, distros

    def _save_to_cache(self) -> None:
        """Save parsed apps and distros to local cache."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "apps": [
                {
                    "id": app.id,
                    "name": app.name,
                    "description": app.description,
                    "category": app.category,
                    "targets": app.targets,
                    "unavailable_reason": app.unavailable_reason,
                }
                for app in self.apps
            ],
            "distros": [
                {
                    "id": d.id,
                    "name": d.name,
                    "install_prefix": d.install_prefix,
                }
                for d in self.distros.values()
            ],
        }

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


def detect_distro() -> Optional[str]:
    """Detect the current system Linux distribution."""
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
