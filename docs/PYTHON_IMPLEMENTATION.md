# Script Generation: Python Implementation

While [tuxmate](https://github.com/abusoww/tuxmate) (the web app) uses TypeScript for browser-based script generation, **tuxmate-cli** implements the same logic in Python for Linux terminal usage.

## Why Python Instead of TypeScript?

### Tuxmate's Context
- Web application running in browsers
- Must use JavaScript/TypeScript (browser constraint)
- Generates scripts for download
- User copies/downloads script to run on their system

### Our Context
- Terminal application running on Linux systems
- Python is pre-installed on all Linux distributions
- No Node.js dependency required
- Scripts execute directly on the system
- Better integration with Linux ecosystem (subprocess, os modules)
- Native terminal experience with rich formatting

## Design Philosophy

Both implementations achieve the same goal: generate distro-specific installation scripts. The choice of language is driven by the execution environment:
- **Web → TypeScript** (runs in browser)
- **Terminal → Python** (native to Linux)

## Script Generation Approach

We follow tuxmate's patterns from [`src/lib/scripts/`](https://github.com/abusoww/tuxmate/tree/main/src/lib/scripts).

> **Note:** For a complete list of implemented and planned features, see the [Roadmap section in README.md](../README.md#roadmap).

## Code Comparison

### TypeScript (Tuxmate Web)
```typescript
export function generateUbuntuScript(packages: string[]): string {
  return `#!/bin/bash
sudo apt update
sudo apt install -y ${packages.join(' ')}
`;
}
```

### Python (Tuxmate CLI)
```python
def generate_ubuntu_script(packages: list[str]) -> str:
    return f"""#!/bin/bash
sudo apt update
sudo apt install -y {' '.join(packages)}
"""
```

Same logic, different language - each optimized for its runtime environment.

## Benefits of Python Implementation

1. **No Additional Dependencies**: Python ships with every Linux distro
2. **Direct System Integration**: Native subprocess handling for script execution
3. **Rich Terminal UI**: Easy integration with `rich` library for beautiful output
4. **Consistent Tooling**: Single language for entire CLI application
5. **Easier Packaging**: Standard Python packaging (pip, PyPI)
