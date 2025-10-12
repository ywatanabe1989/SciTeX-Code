#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar pipelines - Modular paper processing workflows.

This module contains the actual implementation of paper processing pipelines.
Scholar class acts as a facade that delegates to these pipelines.

Architecture:
- Pipelines contain the workflow logic
- Scholar provides simple, user-friendly API
- Advanced users can use pipelines directly for fine-grained control

Usage:
    # Via Scholar (simple)
    scholar = Scholar()
    paper = scholar.process_paper(doi="10.1234/example")

    # Via Pipeline (advanced)
    from scitex.scholar.pipelines import PaperProcessingPipeline
    pipeline = PaperProcessingPipeline(config=config)
    paper = await pipeline.run(doi="10.1234/example")
"""

from ._ScholarPipelineBase import ScholarPipelineBase
from .ScholarPipelinePaper import ScholarPipelinePaper
from .ScholarPipelinePapers import ScholarPipelinePapers
from .ScholarPipelineEnrichment import ScholarPipelineEnrichment
from .ScholarPipelineBibTeX import ScholarPipelineBibTeX

# Backward compatibility aliases
BasePipeline = ScholarPipelineBase
PaperProcessingPipeline = ScholarPipelinePaper
BatchProcessingPipeline = ScholarPipelinePapers
EnrichmentPipeline = ScholarPipelineEnrichment
BibTeXImportPipeline = ScholarPipelineBibTeX

__all__ = [
    "ScholarPipelineBase",
    "ScholarPipelinePaper",
    "ScholarPipelinePapers",
    "ScholarPipelineEnrichment",
    "ScholarPipelineBibTeX",
    # Backward compatibility
    "BasePipeline",
    "PaperProcessingPipeline",
    "BatchProcessingPipeline",
    "EnrichmentPipeline",
    "BibTeXImportPipeline",
]

# EOF
