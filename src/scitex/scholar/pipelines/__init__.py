#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar pipelines - Primary implementations for paper processing workflows.

This module contains the battle-tested pipeline implementations moved from core/.
These are the single source of truth for all Scholar workflows.

Pipelines:
- ScholarPipelineSingle: Process one paper (DOI → metadata → URLs → PDF)
- ScholarPipelineParallel: Process multiple papers in parallel
- ScholarPipelineBibTeX: Import and process BibTeX files

Usage:
    # Single paper processing
    from scitex.scholar.pipelines import ScholarPipelineSingle
    pipeline = ScholarPipelineSingle()
    paper = await pipeline.process_paper_async(doi="10.1038/...")

    # Parallel processing
    from scitex.scholar.pipelines import ScholarPipelineParallel
    pipeline = ScholarPipelineParallel(num_workers=8)
    papers = await pipeline.process_papers_from_collection_async(papers)

    # BibTeX import
    from scitex.scholar.pipelines import ScholarPipelineBibTeX
    pipeline = ScholarPipelineBibTeX(num_workers=8)
    papers = await pipeline.process_bibtex_file_async(
        bibtex_path="papers.bib",
        project="my_project"
    )

    # Via Scholar API (recommended for most users)
    from scitex.scholar.core import Scholar
    scholar = Scholar(project="my_project")
    paper = await scholar.process_paper_async(doi="10.1038/...")
"""

from .ScholarPipelineSingle import ScholarPipelineSingle
from .ScholarPipelineParallel import ScholarPipelineParallel
from .ScholarPipelineBibTeX import ScholarPipelineBibTeX

__all__ = [
    "ScholarPipelineSingle",
    "ScholarPipelineParallel",
    "ScholarPipelineBibTeX",
]

# EOF
