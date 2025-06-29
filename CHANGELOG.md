# Changelog

All notable changes to SciTeX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-29

### Added
- **MCP Server Infrastructure**: Complete Model Context Protocol implementation for AI-assisted development
  - 12 specialized servers covering all major SciTeX modules
  - Bidirectional code translation between standard Python and SciTeX
  - Comprehensive validation and analysis tools
  - Project scaffolding and template generation
  - Configuration management system
  - Workflow orchestration capabilities

### MCP Servers Added
- `scitex-base`: Shared functionality for all servers
- `scitex-io`: File I/O translation for 30+ formats
- `scitex-plt`: Matplotlib enhancement translations
- `scitex-stats`: Statistical function translations with p-value formatting
- `scitex-dsp`: Signal processing translations
- `scitex-pd`: Pandas operation translations
- `scitex-torch`: PyTorch deep learning translations
- `scitex-analyzer`: Code analysis with comprehensive validation
- `scitex-framework`: Template and project generation
- `scitex-config`: Configuration file management
- `scitex-orchestrator`: Workflow coordination
- `scitex-validator`: Compliance validation

### Enhanced
- **Analyzer**: Added comprehensive validation tools
  - Import order verification
  - Docstring format validation
  - Cross-file dependency analysis
  - Naming convention checking
  - CONFIG usage validation
  - Path handling verification
  - Framework compliance checking

### Infrastructure
- One-command installation: `./install_all.sh`
- Concurrent server launching: `./launch_all.sh`
- Comprehensive testing: `./test_all.sh`
- MCP configuration examples for AI assistants

### Documentation
- Complete documentation for all MCP servers
- Module coverage analysis (95%+ functionality coverage)
- Usage examples and quickstart guides
- Integration guides for AI assistants

## [1.0.0] - Previous Release

### Core Features
- Standardized project structure
- Configuration management system
- Enhanced I/O operations
- Matplotlib wrapper with tracking
- Statistical analysis tools
- Signal processing utilities
- PyTorch integration

---

For detailed release notes, see the [GitHub Releases](https://github.com/ywatanabe1989/SciTeX-Code/releases) page.

# EOF