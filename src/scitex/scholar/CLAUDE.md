<!-- ---
!-- Timestamp: 2025-07-23 16:00:16
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/CLAUDE.md
!-- --- -->

- [x] Implement scitex-specific warning/error systems: /home/ywatanabe/proj/scitex_repo/src/scitex/errors.py
  - ✅ Using ScholarError, DOIResolutionError, PDFExtractionError, BibTeXEnrichmentError, etc.
  - ✅ Using SciTeXWarning for non-critical issues
- [x] Filenames of Python scripts should start from underscore, to show they are not modules
  - [x] If the main components of the script is class definition, the script should be named in the ClassName convensions
    - ✅ _Paper.py, _Papers.py, _Scholar.py, _Config.py, _DOIResolver.py, etc.
  - [x] If the main components of the script is function, the script should be named in the function_name convensions in verb forms
    - ✅ _utils.py, _ethical_usage.py

<!-- EOF -->