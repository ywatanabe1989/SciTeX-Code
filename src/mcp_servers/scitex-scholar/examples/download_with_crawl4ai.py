#!/usr/bin/env python3
"""Example: Download PDFs using Crawl4AI through MCP server."""

import asyncio
import json
from pathlib import Path


async def download_papers_example():
    """Demonstrate downloading papers with Crawl4AI."""
    
    # Example DOIs to download
    dois = [
        "10.1038/nature12373",  # Example Nature paper
        "10.1126/science.1234567",  # Example Science paper
        "10.1016/j.cell.2023.01.001"  # Example Cell paper
    ]
    
    # Note: In actual MCP usage through Claude, these would be MCP tool calls
    # This is a demonstration of the workflow
    
    print("=== SciTeX Scholar MCP - Crawl4AI Download Example ===\n")
    
    # Step 1: Configure Crawl4AI for specific publishers
    print("1. Configuring Crawl4AI profiles...")
    
    # Configure for Nature journals
    nature_config = {
        "profile_name": "nature_journals",
        "browser_type": "chromium",
        "headless": False,  # Show browser for demo
        "simulate_user": True,
        "viewport_size": [1920, 1080],
        "random_delays": True
    }
    print(f"   - Nature profile: {nature_config}")
    
    # Configure for Science journals
    science_config = {
        "profile_name": "science_journals",
        "browser_type": "chromium",
        "headless": True,
        "simulate_user": True
    }
    print(f"   - Science profile: {science_config}")
    
    # Step 2: Download PDFs one by one with appropriate profile
    print("\n2. Downloading PDFs...")
    
    for doi in dois:
        print(f"\n   Downloading: {doi}")
        
        # Determine profile based on DOI
        if "nature" in doi:
            profile = "nature_journals"
        elif "science" in doi:
            profile = "science_journals"
        else:
            profile = "scitex_academic"  # Default profile
        
        # Simulate MCP tool call
        download_args = {
            "doi": doi,
            "output_dir": "./pdfs/crawl4ai_demo",
            "profile_name": profile,
            "headless": False if profile == "nature_journals" else True
        }
        
        print(f"   Using profile: {profile}")
        print(f"   Output: {download_args['output_dir']}")
        
        # In real MCP usage, this would be:
        # result = await mcp_client.call_tool("download_with_crawl4ai", download_args)
        
    # Step 3: Batch download with progress tracking
    print("\n3. Batch download with progress tracking...")
    
    batch_args = {
        "dois": dois,
        "output_dir": "./pdfs/batch_demo",
        "strategy": "crawl4ai",
        "max_concurrent": 2
    }
    
    print(f"   Downloading {len(dois)} papers")
    print(f"   Max concurrent: {batch_args['max_concurrent']}")
    
    # Simulate batch download
    # batch_result = await mcp_client.call_tool("download_pdfs_batch", batch_args)
    
    # Step 4: Check download status
    print("\n4. Checking download status...")
    
    # status = await mcp_client.call_tool("get_download_status", {"batch_id": "download_20250801_120000"})
    
    print("\n=== Example Complete ===")
    print("\nKey features demonstrated:")
    print("- Publisher-specific Crawl4AI profiles")
    print("- Visual debugging with headless=False")
    print("- Batch downloads with concurrency control")
    print("- Progress tracking for large downloads")
    
    print("\nTo use in Claude:")
    print("1. Configure MCP server in Claude settings")
    print("2. Use tools like 'download_with_crawl4ai' directly")
    print("3. Claude will handle the async operations")


async def advanced_crawl4ai_example():
    """Advanced Crawl4AI configuration example."""
    
    print("\n\n=== Advanced Crawl4AI Configuration ===\n")
    
    # Example: Configure for a difficult paywall site
    paywall_config = {
        "profile_name": "aggressive_paywall",
        "browser_type": "chromium",
        "headless": False,
        "simulate_user": True,
        "viewport_size": [1920, 1080],
        "random_delays": True,
        # Additional stealth options could be added
    }
    
    print("Configuring for aggressive paywall site:")
    print(json.dumps(paywall_config, indent=2))
    
    # Example: Download with authentication
    print("\n\nDownloading with institutional authentication:")
    print("1. First login manually or with OpenAthens")
    print("2. Profile 'university_login' preserves cookies")
    print("3. Subsequent downloads use authenticated session")
    
    auth_download = {
        "doi": "10.1234/paywalled.2024.12345",
        "profile_name": "university_login",
        "headless": True,  # Can be headless after login
        "simulate_user": True
    }
    
    print(f"\nAuthenticated download config:")
    print(json.dumps(auth_download, indent=2))


if __name__ == "__main__":
    # Run examples
    asyncio.run(download_papers_example())
    asyncio.run(advanced_crawl4ai_example())
    
    print("\n\nNote: This example shows the workflow.")
    print("In actual use, these would be MCP tool calls from Claude.")
    print("Install the MCP server to use these features in Claude.")