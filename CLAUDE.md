<!-- ---
!-- Timestamp: 2025-07-12 12:07:40
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->

Working with other agents using the bulletin board.

Current top-most priority lies in scholar module improvement.

See ./docs/to_claude/guidelines/python/*SCITEX*.md

Please do not use try-error as much as possible as it is difficult for me to find problems. At least, warn error messages.

## Working Directory
- Note that you are automatically cd backed to `./` (this project root) by each iteration

## Modularize the db module
- [ ] ./src/scitex/db/_sqlite3
- [ ] ./src/scitex/db/_postgresql
- [ ] Also, check other modules about whether they use old db codes (paths)
- [ ] Also, update examples and tests for the updated db module

## Error/Warning handling
Use ./scitex_repo/src/scitex/errors.py

<!-- EOF -->