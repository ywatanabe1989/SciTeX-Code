# SciTeX Analyzer MCP Server

Advanced code analysis and understanding for SciTeX projects. Goes beyond translation to provide comprehensive project insights.

## Features

### 1. Project Analysis
- **Complete project scanning** - Analyze entire codebases
- **Pattern detection** - Find SciTeX and anti-patterns
- **Structure validation** - Check project organization
- **Configuration analysis** - Validate configs

### 2. Code Understanding
- **Pattern explanation** - Learn what SciTeX patterns do
- **Benefit analysis** - Understand why patterns matter
- **Example finding** - See real usage examples
- **Anti-pattern detection** - Find problematic code

### 3. Improvement Suggestions
- **Performance optimization** - Cache expensive operations
- **Reproducibility enhancement** - Extract hardcoded values
- **Maintainability improvements** - Better code organization
- **Priority-based recommendations** - Focus on what matters

## Available Tools

1. **analyze_scitex_project** - Comprehensive project analysis
   ```python
   result = analyze_scitex_project("/path/to/project")
   # Returns structure analysis, patterns, configs, recommendations
   ```

2. **explain_scitex_pattern** - Understand SciTeX patterns
   ```python
   explanation = explain_scitex_pattern(
       "stx.io.save(data, './output.csv', symlink_from_cwd=True)"
   )
   # Returns pattern explanation, benefits, examples
   ```

3. **suggest_scitex_improvements** - Get specific improvements
   ```python
   suggestions = suggest_scitex_improvements(code, context="research_script")
   # Returns prioritized improvement suggestions
   ```

4. **find_scitex_examples** - Find usage examples
   ```python
   examples = find_scitex_examples("io_save", context="data_analysis")
   # Returns relevant code examples
   ```

## Installation

```bash
cd mcp_servers/scitex-analyzer
pip install -e .
```

## Usage

### Standalone
```bash
python server.py
```

### With MCP Client
```json
{
  "mcpServers": {
    "scitex-analyzer": {
      "command": "python",
      "args": ["-m", "scitex_analyzer.server"],
      "cwd": "/path/to/mcp_servers/scitex-analyzer"
    }
  }
}
```

## Analysis Examples

### Project Analysis Output
```json
{
  "project_structure": {
    "total_files": 45,
    "existing_directories": ["scripts", "config", "data"],
    "missing_directories": ["examples", "tests"],
    "structure_score": 60.0
  },
  "code_patterns": {
    "patterns_found": {
      "io_save": 23,
      "plt_subplots": 15,
      "config_access": 47
    },
    "anti_patterns_found": {
      "absolute_path": 5,
      "hardcoded_number": 18
    },
    "compliance_score": 85.3
  },
  "recommendations": [
    {
      "category": "patterns",
      "issue": "Found 5 absolute paths",
      "suggestion": "Convert to relative paths for reproducibility",
      "priority": "high"
    }
  ]
}
```

### Pattern Explanation Output
```json
{
  "pattern_name": "SciTeX IO Save Pattern",
  "explanation": "stx.io.save() provides unified file saving...",
  "benefits": [
    "Automatic directory creation",
    "Format detection from extension",
    "Consistent handling across formats"
  ],
  "example": "stx.io.save(data, './results.csv', symlink_from_cwd=True)",
  "common_mistakes": [
    "Using absolute paths",
    "Forgetting symlink parameter"
  ]
}
```

## Benefits

1. **Deep Understanding** - Know exactly how your code uses SciTeX
2. **Proactive Detection** - Find issues before they cause problems
3. **Learning Tool** - Understand patterns through explanation
4. **Guided Improvement** - Prioritized, actionable suggestions
5. **Project Health** - Monitor code quality over time

## Future Enhancements

- Performance profiling
- Dependency analysis
- Test coverage integration
- Git history analysis
- Team coding standards