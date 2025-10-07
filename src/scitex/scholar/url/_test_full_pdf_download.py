#!/usr/bin/env python3
"""
Test full PDF download workflow: OpenURL → popup → click download → get PDF
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


async def test_full_download(paper_id, doi, openurl_query, link_text):
    """Test complete workflow to PDF download."""

    config = ScholarConfig()
    profile_dir = config.get_chrome_cache_dir("system")

    screenshot_dir = Path(f".dev/access_strategy_experiments/screenshots/{paper_id}")
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1920, "height": 1080},
        )

        page = await browser.new_page()

        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Full PDF Download Test: {paper_id}")
            logger.info(f"{'='*60}")

            # Step 1: Navigate to OpenURL
            logger.info("Step 1: Navigate to OpenURL...")
            await page.goto(openurl_query, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Step 2: Click link and capture popup
            logger.info(f"Step 2: Click '{link_text}' link...")
            link = await page.query_selector(f'a:has-text("{link_text}")')
            if not link:
                logger.error(f"Link not found: {link_text}")
                return

            popup_future = page.wait_for_event("popup", timeout=15000)
            await link.click()
            popup_page = await popup_future

            logger.info(f"  Popup opened: {popup_page.url}")
            await popup_page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(3)

            await popup_page.screenshot(path=str(screenshot_dir / "step2_popup.png"))

            # Step 3: Look for article link on search results page
            logger.info("Step 3: Find article link...")

            # IEEE search page - need to click on the article title
            article_links = await popup_page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a').forEach(a => {
                        const text = a.textContent.trim();
                        // Look for the article title
                        if (text.includes('FPGA Implementation') ||
                            text.includes('Epileptic Seizure')) {
                            links.push({
                                text: text.substring(0, 100),
                                href: a.href
                            });
                        }
                    });
                    return links;
                }
            """)

            logger.info(f"  Found {len(article_links)} potential article links")
            for link_data in article_links:
                logger.info(f"    - {link_data['text']}")
                logger.info(f"      {link_data['href']}")

            if not article_links:
                logger.error("  No article link found!")
                return

            # Click first article link
            logger.info("  Clicking first article link...")
            article_link = await popup_page.query_selector(f'a[href="{article_links[0]["href"]}"]')
            await article_link.click()

            await popup_page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(3)

            logger.info(f"  Article page: {popup_page.url}")
            await popup_page.screenshot(path=str(screenshot_dir / "step3_article.png"))

            # Step 4: Build PDF URL from article number
            logger.info("Step 4: Extract article number and build PDF URL...")

            # Extract from URL like: /document/9942397/
            import re
            match = re.search(r'/document/(\d+)', popup_page.url)
            if match:
                article_num = match.group(1)
                pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_num}"
                logger.info(f"  Article number: {article_num}")
                logger.info(f"  PDF URL: {pdf_url}")

                # Step 5: Navigate to PDF
                logger.info("Step 5: Navigate to PDF viewer...")
                await popup_page.goto(pdf_url, wait_until="load", timeout=30000)
                await asyncio.sleep(5)

                await popup_page.screenshot(
                    path=str(screenshot_dir / "step5_pdf_viewer.png"),
                    full_page=True
                )

                # Step 6: Check if PDF loaded
                logger.info("Step 6: Check PDF viewer...")
                pdf_info = await popup_page.evaluate("""
                    () => {
                        return {
                            has_embed: !!document.querySelector('embed[type="application/pdf"]'),
                            has_iframe: !!document.querySelector('iframe[src*=".pdf"]'),
                            title: document.title,
                            url: window.location.href
                        };
                    }
                """)

                logger.info(f"  PDF viewer present: {pdf_info['has_embed'] or pdf_info['has_iframe']}")
                logger.info(f"  Page title: {pdf_info['title']}")

                if pdf_info['has_embed'] or pdf_info['has_iframe']:
                    logger.success("✅ PDF viewer loaded successfully!")
                    logger.success(f"✅ PDF URL: {pdf_url}")

                    # Save results
                    import json
                    results = {
                        "success": True,
                        "paper_id": paper_id,
                        "doi": doi,
                        "article_number": article_num,
                        "pdf_url": pdf_url,
                        "pdf_viewer_loaded": True
                    }

                    (screenshot_dir / "full_download_results.json").write_text(
                        json.dumps(results, indent=2)
                    )

                    logger.info("\nKeeping PDF open for 10 seconds...")
                    await asyncio.sleep(10)

                else:
                    logger.error("❌ PDF viewer not detected")

            else:
                logger.error("  Could not extract article number from URL")

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            try:
                if 'popup_page' in locals():
                    await popup_page.screenshot(path=str(screenshot_dir / "error.png"))
            except:
                pass

        finally:
            await browser.close()


async def main():
    """Test full download workflow."""

    logger.info("Testing full PDF download workflow\n")

    await test_full_download(
        paper_id="39305E03",
        doi="10.1109/niles56402.2022.9942397",
        openurl_query="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1109/niles56402.2022.9942397",
        link_text="IEEE"
    )

    logger.info("\n" + "="*60)
    logger.info("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
