#!/usr/bin/env python3
"""
Update symlinks utility for Scholar library.
This utility updates all symlinks in a project to reflect current status:
- Citation count (CITED)
- PDF availability (PDFo/PDFx)
- Impact factor (IF)
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._LibraryManager import LibraryManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SymlinkUpdater:
    """Utility to update Scholar library symlinks with current status."""

    def __init__(self, project: str = None):
        """Initialize the symlink updater.

        Args:
            project: Project name to update symlinks for. If None, updates all projects.
        """
        self.config = ScholarConfig()
        self.library_dir = self.config.get_library_dir()
        self.library_manager = LibraryManager(self.config)
        self.project = project

    def get_projects(self) -> List[str]:
        """Get list of projects to update.

        Returns:
            List of project directory names.
        """
        if self.project:
            project_dir = self.library_dir / self.project
            if not project_dir.exists():
                logger.error(f"Project {self.project} does not exist")
                return []
            return [self.project]

        # Get all project directories (exclude MASTER)
        projects = []
        for d in self.library_dir.iterdir():
            if d.is_dir() and d.name != "MASTER":
                projects.append(d.name)
        return sorted(projects)

    def parse_existing_symlink(self, symlink_path: Path) -> Optional[Dict]:
        """Parse information from existing symlink name.

        Args:
            symlink_path: Path to the symlink.

        Returns:
            Dictionary with parsed information or None if not parseable.
        """
        name = symlink_path.name

        # Try to parse the standard format: CITED{count}-PDF{status}-IF{factor}-{year}-{author}-{journal}
        pattern = r'^CITED(\d+)-PDF([ox])-IF(\d+)-(\d{4})-(.+?)-(.+?)$'
        match = re.match(pattern, name)

        if match:
            return {
                'cited_count': int(match.group(1)),
                'pdf_status': match.group(2),
                'impact_factor': int(match.group(3)),
                'year': match.group(4),
                'author': match.group(5),
                'journal': match.group(6)
            }

        # Try older format without all fields
        # Just extract what we can
        info = {}
        if 'CITED' in name:
            cited_match = re.search(r'CITED(\d+)', name)
            if cited_match:
                info['cited_count'] = int(cited_match.group(1))

        if 'PDF' in name:
            pdf_match = re.search(r'PDF([ox])', name)
            if pdf_match:
                info['pdf_status'] = pdf_match.group(1)

        if 'IF' in name:
            if_match = re.search(r'IF(\d+)', name)
            if if_match:
                info['impact_factor'] = int(if_match.group(1))

        # Extract year if present
        year_match = re.search(r'-(\d{4})-', name)
        if year_match:
            info['year'] = year_match.group(1)

        return info if info else None

    def get_paper_status(self, master_id: str) -> Dict:
        """Get current status of a paper from MASTER storage.

        Args:
            master_id: The 8-character master ID.

        Returns:
            Dictionary with current paper status.
        """
        master_path = self.library_dir / "MASTER" / master_id
        status = {
            'pdf_available': False,
            'cited_count': 0,
            'impact_factor': 0,
            'metadata': {}
        }

        if not master_path.exists():
            return status

        # Check for PDFs
        pdf_files = list(master_path.glob("*.pdf"))
        status['pdf_available'] = len(pdf_files) > 0

        # Load metadata if available
        metadata_path = master_path / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    status['metadata'] = metadata

                    # Extract citation count
                    if 'citationCount' in metadata:
                        status['cited_count'] = int(metadata.get('citationCount', 0))
                    elif 'citation_count' in metadata:
                        status['cited_count'] = int(metadata.get('citation_count', 0))

                    # Extract impact factor
                    if 'journal_impact_factor' in metadata:
                        status['impact_factor'] = float(metadata.get('journal_impact_factor', 0))
                    elif 'impact_factor' in metadata:
                        status['impact_factor'] = float(metadata.get('impact_factor', 0))

            except Exception as e:
                logger.warning(f"Failed to load metadata for {master_id}: {e}")

        return status

    def create_updated_symlink_name(self, master_id: str, existing_info: Optional[Dict] = None) -> str:
        """Create an updated symlink name based on current status.

        Args:
            master_id: The 8-character master ID.
            existing_info: Information parsed from existing symlink name.

        Returns:
            New symlink name with updated status.
        """
        status = self.get_paper_status(master_id)
        metadata = status['metadata']

        # Get components for the new name
        cited_count = status['cited_count']
        pdf_status = "PDFo" if status['pdf_available'] else "PDFx"
        impact_factor = int(status['impact_factor'])

        # Try to get year, author, journal from metadata or existing info
        year = metadata.get('year', '')
        if not year and existing_info:
            year = existing_info.get('year', '')
        if not year:
            year = "0000"

        # Get first author
        authors = metadata.get('authors', [])
        if authors and isinstance(authors, list) and authors[0]:
            if isinstance(authors[0], dict):
                first_author = authors[0].get('name', '').split()[0] if authors[0].get('name') else 'Unknown'
            else:
                first_author = str(authors[0]).split()[0] if authors[0] else 'Unknown'
        elif existing_info and existing_info.get('author'):
            first_author = existing_info['author']
        else:
            first_author = 'Unknown'

        # Clean author name
        first_author = re.sub(r'[^\w\-]', '', first_author)[:20]  # Max 20 chars

        # Get journal
        journal = metadata.get('journal', '')
        if not journal and metadata.get('venue'):
            journal = metadata['venue']
        if not journal and existing_info:
            journal = existing_info.get('journal', '')
        if not journal:
            journal = 'Unknown'

        # Clean journal name
        journal = re.sub(r'[^\w\-]', '-', journal)
        journal = re.sub(r'-+', '-', journal).strip('-')[:30]  # Max 30 chars

        # Create the new name
        new_name = f"CITED{cited_count:06d}-{pdf_status}-IF{impact_factor:03d}-{year}-{first_author}-{journal}"

        return new_name

    def update_symlink(self, symlink_path: Path) -> Tuple[bool, str]:
        """Update a single symlink to reflect current status.

        Args:
            symlink_path: Path to the symlink to update.

        Returns:
            Tuple of (success, message).
        """
        if not symlink_path.is_symlink():
            return False, f"{symlink_path} is not a symlink"

        # Get the target (MASTER ID)
        try:
            target = symlink_path.resolve()

            # Skip non-MASTER symlinks (like bibtex files)
            if "MASTER" not in str(target):
                return True, f"Skipped non-MASTER symlink: {symlink_path.name}"

            master_id = target.name

            # Parse existing symlink info
            existing_info = self.parse_existing_symlink(symlink_path)

            # Create new symlink name
            new_name = self.create_updated_symlink_name(master_id, existing_info)

            # Check if name needs updating
            if symlink_path.name == new_name:
                return True, f"Already up to date: {symlink_path.name}"

            # Create new symlink path
            new_symlink_path = symlink_path.parent / new_name

            # Check if new path already exists
            if new_symlink_path.exists() and new_symlink_path != symlink_path:
                return False, f"Target already exists: {new_symlink_path}"

            # Remove old symlink and create new one
            symlink_path.unlink()
            new_symlink_path.symlink_to(target)

            return True, f"Updated: {symlink_path.name} -> {new_name}"

        except Exception as e:
            return False, f"Failed to update {symlink_path}: {e}"

    def update_project_symlinks(self, project: str) -> Dict:
        """Update all symlinks in a project.

        Args:
            project: Project name.

        Returns:
            Dictionary with update statistics.
        """
        project_dir = self.library_dir / project
        stats = {
            'total': 0,
            'updated': 0,
            'already_current': 0,
            'failed': 0,
            'messages': []
        }

        # Find all symlinks in the project directory
        symlinks = [p for p in project_dir.iterdir() if p.is_symlink()]
        stats['total'] = len(symlinks)

        logger.info(f"Found {stats['total']} symlinks in project {project}")

        for symlink in symlinks:
            success, message = self.update_symlink(symlink)

            if success:
                if "Already up to date" in message:
                    stats['already_current'] += 1
                else:
                    stats['updated'] += 1
                    logger.info(message)
            else:
                stats['failed'] += 1
                logger.warning(message)

            stats['messages'].append(message)

        return stats

    def run(self) -> None:
        """Run the symlink update process."""
        projects = self.get_projects()

        if not projects:
            logger.error("No projects found to update")
            return

        total_stats = {
            'projects': len(projects),
            'total_symlinks': 0,
            'total_updated': 0,
            'total_current': 0,
            'total_failed': 0
        }

        for project in projects:
            logger.info(f"\nUpdating project: {project}")
            logger.info("-" * 50)

            stats = self.update_project_symlinks(project)

            # Update totals
            total_stats['total_symlinks'] += stats['total']
            total_stats['total_updated'] += stats['updated']
            total_stats['total_current'] += stats['already_current']
            total_stats['total_failed'] += stats['failed']

            # Print project summary
            logger.info(f"Project {project} summary:")
            logger.info(f"  Total symlinks: {stats['total']}")
            logger.info(f"  Updated: {stats['updated']}")
            logger.info(f"  Already current: {stats['already_current']}")
            logger.info(f"  Failed: {stats['failed']}")

        # Print overall summary
        logger.info("\n" + "=" * 50)
        logger.info("Overall Summary:")
        logger.info(f"  Projects processed: {total_stats['projects']}")
        logger.info(f"  Total symlinks: {total_stats['total_symlinks']}")
        logger.info(f"  Updated: {total_stats['total_updated']}")
        logger.info(f"  Already current: {total_stats['total_current']}")
        logger.info(f"  Failed: {total_stats['total_failed']}")


def main():
    """Main entry point for the update_symlinks utility."""
    parser = argparse.ArgumentParser(
        description="Update Scholar library symlinks to reflect current status"
    )
    parser.add_argument(
        "--project",
        "-p",
        help="Project name to update. If not specified, updates all projects."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    updater = SymlinkUpdater(project=args.project)
    updater.run()


if __name__ == "__main__":
    main()