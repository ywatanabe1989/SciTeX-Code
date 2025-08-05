<!-- ---
!-- Timestamp: 2025-08-03 19:55:02
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/utils/CHROME_EXTENSIONS/PROFILE_NAMES.md
!-- --- -->

1. scholar_auth - Authentication & Manual Tasks
- Purpose: Manual login (OpenAthens, institutional access)
- Mode: Visible, human-controlled
- Extensions: Lean Library, Accept Cookies, Zotero Connector
- Use: Steps 1-2 (authentication, cookie storage)

2. scholar_extensions - Extension-Based Workflows
- Purpose: Workflows requiring extensions (PDF discovery, metadata)
- Mode: Visible but automated
- Extensions: All Scholar extensions (Lean Library, Zotero, Captcha solvers)
- Use: Steps 6-7 (enrichment, some PDF download_asyncs)

3. scholar_stealth - Automated Scraping
- Purpose: Headless automation, rate-limited tasks
- Mode: Invisible, stealth features
- Extensions: Minimal (may conflict with stealth)
- Use: Steps 4-5 (DOI resolution, OpenURL resolution)

4. scholar_debug - Development & Troubleshooting
- Purpose: Testing, screenshots, problem diagnosis
- Mode: Visible, full logging
- Extensions: All extensions + dev tools
- Use: All steps (for debugging)

Why This Separation:

- Extensions vs Automation: Chrome Web Store restrictions make extensions unreliable in fully automated
contexts
- Stealth vs Extensions: Stealth features often conflict with extension functionality
- Auth vs Automation: Authentication requires human interaction but automation needs to be headless
- Context Switching: Different tasks need different browser capabilities

<!-- EOF -->