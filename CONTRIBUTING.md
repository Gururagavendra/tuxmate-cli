# Contributing to TuxMate CLI

Thank you for considering contributing to TuxMate CLI! 🎉

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Use the GitHub issue tracker
- Include clear steps to reproduce
- Mention your OS and Python version

### Submitting Pull Requests

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test your changes: `uv run tuxmate-cli --help`
5. Commit with clear messages: `git commit -m "feat: add feature"`
6. Push to your fork: `git push origin feature/your-feature`
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/tuxmate-cli.git
cd tuxmate-cli

# Install dependencies
uv sync

# Run the CLI
uv run tuxmate-cli --help

# Test your changes
uv run tuxmate-cli list
```

## Commit Message Format

We follow simple conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Example: `feat: add already-installed package detection`

## Code Style

- Follow existing code patterns
- Use type hints where possible
- Keep functions focused and small
- Add docstrings to functions
- Run pre-commit hooks (they'll auto-format)

## What to Work On

Check the [Roadmap in README.md](README.md#roadmap) for ideas. Features marked as **Must have** or **Should have** are great starting points!

## Questions?

Open an issue or start a discussion. We're happy to help!

## License

By contributing, you agree that your contributions will be licensed under GPL-3.0.
