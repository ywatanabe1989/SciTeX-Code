<!-- ---
!-- Timestamp: 2025-08-12 18:52:31
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->


# SciTeX Scholar

A comprehensive Python library for scientific literature management with automatic enrichment of journal impact factors and citation counts.

## Literature review as BibTeX
[AI2 Scholar QA](https://scholarqa.allen.ai/chat/)
Expand -> Export All Citations

python -m scitex.scholar.metadata.doi.resolvers._DOIResolver
python -m scitex.scholar.metadata.enrichment._LibraryEnricher
 

## Core Objects

- [`./_Scholar.py`](./_Scholar.py)
- [`./Paper.py`](./Paper.py)
- [`./Papers.py`](./Papers.py)

``` mermaid
classDiagram
    direction LR

    class Scholar {
        +search(query) Papers
        +enrich_bibtex(path) Papers
        +download_pdfs(items) dict
    }

    class Papers {
        -papers: List~Paper~
        +filter(criteria) Papers
        +sort_by(criteria) Papers
        +save(path)
        +to_dataframe() DataFrame
    }

    class Paper {
        +doi: str
        +title: str
        +authors: List~str~
        +year: int
        +journal: str
        +citation_count: int
        +impact_factor: float
        +to_dict() dict
        +to_bibtex() str
    }

    Scholar "1" --o "many" Papers : creates
    Papers "1" --* "many" Paper : contains
```



## End-to-End Paper Acuisition Workflow

``` mermaid
graph TD
    A[User Input: DOI or Title] --> B[DOI Resolution];
    B --> C[Get Publisher URL];
    C --> D[Authentication];
    D --> E[Access Publisher Page with Authenticated Browser];
    E --> F[PDF Download];
    F --> G[PDF File];
    G --> H[PDF Validation];
    H -- Valid --> I[Metadata Enrichment];
    I --> J[Store in Library];
    style J fill:#f9f,stroke:#333,stroke-width:2px
    J --> K[End];
    H -- Invalid --> L[Log Error];
    L --> K;

    subgraph Library Storage
        J1[Save to MASTER/<ID>]
        J2[Create Project Symlink]
    end

    J --> J1 & J2
```


## SSO Automation Workflow: [`./auth/sso_automation`](./auth/sso_automation)

``` mermaid
graph TD
    A[Browser navigates to a page] --> B{Is it an SSO page?};
    B -- No --> C[Proceed normally];
    B -- Yes --> D[Detect Institution];
    D --> E[Select appropriate SSO Automator];
    E --> F[Automator performs login steps];

    subgraph Login Steps
        F1[Fill Username] --> F2[Fill Password];
        F2 --> F3{2FA Required?};
        F3 -- Yes --> F4[Handle 2FA (e.g., Duo Push)];
        F4 --> F5[User Approves on Device];
        F3 -- No --> F6[Submit Form];
        F5 --> F6;
    end

    F --> F1;
    F6 --> G{Login Successful?};
    G -- Yes --> H[Save Session State];
    H --> I[Redirect to Publisher Page];
    G -- No --> J[Log Failure];
    I --> K[End];
    J --> K;
    C --> K;
```


## DOI Resolution Workflow: [`./metadata/doi`](./metadata/doi)
``` mermaid
graph TD
    A[Start DOI Resolution] --> B{Check Cache};
    B -- Yes --> C[Return Cached DOI];
    B -- No --> D{Select Optimal Sources};
    D --> E[Attempt Resolution with Source 1];
    E -- Success --> F{Validate & Clean DOI};
    F --> G[Save to Cache];
    G --> H[Return DOI];
    E -- Failure --> I{Attempt Resolution with Source 2};
    I -- Success --> F;
    I -- Failure --> J{Attempt Resolution with Source 3};
    J -- Success --> F;
    J -- Failure --> K[Log Failure];
    K --> L[Return Not Found];

    subgraph Sources
        direction LR
        S1[URLDOIExtractor]
        S2[CrossRefSource]
        S3[SemanticScholarSource]
        S4[PubMedSource]
        S5[OpenAlexSource]
    end

    D --> S1;
    D --> S2;
    D --> S3;
    D --> S4;
    D --> S5;
```

## Metadata Enrichment Workflow [`./metadata/enrichment`](./metadata/enrichment)

``` mermaid
graph TD
    A[Start with Paper Object (Title/Authors)] --> B{Has DOI?};
    B -- No --> C[1. Resolve DOI];
    B -- Yes --> D[2. Fetch Citation Count];
    C --> D;
    D --> E[3. Fetch Journal Impact Factor];
    E --> F[4. Fetch Abstract];
    F --> G[Update Paper Object with Enriched Data];
    G --> H[End];

    subgraph Data Sources
        S1[CrossRef]
        S2[Semantic Scholar]
        S3[PubMed]
        S4[JCR Data]
    end

    C --> S1 & S2 & S3;
    D --> S1 & S2;
    E --> S4;
    F --> S1 & S2 & S3;
```

## PDF Download Workflow [`./metadata/urls`](./metadata/urls)

``` mermaid
graph TD
    A[Start with Authenticated Browser & URL] --> B{Attempt Direct Download};
    B -- Success --> C[Save PDF File];
    B -- Failure --> D{Attempt Download via Zotero Translator};
    D -- Success --> C;
    D -- Failure --> E[Log Download Failure];
    C --> F{Validate PDF Content};
    F -- Valid --> G[Store PDF in Library];
    F -- Invalid --> H{Move to Invalid PDFs};
    H --> I[Log Validation Failure];
    G --> J[End];
    E --> J;
    I --> J;

    subgraph Validation Checks
        V1[Check File Size]
        V2[Check Page Count]
        V3[Check for Error Text]
        V4[Check for Main Sections (Abstract, Intro, etc.)]
    end

    F --> V1;
    F --> V2;
    F --> V3;
    F --> V4;
```

## Library Management Workflow: [`./metadata/urls`](./)

``` mermaid
graph TD
    A[Start with New Paper (Metadata & PDF)] --> B{Generate Unique 8-Digit ID};
    B --> C[Create Directory in /MASTER/];
    style C fill:#f9f,stroke:#333,stroke-width:2px
    C --> D[Save metadata.json];
    C --> E[Save PDF File];
    B --> F{Generate Human-Readable Name (Author-Year-Journal)};
    F --> G[Create Symlink in /project/pac/];
    style G fill:#ccf,stroke:#333,stroke-width:2px
    G -- points to --> C;
    G --> H[Update Project BibTeX File];
    H --> I[End];
```

## Library Structure

``` plaintext
~/.scitex/scholar/
├── cache
│   ├── auth
│   └── chrome
├── config
│   ├── default.yaml
│   ├── settings
│   └── styles
├── library/
│   ├── MASTER/
│   │   ├── <8-DIGIT-ID>/
│   │   │   ├── metadata.json
│   │   │   └── paper.pdf
│   │   └── <8-DIGIT-ID>/
│   │       ├── metadata.json
│   │       └── paper.pdf
│   └── <project-name>/
│       ├── Author-Year-Journal -> ../MASTER/<8-DIGIT-ID>
│       ├── Author-Year-Journal -> ../MASTER/<8-DIGIT-ID>
│       └── info/
│           └── pac.bib
├── README.md
├── sso_sessions
│   ├── openathens_session.json
│   └── unimelb_session.json
├── url_cache
└── workspace
    ├── download_asyncs
    ├── downloads
    ├── logs
    └── screenshots
```
## Installation

```bash
sudo apt update && sudo apt install -y tesseract-ocr

# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies for enhanced functionality
pip install impact-factor  # For real 2024 JCR impact factors
pip install PyMuPDF       # For PDF text extraction
pip install sentence-transformers  # For vector similarity search
pip install selenium webdriver-manager  # For PDF downloading from Sci-Hub
pip install scholarly     # For Google Scholar search (Note: may be rate-limited)
pip install pytesseract
pip install pyautogui

git clone git@github.com:zotero/translators.git zotero_translators

# Install Lean Library browser extension (recommended for institutional access)
# Chrome/Edge: https://chrome.google.com/webstore/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/lean-library/
```


## Citation

If you use SciTeX Scholar in your research, please cite:

```bibtex
@software{scitex_scholar,
  title = {SciTeX Scholar: Scientific Literature Management with Automatic Enrichment},
  author = {Watanabe, Yusuke},
  year = {2025},
  url = {https://github.com/ywatanabe1989/scitex}
}
```

## License

MIT

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->