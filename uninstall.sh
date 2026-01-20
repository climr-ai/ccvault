#!/bin/bash
# CCVault Uninstaller
# Run: curl -fsSL https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/uninstall.sh | bash

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

# Banner
echo -e "${MAGENTA}"
cat << 'EOF'

   ██████╗ ██████╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
  ██╔════╝██╔════╝██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
  ██║     ██║     ██║   ██║███████║██║   ██║██║     ██║
  ██║     ██║     ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║
  ╚██████╗╚██████╗ ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║
   ╚═════╝ ╚═════╝  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝

                    Uninstaller

EOF
echo -e "${NC}"

echo -e "  ${WHITE}We're sorry to see you go!${NC}"
echo ""

# Check if ccvault is installed
step "Checking installation..."
if command -v ccvault &> /dev/null || command -v uv &> /dev/null && uv tool list 2>/dev/null | grep -q ccvault; then
    success "CCVault installation found"
else
    warn "CCVault doesn't appear to be installed"
    echo ""
    exit 0
fi

# Data directories
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/dnd-manager"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/dnd-manager"

# Check for character data
if [ -d "$DATA_DIR/characters" ]; then
    CHAR_COUNT=$(find "$DATA_DIR/characters" -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$CHAR_COUNT" -gt 0 ]; then
        echo ""
        echo -e "  ${YELLOW}You have $CHAR_COUNT character(s) saved.${NC}"
        echo -e "  ${GRAY}Location: $DATA_DIR/characters${NC}"
        echo ""
    fi
fi

# Confirm uninstall
echo -e "  ${WHITE}What would you like to remove?${NC}"
echo ""
echo "  1) CCVault only (keep your characters and settings)"
echo "  2) Everything (CCVault + characters + settings)"
echo "  3) Cancel"
echo ""
read -p "  Choose [1/2/3]: " -n 1 -r CHOICE
echo ""

case $CHOICE in
    1)
        REMOVE_DATA=false
        ;;
    2)
        REMOVE_DATA=true
        echo ""
        echo -e "  ${YELLOW}This will permanently delete all your characters and settings!${NC}"
        read -p "  Are you sure? (y/N) " -n 1 -r CONFIRM
        echo ""
        if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "  ${GREEN}Uninstall cancelled. Your data is safe.${NC}"
            exit 0
        fi
        ;;
    *)
        echo ""
        echo -e "  ${GREEN}Uninstall cancelled.${NC}"
        exit 0
        ;;
esac

# Uninstall ccvault
step "Removing CCVault..."
if command -v uv &> /dev/null; then
    if uv tool uninstall ccvault 2>/dev/null; then
        success "CCVault removed"
    else
        warn "CCVault was not installed via uv tool"
    fi
else
    warn "uv not found - CCVault may need manual removal"
fi

# Remove data if requested
if [ "$REMOVE_DATA" = true ]; then
    step "Removing data..."

    if [ -d "$DATA_DIR" ]; then
        rm -rf "$DATA_DIR"
        success "Removed data directory: $DATA_DIR"
    fi

    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR"
        success "Removed config directory: $CONFIG_DIR"
    fi
fi

# Success message
echo -e "${GREEN}"
cat << 'EOF'

  ╔════════════════════════════════════════════════════════════╗
  ║                                                            ║
  ║   CCVault has been uninstalled.                            ║
  ║                                                            ║
  ║   Thank you for trying CCVault!                            ║
  ║                                                            ║
  ║   If you have feedback, we'd love to hear it:              ║
  ║   https://github.com/jaredgiosinuff/dnd-manager/issues     ║
  ║                                                            ║
  ║   To reinstall anytime:                                    ║
  ║   curl -fsSL https://git.io/ccvault | bash                 ║
  ║                                                            ║
  ╚════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

if [ "$REMOVE_DATA" = false ]; then
    echo -e "  ${GRAY}Your characters are still saved at: $DATA_DIR/characters${NC}"
    echo ""
fi

echo -e "  ${CYAN}May your future adventures be legendary!${NC}"
echo ""
