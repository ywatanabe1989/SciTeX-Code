<!-- ---
!-- Timestamp: 2025-07-19 09:48:11
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/STRUCTURE_MIGRATION.md
!-- --- -->

## Reorganized Scholar Package Structure

```
src/scitex/scholar/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── scholar.py
│   ├── paper.py
│   └── collections.py
├── search/
│   ├── __init__.py
│   ├── local.py
│   ├── vector.py
│   └── engines.py
├── sources/
│   ├── __init__.py
│   ├── semantic_scholar.py
│   ├── pubmed.py
│   └── acquisition.py
├── processing/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── latex_parser.py
│   └── text_processor.py
├── enrichment/
│   ├── __init__.py
│   ├── journal_metrics.py
│   └── enrichment.py
├── utils/
│   ├── __init__.py
│   ├── downloader.py
│   └── bibliography.py
└── interfaces/
    ├── __init__.py
    └── mcp_server.py
```

## Key File Consolidations

1. `_paper.py` + `_paper_enhanced.py` → `core/paper.py`
2. `_scholar.py` + `scholar.py` → `core/scholar.py`
3. `_vector_search.py` + `_vector_search_engine.py` → `search/vector.py`
4. `_semantic_scholar_client.py` → `sources/semantic_scholar.py`
5. `_scientific_pdf_parser.py` → `processing/pdf_parser.py`
6. `_journal_metrics.py` + `_impact_factor_integration.py` → `enrichment/journal_metrics.py`
7. `_mcp_server.py` + `_mcp_vector_server.py` → `interfaces/mcp_server.py`

## Main __init__.py

File: `src/scitex/scholar/__init__.py`

```python
"""SciTeX Scholar - Scientific Literature Management"""

from .core.scholar import Scholar
from .core.collections import PaperCollection  
from .core.paper import Paper
from .search.local import LocalSearchEngine
from .utils.downloader import PDFDownloader
from .utils.bibliography import build_index

__all__ = [
    "Scholar",
    "PaperCollection", 
    "Paper",
    "LocalSearchEngine",
    "PDFDownloader",
    "build_index",
]
```

## Core Scholar Interface

File: `src/scitex/scholar/core/scholar.py`

```python
"""Unified Scholar interface"""

import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Union
from .collections import PaperCollection
from .paper import Paper
from ..sources.acquisition import PaperAcquisition

class Scholar:
    def __init__(self, 
                 email: Optional[str] = None,
                 download_dir: Optional[Path] = None,
                 enrich_by_default: bool = True):
        self.email = email
        self.download_dir = download_dir or Path("./papers")
        self.enrich_by_default = enrich_by_default
        self.acquisition = PaperAcquisition(
            download_dir=self.download_dir,
            email=self.email
        )

    def search(self, 
               query: str,
               limit: int = 20,
               sources: Union[str, List[str]] = 'semantic_scholar') -> PaperCollection:
        papers = asyncio.run(self._search_async(query, limit, sources))
        collection = PaperCollection(papers, self)
        if self.enrich_by_default:
            collection = collection.enrich()
        return collection

    async def _search_async(self, query: str, limit: int, sources) -> List[Paper]:
        if isinstance(sources, str):
            sources = [sources]
        results = await self.acquisition.search(query, sources, limit)
        return [self._metadata_to_paper(result) for result in results]

    def _metadata_to_paper(self, metadata) -> Paper:
        return Paper(
            title=metadata.title,
            authors=metadata.authors,
            abstract=metadata.abstract,
            source=metadata.source,
            year=metadata.year,
            doi=metadata.doi
        )
```

## Paper Collections

File: `src/scitex/scholar/core/collections.py`

