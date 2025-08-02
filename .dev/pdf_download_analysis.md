# PDF Download Analysis

## Current Status
- Total papers: 90 storage directories
- Papers with DOIs: 81 (after resolving 2 more)
- PDFs downloaded: ~16-17 (estimated based on partial runs)

## Why Downloads Are Failing

### 1. Paywall Issues
Most papers are behind publisher paywalls:
- **IEEE**: Shows "Need Full-Text access to IEEE Xplore" 
- **Wiley**: Redirects to Web of Science with captcha
- **Elsevier**: Requires institutional login
- **Springer**: Requires subscription

### 2. Open Access Success
Successfully downloaded from:
- **Frontiers** (10.3389/*): Open access journal
- **PLoS** (10.1371/*): Open access journal
- **bioRxiv/medRxiv** (10.1101/*): Preprint servers
- **eLife**: Open access journal

### 3. Technical Issues
- Some DOIs have version suffixes (e.g., "/v1/review1") that break direct PDF URLs
- Captcha/bot detection on some sites
- Need authentication cookies from institutional login

## Solutions

### 1. OpenAthens Authentication (Priority)
You mentioned OpenAthens login for University of Melbourne. We need to:
1. Use your existing auth cookies
2. Pass them to download requests
3. Handle redirects through institutional proxy

### 2. Manual Download Helper
Create a script that:
1. Opens all paywall papers in browser tabs
2. Lets you use Zotero connector after manual login
3. Organizes downloaded PDFs into correct directories

### 3. Preprint Fallback
Search for preprint versions on:
- arXiv
- bioRxiv/medRxiv  
- ResearchGate
- Author websites

### 4. Use Existing Infrastructure
- Your NAS might have cached PDFs
- Check if Zotero already has some papers
- Use local Crossref dataset when available

## Next Steps
1. Implement OpenAthens cookie authentication
2. Create browser automation for manual downloads
3. Search for open access alternatives
4. Generate report of papers needing manual intervention