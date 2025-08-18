<!-- ---
!-- Timestamp: 2025-08-18 19:27:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/IMPROVEMENT_SUGGESTIONS.md
!-- --- -->

🚀 1. Improve Robustness & Success Rate
The primary goal is to increase the 88.0% success rate by handling complex publisher sites and institutional resolvers more effectively.

Problem: Failures on Major Publisher Sites (Elsevier/ScienceDirect)
The log shows multiple failures for publishers like Elsevier, where the script lands on an abstract page (/abs/pii/) and the existing patterns fail to find a PDF link.

💡 Suggestion: Enhance Publisher-Specific Scraping Logic
Instead of relying solely on URL transformation patterns, improve the scraping logic within _find_direct_pdf_links in _find_functions.py to actively look for download buttons on the page.

Example for _find_functions.py:

Python

# In _find_direct_pdf_links, expand the downloadSelectors list

const downloadSelectors = [
    // ... existing selectors ...

    // ++ Add Selectors for Major Publishers ++
    // For ScienceDirect (Elsevier)
    'a.PdfLink', // Main PDF link
    'a.article-tools-pdf-link',

    // For Wiley Online Library
    'a#article-pdf-link',
    'a.pdf-download',

    // For SpringerLink
    'a[data-track-action="download pdf"]',
    'a.c-pdf-download__link',

    // For Oxford Academic
    'a.al-link.pdf-link',
];
Problem: Unreliable OpenURL Resolver Navigation
The log shows the script struggling with institutional resolvers (unimelb.hosted.exlibrisgroup.com), encountering consent pages (accounts.ebsco.com), and failing with timeout errors. The current method of clicking the first likely link is brittle.

💡 Suggestion: Improve the Resolver Link Finder
Make the _ResolverLinkFinder.py smarter by adding negative keywords to avoid clicking non-article links. Also, refine the click-and-wait logic to be more adaptive.

Example for _ResolverLinkFinder.py:

Python

# In _find_by_domain, add a filter for negative keywords

# ... inside the loop
for link in all_links:
    href = await link.get_attribute("href") or ""
    text = await link.inner_text() or ""
    text_lower = text.lower()

    # ++ Define words that indicate a non-article link ++
    negative_keywords = ["cookie", "policy", "about us", "privacy", "terms"]

    # ++ Check for negative keywords before returning a link ++
    if any(keyword in text_lower for keyword in negative_keywords):
        logger.debug(f"Skipping non-article link: {text}")
        continue

    # ... rest of the domain matching logic ...
Example for click_and_wait in _ResolverLinkFinder.py:
Instead of fixed timeouts, wait for a navigation event, which is more reliable.

Python

# Replace the waiting logic in click_and_wait
try:
    # Perform the click that should trigger navigation
    async with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
        await link.click()
    
    # Add a small, final wait for any JS-based redirects
    await page.wait_for_timeout(2000)

except Exception as e:
    logger.warning(f"Navigation after click did not complete as expected: {e}")
    # Fallback check if the URL changed without a standard navigation event
    if page.url == initial_url:
        logger.warning("No navigation occurred after click")
        return False
⚡️ 2. Boost Performance
The process can be slow due to creating new browser pages for each task and loading unnecessary web content.

Problem: High Overhead from Creating New Pages
In ScholarURLFinder.py, the find_urls_batch function creates and destroys a new browser page for every single DOI. This is a major performance bottleneck.

💡 Suggestion: Implement Page Re-use (Pooling)
Manage a pool of pre-created pages. Each concurrent task can check out a page, use it to navigate and scrape, and then return it to the pool. This avoids the costly setup/teardown process for each URL.

Conceptual Example in ScholarURLFinder.py:

Python

# In find_urls_batch
from asyncio import Queue

# Create a pool of pages
page_pool = Queue()
for _ in range(max_concurrent):
    page = await self.context.new_page()
    await page_pool.put(page)

async def find_urls_with_pooled_page(doi: str):
    # Get a page from the pool
    page = await page_pool.get()
    try:
        return await self.find_urls(doi=doi, page=page)
    finally:
        # Return the page to the pool for re-use
        await page_pool.put(page)

# ... create and run tasks with find_urls_with_pooled_page
Problem: Loading Unnecessary Resources
Pages are slowed down by loading images, CSS, ads, and tracking scripts, none of which are needed for finding a PDF link.

💡 Suggestion: Block Unnecessary Network Requests
Use Playwright's network request interception to block non-essential resources. This can dramatically speed up page load times.

Example (can be added to your BrowserManager or ScholarURLFinder):

Python

# This function can be called on a new page to set up blocking
async def block_unnecessary_requests(page: Page):
    await page.route("**/*", lambda route: 
        route.abort() 
        if route.request.resource_type in ["image", "stylesheet", "font", "media"]
        else route.continue_()
    )

