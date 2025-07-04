#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 02:50:00 (ywatanabe)"
# File: ./mcp_servers/scitex_io_translator/server.py
# ----------------------------------------
import os
__FILE__ = "./mcp_servers/scitex_io_translator/server.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
MCP server for translating between standard Python and SciTeX formats.
Focuses on IO module translations.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
import re
from pathlib import Path

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio
from mcp.types import (
    Tool,
    TextContent,
    EmbeddedResource,
    BlobResourceContents,
    TextResourceContents
)
from pydantic import AnyUrl

# Import translation modules
from .translators import (
    IOTranslator,
    PathTranslator,
    TemplateTranslator,
    ValidationEngine
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScitexTranslationServer:
    """MCP server for SciTeX code translation."""
    
    def __init__(self):
        self.server = Server("scitex-io-translator")
        self.io_translator = IOTranslator()
        self.path_translator = PathTranslator()
        self.template_translator = TemplateTranslator()
        self.validator = ValidationEngine()
        
        # Register handlers
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup all MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available translation tools."""
            return [
                Tool(
                    name="translate_to_scitex",
                    description="Convert standard Python code to SciTeX format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_code": {
                                "type": "string",
                                "description": "Python source code to translate"
                            },
                            "target_modules": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "SciTeX modules to use (io, plt, stats, etc.)",
                                "default": ["io"]
                            },
                            "preserve_comments": {
                                "type": "boolean",
                                "description": "Preserve original comments",
                                "default": True
                            },
                            "add_config_support": {
                                "type": "boolean",
                                "description": "Extract hardcoded values to config files",
                                "default": False
                            }
                        },
                        "required": ["source_code"]
                    }
                ),
                Tool(
                    name="translate_from_scitex",
                    description="Convert SciTeX code to standard Python",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scitex_code": {
                                "type": "string",
                                "description": "SciTeX source code to translate"
                            },
                            "target_style": {
                                "type": "string",
                                "description": "Target style (matplotlib, pandas, numpy)",
                                "default": "standard"
                            },
                            "include_dependencies": {
                                "type": "boolean",
                                "description": "Include import statements",
                                "default": True
                            }
                        },
                        "required": ["scitex_code"]
                    }
                ),
                Tool(
                    name="validate_scitex_compliance",
                    description="Check if code follows SciTeX guidelines",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to validate"
                            },
                            "strict_mode": {
                                "type": "boolean",
                                "description": "Use strict validation rules",
                                "default": False
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="extract_io_patterns",
                    description="Extract IO patterns from code for analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to analyze"
                            }
                        },
                        "required": ["code"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            
            if name == "translate_to_scitex":
                result = await self.translate_to_scitex(
                    source_code=arguments["source_code"],
                    target_modules=arguments.get("target_modules", ["io"]),
                    preserve_comments=arguments.get("preserve_comments", True),
                    add_config_support=arguments.get("add_config_support", False)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "translate_from_scitex":
                result = await self.translate_from_scitex(
                    scitex_code=arguments["scitex_code"],
                    target_style=arguments.get("target_style", "standard"),
                    include_dependencies=arguments.get("include_dependencies", True)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "validate_scitex_compliance":
                result = await self.validate_compliance(
                    code=arguments["code"],
                    strict_mode=arguments.get("strict_mode", False)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "extract_io_patterns":
                result = await self.extract_patterns(code=arguments["code"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def translate_to_scitex(
        self,
        source_code: str,
        target_modules: List[str],
        preserve_comments: bool,
        add_config_support: bool
    ) -> Dict[str, Any]:
        """Translate standard Python to SciTeX format."""
        
        try:
            # Step 1: Add SciTeX boilerplate
            code = self.template_translator.add_boilerplate(source_code, preserve_comments)
            
            # Step 2: Translate IO operations
            if "io" in target_modules:
                code = self.io_translator.translate_to_scitex(code)
            
            # Step 3: Fix paths
            code = self.path_translator.convert_to_relative_paths(code)
            
            # Step 4: Extract config if requested
            config_files = {}
            if add_config_support:
                code, config_files = self.extract_config_values(code)
            
            # Step 5: Validate result
            validation = self.validator.validate(code)
            
            return {
                "success": True,
                "translated_code": code,
                "config_files": config_files,
                "validation": validation,
                "changes_made": self._summarize_changes(source_code, code)
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_code": source_code
            }
    
    async def translate_from_scitex(
        self,
        scitex_code: str,
        target_style: str,
        include_dependencies: bool
    ) -> Dict[str, Any]:
        """Translate SciTeX to standard Python."""
        
        try:
            # Step 1: Remove SciTeX boilerplate
            code = self.template_translator.remove_boilerplate(scitex_code)
            
            # Step 2: Translate IO operations back
            code = self.io_translator.translate_from_scitex(code)
            
            # Step 3: Add necessary imports
            if include_dependencies:
                code = self._add_standard_imports(code)
            
            # Step 4: Convert paths if needed
            code = self.path_translator.ensure_output_dirs(code)
            
            return {
                "success": True,
                "translated_code": code,
                "style": target_style,
                "imports_added": include_dependencies
            }
            
        except Exception as e:
            logger.error(f"Reverse translation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_code": scitex_code
            }
    
    async def validate_compliance(self, code: str, strict_mode: bool) -> Dict[str, Any]:
        """Validate SciTeX compliance."""
        
        issues = self.validator.validate(code, strict=strict_mode)
        
        return {
            "compliant": len(issues.get("errors", [])) == 0,
            "issues": issues,
            "suggestions": self.validator.get_suggestions(code)
        }
    
    async def extract_patterns(self, code: str) -> Dict[str, Any]:
        """Extract IO patterns from code."""
        
        patterns = self.io_translator.extract_io_patterns(code)
        
        return {
            "io_operations": patterns,
            "statistics": {
                "total_operations": len(patterns),
                "by_type": self._count_by_type(patterns)
            }
        }
    
    def extract_config_values(self, code: str) -> tuple[str, Dict[str, str]]:
        """Extract hardcoded values to config files."""
        # Implementation for config extraction
        # This would analyze the code and extract paths, parameters, etc.
        configs = {}
        
        # Extract paths
        path_pattern = r'["\']([./].*?\.(?:csv|png|jpg|npy|pkl|json))["\']'
        paths = re.findall(path_pattern, code)
        
        if paths:
            configs["PATH.yaml"] = self._generate_path_config(paths)
            code = self._replace_paths_with_config(code, paths)
        
        return code, configs
    
    def _generate_path_config(self, paths: List[str]) -> str:
        """Generate PATH.yaml content."""
        config = "# Auto-generated path configuration\n"
        config += "paths:\n"
        for i, path in enumerate(set(paths)):
            key = Path(path).stem.upper()
            config += f"  {key}: '{path}'\n"
        return config
    
    def _replace_paths_with_config(self, code: str, paths: List[str]) -> str:
        """Replace hardcoded paths with config references."""
        for path in set(paths):
            key = Path(path).stem.upper()
            code = code.replace(f'"{path}"', f'CONFIG.paths.{key}')
            code = code.replace(f"'{path}'", f'CONFIG.paths.{key}')
        return code
    
    def _summarize_changes(self, original: str, translated: str) -> Dict[str, int]:
        """Summarize changes made during translation."""
        return {
            "lines_added": translated.count('\n') - original.count('\n'),
            "io_operations_converted": self.io_translator.count_conversions(original, translated),
            "paths_converted": self.path_translator.count_path_conversions(original, translated)
        }
    
    def _add_standard_imports(self, code: str) -> str:
        """Add standard library imports based on usage."""
        imports = []
        
        if 'pd.read_csv' in code or 'DataFrame' in code:
            imports.append('import pandas as pd')
        if 'np.' in code or 'array' in code:
            imports.append('import numpy as np')
        if 'plt.' in code or 'matplotlib' in code:
            imports.append('import matplotlib.pyplot as plt')
        if 'Path(' in code:
            imports.append('from pathlib import Path')
        
        if imports:
            return '\n'.join(imports) + '\n\n' + code
        return code
    
    def _count_by_type(self, patterns: List[Dict]) -> Dict[str, int]:
        """Count patterns by type."""
        counts = {}
        for pattern in patterns:
            op_type = pattern.get('type', 'unknown')
            counts[op_type] = counts.get(op_type, 0) + 1
        return counts
    
    async def run(self):
        """Run the MCP server."""
        async with stdio() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="scitex-io-translator",
                    server_version="0.1.0"
                )
            )


async def main():
    """Main entry point."""
    server = ScitexTranslationServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())