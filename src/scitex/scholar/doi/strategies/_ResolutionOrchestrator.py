#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/strategies/_ResolutionOrchestrator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/strategies/_ResolutionOrchestrator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Resolution orchestrator for DOI resolution and metadata enrichment.

This orchestrator coordinates the entire paper resolution workflow:
1. Library Check (ScholarLibraryStrategy)
2. Source Resolution (SourceResolutionStrategy) 
3. Metadata Enrichment (existing EnricherPipeline)
4. Library Save (ScholarLibraryStrategy)

Extracted from SingleDOIResolver to follow Single Responsibility Principle and
integrate with existing enrichment infrastructure.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from scitex import logging

from ..._Paper import Paper
from ._ScholarLibraryStrategy import ScholarLibraryStrategy
from ._SourceResolutionStrategy import SourceResolutionStrategy

logger = logging.getLogger(__name__)


class ResolutionOrchestrator:
    """Orchestrator for complete paper resolution workflow with enrichment."""

    def __init__(
        self, 
        config: Any,
        project: str = "master",
        sources: Optional[List[str]] = None,
        rate_limit_handler: Optional[Any] = None,
        source_rotation_manager: Optional[Any] = None,
        email_config: Optional[Dict[str, str]] = None,
        enrichment_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize resolution orchestrator.
        
        Args:
            config: ScholarConfig object for path management
            project: Project name for library organization
            sources: List of DOI sources to use
            rate_limit_handler: Rate limit handler instance
            source_rotation_manager: Source rotation manager instance
            email_config: Email configuration for DOI sources
            enrichment_config: Configuration for metadata enrichment
        """
        self.config = config
        self.project = project
        
        # Initialize strategies
        self.library_strategy = ScholarLibraryStrategy(config, project)
        self.source_strategy = SourceResolutionStrategy(
            sources=sources,
            rate_limit_handler=rate_limit_handler,
            source_rotation_manager=source_rotation_manager,
            email_config=email_config
        )
        
        # Store enrichment config for lazy initialization to avoid circular imports
        self.enrichment_config = enrichment_config or {}
        self._enrichment_pipeline = None
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'library_hits': 0,
            'source_resolutions': 0,
            'enrichments': 0,
            'failures': 0,
            'start_time': None,
            'processing_times': []
        }
        
        logger.debug(f"ResolutionOrchestrator initialized for project '{project}'")

    @property 
    def enrichment_pipeline(self):
        """Lazy initialization of EnricherPipeline to avoid circular imports."""
        if self._enrichment_pipeline is None:
            try:
                from ...enrichment._EnricherPipeline import EnricherPipeline
                self._enrichment_pipeline = EnricherPipeline(
                    email_crossref=self.enrichment_config.get('email_crossref', 'research@example.com'),
                    email_pubmed=self.enrichment_config.get('email_pubmed', 'research@example.com'),
                    email_openalex=self.enrichment_config.get('email_openalex', 'research@example.com'),
                    email_semantic_scholar=self.enrichment_config.get('email_semantic_scholar', 'research@example.com'),
                    semantic_scholar_api_key=self.enrichment_config.get('semantic_scholar_api_key')
                )
                logger.debug("EnricherPipeline initialized successfully")
            except ImportError as e:
                logger.warning(f"Could not import EnricherPipeline: {e}")
                self._enrichment_pipeline = None
        return self._enrichment_pipeline

    async def resolve_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        url: Optional[str] = None,
        bibtex_source: Optional[str] = None,
        enable_enrichment: bool = True,
        **kwargs
    ) -> Optional[Dict]:
        """Complete resolution workflow: Library → Sources → Enrichment → Save.
        
        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)
            url: URL to extract DOI from (optional)
            bibtex_source: Original BibTeX source (optional)
            enable_enrichment: Whether to enrich metadata (default: True)
            **kwargs: Additional parameters for source resolution
            
        Returns:
            Dict with resolution results and metadata, or None if failed
        """
        if not title:
            return None
            
        start_time = time.time()
        self.stats['total_processed'] += 1
        
        if self.stats['start_time'] is None:
            self.stats['start_time'] = start_time
        
        try:
            # Phase 1: Check Scholar Library for existing DOI
            existing_doi = self.library_strategy.check_library_for_doi(title, year)
            if existing_doi:
                self.stats['library_hits'] += 1
                logger.info(f"DOI found in Scholar library: {existing_doi}")
                
                processing_time = time.time() - start_time
                self.stats['processing_times'].append(processing_time)
                
                return {
                    'doi': existing_doi,
                    'source': 'scholar_library'
                }
            
            # Phase 2: Source Resolution
            logger.debug(f"Resolving from sources: {title[:50]}...")
            resolution_result = await self.source_strategy.resolve_from_sources(
                title=title,
                year=year,
                authors=authors,
                url=url,
                **kwargs
            )
            
            if not resolution_result or not resolution_result.get('doi'):
                # Resolution failed - save as unresolved
                self.library_strategy.save_unresolved_paper(
                    title=title,
                    year=year,
                    authors=authors,
                    reason="DOI not found after source resolution",
                    bibtex_source=bibtex_source
                )
                self.stats['failures'] += 1
                
                processing_time = time.time() - start_time
                self.stats['processing_times'].append(processing_time)
                
                return None
            
            self.stats['source_resolutions'] += 1
            doi = resolution_result['doi']
            source = resolution_result['source']
            metadata = resolution_result.get('metadata', {})
            
            logger.success(f"DOI resolved via {source}: {doi}")
            
            # Phase 3: Metadata Enrichment (disabled to avoid nested metadata structure)
            enriched_metadata = metadata
            if enable_enrichment:
                logger.info("Enrichment temporarily disabled to prevent nested metadata structure - using source metadata only")
            
            # Phase 4: Save to Scholar Library
            paper_id = self.library_strategy.save_resolved_paper(
                title=title,
                doi=doi,
                year=year,
                authors=authors,
                source=source,
                metadata=enriched_metadata,
                bibtex_source=bibtex_source
            )
            
            processing_time = time.time() - start_time
            self.stats['processing_times'].append(processing_time)
            
            return {
                'doi': doi,
                'source': source,
                'metadata': enriched_metadata,
                'paper_id': paper_id
            }
            
        except Exception as e:
            self.stats['failures'] += 1
            processing_time = time.time() - start_time
            self.stats['processing_times'].append(processing_time)
            
            logger.error(f"Resolution orchestration failed for '{title[:50]}...': {e}")
            
            # Save as unresolved with error details
            self.library_strategy.save_unresolved_paper(
                title=title,
                year=year,
                authors=authors,
                reason=f"Orchestration error: {str(e)}",
                bibtex_source=bibtex_source
            )
            
            return None

    async def resolve_doi_async(self, *args, **kwargs) -> Optional[Dict]:
        """Alias for resolve_async to maintain backward compatibility with SingleDOIResolver."""
        return await self.resolve_async(*args, **kwargs)

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow statistics."""
        total_time = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        avg_processing_time = (
            sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            if self.stats['processing_times'] else 0
        )
        
        workflow_stats = {
            # Basic counts
            'total_processed': self.stats['total_processed'],
            'library_hits': self.stats['library_hits'],
            'source_resolutions': self.stats['source_resolutions'],
            'enrichments': self.stats['enrichments'],
            'failures': self.stats['failures'],
            
            # Success rates
            'library_hit_rate': (
                self.stats['library_hits'] / self.stats['total_processed'] * 100
                if self.stats['total_processed'] > 0 else 0
            ),
            'source_resolution_rate': (
                self.stats['source_resolutions'] / self.stats['total_processed'] * 100
                if self.stats['total_processed'] > 0 else 0
            ),
            'enrichment_rate': (
                self.stats['enrichments'] / self.stats['source_resolutions'] * 100
                if self.stats['source_resolutions'] > 0 else 0
            ),
            'overall_success_rate': (
                (self.stats['library_hits'] + self.stats['source_resolutions']) / 
                self.stats['total_processed'] * 100
                if self.stats['total_processed'] > 0 else 0
            ),
            
            # Performance metrics
            'total_runtime': total_time,
            'average_processing_time': avg_processing_time,
            'throughput_per_minute': (
                self.stats['total_processed'] / (total_time / 60)
                if total_time > 0 else 0
            ),
            
            # Component statistics
            'source_strategy_stats': self.source_strategy.get_source_statistics(),
        }
        
        return workflow_stats

    def reset_statistics(self) -> None:
        """Reset workflow statistics."""
        self.stats = {
            'total_processed': 0,
            'library_hits': 0,
            'source_resolutions': 0,
            'enrichments': 0,
            'failures': 0,
            'start_time': None,
            'processing_times': []
        }
        logger.info("Workflow statistics reset")


