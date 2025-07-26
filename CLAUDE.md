<!-- ---
!-- Timestamp: 2025-07-26 14:04:43
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


## Reorganize the Scholar module
Of course. I can certainly adapt the proposed structure to follow your specific naming conventions. Your rules provide a clear, consistent way to distinguish between files based on their primary content (classes vs. functions) and their role (abstract vs. concrete).

Here is the revised project structure that incorporates your rules.

Revised Project Structure
This structure maintains the feature-based grouping while adhering to your filename conventions (_ClassName.py, _function_name.py, _BaseXXX.py).

Plaintext

src/scitex/scholar/
├── __init__.py                 # Minimal; exposes the public API from _Scholar.py
├── _Scholar.py                 # Main facade class `Scholar`
├── _Config.py                  # Class `ScholarConfig`
├── _Paper.py                   # Class `Paper`
├── _Papers.py                  # Class `Papers`
├── _exceptions.py              # Custom Exception classes for the module
│
├── auth/                       # Handles all authentication logic
│   ├── __init__.py
│   ├── _BaseAuthenticationProvider.py # ABC: `BaseAuthenticationProvider`
│   ├── _AuthenticationManager.py      # Class: `AuthenticationManager`
│   ├── _OpenAthensAuthentication.py   # Class: `OpenAthensAuthentication`
│   └── _LeanLibraryAuthentication.py  # Class: `LeanLibraryAuthentication`
│
├── download/                   # Handles all PDF downloading logic
│   ├── __init__.py
│   ├── _PDFDownloader.py             # Main `PDFDownloader` class
│   ├── _BaseDownloadStrategy.py      # ABC: `BaseDownloadStrategy`
│   ├── _DirectDownloadStrategy.py    # Strategy for direct HTTP downloads
│   ├── _SciHubDownloadStrategy.py    # Strategy for Sci-Hub
│   └── _BrowserDownloadStrategy.py   # Strategy for browser automation
│
├── search/                     # Handles searching from all sources
│   ├── __init__.py
│   ├── _UnifiedSearcher.py           # Class `UnifiedSearcher`
│   ├── _BaseSearchEngine.py          # ABC: `BaseSearchEngine`
│   ├── _PubMedEngine.py              # Class `PubMedEngine`
│   ├── _SemanticScholarEngine.py     # Class `SemanticScholarEngine`
│   └── _ArxivEngine.py               # Class `ArxivEngine`
│
├── core/                       # Core internal components and business logic
│   ├── __init__.py
│   ├── _MetadataEnricher.py          # Class `MetadataEnricher`
│   ├── _PDFParser.py                 # Class `PDFParser`
│   ├── _DOIResolver.py               # Class `DOIResolver`
│   └── _OpenURLResolver.py           # Class `OpenURLResolver`
│
└── utils/                      # Utility functions
    ├── __init__.py
    ├── _formatters.py                # Functions like `_papers_to_bibtex`
    └── _ethical_usage.py             # Functions related to ethical notices
How the Rules Were Applied
Prefix _: All Python source files (except __init__.py) are prefixed with an underscore to mark them as internal components of the scholar package.

_ClassName.py Convention:

The main Scholar facade is in _Scholar.py.

Core models Paper and Papers are now in separate files, _Paper.py and _Papers.py, as per your example.

Each specific implementation of an authenticator, download strategy, or search engine gets its own _ClassName.py file (e.g., _PubMedEngine.py).

Manager classes like _AuthenticationManager.py and _UnifiedSearcher.py also follow this convention.

_BaseXXX.py for Abstract Classes:

The abstract base class for authentication providers now resides in auth/_BaseAuthenticationProvider.py.

The base for search engines is in search/_BaseSearchEngine.py.

The base for download strategies is in download/_BaseDownloadStrategy.py.

_function_name.py Convention:

The utils/ directory now contains files like _formatters.py and _ethical_usage.py, as their primary purpose is to export a collection of related functions, matching your examples.

This revised structure successfully combines the strong separation of concerns from the initial proposal with your desired naming conventions, resulting in a codebase that is both well-organized and internally consistent.

<!-- EOF -->