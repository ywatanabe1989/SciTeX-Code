#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 11:04:00 (ywatanabe)"
# File: ./mcp_servers/test_integration.py
# ----------------------------------------

"""Integration test to verify all MCP servers can be imported and initialized."""

import sys
import os
from pathlib import Path

# Add mcp_servers to path
sys.path.insert(0, str(Path(__file__).parent))

def test_server_imports():
    """Test that all servers can be imported."""
    servers = [
        ("scitex-io", "server", "ScitexIoMCPServer"),
        ("scitex-plt", "server", "ScitexPltMCPServer"),
        ("scitex-analyzer", "server", "ScitexAnalyzerMCPServer"),
        ("scitex-framework", "server", "ScitexFrameworkMCPServer"),
        ("scitex-config", "server", "ScitexConfigMCPServer"),
        ("scitex-orchestrator", "server", "ScitexOrchestratorMCPServer"),
        ("scitex-validator", "server", "ScitexValidatorMCPServer"),
        ("scitex-stats", "server", "ScitexStatsMCPServer"),
        ("scitex-pd", "server", "ScitexPdMCPServer"),
        ("scitex-dsp", "server", "ScitexDspMCPServer"),
        ("scitex-torch", "server", "ScitexTorchMCPServer"),
    ]
    
    results = {"passed": [], "failed": []}
    
    for server_dir, module_name, class_name in servers:
        try:
            # Add server directory to path
            server_path = Path(__file__).parent / server_dir
            sys.path.insert(0, str(server_path))
            
            # Import module
            module = __import__(module_name, fromlist=[class_name])
            
            # Get class
            server_class = getattr(module, class_name)
            
            # Check it's a class
            if isinstance(server_class, type):
                results["passed"].append(f"{server_dir}/{module_name}")
                print(f"✅ {server_dir}/{module_name}.py")
            else:
                raise Exception(f"{class_name} is not a class")
            
            # Remove from path
            sys.path.pop(0)
            
        except Exception as e:
            results["failed"].append((f"{server_dir}/{module_name}", str(e)))
            print(f"❌ {server_dir}/{module_name}.py: {e}")
            if sys.path[0] == str(server_path):
                sys.path.pop(0)
    
    return results

def test_server_tools():
    """Test that servers have required methods."""
    # Import from a specific server
    server_path = Path(__file__).parent / "scitex-io"
    sys.path.insert(0, str(server_path))
    
    try:
        from server import ScitexIoMCPServer
        server = ScitexIoMCPServer()
    finally:
        sys.path.pop(0)
    
    # Check required methods exist
    required_methods = [
        "get_module_description",
        "get_available_tools",
        "validate_module_usage"
    ]
    
    results = {"passed": [], "failed": []}
    
    for method in required_methods:
        if hasattr(server, method):
            results["passed"].append(method)
            print(f"✅ Method exists: {method}")
        else:
            results["failed"].append(method)
            print(f"❌ Missing method: {method}")
    
    return results

def main():
    """Run all integration tests."""
    print("SciTeX MCP Servers Integration Test")
    print("=" * 50)
    
    print("\n1. Testing Server Imports:")
    print("-" * 30)
    import_results = test_server_imports()
    
    print("\n2. Testing Server Methods:")
    print("-" * 30)
    method_results = test_server_tools()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Import Tests: {len(import_results['passed'])} passed, {len(import_results['failed'])} failed")
    print(f"Method Tests: {len(method_results['passed'])} passed, {len(method_results['failed'])} failed")
    
    if import_results['failed'] or method_results['failed']:
        print("\nFAILED TESTS:")
        for module, error in import_results['failed']:
            print(f"  - {module}: {error}")
        for method in method_results['failed']:
            print(f"  - Missing method: {method}")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

# EOF