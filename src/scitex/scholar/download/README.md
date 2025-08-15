<!-- ---
!-- Timestamp: 2025-08-15 19:54:28
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/README.md
!-- --- -->

## Usage

``` python
async def main_async():
    from scitex.scholar import ScholarPDFDownloader

    DOI = "10.1523/jneurosci.2929-12.2012"
    OUTPUT_DIR = "/tmp/"

    async with ScholarPDFDownloader() as downloader:
        await downloader.download_from_doi(doi, output_dir=output_dir)

import asyncio

asyncio.run(main_async())
```

<!-- EOF -->