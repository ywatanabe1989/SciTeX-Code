<!-- ---
!-- Timestamp: 2025-05-30 04:47:50
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/IMPORTANT-MNGS-01-basic.md
!-- --- -->

# MNGS Basic Guidelines

**!!! IMPORATANT !!!**
**ANY PYTHON SCRIPTS MUST BE WRITTEN IN THE MNGS FORMAT EXPLAINED BELOW.**
THE EXCEPTIONS ARE:
    - Pacakges authored by others
    - Source (`./src` and `./tests`) of pip packages to reduce dependency
IN OTHER WORDS, IN ANY PYTHON PROJECT, MNGS MUST BE USED AT LEAST IN:
- `./scripts`
- `./examples`

## Feature Request
When MNGS does not work, create a bug-report under `~/proj/mngs_repo/project_management/bug-reports/bug-report-<title>.md`, just like creating an issue ticket on GitHub

## What is MNGS?
- `mngs` is:
    - A Python utility package
    - Designed to standardize scientific analyses and applications
    - Maintained by the user and installed via editable mode.
    - The acronym of "monogusa", meaning "lazy" in Japanese
    - Located in `~/proj/mngs_repo/src/mngs`
    - Remote repository: `git@github.com:ywatanabe1989:mngs`
    - Installed via pip in development mode: `pip install -e ~/proj/mngs_repo`
- `mngs` MUST BE:
    - MAINTAINED AND UPDATED REGULARLY

## Bug Report
- Create a bug report when you encountered mngs-related problems
- The bug reprot should be written as a markdown file in the mngs local repository like on GitHub Issues
  `~/proj/mngs_repo/project_management/bug-report-<title>.md`
  - Follow the `./docs/to_claude/guidelines/guidelines-programming-Bug-Report-Rules.md`

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->