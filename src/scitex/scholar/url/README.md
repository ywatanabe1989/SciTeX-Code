<!-- ---
!-- Timestamp: 2025-08-15 19:00:02
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/README.md
!-- --- -->

## Usage

```python
import asyncio

from scitex.scholar import ScholarURLFinder
from scitex.scholar import ScholarBrowserManager
from scitex.scholar import ScholarAuthManager


async def main_async():
    # Initialize with authenticated browser context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Create URL handler
    url_finder = ScholarURLFinder(context)

    # Get all URLs for a paper
    doi = "10.1038/s41467-023-44201-2"
    urls = await url_finder.find_urls(
        doi=doi,
    )


asyncio.run(main_async())

# print(urls.keys())
# dict_keys(['url_doi', 'url_publisher', 'url_pdf', 'url_supplementary'])

# from pprint import pprint
# pprint(urls)
# {'url_doi': 'https://doi.org/10.1038/s41467-023-44201-2',
#  'url_pdf': [{'reliability': 'high',
#               'source': 'zotero_translator',
#               'url': 'https://www.nature.com/articles/s41467-023-44201-2.pdf'},
#              {'reliability': 'high',
#               'source': 'zotero_translator',
#               'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM1_ESM.pdf'},
#              {'reliability': 'high',
#               'source': 'zotero_translator',
#               'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM2_ESM.pdf'},
#              {'reliability': 'high',
#               'source': 'zotero_translator',
#               'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM3_ESM.pdf'}],
#  'url_publisher': 'https://www.nature.com/articles/s41467-023-44201-2',
#  'url_supplementary': [{'description': 'Additional information',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'unknown',
#                         'url': 'https://www.nature.com/articles/s41467-023-44201-2#additional-information'},
#                        {'description': 'Google Scholar',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'unknown',
#                         'url': 'http://scholar.google.com/scholar_lookup?&title=A%20DIVERSITY%20OF%20SELECTIVE%20AUTOPHAGY%20RECEPTORS%20DETERMINES%20THE%20SPECIFICITY%20OF%20THE%20AUTOPHAGY%20PAThway&journal=Mol.%20Cell&doi=10.1016%2Fj.molcel.2019.09.005&volume=76&pages=268-285&publication_year=2019&author=Kirkin%2CV&author=Rogov%2CVV'},
#                        {'description': '1a',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'unknown',
#                         'url': 'https://www.nature.com/articles/s41467-023-44201-2#MOESM1'},
#                        {'description': 'Nature Portfolio Reporting Summary',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'unknown',
#                         'url': 'https://www.nature.com/articles/s41467-023-44201-2#MOESM3'},
#                        {'description': 'Suuplementary information',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'pdf',
#                         'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM1_ESM.pdf'},
#                        {'description': 'Peer Review File',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'pdf',
#                         'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM2_ESM.pdf'},
#                        {'description': 'Reporting Summary',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'pdf',
#                         'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM3_ESM.pdf'},
#                        {'description': 'Source Data',
#                         'reliability': 'low',
#                         'source': 'href_pattern',
#                         'type': 'excel',
#                         'url': 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-44201-2/MediaObjects/41467_2023_44201_MOESM4_ESM.xlsx'}]}
```

<!-- EOF -->