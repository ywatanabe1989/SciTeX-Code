<!-- ---
!-- Timestamp: 2025-07-26 13:57:55
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
    - Abstract Class should be named as `_BaseXXX.py` and `BaseXXX` Class as a separate file

- [x] Reorganize Scholar module into subdirectories (completed 2025-07-26)
  - ✅ auth/ - Authentication components (_OpenAthensAuthentication.py, _LeanLibraryAuthentication.py, etc.)
  - ✅ download/ - Download strategies (_PDFDownloader.py, _ZoteroTranslatorRunner.py, etc.)
  - ✅ search/ - Search engines (_UnifiedSearcher.py)
  - ✅ core/ - Core components (_DOIResolver.py, _MetadataEnricher.py, _OpenURLResolver.py, etc.)
  - ✅ utils/ - Utility functions (_ethical_usage.py, _formatters.py, _progress_tracker.py, _paths.py)
  - ✅ All imports updated to reflect new structure

<!-- EOF -->