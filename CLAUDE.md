<!-- ---
!-- Timestamp: 2025-08-01 21:15:10
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
## Develop Scholar module
Now we are facing challenges with automating literature search, which is one of the modules for automatic scientific research project, SciTeX (https://scitex.ai).

Scholar related temporal files, including auth cookies and cache files, should be placed under `~/.scitex/scholar` (= "$SCITEX_DIR/scholar")

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

### !!! IMPORTANT: THIS IS THE MOST CRITICAL TASK NOW!!!
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

8. Confirm downloaded PDFs are the main contents
   - Extract sections

9. Organize everything in a database

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

<!-- EOF -->