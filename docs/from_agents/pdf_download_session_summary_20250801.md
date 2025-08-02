# PDF Download Session Summary
Date: 2025-08-01
DOI: 10.1016/j.neubiorev.2020.07.005

## Paper Details
- **Title**: Generative models, linguistic communication and active inference
- **Authors**: Karl J. Friston, Thomas Parr, Yan Yufik, Noor Sajid, Catherine J. Price, Emma Holmes
- **Journal**: Neuroscience & Biobehavioral Reviews
- **Year**: 2020
- **Volume**: 118
- **Pages**: 42-64

## Session Activities

### 1. Browser Navigation
- Successfully opened Chrome browser using Puppeteer MCP
- Navigated to DOI resolver URL: https://doi.org/10.1016/j.neubiorev.2020.07.005
- Page redirected to ScienceDirect: https://www.sciencedirect.com/science/article/pii/S0149763420304668

### 2. PDF Access Attempts
- Found PDF link on ScienceDirect page
- PDF URL: https://www.sciencedirect.com/science/article/pii/S0149763420304668/pdfft?md5=ddcdca44eec97eab80e3d3486fe9a855&pid=1-s2.0-S0149763420304668-main.pdf
- Clicked "View PDF" button successfully
- Browser opened new window/tab for PDF viewing

### 3. Download Methods Tested
1. **Direct Download with requests**: Failed (HTTP 400 - requires authentication)
2. **Crawl4AI PDF endpoint**: Failed (connection issues)
3. **Scholar module with search**: Found wrong paper (DOI mismatch issue)
4. **OpenURL resolver**: Script created but authentication needed

### 4. Key Findings
- ScienceDirect requires institutional authentication for PDF downloads
- The paper is accessible through the browser with proper authentication
- OpenAthens authentication would enable automated downloads
- Manual download through browser is possible by clicking download button in PDF viewer

## Recommendations

### For Manual Download
1. Use the open browser window
2. Click on the PDF viewer's download button
3. Save the PDF locally

### For Automated Downloads
1. Configure OpenAthens authentication:
   ```python
   from scitex.scholar import Scholar
   scholar = Scholar()
   scholar.configure_openathens(email="your_email@unimelb.edu.au")
   scholar.authenticate_openathens()
   ```

2. Use Scholar module with authentication:
   ```python
   papers = scholar.search(query="doi:10.1016/j.neubiorev.2020.07.005")
   scholar.download_pdfs(papers, output_dir="pdfs")
   ```

3. Or use OpenURL resolver for batch processing:
   ```python
   from scitex.scholar.open_url import OpenURLResolver
   from scitex.scholar.auth import AuthenticationManager
   
   auth_manager = AuthenticationManager()
   resolver = OpenURLResolver(auth_manager)
   result = resolver.resolve(doi="10.1016/j.neubiorev.2020.07.005")
   ```

## Files Created
- `.dev/download_single_pdf.py` - Scholar module download script
- `.dev/download_with_openurl.py` - OpenURL resolver script
- `.dev/download_pdf_simple.py` - Direct download attempt

## Next Steps
1. Complete manual download from browser if needed
2. Set up OpenAthens authentication for automated downloads
3. Test batch download functionality with multiple DOIs