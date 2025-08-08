#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 13:43:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/openurl_resolve_urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/openurl_resolve_urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-08-01 02:43:00 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/resolve_urls/__main__.py
# # ----------------------------------------
# from __future__ import annotations
# import os
# __FILE__ = (
#     "./src/scitex/scholar/open_url/resolve_urls/__main__.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------

# """Command-line interface for resumable OpenURL resolution.

# Usage:
#     python -m scitex.scholar.open_url.resolve_urls dois.txt [--output results.json] [--progress progress.json]

# Examples:
#     # Resolve URLs from DOI list
#     python -m scitex.scholar.open_url.resolve_urls dois.txt

#     # Resume interrupted resolution
#     python -m scitex.scholar.open_url.resolve_urls dois.txt --progress openurl_20250801.progress.json

#     # Save results to JSON
#     python -m scitex.scholar.open_url.resolve_urls dois.txt --output resolved_urls.json

#     # Use specific resolver
#     python -m scitex.scholar.open_url.resolve_urls dois.txt --resolver https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# """

# import argparse
# import asyncio
# import json
# import sys
# from pathlib import Path

# from scitex import logging
# from scitex.scholar.auth import AuthenticationManager
# from .._ResumableOpenURLResolver import ResumableOpenURLResolver

# logger = logging.getLogger(__name__)


# def main():
#     """Main CLI function for OpenURL resolution."""
#     parser = argparse.ArgumentParser(
#         description="Resolve publisher URLs via OpenURL with resume capability",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   # Resolve URLs from DOI list file
#   python -m scitex.scholar.open_url.resolve_urls dois.txt

#   # Resume interrupted resolution
#   python -m scitex.scholar.open_url.resolve_urls dois.txt --progress openurl_resolution.progress.json

#   # Save results to JSON
#   python -m scitex.scholar.open_url.resolve_urls dois.txt --output resolved_urls.json

#   # Use specific OpenURL resolver
#   python -m scitex.scholar.open_url.resolve_urls dois.txt --resolver https://unimelb.hosted.exlibrisgroup.com/sfxlcl41

#   # Authenticate first
#   python -m scitex.scholar.open_url.resolve_urls dois.txt --authenticate_async

# This command will:
# - Load DOIs from text file (one per line) or JSON
# - Resolve publisher URLs via institutional OpenURL resolver
# - Use OpenAthens authentication for access
# - Save progress automatically (can resume if interrupted)
# - Handle rate limits and errors gracefully
#         """
#     )

#     parser.add_argument(
#         "input",
#         type=str,
#         help="Input file with DOIs (text file with one DOI per line, or JSON)"
#     )

#     parser.add_argument(
#         "--output",
#         "-o",
#         type=str,
#         help="Output file for results (JSON format)"
#     )

#     parser.add_argument(
#         "--progress",
#         "-p",
#         type=str,
#         help="Progress file to resume from (or create)"
#     )

#     parser.add_argument(
#         "--resolver",
#         "-r",
#         type=str,
#         help="OpenURL resolver URL (defaults to SCITEX_SCHOLAR_OPENURL_RESOLVER_URL)"
#     )

#     parser.add_argument(
#         "--authenticate_async",
#         "-a",
#         action="store_true",
#         help="Authenticate with OpenAthens before resolution"
#     )

#     parser.add_argument(
#         "--concurrency",
#         "-c",
#         type=int,
#         default=2,
#         help="Maximum concurrent resolutions (default: 2)"
#     )

#     parser.add_argument(
#         "--quiet",
#         "-q",
#         action="store_true",
#         help="Suppress progress output"
#     )

#     parser.add_argument(
#         "--verbose",
#         "-v",
#         action="store_true",
#         help="Show detailed progress"
#     )

#     args = parser.parse_args()

#     # Load DOIs
#     input_path = Path(args.input)
#     if not input_path.exists():
#         logger.fail(f"Input file not found: {input_path}")
#         sys.exit(1)

