#!/usr/bin/env python3
"""
Test popup window capture from OpenURL JavaScript links
Goal: Click the link, capture the popup, and get the publisher URL
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


async def test_popup_capture(paper_id, doi, openurl_query, link_text):
    """Test capturing popup window when clicking OpenURL link."""

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
            logger.info(f"Testing: {paper_id} - {doi}")
            logger.info(f"Looking for link: {link_text}")
            logger.info(f"{'='*60}")

            # Navigate to OpenURL
            logger.info(f"Navigating to OpenURL...")
            await page.goto(openurl_query, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Screenshot before click
            await page.screenshot(path=str(screenshot_dir / "before_click.png"))
            logger.info("Screenshot: before_click.png")

            # Find the link
            logger.info(f"Finding link containing: {link_text}")
            link = await page.query_selector(f'a:has-text("{link_text}")')

            if not link:
                logger.error(f"Link not found: {link_text}")
                return

            logger.info("Link found!")

            # Set up popup listener BEFORE clicking
            logger.info("Setting up popup listener...")
            popup_future = page.wait_for_event("popup", timeout=10000)

            # Click the link
            logger.info("Clicking link...")
            await link.click()

            # Wait for popup
            logger.info("Waiting for popup window...")
            popup_page = await popup_future

            logger.info(f"Popup opened!")
            logger.info(f"Popup URL: {popup_page.url}")

            # Wait for popup to load
            await popup_page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(3)

            # Screenshot the popup
            await popup_page.screenshot(
                path=str(screenshot_dir / "popup_page.png"),
                full_page=True
            )
            logger.info("Screenshot: popup_page.png")

            # Get popup HTML
            html = await popup_page.content()
            (screenshot_dir / "popup_page.html").write_text(html, encoding='utf-8')
            logger.info("Saved popup HTML")

            # Try to find PDF-related elements
            pdf_elements = await popup_page.evaluate("""
                () => {
                    const results = [];

                    // Look for PDF links
                    document.querySelectorAll('a').forEach(a => {
                        const text = a.textContent.toLowerCase();
                        const href = a.href.toLowerCase();
                        if (text.includes('pdf') ||
                            text.includes('download') ||
                            href.includes('.pdf') ||
                            href.includes('pdf')) {
                            results.push({
                                type: 'link',
                                text: a.textContent.trim(),
                                href: a.href
                            });
                        }
                    });

                    // Look for PDF buttons
                    document.querySelectorAll('button').forEach(btn => {
                        const text = btn.textContent.toLowerCase();
                        if (text.includes('pdf') || text.includes('download')) {
                            results.push({
                                type: 'button',
                                text: btn.textContent.trim(),
                                classes: Array.from(btn.classList).join(' ')
                            });
                        }
                    });

                    // Look for iframe with PDF
                    document.querySelectorAll('iframe').forEach(iframe => {
                        const src = iframe.src || '';
                        if (src.includes('.pdf') || src.includes('pdf')) {
                            results.push({
                                type: 'iframe',
                                src: src
                            });
                        }
                    });

                    return results;
                }
            """)

            logger.info(f"\nFound {len(pdf_elements)} PDF-related elements:")
            for elem in pdf_elements:
                logger.info(f"  Type: {elem['type']}")
                if 'href' in elem:
                    logger.info(f"  Text: {elem['text']}")
                    logger.info(f"  URL: {elem['href']}")
                elif 'src' in elem:
                    logger.info(f"  Src: {elem['src']}")
                else:
                    logger.info(f"  Text: {elem['text']}")
                logger.info("")

            # Save results
            import json
            results = {
                "paper_id": paper_id,
                "doi": doi,
                "openurl_query": openurl_query,
                "link_clicked": link_text,
                "popup_url": popup_page.url,
                "pdf_elements": pdf_elements
            }

            (screenshot_dir / "popup_results.json").write_text(
                json.dumps(results, indent=2)
            )
            logger.info("Results saved")

            # Keep popup open for inspection
            logger.info("\nKeeping popup open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)

            await popup_page.close()
            await page.close()

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            try:
                await page.screenshot(path=str(screenshot_dir / "error.png"))
            except:
                pass

        finally:
            await browser.close()


async def main():
    """Test popup capture for different publishers."""

    logger.info("Testing popup capture mechanism\n")

    # Test IEEE
    await test_popup_capture(
        paper_id="39305E03",
        doi="10.1109/niles56402.2022.9942397",
        openurl_query="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1109/niles56402.2022.9942397",
        link_text="IEEE"  # Partial text match
    )

    logger.info("\n" + "="*60)
    logger.info("Test complete!")
    logger.info("Check .dev/access_strategy_experiments/screenshots/39305E03/")


if __name__ == "__main__":
    asyncio.run(main())
