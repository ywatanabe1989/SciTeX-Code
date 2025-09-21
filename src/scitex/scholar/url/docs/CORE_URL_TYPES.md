<!-- ---
!-- Timestamp: 2025-08-08 08:37:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/urls/CORE_URL_TYPES.md
!-- --- -->

# Core URL Types for Scholar Metadata

## Essential URLs in Resolution Order

## Usage

``` python
from scitex.scholar.metadata.urls import ScholarURLFinder
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.auth import ScholarAuthManager

browser_manager = ScholarBrowserManager(
    chrome_profile_name="system",
    browser_mode="interactive",
    auth_manager=ScholarAuthManager(),
)

browser, context = (
    await browser_manager.get_authenticated_browser_and_context_async()
)

url_finder = ScholarURLFinder(context)
urls = await url_handler.find_urls(doi="10.1523/jneurosci.2929-12.2012")
print(urls)
# {'url_doi': 'https://doi.org/10.1523/jneurosci.2929-12.2012',
#  'url_publisher': 'https://www.jneurosci.org/content/32/44/15467',
#  'url_pdf': ['https://www.jneurosci.org/content/jneuro/32/44/15467.full.pdf',
#   'https://www.jneurosci.org/content/32/44.toc.pdf',
#   'https://www.jneurosci.org/content/jneuro/32/44/local/advertising.pdf',
#   'https://www.jneurosci.org/content/jneuro/32/44/local/ed-board.pdf',
#   'https://www.jneurosci.org/content/jneuro/32/44/15467.full-text.pdf',
#   'https://www.jneurosci.org/content/32/44/15467.full.pdf']}

## Download article PDF
from playwright.async_api import BrowserContext
from pathlib import Path
from scitex import logging

logger = logging.getLogger(__name__)


async def download_from_url(context: BrowserContext, pdf_url: str, output_path: Path):
    """
    Download PDF using request context (bypasses Chrome PDF viewer).
    
    This sends HTTP requests with the browser's cookies/auth,
    but doesn't render the response in the browser.
    """
    response = await context.request.get(pdf_url)
    
    if response.ok and response.headers.get('content-type', '').startswith('application/pdf'):
        content = await response.body()
        
        with open(output_path, 'wb') as f:
            f.write(content)
        
        return True
    return False

for ii_pdf, url_pdf in enumerate(urls["url_pdf"]):
    success = await download_from_url(context, url_pdf, f"/tmp/tmp_{ii_pdf}.pdf")
    if success:
        logger.success(f"Downloaded: {url_pdf}")
    else:
        logger.fail(f"Not downloaded {url_pdf}")


```



### 1. **DOI URL** (`url_doi`)
- **What**: The DOI resolver URL
- **Example**: `https://doi.org/10.1038/s41593-025-01990-7`
- **Purpose**: Permanent identifier that redirects to current publisher location
- **Source**: Extracted from metadata or constructed from DOI

### 2. **Publisher URL** (`url_publisher`) 
- **What**: The actual publisher's article page (after DOI redirect)
- **Example**: `https://www.nature.com/articles/s41593-025-01990-7`
- **Purpose**: The publisher's canonical article page
- **Source**: Result of following DOI redirect

### 3. **OpenURL Query URL** (`url_openurl_query`)
- **What**: The OpenURL query with metadata parameters
- **Example**: `https://unimelb.hosted.exlibrisgroup.com/openurl/61UNIMELB/61UNIMELB_INST?sid=google&auinit=S&aulast=Elyounssi&atitle=Addressing%20artifactual%20bias&jtitle=Nature%20Neuroscience&doi=10.1038/s41593-025-01990-7`
- **Purpose**: Query URL containing bibliographic metadata for resolver
- **Source**: Generated from article metadata using OpenURL 1.0 standard

### 4. **OpenURL Resolved URL** (`url_openurl_resolved`)
- **What**: The final URL after OpenURL resolver processes the query
- **Example**: `https://www-nature-com.eu1.proxy.openathens.net/articles/s41593-025-01990-7`
- **Purpose**: The authenticated publisher URL via institutional proxy
- **Source**: Result of OpenURL resolver's "Go" button or automatic redirect

### 5. **Final PDF URL** (`url_final_pdf`)
- **What**: The actual working PDF download URL
- **Example**: `https://www-nature-com.eu1.proxy.openathens.net/articles/s41593-025-01990-7.pdf`
- **Purpose**: Direct link to download the PDF (with authentication)
- **Source**: Discovered through various methods (Zotero, patterns, page scraping)

## Simplified Metadata Structure

```json
{
  "scitex_id": "F99329E1",
  "title": "Addressing artifactual bias in large...",
  
  "doi": "10.1038/s41593-025-01990-7",
  "url_doi": "https://doi.org/10.1038/s41593-025-01990-7",
  "url_doi_source": "CrossRef",
  
  "url_publisher": "https://www.nature.com/articles/s41593-025-01990-7",
  "url_publisher_source": "DOI_resolution",
  
  "url_openurl_query": "https://unimelb.hosted.exlibrisgroup.com/openurl/61UNIMELB/61UNIMELB_INST?sid=scitex&doi=10.1038/s41593-025-01990-7",
  "url_openurl_query_source": "OpenURLGenerator",
  
  "url_openurl_resolved": "https://www-nature-com.eu1.proxy.openathens.net/articles/s41593-025-01990-7",
  "url_openurl_resolved_source": "OpenURLResolver",
  
  "url_final_pdf": "https://www-nature-com.eu1.proxy.openathens.net/articles/s41593-025-01990-7.pdf",
  "url_final_pdf_source": "DirectRequest",
  
  "urls_pdf": [
    "https://www.nature.com/articles/s41593-025-01990-7.pdf",
    "https://www-nature-com.eu1.proxy.openathens.net/articles/s41593-025-01990-7.pdf"
  ],
  "urls_pdf_source": "MultipleStrategies",
  
  "pdf_downloaded": false,
  "pdf_download_attempts": [],
  
  "urls_updated_at": "2025-08-08T00:00:00Z"
}
```

## Resolution Pipeline

```
1. DOI → url_doi
   ↓
2. Resolve DOI → url_publisher
   ↓
3. Build OpenURL query → url_openurl_query
   ↓
4. Submit to resolver → url_openurl_resolved (authenticated)
   ↓
5. Find PDF URLs (multiple strategies) → urls_pdf[]
   ↓
6. Test & download PDFs → url_final_pdf
```

## OpenURL Query Parameters

The `url_openurl_query` typically includes:
- `sid`: Source identifier (e.g., "scitex", "google")
- `doi`: Digital Object Identifier
- `atitle`: Article title
- `jtitle`: Journal title
- `aulast`: Author last name
- `aufirst`: Author first name
- `date`: Publication date
- `volume`: Volume number
- `issue`: Issue number
- `spage`: Start page
- `epage`: End page
- `issn`: Journal ISSN

## Key Differences

- **`url_openurl_query`**: The constructed query URL with metadata parameters - what you send TO the resolver
- **`url_openurl_resolved`**: The authenticated URL you get BACK from the resolver after it processes your query

This distinction is important because:
1. The query URL is what we generate from metadata
2. The resolved URL is what we get after authentication/proxy routing
3. Sometimes the resolver shows an intermediate page with multiple options
4. The resolved URL may vary based on institutional subscriptions

<!-- EOF -->