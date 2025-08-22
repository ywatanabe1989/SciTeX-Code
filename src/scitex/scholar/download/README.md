<!-- ---
!-- Timestamp: 2025-08-22 07:39:17
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/README.md
!-- --- -->

## Science Direct
● The key issue is that the authenticated PDF URLs (from pdf.sciencedirectassets.com) contain session-specific tokens that are
  only valid within the browser context where they were generated. When you try to access them directly in a new session, they
  redirect back to the publisher page.

  The solution is to download the PDF within the same browser context where we obtained the URL. Let me check how the
  ScholarPDFDownloader handles this:


## Usage

``` python
async def main_async():
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarURLFinder,
    )

    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=ScholarAuthManager(),
        use_zenrows_proxy=False,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )
    pdf_downloader = ScholarPDFDownloader(context)

    # Parameters
    PDF_URL = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"
    OUTPUT_PATH = "/tmp/hippocampal_ripples-by-stealth.pdf"

    # Main
    saved_path = await pdf_downloader.download_from_url(
        PDF_URL,
        output_path=OUTPUT_PATH,
    )

    if saved_path:
        logger.success(f"PDF downloaded successfully to: {saved_path}")
    else:
        logger.error("Failed to download PDF")

import asyncio
asyncio.run(main_async())
```

<!-- EOF -->