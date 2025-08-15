#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 10:40:07 (ywatanabe)"
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

BASE_STRUCTURE = OrderedDict(
    [
        (
            "id",
            OrderedDict(
                [
                    ("doi", None),
                    ("doi_engines", None),
                    ("arxiv_id", None),
                    ("arxiv_id_engines", None),
                    ("pmid", None),
                    ("pmid_engines", None),
                    ("scholar_id", None),
                    ("scholar_id_engines", None),
                ]
            ),
        ),
        (
            "basic",
            OrderedDict(
                [
                    ("title", None),
                    ("title_engines", None),
                    ("authors", None),
                    ("authors_engines", None),
                    ("year", None),
                    ("year_engines", None),
                    ("abstract", None),
                    ("abstract_engines", None),
                    ("keywords", None),
                    ("keywords_engines", None),
                    ("type", None),
                    ("type_engines", None),
                ]
            ),
        ),
        (
            "citation_count",
            OrderedDict(
                [
                    ("total", None),
                    ("total_engines", None),
                    ("2025", None),
                    ("2025_engines", None),
                    ("2024", None),
                    ("2024_engines", None),
                    ("2023", None),
                    ("2023_engines", None),
                    ("2022", None),
                    ("2022_engines", None),
                    ("2021", None),
                    ("2021_engines", None),
                    ("2020", None),
                    ("2020_engines", None),
                    ("2019", None),
                    ("2019_engines", None),
                    ("2018", None),
                    ("2018_engines", None),
                    ("2017", None),
                    ("2017_engines", None),
                    ("2016", None),
                    ("2016_engines", None),
                    ("2015", None),
                    ("2015_engines", None),
                ]
            ),
        ),
        (
            "publication",
            OrderedDict(
                [
                    ("journal", None),
                    ("journal_engines", None),
                    ("short_journal", None),
                    ("short_journal_engines", None),
                    ("impact_factor", None),
                    ("impact_factor_engines", None),
                    ("issn", None),
                    ("issn_engines", None),
                    ("volume", None),
                    ("volume_engines", None),
                    ("issue", None),
                    ("issue_engines", None),
                    ("first_page", None),
                    ("first_page_engines", None),
                    ("last_page", None),
                    ("last_page_engines", None),
                    ("publisher", None),
                    ("publisher_engines", None),
                ]
            ),
        ),
        (
            "url",
            OrderedDict(
                [
                    ("doi", None),
                    ("doi_engines", None),
                    ("publisher", None),
                    ("publisher_engines", None),
                    ("openurl_query", None),
                    ("openurl_engines", None),
                    ("openurl_resolved", []),
                    ("openurl_resolved_engines", []),
                    ("pdfs", []),
                    ("pdfs_engines", []),
                    ("supplementary_files", []),
                    ("supplementary_files_engines", []),
                    ("additional_files", []),
                    ("additional_files_engines", []),
                ]
            ),
        ),
        (
            "path",
            OrderedDict(
                [
                    ("pdfs", []),
                    ("pdfs_engines", []),
                    ("supplementary_files", []),
                    ("supplementary_files_engines", []),
                    ("additional_files", []),
                    ("additional_files_engines", []),
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


def to_complete_metadata_structure(metadata):
    """Initialize all required fields with null values."""
    import copy

    complete_structure = copy.deepcopy(BASE_STRUCTURE)

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
#                 ("doi_engine", None),
#                 ("arxiv_id", None),
#                 ("arxiv_id_engine", None),
#                 ("pmid", None),
#                 ("pmid_engine", None),
#                 ("scholar_id", None),
#                 ("scholar_id_engine", None),
#             ),
#             (
#                 "basic",
#                 ("title", None),
#                 ("title_engine", None),
#                 ("authors", None),
#                 ("authors_engine", None),
#                 ("year", None),
#                 ("year_engine", None),
#                 ("abstract", None),
#                 ("abstract_engine", None),
#                 ("citation_count", None),
#                 ("citation_engine", None),
#             ),
#             (
#                 "journal",
#                 ("journal", None),
#                 ("journal_engine", None),
#                 ("impact_factor", None),
#                 ("impact_factor_engine", None),
#                 ("issn", None),
#                 ("issn_engine", None),
#                 ("volume", None),
#                 ("volume_engine", None),
#                 ("issue", None),
#                 ("issue_engine", None),
#                 # Metrics
#             )(
#                 "urls",
#                 {
#                     "url_doi": None,
#                     "url_doi_engine": None,
#                     "url_publisher": None,
#                     "url_publisher_engine": None,
#                     "url_openurl_query": None,
#                     "url_openurl_engine": None,
#                     "url_openurl_resolved": [],
#                     "url_openurl_resolved_engine": [],
#                     "url_pdf": [],
#                     "url_pdf_engine": [],
#                     "url_supplementary": [],
#                     "url_supplementary_engine": [],
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
#         "doi_engine": None,
#         "arxiv_id": None,
#         "arxiv_id_engine": None,
#         "pmid": None,
#         "pmid_engine": None,
#         "scholar_id": None,
#         # Basic metadata
#         "title": None,
#         "title_engine": None,
#         "authors": None,
#         "authors_engine": None,
#         "year": None,
#         "year_engine": None,
#         # Publication details
#         "journal": None,
#         "journal_engine": None,
#         "issn": None,
#         "issn_engine": None,
#         "volume": None,
#         "volume_engine": None,
#         "issue": None,
#         "issue_engine": None,
#         # Content
#         "abstract": None,
#         "abstract_engine": None,
#         # Metrics
#         "impact_factor": None,
#         "impact_factor_engine": None,
#         "citation_count": None,
#         "citation_engine": None,
#         # URLs
#         "urls": {
#             "url_doi": None,
#             "url_doi_engine": None,
#             "url_publisher": None,
#             "url_publisher_engine": None,
#             "url_openurl_query": None,
#             "url_openurl_engine": None,
#             "url_openurl_resolved": [],
#             "url_openurl_resolved_engine": [],
#             "url_pdf": [],
#             "url_pdf_engine": [],
#             "url_supplementary": [],
#             "url_supplementary_engine": [],
#         },
#     }

#     # Update with existing metadata
#     complete_structure.update(metadata)
#     return complete_structure

# # EOF

# EOF
