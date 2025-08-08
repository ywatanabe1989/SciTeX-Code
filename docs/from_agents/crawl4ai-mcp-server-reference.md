<!-- ---
!-- Timestamp: 2025-08-06 21:09:00
!-- Author: Claude (Assistant)
!-- File: /home/ywatanabe/proj/SciTeX-Code/docs/from_agents/crawl4ai-mcp-server-reference.md
!-- Purpose: Complete reference guide for Crawl4ai MCP server functionalities
!-- --- -->

# Crawl4ai MCP Server - Complete Reference Guide

## Overview
The Crawl4ai MCP server provides 7 core functionalities for web crawling, content extraction, and browser automation. All functions return structured JSON responses with success indicators and comprehensive metadata.

## 1. Markdown Extraction (`mcp__crawl4ai__md`)

**Purpose**: Convert web pages to clean markdown with content filtering

**Parameters**:
- `url` (required): Absolute HTTP/HTTPS URL to fetch
- `f` (optional): Content filter strategy
  - `"fit"` (default): Optimized content extraction
  - `"raw"`: Raw content without filtering
  - `"bm25"`: BM25-based content filtering
  - `"llm"`: LLM-based content filtering
- `q` (optional): Query string for BM25/LLM filters
- `c` (optional): Cache-bust/revision counter (default: "0")

**Usage Example**:
```python
mcp__crawl4ai__md(
    url="https://example.com",
    f="fit",
    q="main content extraction"
)
```

**Returns**: JSON with `url`, `filter`, `query`, `cache`, `markdown`, `success`

## 2. HTML Preprocessing (`mcp__crawl4ai__html`)

**Purpose**: Get sanitized HTML structure for schema extraction and further processing

**Parameters**:
- `url` (required): URL to process

**Usage Example**:
```python
mcp__crawl4ai__html(url="https://example.com")
```

**Returns**: JSON with `html`, `url`, `success`

## 3. Screenshot Capture (`mcp__crawl4ai__screenshot`)

**Purpose**: Capture full-page PNG screenshots of rendered pages

**Parameters**:
- `url` (required): URL to screenshot
- `output_path` (optional): Path to save screenshot file
- `screenshot_wait_for` (optional): Seconds to wait before capture (default: 2)

**Usage Example**:
```python
mcp__crawl4ai__screenshot(
    url="https://example.com",
    output_path="/tmp/screenshot.png"
)
```

**Returns**: JSON with `success`, `path`

## 4. PDF Generation (`mcp__crawl4ai__pdf`)

**Purpose**: Generate PDF documents of web pages

**Parameters**:
- `url` (required): URL to convert to PDF
- `output_path` (optional): Path to save PDF file

**Usage Example**:
```python
mcp__crawl4ai__pdf(
    url="https://example.com",
    output_path="/tmp/document.pdf"
)
```

**Returns**: JSON with `success`, `path`

## 5. JavaScript Execution (`mcp__crawl4ai__execute_js`)

**Purpose**: Execute custom JavaScript snippets in browser context and get comprehensive crawl results

**Parameters**:
- `url` (required): URL to load and execute scripts on
- `scripts` (required): Array of JavaScript snippets to execute sequentially

**Usage Example**:
```python
mcp__crawl4ai__execute_js(
    url="https://example.com",
    scripts=[
        "document.title",
        "document.querySelectorAll('p').length",
        "window.location.href"
    ]
)
```

**Returns**: Complete CrawlResult JSON including:
- `url`, `html`, `success`, `cleaned_html`
- `media`, `links`, `metadata`
- `js_execution_result` with script results
- `response_headers`, `status_code`
- `markdown` with multiple format variants
- Performance and network data

## 6. Multi-URL Crawling (`mcp__crawl4ai__crawl`)

**Purpose**: Process multiple URLs simultaneously with performance metrics

**Parameters**:
- `urls` (required): Array of URLs to crawl (1-100 URLs)
- `browser_config` (optional): Browser configuration object
- `crawler_config` (optional): Crawler configuration object

**Usage Example**:
```python
mcp__crawl4ai__crawl(
    urls=["https://example.com", "https://httpbin.org/json"]
)
```

**Returns**: JSON with:
- `success`: Overall operation status
- `results`: Array of complete CrawlResult objects for each URL
- `server_processing_time_s`: Performance metrics
- `server_memory_delta_mb`: Memory usage stats

## 7. Documentation/Context Query (`mcp__crawl4ai__ask`)

**Purpose**: Search Crawl4ai documentation and context using BM25 filtering

**Parameters**:
- `context_type` (optional): Type of context to search
  - `"doc"`: Documentation context
  - `"code"`: Code context  
  - `"all"`: Both documentation and code
- `query` (recommended): Search query to filter results
- `score_ratio` (optional): Minimum score fraction for filtering
- `max_results` (optional): Maximum results to return (default: 20)

**Usage Example**:
```python
mcp__crawl4ai__ask(
    context_type="doc",
    query="markdown extraction",
    max_results=5
)
```

**Returns**: JSON string with `doc_results` and/or `code_results` arrays containing relevant documentation snippets with scores

## Common Response Structure

All functions return structured responses with:
- `success`: Boolean indicating operation success
- Function-specific data (markdown, html, path, results, etc.)
- Error handling with descriptive messages
- Metadata including response headers, status codes, processing times

## Error Handling

- Invalid URLs return error responses
- Large responses (>25000 tokens) are automatically truncated
- Network issues and timeouts are handled gracefully
- All errors include descriptive messages for debugging

## Best Practices

1. **URL Validation**: Always use absolute HTTP/HTTPS URLs
2. **Output Paths**: Use `/tmp/` for temporary files or specify full paths
3. **Content Filtering**: Use `"fit"` filter for most content extraction needs
4. **Batch Processing**: Use `crawl` for multiple URLs to benefit from parallel processing
5. **Query Filtering**: Always provide queries for `ask` function to get relevant results
6. **Error Checking**: Always check `success` field before processing results

## Integration with SciTeX Scholar Module

This MCP server is particularly useful for:
- **PDF Discovery**: Extract download links from publisher pages
- **Metadata Extraction**: Get structured data from academic paper pages  
- **Authentication Handling**: Screenshot and verify login flows
- **Content Validation**: Verify downloaded PDFs contain expected content
- **Batch Processing**: Handle multiple DOIs/URLs efficiently

<!-- EOF -->