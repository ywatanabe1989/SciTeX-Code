<!-- ---
!-- Timestamp: 2025-05-30 01:05:17
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/mngs_repo/.claude/commands/auto.md
!-- --- -->

1. If THIS TIME OF REQUEST below is not empty, just work on the request.
   === THIS TIME OF REQUEST STARTS ===
   $ARGUMENTS
   === THIS TIME OF REQUEST ENDS ===

2. Continue important ongoing work if exists

3. Otherwise, decide most appropriate next step
   - Check user's daily commands:
     - Project: `PROJECT_ROOT/.claude/commands/*.md (priority)`
     - Global: `~/.claude/commands/*.md`
  For example, command files under the global commands directory would be:
    - `advance.md`
    - `auto.md`
    - `bug-report.md`
    - `bug-report-solved.md`
    - `cleanup.md`
    - `communicate.md`
    - `examples.md`
    - `exit.md`
    - `factor-out.md`
    - `feature-request.md`
    - `feature-request-solved.md`
    - `git.md`
    - `mngs.md`
    - `plan.md`
    - `progress.md`
    - `refactor.md`
    - `rename.md`
    - `reports.md`
    - `resolve-conflicts.md`
    - `rollback.md`
    - `tests.md`
    - `timeline.md`
    - `tree.md`
    - `understand-guidelines.md`
    - `update-guidelines.md`
     - 
4. Execute the best choice

<!-- EOF -->