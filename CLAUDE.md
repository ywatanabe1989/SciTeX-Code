<!-- ---
!-- Timestamp: 2025-07-02 02:37:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->

## Scholar Migration ✅ COMPLETED (2025-07-02)
- [x] Naming convensions for scitex as in other modules ./src/scitex/* should be applied to newly migrated ./src/scitex/scholar module as well
- [x] scitex_repo is just a symlink to SciTeX-Code:
  - [x] /home/ywatanabe/proj/scitex_repo -> /home/ywatanabe/proj/SciTeX-Code
- [x] Implement tests for the migrated scholar module as a scitex pip package
- [x] Implement examples for the migrated scholar module as a scitex pip package
  - [x] Also implement examples in jupyter notebooks (although i am not sure about it, it may be useful when rendered in github)
- [x] NEVER USE DEMO OR FAKE DATA FOR ENSURING CREDIBILITY

## Current Priority: MCP Translation Servers
Current top-most priority lies in MCP translation/reverse-translation servers construction.

See ./docs/to_claude/guidelines/python/*SCITEX*.md
See ./docs/from_user/scitex_translation_mcp_servers.md

## Multi Agent System
Working with other agents using the bulletin board: ./project_management/BULLETIN-BOARD.md

## MNGS is obsolete
We have renamed mngs to scitex. Use scitex all the time.

## No try-error as much as possible
Please do not use try-error as much as possible as it is difficult for me to find problems. At least, warn error messages.

<!-- EOF -->