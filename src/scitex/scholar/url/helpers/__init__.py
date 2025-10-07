from .finders import find_pdf_urls
# , find_supplementary_urls
from .resolvers._resolve_functions import (
    normalize_doi_as_http,
    resolve_publisher_url_by_navigating_to_doi_page,
    extract_doi_from_url,
    resolve_openurl,
)
