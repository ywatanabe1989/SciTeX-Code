<!-- ---
!-- Timestamp: 2025-08-22 18:19:57
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/externals/impact_factor/README.md
!-- --- -->

# Impact Factor Calculator

A comprehensive, legally compliant impact factor calculation system using open APIs from OpenAlex, Crossref, and Semantic Scholar. This package provides transparent, verifiable impact factor calculations without relying on proprietary databases or restricted access systems.

## 🌟 Key Features

- **Legal & Transparent**: Uses only publicly available APIs and open data sources
- **Multi-Source Integration**: Combines data from OpenAlex, Crossref, and Semantic Scholar
- **Advanced Matching**: Sophisticated journal matching algorithms across data sources
- **Efficient Caching**: Intelligent caching system with configurable TTL and size limits
- **Batch Processing**: Support for bulk calculations with progress tracking
- **CLI Interface**: Full-featured command-line interface
- **Export Formats**: JSON, CSV, and human-readable output formats
- **Comprehensive Documentation**: Examples and detailed methodology explanations

## 📊 Impact Factor Calculation Methods

### 1. Classical 2-Year Impact Factor
```
IF = Citations in year Y to papers from years (Y-1) and (Y-2) / Papers published in years (Y-1) and (Y-2)
```

### 2. H-Index Based Impact Indicator
```  
H-IF = H-index / 10 (normalized)
```

### 3. Citation Per Paper Ratio
```
CPP = Total citations / Total papers (estimated for 2-year window)
```

### 4. Confidence Score
Based on data availability across sources (0.0 - 1.0 scale)

## 🚀 Installation

```bash
cd /path/to/this/package
pip install -e .
```

## 📈 Quick Start

### Basic Usage

```python
from impact_factor import ImpactFactorCalculator

# Initialize calculator
calculator = ImpactFactorCalculator()

# Calculate impact factor for a journal
result = calculator.calculate_impact_factor("Nature")

if 'error' not in result:
    impact_factors = result['impact_factors']
    print(f"Journal: {result['journal_name']}")
    print(f"Classical 2-year IF: {impact_factors['classical_2year']}")
    print(f"H-index based IF: {impact_factors['h_index_based']}")
    print(f"Confidence score: {impact_factors['confidence_score']}")
else:
    print(f"Error: {result['error']}")
```

### Batch Processing

```python
# Calculate for multiple journals
journals = ["Nature", "Science", "Cell", "PLOS ONE"]
results = calculator.batch_calculate(journals)

for result in results:
    if 'error' not in result:
        name = result['journal_name']
        if_value = result['impact_factors']['classical_2year']
        print(f"{name}: {if_value}")
```

## 🖥️ Command Line Interface

### Single Journal Calculation
```bash
# Basic calculation
python -m impact_factor.cli calculate "Nature"

# Specify year and output format
python -m impact_factor.cli calculate "Nature" --year 2022 --format json

# Save to file
python -m impact_factor.cli calculate "Nature" --output results.json
```

### Batch Processing
```bash
# Multiple journals
python -m impact_factor.cli batch --journals "Nature" "Science" "Cell"

# From file (supports .txt, .csv, .json)
python -m impact_factor.cli batch --file journals.txt --format csv

# Export results
python -m impact_factor.cli batch --file journals.txt --output results.csv --format csv
```

### Cache Management
```bash
# View cache statistics
python -m impact_factor.cli cache stats

# Clear all cache
python -m impact_factor.cli cache clear

# Clean up expired entries
python -m impact_factor.cli cache cleanup

# List cache entries
python -m impact_factor.cli cache list
```

### Journal Search
```bash
# Search for journal information
python -m impact_factor.cli search "Journal of Biological Chemistry"

# JSON output
python -m impact_factor.cli search "Nature" --format json
```

### Demo Mode
```bash
# Run demonstration with sample journals
python -m impact_factor.cli demo

# Export demo results
python -m impact_factor.cli demo --output demo_results.csv --format csv
```

## 🔧 Advanced Configuration

### Custom Cache Configuration
```python
from impact_factor import ImpactFactorCalculator

calculator = ImpactFactorCalculator(
    cache_dir="/path/to/cache",
    default_ttl=3600 * 24,  # 1 day
    max_cache_size_mb=100
)
```

### Direct API Usage
```python
from impact_factor.fetchers import OpenAlexFetcher, CrossrefFetcher, SemanticScholarFetcher

# Use individual fetchers
openalex = OpenAlexFetcher()
journals = openalex.fetch_all_journals(limit=100)

crossref = CrossrefFetcher()
journals = crossref.fetch_all_journals(limit=100)

semantic_scholar = SemanticScholarFetcher()
metrics = semantic_scholar.get_journal_metrics_from_papers("Nature")
```

