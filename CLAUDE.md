<!-- ---
!-- Timestamp: 2025-07-31 00:40:38
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->

----------------------------------------
# General Guidelines
----------------------------------------
## Multi Agent System
Working with other agents using the bulletin board: ./project_management/BULLETIN-BOARD.md

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

----------------------------------------
# Project-specific Guidelines
----------------------------------------

## Error/Warning handling
Use `./scitex_repo/src/scitex/errors.py

----------------------------------------
# Current priority
----------------------------------------
## Scholar module
- [x] auth
- [x] browser
- [x] config (2Captcha integration added)
- [x] _Config.py (2Captcha fields added)
- [x] doi
- [x] download (completed with 2Captcha via ZenRows)
- [x] enrichment
- [x] open_url (ZenRows with 2Captcha support)
- [x] _Paper.py
- [x] _Papers.py
- [x] _Scholar.py
- [x] search
- [x] search_engine
- [x] utils
- [ ] zotero_translators (framework exists, individual translators needed)

<!-- EOF -->