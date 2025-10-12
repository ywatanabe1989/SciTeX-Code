# JCR Impact Factor Engine

This module provides fast SQLite-based lookups for journal impact factors using Journal Citation Reports (JCR) data.

## Components

### ImpactFactorJCREngine.py
- Query engine for JCR database
- Fast SQLite-based journal metrics lookup
- Returns impact factor, quartile, and ISSN information
- Handles missing data gracefully

### build_database.py
- Builds SQLite database from JCR Excel files
- Parses JCR Excel exports
- Creates indexed database for fast queries
- Extracts impact factors and quartiles

## Usage

### Building the Database

```python
from scitex.scholar.impact_factor.jcr.build_database import build_database
from pathlib import Path

# Build database from JCR Excel file
excel_path = Path("JCR_IF_2021.xlsx")
db_path = build_database(excel_path)
```

Or run as a script:
```bash
python -m scitex.scholar.impact_factor.jcr.build_database --excel JCR_IF_2021.xlsx
```

### Querying Impact Factors

```python
from scitex.scholar.impact_factor.jcr.ImpactFactorJCREngine import ImpactFactorJCREngine

# Initialize engine
engine = ImpactFactorJCREngine()

# Search by journal name
results = engine.search("Nature")

# Search by ISSN
results = engine.search("0028-0836", key="issn")

# Filter by impact factor range
high_impact = engine.filter(min_value=10.0, limit=100)
```

## Data Format

### Input
- JCR Excel files (.xlsx) with columns:
  - Journal Name / Name
  - ISSN
  - EISSN
  - 2021 JIF / JIF
  - CATEGORY (with quartile info)

### Output
SQLite database with schema:
- `journal` (str, primary key): Journal name
- `journal_abbr` (str): Journal abbreviation
- `issn` (str): Print ISSN
- `eissn` (str): Electronic ISSN
- `factor` (float): Impact factor
- `jcr` (str): JCR quartile (Q1-Q4)
- `nlm_id` (str): NLM unique ID

## Data Location

- Input Excel files: `../../data/impact_factor/JCR_IF_YYYY.xlsx`
- Output database: `../../data/impact_factor/impact_factor.db`

## Dependencies

- openpyxl: Excel file parsing
- sqlalchemy: Database operations
- sql_manager: Dynamic model management
