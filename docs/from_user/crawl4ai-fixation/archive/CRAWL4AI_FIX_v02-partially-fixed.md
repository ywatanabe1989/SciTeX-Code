<!-- ---
!-- Timestamp: 2025-08-07 04:44:10
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/docs/from_user/crawl4ai-fixation/CRAWL4AI_FIX_v02-partially-fixed.md
!-- --- -->

# Crawl4AI MCP Server Fix Documentation

## Status: FIXED ✅
- All fixes have been applied and committed to a new Docker image: `crawl4ai:fixed`
- MCP SSE endpoint is responding at `http://localhost:11235/mcp/sse`
- Direct API is functional at `http://localhost:11235/`

## Quick Start (Using Pre-Fixed Image)

```bash
# Use the pre-fixed image that already has all fixes applied
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g crawl4ai:fixed
```

## Automated Fix Process (Using Scripts in This Directory)

### Step 1: Start Container
```bash
export CRAWL4AI_VERSION=0.7.0-r1
docker pull unclecode/crawl4ai:$CRAWL4AI_VERSION
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:$CRAWL4AI_VERSION

# Get container ID
CONTAINER_ID=$(docker ps | grep crawl4ai | awk '{print $1}')
echo "Container ID: $CONTAINER_ID"
```

### Step 2: Apply All Fixes (In Order)
```bash
# Fix 1: Set proper file permissions (required before making any edits)
docker exec -u root $CONTAINER_ID chown -R appuser:appuser /usr/local/lib/python3.12/site-packages/starlette/
docker exec -u root $CONTAINER_ID chown -R appuser:appuser /app/

# Fix 2: Apply Starlette middleware fix (handles MCP pathsend messages)
docker cp ./fix_starlette.py $CONTAINER_ID:/tmp/
docker exec $CONTAINER_ID python /tmp/fix_starlette.py

# Fix 3: Apply server JSON serialization fix (handles model_dump)
docker cp ./fix_server_json.py $CONTAINER_ID:/tmp/
docker exec $CONTAINER_ID python /tmp/fix_server_json.py

# Fix 4: Apply port configuration fix (changes port from 11234 to 11235)
docker cp ./fix_config_port.py $CONTAINER_ID:/tmp/
docker exec $CONTAINER_ID python /tmp/fix_config_port.py
```

### Step 3: Save Fixed Image and Restart
```bash
# Commit the fixed container to a new image
docker commit $CONTAINER_ID crawl4ai:fixed

# Restart the container with fixes
docker restart $CONTAINER_ID
```

## Manual Fix Process (Step-by-Step)

### Prerequisites
```bash
export CRAWL4AI_VERSION=0.7.0-r1
docker pull unclecode/crawl4ai:$CRAWL4AI_VERSION
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:$CRAWL4AI_VERSION
CONTAINER_ID=$(docker ps | grep crawl4ai | awk '{print $1}')
```

### Fix 1: File Permissions (MUST BE FIRST)
```bash
# Grant write permissions to appuser for required directories
docker exec -u root $CONTAINER_ID chown -R appuser:appuser /usr/local/lib/python3.12/site-packages/starlette/
docker exec -u root $CONTAINER_ID chown -R appuser:appuser /app/
```

### Fix 2: Starlette Middleware
Location: `/usr/local/lib/python3.12/site-packages/starlette/middleware/base.py`

Find the `body_stream()` method around line 158 and add:
```python
async def body_stream() -> BodyStreamGenerator:
    async for message in recv_stream:
        if message["type"] == "http.response.start":  # NEW LINE
            yield message                              # NEW LINE
            continue                                   # NEW LINE
        if message["type"] == "http.response.pathsend":
            yield message
            break
        # ... rest of the method
```

### Fix 3: JSON Serialization
Location: `/app/server.py` around line 446

Replace:
```python
return JSONResponse(res)
```

With:
```python
return JSONResponse(res.model_dump() if hasattr(res, 'model_dump') else res.__dict__)
```

### Fix 4: Port Configuration
Location: `/app/config.yml` line 6

Replace:
```yaml
port: 11234
```

With:
```yaml
port: 11235
```

### Fix 5: Commit and Restart
```bash
# Save all changes to a new image
docker commit $CONTAINER_ID crawl4ai:fixed

# Restart to apply all changes
docker restart $CONTAINER_ID
```

## Testing

### Test 1: SSE Endpoint
```bash
# Should return HTTP 200 and stream data
timeout 10 curl -v http://localhost:11235/mcp/sse
```

### Test 2: Direct API
```bash
curl -X POST "http://localhost:11235/crawl" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "word_count_threshold": 10}'
```

### Test 3: Playground
Visit: http://localhost:11235/playground

## MCP Configuration

Already configured in `.claude/mcp-config.json`:
```json
"crawl4ai": {
    "type": "sse",
    "url": "http://localhost:11235/mcp/sse"
}
```

## Files in This Directory

| File | Purpose | When to Use |
|------|---------|-------------|
| `fix_starlette.py` | Fixes Starlette middleware to handle MCP messages | After setting permissions |
| `fix_server_json.py` | Fixes JSON serialization for model objects | After Starlette fix |
| `fix_config_port.py` | Changes port from 11234 to 11235 | After JSON fix |
| `CRAWL4AI_FIX_v01.md` | Original documentation | Reference only |

## Troubleshooting

### Container won't start?
```bash
docker logs crawl4ai --tail 50
```

### SSE endpoint not responding?
```bash
# Check if port 11235 is listening
docker exec $CONTAINER_ID netstat -tlnp | grep 11235
```

### MCP not appearing in Claude Code?
1. Restart Claude Code completely
2. Check MCP config: `cat ~/.claude/mcp-config.json`
3. Verify SSE endpoint: `curl -v http://localhost:11235/mcp/sse`

## Known Issues

- MCP tools may not immediately appear in Claude Code after fixes
- Direct API calls work but MCP integration requires Claude Code restart
- Container must be restarted after applying fixes for changes to take effect

<!-- EOF -->