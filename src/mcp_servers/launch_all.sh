#\!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:16:00 (ywatanabe)"
# File: ./mcp_servers/launch_all.sh
# ----------------------------------------

# Launch all SciTeX MCP servers concurrently

echo "Starting all SciTeX MCP servers..."

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
    if [ \! -f "$SCRIPT_DIR/$server/server.py" ]; then
        echo "Warning: $server/server.py not found"
        return 1
    fi
    return 0
}

# Launch servers
PIDS=()
for server in "${SERVERS[@]}"; do
    if check_server "$server"; then
        echo "Launching $server..."
        cd "$SCRIPT_DIR/$server"
        python -m server &
        PIDS+=($\!)
        echo "$server launched with PID ${PIDS[-1]}"
    fi
done

echo ""
echo "All servers launched. PIDs: ${PIDS[@]}"
echo "Press Ctrl+C to stop all servers"

# Function to kill all servers on exit
cleanup() {
    echo ""
    echo "Stopping all servers..."
    for pid in "${PIDS[@]}"; do
        kill $pid 2>/dev/null
    done
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for all background processes
wait

# EOF
