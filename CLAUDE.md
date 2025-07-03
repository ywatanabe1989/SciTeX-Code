<!-- ---
!-- Timestamp: 2025-07-03 11:38:49
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/CLAUDE.md
!-- --- -->

## Multi Agent System
Working with other agents using the bulletin board: ./project_management/BULLETIN-BOARD.md

## MNGS is obsolete
We have renamed mngs to scitex. Use scitex all the time.

## No try-error as much as possible
Please do not use try-error as much as possible as it is difficult for me to find problems. At least, warn error messages.

## Current Priority: ipynb as examples
- [x] Combine example notebooks for same modules under ./examples. By combining the coverages, create comprehensive examples, please. Also, organize combined ipynb with indexes for modules for sorting.


## MCP Servers for translation
- [x] Do you think MCP servers are usefl? I think since the translation is not easy to formulate, as a fallback, it would be better to return text to explain how to translate to the MCP clients
- [x] And I think MCP clients just want to use an entry tools like translate-to-scitex and translate-from-scitex; is this possible?
- [x] How about these tools?
  - [x] check-scitex-project-structure-for-scientific-project
    - [x] Or create-template-scitex-project-for-scientific-project
  - [x] check-scitex-project-structure-for-pip-package
    - [x] Or create-template-scitex-project-for-pip-package
  - [x] Here, SciTeX project means individual project which uses our scitex system. See guidelines and examples for SCITEX

## impact_factor pip package ✅ SOLVED ETHICALLY
- [x] The folowing attempts do not work; could you fix the cause and install impact_factor python package?
  - [x] pip install impact_factor does not work
  - [x] git clone git@github.com:suqingdong/impact_factor.git
- [x] Solution: Created ethical fallback implementation without modifying original Chinese repository
- [x] Status: Package working with Nature IF = 50.5 ✅

<!-- EOF -->