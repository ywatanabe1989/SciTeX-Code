#\!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:21:00 (ywatanabe)"  
# File: ./mcp_servers/test_all.sh
# ----------------------------------------

# Test all SciTeX MCP servers

echo "Testing all SciTeX MCP servers..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Array of available servers with test files
SERVERS=(
    "scitex-io"
    "scitex-plt"
    "scitex-stats"
    "scitex-pd"
    "scitex-dsp"
    "scitex-gen"
    "scitex_io_translator"
)

# Test each server
for server in "${SERVERS[@]}"; do
    # Special case for scitex_io_translator
    if [ "$server" = "scitex_io_translator" ]; then
        test_file="test_translator.py"
    else
        test_file="test_server.py"
    fi
    
    if [ -f "$SCRIPT_DIR/$server/$test_file" ]; then
        echo ""
        echo "========================================="
        echo "Testing $server..."
        echo "========================================="
        cd "$SCRIPT_DIR/$server"
        python "$test_file"
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
echo "========================================="
echo "Running integration tests..."
echo "========================================="
cd "$SCRIPT_DIR"
if [ -f "test_integration.py" ]; then
    python test_integration.py
    if [ $? -eq 0 ]; then
        echo "✅ Integration tests passed"
    else
        echo "❌ Integration tests failed"
    fi
else
    echo "⚠️  No integration tests found"
fi

echo ""
echo "All tests completed!"

# EOF