# In the batch processor, apply this to each page in the pool
# e.g., in find_urls_with_pooled_page
page = await page_pool.get()
await block_unnecessary_requests(page) # Call it once per page
try:
    # ...
🐛 3. Improve Error Handling and Debugging
The logs show cryptic errors like Target page, context or browser has been closed, and debugging screenshots lack context.

Problem: Ambiguous "Page Closed" Errors
This error typically happens in asynchronous code when one part of the program closes a page while another part is still trying to use it.

💡 Suggestion: Centralize Page Lifecycle Management
Ensure that the function responsible for creating a page is also responsible for closing it. The proposed "Page Re-use" pattern above helps solve this by creating a clear ownership model where the batch processor manages the lifecycle of all pages in the pool. Avoid passing page objects up and down long call chains where their state can become uncertain.

Problem: Generic Screenshot Filenames
Screenshots are sometimes saved as ..._unknown.png because the DOI context is lost.

💡 Suggestion: Propagate Context for Debugging
Ensure the doi is passed down through the function calls to _take_debug_screenshot. The log shows this is already happening in some places but failing in others. A quick review of the call stack leading to _take_debug_screenshot can identify where the doi variable is not being passed.

🛠 4. Enhance Code Quality and Maintainability
The code is modular, but some parts can be made more flexible and less redundant.

Problem: Hardcoded Selectors and Patterns
The CSS selectors in _ResolverLinkFinder.py and the publisher URL patterns in _find_functions.py are hardcoded. As websites change, developers will need to constantly edit these Python files.

💡 Suggestion: Externalize Configuration
Move these lists of selectors and patterns into an external configuration file (e.g., config/selectors.yaml). This allows for easier updates without touching the core logic. The script can load this file at startup.

Example selectors.yaml:

YAML

resolver_structure_selectors:
  - "div#fulltext a"
  - ".sfx-fulltext a"
  # ... etc

publisher_pdf_patterns:
  nature:
    domain: "nature.com"
    pattern: "{url}.pdf"
  frontiers:
    domain: "frontiersin.org"
    pattern: "{url_with_/full}/pdf"
Problem: Redundant PDF Scraping Logic
Both _ZoteroTranslatorRunner.py and _find_functions.py contain JavaScript snippets that search for PDF links using query selectors. This logic is duplicated.

💡 Suggestion: Consolidate Scraping Logic
The _find_direct_pdf_links function in _find_functions.py should be the single source of truth for all direct page scraping. The Zotero runner should be simplified to only run the translator script. The main find_urls_pdf orchestrator can then call the translator first and _find_direct_pdf_links second as a fallback. This reduces redundancy and makes the logic easier to maintain.


########################################################################################################################
########################################################################################################################
########################################################################################################################

 I've analyzed the new log file to assess the impact of your changes.

The updated selectors have had a mixed effect. While some specific lookups are now succeeding where they might have failed before, the overall success rate has unfortunately decreased from 88.0% (66/75) to 76.0% (57/75).

Let's break down what's happening.

✅ What's Working Well (The Good News)
Your script continues to be very effective with certain types of sources:

Preprint Servers: It handles arxiv.org and biorxiv.org flawlessly using the Zotero translators.

Direct Publisher Patterns: The logic for publishers like PLOS, IEEE, and Wiley seems robust, finding PDFs via both Zotero and your custom publisher patterns ("source": "publisher_pattern").

ScienceDirect (via Zotero): The log shows a key success where the Zotero translator did work on a ScienceDirect page:
SUCCESS: Zotero Translator extracted 1 URLs from https://www.sciencedirect.com/science/article/pii/S1087079220300964?via%3Dihub
This confirms that when the script can get to the right page, the Zotero integration is a powerful tool.

❗️ Key Issues to Address (The Bad News)
The drop in success rate appears to be caused by two persistent, critical issues that are preventing your new selectors from even being used in many cases.

1. Critical Bug: "Page Closed" Errors During Resolution
This is the most significant problem. The log is filled with this error:
ERROR: OpenURL resolution failed: Page.goto: Target page, context or browser has been closed

What's Happening: When your script clicks a link on a university resolver page (e.g., a link that says "Elsevier ScienceDirect Journals"), that link often opens the article in a new browser tab. However, your script's logic in resolve_openurl (_resolve_functions.py) doesn't correctly "capture" this new tab. It continues to operate on the original, now-irrelevant resolver tab, which may get closed by other parts of the code, leading to the crash.

Why It's Lowering the Score: Every time this error occurs, the script fails to reach the publisher's page, and the chance of finding the PDF drops to zero for that DOI. This is a major source of the failures.

How to Fix It: You need to explicitly handle new tabs. Playwright provides an event listener for this.

💡 Suggested Fix in _resolve_functions.py (inside resolve_openurl):

