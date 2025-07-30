#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-30 21:35:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/.dev/debug_zenrows_cookie_visualization.py
# ----------------------------------------
"""Debug script to visualize cookie transfer process with ZenRows.

This script provides detailed logging and visualization of:
1. Initial cookies from authentication
2. Cookie capture from ZenRows responses
3. Cookie sending in subsequent requests
4. Cookie evolution over multiple requests
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


class CookieDebugger:
    """Debug helper for visualizing cookie flow."""
    
    def __init__(self):
        self.request_log: List[Dict] = []
        self.cookie_history: List[Dict] = []
        
    def log_request(self, url: str, cookies_sent: Dict[str, str], 
                   cookies_received: Dict[str, str], status: int):
        """Log a request with cookie details."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "cookies_sent": cookies_sent.copy(),
            "cookies_received": cookies_received.copy(),
            "status": status,
            "request_number": len(self.request_log) + 1
        }
        self.request_log.append(entry)
        
        # Track cookie evolution
        self.cookie_history.append({
            "request": len(self.request_log),
            "total_cookies": len(cookies_sent) + len(cookies_received),
            "new_cookies": len(cookies_received)
        })
        
    def display_summary(self):
        """Display visual summary of cookie flow."""
        
        # Request summary table
        table = Table(title="Cookie Transfer Summary")
        table.add_column("Request #", style="cyan", no_wrap=True)
        table.add_column("URL", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Sent", style="yellow")
        table.add_column("Received", style="blue")
        
        for entry in self.request_log:
            table.add_row(
                str(entry["request_number"]),
                entry["url"][:50] + "..." if len(entry["url"]) > 50 else entry["url"],
                str(entry["status"]),
                str(len(entry["cookies_sent"])),
                str(len(entry["cookies_received"]))
            )
            
        console.print(table)
        
        # Cookie details
        if self.request_log:
            latest = self.request_log[-1]
            
            # Sent cookies
            if latest["cookies_sent"]:
                sent_panel = Panel(
                    "\n".join([f"{k}: {v[:30]}..." for k, v in latest["cookies_sent"].items()]),
                    title="[yellow]Last Sent Cookies[/yellow]",
                    border_style="yellow"
                )
                console.print(sent_panel)
                
            # Received cookies
            if latest["cookies_received"]:
                received_panel = Panel(
                    "\n".join([f"{k}: {v[:30]}..." for k, v in latest["cookies_received"].items()]),
                    title="[blue]Last Received Cookies[/blue]",
                    border_style="blue"
                )
                console.print(received_panel)


async def debug_zenrows_cookie_flow():
    """Debug the complete cookie flow with ZenRows."""
    
    debugger = CookieDebugger()
    
    # Check for API key
    api_key = os.environ.get("ZENROWS_API_KEY")
    if not api_key:
        console.print("[red]❌ ZENROWS_API_KEY not found in environment[/red]")
        return
        
    console.print("[green]✅ ZenRows API key found[/green]")
    
    # Test URLs that typically set cookies
    test_urls = [
        {
            "name": "HTTPBin Cookie Test",
            "url": "https://httpbin.org/cookies/set?session_id=test123&user=debug"
        },
        {
            "name": "Nature Homepage",
            "url": "https://www.nature.com"
        },
        {
            "name": "DOI Resolver",
            "url": "https://doi.org/10.1038/nature12373"
        }
    ]
    
    session_id = str(asyncio.current_task().get_name())[:8]  # Simple session ID
    accumulated_cookies: Dict[str, str] = {}
    
    console.print(f"\n[cyan]Starting debug session: {session_id}[/cyan]\n")
    
    for i, test in enumerate(test_urls):
        console.print(f"\n[bold]Test {i+1}: {test['name']}[/bold]")
        console.print(f"URL: {test['url']}")
        
        # Prepare request
        params = {
            "url": test['url'],
            "apikey": api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": session_id,
            "wait": "3"
        }
        
        headers = {}
        if accumulated_cookies:
            # Send accumulated cookies
            cookie_string = "; ".join([f"{k}={v}" for k, v in accumulated_cookies.items()])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            console.print(f"[yellow]→ Sending {len(accumulated_cookies)} cookies[/yellow]")
        else:
            console.print("[dim]→ No cookies to send[/dim]")
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    status = response.status
                    console.print(f"[green]← Response: {status}[/green]")
                    
                    # Check for cookies in response
                    zr_cookies_header = response.headers.get('Zr-Cookies', '')
                    new_cookies = {}
                    
                    if zr_cookies_header:
                        # Parse cookies
                        for cookie in zr_cookies_header.split(';'):
                            cookie = cookie.strip()
                            if '=' in cookie:
                                name, value = cookie.split('=', 1)
                                new_cookies[name.strip()] = value.strip()
                                
                        console.print(f"[blue]← Received {len(new_cookies)} new cookies[/blue]")
                        
                        # Show cookie names
                        for name in new_cookies:
                            console.print(f"   • {name}")
                            
                        # Update accumulated cookies
                        accumulated_cookies.update(new_cookies)
                    else:
                        console.print("[dim]← No cookies received[/dim]")
                        
                    # Log the request
                    debugger.log_request(
                        test['url'],
                        accumulated_cookies if i > 0 else {},
                        new_cookies,
                        status
                    )
                    
                    # Show final URL if redirected
                    final_url = response.headers.get('Zr-Final-Url', '')
                    if final_url and final_url != test['url']:
                        console.print(f"[magenta]↪ Redirected to: {final_url}[/magenta]")
                        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            debugger.log_request(test['url'], accumulated_cookies, {}, 0)
            
        # Brief pause between requests
        await asyncio.sleep(1)
        
    # Display final summary
    console.print("\n" + "="*60 + "\n")
    debugger.display_summary()
    
    # Final cookie state
    if accumulated_cookies:
        final_panel = Panel(
            f"Total cookies accumulated: {len(accumulated_cookies)}\n\n" +
            "\n".join([f"• {k}" for k in accumulated_cookies.keys()]),
            title="[green]Final Cookie State[/green]",
            border_style="green"
        )
        console.print(final_panel)
    else:
        console.print("[yellow]No cookies were accumulated during the session[/yellow]")
        
    # Save detailed log
    log_file = Path(".dev/zenrows_cookie_debug_log.json")
    with open(log_file, "w") as f:
        json.dump({
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "requests": debugger.request_log,
            "final_cookies": accumulated_cookies
        }, f, indent=2)
        
    console.print(f"\n[dim]Detailed log saved to: {log_file}[/dim]")


async def test_specific_publisher(publisher_url: str, doi: Optional[str] = None):
    """Test cookie handling for a specific publisher."""
    
    console.print(f"\n[bold]Testing specific publisher[/bold]")
    console.print(f"URL: {publisher_url}")
    if doi:
        console.print(f"DOI: {doi}")
        
    # This would integrate with the full resolver
    # For now, just show the concept
    console.print("\n[yellow]To test with real authentication:[/yellow]")
    console.print("1. Run the full authentication flow first")
    console.print("2. Use the OpenURLResolverWithZenRows")
    console.print("3. Check if cookies enable access")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug ZenRows cookie transfer")
    parser.add_argument("--publisher", help="Test specific publisher URL")
    parser.add_argument("--doi", help="DOI to test")
    
    args = parser.parse_args()
    
    if args.publisher:
        asyncio.run(test_specific_publisher(args.publisher, args.doi))
    else:
        asyncio.run(debug_zenrows_cookie_flow())