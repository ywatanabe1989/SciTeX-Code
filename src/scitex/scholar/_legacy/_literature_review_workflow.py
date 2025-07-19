#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:15:00 (ywatanabe)"
# File: src/scitex_scholar/literature_review_workflow.py

"""
Integrated literature review workflow.

This module combines paper acquisition, indexing, and semantic search
for comprehensive literature review capabilities.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import json

from ._paper_acquisition import PaperAcquisition, PaperMetadata
from ._vector_search_engine import VectorSearchEngine
from ._document_indexer import DocumentIndexer
from ._search_engine import SearchEngine

logger = logging.getLogger(__name__)


class LiteratureReviewWorkflow:
    """
    Complete workflow for literature review including:
    - Paper discovery from multiple sources
    - Automated downloading
    - Vector indexing
    - Semantic search and analysis
    """
    
    def __init__(self, 
                 workspace_dir: Path = None,
                 email: str = None):
        """
        Initialize literature review workflow.
        
        Args:
            workspace_dir: Directory for all data
            email: Email for API compliance
        """
        self.workspace_dir = workspace_dir or Path("./literature_review_workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-directories
        self.papers_dir = self.workspace_dir / "papers"
        self.index_dir = self.workspace_dir / "index"
        self.vector_db_dir = self.workspace_dir / "vector_db"
        self.metadata_dir = self.workspace_dir / "metadata"
        
        for dir_path in [self.papers_dir, self.index_dir, self.vector_db_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.acquisition = PaperAcquisition(download_dir=self.papers_dir, email=email)
        self.search_engine = SearchEngine()
        self.vector_engine = VectorSearchEngine(db_path=str(self.vector_db_dir))
        self.indexer = DocumentIndexer(self.search_engine)
        
        # Track workflow state
        self.state_file = self.workspace_dir / "workflow_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load workflow state."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'searches': [],
            'downloaded_papers': {},
            'indexed_papers': set(),
            'created_at': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save workflow state."""
        # Convert sets to lists for JSON serialization
        state_to_save = self.state.copy()
        if isinstance(state_to_save.get('indexed_papers'), set):
            state_to_save['indexed_papers'] = list(state_to_save['indexed_papers'])
        
        with open(self.state_file, 'w') as f:
            json.dump(state_to_save, f, indent=2)
    
    async def discover_papers(self,
                            query: str,
                            sources: List[str] = None,
                            max_results: int = 20,
                            start_year: Optional[int] = None) -> List[PaperMetadata]:
        """
        Discover papers from multiple sources.
        
        Args:
            query: Search query
            sources: Sources to search
            max_results: Maximum results per source
            start_year: Filter by start year
            
        Returns:
            List of discovered papers
        """
        logger.info(f"Discovering papers for query: {query}")
        
        # Search papers
        papers = await self.acquisition.search(
            query=query,
            sources=sources,
            max_results=max_results,
            start_year=start_year
        )
        
        # Save search metadata
        search_record = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'sources': sources or ['all'],
            'results_count': len(papers),
            'papers': [p.to_dict() for p in papers]
        }
        
        self.state['searches'].append(search_record)
        self._save_state()
        
        # Save detailed metadata
        metadata_file = self.metadata_dir / f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(search_record, f, indent=2)
        
        logger.info(f"Discovered {len(papers)} papers")
        return papers
    
    async def acquire_papers(self,
                           papers: List[PaperMetadata],
                           skip_existing: bool = True) -> Dict[str, Path]:
        """
        Download papers that are freely available.
        
        Args:
            papers: Papers to download
            skip_existing: Skip already downloaded papers
            
        Returns:
            Mapping of titles to file paths
        """
        logger.info(f"Acquiring {len(papers)} papers...")
        
        # Filter papers to download
        to_download = []
        for paper in papers:
            if skip_existing and paper.title in self.state['downloaded_papers']:
                logger.info(f"Skipping existing: {paper.title}")
                continue
            to_download.append(paper)
        
        # Download papers
        downloaded = await self.acquisition.batch_download(to_download)
        
        # Update state
        for title, path in downloaded.items():
            self.state['downloaded_papers'][title] = str(path)
        self._save_state()
        
        logger.info(f"Successfully downloaded {len(downloaded)} papers")
        return downloaded
    
    async def index_papers(self, 
                         paper_paths: Optional[List[Path]] = None,
                         force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index papers for vector search.
        
        Args:
            paper_paths: Specific papers to index (None = all)
            force_reindex: Force reindexing
            
        Returns:
            Indexing statistics
        """
        logger.info("Indexing papers for vector search...")
        
        # Determine papers to index
        if paper_paths is None:
            # Index all papers in directory
            paper_paths = list(self.papers_dir.glob("*.pdf"))
        
        # Filter already indexed unless forcing
        if not force_reindex:
            paper_paths = [p for p in paper_paths if str(p) not in self.state['indexed_papers']]
        
        if not paper_paths:
            logger.info("No new papers to index")
            return {'indexed': 0}
        
        # Index with standard indexer first
        stats = await self.indexer.index_documents(
            paths=[self.papers_dir],
            patterns=['*.pdf'],
            force_reindex=force_reindex
        )
        
        # Add to vector database
        indexed_count = 0
        for doc_id, doc_data in self.search_engine.documents.items():
            if doc_id not in self.state['indexed_papers'] or force_reindex:
                success = self.vector_engine.add_document(
                    doc_id=doc_id,
                    content=doc_data['content'],
                    metadata=doc_data['metadata'],
                    paper_data=doc_data.get('processed')
                )
                if success:
                    indexed_count += 1
                    if isinstance(self.state['indexed_papers'], list):
                        self.state['indexed_papers'] = set(self.state['indexed_papers'])
                    self.state['indexed_papers'].add(doc_id)
        
        self._save_state()
        
        stats['vector_indexed'] = indexed_count
        logger.info(f"Indexed {indexed_count} papers into vector database")
        
        return stats
    
    async def search_literature(self,
                              query: str,
                              search_type: str = 'hybrid',
                              n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search indexed literature using vector search.
        
        Args:
            query: Search query
            search_type: Type of search (semantic/chunk/hybrid)
            n_results: Number of results
            
        Returns:
            Search results with metadata
        """
        results = self.vector_engine.search(
            query=query,
            search_type=search_type,
            n_results=n_results,
            expand_query=True
        )
        
        # Format results
        formatted = []
        for result in results:
            formatted.append({
                'title': result.metadata.get('title', 'Unknown'),
                'authors': result.metadata.get('authors', []),
                'year': result.metadata.get('year', ''),
                'score': result.score,
                'path': result.metadata.get('file_path', ''),
                'highlights': result.highlights,
                'methods': result.metadata.get('methods', []),
                'datasets': result.metadata.get('datasets', [])
            })
        
        return formatted
    
    async def find_research_gaps(self, topic: str) -> Dict[str, Any]:
        """
        Analyze research gaps in a topic area.
        
        Args:
            topic: Research topic
            
        Returns:
            Analysis of potential research gaps
        """
        # Search for papers on the topic
        papers = self.search_literature(topic, n_results=50)
        
        # Analyze methods and datasets used
        all_methods = set()
        all_datasets = set()
        year_distribution = {}
        
        for paper in papers:
            all_methods.update(paper.get('methods', []))
            all_datasets.update(paper.get('datasets', []))
            
            year = paper.get('year', 'Unknown')
            year_distribution[year] = year_distribution.get(year, 0) + 1
        
        # Identify potential gaps
        common_methods = ['CNN', 'LSTM', 'Transformer', 'SVM', 'Random Forest']
        common_datasets = ['MNIST', 'ImageNet', 'CIFAR', 'COCO']
        
        unused_methods = set(common_methods) - all_methods
        unused_datasets = set(common_datasets) - all_datasets
        
        # Temporal analysis
        recent_years = sorted([y for y in year_distribution.keys() if y.isdigit()])[-3:]
        recent_focus = sum(year_distribution.get(y, 0) for y in recent_years)
        
        return {
            'topic': topic,
            'papers_analyzed': len(papers),
            'methods_used': sorted(list(all_methods)),
            'datasets_used': sorted(list(all_datasets)),
            'potential_unused_methods': sorted(list(unused_methods)),
            'potential_unused_datasets': sorted(list(unused_datasets)),
            'temporal_trend': {
                'increasing': recent_focus > len(papers) * 0.5,
                'recent_papers': recent_focus,
                'year_distribution': dict(sorted(year_distribution.items()))
            }
        }
    
    async def generate_review_summary(self, topic: str) -> str:
        """
        Generate a summary of literature on a topic.
        
        Args:
            topic: Research topic
            
        Returns:
            Formatted summary
        """
        # Search for papers
        papers = await self.search_literature(topic, n_results=20)
        
        # Analyze
        gaps = await self.find_research_gaps(topic)
        
        # Generate summary
        summary = f"""# Literature Review Summary: {topic}

## Overview
- Total papers analyzed: {len(papers)}
- Date range: {min(p['year'] for p in papers if p['year'])} - {max(p['year'] for p in papers if p['year'])}

## Key Papers
"""
        
        for i, paper in enumerate(papers[:5], 1):
            summary += f"\n{i}. **{paper['title']}**\n"
            summary += f"   - Authors: {', '.join(paper['authors'][:3])}\n"
            summary += f"   - Year: {paper['year']}\n"
            if paper['methods']:
                summary += f"   - Methods: {', '.join(paper['methods'])}\n"
        
        summary += f"\n## Research Landscape\n"
        summary += f"- Common methods: {', '.join(gaps['methods_used'][:10])}\n"
        summary += f"- Common datasets: {', '.join(gaps['datasets_used'][:10])}\n"
        
        if gaps['potential_unused_methods']:
            summary += f"\n## Potential Research Opportunities\n"
            summary += f"- Unexplored methods: {', '.join(gaps['potential_unused_methods'])}\n"
        
        summary += f"\n## Temporal Trends\n"
        if gaps['temporal_trend']['increasing']:
            summary += f"- This is an active area with {gaps['temporal_trend']['recent_papers']} recent papers\n"
        else:
            summary += f"- Research activity appears to be stable or declining\n"
        
        return summary
    
    async def full_review_pipeline(self,
                                 topic: str,
                                 sources: List[str] = None,
                                 max_papers: int = 50,
                                 start_year: int = None) -> Dict[str, Any]:
        """
        Execute complete literature review pipeline.
        
        Args:
            topic: Research topic
            sources: Paper sources
            max_papers: Maximum papers to process
            start_year: Start year filter
            
        Returns:
            Complete review results
        """
        logger.info(f"Starting full literature review for: {topic}")
        
        # 1. Discover papers
        papers = await self.discover_papers(
            query=topic,
            sources=sources,
            max_results=max_papers,
            start_year=start_year
        )
        
        # 2. Download available papers
        downloaded = await self.acquire_papers(papers)
        
        # 3. Index papers
        index_stats = await self.index_papers()
        
        # 4. Generate review
        summary = await self.generate_review_summary(topic)
        
        # 5. Find research gaps
        gaps = await self.find_research_gaps(topic)
        
        # Save summary
        summary_file = self.workspace_dir / f"review_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return {
            'topic': topic,
            'papers_found': len(papers),
            'papers_downloaded': len(downloaded),
            'papers_indexed': index_stats.get('vector_indexed', 0),
            'summary_path': str(summary_file),
            'research_gaps': gaps,
            'workspace': str(self.workspace_dir)
        }


# Convenience function
async def conduct_literature_review(topic: str, **kwargs) -> Dict[str, Any]:
    """Quick function to conduct a literature review."""
    workflow = LiteratureReviewWorkflow()
    return await workflow.full_review_pipeline(topic, **kwargs)


# EOF