Python

# In resolve_openurl, when you are about to click a link...
if link:
    logger.info("Found resolver link, attempting to click...")
    
    # Use context.expect_page() to gracefully handle new tabs
    async with context.expect_page() as new_page_info:
        await link.click() # Click the link that opens a new tab
    
    new_page = await new_page_info.value
    await new_page.wait_for_load_state("domcontentloaded")
    
    logger.success(f"Successfully navigated to new tab: {new_page.url}")
    
    # NOW, you can search for the PDF on this 'new_page'
    # ... your find_urls_pdf logic would go here ...

    final_url = new_page.url
    await new_page.close()
    return final_url
2. Landing on Abstract Pages for Elsevier/ScienceDirect
The second major issue is that even when the script successfully navigates to ScienceDirect, it often lands on an abstract page (URLs containing /abs/pii/).

What's Happening: Your new selectors for finding PDF links (a.PdfLink, etc.) are great, but they are useless on an abstract page because those links often don't exist there. The actual PDF is usually one click away, behind a "View PDF" or "Download PDF" button that takes you to the PDF viewer page.

How to Fix It: The script needs a two-step approach for these sites:

Check the URL: If the page URL contains /abs/, it's an abstract page.

Perform a Second Click: On the abstract page, search for a link/button with text like "View PDF" and click it to navigate to the actual article page before searching for the download links.

Summary & Next Steps
Your core PDF-finding strategies (Zotero, selectors, patterns) are solid, but they are being undermined by navigation failures.

Highest Priority: Fix the "Page Closed" bug in your OpenURL resolver logic by properly handling new tabs. This is the single biggest cause of failures in the log.

Second Priority: Implement a two-step process for ScienceDirect to navigate from abstract pages to full-text/PDF pages before running your selectors.

Addressing these two navigation issues will allow your improved selectors to run on the correct pages, which should significantly increase your success rate.


########################################
########################################
########################################



Yes, I can analyze the progress based on the new log file.

You've made some progress, as the success rate has 

increased slightly from 88.0% to 90.7% (68/75 PDFs found). This is a positive step. The script is now successfully finding PDFs for some Elsevier (

sciencedirect.com) and Cell Press (cell.com) articles that were previously failing.

However, the core underlying problems persist, preventing a more significant improvement.

✅ Analysis of Progress & Successes
Zotero Translators are Working on Complex Sites: You now have confirmed successes where the Zotero translator is correctly extracting PDF links from authenticated Elsevier and Cell Press pages. This is a significant win because it shows your authentication is working and the core strategy is sound when it can get to the right page.



Publisher Patterns Remain Robust: Simple publisher-specific URL transformations (e.g., for Frontiers, PLOS, IEEE) continue to work reliably, providing a solid baseline success rate.




Direct Link Scraping is Effective: Your updated selectors are successfully finding direct links on pages for publishers like SAGE and Oxford University Press (academic.oup.com), which were failing in the previous log.


❗️ Remaining Core Issues
The reason the success rate isn't higher is that the same two critical issues are still causing many lookups to fail before your improved selectors can even run.

1. "Page Closed" Errors on Resolver Links (Highest Priority)
This remains the biggest issue. The log is still showing multiple instances of the script failing when it tries to follow a link from your university's resolver.


Symptom: ERROR: OpenURL resolution failed: Page.goto: Target page, context or browser has been closed.


Root Cause: The script clicks a link on the resolver page that opens the publisher's site in a new browser tab. The code isn't correctly handling this new tab, and the original tab is being closed prematurely, causing the operation to crash. This accounts for most of the completely missed PDFs.

2. Landing on Abstract Pages
Even when the script successfully navigates to a publisher like ScienceDirect, it often lands on an abstract page (e.g., one with 

/abs/ in the URL) where there is no direct PDF link. Your new selectors can't find a link that doesn't exist on the current page.



Symptom: FAIL: Not found any PDF URLs from https://www.sciencedirect.com/science/article/abs/pii/....


Root Cause: The resolver is correctly authenticating you but is sending you to the abstract page. The script lacks a mechanism to perform a second click on the "View PDF" button to get to the page where the actual PDF is available.

🎯 Next Steps to Increase Success Rate
Fix the New Tab Handling: This is essential. Modifying the resolve_openurl function in url/helpers/_resolve_functions.py to correctly manage new tabs (using context.expect_page()) will solve the majority of the outright failures.

Implement Two-Step Clicks: Enhance your PDF finding logic to check if it has landed on an abstract page. If so, it should then search for and click a "View PDF" or similar link before running the final PDF selectors.


Refine Negative Keywords: You correctly identified that the script was clicking a "Cookie Policy" link. Adding keywords like 

cookie to a negative list (as previously suggested) will prevent this and make the resolver logic more robust.

<!-- EOF -->