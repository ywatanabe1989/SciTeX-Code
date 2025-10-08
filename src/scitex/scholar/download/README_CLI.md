# PDF Downloader CLI Usage

## Single Paper Download with Arguments

You can now test downloading papers one by one using command-line arguments:

### Basic Usage

```bash
python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
    --doi "10.1088/1741-2552/aaf92e" \
    --output /tmp/my_paper.pdf
```

### With Browser Mode

```bash
# Stealth mode (headless, default)
python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
    --doi "10.1016/s1474-4422(13)70075-9" \
    --browser-mode stealth

# Interactive mode (visible browser, good for debugging)
python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
    --doi "10.1016/s1474-4422(13)70075-9" \
    --browser-mode interactive

# Manual mode (you control the browser)
python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
    --doi "10.1016/s1474-4422(13)70075-9" \
    --browser-mode manual
```

### With Direct PDF URL

```bash
python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
    --doi "10.48550/arXiv.2309.09471" \
    --pdf-url "https://arxiv.org/pdf/2309.09471" \
    --output /tmp/arxiv_paper.pdf
```

## Arguments

- `--doi` (required): DOI of the paper (with or without https://doi.org/ prefix)
- `--pdf-url` (optional): Direct PDF URL. If not provided, will be found automatically from DOI
- `--output` (optional): Output path for the PDF (default: /tmp/downloaded_paper.pdf)
- `--browser-mode` (optional): Browser mode - stealth/interactive/manual (default: stealth)

## Test Script

A test script is available at `.dev/test_download_one.sh` that tries downloading a paper that failed earlier:

```bash
.dev/test_download_one.sh
```

## Examples of Failed Papers to Test

From the neurovista collection, these papers have DOIs but failed to download:

1. **Lancet Neurology (Cook 2013)** - Paywall
   ```bash
   python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
       --doi "10.1016/s1474-4422(13)70075-9" \
       --browser-mode interactive
   ```

2. **IEEE Paper** - Not subscribed
   ```bash
   python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
       --doi "10.1109/niles56402.2022.9942397" \
       --browser-mode interactive
   ```

3. **Brain (Grigorovsky 2020)** - Oxford Academic
   ```bash
   python -m scitex.scholar.download.ScholarPDFDownloaderWithScreenshots \
       --doi "10.1093/brain/awx098" \
       --browser-mode interactive
   ```

## Tips

- Use `--browser-mode interactive` to see what's happening in the browser
- Screenshots are automatically saved to the cache directory for debugging
- Check the download log for detailed information about what went wrong
- Some papers behind paywalls may require manual intervention even with authentication

