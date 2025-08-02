#!/usr/bin/env python3
"""MCP server for SciTeX Scholar - Scientific literature management."""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Handle potential import issues
try:
    from scitex.scholar import Scholar, Papers, Paper
    from scitex.scholar.download import Crawl4AIDownloadStrategy
    from scitex.scholar.resolve_dois import ResumableDOIResolver
    from scitex.scholar.open_url import ResumableOpenURLResolver
    from scitex.scholar.validation import PDFValidator
    from scitex.scholar.database import PaperDatabase
    from scitex.scholar.search import SemanticSearchEngine
    SCHOLAR_AVAILABLE = True
except ImportError as e:
    SCHOLAR_AVAILABLE = False
    import_error = str(e)


# Global instances
server = Server("scitex-scholar")
scholar_instance = None
crawl4ai_configs = {}
download_batches = {}


def ensure_scholar():
    """Ensure Scholar instance is initialized."""
    global scholar_instance
    if not SCHOLAR_AVAILABLE:
        raise RuntimeError(f"SciTeX Scholar not available: {import_error}")
    if scholar_instance is None:
        scholar_instance = Scholar()
    return scholar_instance


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Scholar tools."""
    tools = []
    
    # Search tools
    tools.append(types.Tool(
        name="search_papers",
        description="Search for scientific papers across multiple databases",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 20},
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources to search (pubmed, crossref, semantic_scholar, etc.)"
                }
            },
            "required": ["query"]
        }
    ))
    
    tools.append(types.Tool(
        name="search_quick",
        description="Quick search returning only paper titles",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_n": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    ))
    
    # BibTeX tools
    tools.append(types.Tool(
        name="parse_bibtex",
        description="Parse a BibTeX file and return paper objects",
        inputSchema={
            "type": "object",
            "properties": {
                "bibtex_path": {"type": "string", "description": "Path to BibTeX file"}
            },
            "required": ["bibtex_path"]
        }
    ))
    
    tools.append(types.Tool(
        name="enrich_bibtex",
        description="Enrich BibTeX with DOIs, impact factors, and citations",
        inputSchema={
            "type": "object",
            "properties": {
                "bibtex_path": {"type": "string"},
                "output_path": {"type": "string"},
                "add_abstracts": {"type": "boolean", "default": True},
                "add_impact_factors": {"type": "boolean", "default": True}
            },
            "required": ["bibtex_path"]
        }
    ))
    
    # Resolution tools
    tools.append(types.Tool(
        name="resolve_dois",
        description="Resolve DOIs from paper titles (resumable)",
        inputSchema={
            "type": "object",
            "properties": {
                "papers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "authors": {"type": "array", "items": {"type": "string"}},
                            "year": {"type": "integer"}
                        }
                    }
                },
                "progress_file": {"type": "string", "description": "Path to progress file for resumability"}
            },
            "required": ["papers"]
        }
    ))
    
    tools.append(types.Tool(
        name="resolve_openurls",
        description="Resolve publisher URLs via OpenURL (resumable)",
        inputSchema={
            "type": "object",
            "properties": {
                "dois": {"type": "array", "items": {"type": "string"}},
                "resolver_url": {"type": "string", "description": "OpenURL resolver URL"},
                "progress_file": {"type": "string"}
            },
            "required": ["dois"]
        }
    ))
    
    # Download tools
    tools.append(types.Tool(
        name="download_pdf",
        description="Download a single PDF using the best available strategy",
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {"type": "string"},
                "output_dir": {"type": "string", "default": "./pdfs"},
                "strategy": {
                    "type": "string",
                    "enum": ["auto", "crawl4ai", "zenrows", "direct"],
                    "default": "auto"
                }
            },
            "required": ["doi"]
        }
    ))
    
    tools.append(types.Tool(
        name="download_pdfs_batch",
        description="Download multiple PDFs with progress tracking",
        inputSchema={
            "type": "object",
            "properties": {
                "dois": {"type": "array", "items": {"type": "string"}},
                "output_dir": {"type": "string", "default": "./pdfs"},
                "strategy": {"type": "string", "default": "auto"},
                "max_concurrent": {"type": "integer", "default": 3}
            },
            "required": ["dois"]
        }
    ))
    
    tools.append(types.Tool(
        name="download_with_crawl4ai",
        description="Download PDF using Crawl4AI with anti-bot bypass",
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {"type": "string"},
                "output_dir": {"type": "string", "default": "./pdfs"},
                "headless": {"type": "boolean", "default": True},
                "profile_name": {"type": "string", "default": "scitex_academic"},
                "simulate_user": {"type": "boolean", "default": True}
            },
            "required": ["doi"]
        }
    ))
    
    # Utility tools
    tools.append(types.Tool(
        name="configure_crawl4ai",
        description="Configure Crawl4AI settings for a specific profile",
        inputSchema={
            "type": "object",
            "properties": {
                "profile_name": {"type": "string"},
                "browser_type": {"type": "string", "default": "chromium"},
                "headless": {"type": "boolean", "default": True},
                "simulate_user": {"type": "boolean", "default": True},
                "viewport_size": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "default": [1920, 1080]
                },
                "random_delays": {"type": "boolean", "default": False}
            },
            "required": ["profile_name"]
        }
    ))
    
    tools.append(types.Tool(
        name="get_download_status",
        description="Get status of a batch download",
        inputSchema={
            "type": "object",
            "properties": {
                "batch_id": {"type": "string"}
            },
            "required": ["batch_id"]
        }
    ))
    
    # PDF Validation tools
    tools.append(types.Tool(
        name="validate_pdf",
        description="Validate a single PDF file for completeness and readability",
        inputSchema={
            "type": "object",
            "properties": {
                "pdf_path": {"type": "string", "description": "Path to PDF file"}
            },
            "required": ["pdf_path"]
        }
    ))
    
    tools.append(types.Tool(
        name="validate_pdfs_batch",
        description="Validate multiple PDF files",
        inputSchema={
            "type": "object",
            "properties": {
                "pdf_paths": {"type": "array", "items": {"type": "string"}},
                "generate_report": {"type": "boolean", "default": True}
            },
            "required": ["pdf_paths"]
        }
    ))
    
    tools.append(types.Tool(
        name="validate_pdf_directory",
        description="Validate all PDFs in a directory",
        inputSchema={
            "type": "object",
            "properties": {
                "directory": {"type": "string"},
                "recursive": {"type": "boolean", "default": True},
                "report_path": {"type": "string", "description": "Optional path to save report"}
            },
            "required": ["directory"]
        }
    ))
    
    # Database tools
    tools.append(types.Tool(
        name="database_add_papers",
        description="Add papers to the database from BibTeX or search results",
        inputSchema={
            "type": "object",
            "properties": {
                "bibtex_path": {"type": "string", "description": "Path to BibTeX file"},
                "papers": {"type": "array", "items": {"type": "object"}, "description": "Paper objects to add"},
                "update_existing": {"type": "boolean", "default": True}
            }
        }
    ))
    
    tools.append(types.Tool(
        name="database_organize_pdfs",
        description="Organize PDFs in database structure by year/journal",
        inputSchema={
            "type": "object",
            "properties": {
                "entry_ids": {"type": "array", "items": {"type": "string"}},
                "organization": {
                    "type": "string",
                    "enum": ["year_journal", "year_author", "flat"],
                    "default": "year_journal"
                }
            }
        }
    ))
    
    tools.append(types.Tool(
        name="database_search",
        description="Search papers in database by various criteria",
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {"type": "string"},
                "title": {"type": "string"},
                "author": {"type": "string"},
                "year": {"type": "integer"},
                "journal": {"type": "string"},
                "tag": {"type": "string"},
                "collection": {"type": "string"},
                "status": {"type": "string"}
            }
        }
    ))
    
    tools.append(types.Tool(
        name="database_export",
        description="Export database entries to BibTeX or JSON",
        inputSchema={
            "type": "object",
            "properties": {
                "output_path": {"type": "string"},
                "format": {"type": "string", "enum": ["bibtex", "json"], "default": "bibtex"},
                "entry_ids": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["output_path"]
        }
    ))
    
    tools.append(types.Tool(
        name="database_statistics",
        description="Get database statistics and summary",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ))
    
    # Semantic search tools
    tools.append(types.Tool(
        name="semantic_index_papers",
        description="Index papers for semantic search",
        inputSchema={
            "type": "object",
            "properties": {
                "entry_ids": {"type": "array", "items": {"type": "string"}},
                "force_reindex": {"type": "boolean", "default": False},
                "batch_size": {"type": "integer", "default": 100}
            }
        }
    ))
    
    tools.append(types.Tool(
        name="semantic_search",
        description="Search for papers using semantic similarity",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "k": {"type": "integer", "default": 10},
                "threshold": {"type": "number", "default": 0.5},
                "search_mode": {
                    "type": "string",
                    "enum": ["semantic", "keyword", "hybrid"],
                    "default": "hybrid"
                }
            },
            "required": ["query"]
        }
    ))
    
    tools.append(types.Tool(
        name="find_similar_papers",
        description="Find papers similar to a given paper",
        inputSchema={
            "type": "object",
            "properties": {
                "entry_id": {"type": "string", "description": "Entry ID of reference paper"},
                "k": {"type": "integer", "default": 10}
            },
            "required": ["entry_id"]
        }
    ))
    
    tools.append(types.Tool(
        name="recommend_papers",
        description="Get recommendations based on multiple papers",
        inputSchema={
            "type": "object",
            "properties": {
                "entry_ids": {"type": "array", "items": {"type": "string"}},
                "k": {"type": "integer", "default": 10},
                "method": {"type": "string", "enum": ["average", "max"], "default": "average"}
            },
            "required": ["entry_ids"]
        }
    ))
    
    return tools


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    
    if not SCHOLAR_AVAILABLE:
        return [types.TextContent(
            type="text",
            text=f"Error: SciTeX Scholar not available. {import_error}"
        )]
    
    try:
        # Search tools
        if name == "search_papers":
            scholar = ensure_scholar()
            papers = await scholar.search_async(
                query=arguments["query"],
                limit=arguments.get("limit", 20),
                sources=arguments.get("sources")
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(papers),
                    "papers": [p.to_dict() for p in papers]
                }, indent=2)
            )]
        
        elif name == "search_quick":
            scholar = ensure_scholar()
            titles = scholar.search_quick(
                query=arguments["query"],
                top_n=arguments.get("top_n", 10)
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({"titles": titles}, indent=2)
            )]
        
        # BibTeX tools
        elif name == "parse_bibtex":
            scholar = ensure_scholar()
            papers = scholar.load_bibtex(arguments["bibtex_path"])
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(papers),
                    "papers": [p.to_dict() for p in papers]
                }, indent=2)
            )]
        
        elif name == "enrich_bibtex":
            scholar = ensure_scholar()
            papers = scholar.enrich_bibtex(
                bibtex_path=arguments["bibtex_path"],
                output_path=arguments.get("output_path"),
                add_missing_abstracts=arguments.get("add_abstracts", True),
                add_missing_urls=arguments.get("add_impact_factors", True)
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "enriched_count": len(papers),
                    "summary": {
                        "with_doi": sum(1 for p in papers if p.doi),
                        "with_impact_factor": sum(1 for p in papers if p.impact_factor),
                        "with_citations": sum(1 for p in papers if p.citation_count)
                    }
                }, indent=2)
            )]
        
        # Resolution tools
        elif name == "resolve_dois":
            resolver = ResumableDOIResolver(
                progress_file=arguments.get("progress_file")
            )
            
            # Convert paper dicts to Paper objects if needed
            papers = []
            for p in arguments["papers"]:
                if isinstance(p, dict):
                    papers.append(Paper(**p))
                else:
                    papers.append(p)
            
            results = resolver.resolve_batch(papers)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "resolved": len(results),
                    "dois": results
                }, indent=2)
            )]
        
        elif name == "resolve_openurls":
            auth_manager = None  # Could be enhanced with auth
            resolver = ResumableOpenURLResolver(
                auth_manager=auth_manager,
                resolver_url=arguments.get("resolver_url"),
                progress_file=arguments.get("progress_file")
            )
            
            results = await resolver.resolve_from_dois_async(arguments["dois"])
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "resolved": len(results),
                    "urls": results
                }, indent=2)
            )]
        
        # Download tools
        elif name == "download_pdf":
            scholar = ensure_scholar()
            
            # Create paper object from DOI
            paper = Paper(doi=arguments["doi"])
            
            # Download based on strategy
            if arguments.get("strategy") == "crawl4ai":
                return await handle_crawl4ai_download(paper, arguments)
            else:
                # Use Scholar's default downloader
                results = await scholar.download_pdfs_async(
                    [paper],
                    download_dir=arguments.get("output_dir", "./pdfs")
                )
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
        
        elif name == "download_pdfs_batch":
            batch_id = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create paper objects
            papers = [Paper(doi=doi) for doi in arguments["dois"]]
            
            # Track batch
            download_batches[batch_id] = {
                "total": len(papers),
                "completed": 0,
                "failed": 0,
                "status": "running"
            }
            
            # Start download
            scholar = ensure_scholar()
            results = await scholar.download_pdfs_async(
                papers,
                download_dir=arguments.get("output_dir", "./pdfs"),
                max_workers=arguments.get("max_concurrent", 3)
            )
            
            # Update batch status
            download_batches[batch_id]["status"] = "completed"
            download_batches[batch_id]["results"] = results
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "batch_id": batch_id,
                    "results": results
                }, indent=2)
            )]
        
        elif name == "download_with_crawl4ai":
            paper = Paper(doi=arguments["doi"])
            return await handle_crawl4ai_download(paper, arguments)
        
        elif name == "configure_crawl4ai":
            profile_name = arguments["profile_name"]
            crawl4ai_configs[profile_name] = {
                "browser_type": arguments.get("browser_type", "chromium"),
                "headless": arguments.get("headless", True),
                "simulate_user": arguments.get("simulate_user", True),
                "viewport_size": arguments.get("viewport_size", [1920, 1080]),
                "random_delays": arguments.get("random_delays", False)
            }
            
            return [types.TextContent(
                type="text",
                text=f"Configured Crawl4AI profile: {profile_name}"
            )]
        
        elif name == "get_download_status":
            batch_id = arguments["batch_id"]
            status = download_batches.get(batch_id, {"error": "Batch not found"})
            
            return [types.TextContent(
                type="text",
                text=json.dumps(status, indent=2)
            )]
        
        # PDF Validation tools
        elif name == "validate_pdf":
            validator = PDFValidator(cache_results=True)
            result = validator.validate(arguments["pdf_path"])
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result.to_dict(), indent=2)
            )]
        
        elif name == "validate_pdfs_batch":
            validator = PDFValidator(cache_results=True)
            
            async def progress_callback(current, total, filename):
                logger.info(f"Validating {current}/{total}: {filename}")
            
            results = await validator.validate_batch_async(
                arguments["pdf_paths"],
                progress_callback if arguments.get("generate_report", True) else None
            )
            
            # Convert results to serializable format
            results_dict = {
                path: result.to_dict() for path, result in results.items()
            }
            
            # Generate report if requested
            if arguments.get("generate_report", True):
                report = validator.generate_report(results)
                results_dict["_report"] = report
            
            return [types.TextContent(
                type="text",
                text=json.dumps(results_dict, indent=2)
            )]
        
        elif name == "validate_pdf_directory":
            validator = PDFValidator(cache_results=True)
            results = validator.validate_directory(
                arguments["directory"],
                recursive=arguments.get("recursive", True)
            )
            
            # Convert results
            results_dict = {
                path: result.to_dict() for path, result in results.items()
            }
            
            # Generate report
            report = validator.generate_report(results, arguments.get("report_path"))
            
            summary = {
                "total_files": len(results),
                "valid_count": sum(1 for r in results.values() if r.is_valid),
                "complete_count": sum(1 for r in results.values() if r.is_complete),
                "searchable_count": sum(1 for r in results.values() if r.is_text_searchable),
                "results": results_dict,
                "report": report
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(summary, indent=2)
            )]
        
        # Database tools
        elif name == "database_add_papers":
            db = PaperDatabase()
            
            # Load papers from BibTeX or use provided papers
            if arguments.get("bibtex_path"):
                scholar = ensure_scholar()
                papers = scholar.load_bibtex(arguments["bibtex_path"])
            elif arguments.get("papers"):
                papers = [Paper(**p) if isinstance(p, dict) else p for p in arguments["papers"]]
            else:
                return [types.TextContent(
                    type="text",
                    text="Error: Either bibtex_path or papers must be provided"
                )]
            
            # Add to database
            entry_ids = db.import_from_papers(papers, arguments.get("update_existing", True))
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "added_count": len(entry_ids),
                    "entry_ids": entry_ids,
                    "database_size": len(db.entries)
                }, indent=2)
            )]
        
        elif name == "database_organize_pdfs":
            db = PaperDatabase()
            
            entry_ids = arguments.get("entry_ids", list(db.entries.keys()))
            organization = arguments.get("organization", "year_journal")
            
            organized = []
            failed = []
            
            for entry_id in entry_ids:
                entry = db.get_entry(entry_id)
                if entry and entry.pdf_path and Path(entry.pdf_path).exists():
                    try:
                        new_path = db.organize_pdf(entry_id, entry.pdf_path, organization)
                        organized.append({
                            "entry_id": entry_id,
                            "old_path": entry.pdf_path,
                            "new_path": str(new_path)
                        })
                    except Exception as e:
                        failed.append({
                            "entry_id": entry_id,
                            "error": str(e)
                        })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "organized_count": len(organized),
                    "failed_count": len(failed),
                    "organized": organized,
                    "failed": failed
                }, indent=2)
            )]
        
        elif name == "database_search":
            db = PaperDatabase()
            
            # Build search query
            query = {k: v for k, v in arguments.items() if v is not None}
            
            # Search
            results = db.search(**query)
            
            # Format results
            formatted_results = []
            for entry_id, entry in results:
                formatted_results.append({
                    "entry_id": entry_id,
                    "title": entry.title,
                    "authors": entry.authors[:3] if entry.authors else [],
                    "year": entry.year,
                    "journal": entry.journal,
                    "doi": entry.doi,
                    "pdf_status": entry.download_status,
                    "pdf_valid": entry.pdf_valid
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(results),
                    "results": formatted_results
                }, indent=2)
            )]
        
        elif name == "database_export":
            db = PaperDatabase()
            
            output_path = arguments["output_path"]
            format_type = arguments.get("format", "bibtex")
            entry_ids = arguments.get("entry_ids")
            
            if format_type == "bibtex":
                export_path = db.export_to_bibtex(output_path, entry_ids)
            else:  # json
                export_path = db.export_to_json(output_path, entry_ids)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "exported": True,
                    "path": str(export_path),
                    "format": format_type,
                    "entry_count": len(entry_ids) if entry_ids else len(db.entries)
                }, indent=2)
            )]
        
        elif name == "database_statistics":
            db = PaperDatabase()
            stats = db.get_statistics()
            
            return [types.TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
            )]
        
        # Semantic search tools
        elif name == "semantic_index_papers":
            db = PaperDatabase()
            engine = SemanticSearchEngine(database=db)
            
            # Index papers
            stats = engine.index_papers(
                entry_ids=arguments.get("entry_ids"),
                force_reindex=arguments.get("force_reindex", False),
                batch_size=arguments.get("batch_size", 100)
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
            )]
        
        elif name == "semantic_search":
            db = PaperDatabase()
            engine = SemanticSearchEngine(database=db)
            
            # Search
            results = engine.search_by_text(
                query=arguments["query"],
                k=arguments.get("k", 10),
                search_mode=arguments.get("search_mode", "hybrid")
            )
            
            # Format results
            formatted_results = []
            for entry, score in results:
                formatted_results.append({
                    "score": float(score),
                    "title": entry.title,
                    "authors": entry.authors[:3] if entry.authors else [],
                    "year": entry.year,
                    "journal": entry.journal,
                    "doi": entry.doi,
                    "abstract": entry.abstract[:200] + "..." if entry.abstract else None
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(results),
                    "results": formatted_results
                }, indent=2)
            )]
        
        elif name == "find_similar_papers":
            db = PaperDatabase()
            engine = SemanticSearchEngine(database=db)
            
            # Find similar
            similar = engine.find_similar_papers(
                paper=arguments["entry_id"],
                k=arguments.get("k", 10)
            )
            
            # Format results
            formatted_results = []
            for entry, similarity in similar:
                formatted_results.append({
                    "similarity": float(similarity),
                    "title": entry.title,
                    "authors": entry.authors[:3] if entry.authors else [],
                    "year": entry.year,
                    "journal": entry.journal,
                    "doi": entry.doi
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(similar),
                    "similar_papers": formatted_results
                }, indent=2)
            )]
        
        elif name == "recommend_papers":
            db = PaperDatabase()
            engine = SemanticSearchEngine(database=db)
            
            # Get recommendations
            recommendations = engine.recommend_papers(
                entry_ids=arguments["entry_ids"],
                k=arguments.get("k", 10),
                method=arguments.get("method", "average")
            )
            
            # Format results
            formatted_results = []
            for entry, score in recommendations:
                formatted_results.append({
                    "score": float(score),
                    "title": entry.title,
                    "authors": entry.authors[:3] if entry.authors else [],
                    "year": entry.year,
                    "journal": entry.journal,
                    "doi": entry.doi
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(recommendations),
                    "recommendations": formatted_results
                }, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def handle_crawl4ai_download(paper: Paper, arguments: dict) -> list[types.TextContent]:
    """Handle download using Crawl4AI strategy."""
    
    # Get profile config
    profile_name = arguments.get("profile_name", "scitex_academic")
    config = crawl4ai_configs.get(profile_name, {})
    
    # Create strategy
    strategy = Crawl4AIDownloadStrategy(
        browser_type=config.get("browser_type", arguments.get("browser_type", "chromium")),
        headless=config.get("headless", arguments.get("headless", True)),
        profile_name=profile_name,
        simulate_user=config.get("simulate_user", arguments.get("simulate_user", True))
    )
    
    # Download
    output_dir = arguments.get("output_dir", "./pdfs")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    result = await strategy.download_async(
        paper=paper,
        output_dir=output_dir
    )
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "success": result is not None,
            "path": result,
            "strategy": "crawl4ai",
            "profile": profile_name
        }, indent=2)
    )]


async def main():
    """Run the server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="scitex-scholar",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())