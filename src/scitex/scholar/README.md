# SciTeX Scholar - Unified Literature Management

The SciTeX Scholar module provides a unified, easy-to-use interface for scientific literature search, enrichment, and management. The new `Scholar` class consolidates all functionality into a single entry point with method chaining support.

## Quick Start

```python
from scitex.scholar import Scholar

# Initialize with smart defaults
scholar = Scholar(email="researcher@university.edu")

# Simple search with automatic enrichment
papers = scholar.search("deep learning neuroscience")

# Method chaining for complex workflows
high_impact = scholar.search("machine learning") \
                    .filter(year_min=2020, min_citations=10) \
                    .sort_by("impact_factor") \
                    .save("high_impact_papers.bib")
```

## Key Features

### 🎯 Single Entry Point
- One class (`Scholar`) for all literature management tasks
- Replaces the scattered API of multiple classes and functions
- Smart defaults with automatic configuration detection

### ⛓️ Method Chaining
- Fluent interface for readable, chainable operations
- Natural workflow: search → filter → sort → export
- All operations return collections for further processing

### 🔄 Automatic Enrichment
- Journal metrics (impact factor, quartile) added by default
- Can be disabled with `enrich_by_default=False`
- Uses comprehensive journal database

### 📊 Built-in Analysis
- Trend analysis across paper collections
- Export to multiple formats (BibTeX, CSV, JSON)
- Convert to pandas DataFrame for advanced analysis

### 🤖 AI Integration (Optional)
- Research gap identification
- Literature summaries
- Paper recommendations
- Supports multiple AI providers

## Core Classes

### Scholar Class

The main interface for all operations:

```python
class Scholar:
    def __init__(self,
                 email=None,                    # Auto-detected from env
                 api_keys=None,                 # Dict of API keys
                 enrich_by_default=True,        # Auto-enrich with metrics
                 download_dir=None,             # PDF download location
                 ai_provider=None):             # Optional AI provider
```

**Key Methods:**
- `search(query, limit=20, **filters)` - Search papers with enrichment
- `search_multiple(queries, papers_per_query=10)` - Batch search
- `quick_search(query, top_n=5)` - Returns just titles
- `get_recommendations(paper_title, limit=10)` - Related papers

### PaperCollection Class

Container for search results with chainable methods:

```python
# Filtering
.filter(year_min=2020, min_citations=10, open_access_only=True)

# Sorting
.sort_by("citations" | "year" | "impact_factor" | "title")

# Analysis
.analyze_trends()           # Statistical analysis
.find_gaps(topic)          # AI-powered gap analysis
.summary()                 # Text summary

# Export
.save("papers.bib", format="bibtex" | "csv" | "json")
.to_dataframe()            # Convert to pandas
.download_pdfs()           # Download available PDFs
```

## Usage Examples

### Basic Search and Filter

```python
# Search recent high-impact papers
papers = scholar.search("CRISPR gene editing") \
               .filter(year_min=2021, impact_factor_min=10) \
               .sort_by("citations")

print(f"Found {len(papers)} high-impact CRISPR papers")
print(papers.summary())
```

### Multi-Topic Literature Review

```python
# Comprehensive literature review
topics = [
    "machine learning drug discovery",
    "AI pharmaceutical research", 
    "deep learning molecular design"
]

all_papers = scholar.search_multiple(topics, papers_per_query=20)

# Analyze and export
trends = all_papers.analyze_trends()
all_papers.save("drug_discovery_ai.bib")

# AI analysis (if configured)
gaps = all_papers.find_gaps("AI in drug discovery")
for gap in gaps[:3]:
    print(f"• {gap}")
```

### PDF Download and Analysis

```python
# Find and download open access papers
oa_papers = scholar.search("neural networks brain imaging") \
                  .filter(open_access_only=True, year_min=2020) \
                  .download_pdfs(max_concurrent=3)

# Convert to DataFrame for analysis
df = oa_papers.to_dataframe()
print(df.groupby('year')['citation_count'].mean())
```

### Context Manager Usage

```python
# Automatic resource management
with Scholar(ai_provider="anthropic") as s:
    papers = s.search("quantum machine learning", limit=10)
    gaps = papers.find_gaps("quantum ML applications")
    papers.save("quantum_ml.bib")
```

