<!-- ---
!-- Timestamp: 2025-07-02 00:25:34
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->


## Scholar Migration (Current Top-Most Priority)
- [x] Migrate ./src/scitex/SciTeX-Scholar to ./src/scitex/scholar
- [x] Backup has been already created as ./src/scitex/scholar_backup
- [x] Naming convensions for scitex as in other modules ./src/scitex/* should be applied to newly migrated ./src/scitex/scholar module as well
- [x] scitex_repo is just a symlink to SciTeX-Code:
  - [x] /home/ywatanabe/proj/scitex_repo -> /home/ywatanabe/proj/SciTeX-Code
- [x] Implement tests for the migrated scholar module as a scitex pip package
- [x] Implement examples for the migrated scholar module as a scitex pip package

## Multi Agent System
Work with other agents using the bulletin board: ./project_management/BULLETIN-BOARD.md

## MNGS is obsolete
We have renamed mngs to scitex. Use scitex all the time.

## No try-error as much as possible
Please do not use try-error as much as possible as it is difficult for me to find problems. At least, warn error messages.

<!-- EOF -->