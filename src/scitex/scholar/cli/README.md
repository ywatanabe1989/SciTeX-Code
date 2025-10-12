<!-- ---
!-- Timestamp: 2025-10-06 11:30:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/README.md
!-- --- -->

# SciTeX Scholar CLI Documentation

## 🚀 Overview

The SciTeX Scholar CLI provides a **unified, flexible command-line interface** for managing scientific literature. Unlike traditional CLIs with rigid subcommands, our design allows **combinable operations** in a single command.

## Command Structure

```bash
python -m scitex.scholar [INPUT] [OPERATIONS] [OPTIONS]
```

Where:
- **INPUT**: Source of papers (--bibtex, --doi, --dois, --title)
- **OPERATIONS**: Actions to perform (--enrich, --download, --list, --search, --export)
- **OPTIONS**: Filters and settings (--project, --year-min, --min-citations, etc.)

## 📋 Complete CLI Reference

### 🎯 Input Sources

| Option | Description | Example |
|--------|-------------|---------|
| `--bibtex FILE` | Path to BibTeX file | `--bibtex papers.bib` |
| `--doi DOI` | Single DOI string | `--doi "10.1038/nature12373"` |
| `--dois DOI [DOI ...]` | Multiple DOIs | `--dois "10.1038/xxx" "10.1126/yyy"` |
| `--title TITLE` | Paper title for resolution | `--title "Deep learning review"` |

### 📚 Project Management

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--project NAME` | `-p` | Project for persistent storage | `--project neurovista` |
| `--create-project` | | Create new project | `--create-project` |
| `--description TEXT` | | Project description | `--description "Seizure research"` |

### ⚡ Operations

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--enrich` | `-e` | Enrich with metadata (DOIs, abstracts, citations) | `--enrich` |
| `--download` | `-d` | Download PDFs to MASTER library | `--download` |
| `--list` | `-l` | List papers in project | `--list` |
| `--search QUERY` | `-s` | Search papers in library | `--search "EEG"` |
| `--stats` | | Show library statistics | `--stats` |
| `--export FORMAT` | | Export project (bibtex/csv/json) | `--export bibtex` |

### 🔍 Filtering Options

| Option | Description | Example |
|--------|-------------|---------|
| `--year-min YEAR` | Minimum publication year | `--year-min 2020` |
| `--year-max YEAR` | Maximum publication year | `--year-max 2024` |
| `--min-citations N` | Minimum citation count | `--min-citations 50` |
| `--min-impact-factor F` | Minimum journal impact factor | `--min-impact-factor 5.0` |
| `--has-pdf` | Only papers with PDFs | `--has-pdf` |

### 📁 Output Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--output FILE` | `-o` | Output file path | `--output enriched.bib` |

### 🔧 System Options

| Option | Description | Example |
|--------|-------------|---------|
| `--debug` | Enable debug output | `--debug` |
| `--no-cache` | Disable caching | `--no-cache` |
| `--browser MODE` | Browser mode (stealth/interactive) | `--browser interactive` |

## 📖 Working Examples with Real Data

### 1. Basic BibTeX Enrichment

```bash
# Enrich neurovista dataset
cd /home/ywatanabe/proj/scitex_repo/src/scitex/scholar
python -m scitex.scholar \
    --bibtex data/neurovista.bib \
    --enrich \
    --output data/neurovista_enriched.bib

# With project storage
python -m scitex.scholar \
    --bibtex data/neurovista.bib \
    --project neurovista \
    --enrich
```

### 2. PDF Downloads

```bash
# Download from enriched BibTeX (MASTER storage with project symlinks)
python -m scitex.scholar \
    --bibtex data/neurovista_enriched.bib \
    --project neurovista \
    --download

# Download single DOI
python -m scitex.scholar \
    --doi "10.1038/s41598-024-67155-x" \
    --project neurovista \
    --download

# Download multiple DOIs
python -m scitex.scholar \
    --dois "10.1093/brain/awx098" "10.1371/journal.pone.0081920" \
    --project neurovista \
    --download
```

### 3. Combined Operations

```bash
# Enrich and download in one command
python -m scitex.scholar \
    --bibtex data/neurovista.bib \
    --project neurovista \
    --enrich \
    --download

# Create project, enrich, filter, and download
python -m scitex.scholar \
    --bibtex data/pac-seizure_prediction.bib \
    --project seizure_2024 \
    --create-project \
    --description "2024 Seizure prediction papers" \
    --enrich \
    --year-min 2020 \
    --min-citations 30 \
    --download
```

### 4. Filtering Examples

```bash
# Download only high-impact recent papers
python -m scitex.scholar \
    --bibtex data/pac-seizure_prediction_enriched.bib \
    --project high_impact \
    --year-min 2022 \
    --min-citations 100 \
    --min-impact-factor 10.0 \
    --download

# Export filtered results
python -m scitex.scholar \
    --project neurovista \
    --year-min 2020 \
    --has-pdf \
    --export bibtex \
    --output recent_with_pdfs.bib
```

### 5. Project Management

```bash
# Create new project
python -m scitex.scholar \
    --project ml_papers \
    --create-project \
    --description "Machine learning in neuroscience"

# List papers in project
python -m scitex.scholar \
    --project neurovista \
    --list

# Search within project
python -m scitex.scholar \
    --project neurovista \
    --search "seizure detection"

# Search across all projects
python -m scitex.scholar \
    --search "deep learning"
```

### 6. Library Operations