## Configuration

### Environment Variables

The Scholar class automatically detects configuration from environment variables:

```bash
# API Keys
export SEMANTIC_SCHOLAR_API_KEY="your_s2_key"
export OPENAI_API_KEY="your_openai_key"
export ENTREZ_EMAIL="your.email@example.com"

# Directories
export SCHOLAR_DOWNLOAD_DIR="./papers"
export SCHOLAR_CACHE_DIR="./cache"
```

### API Key Setup

```python
# Manual API key configuration
scholar = Scholar(
    api_keys={
        's2': 'your_semantic_scholar_key',
        'openai': 'your_openai_key'
    },
    ai_provider='openai'
)
```

## Data Sources

The Scholar class searches multiple databases:

1. **Semantic Scholar** (primary) - 200M+ papers with citation data
2. **PubMed** - Biomedical literature with abstracts
3. **arXiv** - Preprints with full text access
4. **bioRxiv** - Biology preprints (limited)

Results are automatically deduplicated and ranked by relevance.

## Export Formats

### BibTeX (Default)
```python
papers.save("papers.bib")  # Enriched with journal metrics
```

### CSV for Analysis
```python
papers.save("papers.csv", format="csv")
# Columns: title, authors, year, journal, citations, impact_factor, etc.
```

### JSON for Processing
```python
papers.save("papers.json", format="json")
# Structured data with all metadata
```

### pandas DataFrame
```python
df = papers.to_dataframe()
# Ready for statistical analysis, plotting, etc.
```

## Migration from Legacy API

### Old Way (Multiple Classes)
```python
# Old scattered approach
from scitex.scholar import PaperAcquisition, PaperEnrichmentService
from scitex.scholar import generate_enriched_bibliography

acquisition = PaperAcquisition(email="user@example.com")
papers = await acquisition.search("topic", max_results=20)
enricher = PaperEnrichmentService()
enriched = enricher.enrich_papers(papers)
generate_enriched_bibliography(enriched, "output.bib")
```

### New Way (Unified Interface)
```python
# New unified approach
from scitex.scholar import Scholar

scholar = Scholar(email="user@example.com")
papers = scholar.search("topic", limit=20).save("output.bib")
```

## Performance Tips

1. **Use `enrich_by_default=False`** for large searches if you don't need journal metrics
2. **Set reasonable limits** - start with 20-50 papers for exploration
3. **Use filters early** - filter by year, citations, etc. to reduce data
4. **Batch operations** - use `search_multiple()` for related topics
5. **Cache results** - enable caching for repeated searches

## Error Handling

The Scholar class handles common errors gracefully:

```python
try:
    papers = scholar.search("nonexistent topic")
    if not papers:
        print("No papers found")
except Exception as e:
    print(f"Search failed: {e}")
```

## Advanced Features

### Research Trend Analysis
```python
trends = papers.analyze_trends()
# Returns: yearly distribution, top journals, citation stats, etc.
```

### AI-Powered Gap Analysis
```python
gaps = papers.find_gaps("research topic")
# Returns: list of identified research opportunities
```

### Citation Network Analysis
```python
# Get papers that cite a specific paper
recommendations = scholar.get_recommendations("paper title")
```

## Backward Compatibility

All legacy functions remain available for existing code:

```python
# Legacy imports still work
from scitex.scholar import PaperAcquisition, SemanticScholarClient
from scitex.scholar import search_papers, generate_enriched_bibliography

# But new code should use:
from scitex.scholar import Scholar
```

## Requirements

- Python 3.8+
- Required: `aiohttp`, `pandas`, `pathlib`
- Optional: `scitex.ai` for AI features
- Optional: API keys for enhanced functionality

## Support

- 📖 Full documentation: [examples/scholar/scholar_tutorial_new.ipynb]
- 🚀 Quick demo: [examples/scholar/simple_scholar_demo.py]
- 🐛 Issues: Create bug reports in project management
- 💡 Feature requests: Follow project guidelines

---

The unified Scholar interface makes literature management intuitive and powerful, replacing complex multi-class workflows with simple, chainable operations.