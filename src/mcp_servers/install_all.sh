#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 17:39:56 (ywatanabe)"
# File: ./src/mcp_servers/install_all.sh

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
#\!/bin/bash
# ----------------------------------------

# Install all SciTeX MCP servers

echo "Installing all SciTeX MCP servers..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Install requirements first
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "⚠️  Some dependencies failed to install. Continuing anyway..."
    fi
else
    echo "Warning: requirements.txt not found"
fi

# Install base server first
echo "Installing scitex-base first..."
if [ -d "$SCRIPT_DIR/scitex-base" ]; then
    cd "$SCRIPT_DIR/scitex-base"
    pip install -e .
    if [ $? -eq 0 ]; then
        echo "✅ scitex-base installed successfully"
    else
        echo "❌ Failed to install scitex-base"
        echo "Base server is required. Exiting..."
        exit 1
    fi
else
    echo "Warning: scitex-base not found. Continuing anyway..."
fi

# Array of available servers
SERVERS=(
    "scitex-io"
    "scitex-plt"
    "scitex-analyzer"
    "scitex-framework"
    "scitex-config"
    "scitex-orchestrator"
    "scitex-stats"
    "scitex-pd"
    "scitex-validator"
    "scitex-dsp"
    "scitex-torch"
    "scitex-launcher"
    "scitex-ai"
    "scitex-linalg"
    "scitex-db"
    "scitex-parallel"
    "scitex-viz"
    "scitex-time"
    "scitex-ml"
    "scitex-opt"
    "scitex-signal"
    "scitex-utils"
    "scitex-data"
    "scitex-project"
    "scitex-scholar"
)

# Function to check if server directory exists
check_server() {
    local server=$1
    if [ \! -d "$SCRIPT_DIR/$server" ]; then
        echo "Warning: Server directory $server not found"
        return 1
    fi
    if [ \! -f "$SCRIPT_DIR/$server/pyproject.toml" ]; then
        echo "Warning: $server/pyproject.toml not found"
        return 1
    fi
    return 0
}

# Install servers
for server in "${SERVERS[@]}"; do
    if check_server "$server"; then
        echo ""
        echo "Installing $server..."
        cd "$SCRIPT_DIR/$server"
        pip install -e .
        if [ $? -eq 0 ]; then
            echo "✅ $server installed successfully"
        else
            echo "❌ Failed to install $server"
        fi
    fi
done

echo ""
echo "Installation complete\!"
echo "You can now use the MCP servers with your MCP-compatible tools."
echo "See mcp_config_example.json for configuration."

# EOF