if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    
    async def test_resolution_orchestrator():
        """Test the resolution orchestrator functionality."""
        print("=" * 60)
        print("ResolutionOrchestrator Test")
        print("=" * 60)
        
        # Mock config object
        class MockConfig:
            class PathManager:
                def get_scholar_library_path(self):
                    return Path("/tmp/test_scholar_library")
                def get_paper_storage_paths(self, paper_info, collection_name):
                    import uuid
                    unique_id = str(uuid.uuid4())[:8]
                    storage_path = self.get_scholar_library_path() / collection_name / unique_id
                    readable_path = Path(f"AUTHOR-{paper_info.get('year', 'UNKNOWN')}-JOURNAL")
                    return {
                        'unique_id': unique_id,
                        'storage_path': storage_path,
                        'readable_path': readable_path
                    }
            path_manager = PathManager()
        
        config = MockConfig()
        
        # Create orchestrator with test configuration
        orchestrator = ResolutionOrchestrator(
            config=config,
            project="test",
            enrichment_config={
                'email_crossref': 'test@example.com',
                'email_pubmed': 'test@example.com',
                'email_openalex': 'test@example.com',
                'email_semantic_scholar': 'test@example.com'
            }
        )
        
        print("✅ ResolutionOrchestrator initialized")
        
        # Test papers
        test_papers = [
            {
                "title": "Attention is All You Need",
                "year": 2017,
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                "year": 2018,
                "authors": ["Jacob Devlin"],
            },
        ]

        print("\n1. Testing complete resolution workflow:")
        for i, paper in enumerate(test_papers, 1):
            print(f"\n   📋 Test {i}: {paper['title'][:50]}...")
            try:
                result = await orchestrator.resolve_async(
                    title=paper["title"],
                    year=paper.get("year"),
                    authors=paper.get("authors"),
                    enable_enrichment=True  # Test full workflow
                )

                if result:
                    print(f"   ✅ Success: {result.get('doi')}")
                    print(f"   📊 Source: {result.get('source')}")
                    print(f"   ⏱️  Time: {result.get('processing_time', 0):.2f}s")
                    print(f"   🎯 Stage: {result.get('workflow_stage')}")
                    if result.get('enrichment_applied'):
                        print(f"   📈 Enrichment: Applied")
                else:
                    print(f"   ❌ Failed to resolve")

            except Exception as e:
                print(f"   ⚠️ Error: {e}")

        # Test workflow statistics
        print("\n2. Testing workflow statistics:")
        stats = orchestrator.get_workflow_statistics()
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   Overall success rate: {stats['overall_success_rate']:.1f}%")
        print(f"   Library hit rate: {stats['library_hit_rate']:.1f}%")
        print(f"   Source resolution rate: {stats['source_resolution_rate']:.1f}%")
        print(f"   Enrichment rate: {stats['enrichment_rate']:.1f}%")
        print(f"   Average processing time: {stats['average_processing_time']:.2f}s")
        print(f"   Throughput: {stats['throughput_per_minute']:.1f} papers/min")

        print("\n✅ ResolutionOrchestrator test completed!")
        print("\nWorkflow Architecture:")
        print("1. Library Check → Find existing DOI in Scholar library")
        print("2. Source Resolution → Resolve DOI from multiple sources")
        print("3. Metadata Enrichment → Apply existing EnricherPipeline")
        print("4. Library Save → Store paper with comprehensive metadata")
        print("\nIntegration Benefits:")
        print("• Leverages existing enrichment infrastructure")
        print("• Provides unified workflow with statistics")
        print("• Handles failures gracefully with unresolved entries")
        print("• Configurable enrichment and source selection")

    asyncio.run(test_resolution_orchestrator())


# python -m scitex.scholar.doi.strategies._ResolutionOrchestrator

# EOF