```bash
# Show library statistics
python -m scitex.scholar --stats

# Export project to JSON
python -m scitex.scholar \
    --project neurovista \
    --export json \
    --output neurovista_papers.json

# Export filtered papers
python -m scitex.scholar \
    --project neurovista \
    --year-min 2023 \
    --export bibtex \
    --output neurovista_2023.bib
```

## 🔄 What Enrichment Adds

The `--enrich` operation adds the following metadata to each paper:

| Metadata | Source | Description |
|----------|---------|------------|
| **DOI** | CrossRef, Semantic Scholar, PubMed | Digital Object Identifier |
| **Abstract** | Multiple databases | Paper abstract |
| **Citation Count** | OpenAlex, Semantic Scholar | Number of citations |
| **Impact Factor** | JCR 2024 database | Journal 2-year impact factor |
| **Keywords** | Publisher metadata | Research keywords |
| **PMID** | PubMed | PubMed ID |
| **ArXiv ID** | arXiv | arXiv identifier |

### Example Enriched Entry

```bibtex
@article{Cook2013,
  title = {Prediction of seizure likelihood with a long-term, implanted seizure advisory system},
  author = {Cook, Mark J and O'Brien, Terence J and Berkovic, Samuel F},
  year = {2013},
  journal = {The Lancet Neurology},
  doi = {10.1016/s1474-4422(13)70075-9},
  abstract = {Seizure prediction would be a valuable capability for...},
  citation_count = {543},
  journal_impact_factor = {59.935},
  doi_source = {crossref},
  abstract_source = {semantic_scholar},
}
```

## 📁 Storage Architecture

After running operations with `--project`, your library is organized as:

```
~/.scitex/scholar/library/
├── MASTER/                         # Centralized storage
│   ├── A1B2C3D4/                  # Hash from DOI
│   │   ├── metadata.json          # Complete metadata
│   │   └── DOI_10.1038_xxx.pdf    # Downloaded PDF
│   └── E5F6G7H8/
│       ├── metadata.json
│       └── DOI_10.1126_yyy.pdf
└── neurovista/                     # Project directory
    ├── Cook-2013-Lancet -> ../MASTER/A1B2C3D4
    └── Author-2024-Nature -> ../MASTER/E5F6G7H8
```

## 🚀 Advanced Usage

### Batch Processing

```bash
#!/bin/bash
# Process all BibTeX files in a directory
for bib_file in data/*.bib; do
    echo "Processing $bib_file..."
    python -m scitex.scholar \
        --bibtex "$bib_file" \
        --project combined_research \
        --enrich \
        --download
done
```

### Resume Interrupted Downloads

```bash
# Caching allows safe re-runs - already downloaded PDFs are skipped
python -m scitex.scholar \
    --bibtex data/large_dataset.bib \
    --project large_project \
    --download
```

### Interactive Browser Mode

```bash
# Use visible browser for difficult papers
python -m scitex.scholar \
    --bibtex data/paywalled_papers.bib \
    --project paywalled \
    --download \
    --browser interactive

# Open browser for manual login
python -m scitex.scholar chrome
```

## ⚠️ Error Handling

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| **No DOIs found** | First run with `--enrich` to resolve DOIs |
| **Authentication required** | Use `python -m scitex.scholar chrome` to login |
| **Rate limiting** | System automatically handles with retries and caching |
| **Download failures** | Re-run command - caching skips completed downloads |

## 🎯 Best Practices

1. **Always enrich first** - Resolves DOIs and metadata needed for downloads
2. **Use projects** - Keeps papers organized with persistent storage
3. **Filter strategically** - Download high-impact papers first
4. **Check stats regularly** - Monitor library growth with `--stats`
5. **Export for sharing** - Use `--export bibtex` for curated collections

## 📊 Metadata Sources

| Database | Used For |
|----------|----------|
| **CrossRef** | DOIs, basic metadata |
| **Semantic Scholar** | Citations, abstracts, related papers |
| **PubMed** | Biomedical abstracts, PMIDs |
| **OpenAlex** | Citation counts, author affiliations |
| **arXiv** | Preprints, arXiv IDs |
| **JCR Database** | Journal impact factors (2024) |
| **Publisher Sites** | PDFs via institutional access |

## 📍 File Locations

| Component | Location |
|-----------|----------|
| **Main Entry** | `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py` |
| **Library** | `~/.scitex/scholar/library/` |
| **URL Cache** | `~/.scitex/scholar/cache/url_finder/` |
| **Browser Profiles** | `~/.scitex/scholar/cache/chrome/` |
| **Auth Cookies** | `~/.scitex/scholar/cache/auth/` |

## 🔄 Workflow Diagram

```
Input Sources          Operations           Storage
─────────────         ────────────         ───────────
BibTeX File    ──┐                      ┌→ MASTER/
                 ├→ Enrich → Filter → Download
Single DOI     ──┤          ↓         ↓         └→ project/
                 │      Metadata    PDFs
Multiple DOIs  ──┘
```

## 📞 Support

- **GitHub Issues**: https://github.com/ywatanabe1989/SciTeX-Code/issues
- **Email**: ywatanabe@scitex.ai
- **Documentation**: This file and main README.md

## 🎓 Citation

If you use SciTeX Scholar CLI in your research:

```bibtex
@software{scitex_scholar_cli,
  title = {SciTeX Scholar CLI: Unified Literature Management Interface},
  author = {Yusuke Watanabe},
  year = {2025},
  url = {https://github.com/ywatanabe1989/SciTeX-Code/tree/main/src/scitex/scholar/cli}
}
```

<!-- EOF -->