#!/usr/bin/env python3
"""Enhanced error diagnostics for Scholar PDF download_asyncs.

This module provides detailed error analysis and troubleshooting
suggestions to help users quickly resolve download_async issues.
"""

import json
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from ...errors import PDFDownloadError, ScholarError


class DownloadErrorDiagnostics:
    """Analyze download_async errors and provide actionable diagnostics."""
    
    # Common error patterns and their solutions
    ERROR_PATTERNS = {
        # Authentication errors
        r"401|unauthorized|authentication required": {
            "category": "authentication",
            "message": "Authentication required",
            "solutions": [
                "Enable institutional authentication (OpenAthens)",
                "Check if your institution has access to this journal",
                "Try using a VPN connected to your institution",
                "Use ZenRows API key for anti-bot bypass"
            ]
        },
        
        # Access denied
        r"403|forbidden|access denied": {
            "category": "access_denied",
            "message": "Access denied by publisher",
            "solutions": [
                "Paper may be behind paywall - check institutional access",
                "Try accessing from campus network",
                "Enable cookies and JavaScript in browser",
                "Some publishers block automated download_asyncs"
            ]
        },
        
        # Rate limiting
        r"429|rate limit|too many requests": {
            "category": "rate_limit",
            "message": "Rate limit exceeded",
            "solutions": [
                "Wait a few minutes before retrying",
                "Reduce concurrent download_asyncs (max_concurrent parameter)",
                "Use different IP address or proxy",
                "Add delays between requests"
            ]
        },
        
        # Bot detection
        r"captcha|robot|bot|human verification|cloudflare": {
            "category": "bot_detection",
            "message": "Bot detection triggered",
            "solutions": [
                "Use ZenRows API with JavaScript rendering",
                "Enable Playwright with stealth mode",
                "Try manual download_async through browser",
                "Use institutional proxy/VPN"
            ]
        },
        
        # Network errors
        r"timeout|timed out|connection reset|connection refused": {
            "category": "network",
            "message": "Network connectivity issue",
            "solutions": [
                "Check internet connection",
                "Increase timeout parameter",
                "Try using a different network",
                "Check if publisher site is down"
            ]
        },
        
        # Invalid DOI/URL
        r"404|not found|invalid doi|unknown doi": {
            "category": "not_found",
            "message": "DOI or URL not found",
            "solutions": [
                "Verify the DOI is correct",
                "Check if paper has been retracted",
                "Try searching by title instead",
                "Paper may not have a PDF available"
            ]
        },
        
        # PDF detection
        r"no pdf|pdf not found|unable to locate pdf": {
            "category": "pdf_detection",
            "message": "Could not find PDF on page",
            "solutions": [
                "Paper may only have HTML version",
                "PDF might require additional clicks to access",
                "Try using Zotero translators",
                "Check if PDF is in supplementary materials"
            ]
        },
        
        # Server errors
        r"500|502|503|internal server error|bad gateway": {
            "category": "server_error",
            "message": "Publisher server error",
            "solutions": [
                "Wait and retry later - server may be down",
                "Try accessing publisher site directly",
                "Check publisher's status page",
                "Report issue to publisher if persistent"
            ]
        }
    }
    
    def __init__(self, debug_dir: Optional[Path] = None):
        """Initialize diagnostics.
        
        Args:
            debug_dir: Directory to save diagnostic files
        """
        self.debug_dir = Path(debug_dir or "./scholar_debug")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze an error and provide diagnostics.
        
        Args:
            error: The exception that occurred
            context: Context information (url, doi, method, etc.)
            
        Returns:
            Diagnostic report dictionary
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Match error patterns
        matched_pattern = None
        for pattern, info in self.ERROR_PATTERNS.items():
            if re.search(pattern, error_str, re.IGNORECASE):
                matched_pattern = info
                break
        
        # Build diagnostic report
        report = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": str(error),
            "category": matched_pattern["category"] if matched_pattern else "unknown",
            "diagnosis": matched_pattern["message"] if matched_pattern else "Unknown error",
            "solutions": matched_pattern["solutions"] if matched_pattern else [],
            "context": context,
            "traceback": traceback.format_exc() if context.get("include_traceback") else None,
        }
        
        # Add specific diagnostics based on context
        self._add_context_diagnostics(report, context)
        
        # Save diagnostic report if requested
        if context.get("save_diagnostics", True):
            self.save_diagnostic_report(report, context.get("identifier", "unknown"))
        
        return report
    
    def _add_context_diagnostics(
        self,
        report: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """Add context-specific diagnostics."""
        
        # URL/DOI diagnostics
        if "url" in context:
            url_info = self._analyze_url(context["url"])
            report["url_analysis"] = url_info
            
            # Publisher-specific advice
            if url_info["publisher"]:
                report["publisher_notes"] = self._get_publisher_notes(
                    url_info["publisher"]
                )
        
        # Method-specific diagnostics
        if "method" in context:
            report["method_notes"] = self._get_method_notes(
                context["method"],
                report["category"]
            )
        
        # Network diagnostics
        if report["category"] == "network":
            report["network_diagnostics"] = self._get_network_diagnostics(context)
        
        # Add screenshot path if available
        if "screenshot_path" in context:
            report["screenshot"] = str(context["screenshot_path"])
            report["solutions"].append(
                f"Check screenshot for visual clues: {context['screenshot_path']}"
            )
    
    def _analyze_url(self, url: str) -> Dict[str, str]:
        """Analyze URL for diagnostic information."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Identify publisher
        publisher_map = {
            "nature.com": "Nature",
            "science.org": "Science/AAAS",
            "sciencedirect.com": "Elsevier",
            "cell.com": "Cell Press",
            "wiley.com": "Wiley",
            "springer.com": "Springer",
            "tandfonline.com": "Taylor & Francis",
            "oup.com": "Oxford University Press",
            "cambridge.org": "Cambridge University Press",
            "pnas.org": "PNAS",
            "plos.org": "PLOS",
            "ieee.org": "IEEE",
            "acm.org": "ACM",
            "acs.org": "ACS Publications",
            "rsc.org": "Royal Society of Chemistry",
        }
        
        publisher = None
        for domain_pattern, pub_name in publisher_map.items():
            if domain_pattern in domain:
                publisher = pub_name
                break
        
        return {
            "domain": domain,
            "publisher": publisher,
            "protocol": parsed.scheme,
            "path": parsed.path,
        }
    
    def _get_publisher_notes(self, publisher: str) -> List[str]:
        """Get publisher-specific troubleshooting notes."""
        notes = {
            "Nature": [
                "Nature requires institutional access for most papers",
                "Try using your institution's library proxy",
                "Some Nature papers have free PDF links after embargo"
            ],
            "Science/AAAS": [
                "Science uses complex JavaScript rendering",
                "Enable Playwright or ZenRows for better success",
                "Check if paper is in Science's free archive"
            ],
            "Elsevier": [
                "Elsevier often requires cookies from ScienceDirect",
                "May need to accept terms of use",
                "Try accessing via your library's ScienceDirect portal"
            ],
            "Wiley": [
                "Wiley uses aggressive bot detection",
                "ZenRows with JavaScript rendering recommended",
                "Some Wiley journals offer free access after 12 months"
            ],
        }
        
        return notes.get(publisher, [f"No specific notes for {publisher}"])
    
    def _get_method_notes(self, method: str, error_category: str) -> List[str]:
        """Get method-specific diagnostic notes."""
        notes = {
            "ZenRows": {
                "bot_detection": [
                    "ZenRows should bypass most bot detection",
                    "Ensure your API key is valid and has credits",
                    "Try enabling JavaScript rendering"
                ],
                "authentication": [
                    "ZenRows cannot handle institutional logins",
                    "Use OpenAthens or manual authentication first"
                ],
            },
            "Playwright": {
                "timeout": [
                    "Increase timeout for slow-loading pages",
                    "Check if Playwright browsers are installed",
                    "Try headless=False to see what's happening"
                ],
                "bot_detection": [
                    "Enable stealth mode in Playwright",
                    "Use undetected-playwright package",
                    "Add random delays between actions"
                ],
            },
            "Direct": {
                "pdf_detection": [
                    "Direct download_async couldn't find PDF link",
                    "Page may require JavaScript rendering",
                    "Try Playwright or Zotero translators"
                ],
            },
        }
        
        method_notes = notes.get(method, {})
        return method_notes.get(error_category, [f"No specific notes for {method}"])
    
    def _get_network_diagnostics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get network-specific diagnostics."""
        diagnostics = {
            "suggestions": [
                "Test connection: ping " + urlparse(context.get("url", "")).netloc,
                "Check DNS resolution",
                "Try using a different DNS server (8.8.8.8)",
                "Check if firewall is blocking requests"
            ]
        }
        
        if "status_code" in context:
            diagnostics["http_status"] = context["status_code"]
            diagnostics["status_meaning"] = self._get_status_meaning(
                context["status_code"]
            )
        
        return diagnostics
    
    def _get_status_meaning(self, status_code: int) -> str:
        """Get human-readable meaning of HTTP status code."""
        meanings = {
            200: "OK - Request successful",
            301: "Moved Permanently - URL has changed",
            302: "Found - Temporary redirect",
            400: "Bad Request - Invalid request format",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource doesn't exist",
            429: "Too Many Requests - Rate limited",
            500: "Internal Server Error - Server problem",
            502: "Bad Gateway - Proxy/gateway error",
            503: "Service Unavailable - Server overloaded",
            504: "Gateway Timeout - Proxy timeout",
        }
        
        return meanings.get(status_code, f"HTTP {status_code}")
    
    def save_diagnostic_report(
        self,
        report: Dict[str, Any],
        identifier: str
    ):
        """Save diagnostic report to file.
        
        Args:
            report: Diagnostic report
            identifier: DOI or identifier for filename
        """
        # Clean identifier for filename
        clean_id = re.sub(r'[^\w.-]', '_', identifier)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = self.debug_dir / f"error_{clean_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def create_summary_report(
        self,
        all_errors: List[Dict[str, Any]]
    ) -> str:
        """Create a summary report of all errors.
        
        Args:
            all_errors: List of error reports
            
        Returns:
            Formatted summary report
        """
        if not all_errors:
            return "No errors to report"
        
        # Group by category
        by_category = {}
        for error in all_errors:
            cat = error.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(error)
        
        # Build summary
        lines = ["=== Download Error Summary ===\n"]
        lines.append(f"Total errors: {len(all_errors)}")
        lines.append(f"Error categories: {', '.join(by_category.keys())}\n")
        
        # Category breakdowns
        for category, errors in by_category.items():
            lines.append(f"\n{category.upper()} ({len(errors)} errors):")
            
            # Get unique solutions
            all_solutions = set()
            for error in errors:
                all_solutions.update(error.get("solutions", []))
            
            if all_solutions:
                lines.append("  Recommended solutions:")
                for solution in sorted(all_solutions):
                    lines.append(f"    • {solution}")
        
        # Most common publishers with errors
        publishers = {}
        for error in all_errors:
            pub = error.get("url_analysis", {}).get("publisher", "Unknown")
            publishers[pub] = publishers.get(pub, 0) + 1
        
        if publishers:
            lines.append("\n\nPublishers with errors:")
            for pub, count in sorted(publishers.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {pub}: {count} errors")
        
        return "\n".join(lines)


def create_diagnostic_report(
    error: Exception,
    doi: Optional[str] = None,
    url: Optional[str] = None,
    method: Optional[str] = None,
    save_screenshot: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to create diagnostic report.
    
    Args:
        error: The exception
        doi: DOI if available
        url: URL if available  
        method: Download method used
        save_screenshot: Whether to capture screenshot
        **kwargs: Additional context
        
    Returns:
        Diagnostic report
    """
    diagnostics = DownloadErrorDiagnostics()
    
    context = {
        "identifier": doi or url or "unknown",
        "doi": doi,
        "url": url,
        "method": method,
        "save_diagnostics": True,
        **kwargs
    }
    
    report = diagnostics.analyze_error(error, context)
    
    return report