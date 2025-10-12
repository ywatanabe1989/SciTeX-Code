<!-- ---
!-- Timestamp: 2025-10-08 06:56:32
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/README.md
!-- --- -->


1. URL -> OpenAthens Auth -> Download <= This does not work. Authentication is on openathens.net and not on publisher page
2. URL -> OpenURL -> Publisher-specific cache -> Publisher page (authenticated) -> Download

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
    OUTPUT_PATH = "~/.scitex/scholar/downloads/hippocampal_ripples-by-stealth.pdf"

    # Main
    saved_path = await pdf_downloader.download_from_url(
        PDF_URL,
        output_path=OUTPUT_PATH,
    )

    if saved_path:
        logger.info(f"PDF downloaded suffcessfully to: {saved_path}")
    else:
        logger.error("Failed to download PDF")

import asyncio
asyncio.run(main_async())
```

<!-- EOF -->