#     dois = _load_dois(input_path)
#     if not dois:
#         logger.fail("No DOIs found in input file")
#         sys.exit(1)

#     # Configure logging
#     if args.quiet:
#         logging.disable(logging.INFO)
#     elif args.verbose:
#         logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)

#     try:
#         # Run async main
#         asyncio.run(_async_main_async(args, dois))

#     except KeyboardInterrupt:
#         logger.warning("\nOpenURL resolution interrupted - progress saved")
#         sys.exit(1)
#     except Exception as e:
#         logger.fail(f"OpenURL resolution failed: {e}")
#         if args.verbose:
#             import traceback
#             traceback.print_exc()
#         sys.exit(1)


# async def _async_main_async(args, dois):
#     """Async main function."""
#     # Create auth manager
#     auth_manager = AuthenticationManager()

#     # Authenticate if requested
#     if args.authenticate_async:
#         logger.info("Authenticating with OpenAthens...")
#         await auth_manager.authenticate_async()

#     # Check authentication
#     if not await auth_manager.is_authenticate_async():
#         logger.warning("Not authenticate_async - some resources may not be accessible")
#         logger.info("Use --authenticate_async flag to log in with OpenAthens")

#     # Create resolver
#     progress_file = Path(args.progress) if args.progress else None
#     resolver = ResumableOpenURLResolver(
#         auth_manager=auth_manager,
#         resolver_url=args.resolver,
#         progress_file=progress_file,
#         concurrency=args.concurrency
#     )

#     # Show status
#     if not args.quiet:
#         if progress_file and progress_file.exists():
#             logger.info(f"Resuming from progress file: {progress_file}")
#         else:
#             logger.info(f"Resolving URLs for {len(dois)} DOIs")
#             if resolver.resolver_url:
#                 logger.info(f"Using resolver: {resolver.resolver_url}")

#     # Resolve URLs
#     results = await resolver.resolve_from_dois_async(dois)

#     # Save results if requested
#     if args.output:
#         output_path = Path(args.output)
#         # Convert to simple doi->url mapping
#         simple_results = {}
#         for doi, result in results.items():
#             if result.get("final_url"):
#                 simple_results[doi] = result["final_url"]

#         with open(output_path, 'w') as f:
#             json.dump(simple_results, f, indent=2)
#         logger.success(f"Results saved to: {output_path}")

#     # Show sample results
#     if not args.quiet and results:
#         logger.info("\nSample results:")
#         for i, (doi, result) in enumerate(list(results.items())[:5]):
#             if result.get("final_url"):
#                 logger.info(f"  {doi} -> {result['final_url']}")
#         if len(results) > 5:
#             logger.info(f"  ... and {len(results) - 5} more")


# def _load_dois(input_path: Path) -> list:
#     """Load DOIs from input file."""
#     dois = []

#     # Try JSON first
#     if input_path.suffix.lower() == '.json':
#         try:
#             with open(input_path, 'r') as f:
#                 data = json.load(f)

#             # Handle different JSON formats
#             if isinstance(data, list):
#                 dois = data
#             elif isinstance(data, dict):
#                 # Try common keys
#                 for key in ['dois', 'DOIs', 'doi_list', 'articles']:
#                     if key in data and isinstance(data[key], list):
#                         dois = data[key]
#                         break
#                 else:
#                     # Extract DOIs from values
#                     for value in data.values():
#                         if isinstance(value, str) and value.startswith('10.'):
#                             dois.append(value)

#             logger.info(f"Loaded {len(dois)} DOIs from JSON")
#             return dois
#         except:
#             pass

#     # Try text file (one DOI per line)
#     try:
#         with open(input_path, 'r') as f:
#             for line in f:
#                 line = line.strip()
#                 if line and line.startswith('10.'):
#                     dois.append(line)

#         logger.info(f"Loaded {len(dois)} DOIs from text file")
#         return dois
#     except Exception as e:
#         logger.error(f"Failed to load DOIs: {e}")
#         return []


# if __name__ == "__main__":
#     main()

# # EOF

# EOF
