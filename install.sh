#!/bin/bash
set -e

echo "Installing CCVault - D&D Character Manager"
echo "==========================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source the shell config to get uv in PATH
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
fi

echo "Installing ccvault..."
uv tool install git+https://github.com/jaredgiosinuff/dnd-manager

echo ""
echo "Done! Run 'ccvault' to start."
