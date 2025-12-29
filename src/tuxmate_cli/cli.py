"""
CLI interface for tuxmate-cli.

Provides commands for searching, listing, and installing packages
using tuxmate's package database.
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from .data import TuxmateDataFetcher, detect_distro
from .generator import ScriptGenerator

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="tuxmate-cli")
def cli():
    """TuxMate CLI - Install Linux packages with ease.

    A command-line interface that leverages tuxmate's curated package database
    to install applications across multiple Linux distributions.
    """
    pass


@cli.command()
@click.option("--refresh", "-r", is_flag=True, help="Force refresh package database")
def update(refresh: bool):
    """Update the local package database from tuxmate."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Fetching latest package data from tuxmate...", total=None)
        try:
            fetcher = TuxmateDataFetcher(force_refresh=True)
            console.print(
                f"[green]✓[/green] Updated! {len(fetcher.apps)} packages available"
            )
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to update: {e}")
            sys.exit(1)


@cli.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--distro", "-d", help="Filter by distro availability")
def list(category: Optional[str], distro: Optional[str]):
    """List available packages."""
    try:
        fetcher = TuxmateDataFetcher()
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
def categories():
    """List all package categories."""
    try:
        fetcher = TuxmateDataFetcher()
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
def search(query: str, distro: Optional[str]):
    """Search for packages by name or description."""
    try:
        fetcher = TuxmateDataFetcher()
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
def info(app_id: str):
    """Show detailed information about a package."""
    try:
        fetcher = TuxmateDataFetcher()
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
def install(
    packages: tuple,
    distro: Optional[str],
    flatpak: bool,
    snap: bool,
    dry_run: bool,
    output: Optional[str],
):
    """Install packages.

    PACKAGES: One or more package IDs to install.

    Examples:

        tuxmate-cli install firefox neovim git

        tuxmate-cli install vscode --flatpak

        tuxmate-cli install firefox --distro arch --dry-run
    """
    try:
        fetcher = TuxmateDataFetcher()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load data: {e}")
        sys.exit(1)

    # Find requested apps
    apps_to_install = []
    not_found = []

    for pkg in packages:
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
        if not apps_to_install:
            sys.exit(1)

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
def script(packages: tuple, distro: Optional[str]):
    """Generate installation script for packages (stdout).

    Useful for piping to bash or saving to a file.

    Examples:

        tuxmate-cli script firefox neovim | bash

        tuxmate-cli script firefox neovim > install.sh
    """
    try:
        fetcher = TuxmateDataFetcher()
        apps = [fetcher.get_app(p) for p in packages]
        apps = [a for a in apps if a]

        if not apps:
            sys.exit(1)

        generator = ScriptGenerator(distro=distro)
        result = generator.generate(apps)

        print(result.script)
    except Exception:
        sys.exit(1)


@cli.command()
@click.argument("packages", nargs=-1, required=True)
@click.option("--distro", "-d", help="Target distribution")
def oneliner(packages: tuple, distro: Optional[str]):
    """Generate a one-liner install command.

    Examples:

        tuxmate-cli oneliner firefox neovim git
    """
    try:
        fetcher = TuxmateDataFetcher()
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
def distros():
    """List supported distributions."""
    try:
        fetcher = TuxmateDataFetcher()
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
