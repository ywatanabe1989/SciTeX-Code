# SciTeX-Scholar Vector Search Guide

## Overview

SciTeX-Scholar now includes a sophisticated vector-based search engine that uses embeddings to understand the semantic meaning of your queries. Unlike traditional keyword search, this system can find relevant papers even when they don't contain your exact search terms.

## Key Features

### 1. **Semantic Understanding**
- Searches based on meaning, not just keywords
- Finds conceptually related papers
- Works across different terminologies

### 2. **Multiple Search Modes**
- **Semantic**: Pure embedding-based search
- **Chunk**: Searches within document sections
- **Hybrid**: Combines semantic and keyword matching

### 3. **Advanced Capabilities**
- Find similar papers
- Query expansion
- Metadata filtering
- Passage highlighting

## Installation & Setup

### Quick Start
```bash
# Run the setup script
./setup_and_run.sh
```

### Manual Setup
```bash
# Create virtual environment
python -m venv .env
source .env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model (first time only)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('allenai/scibert_scivocab_uncased')"
```

### Using Apptainer/Singularity
```bash
# Build container
apptainer build scitex-scholar.sif scitex-scholar.def

# Run with your PDFs mounted
apptainer run --bind ./Exported\ Items:/data/pdfs scitex-scholar.sif
```

## Usage Examples

### 1. Basic Semantic Search
```python
from scitex_scholar.vector_search_engine import VectorSearchEngine

# Initialize engine
engine = VectorSearchEngine()

# Semantic search
results = engine.search(
    query="neural synchronization during sleep",
    search_type="semantic",
    n_results=10
)

for result in results:
    print(f"{result.metadata['title']} - Score: {result.score:.3f}")
```

### 2. Find Similar Papers
```python
# Find papers similar to a specific document
similar = engine.find_similar_documents(
    doc_id="/path/to/paper.pdf",
    n_results=5
)
```

### 3. Advanced Hybrid Search
```python
# Combine semantic and keyword search
results = engine.search(
    query="phase amplitude coupling seizure detection Edakawa",
    search_type="hybrid",
    expand_query=True,  # Expands abbreviations
    filters={
        "year": "2023",
        "file_type": "pdf"
    }
)
```

### 4. Chunk-Based Search
```python
# Search within document sections
results = engine.search(
    query="classification accuracy above 95%",
    search_type="chunk",
    n_results=5
)

# Access relevant passages
for result in results:
    print(f"From: {result.metadata['title']}")
    print(f"Passage: {result.chunk_text}")
    print(f"Highlights: {result.highlights}")
```

## MCP Server Usage

### Starting the Server
```bash
python -m scitex_scholar.mcp_vector_server
```

### Available MCP Tools

1. **vector_search**
   - Semantic search with filters
   - Returns scored results with highlights

2. **find_similar_papers**
   - Finds semantically similar documents
   - Useful for literature exploration

3. **index_documents**
   - Index new documents with embeddings
   - Supports incremental updates

4. **analyze_collection**
   - Get insights about your document collection
   - Shows methods, datasets, trends

### Example MCP Queries
```javascript
// Semantic search
{
  "tool": "vector_search",
  "arguments": {
    "query": "deep learning for medical image segmentation",
    "search_type": "hybrid",
    "limit": 10,
    "year": "2023"
  }
}

// Find similar papers
{
  "tool": "find_similar_papers",
  "arguments": {
    "doc_path": "/path/to/reference_paper.pdf",
    "n_results": 5
  }
}
```

## Understanding Search Types

### Semantic Search
- **Best for**: Conceptual queries, exploring topics
- **Example**: "innovative approaches to biomarker discovery"
- **How it works**: Compares query embedding with document embeddings

### Chunk Search
- **Best for**: Finding specific information within papers
- **Example**: "accuracy greater than 90%"
- **How it works**: Searches embedded document chunks

### Hybrid Search
- **Best for**: Balanced precision and recall
- **Example**: "transformer architecture COVID-19 detection"
- **How it works**: Combines semantic similarity with keyword matching

## Performance Tips

1. **First-time indexing**: Takes longer due to embedding generation
2. **Cached embeddings**: Subsequent searches are much faster
3. **Batch processing**: Index multiple documents at once
4. **Model selection**: SciBERT is optimized for scientific text

## Advanced Configuration

### Custom Models
```python
# Use different embedding models
engine = VectorSearchEngine(
    model_name="sentence-transformers/all-mpnet-base-v2",  # General purpose
    # or
    model_name="pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb",  # Biomedical
)
```

### Chunking Strategy
```python
engine = VectorSearchEngine(
    chunk_size=512,      # Tokens per chunk
    chunk_overlap=128    # Overlap between chunks
)
```

## Troubleshooting

### Out of Memory
- Use CPU-only PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Reduce batch size in indexing
- Use smaller model

### Slow Indexing
- Normal for first run (building embeddings)
- Use pre-computed embeddings when possible
- Consider GPU acceleration

### No Results
- Check if documents are indexed: `engine.get_statistics()`
- Try broader queries
- Use semantic search instead of exact phrase

## Research Use Cases

1. **Literature Review**
   - Find all papers on a topic regardless of terminology
   - Identify research gaps
   - Track methodology evolution

2. **Paper Discovery**
   - Find similar papers to expand bibliography
   - Discover cross-disciplinary connections
   - Identify seminal works

3. **Trend Analysis**
   - Track accuracy improvements over time
   - Identify popular methods/datasets
   - Find emerging research directions

4. **Systematic Review**
   - Comprehensive topic coverage
   - Reduce selection bias
   - Reproducible search methodology

# EOF