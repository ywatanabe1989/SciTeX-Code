#\!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:21:00 (ywatanabe)"  
# File: ./mcp_servers/test_all.sh
# ----------------------------------------

# Test all SciTeX MCP servers

echo "Testing all SciTeX MCP servers..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Array of available servers
SERVERS=(
    "scitex-io"
    "scitex-plt"
    "scitex-analyzer"
)

# Test each server
for server in "${SERVERS[@]}"; do
    if [ -f "$SCRIPT_DIR/$server/test_server.py" ]; then
        echo ""
        echo "========================================="
        echo "Testing $server..."
        echo "========================================="
        cd "$SCRIPT_DIR/$server"
        python test_server.py
        if [ $? -eq 0 ]; then
            echo "✅ $server tests passed"
        else
            echo "❌ $server tests failed"
        fi
    else
        echo "⚠️  No tests found for $server"
    fi
done

echo ""
echo "All tests completed\!"

# EOF
