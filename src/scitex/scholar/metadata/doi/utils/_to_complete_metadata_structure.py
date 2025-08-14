#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 10:59:36 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/utils/_to_complete_metadata_structure.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/utils/_to_complete_metadata_structure.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from collections import OrderedDict


def to_complete_metadata_structure(metadata):
    """Initialize all required fields with null values."""
    complete_structure = OrderedDict(
        [
            (
                "id",
                OrderedDict(
                    [
                        ("doi", None),
                        ("doi_source", None),
                        ("arxiv_id", None),
                        ("arxiv_id_source", None),
                        ("pmid", None),
                        ("pmid_source", None),
                        ("scholar_id", None),
                        ("scholar_id_source", None),
                    ]
                ),
            ),
            (
                "basic",
                OrderedDict(
                    [
                        ("title", None),
                        ("title_source", None),
                        ("authors", None),
                        ("authors_source", None),
                        ("year", None),
                        ("year_source", None),
                        ("abstract", None),
                        ("abstract_source", None),
                        ("keywords", None),
                        ("keywords_source", None),
                        ("type", None),
                        ("type_source", None),
                    ]
                ),
            ),
            (
                "citation_count",
                OrderedDict(
                    [
                        ("total", None),
                        ("2025", None),
                        ("2024", None),
                        ("2023", None),
                        ("2022", None),
                        ("2021", None),
                        ("2020", None),
                        ("2019", None),
                        ("2018", None),
                        ("2017", None),
                        ("2016", None),
                        ("2015", None),
                    ]
                ),
            ),
            (
                "publication",
                OrderedDict(
                    [
                        ("journal", None),
                        ("journal_source", None),
                        ("short_journal", None),
                        ("short_journal_source", None),
                        ("impact_factor", None),
                        ("impact_factor_source", None),
                        ("issn", None),
                        ("issn_source", None),
                        ("volume", None),
                        ("volume_source", None),
                        ("issue", None),
                        ("issue_source", None),
                        ("first_page", None),
                        ("first_source", None),
                        ("last_page", None),
                        ("last_page_source", None),
                        ("publisher", None),
                        ("publisher_source", None),
                    ]
                ),
            ),
            (
                "url",
                OrderedDict(
                    [
                        ("doi", None),
                        ("doi_source", None),
                        ("publisher", None),
                        ("publisher_source", None),
                        ("openurl_query", None),
                        ("openurl_source", None),
                        ("openurl_resolved", []),
                        ("openurl_resolved_source", []),
                        ("pdfs", []),
                        ("pdfs_source", []),
                        ("supplementary_files", []),
                        ("supplementary_files_source", []),
                        ("additional_files", []),
                        ("additional_files_source", []),
                    ]
                ),
            ),
            (
                "paths",
                OrderedDict(
                    [
                        ("pdfs", []),
                        ("pdfs_source", []),
                        ("supplementary_files", []),
                        ("supplementary_files_source", []),
                        ("additional_files", []),
                        ("additional_files_source", []),
                    ]
                ),
            ),
            (
                "system",
                OrderedDict(
                    [
                        ("searched_by_arXiv", None),
                        ("searched_by_CrossRef", None),
                        ("searched_by_OpenAlex", None),
                        ("searched_by_PubMed", None),
                        ("searched_by_Semantic_Scholar", None),
                        ("searched_by_URL", None),
                    ]
                ),
            ),
        ]
    )

    # Deep update with existing metadata
    for section_key, section_data in metadata.items():
        if section_key in complete_structure:
            if isinstance(complete_structure[section_key], dict):
                complete_structure[section_key].update(section_data)
            else:
                complete_structure[section_key] = section_data

    return complete_structure


# def to_complete_metadata_structure(metadata):
#     """Initialize all required fields with null values."""
#     complete_structure = OrderedDict(
#         [
#             # Core identification
#             (
#                 "id",
#                 ("doi", None),
#                 ("doi_source", None),
#                 ("arxiv_id", None),
#                 ("arxiv_id_source", None),
#                 ("pmid", None),
#                 ("pmid_source", None),
#                 ("scholar_id", None),
#                 ("scholar_id_source", None),
#             ),
#             (
#                 "basic",
#                 ("title", None),
#                 ("title_source", None),
#                 ("authors", None),
#                 ("authors_source", None),
#                 ("year", None),
#                 ("year_source", None),
#                 ("abstract", None),
#                 ("abstract_source", None),
#                 ("citation_count", None),
#                 ("citation_source", None),
#             ),
#             (
#                 "journal",
#                 ("journal", None),
#                 ("journal_source", None),
#                 ("impact_factor", None),
#                 ("impact_factor_source", None),
#                 ("issn", None),
#                 ("issn_source", None),
#                 ("volume", None),
#                 ("volume_source", None),
#                 ("issue", None),
#                 ("issue_source", None),
#                 # Metrics
#             )(
#                 "urls",
#                 {
#                     "url_doi": None,
#                     "url_doi_source": None,
#                     "url_publisher": None,
#                     "url_publisher_source": None,
#                     "url_openurl_query": None,
#                     "url_openurl_source": None,
#                     "url_openurl_resolved": [],
#                     "url_openurl_resolved_source": [],
#                     "url_pdf": [],
#                     "url_pdf_source": [],
#                     "url_supplementary": [],
#                     "url_supplementary_source": [],
#                 },
#             ),
#         ]
#     )

#     # Update with existing metadata
#     complete_structure.update(metadata)
#     return complete_structure


# EOF
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-08-14 06:53:44 (ywatanabe)"
# # File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/utils/_to_complete_metadata_structure.py
# # ----------------------------------------
# from __future__ import annotations
# import os
# __FILE__ = (
#     "./src/scitex/scholar/metadata/doi/utils/_to_complete_metadata_structure.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------

# from collections import OrderedDict

# def to_complete_metadata_structure(metadata):
#     """Initialize all required fields with null values."""
#     complete_structure = {
#         # Core identification
#         "doi": None,
#         "doi_source": None,
#         "arxiv_id": None,
#         "arxiv_id_source": None,
#         "pmid": None,
#         "pmid_source": None,
#         "scholar_id": None,
#         # Basic metadata
#         "title": None,
#         "title_source": None,
#         "authors": None,
#         "authors_source": None,
#         "year": None,
#         "year_source": None,
#         # Publication details
#         "journal": None,
#         "journal_source": None,
#         "issn": None,
#         "issn_source": None,
#         "volume": None,
#         "volume_source": None,
#         "issue": None,
#         "issue_source": None,
#         # Content
#         "abstract": None,
#         "abstract_source": None,
#         # Metrics
#         "impact_factor": None,
#         "impact_factor_source": None,
#         "citation_count": None,
#         "citation_source": None,
#         # URLs
#         "urls": {
#             "url_doi": None,
#             "url_doi_source": None,
#             "url_publisher": None,
#             "url_publisher_source": None,
#             "url_openurl_query": None,
#             "url_openurl_source": None,
#             "url_openurl_resolved": [],
#             "url_openurl_resolved_source": [],
#             "url_pdf": [],
#             "url_pdf_source": [],
#             "url_supplementary": [],
#             "url_supplementary_source": [],
#         },
#     }

#     # Update with existing metadata
#     complete_structure.update(metadata)
#     return complete_structure

# # EOF

# EOF
