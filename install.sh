#!/bin/bash
# CCVault Installer - D&D Character Manager
# One-line install: curl -fsSL https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/install.sh | bash

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color

step() { echo -e "\n${CYAN}>>${NC} $1"; }
success() { echo -e "   ${GREEN}[OK]${NC} $1"; }
info() { echo -e "   ${GRAY}$1${NC}"; }
warn() { echo -e "   ${YELLOW}[!]${NC} $1"; }
error() { echo -e "   ${RED}[ERROR]${NC} $1"; }

# ASCII Banner
echo -e "${MAGENTA}"
cat << 'EOF'

   ██████╗ ██████╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
  ██╔════╝██╔════╝██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
  ██║     ██║     ██║   ██║███████║██║   ██║██║     ██║
  ██║     ██║     ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║
  ╚██████╗╚██████╗ ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║
   ╚═════╝ ╚═════╝  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝

        D&D Character Manager - CLI Master Race

EOF
echo -e "${NC}"

echo -e "  ${WHITE}The world's finest CLI-based D&D 5e character creator${NC}"
echo -e "  ${GRAY}Supports: D&D 2014, D&D 2024, Tales of the Valiant${NC}"
echo ""

# Detect OS
step "Checking system..."
OS="$(uname -s)"
case "$OS" in
    Linux*)  OS_NAME="Linux" ;;
    Darwin*) OS_NAME="macOS" ;;
    *)       OS_NAME="Unknown" ;;
esac
success "$OS_NAME detected"

# Check for Python
step "Checking for Python..."
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    success "Found $PY_VERSION"
elif command -v python &> /dev/null; then
    PY_VERSION=$(python --version 2>&1)
    success "Found $PY_VERSION"
else
    warn "Python not found - uv will handle this"
fi

# Install uv if not present
step "Setting up uv (fast Python package manager)..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1)
    success "uv already installed ($UV_VERSION)"
else
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source the shell config to get uv in PATH
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi

    # Also try common uv install locations
    if [ -d "$HOME/.local/bin" ]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi

    success "uv installed successfully"
fi

# Verify uv is available
if ! command -v uv &> /dev/null; then
    error "uv not found in PATH after installation"
    echo ""
    echo -e "   ${YELLOW}Please restart your terminal and run this installer again.${NC}"
    echo -e "   ${GRAY}Or install uv manually: https://docs.astral.sh/uv/${NC}"
    exit 1
fi

# Install ccvault
step "Installing CCVault..."

# Uninstall first if exists (clean install)
uv tool uninstall ccvault 2>/dev/null || true

# Install from GitHub
if uv tool install "git+https://github.com/jaredgiosinuff/dnd-manager"; then
    success "CCVault installed successfully"
else
    error "Failed to install CCVault"
    exit 1
fi

# Verify installation
step "Verifying installation..."

# Add uv tools to path for current session
if [ -d "$HOME/.local/bin" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

if command -v ccvault &> /dev/null; then
    success "ccvault command is available"
else
    warn "ccvault not found in PATH yet"
    info "You may need to restart your terminal"
fi

# Success message
echo -e "${GREEN}"
cat << 'EOF'

  ╔════════════════════════════════════════════════════════════╗
  ║                                                            ║
  ║   Installation complete!                                   ║
  ║                                                            ║
  ║   To start CCVault, open a new terminal and run:           ║
  ║                                                            ║
  ║      ccvault                                                ║
  ║                                                            ║
  ║   Quick commands:                                          ║
  ║      ccvault new "Gandalf" --class Wizard                  ║
  ║      ccvault list                                          ║
  ║      ccvault roll 2d6+5                                    ║
  ║      ccvault ask "How does sneak attack work?"             ║
  ║                                                            ║
  ╚════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

echo -e "  ${CYAN}Welcome to the CLI Master Race!${NC}"
echo -e "  ${GRAY}May your rolls be ever in your favor.${NC}"
echo ""

# Offer to launch now
read -p "  Launch CCVault now? (Y/n) " -n 1 -r REPLY
echo ""
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    if command -v ccvault &> /dev/null; then
        ccvault
    else
        # Try direct path
        if [ -x "$HOME/.local/bin/ccvault" ]; then
            "$HOME/.local/bin/ccvault"
        else
            echo -e "  ${YELLOW}Please restart your terminal first, then run: ccvault${NC}"
        fi
    fi
fi
