#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:45:00"
# File: server.py

"""
Unified MCP server for SciTeX translation.
Provides a single server with pluggable module translators.
"""

import asyncio
from scitex import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from mcp.server import Server
from mcp.types import (
    Tool, TextContent, ErrorContent, EmbeddedResource,
    ImageContent, BlobResourceContents
)

from scitex_translators.core.base_translator import BaseTranslator, TranslationContext
from scitex_translators.core.context_analyzer import ContextAnalyzer
from scitex_translators.validators.base_validator import (
    BaseValidator, ModuleSpecificValidator, TranslationValidator
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedTranslatorServer:
    """
    Unified MCP server with pluggable module translators.
    Provides intelligent, context-aware code translation.
    """
    
    def __init__(self):
        self.server = Server("scitex-unified-translator")
        self.translators: Dict[str, BaseTranslator] = {}
        self.context_analyzer = ContextAnalyzer()
        self.base_validator = BaseValidator()
        self.translation_validator = TranslationValidator()
        self.module_validators: Dict[str, ModuleSpecificValidator] = {}
        
        # Initialize components
        self._load_translators()
        self._setup_tools()
        
        logger.info("Unified SciTeX Translator Server initialized")
    
    def _load_translators(self):
        """Load all available module translators."""
        # Import module translators and ordering
        try:
            from scitex_translators.modules import (
                IOTranslator, PLTTranslator, AITranslator, GenTranslator, MODULE_ORDER
            )
            
            # Register translators
            translator_classes = {
                "io": IOTranslator,
                "plt": PLTTranslator,
                "ai": AITranslator,
                "gen": GenTranslator
            }
            
            for module_name, translator_class in translator_classes.items():
                if translator_class is not None:
                    translator = translator_class()
                    self.translators[translator.module_name] = translator
                    self.module_validators[translator.module_name] = ModuleSpecificValidator(translator.module_name)
                    logger.info(f"Loaded translator for module: {translator.module_name}")
            
            # Store module order for translation
            self.module_order = MODULE_ORDER
        
        except ImportError as e:
            logger.warning(f"Some translators not available yet: {e}")
            # Continue with available translators
            self.module_order = ["ai", "plt", "io", "gen"]  # Default order
    
    def _setup_tools(self):
        """Set up MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools."""
            tools = [
                Tool(
                    name="translate_to_scitex",
                    description="Translate standard Python code to SciTeX style",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to translate"
                            },
                            "modules": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific modules to use (optional, auto-detected if not provided)"
                            },
                            "validate": {
                                "type": "boolean",
                                "description": "Whether to validate the translation",
                                "default": True
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="translate_from_scitex",
                    description="Translate SciTeX code to standard Python or other styles",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "SciTeX code to translate"
                            },
                            "target_style": {
                                "type": "string",
                                "description": "Target style: standard, numpy, pandas",
                                "default": "standard"
                            },
                            "validate": {
                                "type": "boolean",
                                "description": "Whether to validate the translation",
                                "default": True
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="analyze_code",
                    description="Analyze code structure and suggest SciTeX modules",
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
                ),
                Tool(
                    name="validate_code",
                    description="Validate code syntax, style, and complexity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to validate"
                            },
                            "module": {
                                "type": "string",
                                "description": "Specific module to validate against (optional)"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="list_modules",
                    description="List all available SciTeX modules and their capabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_module_info",
                    description="Get detailed information about a specific module",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module": {
                                "type": "string",
                                "description": "Module name"
                            }
                        },
                        "required": ["module"]
                    }
                ),
                Tool(
                    name="batch_translate",
                    description="Translate multiple code snippets in batch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "snippets": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "string"},
                                        "direction": {
                                            "type": "string",
                                            "enum": ["to_scitex", "from_scitex"],
                                            "default": "to_scitex"
                                        }
                                    }
                                },
                                "description": "Array of code snippets to translate"
                            }
                        },
                        "required": ["snippets"]
                    }
                )
            ]
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ErrorContent]:
            """Handle tool calls."""
            try:
                if name == "translate_to_scitex":
                    result = await self._translate_to_scitex(
                        arguments["code"],
                        arguments.get("modules"),
                        arguments.get("validate", True)
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "translate_from_scitex":
                    result = await self._translate_from_scitex(
                        arguments["code"],
                        arguments.get("target_style", "standard"),
                        arguments.get("validate", True)
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "analyze_code":
                    result = await self._analyze_code(arguments["code"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "validate_code":
                    result = await self._validate_code(
                        arguments["code"],
                        arguments.get("module")
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "list_modules":
                    result = self._list_modules()
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_module_info":
                    result = self._get_module_info(arguments["module"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "batch_translate":
                    result = await self._batch_translate(arguments["snippets"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                else:
                    return [ErrorContent(type="error", error=f"Unknown tool: {name}")]
            
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [ErrorContent(type="error", error=str(e))]
    
    async def _translate_to_scitex(self, code: str, modules: Optional[List[str]] = None, 
                                  validate: bool = True) -> Dict[str, Any]:
        """Translate standard Python to SciTeX."""
        result = {
            "success": False,
            "translated_code": "",
            "modules_used": [],
            "validation": None,
            "errors": [],
            "suggestions": []
        }
        
        try:
            # Analyze code if modules not specified
            if not modules:
                context = await self.context_analyzer.analyze_code(code)
                modules = self.context_analyzer.suggest_modules(context)
                result["suggestions"] = modules
            
            # Apply translators in order
            translated = code
            global_context = TranslationContext()
            
            # Order modules according to MODULE_ORDER
            ordered_modules = sorted(modules, 
                key=lambda m: self.module_order.index(m) if m in self.module_order else len(self.module_order))
            
            for module_name in ordered_modules:
                if module_name in self.translators:
                    translator = self.translators[module_name]
                    if translator.can_handle(translated):
                        translated, context = await translator.to_scitex(translated, global_context)
                        global_context.merge(context)
                        result["modules_used"].append(module_name)
            
            result["translated_code"] = translated
            
            # Validate if requested
            if validate:
                validation = self.translation_validator.validate_translation(
                    code, translated, "to_scitex"
                )
                result["validation"] = {
                    "valid": validation.valid,
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "suggestions": validation.suggestions,
                    "metrics": validation.metrics
                }
            
            result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    async def _translate_from_scitex(self, code: str, target_style: str = "standard",
                                    validate: bool = True) -> Dict[str, Any]:
        """Translate SciTeX to standard Python or other styles."""
        result = {
            "success": False,
            "translated_code": "",
            "target_style": target_style,
            "modules_detected": [],
            "validation": None,
            "errors": []
        }
        
        try:
            # Detect which modules are used
            modules_detected = []
            for module_name, translator in self.translators.items():
                if translator.can_handle(code):
                    modules_detected.append(module_name)
            
            result["modules_detected"] = modules_detected
            
            # Apply translators in reverse order (most general to most specific)
            translated = code
            global_context = TranslationContext()
            
            # Reverse order for from_scitex (gen -> io -> plt -> ai)
            ordered_modules = sorted(modules_detected,
                key=lambda m: self.module_order.index(m) if m in self.module_order else len(self.module_order),
                reverse=True)
            
            for module_name in ordered_modules:
                if module_name in self.translators:
                    translator = self.translators[module_name]
                    translated, context = await translator.from_scitex(
                        translated, target_style, global_context
                    )
                    global_context.merge(context)
            
            result["translated_code"] = translated
            
            # Validate if requested
            if validate:
                validation = self.translation_validator.validate_translation(
                    code, translated, "from_scitex"
                )
                result["validation"] = {
                    "valid": validation.valid,
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "suggestions": validation.suggestions,
                    "metrics": validation.metrics
                }
            
            result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    async def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code structure and suggest modules."""
        try:
            context = await self.context_analyzer.analyze_code(code)
            hints = self.context_analyzer.get_translation_hints(context)
            
            return {
                "imports": list(context.imports),
                "functions_used": list(context.functions_used),
                "patterns_found": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "module": p.module,
                        "confidence": p.confidence
                    }
                    for p in context.patterns_found
                ],
                "suggested_modules": hints["modules"],
                "style_hints": hints["style"],
                "confidence": hints["confidence"]
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    async def _validate_code(self, code: str, module: Optional[str] = None) -> Dict[str, Any]:
        """Validate code syntax, style, and complexity."""
        results = {}
        
        # Base validation
        syntax_valid, syntax_error = self.base_validator.validate_syntax(code)
        results["syntax"] = {
            "valid": syntax_valid,
            "error": syntax_error
        }
        
        if syntax_valid:
            # Import validation
            import_result = self.base_validator.validate_imports(code)
            results["imports"] = {
                "valid": import_result.valid,
                "errors": import_result.errors,
                "warnings": import_result.warnings,
                "metrics": import_result.metrics
            }
            
            # Style validation
            style_result = self.base_validator.validate_style(code)
            results["style"] = {
                "valid": style_result.valid,
                "warnings": style_result.warnings,
                "suggestions": style_result.suggestions,
                "metrics": style_result.metrics
            }
            
            # Complexity validation
            complexity_result = self.base_validator.validate_complexity(code)
            results["complexity"] = {
                "valid": complexity_result.valid,
                "warnings": complexity_result.warnings,
                "suggestions": complexity_result.suggestions,
                "metrics": complexity_result.metrics
            }
            
            # Module-specific validation
            if module and module in self.module_validators:
                module_result = self.module_validators[module].validate_module_specific(code)
                results["module_specific"] = {
                    "module": module,
                    "valid": module_result.valid,
                    "warnings": module_result.warnings,
                    "suggestions": module_result.suggestions
                }
        
        return results
    
    def _list_modules(self) -> Dict[str, Any]:
        """List all available modules and capabilities."""
        modules = {}
        
        for name, translator in self.translators.items():
            capabilities = translator.get_capabilities()
            modules[name] = {
                "functions": capabilities["functions"],
                "bidirectional": capabilities["bidirectional"],
                "target_styles": capabilities["target_styles"]
            }
        
        return {
            "available_modules": list(modules.keys()),
            "modules": modules,
            "total_translators": len(self.translators)
        }
    
    def _get_module_info(self, module: str) -> Dict[str, Any]:
        """Get detailed information about a module."""
        if module not in self.translators:
            return {"error": f"Module '{module}' not found"}
        
        translator = self.translators[module]
        capabilities = translator.get_capabilities()
        
        return {
            "module": module,
            "functions": capabilities["functions"],
            "standard_equivalents": capabilities["standard_equivalents"],
            "bidirectional": capabilities["bidirectional"],
            "target_styles": capabilities["target_styles"]
        }
    
    async def _batch_translate(self, snippets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Translate multiple code snippets."""
        results = []
        
        for i, snippet in enumerate(snippets):
            code = snippet.get("code", "")
            direction = snippet.get("direction", "to_scitex")
            
            try:
                if direction == "to_scitex":
                    result = await self._translate_to_scitex(code, validate=False)
                else:
                    result = await self._translate_from_scitex(code, validate=False)
                
                results.append({
                    "index": i,
                    "success": result["success"],
                    "translated": result["translated_code"],
                    "errors": result.get("errors", [])
                })
            
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "translated": "",
                    "errors": [str(e)]
                })
        
        return {
            "total": len(snippets),
            "successful": sum(1 for r in results if r["success"]),
            "results": results
        }
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server._options
            )


async def main():
    """Main entry point."""
    server = UnifiedTranslatorServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())