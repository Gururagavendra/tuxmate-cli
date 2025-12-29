"""
CLI interface for tuxmate-cli.

Provides commands for searching, listing, and installing packages
using tuxmate's package database.
"""

import re
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from . import __version__
from .data import TuxmateDataFetcher, detect_distro
from .generator import ScriptGenerator

console = Console()

# Security: Input validation pattern for package/app IDs
VALID_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")


def validate_input(value: str, field_name: str = "input") -> str:
    """Validate user input to prevent injection attacks."""
    if not value or len(value) > 256:
        raise click.BadParameter(f"{field_name} must be 1-256 characters")
    if not VALID_ID_PATTERN.match(value):
        raise click.BadParameter(
            f"{field_name} contains invalid characters. "
            "Only alphanumeric, dash, underscore, and dot allowed."
        )
    return value


@click.group()
@click.version_option(version=__version__, prog_name="tuxmate-cli")
def cli():
    """TuxMate CLI - Install Linux packages with ease.

    A command-line interface that leverages tuxmate's curated package database
    to install applications across multiple Linux distributions.
    """
    pass


@cli.command()
def update():
    """Update the local package database cache from tuxmate.

    Note: By default, tuxmate-cli always fetches fresh data.
    This command explicitly updates the cache for offline use.
    Use the --cache flag with other commands to use cached data.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Fetching latest package data from tuxmate...", total=None)
        try:
            fetcher = TuxmateDataFetcher(force_refresh=True, use_cache=True)
            console.print(
                f"[green]✓[/green] Cache updated! {len(fetcher.apps)} packages available"
            )
            console.print(
                "[dim]Use --cache flag with commands to use cached data (faster, may be stale)[/dim]"
            )
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to update: {e}")
            sys.exit(1)


@cli.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--distro", "-d", help="Filter by distro availability")
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def list(category: Optional[str], distro: Optional[str], cache: bool):
    """List available packages."""
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    apps = fetcher.apps

    if category:
        apps = [a for a in apps if a.category.lower() == category.lower()]

    if distro:
        apps = [a for a in apps if distro in a.targets]

    if not apps:
        console.print("[yellow]No packages found[/yellow]")
        return

    table = Table(title=f"Available Packages ({len(apps)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Category", style="green")
    table.add_column("Description")

    for app in apps[:50]:  # Limit to 50 for readability
        table.add_row(app.id, app.name, app.category, app.description)

    console.print(table)

    if len(apps) > 50:
        console.print(f"[dim]...and {len(apps) - 50} more. Use search to filter.[/dim]")


@cli.command()
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def categories(cache: bool):
    """List all package categories."""
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    cats = fetcher.get_categories()

    table = Table(title="Package Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")

    for cat in cats:
        count = len(fetcher.get_apps_by_category(cat))
        table.add_row(cat, str(count))

    console.print(table)


@cli.command()
@click.argument("query")
@click.option("--distro", "-d", help="Filter by distro availability")
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def search(query: str, distro: Optional[str], cache: bool):
    """Search for packages by name or description."""
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    apps = fetcher.search_apps(query)

    if distro:
        apps = [a for a in apps if distro in a.targets]

    if not apps:
        console.print(f"[yellow]No packages found for '{query}'[/yellow]")
        return

    table = Table(title=f"Search Results for '{query}' ({len(apps)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Category", style="green")
    table.add_column("Description")

    for app in apps:
        table.add_row(app.id, app.name, app.category, app.description)

    console.print(table)


@cli.command()
@click.argument("app_id")
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def info(app_id: str, cache: bool):
    """Show detailed information about a package."""
    # Security: Validate input
    try:
        app_id = validate_input(app_id, "app_id")
    except click.BadParameter as e:
        console.print(f"[red]✗[/red] {e.message}")
        sys.exit(1)

    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    app = fetcher.get_app(app_id)

    if not app:
        console.print(f"[red]✗[/red] Package '{app_id}' not found")
        sys.exit(1)

    # Build availability table
    avail_table = Table(show_header=False, box=None)
    avail_table.add_column("Distro", style="cyan")
    avail_table.add_column("Package")

    for distro_id, distro in fetcher.distros.items():
        if distro_id in app.targets:
            avail_table.add_row(distro.name, f"[green]{app.targets[distro_id]}[/green]")
        else:
            avail_table.add_row(distro.name, "[dim]Not available[/dim]")

    content = f"""[bold]{app.name}[/bold]
[dim]{app.description}[/dim]

[cyan]Category:[/cyan] {app.category}
[cyan]ID:[/cyan] {app.id}

