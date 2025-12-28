#!/bin/bash
# tuxmate-cli.sh - Bash wrapper for tuxmate-cli
# Handles dependency checking and provides easy access to tuxmate-cli commands

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║         TuxMate CLI v0.1.0                ║"
    echo "║   Linux Package Installer Made Easy       ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            return 0
        fi
    fi

    echo -e "${RED}✗ Python 3.10+ is required${NC}"
    echo -e "${YELLOW}  Install with: sudo apt install python3${NC}"
    return 1
}

check_uv() {
    if command -v uv &> /dev/null; then
        return 0
    fi

    echo -e "${YELLOW}Installing uv package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
}

setup_venv() {
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        echo -e "${CYAN}Setting up virtual environment...${NC}"
        cd "$SCRIPT_DIR"
        uv sync
    fi
}

run_cli() {
    cd "$SCRIPT_DIR"
    uv run python -m tuxmate_cli.cli "$@"
}

# Main execution
main() {
    # Check dependencies
    check_python || exit 1
    check_uv
    setup_venv

    # If no arguments, show help
    if [ $# -eq 0 ]; then
        print_banner
        run_cli --help
    else
        run_cli "$@"
    fi
}

main "$@"
