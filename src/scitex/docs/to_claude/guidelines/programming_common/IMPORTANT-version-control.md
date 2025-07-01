<!-- ---
!-- Timestamp: 2025-05-30 15:07:57
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/programming_common/IMPORTANT-version-control.md
!-- --- -->

## Test-Driven Development
ANY COMMIT MUST BE ASSOCIATED WITH THE LATEST TESTING REPORT
This ensures the quality of the commited contents

## Git/GitHub Availability
- `git` and `gh` commands available
- SSH public key is registered in GitHub account `ywatanabe1989`
- `git push` to `origin/main` is not accepted

## Our Version Control Workflow

### Standard Workflow (Single Working Directory)
01. Using `git status`, `git log`, `git stash list`, and so on, understand our step in the workflow
02. Start from `develop` branch
03. Checkout to `feature/<verb>-<object>`
04. Confirmed `feature/<verb>-<object>` is correctly implemented
05. Once the feature implementation is verified using tests, merge back `feature/<verb>-<object>`into `develop`
06. Once `feature/<verb>-<object>` branch merged correctly without any problems, delete `feature/<verb>-<object>` branch for cleanliness
07. Push to origin/develop
08. For important update, create PR with auto merging from `origin/develop` to `origin/main`
09. Once PR merged, udpate local `main`
10. Add tag based on the previous tags conventions
11. Add release using the tag with descriptive messages
12. Don't forget to switch back to `develop` branch locally

### Worktree for Claude
Claude MUST work on a dedicated worktree, with the path of which under `.claude-worktree` like this:
  - Repository Root for the User: `/path/to/project-parent/project-name`
  - Working tree for Claude: `/path/to/project-parent/.claude-worktree/project-name`

Exception:
  - If Claude is NOT IN A CLAUDE-DEDICATED WORKTREE, ask the user whether to work there:
    ```plaintext
    1: Work this directory `/path/to/project-parent/project-name`
    2: Create claude-dedicated worktree (`/path/to/project-parent/.claude-worktree/project-name`)?
    ```
  - 1 is the default
  - If user selects `1`, keep working there without hesitation.
  - If user selects `2`,
    - Claude do:
      - `mkdir -p /path/to/project-parent/.claude-worktree/project-name`
      - `git worktree add -b claude-develop /path/to/project-parent/.claude-worktree/project-name`
      - Instruct the user to:
        1. Stop the current session
        2. Change Directory to:
           `/path/to/project-parent/.claude-worktree/project-name`
        3. Prepare an environment 
           `python -v venv .env && source .env/bin/activate && uv pip install -e .`
        4. Start new Claude session there.

## Merge Rules
When conflicts found, check if they are minor problems. If it is a tiny problem solve it immediately. Otherwise, let's work on in a safe, dedicated manner

## Before Git Handling
Let me know your opinion, available plans (e.g., Plan A, Plan B, and Plan C), and reasons in the order of your recommendation
Once agreed plans determined, process git commands baesd on the agreements

## Rollback
If the project gets stacked or going not well. Roll back to the recent stable commit.

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->