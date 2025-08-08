<!-- ---
!-- Timestamp: 2025-08-07 04:19:29
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/docs/from_user/CRAWL4AI_FIX.md
!-- --- -->


0. Pull the latest image
```bash
export CRAWL4AI_VERSION=0.7.0-r1
docker pull unclecode/crawl4ai:$CRAWL4AI_VERSION
```

1. Run Docker container:
```bash
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:$CRAWL4AI_VERSION
```

2. Find Starlette installation:
```bash
docker exec crawl4ai python -c "import starlette; print(starlette.__file__)"
# /usr/local/lib/python3.12/site-packages/starlette/__init__.py
```

3. Change file permissions (from host):
```bash
CONTAINER_ID=$(docker ps | grep $CRAWL4AI_VERSION | awk '{print $1}')
echo $CONTAINER_ID # a7936c5150e1
docker exec -u root $CONTAINER_ID chown -R appuser:appuser /usr/local/lib/python3.12/site-packages/starlette/
docker exec -u root $CONTAINER_ID chown -R appuser:appuser /app/
```

4. Edit `/usr/local/lib/python3.12/site-packages/starlette/middleware/base.py` with Emacs TRAMP:
```
# https://github.com/encode/starlette/pull/2953/files
C-x C-f /docker:CONTAINER_ID:/usr/local/lib/python3.12/site-packages/starlette/middleware/base.py
# Please edit CONTAINER_ID to actual hash
```

5. Add pathsend handling in body_stream() method around line 166:
```python
# https://github.com/encode/starlette/pull/2953/files
if message["type"] == "http.response.start": # Added
    yield message # Added
    continue # Added
if message["type"] == "http.response.pathsend":
    yield message
    break
```

5. Edit `/app/server.py` JSON serialization via TRAMP:
C-x C-f `/docker:42639fc00b91:/app/server.py`
# Please edit CONTAINER_ID to actual hash

Around line 446, replace:
```python
# return JSONResponse(res)
return JSONResponse(res.model_dump() if hasattr(res, 'model_dump') else res.__dict__)
```

5. Edit `/app/config.yaml`
C-x C-f `/docker:42639fc00b91:/app/config.yaml`
# Please edit CONTAINER_ID to actual hash

Around line 6, replace:
```python
# port: 11234
port: 11235
```

6. Run the edited docker

``` bash
docker stop crawl4ai
docker rm crawl4ai
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:$CRAWL4AI_VERSION
```

7. Manually check the docker with `starlette` updated
```bash
curl -s http://127.0.0.1:11234/mcp/sse
curl -s http://localhost:11234/mcp/sse
export WSL_HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
curl -s http://"$WSL_HOST_IP":11234/mcp/sse
```

8. Working with Claude Code

``` bash
# Add Crawl4AI to Claude Code
claude mcp add --transport sse c4ai-sse http://localhost:11235/mcp/sse
claude
/mcp

╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮│ Manage MCP servers                                                                                                ││                                                                                                                   ││ ❯ 1. c4ai-sse  ✔ connected · Enter to view details                                                                ││                                                                                                                   ││ MCP Config locations (by scope):                                                                                  ││  • User config (available in all your projects):                                                                  ││    • /home/ywatanabe/.claude.json                                                                                 ││  • Project config (shared via .mcp.json):                                                                         ││    • /home/ywatanabe/proj/SciTeX-Code/.mcp.json (file does not exist)                                             ││  • Local config (private to you in this project):                                                                 ││    • /home/ywatanabe/.claude.json [project: /home/ywatanabe/proj/SciTeX-Code]                                     ││                                                                                                                   ││ For help configuring MCP servers, see: https://docs.anthropic.com/en/docs/claude-code/mcp                         │
```

# Run the crawl4ai MCP server

``` bash
could you fetch example.com using crawl4ai?
# ● crawl4ai - md (MCP)(url: "https://example.com")
#   ⎿  Error: All connection attempts failed
docker logs crawl4ai --tail 256



it the playground at http://localhost:11235/playground

EOF -->

<!-- EOF -->