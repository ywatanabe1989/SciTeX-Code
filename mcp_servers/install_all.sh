#\!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:20:00 (ywatanabe)"
# File: ./mcp_servers/install_all.sh
# ----------------------------------------

# Install all SciTeX MCP servers

echo "Installing all SciTeX MCP servers..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

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
    # Add more servers as they are implemented
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
