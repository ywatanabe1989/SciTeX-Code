<!-- ---
!-- Timestamp: 2025-10-01 19:00:59
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/TODO.md
!-- --- -->


- [ ] Need to update source code to adhere the following format
  - [ ] Pefect, complete script: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/tests/nonparametric/_test_brunner_munzel.py
    - Uses main, parse_args, and run_main correctly
    - Saving path is correctly specified with stx.io.save
      - Output directory is handled so no need to mkdir in the script
      - logger.success is automatically handled so no need to print anything
    - logger.info is included in the source code and not crucial printing in main

- This is the template we must to adhere: 
  /home/ywatanabe/proj/scitex_repo/src/scitex/stats/template.py 

<!-- EOF -->