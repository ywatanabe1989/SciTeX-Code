# Scholar Search Engine Architecture Proposal

## Current State
All search engines are currently in a single file: `_SearchEngines.py` (1100+ lines)

## Proposed Architecture

### 1. Base Engine Interface
Create `_base_engine.py`:
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .._Paper import Paper

class BaseSearchEngine(ABC):
    """Base interface for all search engines."""
    
    def __init__(self, name: str, rate_limit: float = 0.1):
        self.name = name
        self.rate_limit = rate_limit
        self._last_request = 0
    
    @abstractmethod
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search for papers. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _parse_response(self, data: Any) -> List[Paper]:
        """Parse API response into Paper objects."""
        pass
    
    async def _rate_limit(self):
        """Enforce rate limiting."""
        # Common implementation
```

### 2. Separate Engine Files
- `engines/pubmed.py` - PubMedEngine
- `engines/semantic_scholar.py` - SemanticScholarEngine  
- `engines/arxiv.py` - ArxivEngine
- `engines/crossref.py` - CrossRefEngine
- `engines/google_scholar.py` - GoogleScholarEngine
- `engines/local.py` - LocalSearchEngine
- `engines/vector.py` - VectorSearchEngine

### 3. Benefits
1. **Modularity**: Each engine in its own file (~150-200 lines)
2. **Testability**: Easier to test individual engines
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new engines
5. **Type Safety**: Consistent interface enforced by base class

### 4. Example Implementation
```python
# engines/crossref.py
from typing import List, Dict, Any, Optional
import aiohttp
from .._base_engine import BaseSearchEngine
from ..._Paper import Paper
from ...errors import SearchError

class CrossRefEngine(BaseSearchEngine):
    """CrossRef search engine for academic papers."""
    
    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        super().__init__("crossref", rate_limit=0.5)
        self.api_key = api_key
        self.email = email or "research@example.com"
        self.base_url = "https://api.crossref.org/works"
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search CrossRef for papers."""
        await self._rate_limit()
        # Implementation...
        
    def _parse_response(self, data: Dict[str, Any]) -> List[Paper]:
        """Parse CrossRef API response."""
        # Implementation...
```

### 5. Migration Path
1. Create base engine class
2. Move engines one by one to separate files
3. Update imports in UnifiedSearcher
4. Add comprehensive tests for each engine
5. Deprecate old _SearchEngines.py

## Decision
This would improve code organization significantly, but requires careful migration to avoid breaking existing functionality.