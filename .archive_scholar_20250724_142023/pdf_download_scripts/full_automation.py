#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-22 23:25:28 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/full_automation.py
# ----------------------------------------
import os
__FILE__ = (
    "./full_automation.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Full Automation with Zotero Connection Test
Tests connection and implements complete automation
"""

import asyncio
import subprocess
import uuid
from pathlib import Path
from urllib.parse import urljoin

import aiohttp


class FullAutomationDownloader:
    """Fully automated downloader with Zotero integration"""

    def __init__(self, headless=True):
        self.headless = headless
        self.is_wsl2 = self._detect_wsl2()
        self.windows_username = self._get_windows_username()
        self.download_dir = Path("./downloads")
        self.download_dir.mkdir(exist_ok=True)

        # Set up Zotero connection
        self.zotero_urls = self._get_zotero_urls()
        self.working_zotero_url = None

    def _detect_wsl2(self):
        """Detect WSL2"""
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except:
            return False

    def _get_windows_username(self):
        """Get Windows username"""
        try:
            result = subprocess.run(
                ["cmd.exe", "/c", "echo %USERNAME%"],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except:
            return "User"

    def _get_windows_host_ip(self):
        """Get Windows host IP"""
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True,
                text=True,
            )
            return result.stdout.split()[2]
        except:
            return None

    def _get_zotero_urls(self):
        """Get potential Zotero URLs to test"""
        urls = [
            "http://127.0.0.1:23119",
            "http://localhost:23119",
        ]

        if self.is_wsl2:
            windows_ip = self._get_windows_host_ip()
            if windows_ip:
                urls.append(f"http://{windows_ip}:23119")

        return urls

    async def test_zotero_connection(self):
        """Test Zotero connection with detailed diagnostics"""

        print("🔍 TESTING ZOTERO CONNECTION")
        print("=" * 50)

        for url in self.zotero_urls:
            print(f"Testing: {url}")

            try:
                async with aiohttp.ClientSession() as session:
                    # Test ping
                    async with session.get(
                        f"{url}/connector/ping", timeout=5
                    ) as response:
                        if response.status == 200:
                            print(f"  ✅ Ping successful")

                            # Test translator availability
                            test_payload = {
                                "url": "https://www.nature.com/articles/",
                                "sessionID": f"test-{uuid.uuid4().hex[:8]}",
                            }

                            async with session.post(
                                f"{url}/connector/getTranslators",
                                json=test_payload,
                                timeout=10,
                            ) as trans_response:

                                if trans_response.status == 200:
                                    translators = await trans_response.json()
                                    print(
                                        f"  ✅ Translators available: {len(translators)}"
                                    )
                                    print(f"  🎉 WORKING CONNECTION FOUND!")
                                    self.working_zotero_url = url
                                    return True
                                else:
                                    print(
                                        f"  ⚠️ Translators test failed: {trans_response.status}"
                                    )
                        else:
                            print(f"  ❌ Ping failed: HTTP {response.status}")

            except asyncio.TimeoutError:
                print(f"  ❌ Timeout")
            except Exception as e:
                print(f"  ❌ Error: {type(e).__name__}")

        print(f"\n❌ No working Zotero connection found")
        return False

    def _get_chrome_profile_path(self):
        """Get Chrome profile path"""
        if self.is_wsl2:
            profile_path = f"/mnt/c/Users/{self.windows_username}/AppData/Local/Google/Chrome/User Data/Default"
            if Path(profile_path).exists():
                return profile_path

        return str(Path.home() / ".config" / "google-chrome-default")

    async def fully_automated_download(self, dois):
        """Fully automated download with Zotero integration"""

        # Test connection first
        if not await self.test_zotero_connection():
            print("\n❌ Cannot proceed without Zotero connection")
            print("💡 Troubleshooting steps:")
            print("   1. Ensure Zotero is running on Windows")
            print("   2. Check connector is enabled in Zotero preferences")
            print("   3. Try restarting Zotero")
            print("   4. Run the portproxy command again if needed")
            return None

        print(f"\n🚀 FULLY AUTOMATED PROCESSING")
        print(f"=" * 50)
        print(f"Zotero URL: {self.working_zotero_url}")
        print(f"DOIs to process: {len(dois)}")
        print(f"Mode: {'Headless' if self.headless else 'Visible'}")
        print("=" * 50)

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("❌ Playwright not installed")
            print("Run: pip install playwright && playwright install chromium")
            return None

        results = {
            "successful": 0,
            "failed": 0,
            "total": len(dois),
            "saved_papers": [],
            "downloaded_pdfs": [],
        }

        profile_dir = self._get_chrome_profile_path()

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=self.headless,
                downloads_path=str(self.download_dir),
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-extensions" if self.headless else "",
                ],
                accept_downloads=True,
                timeout=60000,
            )

            page = await browser.new_page()
            downloads = []

            def handle_download(download):
                downloads.append(download)
                print(
                    f"    📥 Download started: {download.suggested_filename}"
                )

            page.on("download", handle_download)

            try:
                for i, doi in enumerate(dois):
                    print(f"\n[{i+1}/{len(dois)}] 🎯 Processing: {doi}")

                    success = await self._process_single_paper_full_auto(
                        page, doi
                    )

                    if success:
                        results["successful"] += 1
                        results["saved_papers"].append(doi)
                    else:
                        results["failed"] += 1

                    # Brief pause between papers
                    if i < len(dois) - 1:
                        await asyncio.sleep(3)

                # Wait for pending downloads
                if downloads:
                    print(
                        f"\n⏳ Waiting for {len(downloads)} downloads to complete..."
                    )
                    for download in downloads:
                        try:
                            path = await download.path()
                            print(
                                f"    ✅ Download completed: {download.suggested_filename}"
                            )
                            results["downloaded_pdfs"].append(str(path))
                        except Exception as e:
                            print(f"    ⚠️ Download issue: {e}")

            finally:
                await browser.close()

        return results

    async def _process_single_paper_full_auto(self, page, doi):
        """Process single paper with full automation"""

        try:
            url = f"https://doi.org/{doi}"

            print(f"    🌐 Navigating to: {url}")
            await page.goto(url, timeout=45000, wait_until="networkidle")

            # Wait for authentication
            print(f"    🔐 Waiting for authentication...")
            await asyncio.sleep(12)  # Increased wait time

            # Check for authentication/access indicators
            auth_indicators = [
                "university of melbourne",
                "melbourne uni",
                "your institution",
                "full access",
                "authenticated",
                "download pdf",
                "view pdf",
            ]

            page_text = await page.text_content("body")
            if page_text:
                page_text_lower = page_text.lower()
                is_authenticated = any(
                    indicator in page_text_lower
                    for indicator in auth_indicators
                )

                if is_authenticated:
                    print(f"    ✅ Access confirmed")
                else:
                    print(f"    ⚠️ Access uncertain - continuing...")

            # Automated PDF download
            pdf_downloaded = await self._automated_pdf_download(page, doi)

            # Save to Zotero
            final_url = page.url
            page_html = await page.content()

            zotero_saved = await self._save_to_zotero_automated(
                final_url, page_html
            )

            success = zotero_saved or pdf_downloaded

            if success:
                print(f"    ✅ Paper processed successfully")

                if zotero_saved:
                    print(f"        📚 Saved to Zotero")
                if pdf_downloaded:
                    print(f"        📄 PDF downloaded")
            else:
                print(f"    ❌ Processing failed")

            return success

        except Exception as e:
            print(f"    ❌ Error processing {doi}: {e}")
            return False

    async def _automated_pdf_download(self, page, doi):
        """Automated PDF detection and download"""

        print(f"    🔍 Searching for PDF...")

        # Enhanced PDF selectors for major publishers
        pdf_selectors = [
            # Nature/Springer specific
            'a[data-track-action*="download pdf"]',
            'a[data-track-action*="view pdf"]',
            'a[aria-label*="Download PDF"]',
            'a[title*="Download PDF"]',
            # General PDF patterns
            'a[href*=".pdf"]',
            'a:has-text("Download PDF"):visible',
            'a:has-text("View PDF"):visible',
            'a:has-text("PDF"):visible',
            'button:has-text("Download PDF"):visible',
            'button:has-text("PDF"):visible',
            # More generic patterns
            'a[href*="pdf"]',
            'a[download*=".pdf"]',
            ".pdf-download-btn",
            ".download-pdf",
        ]

        for selector in pdf_selectors:
            try:
                elements = await page.locator(selector).all()

                if elements:
                    print(
                        f"    📄 Found {len(elements)} PDF elements with: {selector}"
                    )

                    for element in elements:
                        try:
                            if await element.is_visible():
                                text = await element.text_content()
                                href = await element.get_attribute("href")

                                print(f"    👆 Clicking: {text} ({href})")

                                # Attempt download
                                with page.expect_download(
                                    timeout=30000
                                ) as download_info:
                                    await element.click()

                                download = await download_info.value

                                # Save with DOI-based name
                                pdf_filename = f"{doi.replace('/', '_').replace('.', '_')}.pdf"
                                pdf_path = self.download_dir / pdf_filename

                                await download.save_as(pdf_path)
                                print(f"    ✅ PDF saved: {pdf_path}")

                                return True

                        except Exception as e:
                            print(f"    ⚠️ Click failed: {e}")
                            continue

            except Exception:
                continue  # Try next selector

        # Fallback: Try direct PDF URL extraction
        print(f"    🔄 Trying direct PDF extraction...")
        return await self._try_direct_pdf_extraction(page, doi)

    async def _try_direct_pdf_extraction(self, page, doi):
        """Try direct PDF URL extraction and download"""

        try:
            pdf_urls = await page.evaluate(
                """
                () => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links
                        .filter(link => {
                            const href = link.href || '';
                            const text = link.textContent || '';
                            return href.toLowerCase().includes('.pdf') ||
                                   href.toLowerCase().includes('pdf') ||
                                   text.toLowerCase().includes('pdf');
                        })
                        .map(link => ({
                            url: link.href,
                            text: link.textContent.trim()
                        }));
                }
            """
            )

            if pdf_urls:
                print(f"    🔗 Found {len(pdf_urls)} PDF URLs")

                for pdf_info in pdf_urls[:3]:  # Try first 3
                    try:
                        pdf_url = pdf_info["url"]
                        print(f"    📥 Trying: {pdf_url}")

                        response = await page.goto(pdf_url, timeout=30000)

                        if response and response.status == 200:
                            content_type = response.headers.get(
                                "content-type", ""
                            )

                            if "pdf" in content_type.lower():
                                pdf_filename = f"{doi.replace('/', '_').replace('.', '_')}.pdf"
                                pdf_path = self.download_dir / pdf_filename

                                pdf_content = await response.body()
                                with open(pdf_path, "wb") as f:
                                    f.write(pdf_content)

                                print(
                                    f"    ✅ Direct download successful: {pdf_path}"
                                )
                                return True

                    except Exception as e:
                        print(f"    ⚠️ Direct download failed: {e}")
                        continue

        except Exception as e:
            print(f"    ❌ PDF extraction error: {e}")

        return False

    async def _save_to_zotero_automated(self, page_url, page_html=None):
        """Save to Zotero using the working connection"""

        if not self.working_zotero_url:
            print(f"    ❌ No Zotero connection available")
            return False

        session_id = f"auto-{uuid.uuid4().hex[:8]}"

        try:
            async with aiohttp.ClientSession() as session:
                # Get translators
                translator_payload = {"url": page_url, "sessionID": session_id}
                if page_html:
                    translator_payload["html"] = page_html

                async with session.post(
                    f"{self.working_zotero_url}/connector/getTranslators",
                    json=translator_payload,
                    timeout=15,
                ) as response:

                    if response.status != 200:
                        print(
                            f"    ❌ Zotero translators failed: {response.status}"
                        )
                        return False

                    translators = await response.json()
                    if not translators:
                        print(f"    ❌ No Zotero translators found")
                        return False

                    translator = translators[0]
                    print(
                        f"    📚 Using translator: {translator.get('label', 'Unknown')}"
                    )

                # Save items
                save_payload = {
                    "url": page_url,
                    "sessionID": session_id,
                    "translatorID": translator["translatorID"],
                }

                if page_html:
                    save_payload["html"] = page_html

                async with session.post(
                    f"{self.working_zotero_url}/connector/saveItems",
                    json=save_payload,
                    timeout=30,
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            print(f"    ✅ Saved to Zotero")
                            return True
                        else:
                            print(
                                f"    ❌ Zotero save failed: {result.get('message')}"
                            )
                    else:
                        print(f"    ❌ Zotero save error: {response.status}")

                    return False

        except Exception as e:
            print(f"    ❌ Zotero error: {e}")
            return False


def read_dois_from_file(file_path):
    """Read DOIs from file"""
    dois = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "doi.org/" in line:
                        doi = line.split("doi.org/")[-1]
                    else:
                        doi = line
                    dois.append(doi)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
    return dois


async def main():
    """Main function for full automation"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Full Automation Academic Paper Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Full automation with Zotero integration:
