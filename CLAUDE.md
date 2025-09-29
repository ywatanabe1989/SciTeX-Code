<!-- ---
!-- Timestamp: 2025-09-21 20:23:43
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->

----------------------------------------
# General Guidelines
----------------------------------------
## Multi Agent System
Work with other agents using the bulletin board: ./project_management/BULLETIN-BOARD.md

## Keep the project clean and tidy
Use `./.dev` directory for your small experiments - You can use the `.dev` directory as you like but I will delete it lator so that do translate once successful results acquired
Comments/memo should be written under `./docs/from_agents/`

## `rm` is not allowed
- rm is not allowed. Use `./docs/to_claude/bin/general/safe_rm.sh` instead
  - `$ safe_rm.sh ./path/to/file.ext` moves `./path/to/file.ext` to `./path/to/.old/file-<timestamp>.ext`
  - `$ safe_rm.sh ./path/to/dir` moves `./path/to/dir` to `./path/to/.old/dir-<timestamp>`

## SciTeX Guidelines
See `./docs/to_claude/guidelines/python/*SCITEX*.md`

## No try-error as much as possible
Do not use `try` and `error` logic as much as possible as it is difficult for me to find problems. At least, warn error messages.

## Working Directory
- Note that you are automatically cd backed to `./` (this project root) by each iteration

## Async functions
- Add `_async` prefix for all async functions to avoid confusion

## Pepper
You can use browser by MCP

## File versioning
When a file needs update, please handle versioning like this:
/path/to/file.py (<- this is only the used script)
/path/to/file_v01-<description>.py
/path/to/file_v02-<description>.py
By following this convention, do not create similar names of files as I cannot understand which files are used in the end.
This convension is good as we do not need to edit related code like import/export statements.
Especially, description would be show problem in the version, like xxx-not-working or yyy-not-implemented.
Since the codebase is not optimized for the config, we need to develop them to accept newly developed config manager
Also, some paths or parameters will be not included in the current config schema. in that case, please ask user how to handle them individually.
I hope this new config system will enhance the codebase to be more consistent and maintainable

## Smaller chunks of functions
I do not like long scripts, functions.
Please organize codebase in appropriate size of scripts, classes, and functions with clean separation of concepts. one chunk of code should have one responsibility.

## Do not use emoji but use scitex.loggingging
Especially success is in green and i can get the large picture from logs they are colored.
Also, do not use emoji as they are not my cup of tea.
The usage would be like:
``` python
from scitex.loggingging import getLoger
logger = getLoger(__name__)
```

## Error/Warning handling
Use `./scitex_repo/src/scitex/errors.py

----------------------------------------
# Browsers
----------------------------------------
## About Crawl4ai MCP Server
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

## Use Puppeteer and Crawl4ai MCP servers
You can work with browsers
When work with browsers, use logs and screenshorts with timestamps. This enables us to review what was happning in a sequential manner and check timing issues.


----------------------------------------
# Project-specific Guidelines
----------------------------------------

----------------------------------------
# Current priority
----------------------------------------
- [ ] Improve scitex.ml.classification modules

<!-- EOF -->