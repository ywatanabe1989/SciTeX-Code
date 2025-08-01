#!/usr/bin/env python3
"""
Download a single paper using Crawl4AI MCP to test the workflow
"""

import json
import os
from pathlib import Path

# Test with the first paper
test_paper = {
    "title": "Quantification of Phase-Amplitude Coupling",
    "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096", 
    "filename": "Hulsemann-2019-FIN.pdf"
}

output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/downloaded_papers")
output_dir.mkdir(exist_ok=True)

print(f"Testing PDF download for: {test_paper['title']}")
print(f"URL: {test_paper['url']}")
print(f"Output: {output_dir / test_paper['filename']}")

# The actual download will be done via MCP tools in the next step