#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-06 21:03:01 (ywatanabe)"
# File: ./.dev_pac/install_zotero.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------
# Install Zotero on Linux (WSL)

echo "=================================================="
echo "Installing Zotero 7.0.22 on Linux"
echo "=================================================="

sudo apt-get update && sudo apt-get install -y libdbus-glib-1-2 libgtk-3-0 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libxtst6 libasound2 libatspi2.0-0 libdrm2 libgbm1 libxss1

# Set installation directory
INSTALL_DIR="$HOME/opt"
ZOTERO_TAR="$HOME/Downloads/Zotero-7.0.22_linux-x86_64.tar.bz2"

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Extract Zotero
echo "Extracting Zotero..."
cd "$INSTALL_DIR"
tar -xjf "$ZOTERO_TAR"

# Create desktop entry
echo "Creating desktop entry..."
cat > ~/.local/share/applications/zotero.desktop << EOF
[Desktop Entry]
Name=Zotero
Comment=Zotero Reference Manager
Exec=$INSTALL_DIR/Zotero_linux-x86_64/zotero
Icon=$INSTALL_DIR/Zotero_linux-x86_64/chrome/icons/default/default256.png
Type=Application
Categories=Office;Education;
StartupNotify=true
EOF

# Create symbolic link in ~/bin
echo "Creating command line launcher..."
mkdir -p ~/bin
ln -sf "$INSTALL_DIR/Zotero_linux-x86_64/zotero" ~/bin/zotero

# Add ~/bin to PATH if not already there
if ! echo "$PATH" | grep -q "$HOME/bin"; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    echo "Added ~/bin to PATH"
fi

echo ""
echo "=================================================="
echo "✅ Zotero installation complete!"
echo "=================================================="
echo ""
echo "You can now run Zotero using:"
echo "  1. Command line: zotero"
echo "  2. Full path: $INSTALL_DIR/Zotero_linux-x86_64/zotero"
echo ""
echo "Note: In WSL, you might want to use Windows Zotero instead"
echo "for better integration. But Linux Zotero will work too!"
echo ""
echo "To test: $INSTALL_DIR/Zotero_linux-x86_64/zotero --version"

# EOF