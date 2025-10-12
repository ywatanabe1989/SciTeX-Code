<!-- ---
!-- Timestamp: 2025-10-09 21:42:32
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/TODO.md
!-- --- -->

- Regarding this browser module, following the ./template.py, please add main, argparser, run_main with main guard to demonstrate each file in standalone when evaluated by python -m ...
- ALL python scripts, from atomic functions to classes, include main, run_main, argparse , following the template.py 
- Since this is a pip package, main should not include print/logging themselves. Instead, use verbose=True and rely on source code logging logics.

<!-- EOF -->