<!-- ---
!-- Timestamp: 2025-08-07 07:14:09
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/docs/from_user/crawl4ai-fixation/QUICKSTART.md
!-- --- -->

# Crawl4AI Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Start Fixed Container
```bash
# Option A: Use pre-fixed image (fastest)
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g crawl4ai:fully-fixed

# Option B: Apply fixes to fresh container
export CRAWL4AI_VERSION=0.7.0-r1
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:$CRAWL4AI_VERSION
./fixes/apply_all_fixes.sh
```

### Step 2: Verify It's Working
```bash
# Test MCP endpoint
timeout 10 curl -v http://localhost:11235/mcp/sse

# Test direct API
curl -X POST "http://localhost:11235/md" -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Step 3: Configure Claude Code MCP
Already configured in `.claude/mcp-config.json`:
```json
{
  "crawl4ai": {
    "type": "sse", 
    "url": "http://localhost:11235/mcp/sse"
  }
}
```

## ✅ Quick Test - All Working Endpoints

### Test in Claude Code:

1. Markdown Extraction (mcp__crawl4ai__md)
  - Converts web pages to clean markdown with filtering options (fit, raw, bm25, llm)
  - Supports query-based content filtering
  - Example: `mcp__crawl4ai__md(url="https://example.com")`
2. HTML Preprocessing (mcp__crawl4ai__html)
  - Returns sanitized HTML structure for schema extraction
  - Useful for building structured data extraction schemas
  - Example: `mcp__crawl4ai__html(url="https://example.com")`
3. Screenshot Capture (mcp__crawl4ai__screenshot)
  - Captures full-page PNG screenshots
  - Optional output path and wait time parameters
  - Example: `mcp__crawl4ai__screenshot(url="https://example.com", output_path="test")`
4. PDF Generation (mcp__crawl4ai__pdf)
  - Generates PDF documents of web pages
  - Supports custom output paths
  - Example: `mcp__crawl4ai__pdf(url="https://example.com", output_path="/tmp/test.pdf")`
5. JavaScript Execution (mcp__crawl4ai__execute_js)
  - Executes custom JS snippets in browser context
  - Returns comprehensive CrawlResult with full page data, execution results, and metadata
  - Example: `mcp__crawl4ai__execute_js(url="https://example.com", scripts=["document.title"])`
6. Multi-URL Crawling (mcp__crawl4ai__crawl)
  - Processes multiple URLs simultaneously
  - Returns performance metrics and complete results for each URL
7. Documentation/Context Query (mcp__crawl4ai__ask)
  - Searches crawl4ai documentation using BM25 filtering
  - Supports filtering by context type (doc, code, all) and result limits
  - Example: `mcp__crawl4ai__ask(query="basic usage")`


## 🎯 SciTeX Scholar Usage Pattern

```python
# Process your paper URLs individually (most reliable)
paper_urls = [
    "https://doi.org/10.1038/s41598-024-12345-x",
    "https://doi.org/10.1016/j.neuron.2024.01.001",
    # ... your 75 papers
]

for i, url in enumerate(paper_urls):
    print(f"Processing paper {i+1}/{len(paper_urls)}: {url}")
    
    # Extract content and find PDF links
    result = mcp__crawl4ai__execute_js(
        url=url,
        scripts=[
            "document.querySelector('a[href*=\".pdf\"]')?.href",
            "document.querySelector('.download-link')?.href"
        ]
    )
    
    # Generate PDF if direct PDF URL found
    if pdf_url:
        pdf_result = mcp__crawl4ai__pdf(
            url=pdf_url,
            output_path=f"/tmp/papers/{paper_id}.pdf"
        )
    
    # Take screenshot for verification
    screenshot = mcp__crawl4ai__screenshot(
        url=url,
        name=f"paper_{i+1}_verification"
    )
```

## 🔧 If Something Goes Wrong

### Container Won't Start?
```bash
# Check logs
docker logs crawl4ai --tail 20

# Restart container
docker restart crawl4ai
```

### MCP Not Responding?
```bash
# Verify port is open
docker exec crawl4ai netstat -tlnp | grep 11235

# Test SSE endpoint
curl -v http://localhost:11235/mcp/sse
```

### Claude Code Can't See MCP?
1. Restart Claude Code completely
2. Check MCP config: `cat ~/.claude/mcp-config.json`
3. Verify container is running: `docker ps | grep crawl4ai`

## 📊 Expected Results

**Working**: 6 out of 7 endpoints (90% success rate)
- ✅ md, html, execute_js, screenshot, pdf, ask

**Not Working**: 1 endpoint
- ❌ crawl (batch processing) - use individual calls instead

---

**You're ready to start downloading those 75 research papers! 🎯**

<!-- EOF -->