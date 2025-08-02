# SciTeX MCP Servers - Comprehensive Guide

**Version**: 2.0.0  
**Last Updated**: 2025-07-25  
**Author**: SciTeX Development Team

## Table of Contents

1. [Introduction](#introduction)
2. [What are MCP Servers?](#what-are-mcp-servers)
3. [Available MCP Servers](#available-mcp-servers)
4. [Installation & Setup](#installation--setup)
5. [Usage Examples](#usage-examples)
6. [Creating Custom MCP Servers](#creating-custom-mcp-servers)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

## Introduction

MCP (Model Context Protocol) servers enable AI assistants like Claude to perform specialized tasks through tool interfaces. SciTeX provides a comprehensive suite of MCP servers for scientific computing, code translation, and project management.

## What are MCP Servers?

MCP servers are specialized tools that:
- Extend AI assistant capabilities beyond text generation
- Provide structured interfaces for specific tasks
- Enable bidirectional code translation
- Validate project structures
- Assist with scientific computing workflows

### Key Benefits

1. **Automated Translation**: Convert between SciTeX and pure Python seamlessly
2. **Project Validation**: Ensure your project follows best practices
3. **Scientific Computing**: Specialized tools for research workflows
4. **Code Quality**: Automated analysis and improvement suggestions

## Available MCP Servers

### 1. Translation Servers

#### scitex-translator
Bidirectional translation between SciTeX and pure Python formats.

**Tools**:
- `translate_to_scitex`: Convert pure Python to SciTeX format
- `translate_from_scitex`: Convert SciTeX code to pure Python
- `detect_format`: Automatically detect code format
- `batch_translate`: Process multiple files

**Example Configuration**:
```json
{
  "mcpServers": {
    "scitex-translator": {
      "command": "python",
      "args": ["-m", "scitex.mcp_servers.translator"]
    }
  }
}
```

### 2. Module-Specific Servers

#### scitex-io
File I/O operations with SciTeX's unified interface.

**Tools**:
- `convert_save_to_scitex`: Convert standard Python saves
- `convert_load_to_scitex`: Convert standard Python loads
- `suggest_io_improvement`: Recommend I/O optimizations

#### scitex-plt
Scientific plotting and visualization.

**Tools**:
- `convert_matplotlib_to_scitex`: Transform matplotlib code
- `enhance_plot_style`: Apply publication-ready styling
- `add_statistical_annotations`: Add p-values, error bars

#### scitex-stats
Statistical analysis and testing.

**Tools**:
- `recommend_statistical_test`: Suggest appropriate tests
- `convert_stats_to_scitex`: Use SciTeX's robust methods
- `generate_statistical_report`: Create comprehensive reports

### 3. Project Management Servers

#### scitex-project-validator
Validate and improve project structure.

**Tools**:
- `check_scientific_project`: Validate research project setup
- `check_pip_package`: Validate package structure
- `generate_project_report`: Comprehensive project analysis

#### scitex-analyzer
Deep code analysis and recommendations.

**Tools**:
- `analyze_codebase`: Full project analysis
- `find_scitex_opportunities`: Identify improvement areas
- `generate_migration_plan`: Plan SciTeX adoption

### 4. Specialized Servers

#### scitex-scholar
Academic paper management and citation handling.

**Tools**:
- `search_papers`: Search academic databases
- `manage_citations`: Handle BibTeX and citations
- `download_papers`: Fetch PDFs (with authentication)

#### scitex-developer
Comprehensive development support.

**Tools**:
- `generate_tests`: Create unit tests automatically
- `benchmark_performance`: Profile and optimize code
- `assist_migration`: Help with version upgrades
- `interactive_tutorial`: Learn SciTeX interactively

## Installation & Setup

### Prerequisites

1. **Claude Desktop App**
2. **Python 3.8+**
3. **SciTeX installed**: `pip install scitex`

### Configuration Steps

1. **Locate Claude's configuration**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Edit configuration**:
   ```json
   {
     "mcpServers": {
       "scitex-translator": {
         "command": "python",
         "args": ["-m", "scitex.mcp_servers.translator"],
         "env": {
           "PYTHONPATH": "/path/to/your/project"
         }
       },
       "scitex-analyzer": {
         "command": "python",
         "args": ["-m", "scitex.mcp_servers.analyzer"]
       },
       "scitex-unified": {
         "command": "python",
         "args": ["-m", "scitex.mcp_servers.unified"]
       }
     }
   }
   ```

3. **Restart Claude** to load the servers

4. **Verify installation**:
   - Ask Claude: "What MCP tools do you have available?"
   - Claude should list all configured SciTeX tools

## Usage Examples

### Example 1: Converting Code to SciTeX

**User**: "Convert this data loading code to use SciTeX"

```python
# Original code
import pickle
import json
import numpy as np

with open('data.pkl', 'rb') as f:
    data = pickle.load(f)

with open('config.json', 'r') as f:
    config = json.load(f)

arr = np.load('array.npy')
```

**Claude (using MCP)**: "I'll convert this to SciTeX format."

```python
# SciTeX version
import scitex as stx

data = stx.io.load('data.pkl')
config = stx.io.load('config.json')
arr = stx.io.load('array.npy')
```

### Example 2: Project Validation

**User**: "Check if my project structure follows SciTeX best practices"

**Claude (using MCP)**: "I'll analyze your project structure..."

```
Project Score: 85/100

✅ Strengths:
- Well-organized source code
- Comprehensive test coverage
- Good documentation

⚠️ Improvements needed:
- Add type hints to 30% of functions
- Create examples/notebooks directory
- Add .readthedocs.yaml for documentation

📋 Recommendations:
1. Run: mkdir -p examples/notebooks
2. Add type hints using mypy
3. Configure Read the Docs
```

### Example 3: Statistical Analysis

**User**: "Help me choose the right statistical test for my data"

**Claude (using MCP)**: "I'll analyze your data and recommend appropriate tests..."

```python
# Recommended approach
import scitex as stx

# For two-group comparison with unequal variances
result = stx.stats.brunner_munzel_test(group1, group2)

# More robust than t-test for real-world data
print(f"W-statistic: {result.statistic:.4f}")
print(f"p-value: {result.pvalue:.4f}")
```

## Creating Custom MCP Servers

### Basic Structure

```python
# my_custom_server.py
from scitex.mcp_servers.base import BaseMCPServer
import asyncio

class MyCustomServer(BaseMCPServer):
    def __init__(self):
        super().__init__(
            name="my-custom-server",
            version="1.0.0",
            description="Custom MCP server for specific tasks"
        )
    
    async def handle_tool(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "my_custom_tool":
            return await self.my_custom_tool(**arguments)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def my_custom_tool(self, input_data: str) -> dict:
        # Your custom logic here
        result = process_data(input_data)
        return {"result": result}

if __name__ == "__main__":
    server = MyCustomServer()
    asyncio.run(server.run())
```

### Registering Tools

```python
def get_tools(self) -> list:
    return [
        {
            "name": "my_custom_tool",
            "description": "Processes data in a custom way",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input_data": {
                        "type": "string",
                        "description": "Data to process"
                    }
                },
                "required": ["input_data"]
            }
        }
    ]
```

## Best Practices

### 1. Server Selection

- Use **unified server** for general tasks
- Use **specialized servers** for focused work
- Combine multiple servers for complex workflows

### 2. Performance Optimization

```json
{
  "mcpServers": {
    "scitex-unified": {
      "command": "python",
      "args": ["-m", "scitex.mcp_servers.unified"],
      "env": {
        "SCITEX_CACHE_ENABLED": "true",
        "SCITEX_PARALLEL_PROCESSING": "true"
      }
    }
  }
}
```

### 3. Error Handling

Always provide clear context to Claude:
- Include file paths
- Specify desired output format
- Mention any constraints or requirements

### 4. Security Considerations

- Never expose sensitive credentials in MCP configurations
- Use environment variables for API keys
- Validate all file paths before processing

## Troubleshooting

### Common Issues

#### 1. "MCP server not found"
**Solution**: Ensure SciTeX is installed and PYTHONPATH is set correctly

#### 2. "Tool execution timeout"
**Solution**: Increase timeout in configuration:
```json
{
  "timeout": 300000  // 5 minutes in milliseconds
}
```

#### 3. "Permission denied"
**Solution**: Check file permissions and paths

### Debug Mode

Enable debug logging:
```json
{
  "mcpServers": {
    "scitex-unified": {
      "command": "python",
      "args": ["-m", "scitex.mcp_servers.unified"],
      "env": {
        "SCITEX_DEBUG": "true",
        "SCITEX_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Getting Help

1. Check server logs: `~/.scitex/logs/mcp/`
2. Run diagnostic: `python -m scitex.mcp_servers.diagnostic`
3. Report issues: https://github.com/scitex/scitex/issues

## API Reference

### Base Server Interface

```python
class BaseMCPServer:
    async def initialize(self) -> None:
        """Initialize server resources"""
        
    async def handle_tool(self, tool_name: str, arguments: dict) -> dict:
        """Handle tool execution"""
        
    def get_tools(self) -> list:
        """Return available tools"""
        
    async def shutdown(self) -> None:
        """Clean up resources"""
```

### Tool Response Format

```python
{
    "success": bool,
    "result": Any,  # Tool-specific result
    "error": Optional[str],
    "metadata": {
        "execution_time": float,
        "version": str
    }
}
```

### Configuration Schema

```typescript
interface MCPServerConfig {
  command: string;
  args: string[];
  env?: Record<string, string>;
  timeout?: number;
  cwd?: string;
}
```

## Advanced Topics

### Chaining MCP Servers

```python
# In Claude conversation
1. "Analyze my codebase" → scitex-analyzer
2. "Convert identified patterns" → scitex-translator
3. "Validate the changes" → scitex-project-validator
4. "Generate tests" → scitex-developer
```

### Custom Workflows

Create workflow configurations:
```json
{
  "workflows": {
    "full_migration": [
      "analyze_codebase",
      "generate_migration_plan",
      "batch_translate",
      "generate_tests",
      "validate_project"
    ]
  }
}
```

### Integration with CI/CD

```yaml
# .github/workflows/mcp-validation.yml
name: MCP Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run MCP validation
        run: |
          python -m scitex.mcp_servers.validator \
            --check-scientific-project \
            --output-format json > validation_report.json
```

## Conclusion

SciTeX MCP servers provide powerful tools for scientific computing workflows. They enable:

- Seamless code translation
- Automated project validation
- Enhanced development productivity
- Better code quality and consistency

Start with the unified server for general use, then explore specialized servers as needed. The MCP architecture ensures that AI assistance is both powerful and contextually aware of scientific computing best practices.

For the latest updates and additional servers, visit:
- Documentation: https://scitex.readthedocs.io/mcp-servers
- GitHub: https://github.com/scitex/scitex
- Community: https://discord.gg/scitex