### Advanced Journal Matching
```python
from impact_factor import JournalMatcher

matcher = JournalMatcher()

# Find best match across data sources
journal_lists = {
    'openalex': openalex_journals,
    'crossref': crossref_journals
}

name_fields = {
    'openalex': 'display_name',
    'crossref': 'title'
}

matches = matcher.find_multiple_matches(
    "Journal of Biological Chemistry",
    journal_lists,
    name_fields
)
```

## 📚 Data Sources

| Source | Description | Data Available |
|--------|-------------|----------------|
| **OpenAlex** | Open catalog of scholarly works | Journal metadata, citation counts, h-index, publication counts |
| **Crossref** | DOI registration agency | Publisher info, ISSN, publication metadata |
| **Semantic Scholar** | AI-powered research database | Paper-level citations, venue information |

### API Rate Limits
- **OpenAlex**: 100,000 requests/day, 10 per second
- **Crossref**: 50 requests/second (polite usage)  
- **Semantic Scholar**: 100 requests per query

## 📁 Example Files

### Input File Formats

**journals.txt**
```
Nature
Science  
Cell
PLOS ONE
```

**journals.csv**
```csv
Journal Name,Field
Nature,Multidisciplinary
Science,Multidisciplinary
Cell,Cell Biology
```

**journals.json**
```json
{
  "journals": [
    "Nature",
    "Science",
    "Cell"
  ]
}
```

## 🎯 Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: Fundamental operations and API usage
- `advanced_usage.py`: Advanced features, caching, bulk processing

Run examples:
```bash
python src/impact_factor/examples/basic_usage.py
python src/impact_factor/examples/advanced_usage.py
```

## 📊 Output Formats

### JSON Output
```json
{
  "journal_name": "Nature",
  "calculation_year": 2023,
  "impact_factors": {
    "classical_2year": 49.962,
    "h_index_based": 39.8,
    "citation_per_paper": 52.3,
    "confidence_score": 1.0
  },
  "journal_data": {
    "openalex": {...},
    "crossref": {...},
    "semantic_scholar": {...}
  },
  "methodology": {...}
}
```

### CSV Output
```csv
Journal Name,Classical 2-Year IF,H-Index Based,Citation Per Paper,Confidence Score,Data Sources
Nature,49.962,39.8,52.3,1.0,openalex|crossref|semantic_scholar
Science,47.728,35.2,48.9,0.9,openalex|crossref
```

## ⚖️ Legal Compliance

This package is designed to be legally compliant:

- ✅ Uses only publicly available APIs
- ✅ Respects API rate limits and terms of service
- ✅ Transparent calculation methodologies
- ✅ No proprietary data or restricted access required
- ✅ Open source with MIT license

## 🛠️ Development

### Running Tests
```bash
# Run individual component demonstrations
python -m impact_factor.core.calculator
python -m impact_factor.core.journal_matcher
python -m impact_factor.core.cache_manager

# Run fetcher demonstrations
python -m impact_factor.fetchers.OpenAlexFetcher
python -m impact_factor.fetchers.CrossrefFetcher
python -m impact_factor.fetchers.SemanticScholarFetcher
```

### Package Structure
```
src/impact_factor/
├── core/
│   ├── calculator.py          # Main impact factor calculation engine
│   ├── journal_matcher.py     # Advanced journal matching algorithms
│   ├── cache_manager.py       # Caching system
│   └── __init__.py
├── fetchers/
│   ├── OpenAlexFetcher.py     # OpenAlex API integration
│   ├── CrossrefFetcher.py     # Crossref API integration
│   ├── SemanticScholarFetcher.py  # Semantic Scholar API integration
│   └── __init__.py
├── examples/
│   ├── basic_usage.py         # Basic usage examples
│   ├── advanced_usage.py      # Advanced features demo
│   └── __init__.py
├── cli.py                     # Command-line interface
└── __init__.py               # Package initialization
```

## 📄 License

MIT License - This project is open source and free to use for academic and commercial purposes.

## 🤝 Contributing

Contributions welcome! Please ensure:
- Legal compliance with API terms of service
- Respect for rate limits
- Clear documentation of calculation methods
- Comprehensive testing

## 📞 Support

For questions or issues, please contact the SciTeX team or create an issue in the repository.

---

**Note**: Impact factor calculations are estimates based on publicly available data and may differ from official Journal Citation Reports (JCR) impact factors. Use for research and comparison purposes.

# EOF

<!-- EOF -->