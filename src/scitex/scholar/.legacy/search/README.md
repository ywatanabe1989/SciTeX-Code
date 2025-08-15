# Scholar Semantic Search Module

Find semantically similar papers using embeddings and vector search.

## Features

### Embedder
- Multiple embedding models (Sentence Transformers, TF-IDF)
- GPU acceleration support
- Embedding caching for performance
- Paper-specific embedding (title, abstract, keywords)

### VectorDatabase
- Fast nearest neighbor search (FAISS/NumPy)
- Multiple index types (flat, IVF, HNSW)
- Persistent storage
- Metadata support
- Batch operations

### SemanticSearchEngine
- Index papers from database
- Find similar papers
- Search by text query
- Multi-paper recommendations
- Hybrid search (semantic + keyword)
- Metadata filtering

## Installation

```bash
# Basic (NumPy/TF-IDF)
pip install scikit-learn

# Recommended (Sentence Transformers)
pip install sentence-transformers

# Advanced (FAISS for fast search)
pip install faiss-cpu  # or faiss-gpu
```

## Usage

```python
from scitex.scholar.database import PaperDatabase
from scitex.scholar.search import SemanticSearchEngine

# Initialize with database
db = PaperDatabase()
engine = SemanticSearchEngine(
    database=db,
    model_name="all-MiniLM-L6-v2",  # Fast and good
    index_type="flat",  # Exact search
    use_gpu=False
)

# Index all papers
stats = engine.index_papers(
    fields=["title", "abstract", "keywords"]
)
print(f"Indexed {stats['indexed']} papers")

# Search by text
results = engine.search_by_text(
    "deep learning for climate modeling",
    k=10,
    search_mode="hybrid"  # Semantic + keyword
)

for paper, score in results:
    print(f"{score:.3f}: {paper.title} ({paper.year})")

# Find similar papers
paper = db.get_entry("doi_10.1038_nature12345")
similar = engine.find_similar_papers(paper, k=5)

# Get recommendations based on multiple papers
recommendations = engine.recommend_papers(
    entry_ids=["doi_1", "doi_2", "doi_3"],
    k=10,
    method="average"
)

# Filter results
ml_papers_2024 = engine.search_similar(
    "machine learning",
    k=20,
    filters={
        "year_min": 2024,
        "has_pdf": True,
        "tag": "reviewed"
    }
)
```

## Embedding Models

### Sentence Transformers (Recommended)
- `all-MiniLM-L6-v2`: Fast, good quality (384 dim)
- `all-mpnet-base-v2`: Higher quality (768 dim)
- `allenai-specter`: Scientific papers (768 dim)

### TF-IDF (Fallback)
- No dependencies beyond scikit-learn
- Vocabulary-based embeddings
- Good for keyword matching

## Index Types

### Flat (Default)
- Exact nearest neighbor search
- Best for < 100k papers
- No training required

### IVF (Inverted File)
- Approximate search
- Good for 100k-1M papers
- Requires training

### HNSW (Hierarchical NSW)
- Very fast approximate search
- Good for > 1M papers
- Higher memory usage

## Performance Tips

1. **Batch Indexing**: Index papers in batches
   ```python
   engine.index_papers(batch_size=1000)
   ```

2. **GPU Acceleration**: Use GPU for faster search
   ```python
   engine = SemanticSearchEngine(use_gpu=True)
   ```

3. **Caching**: Embeddings are cached automatically
   ```python
   # Cache location: ~/.scitex/scholar/embeddings_cache/
   ```

4. **Incremental Updates**: Index only new papers
   ```python
   engine.index_papers()  # Only indexes new entries
   ```

## Advanced Features

### Custom Fields
```python
# Index with custom fields
engine.index_papers(
    fields=["title", "abstract", "authors"]
)
```

### Similarity Metrics
```python
# In Embedder class
similarities = embedder.compute_similarity(
    embeddings1, 
    embeddings2,
    metric="cosine"  # or "dot", "euclidean"
)
```

### Update Index
```python
# Update after paper modification
engine.update_index(entry_id)
```

### Search Modes
- `semantic`: Pure embedding search
- `keyword`: Title/abstract keyword match
- `hybrid`: Combines both approaches

## Storage

Default location: `~/.scitex/scholar/vector_db/`

Structure:
```
vector_db/
├── embeddings.npy       # Embedding vectors
├── entry_ids.json       # Paper IDs
├── metadata.json        # Metadata for each embedding
├── faiss.index         # FAISS index (if available)
├── config.json         # Database configuration
└── indexed_entries.json # List of indexed papers
```

## Troubleshooting

### No sentence-transformers
- Falls back to TF-IDF automatically
- Install with: `pip install sentence-transformers`

### FAISS not available
- Uses NumPy for search (slower but works)
- Install with: `pip install faiss-cpu`

### Out of memory
- Use smaller model: `all-MiniLM-L6-v2`
- Index in smaller batches
- Use approximate index (IVF/HNSW)