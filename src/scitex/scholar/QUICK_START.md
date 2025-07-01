# SciTeX-Scholar Quick Start Guide

Welcome to SciTeX-Scholar - a powerful scientific literature search and analysis system!

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Try the Demo

Run the complete demonstration:

```bash
python demo_literature_search.py
```

This will show you:
- Paper search from PubMed and arXiv
- Automatic PDF downloading
- Semantic search with SciBERT
- Literature analysis capabilities

### 3. For Real Literature Review

For actual research with subscription journals:

```bash
# Step 1: Search and categorize papers
python subscription_journal_workflow.py

# Step 2: Download subscription PDFs manually using your institutional access
# Save them to: ./literature_workspace/pdfs/

# Step 3: Process and analyze
python subscription_journal_workflow.py --process
```

## 📚 Key Features

### Vector-Based Semantic Search
- Uses SciBERT embeddings trained on scientific text
- Understands scientific terminology and concepts
- Finds papers by meaning, not just keywords

### Multi-Source Paper Discovery
- **PubMed**: Biomedical literature
- **arXiv**: Preprints in physics, math, CS, etc.
- Extensible to add more sources

### Intelligent PDF Processing
- Extracts title, authors, abstract
- Identifies methods and datasets
- Parses mathematical content
- Handles LaTeX documents

### Literature Review Workflow
- Automated paper discovery
- Research gap identification
- Citation network analysis
- Markdown report generation

## 💡 Example Use Cases

### 1. Find Similar Papers
```python
from scitex_scholar.vector_search_engine import VectorSearchEngine

engine = VectorSearchEngine()
similar = engine.find_similar_documents("path/to/reference/paper.pdf")
```

### 2. Search by Concept
```python
results = engine.search("transformer architectures for medical image segmentation")
```

### 3. Extract Methods from Papers
```python
from scitex_scholar.scientific_pdf_parser import ScientificPDFParser

parser = ScientificPDFParser()
paper = parser.parse_pdf("paper.pdf")
print("Methods found:", paper.methods_mentioned)
print("Datasets used:", paper.datasets_mentioned)
```

## 🔧 Configuration

### Set Your Email for PubMed
Edit in your scripts:
```python
acquisition = PaperAcquisition(email="your.email@example.com")
```

### Adjust Search Parameters
```python
papers = await acquisition.search(
    query="your research topic",
    max_results=50,  # Number of papers
    sources=['pubmed', 'arxiv']  # Data sources
)
```

## 📁 Project Structure

```
SciTeX-Scholar/
├── src/scitex_scholar/        # Core modules
├── tests/                    # Comprehensive tests
├── examples/                 # Usage examples
├── demo_literature_search.py # Full demo
└── subscription_journal_workflow.py  # For restricted access papers
```

## 🚦 Next Steps

1. **Run Examples**: Check `examples/scitex_scholar/` for detailed usage
2. **Read Tests**: Tests show all functionality with examples
3. **API Development**: Phase 3A will add REST API and web interface
4. **Contribute**: All code is well-documented and tested

## ⚠️ Important Notes

- **First Run**: SciBERT model download (~400MB) happens on first use
- **PDF Access**: Subscription journals require manual download
- **Performance**: First embedding generation is slower; subsequent searches are fast
- **Storage**: Vector database is saved locally in `.vector_db/`

## 🆘 Troubleshooting

### Missing Dependencies
```bash
pip install sentence-transformers chromadb pdfplumber aiohttp
```

### Memory Issues with Large PDFs
- Process PDFs in batches
- Use the document chunking features
- Adjust chunk_size in VectorSearchEngine

### API Rate Limits
- PubMed requires email registration
- Default rate limiting prevents blocking
- Adjust rate_limit parameter if needed

## 📧 Support

- Check `docs/API_DOCUMENTATION.md` for detailed API reference
- See `project_management/` for development roadmap
- File issues in the project repository

---

Happy researching! 🔬📚