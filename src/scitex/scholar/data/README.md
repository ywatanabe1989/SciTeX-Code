# Scholar Data Directory

User-provided data files. This directory is gitignored.

## Structure

```
data/
└── impact_factor/
    ├── JCR_IF_2024.xlsx         # JCR Excel file (user-provided)
    ├── JCR_IF_2024.db           # SQLite database (generated)
    └── impact_factor.db -> JCR_IF_2024.db (symlink to active DB)
```

## Important

- **Data NOT included in git**: This directory is gitignored
- **User responsibility**: Users must provide their own JCR data
- **Licensing**: Users must ensure proper licensing for any data

## Adding JCR Data

1. Obtain JCR Excel file from Clarivate or authorized source
2. Place in `src/scitex/scholar/data/impact_factor/JCR_IF_YYYY.xlsx`
3. Build database (optional - will auto-build if needed):
   ```python
   from scitex.scholar.impact_factor.jcr import build_database
   build_database("JCR_IF_2024.xlsx")
   ```

## File Naming Convention

- Excel: `JCR_IF_YYYY.xlsx` (e.g., JCR_IF_2024.xlsx)
- Database: `JCR_IF_YYYY.db` (e.g., JCR_IF_2024.db)
- Symlink: `impact_factor.db` → points to current year DB

## Legal Notice

JCR data is proprietary (Clarivate Analytics). Users are responsible for:
- Obtaining data through authorized channels
- Compliance with licensing terms
- Not distributing data files

We provide only the code to use the data, not the data itself.
