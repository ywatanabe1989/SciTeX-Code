# Changelog

All notable changes to SciTeX-Scholar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-02

### Added
- Enhanced paper acquisition with Semantic Scholar as primary source
- AI-powered paper analysis and research gap identification
- Journal impact factor integration with automatic lookup
- Enhanced bibliography generation with journal metrics
- Paper enrichment service for comprehensive metadata
- AI integration support for Anthropic, OpenAI, Google, and Perplexity
- Research summary generation with AI assistance
- Citation influence metrics from Semantic Scholar

### Changed
- Improved paper deduplication algorithm
- Enhanced search with multiple sources (Semantic Scholar, PubMed, arXiv)
- Better error handling and logging throughout
- Modular AI client integration

### Fixed
- PDF download functionality properly integrated with paper acquisition workflow
- Added `download_papers_pdfs` method to PaperAcquisition class
- Full literature review now includes PDF downloads by default
- Improved metadata extraction accuracy
- Better handling of missing journal information

## [0.1.0] - 2025-01-12

### Added
- Initial release of SciTeX-Scholar
- Vector-based semantic search using SciBERT embeddings
- Automated paper acquisition from PubMed and arXiv
- Scientific PDF parsing with structure extraction
- LaTeX document parsing and processing
- Literature review workflow automation
- MCP server integration for AI assistants
- Comprehensive test suite with 100% coverage
- Detailed documentation and examples

### Features
- Semantic search with SciBERT embeddings
- Multi-source paper discovery
- Automated PDF downloading for open-access papers
- Manual download workflow for subscription journals
- Extract methods, datasets, and citations from papers
- Research gap identification
- ChromaDB for persistent vector storage
- Support for various document formats (PDF, LaTeX, Markdown, text)

### Technical
- Python 3.8+ support
- Async/await for efficient paper downloading
- Modular architecture
- Extensive test coverage
- Rich example collection