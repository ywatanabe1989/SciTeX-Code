#!/usr/bin/env python3
"""Download PDFs with preserved metadata from enriched BibTeX."""

import asyncio
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from scitex.scholar import Scholar
from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader
from scitex import logging

logger = logging.getLogger(__name__)

async def download_pdfs_with_metadata(bibtex_path: str, project: str):
    """Download PDFs while preserving enriched metadata."""

    # Initialize Scholar
    scholar = Scholar(project=project)

    # Load enriched papers from BibTeX
    papers = scholar.load_bibtex(bibtex_path)
    logger.info(f"Loaded {len(papers)} papers from {bibtex_path}")

    # Filter papers with DOIs
    papers_with_dois = [p for p in papers if p.doi]
    logger.info(f"Found {len(papers_with_dois)} papers with DOIs")

    # Get authenticated browser context
    browser, context = await scholar._browser_manager.get_authenticated_browser_and_context_async()

    # Initialize URL finder and PDF downloader
    url_finder = ScholarURLFinder(context=context, config=scholar.config, use_cache=True)
    pdf_downloader = ScholarPDFDownloader(context=context, config=scholar.config, use_cache=True)

    # Get library paths
    library_dir = scholar.config.get_library_dir()
    master_dir = library_dir / "MASTER"
    project_dir = library_dir / project
    master_dir.mkdir(parents=True, exist_ok=True)
    project_dir.mkdir(parents=True, exist_ok=True)

    results = {"downloaded": 0, "failed": 0, "errors": 0}

    for paper in papers_with_dois:
        try:
            doi = paper.doi
            logger.info(f"Processing: {paper.title[:50]}... (DOI: {doi})")

            # Find URLs for the DOI
            urls = await url_finder.find_urls(doi)
            pdf_urls = urls.get("urls_pdf", [])

            if not pdf_urls:
                logger.warning(f"No PDF URLs found for: {paper.title[:50]}...")
                results["failed"] += 1
                continue

            # Try to download PDF
            downloaded_path = None
            for pdf_entry in pdf_urls:
                pdf_url = pdf_entry.get("url") if isinstance(pdf_entry, dict) else pdf_entry
                if not pdf_url:
                    continue

                # Download to temp location
                temp_output = Path("/tmp") / f"{doi.replace('/', '_').replace(':', '_')}.pdf"
                result = await pdf_downloader.download_from_url(pdf_url=pdf_url, output_path=temp_output)

                if result and result.exists():
                    downloaded_path = result
                    break

            if downloaded_path:
                # Generate unique ID from DOI
                paper_id = hashlib.md5(doi.encode()).hexdigest()[:8].upper()

                # Create MASTER storage directory
                storage_path = master_dir / paper_id
                storage_path.mkdir(parents=True, exist_ok=True)

                # Generate readable name from ENRICHED metadata with metrics
                # Citation count (6 digits, zero-padded)
                citation_count = paper.citation_count if paper.citation_count else 0
                cc_str = f"CC{citation_count:06d}"

                # Impact factor (3 digits integer part only)
                impact_factor = paper.journal_impact_factor if paper.journal_impact_factor else 0.0
                if_int = int(impact_factor)  # 32.1 becomes 32, displayed as 032
                if_str = f"IF{if_int:03d}"

                # Year (4 digits)
                year_str = f"{paper.year:04d}" if paper.year else "0000"

                # First author last name
                first_author = "Unknown"
                if paper.authors and len(paper.authors) > 0:
                    author_parts = paper.authors[0].split()
                    first_author = author_parts[-1] if len(author_parts) > 1 else author_parts[0]
                    # Clean author name - remove special chars
                    first_author = "".join(c for c in first_author if c.isalnum() or c == "-")[:20]  # Limit length

                # Journal name (cleaned)
                journal_clean = "Unknown"
                if paper.journal:
                    journal_clean = "".join(c for c in paper.journal if c.isalnum() or c in " ").replace(" ", "")[:30]  # Limit length
                    if not journal_clean:
                        journal_clean = "Unknown"

                # Format: CC000000-IF032-2016-Author-Journal
                readable_name = f"{cc_str}-{if_str}-{year_str}-{first_author}-{journal_clean}"

                # Copy PDF to MASTER storage
                pdf_filename = f"DOI_{doi.replace('/', '_').replace(':', '_')}.pdf"
                master_pdf_path = storage_path / pdf_filename
                shutil.copy2(downloaded_path, master_pdf_path)

                # Create comprehensive metadata from ENRICHED paper
                metadata = {
                    "doi": doi,
                    "scitex_id": paper_id,
                    "created_at": datetime.now().isoformat(),
                    "created_by": "SciTeX Scholar",
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.year,
                    "journal": paper.journal,
                    "abstract": paper.abstract,
                    "citation_count": paper.citation_count,
                    "journal_impact_factor": paper.journal_impact_factor,
                    "keywords": paper.keywords,
                    "url": paper.url,
                    "pdf_url": paper.pdf_url,
                    "publisher": paper.publisher,
                    "volume": paper.volume,
                    "issue": paper.issue,
                    "pages": paper.pages,
                    "pdf_path": f"MASTER/{paper_id}/{pdf_filename}",
                    "pdf_downloaded_at": datetime.now().isoformat(),
                    "pdf_size_bytes": master_pdf_path.stat().st_size,
                    "updated_at": datetime.now().isoformat()
                }

                # Save metadata
                metadata_file = storage_path / "metadata.json"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

                # Create symlink in project directory
                project_link = project_dir / readable_name
                if not project_link.exists():
                    project_link.symlink_to(f"../MASTER/{paper_id}")

                # Clean up temp file
                downloaded_path.unlink()

                logger.success(f"Downloaded: {readable_name} -> MASTER/{paper_id}")
                results["downloaded"] += 1
            else:
                logger.warning(f"Failed to download: {paper.title[:50]}...")
                results["failed"] += 1

        except Exception as e:
            logger.error(f"Error processing {paper.title[:50]}...: {e}")
            results["errors"] += 1
            results["failed"] += 1

    await scholar._browser_manager.close()
    logger.info(f"Download complete: {results}")
    return results

if __name__ == "__main__":
    # Run the download
    asyncio.run(download_pdfs_with_metadata("data/neurovista_enriched.bib", "neurovista"))