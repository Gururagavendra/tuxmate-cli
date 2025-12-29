# Version Management

## Single Source of Truth

The version for tuxmate-cli is managed in a single location:

** `/src/tuxmate_cli/__init__.py`**

```python
__version__ = "0.1.0"
```

## How It Works

1. **Source**: Version is defined in [`__init__.py`](src/tuxmate_cli/__init__.py)
2. **CLI**: Automatically imported and used in [`cli.py`](src/tuxmate_cli/cli.py)
3. **Package**: Read by hatchling from `__init__.py` during build (configured in [`pyproject.toml`](pyproject.toml))

## Changing the Version

To update the version, **only change it in one place**:

```bash
# Edit src/tuxmate_cli/__init__.py
# Change: __version__ = "0.1.0"
# To:     __version__ = "0.2.0"
```

The version will automatically update in:
- CLI `--version` command
- Package metadata
- Build artifacts

## Verification

```bash
# Check CLI version
uv run tuxmate-cli --version

# Check Python package version
uv run python -c "from tuxmate_cli import __version__; print(__version__)"
```

## Version Format

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
