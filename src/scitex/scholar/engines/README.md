<!-- ---
!-- Timestamp: 2025-08-15 18:57:29
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/README.md
!-- --- -->

## Usage
``` python
import asyncio
from pprint import pprint
from scitex.scholar import ScholarEngine

async def main_async():
    # Query
    TITLE = "Attention is All You Need"
    DOI = "10.1038/nature14539"

    # Example: Unified Engine
    engine = ScholarEngine()
    outputs = {}

    # Search by Title
    outputs["metadata_by_title"] = await engine.search_async(
        title=TITLE,
    )
     
    # Search by DOI
    outputs["metadata_by_doi"] = await engine.search_async(
        doi=DOI,
    )

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)

asyncio.run(main_async())
```

<!-- EOF -->