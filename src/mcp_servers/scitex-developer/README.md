# SciTeX Developer Support MCP Server

Comprehensive developer support system that extends the analyzer with advanced development tools.

## Features

### 🧪 Test Generation & Quality Assurance
- **Automated Test Generation**: Create pytest/unittest tests for any script
- **Coverage Analysis**: Comprehensive test coverage reporting
- **Quality Metrics**: Code complexity, maintainability, and security analysis

### ⚡ Performance Optimization
- **Performance Benchmarking**: Profile scripts for time and memory usage
- **Optimization Planning**: Generate detailed optimization roadmaps
- **Bottleneck Detection**: Identify performance hotspots

### 🔄 Migration & Maintenance
- **Version Migration**: Automated assistance for SciTeX version upgrades
- **Breaking Change Detection**: Identify API changes between versions
- **Refactoring Support**: Comprehensive best practices refactoring

### 📚 Learning & Documentation
- **Interactive Tutorials**: Create custom tutorials for any topic
- **Concept Explanation**: Detailed explanations with examples
- **Best Practices Guide**: Learn common mistakes and solutions

### 🔍 Enhanced Analysis (from Analyzer)
- **Project Analysis**: Complete codebase analysis and recommendations
- **Pattern Detection**: Identify SciTeX patterns and anti-patterns
- **Dependency Mapping**: Visualize project structure and dependencies

## Installation

```bash
cd src/mcp_servers/scitex-developer
pip install -e .
```

## Configuration

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "scitex-developer": {
      "command": "python",
      "args": ["-m", "scitex_developer"]
    }
  }
}
```

## Usage Examples

### Generate Tests
```
"Generate comprehensive tests for my analysis script"
"Create pytest tests with fixtures for data processing"
```

### Performance Analysis
```
"Benchmark my script and suggest optimizations"
"Create a performance optimization plan for 2x speedup"
```

### Migration Assistance
```
"Help me migrate from SciTeX 1.0 to 2.0"
"Detect breaking changes in my API update"
```

### Learning
```
"Explain the SciTeX configuration system with examples"
"Create an interactive tutorial for data visualization"
```

## Available Tools

### Test Generation
- `generate_scitex_tests` - Generate appropriate tests for scripts
- `generate_test_coverage_report` - Analyze test coverage
- `analyze_code_quality_metrics` - Comprehensive quality analysis

### Performance
- `benchmark_scitex_performance` - Profile script performance
- `generate_performance_optimization_plan` - Create optimization roadmap

### Migration
- `migrate_to_latest_scitex` - Version migration assistance
- `detect_breaking_changes` - Find API breaking changes
- `refactor_for_scitex_best_practices` - Refactoring suggestions

### Learning
- `explain_scitex_concept` - Interactive concept explanation
- `create_interactive_tutorial` - Generate custom tutorials

### Analysis (Inherited)
All tools from scitex-analyzer are also available, including:
- `analyze_scitex_project` - Complete project analysis
- `create_scitex_project` - Generate new projects
- `generate_scitex_script` - Create purpose-built scripts
- And many more...

## Architecture

The developer server extends the analyzer server with additional components:

```
ScitexDeveloperMCPServer
├── ScitexAnalyzerMCPServer (inherited)
│   ├── Project Analysis
│   ├── Pattern Detection
│   └── Code Generation
└── Developer Components
    ├── TestGenerator
    ├── PerformanceBenchmarker
    ├── MigrationAssistant
    └── LearningSystem
```

## Examples

See the `examples/` directory for detailed usage examples.

## Contributing

This server is part of the SciTeX MCP infrastructure. Contributions should follow the project guidelines.