# SciTeX-Scholar Examples

This directory contains comprehensive examples demonstrating all features of SciTeX-Scholar, mirroring the source structure.

## Example Structure

```
examples/
├── scitex_scholar/
│   ├── example_document_indexer.py       # Document indexing examples
│   ├── example_latex_parser.py           # LaTeX parsing examples
│   ├── example_literature_review_workflow.py  # Complete workflow examples
│   ├── example_mcp_server.py            # MCP server usage
│   ├── example_mcp_vector_server.py     # Vector MCP server usage
│   ├── example_scientific_pdf_parser.py  # PDF parsing examples
│   ├── example_search_engine.py         # Search engine usage
│   ├── example_text_processor.py        # Text processing examples
│   ├── paper_acquisition_example.py     # Paper acquisition demos
│   └── vector_search_example.py         # Vector search demonstrations
└── complete_literature_review.py        # Legacy complete example
```

## Running Examples

Each example is self-contained and can be run independently:

```bash
# Run a specific example
python examples/scitex_scholar/vector_search_example.py

# Run all examples (from project root)
for example in examples/scitex_scholar/*.py; do
    echo "Running $example..."
    python "$example"
done
```

## Example Categories

### 1. Basic Usage Examples
- `example_search_engine.py` - Basic keyword search
- `example_text_processor.py` - Text cleaning and normalization
- `example_latex_parser.py` - Parsing LaTeX documents

### 2. Advanced Features
- `vector_search_example.py` - Semantic search with embeddings
- `example_scientific_pdf_parser.py` - Extracting structured data from PDFs
- `example_document_indexer.py` - Building searchable document indices

### 3. Workflow Examples
- `example_literature_review_workflow.py` - Complete literature review process
- `paper_acquisition_example.py` - Automated paper discovery and download

### 4. Integration Examples
- `example_mcp_server.py` - MCP server for AI assistants
- `example_mcp_vector_server.py` - Vector-based MCP operations

## Legacy Examples

### Complete Literature Review (`complete_literature_review.py`)

The original comprehensive example demonstrating the full workflow:

- **Paper Discovery**: Search PubMed and arXiv for relevant papers
- **Automated Download**: Download freely available PDFs
- **Vector Indexing**: Create semantic embeddings for intelligent search
- **Semantic Search**: Find papers by meaning, not just keywords
- **Gap Analysis**: Identify unexplored methods and datasets
- **Review Generation**: Automatic literature review summary

**Usage:**
```bash
python examples/complete_literature_review.py
```

## Example Patterns

Each example follows these patterns:

1. **Clear Function Names**
   ```python
   def example_basic_search():
       """Example of basic search functionality."""
   ```

2. **Step-by-Step Progression**
   - Basic usage first
   - Advanced features next
   - Real-world scenarios last

3. **Extensive Comments**
   ```python
   # Initialize the search engine
   engine = SearchEngine()
   
   # Index sample documents
   for doc in documents:
       engine.index_document(doc)
   ```

4. **Output Formatting**
   ```python
   print("=== Example Name ===")
   print(f"Result: {result}")
   print("-" * 50)
   ```

## Key Examples Explained

### Vector Search Example
Demonstrates semantic search using SciBERT embeddings:
- Indexing scientific documents
- Semantic similarity search
- Hybrid search (keyword + semantic)
- Finding similar papers

### PDF Parser Example
Shows extraction of structured information:
- Title, authors, abstract extraction
- Methods and datasets identification
- Citation parsing
- Figure and table detection

### Literature Review Workflow
Complete end-to-end example:
- Paper discovery from multiple sources
- Automated downloading
- Information extraction
- Research gap analysis
- Review generation

### MCP Server Examples
Integration with AI assistants:
- Starting MCP servers
- Handling tool requests
- Async operation examples
- Error handling patterns

## Quick Start Examples

### Basic Semantic Search
```python
from scitex_scholar.vector_search_engine import VectorSearchEngine

engine = VectorSearchEngine()
results = engine.search("neural synchronization sleep", search_type="semantic")
```

### Paper Acquisition
```python
from scitex_scholar.paper_acquisition import search_papers

papers = await search_papers("epilepsy seizure prediction")
for paper in papers:
    print(f"{paper.title} ({paper.year})")
```

### Find Similar Papers
```python
similar = engine.find_similar_documents("path/to/paper.pdf", n_results=5)
```

## Requirements

Before running examples:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For paper acquisition examples:
   - Internet connection
   - Valid email for API compliance

3. For vector search examples:
   - ~2GB RAM for model loading
   - First run will download SciBERT model

## Example Outputs

The examples will create:
- `./my_literature_review/` - Workspace directory
- Downloaded PDFs in workspace
- Vector database for semantic search
- Literature review summaries in Markdown

## Tips for New Users

1. Start with `example_search_engine.py` for basic understanding
2. Move to `vector_search_example.py` for advanced search
3. Try `example_literature_review_workflow.py` for complete workflow
4. Explore MCP examples for AI assistant integration
5. Use small queries (10-20 papers) for initial testing
6. Combine sources (PubMed + arXiv) for comprehensive coverage

Each example includes sample data and expected output, making it easy to verify correct operation.