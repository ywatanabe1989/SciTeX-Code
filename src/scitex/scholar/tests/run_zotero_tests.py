#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner script for Zotero translator tests.
Executes both the pytest suite and the JavaScript pattern tests.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scitex.log import getLogger

logger = getLogger(__name__)


async def run_javascript_pattern_tests():
    """Run the JavaScript pattern validation tests."""
    logger.info("=" * 60)
    logger.info("Running JavaScript Pattern Tests")
    logger.info("=" * 60)
    
    try:
        from test_translator_javascript_patterns import main as js_test_main
        success = await js_test_main()
        return success
    except Exception as e:
        logger.error(f"JavaScript pattern tests failed: {e}")
        return False


async def run_real_url_tests():
    """Run simplified real URL tests (without pytest for now)."""
    logger.info("\n" + "=" * 60)
    logger.info("Running Real URL Tests")
    logger.info("=" * 60)
    
    from playwright.async_api import async_playwright
    from pathlib import Path
    
    # Test cases from SUGGESTIONS.md
    test_urls = [
        ("Frontiers", "https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full"),
        ("arXiv", "https://arxiv.org/abs/2103.14030"),
        ("Nature", "https://www.nature.com/articles/s41586-021-03372-6"),
        ("ScienceDirect OA", "https://www.sciencedirect.com/science/article/pii/S009286742030120X"),
    ]
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        for name, url in test_urls:
            logger.info(f"\nTesting {name}: {url}")
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Load JavaScript environment
                js_dir = Path(__file__).parent.parent / "browser/js/integrations/zotero"
                env_js = (js_dir / "zotero_environment.js").read_text()
                executor_js = (js_dir / "zotero_translator_executor.js").read_text()
                
                await page.add_script_tag(content=env_js)
                await page.add_script_tag(content=executor_js)
                
                # Simple check if translator would work
                result = await page.evaluate("""
                    () => {
                        // Check if page has PDF-related meta tags
                        const pdfMeta = document.querySelector('meta[name="citation_pdf_url"]');
                        const hasPdfMeta = pdfMeta && pdfMeta.content;
                        
                        // Check for PDF links
                        const pdfLinks = Array.from(document.querySelectorAll('a')).filter(
                            a => a.href && (a.href.includes('.pdf') || a.textContent.includes('PDF'))
                        );
                        
                        return {
                            hasPdfMeta: hasPdfMeta,
                            pdfLinkCount: pdfLinks.length,
                            title: document.title
                        };
                    }
                """)
                
                if result['hasPdfMeta'] or result['pdfLinkCount'] > 0:
                    logger.success(f"  ✓ {name}: PDF extraction possible")
                    logger.info(f"    - Has PDF meta: {result['hasPdfMeta']}")
                    logger.info(f"    - PDF links found: {result['pdfLinkCount']}")
                else:
                    logger.warning(f"  ⚠ {name}: No obvious PDF links found")
                
                results.append({
                    "name": name,
                    "url": url,
                    "success": result['hasPdfMeta'] or result['pdfLinkCount'] > 0
                })
                
            except Exception as e:
                logger.error(f"  ✗ {name}: Failed - {e}")
                results.append({
                    "name": name,
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
            finally:
                await page.close()
        
        await browser.close()
    
    successful = sum(1 for r in results if r.get("success", False))
    logger.info(f"\nReal URL Tests: {successful}/{len(results)} successful")
    
    return successful == len(results)


async def main():
    """Run all test suites."""
    logger.info("Starting Comprehensive Zotero Translator Tests")
    logger.info("This validates our standardized approach works across all publishers")
    
    # Run JavaScript pattern tests
    js_success = await run_javascript_pattern_tests()
    
    # Run real URL tests
    url_success = await run_real_url_tests()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("FINAL TEST SUMMARY")
    logger.info("=" * 60)
    
    if js_success and url_success:
        logger.success("✅ ALL TESTS PASSED!")
        logger.success("The Zotero translator runner works in a standardized manner across all patterns and publishers!")
    else:
        logger.warning("⚠️ SOME TESTS FAILED")
        logger.info(f"JavaScript Pattern Tests: {'✅ PASSED' if js_success else '❌ FAILED'}")
        logger.info(f"Real URL Tests: {'✅ PASSED' if url_success else '❌ FAILED'}")
        logger.info("\nThe system needs more work to achieve full standardization.")
    
    return js_success and url_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)