#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 20:20:01 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from pathlib import Path
from pprint import pprint

from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarEngine,
    ScholarPDFDownloader,
    ScholarURLFinder,
)


async def main_async():
    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=ScholarAuthManager(),
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine()
    url_finder = ScholarURLFinder(context)
    pdf_downloader = ScholarPDFDownloader(context)

    # Parameters
    TITLE = "Hippocampal ripples down-regulate synapses"
    # DOI = "10.1126/science.aao0702"

    # 1. Search for metadata
    print("1. Searching for metadata...")
    metadata = await engine.search_async(title=TITLE)
    pprint(metadata)
    doi = metadata.get("id").get("doi")

    # 2. Find URLs
    print("\n2. Finding URLs...")
    urls = await url_finder.find_urls(doi=doi)
    pprint(urls)

    __import__("ipdb").set_trace()
    # 3. Download PDFs
    print("\n3. Downloading PDFs...")
    pdf_urls = [entry["url"] for entry in urls["url_pdf"]]

    downloaded_paths = []
    for ii_, pdf_url in enumerate(pdf_urls[:3]):  # Limit to first 3 URLs
        output_path = Path("/tmp/scholar_pipeline") / f"paper_{ii_}.pdf"
        result = await pdf_downloader.download_from_url(pdf_url, output_path)
        if result:
            downloaded_paths.append(result)

    # Results
    print(f"\nPipeline completed:")
    print(f"- Found metadata: {bool(metadata)}")
    print(f"- Found {len(pdf_urls)} PDF URLs")
    print(f"- Downloaded {len(downloaded_paths)} PDFs")
    for path in downloaded_paths:
        print(f"  - {path}")


asyncio.run(main_async())

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-08-15 20:12:49 (ywatanabe)"
# # File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline.py
# # ----------------------------------------
# from __future__ import annotations
# import os
# __FILE__ = (
#     "./src/scitex/scholar/examples/99_fullpipeline.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------

# import asyncio

# from scitex.logging import configure_logging
# from scitex.scholar import (
#     ScholarAuthManager,
#     ScholarBrowserManager,
#     ScholarEngine,
#     ScholarPDFDownloader,
#     ScholarURLFinder,
# )

# configure_logging("success")


# async def main_async():
#     # Parameters
#     QUERY_TITLE = "Attention is All You Need"
#     QUERY_TITLE = "Hippocampal ripples down-regulate synapses"
#     OUTPUT_DIR = "/tmp/papers/"
#     BROWSER_MODE = ["stealth", "interactive"][1]

#     # Step 0: Instantiate classes
#     print(f"\n{'-'*40}\nStep 0: Instantiate classes\n{'-'*40}")
#     engine = ScholarEngine()
#     browser_manager = ScholarBrowserManager(
#         auth_manager=ScholarAuthManager(),
#         browser_mode=BROWSER_MODE,
#         chrome_profile_name="system",
#     )
#     browser, context = (
#         await browser_manager.get_authenticated_browser_and_context_async()
#     )
#     url_finder = ScholarURLFinder(context)
#     pdf_downloader = ScholarPDFDownloader(context)

#     # Step 1: Query -> Metadata with DOI
#     print(f"\n{'-'*40}\nStep 1: Query -> Metadata with DOI\n{'-'*40}")
#     metadata = await engine.search_async(title=QUERY_TITLE)
#     doi = metadata.get("id").get("doi")

#     # Step 2: Get URLs for the paper
#     print(f"\n{'-'*40}\nStep 2: Get URLs for the paper\n{'-'*40}")
#     urls = await url_finder.find_urls(doi=doi)

#     __import__("ipdb").set_trace()

#     # Step 3: Download PDF
#     print(f"\n{'-'*40}\nStep 3: Download PDF\n{'-'*40}")
#     paths = await pdf_downloader.download_from_doi(doi, output_dir=OUTPUT_DIR)

#     print(paths)

#     # await browser.close()


# asyncio.run(main_async())

# # EOF

# EOF
