<!-- ---
!-- Timestamp: 2025-10-13 10:19:21
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->

# SciTeX Scholar

Fully open-sourced scientific literature management system.

## 📚 Storage Architecture

```
~/.scitex/scholar/library/
├── MASTER/                     # Centralized storage
│   ├── 8DIGIT01/              # Hash-based unique ID from DOI
│   │   ├── metadata.json      # Complete paper metadata
│   │   └── paper.pdf          # Downloaded PDF
│   └── 8DIGIT02/
│       ├── metadata.json
│       └── paper.pdf
├── project_name/               # Project-specific symlinks
│   ├── Author-Year-Journal -> ../MASTER/8DIGIT01
│   └── Author-Year-Journal -> ../MASTER/8DIGIT02
└── neurovista/
    ├── Cook-2013-Lancet -> ../MASTER/8DIGIT03
    └── ...
```

## 🚀 Quick Start

### Installation

```bash
pip install scitex
```

### Usage 1: From a BIBTEX file

**You can get BibTeX files from AI2 Scholar QA their optimized LLM**
   - Visit [Scholar QA](https://scholarqa.allen.ai/chat/)
   - Ask literature questions
   - Click "Export All Citations" to save as BibTeX file (*.bib)

Then, our scholar module can process their bibtex file:

```bash
python -m scitex.scholar bibtex \
    --bibtex papers.bib \
    --project myresearch \
    --num-workers 8
```

That's it! The command:
  - Loads all papers from the BibTeX file
  - Resolves DOIs and enriches metadata in parallel
  - Downloads all PDFs using 8 workers
  - Creates library structure: ~/.scitex/scholar/library/neurovista/
  - Saves enriched BibTeX with download status


### Usage 2: From DOIs or Titles

```bash
# SINGLE paper by DOI or title
python -m scitex.scholar single --doi "10.1038/nature12373" --project myresearch

# MULTIPLE papers in PARALLEL
python -m scitex.scholar parallel \
    --dois 10.1038/nature12373 10.1016/j.neuron.2018.01.023 \
    --project myresearch --num-workers 4
```

## Citation

If you use SciTeX in your research, please cite:

```bibtex
@software{scitex,
  title = {SciTeX: A Python Toolbox for Scientific Research},
  author = {Yusuke Watanabe},
  year = {2025},
  url = {https://github.com/ywatanabe1989/SciTeX-Code}
}
```

## For Developers
<details>
<summary>Project Architecture</summary>

```
                    ┌─────────────────┐
                    │  Scholar (API)  │
                    └────────┬────────┘
                             │
            ┌────────────────┼──────────────┐
            │                │              │
    ┌───────▼────────┐ ┌────▼─────┐ ┌───────▼────────┐
    │ ScholarEngine  │ │   Auth   │ │ ScholarLibrary │
    │  (Enrichment)  │ │ Gateway  │ │   (Storage)    │
    └────────────────┘ └────┬─────┘ └────────────────┘
                            │
                ┌───────────┼──────────┐
                │                      │
         ┌──────▼─────┐         ┌──────▼──────┐
         │ URL Finder │         │ PDF         │
         │            │────────▶│ Downloader  │
         └────────────┘         └─────────────┘
```


</details>

## License

MIT

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->