# SciTeX Scholar Examples

This directory contains demonstration scripts showing how to use the SciTeX Scholar module for scientific literature management and analysis.

## Available Examples

### 1. Basic Scholar Example (`basic_scholar_example.py`)
Introduction to core scholar functionality:
- Creating Paper objects
- Using PDFDownloader
- Local search engine setup
- Building search indices

### 2. Quick Scholar Demo (`quick_scholar_demo.py`)
Simple demonstration of enhanced features:
- Literature search with journal metrics
- AI integration capabilities check
- Bibliography generation

### 3. Demo Literature Search (`demo_literature_search.py`)
Comprehensive literature search workflow:
- Multi-source paper search (PubMed, arXiv)
- PDF downloading
- Paper parsing and analysis
- Vector-based semantic search

### 4. Demo Enhanced Bibliography (`demo_enhanced_bibliography.py`)
Advanced bibliography management:
- Paper search with metadata
- Journal impact factor lookup
- Enhanced BibTeX generation
- Citation formatting

### 5. AI Research Assistant (`ai_research_assistant.py`)
Interactive AI-powered research assistant:
- Intelligent paper search
- AI-driven paper analysis
- Research insights generation

### 6. Enhanced Literature Review Demo (`enhanced_literature_review_demo.py`)
Complete literature review workflow:
- Comprehensive paper search
- Automatic metrics integration
- Citation network analysis
- Review document generation

### 7. GPAC Enhanced Search (`demo_gpac_enhanced_search.py`)
Specialized search for GPAC-related research:
- Targeted keyword search
- Domain-specific filtering
- Quick review generation

### 8. Working Literature System (`demo_working_literature_system.py`)
Production-ready literature management:
- Database integration
- Persistent storage
- Batch processing

### 9. Subscription Journal Workflow (`subscription_journal_workflow.py`)
Handle subscription-based journals:
- Access management
- Manual download integration
- Metadata extraction

## Getting Started

1. Install SciTeX:
```bash
pip install -e /path/to/SciTeX-Code
```

2. Set up environment variables (optional):
```bash
export ANTHROPIC_API_KEY="your-key-here"
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"
```

3. Run a basic example:
```bash
python basic_scholar_example.py
```

4. Try advanced features:
```bash
python demo_enhanced_bibliography.py
```

## Directory Structure

```
examples/scholar/
├── basic_scholar_example.py      # Start here for basics
├── quick_scholar_demo.py         # Quick overview
├── demo_literature_search.py     # Full search workflow
├── demo_enhanced_bibliography.py # Bibliography with metrics
├── ai_research_assistant.py      # AI-powered assistant
├── bibliography_demo/            # Sample outputs
│   ├── enhanced_bibliography_with_metrics.bib
│   └── traditional_bibliography.bib
└── demo_review/                  # Review outputs
    ├── gpac_references.bib
    ├── literature_summary.md
    └── search_results.json
```

## Key Features Demonstrated

- **Paper Management**: Create, search, and organize scientific papers
- **Multi-Source Search**: Query PubMed, arXiv, Semantic Scholar
- **Journal Metrics**: Automatic impact factor and quartile lookup
- **AI Integration**: Optional AI-powered analysis and insights
- **Bibliography Generation**: Enhanced BibTeX with metrics
- **PDF Handling**: Download and parse scientific PDFs
- **Semantic Search**: Vector-based similarity search
- **Citation Networks**: Analyze paper relationships

## Requirements

- Python 3.8+
- SciTeX package with scholar module
- Optional API keys for enhanced functionality:
  - Semantic Scholar API (free, register at semanticscholar.org)
  - AI provider API (Anthropic, OpenAI, etc.)
  - Email for PubMed API compliance

## Troubleshooting

If you encounter import errors:
1. Ensure SciTeX is properly installed
2. Check that you're in the correct directory
3. Verify the scholar module is available: `python -c "import scitex.scholar"`

For API-related issues:
1. Check API key environment variables
2. Verify internet connectivity
3. Review rate limits for external services

## Next Steps

After running these examples:
1. Explore the scholar module API documentation
2. Customize search parameters for your research domain
3. Integrate with your existing research workflow
4. Contribute improvements back to SciTeX-Scholar!