```python
"""Paper collection with filtering and analysis"""

from typing import List, Iterator, Union, Optional, Dict, Any
from pathlib import Path
from .paper import Paper

class PaperCollection:
    def __init__(self, papers: List[Paper], scholar_instance=None):
        self._papers = papers
        self._scholar = scholar_instance
        self._enriched = False

    def __len__(self) -> int:
        return len(self._papers)

    def __iter__(self) -> Iterator[Paper]:
        return iter(self._papers)

    def __getitem__(self, index) -> Union[Paper, 'PaperCollection']:
        if isinstance(index, slice):
            return PaperCollection(self._papers[index], self._scholar)
        return self._papers[index]

    def filter(self,
               year_min: Optional[int] = None,
               min_citations: Optional[int] = None,
               open_access_only: bool = False) -> 'PaperCollection':
        filtered = []
        for paper in self._papers:
            if year_min and paper.year and int(paper.year) < year_min:
                continue
            if min_citations and paper.citation_count < min_citations:
                continue
            if open_access_only and not paper.pdf_url:
                continue
            filtered.append(paper)
        return PaperCollection(filtered, self._scholar)

    def sort_by(self, field: str = "citations", reverse: bool = True) -> 'PaperCollection':
        def get_key(paper):
            if field == "citations":
                return paper.citation_count or 0
            elif field == "year":
                return int(paper.year) if paper.year else 0
            return paper.title.lower()
        
        sorted_papers = sorted(self._papers, key=get_key, reverse=reverse)
        return PaperCollection(sorted_papers, self._scholar)

    def enrich(self) -> 'PaperCollection':
        if not self._enriched:
            from ..enrichment.enrichment import PaperEnrichmentService
            enricher = PaperEnrichmentService()
            self._papers = enricher.enrich_papers(self._papers)
            self._enriched = True
        return self

    def save(self, filename: Union[str, Path], format_type: str = "bibtex") -> Path:
        output_path = Path(filename)
        if format_type == "bibtex":
            content = "\n\n".join(paper.to_bibtex() for paper in self._papers)
            output_path.write_text(content, encoding='utf-8')
        return output_path
```

## Simplified Paper Model

File: `src/scitex/scholar/core/paper.py`

```python
"""Enhanced Paper model"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

class Paper:
    def __init__(self,
                 title: str,
                 authors: List[str],
                 abstract: str,
                 source: str,
                 year: Optional[int] = None,
                 doi: Optional[str] = None,
                 journal: Optional[str] = None,
                 citation_count: Optional[int] = None,
                 pdf_url: Optional[str] = None,
                 impact_factor: Optional[float] = None):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.source = source
        self.year = year
        self.doi = doi
        self.journal = journal
        self.citation_count = citation_count
        self.pdf_url = pdf_url
        self.impact_factor = impact_factor
        self.retrieved_at = datetime.now()

    def to_bibtex(self) -> str:
        first_author = self.authors[0].split()[-1].lower() if self.authors else "unknown"
        year = self.year or "0000"
        key = f"{first_author}{year}"
        
        lines = [f"@article{{{key},"]
        lines.append(f'  title = {{{self.title}}},')
        
        if self.authors:
            authors_str = " and ".join(self.authors)
            lines.append(f'  author = {{{authors_str}}},')
        
        if self.year:
            lines.append(f'  year = {{{self.year}}},')
        
        if self.journal:
            lines.append(f'  journal = {{{self.journal}}},')
        
        if self.doi:
            lines.append(f'  doi = {{{self.doi}}},')
        
        if self.citation_count:
            lines.append(f'  note = {{Citations: {self.citation_count}}},')
        
        lines.append("}")
        return "\n".join(lines)

    def get_identifier(self) -> str:
        if self.doi:
            return f"doi:{self.doi}"
        import hashlib
        content = f"{self.title}_{';'.join(self.authors)}"
        return f"hash:{hashlib.md5(content.encode()).hexdigest()[:12]}"

File: `src/scitex/scholar/search/local.py`

```python
"""Local file search engine"""

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import json
import re
from datetime import datetime
from ..core.paper import Paper

