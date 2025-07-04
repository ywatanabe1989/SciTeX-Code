<!-- ---
!-- Timestamp: 2025-07-01 21:54:41
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Scholar/docs/from_user/suggestions_by_other_LLMs.md
!-- --- -->

Add these sources:
python# In paper_acquisition.py, add:
- PLOS ONE API
- PubMed Central OAI-PMH
- DOAJ (Directory of Open Access Journals)
- Semantic Scholar API (has many open access papers)
- OpenAlex API (successor to Microsoft Academic)

│  - Metadata-only indexing          │
├─────────────────────────────────────┤
│  External Enrichment (New)          │
│  - Semantic Scholar API            │
│  - Citation network analysis       │
│  - Research trend detection        │
└─────────────────────────────────────┘
Implementation Priority

First: Maximize open access coverage (adds 40-60% more papers)
Second: Add metadata-only indexing for comprehensive discovery
Third: Implement reference manager integration
Fourth: Consider institutional proxy support

This approach keeps your valuable custom features while ethically expanding access to subscription content through legitimate channels.

<!-- EOF -->