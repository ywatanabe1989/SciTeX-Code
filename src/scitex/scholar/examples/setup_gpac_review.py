#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:45:00 (ywatanabe)"
# File: ./examples/setup_gpac_review.py

"""
Quick setup script for gPAC literature review.

This script helps you get started with literature review for your gPAC paper
by setting up the necessary directories and configuration.
"""

import os
import sys
from pathlib import Path
import subprocess

def setup_gpac_review():
    """Set up the gPAC literature review environment."""
    
    # Paths
    gpac_dir = Path.home() / "proj" / "gpac"
    paper_dir = gpac_dir / "paper"
    lit_review_dir = paper_dir / "literature_review"
    
    print("🔧 Setting up gPAC literature review environment...")
    print(f"📁 gPAC project: {gpac_dir}")
    print(f"📄 Paper directory: {paper_dir}")
    print(f"📚 Literature review: {lit_review_dir}")
    
    # Check if gPAC project exists
    if not gpac_dir.exists():
        print(f"❌ gPAC project not found at {gpac_dir}")
        print("Please ensure your gPAC project is at ~/proj/gpac/")
        return False
    
    # Create literature review directory
    lit_review_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created literature review directory: {lit_review_dir}")
    
    # Create subdirectories
    subdirs = ["papers", "summaries", "figures", "tables"]
    for subdir in subdirs:
        (lit_review_dir / subdir).mkdir(exist_ok=True)
        print(f"  📁 Created: {subdir}/")
    
    # Copy the literature review script
    scitex_dir = Path(__file__).parent.parent
    review_script = scitex_dir / "examples" / "gpac_literature_review.py"
    target_script = lit_review_dir / "run_literature_review.py"
    
    if review_script.exists():
        import shutil
        shutil.copy2(review_script, target_script)
        os.chmod(target_script, 0o755)  # Make executable
        print(f"✅ Copied literature review script to: {target_script}")
    else:
        print(f"⚠️ Literature review script not found at: {review_script}")
    
    # Create a simple config file
    config_content = f"""# gPAC Literature Review Configuration

# Output directory
output_dir: {lit_review_dir}

# Paper information
paper:
  title: "gPAC: GPU-Accelerated Phase-Amplitude Coupling Analysis for Large-Scale Neural Data"
  authors: ["Your Name"]
  keywords: ["phase-amplitude coupling", "GPU acceleration", "neural oscillations", "PyTorch"]

# Search parameters
search:
  max_papers_per_query: 20
  years_back: 10
  sources: ["pubmed", "arxiv"]

# Analysis parameters
analysis:
  vector_search_threshold: 0.3
  top_k_results: 10
"""
    
    config_file = lit_review_dir / "config.yaml"
    with open(config_file, 'w') as f:
        f.write(config_content)
    print(f"✅ Created configuration file: {config_file}")
    
    # Create a README
    readme_content = f"""# gPAC Literature Review

This directory contains the literature review for the gPAC paper using SciTeX-Scholar.

## Files
- `run_literature_review.py` - Main literature review script
- `config.yaml` - Configuration file
- `papers/` - Downloaded papers and PDFs
- `summaries/` - Generated summaries and analysis
- `figures/` - Figures and visualizations
- `tables/` - Data tables and comparisons

## Usage

1. **Run the literature review:**
   ```bash
   cd {lit_review_dir}
   python run_literature_review.py --output-dir .
   ```

2. **Customize the search:**
   Edit the search queries in `run_literature_review.py` to focus on specific aspects.

3. **Integration with paper:**
   The script will generate:
   - `gpac_references.bib` - Bibliography file for LaTeX
   - `literature_review_summary.md` - Comprehensive summary
   - `gap_analysis.json` - Research gap analysis

## Next Steps

1. Review the generated summary to understand the research landscape
2. Copy the .bib file to your paper directory
3. Use the gap analysis to strengthen your contribution claims
4. Identify key papers to cite in your introduction and related work

## SciTeX-Scholar Features Used

- Multi-source paper search (PubMed, arXiv)
- Vector-based similarity search
- Automated PDF processing
- Gap analysis and recommendation generation
- LaTeX bibliography generation
"""
    
    readme_file = lit_review_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"✅ Created README: {readme_file}")
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print(f"1. cd {lit_review_dir}")
    print("2. python run_literature_review.py --output-dir .")
    print("3. Review the generated summary and bibliography")
    print("4. Integrate findings into your paper")
    
    return True

if __name__ == "__main__":
    setup_gpac_review()