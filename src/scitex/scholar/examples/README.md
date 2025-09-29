<!-- ---
!-- Timestamp: 2025-08-23 01:33:24
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/README.md
!-- --- -->

EXAMPLE_DIR=/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples
"$EXAMPLE_DIR"/00_config.py
"$EXAMPLE_DIR"/01_auth.py
"$EXAMPLE_DIR"/02_browser.py
"$EXAMPLE_DIR"/03_01-engine.py
"$EXAMPLE_DIR"/03_02-engine-for-bibtex.py --no-cache
"$EXAMPLE_DIR"/04_01-url.py --no-cache
"$EXAMPLE_DIR"/04_02-url-for-bibtex.py --no-cache-url-finder --n-samples 10 --browser-mode stealth
"$EXAMPLE_DIR"/05_download_pdf.py --pdf-url
"$EXAMPLE_DIR"/06_find_and_download.py

<!-- EOF -->