- Tests Zotero connection first
- Automated authentication handling
- Intelligent PDF detection and download
- Complete Zotero integration
- Works with WSL2 + Windows setup

Examples:
  python full_auto.py --test
  python full_auto.py 10.1038/s41593-025-01990-7
  python full_auto.py --file dois.txt
  python full_auto.py --no-headless 10.1038/s41593-025-01990-7
        """,
    )

    parser.add_argument("dois", nargs="*", help="DOI strings")
    parser.add_argument("--file", "-f", help="File containing DOIs")
    parser.add_argument(
        "--test", action="store_true", help="Test with sample DOI"
    )
    parser.add_argument(
        "--no-headless", action="store_true", help="Show browser"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Zotero connection only",
    )

    args = parser.parse_args()

    headless = not args.no_headless

    downloader = FullAutomationDownloader(headless=headless)

    # Test connection only
    if args.test_connection:
        await downloader.test_zotero_connection()
        return

    # Get DOIs
    if args.test:
        dois = ["10.1038/s41593-025-01990-7"]
        print("🧪 Testing with Nature Neuroscience paper")
    elif args.file:
        dois = read_dois_from_file(args.file)
    elif args.dois:
        dois = args.dois
    else:
        parser.print_help()
        return

    if not dois:
        print("❌ No DOIs provided")
        return

    print("🤖 FULL AUTOMATION DOWNLOADER")
    print("=" * 50)
    print(f"Mode: {'Headless' if headless else 'Visible Browser'}")
    print(f"DOIs: {len(dois)}")
    print(f"Features: Zotero + PDF + Authentication")
    print("=" * 50)

    # Process papers
    results = await downloader.fully_automated_download(dois)

    if results:
        print(f"\n🎉 FULL AUTOMATION COMPLETE!")
        print(f"=" * 50)
        print(f"Total: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"PDFs downloaded: {len(results['downloaded_pdfs'])}")

        if results["total"] > 0:
            success_rate = results["successful"] / results["total"] * 100
            print(f"Success rate: {success_rate:.1f}%")

        if results["saved_papers"]:
            print(f"\n📚 Saved papers:")
            for doi in results["saved_papers"]:
                print(f"  ✅ {doi}")

        if results["downloaded_pdfs"]:
            print(f"\n📄 Downloaded PDFs:")
            for pdf in results["downloaded_pdfs"][:5]:  # Show first 5
                print(f"  📥 {Path(pdf).name}")
            if len(results["downloaded_pdfs"]) > 5:
                print(f"  ... and {len(results['downloaded_pdfs']) - 5} more")

        print(f"\n💡 Check:")
        print(f"   📚 Zotero library for references")
        print(f"   📁 ./downloads/ for PDFs")


if __name__ == "__main__":
    asyncio.run(main())

# EOF