[cyan]Availability:[/cyan]
"""

    panel = Panel(content, title=f"📦 {app.name}", border_style="blue")
    console.print(panel)
    console.print(avail_table)

    if app.unavailable_reason:
        console.print(f"\n[yellow]Note:[/yellow] {app.unavailable_reason}")


@cli.command()
@click.argument("packages", nargs=-1, required=True)
@click.option(
    "--distro", "-d", help="Target distribution (auto-detected if not specified)"
)
@click.option("--flatpak", "-f", is_flag=True, help="Include Flatpak fallbacks")
@click.option("--snap", "-s", is_flag=True, help="Include Snap fallbacks")
@click.option("--dry-run", "-n", is_flag=True, help="Show script without executing")
@click.option("--output", "-o", type=click.Path(), help="Save script to file")
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def install(
    packages: tuple,
    distro: Optional[str],
    flatpak: bool,
    snap: bool,
    dry_run: bool,
    output: Optional[str],
    cache: bool,
):
    """Install packages.

    PACKAGES: One or more package IDs to install.

    Examples:

        tuxmate-cli install firefox neovim git

        tuxmate-cli install vscode --flatpak

        tuxmate-cli install firefox --distro arch --dry-run
    """
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    # Security: Validate all package inputs
    validated_packages = []
    for pkg in packages:
        try:
            validated_packages.append(validate_input(pkg, "package"))
        except click.BadParameter as e:
            console.print(f"[red]✗[/red] Invalid package '{pkg}': {e.message}")
            sys.exit(1)

    # Find requested apps
    apps_to_install = []
    not_found = []

    for pkg in validated_packages:
        app = fetcher.get_app(pkg)
        if app:
            apps_to_install.append(app)
        else:
            # Try fuzzy search
            results = fetcher.search_apps(pkg)
            if results:
                apps_to_install.append(results[0])
                console.print(f"[yellow]'{pkg}' → Using '{results[0].id}'[/yellow]")
            else:
                not_found.append(pkg)

    if not_found:
        console.print(f"[red]✗[/red] Packages not found: {', '.join(not_found)}")
        console.print("[yellow]⚠[/yellow] Continuing with found packages...")

    if not apps_to_install:
        console.print("[red]✗[/red] No valid packages to install")
        sys.exit(1)

    # Generate script
    try:
        generator = ScriptGenerator(distro=distro)
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)

    result = generator.generate(
        apps_to_install, include_flatpak=flatpak, include_snap=snap
    )

    if result.package_count == 0:
        console.print(f"[yellow]No packages available for {result.distro}[/yellow]")
        sys.exit(1)

    # Output handling
    if output:
        with open(output, "w") as f:
            f.write(result.script)
        console.print(f"[green]✓[/green] Script saved to {output}")
        console.print(f"[dim]Run with: bash {output}[/dim]")
        return

    if dry_run:
        console.print(
            Panel(result.script, title="Generated Script", border_style="blue")
        )
        return

    # Execute the script
    console.print(
        f"[cyan]Installing {result.package_count} packages on {result.distro}...[/cyan]\n"
    )

    import subprocess

    try:
        subprocess.run(["bash", "-c", result.script], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Installation failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled[/yellow]")
        sys.exit(130)


@cli.command()
@click.argument("packages", nargs=-1, required=True)
@click.option("--distro", "-d", help="Target distribution")
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def script(packages: tuple, distro: Optional[str], cache: bool):
    """Generate installation script for packages (stdout).

    Useful for piping to bash or saving to a file.

    Examples:

        tuxmate-cli script firefox neovim | bash

        tuxmate-cli script firefox neovim > install.sh
    """
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
        apps = [fetcher.get_app(p) for p in packages]
        apps = [a for a in apps if a]

        if not apps:
            sys.exit(1)

        generator = ScriptGenerator(distro=distro)
        result = generator.generate(apps)

        print(result.script)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate script: {e}")
        sys.exit(1)


@cli.command()
@click.argument("packages", nargs=-1, required=True)
@click.option("--distro", "-d", help="Target distribution")
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def oneliner(packages: tuple, distro: Optional[str], cache: bool):
    """Generate a one-liner install command.

    Examples:

        tuxmate-cli oneliner firefox neovim git
    """
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
        apps = [fetcher.get_app(p) for p in packages]
        apps = [a for a in apps if a]

        if not apps:
            console.print("[red]✗[/red] No valid packages found")
            sys.exit(1)

        generator = ScriptGenerator(distro=distro)
        cmd = generator.generate_one_liner(apps)

        console.print(Panel(cmd, title="One-liner Command", border_style="green"))
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--cache", is_flag=True, help="Use cached data (faster, may be stale)")
def distros(cache: bool):
    """List supported distributions."""
    try:
        fetcher = TuxmateDataFetcher(use_cache=cache)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    detected = detect_distro()

    table = Table(title="Supported Distributions")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Install Command")
    table.add_column("Status")

    for distro_id, distro in fetcher.distros.items():
        status = "[green]← Detected[/green]" if distro_id == detected else ""
        table.add_row(distro_id, distro.name, distro.install_prefix, status)

    console.print(table)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
