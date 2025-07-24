<!-- ---
!-- Timestamp: 2025-07-25 01:58:33
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
The scholar module should be developed
- [x] OpenAthens Authentication investigated - technically works but not being used effectively
  - Papers download via "Playwright" or "Direct patterns" instead
  - See: ./docs/from_agents/openathens_status_and_lean_library_recommendation.md
- [x] Implement Lean Library integration as primary institutional access method
  - Browser extension provides better UX than OpenAthens
  - Already created: _LeanLibraryAuthenticator.py
  - ✅ Integrated into PDFDownloader as primary strategy
  - ✅ Added to ScholarConfig with use_lean_library option
  - ✅ Updated documentation and created setup guide
  - ✅ Ready for use - requires browser extension installation
  - ✅ Fixed missing config attributes and basic test failures
  - Status: 71% tests passing, core functionality working

<!-- EOF -->