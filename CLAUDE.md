<!-- ---
!-- Timestamp: 2025-08-05 04:06:48
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/CLAUDE.md
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

----------------------------------------
# Project-specific Guidelines
----------------------------------------

## Error/Warning handling
Use `./scitex_repo/src/scitex/errors.py

----------------------------------------
# Current priority
----------------------------------------
## Develop Scholar module
Now we are facing challenges with automating literature search, which is one of the modules for automatic scientific research project, SciTeX (https://scitex.ai).

Scholar related temporal files, including auth cookies and cache files, should be placed under `~/.scitex/scholar` (= "$SCITEX_DIR/scholar")

--- WE NEED TO HANDLE NEWLY IMPLEMENTED CONFIG LOGIC THROUGHOUT THE CODEBASE.SO, PLEASE CHECK ONE BY ONE. ESPECIALLY EACHFILE SHOULD HAVE MAIN TO CHECK EASILY ---

Planned workflow is:
1. Manual Login to OpenAthens (Unimelb)
   - `scitex.scholar.auth`
   - `python -m scitex.scholar.authenticate openathens`

2. Keep the authentication info to cookies
   - `scitex.scholar.auth`
   - [ ] Cookie is stored at: `` (find the actual json file here)
   - [ ] Especially, in the cookifile, which entry is important?

3. Use AI2 products to get related articles as bib file
   - e.g., `./src/scitex/scholar/docs/papers.bib`

4. Resolve DOIs from piece of information such as title in a resumable manner
   - `python -m scitex.scholar.resolve_dois --title ...`
   - `python -m scitex.scholar.resolve_dois --bibtex /path/to/bibtex-file.bib`
   - `python -m scitex.scholar.resolve_dois --bibtex src/scitex/scholar/docs/papers.bib --resume`
     - I think this should be more intuitively work for resumablly
   - Resume to handle rate limit
   - Progress and ETA should be shown like rsync
   - Performance enhancement by reducing overlaps, optimizing retry logics
     - [ ] All the 75 entires are resolved their dois

5. Resolve publisher url using OpenURL for OpenAthens (Unimelb) in a resumable manner
   - `scitex.scholar.open_url.OpenURLResolver`
   - We wanted to use ZenRows but it seems difficult to pass auth info to remote browsers
   - For local version, it seems ZenRows functionality like stealth access are limited
   - Progress and ETA should be shown like rsync

### !!! IMPORTANT: Maybe this step is not fully incorporated yet!!!
6. Enrich the bib file to add metadata in a resumable manner
   - `python -m scitex.scholar.enrich_bibtex /path/to/bibtex-file.bib`
   - `scitex.scholar.Papers.from_bibtex`
   - `scitex.scholar.enrich_bibtex`
   - `/path/to/.tmp-bibtex-file.bib` would be intuitive
   - [ ] Enriching metadata using google scholar and crawl4ai might be also another method
   - Progress and ETA should be shown like rsync
   - [ ] `./src/scitex/scholar/docs/papers-enriched.bib`
   - [ ] `./src/scitex/scholar/docs/papers-enriched.csv`
     - [ ] All the 75 entires are enriched
   - All metadata should have their source explicitly in the bib files
     - `title` should have `title_source` as well
     - In the same way, `xxxx` should have `xxxx_source` all the time

### YES, now this step, the largest challenge, is handled well !!!
7. Download PDFs using AI agents (you, Claude) in an exploratory manner
   - Claude Code
   - Cookie acceptance
   - Captcha handling
   - Zotero translators
   - Store pdfs in this format: `FIRSTAUTHOR-YEAR-JOURNAL.pdf`
   - Headless mode and screencaptures will be better to avoid interferences
   - Skip unsolvable problems and work on other entries, while escalating to the user
     - [ ] PDF files for all the 75 entries are downloaded
     - [ ] Open undownloaded papers urls (dois) as tabs on a browser will be beneficial for user to download using zotero connector

# this is not implemented yet
8. Confirm downloaded PDFs are the main contents
   - Extract sections

# Now this is implemented
9. Organize everything in a database

   ```
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/<original-name-from-the-journal>.pdf
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/attachments/<original-name-from-the-journal>.pdf
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/attachments/<original-name-from-the-journal>.pdf
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/metadata.json
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/screenshots/<timestamp>-description.jpg
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/screenshots/<timestamp>-description.jpg   
   ~/.scitex/scholar/library/<project-human-readable>/AUTHOR-YEAR-JOURNAL -> .../8-DIGITS-ID
   ```

   

10. Allow for semantic vector search

Environment variables are available at:
`/home/ywatanabe/.dotfiles/.bash.d/secrets/000_ENV_UNIMELB.src`
`/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src`

Python env is in the current directory. Do not change directory as bash handles python environments based on working directory.

## Browser extentions
- [Lean Library](https://chromewebstore.google.com/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa?hl=en)
- [Zotero Connector](https://chromewebstore.google.com/detail/zotero-connector/ekhagklcjbdpajgpjgmbionohlpdbjgc?hl=en)
- [Accept all cookies](https://chromewebstore.google.com/detail/accept-all-cookies/ofpnikijgfhlmmjlpkfaifhhdonchhoi?hl=en)
- [Captcha Solver](https://chromewebstore.google.com/detail/captcha-solver-auto-recog/ifibfemgeogfhoebkmokieepdoobkbpo?hl=en)
  - $SCITEX_SCHOLAR_2CAPTCHA_API_KEY


## About Crawl4ai MCP Server (Now, it seems not working)
   - Crawl4ai MCP server
     - # Pull and run the latest release candidate
     <!-- - # Latest version of Crawl4ai MCP server does not work
      !-- - docker pull unclecode/crawl4ai:latest
      !-- - docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
      !-- - docker rm -f crawl4ai -->
     - docker pull unclecode/crawl4ai:0.6.0rc1-r2
     - docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:0.6.0rc1-r2
 │   - docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g --user "$(id -u):$(id -g)" -v                        │
     - Visit the playground at http://localhost:11235/playground

● The c4ai-sse MCP server is working - it's responding to HTTP requests.
  The issue might be with how the MCP client is configured to connect to
  it. Since you're running the crawl4ai Docker container on Windows and
  accessing it from WSL2, the MCP configuration might need to use the
  Windows host IP (10.255.255.254) instead of localhost.

  The server is accessible at http://localhost:11235 from WSL2, so it's not
   a networking issue between WSL2 and Windows.
  
  NOTE: The crawl4ai container uses port 11235 (not 11234 as sometimes 
  reported in GitHub issues). Verified with: docker ps | grep crawl4ai
  
  Maybe it should be http://127.0.0.1:11235 from wsl2 or we need to explicitly resolve windows ip

Expert software engineer that helps review my code based on best practices
Expert software engineer that monitor codebase not to introduce regressions
Expert software engineer that solves path management from newly introduced config manager


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

## Do not use emoji but use scitex.logging
Especially success is in green and i can get the large picture from logs they are colored.
Also, do not use emoji as they are not my cup of tea.
The usage would be like:
``` python
from scitex.logging import getLoger
logger = getLoger(__name__)
```

## Use Puppeteer and Crawl4ai MCP servers
You can work with browsers
When work with browsers, use logs and screenshorts with timestamps. This enables us to review what was happning in a sequential manner and check timing issues.

## PDF download workflow
BrowserManager + Authenticator + Chrome extensions (stealth + auth info))
-> Part of metadata such as title
-> DOI 
-> OpenURL
-> Final URL
-> Find PDF URLS using zetero translators
-> Download PDFs
-> Organize PDFs based on expected structure

## PDF downloaders
Which downloaders should we keep...? ~/proj/scitex_repo/src/scitex/scholar/download/
We need cleanup using safe_rm.sh

## No need metadata
we do not need journal_rank and h_index

## Resolve circular dependency and organize SoC
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_BrowserAuthenticator.py`
  - This should be not specific to unimelb
  - We need to map library authenticators and sso (openathens -> unimelb)
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/sso_automations/_UniversityOfMelbourneSSOAutomator.py`
  - The issue was importing `UniversityOfMelbourneSSOAutomator` which creates a circular dependency since that class imports `BrowserAuthenticator`.
  - This should handle unimelb-specific logics


## DOI resolver
- [x] All info should be saved to library as json file
- [x] All info shoudl be associated with source all the time
- [x] If one field is already filled, no need to override, just skip that field, assuming once entered info is correct 
- [x] How project name, like pac, specified?
  - [x] Is it possible to copy bibtex file when dois are resolved from_bibtex?
  - [x] Is it possible to prepare a summary table to show the results of from_bibtex?
  - [x] For exmaple, ~/.scitex/scholar/library/pac/info/files-bib/summary.csv
  - [x] For exmaple, ~/.scitex/scholar/library/pac/info/filesname-2-bib/summary.csv

## Technical Debt - Storage Architecture
**Issue**: Current storage structure mixes master storage with project directories
**Current (Working but Suboptimal)**:
```
~/.scitex/scholar/library/
├── master/8DIGIT01/  # ✓ Correct
├── project/
│   ├── 8DIGIT02/     # ❌ Should be symlink to master
│   ├── Author-Year -> ../master/8DIGIT03  # ❌ Human-readable not needed
│   └── info/files-bib/  # ❌ Should be info/filename/filename.bib
```

**Desired Architecture**:
```
~/.scitex/scholar/library/
├── master/8DIGIT01/  # All actual data storage
├── project/
│   ├── info/filename/filename.bib  # Project metadata
│   ├── 8DIGIT01 -> ../master/8DIGIT01  # Direct symlinks only
│   └── 8DIGIT02 -> ../master/8DIGIT02
```

**Decision**: Keep current working system, refactor later when time permits
**Priority**: Low (system works correctly, just suboptimal structure)

## Metadata Enrichment
- [ ] Once DOI is resolved, next process is metadata enrichment. Especially:
  - [ ] abstract
  - [ ] citation count
  - [ ] journal impact factor


It would be better to connect journal titles in symlinks with hypehen
e.g. NOT: Journal of Neuroscience, Good: Journal-of-Neuroscience

<!-- EOF -->