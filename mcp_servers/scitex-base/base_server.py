#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:03:00 (ywatanabe)"
# File: ./mcp_servers/scitex-base/base_server.py
# ----------------------------------------

"""Base MCP server class for SciTeX modules."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server


class ScitexBaseMCPServer(ABC):
    """Base class for SciTeX module-specific MCP servers."""
    
    def __init__(self, module_name: str, version: str = "0.1.0"):
        self.module_name = module_name
        self.version = version
        self.app = Server(f"scitex-{module_name}")
        self._register_base_tools()
        self._register_module_tools()
        
    def _register_base_tools(self):
        """Register tools common to all SciTeX MCP servers."""
        
        @self.app.tool()
        async def get_module_info() -> Dict[str, Any]:
            """Get information about this SciTeX module MCP server."""
            return {
                "module": self.module_name,
                "version": self.version,
                "description": self.get_module_description(),
                "available_tools": self.get_available_tools(),
            }
            
        @self.app.tool()
        async def validate_code(code: str) -> Dict[str, Any]:
            """Validate if code uses this module correctly."""
            return await self.validate_module_usage(code)
            
    @abstractmethod
    def _register_module_tools(self):
        """Register module-specific tools. Must be implemented by subclasses."""
        pass
        
    @abstractmethod
    def get_module_description(self) -> str:
        """Get description of this module's functionality."""
        pass
        
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this module."""
        pass
        
    @abstractmethod
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate module-specific usage patterns."""
        pass
        
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(read_stream, write_stream)


class ScitexTranslatorMixin:
    """Mixin for translation capabilities."""
    
    def create_translation_tools(self, module_prefix: str):
        """Create standard translation tools for a module."""
        
        @self.app.tool()
        async def translate_to_scitex(
            code: str,
            preserve_comments: bool = True,
            add_config_support: bool = True,
        ) -> Dict[str, Any]:
            """Translate standard Python to SciTeX format for this module."""
            return await self.module_to_scitex(code, preserve_comments, add_config_support)
            
        @self.app.tool()
        async def translate_from_scitex(
            code: str,
            target_style: str = "standard",
        ) -> Dict[str, Any]:
            """Translate SciTeX code back to standard Python for this module."""
            return await self.module_from_scitex(code, target_style)
            
        @self.app.tool()
        async def suggest_improvements(code: str) -> List[Dict[str, str]]:
            """Suggest SciTeX improvements for existing code."""
            return await self.analyze_improvement_opportunities(code)
            
    @abstractmethod
    async def module_to_scitex(
        self, 
        code: str, 
        preserve_comments: bool,
        add_config_support: bool
    ) -> Dict[str, Any]:
        """Module-specific translation to SciTeX."""
        pass
        
    @abstractmethod
    async def module_from_scitex(
        self,
        code: str,
        target_style: str
    ) -> Dict[str, Any]:
        """Module-specific translation from SciTeX."""
        pass
        
    @abstractmethod
    async def analyze_improvement_opportunities(
        self,
        code: str
    ) -> List[Dict[str, str]]:
        """Analyze code for SciTeX improvement opportunities."""
        pass


def create_mcp_server(server_class):
    """Factory function to create and run an MCP server."""
    async def main():
        server = server_class()
        await server.run()
        
    if __name__ == "__main__":
        asyncio.run(main())

# EOF