class LocalSearchEngine:
    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path
        self.metadata_cache: Dict[str, Dict[str, Any]] = {}
        if self.index_path and self.index_path.exists():
            self._load_cache()

    def search(self, 
               query: str,
               paths: List[Path],
               max_results: Optional[int] = None) -> List[Tuple[Paper, float]]:
        results = []
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        pdf_files = []
        for path in paths:
            if path.is_file():
                pdf_files.append(path)
            else:
                pdf_files.extend(path.rglob("*.pdf"))
        
        for pdf_path in pdf_files:
            metadata = self._get_pdf_metadata(pdf_path)
            if not metadata:
                continue
                
            score = self._calculate_relevance(query_lower, query_terms, metadata)
            if score > 0:
                paper = self._create_paper_from_metadata(pdf_path, metadata)
                results.append((paper, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        if max_results:
            results = results[:max_results]
        return results

    def _get_pdf_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        cache_key = str(pdf_path.absolute())
        if cache_key in self.metadata_cache:
            return self.metadata_cache[cache_key]
        
        metadata = self._extract_pdf_metadata(pdf_path)
        if metadata:
            self.metadata_cache[cache_key] = metadata
        return metadata

    def _extract_pdf_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        metadata = {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "title": pdf_path.stem.replace("_", " ").replace("-", " "),
            "content": pdf_path.stem.replace("_", " ").replace("-", " ")
        }
        
        try:
            import fitz
            with fitz.open(pdf_path) as doc:
                info = doc.metadata
                metadata["title"] = info.get("title", "") or pdf_path.stem
                metadata["author"] = info.get("author", "")
                
                text_parts = []
                for page_idx in range(min(3, len(doc))):
                    page = doc[page_idx]
                    text = page.get_text()
                    if text:
                        text_parts.append(text)
                metadata["content"] = " ".join(text_parts)[:5000]
        except ImportError:
            pass
        
        return metadata

    def _calculate_relevance(self, query_lower: str, query_terms: set, metadata: Dict[str, Any]) -> float:
        score = 0.0
        fields = [("title", 5.0), ("content", 1.0), ("filename", 1.0)]
        
        for field, weight in fields:
            field_value = metadata.get(field, "").lower()
            if not field_value:
                continue
            
            if query_lower in field_value:
                score += weight * 2
            
            field_terms = set(field_value.split())
            matching_terms = query_terms & field_terms
            if matching_terms:
                score += weight * len(matching_terms) / len(query_terms)
        
        return score

    def _create_paper_from_metadata(self, pdf_path: Path, metadata: Dict[str, Any]) -> Paper:
        authors = []
        author_str = metadata.get("author", "")
        if author_str:
            if ";" in author_str:
                authors = [a.strip() for a in author_str.split(";")]
            else:
                authors = [author_str.strip()]
        
        return Paper(
            title=metadata.get("title", pdf_path.stem),
            authors=authors,
            abstract=metadata.get("content", "")[:500],
            source="local"
        )

    def _load_cache(self):
        with open(self.index_path, "r") as file_:
            self.metadata_cache = json.load(file_)
```

File: `src/scitex/scholar/search/vector.py`

```python
"""Vector search engine"""

import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from ..core.paper import Paper

class VectorSearchEngine:
    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path
        self.papers: List[Paper] = []
        self.embeddings: Optional[np.ndarray] = None
        self.paper_ids: Dict[str, int] = {}
        self._embedding_model = None

    def _get_embedding_model(self):
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                self._embedding_model = "random"
        return self._embedding_model

    def _generate_embedding(self, text: str) -> np.ndarray:
        model = self._get_embedding_model()
        if model == "random":
            np.random.seed(hash(text) % 2**32)
            return np.random.randn(384).astype(np.float32)
        return model.encode(text, convert_to_numpy=True).astype(np.float32)

    def add_paper(self, paper: Paper):
        paper_id = paper.get_identifier()
        if paper_id in self.paper_ids:
            return
        
        text = f"{paper.title} {paper.abstract}"
        embedding = self._generate_embedding(text)
        
        self.papers.append(paper)
        self.paper_ids[paper_id] = len(self.papers) - 1
        
        if self.embeddings is None:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Paper, float]]:
        if not self.papers or self.embeddings is None:
            return []
        
        query_embedding = self._generate_embedding(query)
        similarities = self._calculate_similarities(query_embedding, self.embeddings)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            results.append((self.papers[idx], float(score)))
        return results

    def _calculate_similarities(self, query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        embeddings_norm = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
        return np.dot(embeddings_norm, query_norm)
```

## Sources Module

File: `src/scitex/scholar/sources/semantic_scholar.py`

```python
"""Semantic Scholar client"""

import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class S2Paper:
    paperId: str
    title: str
    abstract: Optional[str]
    year: Optional[int]
    authors: List[Dict[str, Any]]
    venue: Optional[str]
    citationCount: int
    doi: Optional[str]
    pdf_url: Optional[str] = None

    @property
    def author_names(self) -> List[str]:
        return [author.get('name', 'Unknown') for author in self.authors if author]

class SemanticScholarClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = None

    async def __aenter__(self):
        headers = {'User-Agent': 'SciTeX-Scholar/1.0'}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_papers(self, query: str, limit: int = 20) -> List[S2Paper]:
        if not self.session:
            raise RuntimeError("Client not initialized")

        url = f"{self.base_url}/paper/search"
        params = {
            'query': query,
            'limit': min(limit, 100),
            'fields': 'paperId,title,abstract,year,authors,venue,citationCount,doi,openAccessPdf'
        }

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                return []

            data = await response.json()
            papers = []
            
            for item in data.get('data', []):
                pdf_url = None
                if item.get('openAccessPdf'):
                    pdf_url = item['openAccessPdf'].get('url')

                paper = S2Paper(
                    paperId=item.get('paperId', ''),
                    title=item.get('title', ''),
                    abstract=item.get('abstract'),
                    year=item.get('year'),
                    authors=item.get('authors', []),
                    venue=item.get('venue'),
                    citationCount=item.get('citationCount', 0),
                    doi=item.get('doi'),
                    pdf_url=pdf_url
                )
                papers.append(paper)

            return papers
```

File: `src/scitex/scholar/sources/acquisition.py`

```python
"""Unified paper acquisition"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .semantic_scholar import SemanticScholarClient, S2Paper

@dataclass
class PaperMetadata:
    title: str
    authors: List[str]
    abstract: str
    year: Optional[str]
    doi: Optional[str]
    source: str
    citation_count: int = 0
    pdf_url: Optional[str] = None

class PaperAcquisition:
    def __init__(self, download_dir=None, email: Optional[str] = None):
        self.download_dir = download_dir
        self.email = email

    async def search(self, 
                    query: str, 
                    sources: List[str], 
                    max_results: int) -> List[PaperMetadata]:
        all_results = []
        
        if 'semantic_scholar' in sources:
            s2_results = await self._search_semantic_scholar(query, max_results)
            all_results.extend(s2_results)
        
        return self._deduplicate_results(all_results)

    async def _search_semantic_scholar(self, query: str, max_results: int) -> List[PaperMetadata]:
        async with SemanticScholarClient() as client:
            s2_papers = await client.search_papers(query, limit=max_results)
            return [self._s2_to_metadata(paper) for paper in s2_papers]

    def _s2_to_metadata(self, s2_paper: S2Paper) -> PaperMetadata:
        return PaperMetadata(
            title=s2_paper.title,
            authors=s2_paper.author_names,
            abstract=s2_paper.abstract or '',
            year=str(s2_paper.year) if s2_paper.year else None,
            doi=s2_paper.doi,
            source='semantic_scholar',
            citation_count=s2_paper.citationCount,
            pdf_url=s2_paper.pdf_url
        )

    def _deduplicate_results(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        unique_papers = []
        seen_dois = set()
        
        for paper in papers:
            if paper.doi and paper.doi in seen_dois:
                continue
            if paper.doi:
                seen_dois.add(paper.doi)
            unique_papers.append(paper)
        
        return unique_papers

<!-- EOF -->