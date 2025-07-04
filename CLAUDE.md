<!-- ---
!-- Timestamp: 2025-07-04 21:14:07
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->

## Multi Agent System
Working with other agents using the bulletin board: ./project_management/BULLETIN-BOARD.md

## MNGS is obsolete
We have renamed mngs to scitex. Use scitex all the time.

## No try-error as much as possible
Please do not use try-error as much as possible as it is difficult for me to find problems. At least, warn error messages.

## Python Env
Python env is ./.env
All codes are expected run from the root of this repository `.`
When cd to different location, it is automatically deactivated.

## Priority
The higher the priority is, the more important, prioritized they should be

## Jupyter Notebooks as examples (priority 10)
- [ ] Examples should be as much simple as possible
- [ ] Do not create variants of files with suffixes
  - [ ] We no need _executed.ipynb
  - [ ] Just run all the cells from scratch in the order
  - [ ] No need .back.ipynb as well
- [ ] Run the example notebooks in ./examples/
- [ ] No print needed. As scitex is designed to print necessary outputs automatically

## Allow me to create read the docs (priority 1)
- [x] Host in Read the Docs
  - Configuration complete: .readthedocs.yaml, docs/RTD/ structure
  - Status report: ./project_management/rtd_setup_status_20250704.md
  - Ready for deployment at readthedocs.org
  - Next: Import project on RTD website
- [ ] Host in https://scitex.ai (our django app)
  - Guide created: ./project_management/django_hosting_guide_20250704.md
  - Recommended: Static files approach (Option 1)
  - Next: Implement in Django project

## For circular importing issues (priority 1)
- [x] Check importing orders
  - Tested all 29 modules - no circular imports found
  - Report: ./project_management/circular_import_check_20250704.md
- [x] Import modules in functions (lazy import)
  - Already implemented via _LazyModule class in __init__.py
  - All modules use lazy loading successfully

## GitHub Actions (priority 1)
- [x] Error raised persistently
  - [x] Identify the causes by checking GitHub logs
    - Documentation path issues (docs/requirements.txt → docs/RTD/requirements.txt)
    - Flake8 scanning .old directories
    - Report: ./project_management/github_actions_analysis_20250704.md
  - [x] Fix the issues
    - Updated ci.yml with correct paths
    - Created .flake8 configuration
    - Report: ./project_management/github_actions_fixes_20250704.md

<!-- EOF -->