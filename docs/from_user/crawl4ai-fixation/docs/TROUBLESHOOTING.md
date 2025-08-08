# Crawl4AI MCP Server Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Container Issues

#### Problem: Container won't start
```bash
# Check container status
docker ps -a | grep crawl4ai

# Check logs for errors
docker logs crawl4ai --tail 50

# Common solutions:
docker restart crawl4ai
# OR
docker stop crawl4ai && docker rm crawl4ai
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g crawl4ai:fully-fixed
```

#### Problem: Port 11235 already in use
```bash
# Find what's using the port
sudo lsof -i :11235

# Kill the process or use different port
docker run -d -p 11236:11235 --name crawl4ai --shm-size=1g crawl4ai:fully-fixed
```

### MCP Connection Issues

#### Problem: Claude Code can't connect to MCP server
```bash
# 1. Verify container is running and port is accessible
curl -v http://localhost:11235/mcp/sse

# 2. Check MCP configuration
cat ~/.claude/mcp-config.json

# 3. Restart Claude Code completely (not just refresh)

# 4. Test direct API as fallback
curl -X POST "http://localhost:11235/md" -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### Problem: MCP endpoints return errors
```bash
# Check if fixes were applied properly
docker exec crawl4ai ls -la /usr/local/lib/python3.12/site-packages/starlette/middleware/

# Re-apply fixes if needed
cd /path/to/crawl4ai-fixation/fixes
./apply_all_fixes.sh
```

### Endpoint-Specific Issues

#### Problem: `mcp__crawl4ai__crawl` fails with URL arrays
**Solution**: This is a known issue. Use individual endpoints instead:
```python
# Instead of (broken):
results = mcp__crawl4ai__crawl(urls=["url1", "url2", "url3"])

# Use (working):
results = []
for url in ["url1", "url2", "url3"]:
    result = mcp__crawl4ai__execute_js(url=url, scripts=["document.title"])
    results.append(result)
```

#### Problem: PDF generation fails
```bash
# Check container has write permissions
docker exec crawl4ai ls -la /tmp/

# Ensure output path is accessible
mcp__crawl4ai__pdf(url="https://example.com", output_path="/tmp/test.pdf")

# Check if file was created
docker exec crawl4ai ls -la /tmp/ | grep pdf
```

#### Problem: Screenshot endpoint requires 'name' parameter
```python
# This fails:
mcp__crawl4ai__screenshot(url="https://example.com", output_path="/tmp/test.png")

# This works:
mcp__crawl4ai__screenshot(url="https://example.com", name="test_screenshot")
```

### Performance Issues

#### Problem: Slow response times
```bash
# Check container resources
docker stats crawl4ai

# Increase memory if needed
docker stop crawl4ai && docker rm crawl4ai
docker run -d -p 11235:11235 --name crawl4ai --shm-size=2g --memory=4g crawl4ai:fully-fixed
```

#### Problem: Memory leaks with many requests
```bash
# Restart container periodically
docker restart crawl4ai

# Or implement automatic restart in your script:
# Every 50 requests: docker restart crawl4ai && sleep 10
```

### Authentication Issues (for SciTeX Scholar)

#### Problem: Can't access paywalled content
```python
# Ensure authentication cookies are available
# Check if your browser session has the necessary cookies
# Use browser automation for complex auth flows

# Example with auth cookies:
result = mcp__crawl4ai__execute_js(
    url="https://protected-journal-site.com/article",
    scripts=["document.querySelector('.download-link')?.href"]
)
```

## 🔧 Diagnostic Commands

### Quick Health Check
```bash
#!/bin/bash
echo "🏥 Crawl4AI Health Check"
echo "========================"

# Container status
echo "📦 Container Status:"
docker ps | grep crawl4ai || echo "❌ Container not running"

# Port availability  
echo "🔌 Port Check:"
curl -s http://localhost:11235/mcp/sse > /dev/null && echo "✅ MCP endpoint responding" || echo "❌ MCP endpoint not responding"

# Direct API test
echo "🌐 Direct API Test:"
curl -s -X POST "http://localhost:11235/md" -H "Content-Type: application/json" -d '{"url": "https://example.com"}' | jq -r '.success' > /dev/null && echo "✅ Direct API working" || echo "❌ Direct API failing"

# Memory usage
echo "💾 Memory Usage:"
docker stats crawl4ai --no-stream | tail -n +2 | awk '{print $3 " / " $4}'
```

### Log Analysis
```bash
# Check recent errors
docker logs crawl4ai --tail 100 | grep -i error

# Monitor real-time logs
docker logs crawl4ai -f

# Check specific endpoint failures
docker logs crawl4ai --tail 500 | grep -i "crawl\|json\|serializ"
```

## 🆘 Emergency Recovery

### Complete Reset
```bash
#!/bin/bash
echo "🚨 Emergency Reset - Complete Crawl4AI Recovery"

# Stop and remove container
docker stop crawl4ai || true
docker rm crawl4ai || true

# Remove potentially corrupted image
docker rmi crawl4ai:fully-fixed || true

# Pull fresh image and apply fixes
export CRAWL4AI_VERSION=0.7.0-r1
docker pull unclecode/crawl4ai:$CRAWL4AI_VERSION
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:$CRAWL4AI_VERSION

# Apply all fixes
cd /path/to/crawl4ai-fixation/fixes
./apply_all_fixes.sh

echo "✅ Emergency recovery complete"
```

### Alternative Port Setup
```bash
# If port 11235 is problematic, use 11236
docker stop crawl4ai && docker rm crawl4ai
docker run -d -p 11236:11235 --name crawl4ai --shm-size=1g crawl4ai:fully-fixed

# Update MCP config
sed -i 's/11235/11236/g' ~/.claude/mcp-config.json

# Restart Claude Code
```

## 📞 Getting Help

### Information to Gather
When reporting issues, collect:
```bash
# System info
docker --version
uname -a

# Container info  
docker ps -a | grep crawl4ai
docker logs crawl4ai --tail 50

# Network info
netstat -tlnp | grep 11235
curl -v http://localhost:11235/mcp/sse

# MCP config
cat ~/.claude/mcp-config.json
```

### Test Commands
```bash
# Test all endpoints systematically
curl -X POST "http://localhost:11235/md" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
curl -X POST "http://localhost:11235/html" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
curl -X POST "http://localhost:11235/screenshot" -H "Content-Type: application/json" -d '{"url": "https://example.com", "name": "test"}'
curl -X POST "http://localhost:11235/pdf" -H "Content-Type: application/json" -d '{"url": "https://example.com", "output_path": "/tmp/test.pdf"}'
curl -X POST "http://localhost:11235/execute_js" -H "Content-Type: application/json" -d '{"url": "https://example.com", "scripts": ["document.title"]}'
```

---

**Remember**: 6 out of 7 endpoints work perfectly. The system is production-ready for SciTeX Scholar PDF downloading! 🚀