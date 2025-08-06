# Scholar Database Module

Organizes and manages download research papers with metadata, search capabilities, and file organization.

## Features

### DatabaseEntry
- Comprehensive metadata storage (DOI, title, authors, etc.)
- PDF validation status tracking
- Tags and collections for organization
- Custom fields support
- Automatic filename generation

### PaperDatabase
- Add/update/remove paper entries
- Import from Paper objects or BibTeX
- Organize PDFs by year/journal/author
- Export to BibTeX or JSON
- Track download and validation status
- Find orphaned PDFs

### DatabaseIndex
- Fast lookup by DOI
- Fuzzy title matching
- Author name search
- Filter by year, journal, tags
- Multi-criteria search
- Persistent index storage

## Usage

```python
from scitex.scholar.database import PaperDatabase

# Initialize database
db = PaperDatabase()

# Import papers
from scitex.scholar import Scholar
scholar = Scholar()
papers = scholar.load_bibtex("papers.bib")
entry_ids = db.import_from_papers(papers)

# Organize PDFs
for entry_id in entry_ids:
    entry = db.get_entry(entry_id)
    if entry.pdf_path:
        new_path = db.organize_pdf(
            entry_id, 
            entry.pdf_path,
            organization="year_journal"
        )

# Search database
results = db.search(
    author="Smith",
    year=2024,
    tag="machine-learning"
)

for entry_id, entry in results:
    print(f"{entry.title} ({entry.year})")

# Export subset
ml_papers = [id for id, e in results]
db.export_to_bibtex("ml_papers.bib", ml_papers)

# Get statistics
stats = db.get_statistics()
print(f"Total papers: {stats['total_entries']}")
print(f"Valid PDFs: {stats['pdf_stats']['valid']}")
```

## Organization Schemes

### year_journal
```
pdfs/
├── 2024/
│   ├── Nature/
│   │   ├── 2024_Smith_DeepLearning.pdf
│   │   └── 2024_Jones_ClimateModel.pdf
│   └── Science/
│       └── 2024_Brown_QuantumComputing.pdf
└── 2023/
    └── Cell/
        └── 2023_Davis_GenomeEditing.pdf
```

### year_author
```
pdfs/
├── 2024/
│   ├── Smith/
│   │   └── 2024_Smith_DeepLearning.pdf
│   └── Jones/
│       └── 2024_Jones_ClimateModel.pdf
```

### flat
```
pdfs/
├── 2024_Smith_DeepLearning.pdf
├── 2024_Jones_ClimateModel.pdf
└── 2023_Davis_GenomeEditing.pdf
```

## Database Location

Default: `~/.scitex/scholar/database/`

Structure:
```
database/
├── data/
│   ├── papers.json      # Main database
│   └── metadata.json    # Statistics
├── pdfs/               # Organized PDFs
├── indices/            # Search indices
└── exports/            # Export files
```