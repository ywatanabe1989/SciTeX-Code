#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 02:09:05 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/ScholarPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import base64
import time
from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar import ScholarURLFinder
from scitex.scholar.browser import PlaywrightVision

logger = logging.getLogger(__name__)

from playwright.async_api import async_playwright

# Downloaded files are deleted when the browser context that produced them is closed.


class ScholarPDFDownloader:
    def __init__(
        self,
        context: BrowserContext,
    ):
        self.context = context
        self.url_finder = ScholarURLFinder(self.context)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def download_from_url(
        self, pdf_url: str, output_path: Union[str, Path]
    ) -> Optional[Path]:
        """
        Main download method that tries all options in order.
        Returns the path if successful, None otherwise.
        """
        if isinstance(output_path, str):
            output_path = Path(output_path)

        if not str(output_path).endswith(".pdf"):
            output_path = Path(str(output_path) + ".pdf")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Try each download method in order of reliability/speed
        download_methods = [
            (
                "Development",
                self._try_download_from_url_with_option_00_development,
            ),
            # (
            #     "Direct Request",
            #     self._try_download_from_url_with_option_01_direct_request,
            # ),
            # (
            #     "Navigate+Fetch",
            #     self._try_download_from_url_with_option_02_navigate_then_fetch,
            # ),
            # # 0.2 MiB of PDF is not what we intend to download; it is just a screen caption of the first page
            # # with chrome browser
            # (
            #     "Page PDF",
            #     self._try_download_from_url_with_option_03_page_pdf,
            # ),
            # (
            #     "Network Intercept",
            #     self._try_download_from_url_with_option_04_network_interception,
            # ),
            # (
            #     "JS Extraction",
            #     self._try_download_from_url_with_option_05_js_extraction,
            # ),
            # (
            #     "Download Button",
            #     self._try_download_from_url_with_option_06_download_button,
            # ),
            # (
            #     "Keyboard Shortcut",
            #     self._try_download_from_url_with_option_07_keyboard_shortcut,
            # ),
            # (
            #     "CDP Fetch",
            #     self._try_download_from_url_with_option_08_cdp_fetch,
            # ),
            # # 0.29 MiB of PDF is not what we intend to download; it is just a screen caption of the first page
            # # with chrome browser
            # (
            #     "Screenshot OCR",
            #     self._try_download_from_url_with_option_09_screenshot_ocr,
            # ),
            # (
            #     "Manual Interaction",
            #     self._try_download_from_url_with_option_10_manual_interaction,
            # ),
            # (
            #     "Computer Vision",
            #     self._try_download_from_url_with_option_11_computer_vision,
            # ),
        ]

        for method_name, method_func in download_methods:
            logger.info(f"Trying method: {method_name}")
            result = await method_func(pdf_url, output_path)
            if result:
                logger.success(f"Successfully downloaded using: {method_name}")
                return result
            else:
                logger.warning(f"Method failed: {method_name}")

        logger.fail(f"All download methods failed for {pdf_url}")
        return None

    async def download_from_urls(
        self, pdf_urls: List[str], output_dir: Union[str, Path] = "/tmp/"
    ) -> List[Path]:
        """Download multiple PDFs."""
        output_paths = [
            Path(str(output_dir)) / os.path.basename(pdf_url)
            for pdf_url in pdf_urls
        ]

        saved_paths = []
        for ii_pdf, (url_pdf, output_path) in enumerate(
            zip(pdf_urls, output_paths), 1
        ):
            logger.info(f"Downloading PDF {ii_pdf}/{len(pdf_urls)}: {url_pdf}")
            saved_path = await self.download_from_url(url_pdf, output_path)
            if saved_path:
                saved_paths.append(saved_path)

        logger.info(
            f"Downloaded {len(saved_paths)}/{len(pdf_urls)} PDFs successfully"
        )
        return saved_paths

    async def download_from_doi(
        self, doi: str, output_dir: str = "/tmp/"
    ) -> List[Path]:
        """Download PDFs for a given DOI."""
        output_dir = Path(str(output_dir))
        urls = await self.url_finder.find_urls(doi=doi)
        pdf_urls = [url_pdf_entry["url"] for url_pdf_entry in urls["url_pdf"]]
        saved_paths = await self.download_from_urls(
            pdf_urls, output_dir=output_dir
        )
        return saved_paths

    async def _try_download_from_url_with_option_00_development(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        try:
            logger.info(f"[Option 0] Development: {pdf_url}")
            page = await self.context.new_page()

            # Intercept PDF requests
            pdf_request_url = None

            async def handle_request(request):
                nonlocal pdf_request_url
                if (
                    request.resource_type == "document"
                    and ".pdf" in request.url
                ):
                    pdf_request_url = request.url

            page.on("request", handle_request)

            response = await page.goto(
                pdf_url, wait_until="load", timeout=60000
            )
            await page.wait_for_timeout(5000)

            content = await response.body()

            if content[:4] == b"%PDF":
                with open(output_path, "wb") as file_:
                    file_.write(content)
                size_MiB = len(content) / 1024 / 1024
                logger.success(
                    f"[Option 0] Success: {output_path} ({size_MiB:.2f} MiB)"
                )
                await page.close()
                return output_path

            # Check for intercepted PDF URL
            if pdf_request_url and (pdf_request_url != pdf_url):
                logger.info(
                    f"Found PDF URL from network other than the original one: {pdf_request_url}"
                )
                pdf_response = await page.goto(pdf_request_url)
                pdf_content = await pdf_response.body()

                with open(output_path, "wb") as file_:
                    file_.write(pdf_content)
                size_MiB = len(pdf_content) / 1024 / 1024
                logger.success(
                    f"[Option 0] Success from network: {output_path} ({size_MiB:.2f} MiB)"
                )
                await page.close()
                return output_path

            # If HTML response, try PDF viewer detection
            await page.wait_for_load_state("networkidle")

            pdf_viewer_present = await page.evaluate(
                """
            () => {
                return !!(
                    document.querySelector('embed[type="application/pdf"]') ||
                    document.querySelector('iframe[src*=".pdf"]') ||
                    document.querySelector('object[type="application/pdf"]') ||
                    window.PDFViewerApplication ||
                    document.querySelector('[data-testid="pdf-viewer"]')
                );
            }
            """
            )

            if pdf_viewer_present:
                logger.info("PDF viewer detected")

                # Focus the PDF viewer element
                await page.evaluate(
                    """() => {
                    const embed = document.querySelector('embed[type="application/pdf"]');
                    if (embed) { embed.focus(); return; }

                    const iframe = document.querySelector('iframe[src*=".pdf"]');
                    if (iframe) { iframe.focus(); return; }

                    const obj = document.querySelector('object[type="application/pdf"]');
                    if (obj) { obj.focus(); return; }

                    const viewer = document.querySelector('[data-testid="pdf-viewer"]');
                    if (viewer) { viewer.focus(); return; }
                }"""
                )

                # # Grid
                # await page.evaluate(
                #     """() => {
                #     const canvas = document.createElement('canvas');
                #     canvas.style.position = 'fixed';
                #     canvas.style.top = '0';
                #     canvas.style.left = '0';
                #     canvas.style.width = '100%';
                #     canvas.style.height = '100%';
                #     canvas.style.pointerEvents = 'none';
                #     canvas.style.zIndex = '9999';
                #     canvas.width = window.innerWidth;
                #     canvas.height = window.innerHeight;

                #     const ctx = canvas.getContext('2d');
                #     ctx.strokeStyle = 'red';
                #     ctx.font = '12px Arial';

                #     for (let xx = 0; xx < canvas.width; xx += 100) {
                #         ctx.beginPath();
                #         ctx.moveTo(xx, 0);
                #         ctx.lineTo(xx, canvas.height);
                #         ctx.stroke();
                #         ctx.fillText(xx, xx + 5, 15);
                #     }

                #     for (let yy = 0; yy < canvas.height; yy += 100) {
                #         ctx.beginPath();
                #         ctx.moveTo(0, yy);
                #         ctx.lineTo(canvas.width, yy);
                #         ctx.stroke();
                #         ctx.fillText(yy, 5, yy + 15);
                #     }

                #     document.body.appendChild(canvas);
                # }"""
                # )

                # Grid with minor ticks

                await page.evaluate(
                    """() => {
                    const canvas = document.createElement('canvas');
                    canvas.style.position = 'fixed';
                    canvas.style.top = '0';
                    canvas.style.left = '0';
                    canvas.style.width = '100%';
                    canvas.style.height = '100%';
                    canvas.style.pointerEvents = 'none';
                    canvas.style.zIndex = '9999';
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;

                    const ctx = canvas.getContext('2d');
                    ctx.font = '12px Arial';

                    for (let xx = 0; xx < canvas.width; xx += 20) {
                        ctx.strokeStyle = xx % 100 === 0 ? 'red' : '#ffcccc';
                        ctx.lineWidth = xx % 100 === 0 ? 1 : 0.5;
                        ctx.beginPath();
                        ctx.moveTo(xx, 0);
                        ctx.lineTo(xx, canvas.height);
                        ctx.stroke();
                        if (xx % 100 === 0) {
                            ctx.fillStyle = 'red';
                            ctx.fillText(xx, xx + 5, 15);
                        }
                    }

                    for (let yy = 0; yy < canvas.height; yy += 20) {
                        ctx.strokeStyle = yy % 100 === 0 ? 'red' : '#ffcccc';
                        ctx.lineWidth = yy % 100 === 0 ? 1 : 0.5;
                        ctx.beginPath();
                        ctx.moveTo(0, yy);
                        ctx.lineTo(canvas.width, yy);
                        ctx.stroke();
                        if (yy % 100 === 0) {
                            ctx.fillStyle = 'red';
                            ctx.fillText(yy, 5, yy + 15);
                        }
                    }

                    document.body.appendChild(canvas);
                }"""
                )

                # Mouse Tracking
                await page.evaluate(
                    """() => {
                    const canvas = document.createElement('canvas');
                    canvas.style.position = 'fixed';
                    canvas.style.top = '0';
                    canvas.style.left = '0';
                    canvas.style.width = '100%';
                    canvas.style.height = '100%';
                    canvas.style.pointerEvents = 'none';
                    canvas.style.zIndex = '9999';
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;

                    const ctx = canvas.getContext('2d');
                    document.body.appendChild(canvas);

                    document.addEventListener('mousemove', (ee) => {
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.strokeStyle = 'black';
                        ctx.lineWidth = 1;

                        ctx.beginPath();
                        ctx.moveTo(ee.clientX, 0);
                        ctx.lineTo(ee.clientX, canvas.height);
                        ctx.stroke();

                        ctx.beginPath();
                        ctx.moveTo(0, ee.clientY);
                        ctx.lineTo(canvas.width, ee.clientY);
                        ctx.stroke();

                        ctx.fillStyle = 'black';
                        ctx.font = '14px Arial';
                        ctx.fillText(`${ee.clientX}, ${ee.clientY}`, ee.clientX + 10, ee.clientY - 10);
                    });
                }"""
                )

                viewport_size = page.viewport_size
                center_x = viewport_size["width"] // 2
                center_y = viewport_size["height"] // 2
                await page.mouse.click(center_x, center_y)

                await page.wait_for_timeout(1000)

                # ########################################
                # WORKING EXMAPLE
                # ########################################
                # Set up download handling
                async with page.expect_download() as download_info:
                    x_download_button = 1820
                    y_download_button = 30
                    await page.mouse.click(
                        x_download_button, y_download_button
                    )

                download = await download_info.value
                spath_pdf = f"/tmp/downloaded{int(time.time())}.pdf"
                await download.save_as(spath_pdf)
                # Verify file exists
                import os

                if os.path.exists(spath_pdf):
                    file_size = os.path.getsize(spath_pdf)
                    print(f"Downloaded: {spath_pdf} ({file_size} bytes)")
                else:
                    print("Download failed")

                logger.success(f"Downloaded: {spath_pdf}")
                # ########################################

                # # # This Works
                # for _ in range(10):
                #     x_download_button = 1820
                #     y_download_button = 30
                #     await page.mouse.click(
                #         x_download_button, y_download_button
                #     )
                #     time.sleep(1)

                # Click download buttons
                # Method 1: Multiple selector attempts
                selectors = [
                    '[title*="download" i]',
                    '[aria-label*="download" i]',
                    'button:has-text("download")',
                    '[data-tooltip*="download" i]',
                    ".download-btn, .btn-download",
                    'a:has-text("download")',
                    '[alt*="download" i]',
                ]

                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        box = await element.bounding_box()
                        if box:
                            await page.evaluate(
                                f"""() => {{
                                const div = document.createElement('div');
                                div.style.position = 'fixed';
                                div.style.left = '{box["x"]}px';
                                div.style.top = '{box["y"]}px';
                                div.style.width = '{box["width"]}px';
                                div.style.height = '{box["height"]}px';
                                div.style.border = '3px solid red';
                                div.style.backgroundColor = 'rgba(255,255,0,0.3)';
                                div.style.zIndex = '10000';
                                div.style.pointerEvents = 'none';
                                document.body.appendChild(div);
                            }}"""
                            )

                time.sleep(60)

                # Try extracting PDF URL from JavaScript
                pdf_url_from_js = await page.evaluate(
                    """
                () => {
                    // Check for PDFViewerApplication (common PDF.js viewer)
                    if (window.PDFViewerApplication && window.PDFViewerApplication.url) {
                        return window.PDFViewerApplication.url;
                    }

                    // Check data attributes
                    const viewer = document.querySelector('[data-pdf-url]');
                    if (viewer) return viewer.getAttribute('data-pdf-url');

                    // Check for blob URLs in iframes
                    const iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        if (iframe.src && (iframe.src.startsWith('blob:') || iframe.src.includes('.pdf'))) {
                            return iframe.src;
                        }
                    }

                    return null;
                }
                """
                )

                if pdf_url_from_js:
                    logger.info(f"Found PDF URL from JS: {pdf_url_from_js}")
                    try:
                        pdf_response = await page.goto(pdf_url_from_js)
                        pdf_content = await pdf_response.body()

                        if pdf_content[:4] == b"%PDF":
                            with open(output_path, "wb") as file_:
                                file_.write(pdf_content)
                            size_MiB = len(pdf_content) / 1024 / 1024
                            logger.success(
                                f"[Option 0] Success from JS URL: {output_path} ({size_MiB:.2f} MiB)"
                            )
                            await page.close()
                            return output_path
                    except:
                        pass

            logger.warning("No PDF content or viewer found")
            await page.close()
            return None

        except Exception as e:
            logger.error(f"[Option 0] Failed: {e}")
            return None

    async def _try_download_from_url_with_option_01_direct_request(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        try:
            logger.info(f"[Option 1] Direct request: {pdf_url}")

            # Extract base URL for referrer
            base_url = "/".join(pdf_url.split("/")[:-1]) + "/"

            response = await self.context.request.get(
                pdf_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/pdf,*/*",
                    "Referer": base_url,
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "no-cache",
                },
            )

            logger.info(f"[Option 1] Response status: {response.status}")

            if response.status == 403:
                logger.warning(f"[Option 1] 403 Forbidden - try other methods")
                return None

            if response.ok:
                content = await response.body()
                if len(content) > 4 and content[:4] == b"%PDF":
                    with open(output_path, "wb") as f:
                        f.write(content)
                    size_MiB = len(content) / 1024 / 1024
                    logger.success(
                        f"[Option 1] Success: {output_path} ({size_MiB:.2f} MiB)"
                    )
                    return output_path

        except Exception as e:
            logger.error(f"[Option 1] Failed: {e}")
        return None

    async def _try_download_from_url_with_option_02_navigate_then_fetch(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 2: Navigate to page first, then fetch with cookies.
        Handles redirects and sets any additional cookies needed.
        """
        page = None
        try:
            logger.info(f"[Option 2] Navigate + fetch: {pdf_url}")

            page = await self.context.new_page()

            # Navigate to ensure all cookies are set
            response = await page.goto(
                pdf_url, wait_until="load", timeout=60000
            )

            await page.wait_for_timeout(5000)

            # Get the final URL after redirects
            current_url = page.url
            logger.info(f"[Option 2] Current URL: {current_url}")

            # Fetch with properly authenticated context
            pdf_response = await self.context.request.get(current_url)

            if pdf_response.ok:
                content = await pdf_response.body()

                if len(content) > 4 and content[:4] == b"%PDF":
                    with open(output_path, "wb") as f:
                        f.write(content)

                    size_MiB = len(content) / 1024 / 1024
                    logger.success(
                        f"[Option 2] Success: {output_path} ({size_MiB:.2f} MiB)"
                    )
                    return output_path
                else:
                    logger.warning(
                        f"[Option 2] Not a PDF. First bytes: {content[:20]}"
                    )

        except Exception as e:
            logger.error(f"[Option 2] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    async def _try_download_from_url_with_option_03_page_pdf(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 3: Use page.pdf() to print the displayed PDF.
        Works when PDF is displayed but not downloadable.
        THIS IS THE METHOD THAT WORKS FOR SCIENCE.ORG!
        """
        page = None
        try:
            logger.info(f"[Option 3] page.pdf() method: {pdf_url}")

            page = await self.context.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})

            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            # Generate PDF from the page
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )

            if pdf_bytes and len(pdf_bytes) > 100:
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)

                size_MiB = len(pdf_bytes) / 1024 / 1024
                logger.success(
                    f"[Option 3] Success: {output_path} ({size_MiB:.2f} MiB)"
                )
                return output_path

        except Exception as e:
            logger.error(f"[Option 3] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    async def _try_download_from_url_with_option_04_network_interception(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 4: Intercept network response.
        Captures PDF as it's loaded by the browser.
        FIXED: Now properly saves the intercepted content!
        """
        page = None
        try:
            logger.info(f"[Option 4] Network interception: {pdf_url}")

            page = await self.context.new_page()
            pdf_content = None

            async def handle_response(response):
                nonlocal pdf_content
                try:
                    # Check if this is our PDF URL or any PDF response
                    if pdf_url in response.url or response.url.endswith(
                        ".pdf"
                    ):
                        content_type = response.headers.get("content-type", "")
                        if (
                            "pdf" in content_type.lower()
                            or response.url.endswith(".pdf")
                        ):
                            temp_content = await response.body()
                            # Verify it's actually a PDF
                            if (
                                len(temp_content) > 4
                                and temp_content[:4] == b"%PDF"
                            ):
                                pdf_content = temp_content
                                logger.info(
                                    f"[Option 4] Intercepted valid PDF from: {response.url} ({len(temp_content)} bytes)"
                                )
                            else:
                                logger.debug(
                                    f"[Option 4] Not a PDF response from: {response.url}"
                                )
                except Exception as e:
                    logger.debug(f"[Option 4] Error handling response: {e}")

            page.on("response", handle_response)

            # Navigate and wait for PDF to load
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)

            # Wait a bit longer for any async responses
            await page.wait_for_timeout(5000)

            # Check if we successfully intercepted the PDF
            if pdf_content:
                with open(output_path, "wb") as f:
                    f.write(pdf_content)

                size_MiB = len(pdf_content) / 1024 / 1024
                logger.success(
                    f"[Option 4] Success: {output_path} ({size_MiB:.2f} MiB)"
                )
                return output_path
            else:
                logger.warning("[Option 4] No PDF content intercepted")

        except Exception as e:
            logger.error(f"[Option 4] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    async def _try_download_from_url_with_option_05_js_extraction(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 5: Extract from embedded viewer using JavaScript.
        Works with iframe/embed/object elements.
        """
        page = None
        try:
            logger.info(f"[Option 5] JavaScript extraction: {pdf_url}")

            page = await self.context.new_page()
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            pdf_data_b64 = await page.evaluate(
                """
                async () => {
                    const embed = document.querySelector('embed[type="application/pdf"]');
                    const iframe = document.querySelector('iframe[src*=".pdf"]');
                    const object = document.querySelector('object[data*=".pdf"]');

                    let pdfUrl = null;

                    if (embed && embed.src) {
                        pdfUrl = embed.src;
                    } else if (iframe && iframe.src) {
                        pdfUrl = iframe.src;
                    } else if (object && object.data) {
                        pdfUrl = object.data;
                    } else if (window.location.href.endsWith('.pdf')) {
                        pdfUrl = window.location.href;
                    }

                    if (pdfUrl) {
                        try {
                            const response = await fetch(pdfUrl);
                            const blob = await response.blob();
                            const reader = new FileReader();
                            return new Promise((resolve) => {
                                reader.onloadend = () => resolve(reader.result);
                                reader.readAsDataURL(blob);
                            });
                        } catch (e) {
                            console.error('Failed to fetch PDF:', e);
                            return null;
                        }
                    }

                    return null;
                }
            """
            )

            if pdf_data_b64:
                if "," in pdf_data_b64:
                    pdf_data_b64 = pdf_data_b64.split(",")[1]

                pdf_data = base64.b64decode(pdf_data_b64)

                if len(pdf_data) > 4 and pdf_data[:4] == b"%PDF":
                    with open(output_path, "wb") as f:
                        f.write(pdf_data)

                    size_MiB = len(pdf_data) / 1024 / 1024
                    logger.success(
                        f"[Option 5] Success: {output_path} ({size_MiB:.2f} MiB)"
                    )
                    return output_path

        except Exception as e:
            logger.error(f"[Option 5] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    # async def _try_download_from_url_with_option_06_download_button(
    #     self, pdf_url: str, output_path: Path
    # ) -> Optional[Path]:
    #     """
    #     Option 6: Click download button if visible.
    #     Looks for common download button selectors.
    #     """
    #     page = None
    #     try:
    #         logger.info(f"[Option 6] Download button click: {pdf_url}")

    #         page = await self.context.new_page()
    #         await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
    #         await page.wait_for_timeout(3000)

    #         download_selectors = [
    #             'button[aria-label="Download"]',
    #             '[title="Download"]',
    #             "#download",
    #             'cr-icon-button[iron-icon="cr:file-download"]',
    #             'a[href$=".pdf"]',
    #             'button:has-text("Download")',
    #             '[aria-label*="download" i]',
    #             ".download-link",
    #         ]

    #         for selector in download_selectors:
    #             try:
    #                 element = page.locator(selector).first
    #                 if await element.is_visible(timeout=1000):
    #                     logger.info(f"[Option 6] Found button: {selector}")

    #                     async with page.expect_download(
    #                         timeout=30000
    #                     ) as download_info:
    #                         await element.click()

    #                     download = download_info.value
    #                     await download.save_as(output_path)

    #                     if output_path.exists():
    #                         size_MiB = output_path.stat().st_size / 1024 / 1024
    #                         logger.success(
    #                             f"[Option 6] Success: {output_path} ({size_MiB:.2f} MiB)"
    #                         )
    #                         return output_path
    #             except:
    #                 continue

    #     except Exception as e:
    #         logger.error(f"[Option 6] Failed: {e}")
    #     finally:
    #         if page:
    #             await page.close()

    #     return None

    async def _try_download_from_url_with_option_06_download_button(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 6: Click download button in Chrome PDF viewer.
        ENHANCED: Properly handles Chrome's PDF viewer shadow DOM and download.
        """
        page = None
        try:
            logger.info(f"[Option 6] Download button click: {pdf_url}")

            page = await self.context.new_page()

            # CRITICAL: Set up download handler BEFORE navigation
            download_promise = asyncio.create_task(
                self._wait_for_download_with_timeout(page, 30000)
            )

            # Navigate to PDF
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)

            # Wait for PDF viewer to load
            await page.wait_for_timeout(5000)

            # Chrome PDF viewer uses shadow DOM, we need to access it properly
            download_clicked = await page.evaluate(
                """
                async () => {
                    // Method 1: Try Chrome's PDF viewer (in shadow DOM)
                    const viewer = document.querySelector('pdf-viewer');
                    if (viewer && viewer.shadowRoot) {
                        // Navigate through shadow DOM
                        const toolbar = viewer.shadowRoot.querySelector('viewer-toolbar');
                        if (toolbar && toolbar.shadowRoot) {
                            const downloadButton = toolbar.shadowRoot.querySelector('#download');
                            if (downloadButton) {
                                downloadButton.click();
                                console.log('Clicked Chrome PDF viewer download button');
                                return true;
                            }
                        }
                    }

                    // Method 2: Try older Chrome PDF viewer structure
                    const embedElement = document.querySelector('embed[type="application/pdf"]');
                    if (embedElement) {
                        // Try to access the plugin's download functionality
                        try {
                            // Send Ctrl+S to the embed element
                            embedElement.focus();
                            const event = new KeyboardEvent('keydown', {
                                key: 's',
                                code: 'KeyS',
                                ctrlKey: true,
                                bubbles: true
                            });
                            embedElement.dispatchEvent(event);
                            console.log('Sent Ctrl+S to embed element');
                            return true;
                        } catch (e) {
                            console.error('Could not send keys to embed:', e);
                        }
                    }

                    // Method 3: Try any visible download button
                    const downloadButtons = [
                        ...document.querySelectorAll('button[aria-label*="download" i]'),
                        ...document.querySelectorAll('button[title*="download" i]'),
                        ...document.querySelectorAll('#download'),
                        ...document.querySelectorAll('[data-testid*="download" i]'),
                        ...document.querySelectorAll('button:has(svg[class*="download" i])')
                    ];

                    for (const button of downloadButtons) {
                        if (button.offsetParent !== null) {  // Check if visible
                            button.click();
                            console.log('Clicked download button:', button);
                            return true;
                        }
                    }

                    return false;
                }
            """
            )

            if download_clicked:
                logger.info("[Option 6] Download button clicked successfully")

                try:
                    # Wait for download to complete
                    download = await download_promise
                    if download:
                        await download.save_as(output_path)

                        if output_path.exists():
                            size_MiB = output_path.stat().st_size / 1024 / 1024
                            logger.success(
                                f"[Option 6] Success: {output_path} ({size_MiB:.2f} MiB)"
                            )
                            return output_path
                except asyncio.TimeoutError:
                    logger.warning(
                        "[Option 6] Download did not trigger after button click"
                    )

            # Fallback: Try keyboard shortcut with proper focus
            logger.info("[Option 6] Trying keyboard shortcut as fallback")

            # Focus the PDF area
            await page.evaluate(
                """
                () => {
                    const pdfArea = document.querySelector('embed, iframe, object, pdf-viewer') || document.body;
                    pdfArea.focus();
                }
            """
            )

            # Set up new download handler
            download_promise = asyncio.create_task(
                self._wait_for_download_with_timeout(page, 10000)
            )

            # Try Ctrl+S
            await page.keyboard.press("Control+s")

            try:
                download = await download_promise
                if download:
                    await download.save_as(output_path)

                    if output_path.exists():
                        size_MiB = output_path.stat().st_size / 1024 / 1024
                        logger.success(
                            f"[Option 6] Success via Ctrl+S: {output_path} ({size_MiB:.2f} MiB)"
                        )
                        return output_path
            except asyncio.TimeoutError:
                logger.warning("[Option 6] Ctrl+S did not trigger download")

        except Exception as e:
            logger.error(f"[Option 6] Failed: {e}")

        return None

    async def _try_download_from_url_with_option_07_keyboard_shortcut(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 7: Use Ctrl+S keyboard shortcut.
        Triggers browser's save dialog.
        """
        page = None
        try:
            logger.info(f"[Option 7] Keyboard shortcut (Ctrl+S): {pdf_url}")

            page = await self.context.new_page()

            # Navigate first, then set up download expectation
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            try:
                async with page.expect_download(
                    timeout=10000
                ) as download_info:
                    # Try Ctrl+S to trigger download
                    await page.keyboard.press("Control+s")

                download = download_info.value
                await download.save_as(output_path)

                if output_path.exists():
                    size_MiB = output_path.stat().st_size / 1024 / 1024
                    logger.success(
                        f"[Option 7] Success: {output_path} ({size_MiB:.2f} MiB)"
                    )
                    return output_path
            except:
                logger.debug(
                    "[Option 7] Ctrl+S did not trigger download dialog"
                )

        except Exception as e:
            logger.error(f"[Option 7] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    # async def _try_download_from_url_with_option_08_cdp_fetch(
    #     self, pdf_url: str, output_path: Path
    # ) -> Optional[Path]:
    #     """
    #     Option 8: Use Chrome DevTools Protocol to fetch the PDF.
    #     This bypasses restrictions by using browser's internal fetch.
    #     """
    #     page = None
    #     try:
    #         logger.info(f"[Option 8] CDP fetch method: {pdf_url}")

    #         page = await self.context.new_page()

    #         # Get CDP session
    #         client = await page.context.new_cdp_session(page)

    #         # Enable network domain
    #         await client.send("Network.enable")

    #         # Navigate to the PDF to establish session/cookies
    #         await page.goto(pdf_url, wait_until="load", timeout=60000)
    #         await page.wait_for_timeout(3000)

    #         # Use CDP to fetch the PDF with all cookies/auth
    #         try:
    #             # Get cookies for the domain
    #             cookies = await client.send(
    #                 "Network.getCookies", {"urls": [pdf_url]}
    #             )

    #             # Fetch the resource using CDP
    #             response = await client.send(
    #                 "Network.getResponseBody",
    #                 {
    #                     "requestId": await self._get_request_id_for_url(
    #                         client, pdf_url
    #                     )
    #                 },
    #             )

    #             if response.get("base64Encoded"):
    #                 import base64

    #                 pdf_content = base64.b64decode(response["body"])
    #             else:
    #                 pdf_content = response["body"].encode()

    #             if len(pdf_content) > 4 and pdf_content[:4] == b"%PDF":
    #                 with open(output_path, "wb") as f:
    #                     f.write(pdf_content)

    #                 size_MiB = len(pdf_content) / 1024 / 1024
    #                 logger.success(
    #                     f"[Option 8] Success via CDP: {output_path} ({size_MiB:.2f} MiB)"
    #                 )
    #                 return output_path

    #         except Exception as cdp_error:
    #             logger.debug(f"[Option 8] CDP fetch failed: {cdp_error}")

    #             # Fallback: Use Page.printToPDF which works differently than page.pdf()
    #             try:
    #                 pdf_result = await client.send(
    #                     "Page.printToPDF",
    #                     {
    #                         "printBackground": True,
    #                         "landscape": False,
    #                         "paperWidth": 8.27,  # A4 width in inches
    #                         "paperHeight": 11.69,  # A4 height in inches
    #                         "marginTop": 0,
    #                         "marginBottom": 0,
    #                         "marginLeft": 0,
    #                         "marginRight": 0,
    #                         "preferCSSPageSize": True,
    #                     },
    #                 )

    #                 if pdf_result.get("data"):
    #                     import base64

    #                     pdf_content = base64.b64decode(pdf_result["data"])

    #                     with open(output_path, "wb") as f:
    #                         f.write(pdf_content)

    #                     size_MiB = len(pdf_content) / 1024 / 1024
    #                     logger.success(
    #                         f"[Option 8] Success via CDP printToPDF: {output_path} ({size_MiB:.2f} MiB)"
    #                     )
    #                     return output_path

    #             except Exception as print_error:
    #                 logger.debug(
    #                     f"[Option 8] CDP printToPDF failed: {print_error}"
    #                 )

    #     except Exception as e:
    #         logger.error(f"[Option 8] Failed: {e}")
    #     finally:
    #         if page:
    #             await page.close()

    #     return None
    async def _try_download_from_url_with_option_08_cdp_fetch(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 8: Use Chrome DevTools Protocol to fetch the PDF.
        ENHANCED: Ensures full PDF is loaded before capture.
        """
        page = None
        try:
            logger.info(f"[Option 8] CDP fetch method: {pdf_url}")

            page = await self.context.new_page()

            # Get CDP session
            client = await page.context.new_cdp_session(page)

            # Enable necessary domains
            await client.send("Network.enable")
            await client.send("Page.enable")

            # Navigate to the PDF
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)

            # CRITICAL: Wait for PDF.js to fully load all pages
            logger.info("[Option 8] Waiting for full PDF to load...")

            # Method 1: Wait for PDF viewer to be fully initialized
            await page.wait_for_timeout(5000)

            # Method 2: Check if PDF.js is loaded and get page count
            pdf_info = await page.evaluate(
                """
                async () => {
                    // Wait for PDFViewerApplication to be available (PDF.js)
                    if (typeof PDFViewerApplication !== 'undefined') {
                        // Wait for PDF to be fully loaded
                        let attempts = 0;
                        while (attempts < 30) {
                            if (PDFViewerApplication.pdfDocument &&
                                PDFViewerApplication.pdfDocument.numPages) {
                                // Get number of pages
                                const numPages = PDFViewerApplication.pdfDocument.numPages;

                                // Scroll through all pages to ensure they're rendered
                                const container = document.getElementById('viewerContainer');
                                if (container) {
                                    // Scroll to bottom
                                    container.scrollTop = container.scrollHeight;
                                    await new Promise(r => setTimeout(r, 2000));
                                    // Scroll to top
                                    container.scrollTop = 0;
                                    await new Promise(r => setTimeout(r, 1000));
                                }

                                return {
                                    loaded: true,
                                    numPages: numPages,
                                    title: PDFViewerApplication.pdfDocument.title || 'PDF Document'
                                };
                            }
                            await new Promise(r => setTimeout(r, 500));
                            attempts++;
                        }
                    }

                    // Fallback for Chrome's native PDF viewer
                    const embed = document.querySelector('embed[type="application/pdf"]');
                    if (embed) {
                        // For Chrome's viewer, we need to wait longer
                        await new Promise(r => setTimeout(r, 5000));

                        // Try to scroll in the embed
                        try {
                            const plugin = embed.contentDocument || embed.contentWindow?.document;
                            if (plugin) {
                                plugin.documentElement.scrollTop = plugin.documentElement.scrollHeight;
                                await new Promise(r => setTimeout(r, 2000));
                                plugin.documentElement.scrollTop = 0;
                            }
                        } catch (e) {
                            // Cross-origin restrictions may prevent this
                        }

                        return {loaded: true, viewer: 'chrome'};
                    }

                    return {loaded: false};
                }
            """
            )

            if pdf_info.get("loaded"):
                logger.info(
                    f"[Option 8] PDF loaded: {pdf_info.get('numPages', 'unknown')} pages"
                )

            # Additional wait to ensure rendering is complete
            await page.wait_for_timeout(3000)

            # Now try to get the PDF content
            try:
                # First attempt: Try to intercept the actual PDF response
                pdf_content = None

                async def handle_response(response):
                    nonlocal pdf_content
                    if response.url == pdf_url or response.url.endswith(
                        ".pdf"
                    ):
                        try:
                            content = await response.body()
                            if len(content) > 4 and content[:4] == b"%PDF":
                                pdf_content = content
                        except:
                            pass

                page.on("response", handle_response)

                # Reload to capture the response
                await page.reload(wait_until="networkidle")
                await page.wait_for_timeout(3000)

                if pdf_content:
                    with open(output_path, "wb") as f:
                        f.write(pdf_content)

                    size_MiB = len(pdf_content) / 1024 / 1024
                    logger.success(
                        f"[Option 8] Success via response intercept: {output_path} ({size_MiB:.2f} MiB)"
                    )
                    return output_path
            except:
                pass

            # Fallback: Use Page.printToPDF with better settings
            try:
                # Get page metrics first
                metrics = await client.send("Page.getLayoutMetrics")
                content_width = metrics["contentSize"]["width"]
                content_height = metrics["contentSize"]["height"]

                # Calculate paper size to fit content
                paper_width = max(
                    8.27, content_width / 96
                )  # Convert pixels to inches
                paper_height = max(11.69, content_height / 96)

                pdf_result = await client.send(
                    "Page.printToPDF",
                    {
                        "printBackground": True,
                        "landscape": False,
                        "paperWidth": paper_width,
                        "paperHeight": paper_height,
                        "marginTop": 0,
                        "marginBottom": 0,
                        "marginLeft": 0,
                        "marginRight": 0,
                        "scale": 1,
                        "displayHeaderFooter": False,
                        "preferCSSPageSize": True,
                    },
                )

                if pdf_result.get("data"):
                    import base64

                    pdf_content = base64.b64decode(pdf_result["data"])

                    with open(output_path, "wb") as f:
                        f.write(pdf_content)

                    size_MiB = len(pdf_content) / 1024 / 1024

                    # Check if size seems reasonable
                    if size_MiB < 0.5:
                        logger.warning(
                            f"[Option 8] PDF may be incomplete: {size_MiB:.2f} MiB"
                        )

                        # Try once more with longer wait
                        await page.wait_for_timeout(10000)

                        pdf_result_retry = await client.send(
                            "Page.printToPDF",
                            {
                                "printBackground": True,
                                "landscape": False,
                                "paperWidth": 11,  # Larger paper size
                                "paperHeight": 17,
                                "marginTop": 0,
                                "marginBottom": 0,
                                "marginLeft": 0,
                                "marginRight": 0,
                                "scale": 1,
                                "displayHeaderFooter": False,
                            },
                        )

                        if pdf_result_retry.get("data"):
                            pdf_content_retry = base64.b64decode(
                                pdf_result_retry["data"]
                            )
                            if len(pdf_content_retry) > len(pdf_content):
                                pdf_content = pdf_content_retry
                                with open(output_path, "wb") as f:
                                    f.write(pdf_content)
                                size_MiB = len(pdf_content) / 1024 / 1024

                    logger.success(
                        f"[Option 8] Success via CDP printToPDF: {output_path} ({size_MiB:.2f} MiB)"
                    )
                    return output_path

            except Exception as print_error:
                logger.error(
                    f"[Option 8] CDP printToPDF failed: {print_error}"
                )

        except Exception as e:
            logger.error(f"[Option 8] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    async def _try_download_from_url_with_option_09_screenshot_ocr(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 9: Last resort - Screenshot each page and combine into PDF.
        This is slow but works when all else fails.
        """
        page = None
        try:
            logger.info(f"[Option 9] Screenshot + combine method: {pdf_url}")

            page = await self.context.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})

            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            # Check if we can detect the number of pages
            num_pages = await page.evaluate(
                """
                () => {
                    if (typeof PDFViewerApplication !== 'undefined' &&
                        PDFViewerApplication.pdfDocument) {
                        return PDFViewerApplication.pdfDocument.numPages;
                    }
                    // Try to find page indicators
                    const pageInfo = document.querySelector('.page-info, #pageNumber, [data-page-number]');
                    if (pageInfo && pageInfo.textContent) {
                        const match = pageInfo.textContent.match(/of (\d+)/);
                        if (match) return parseInt(match[1]);
                    }
                    return 1;  // Default to 1 if we can't detect
                }
            """
            )

            logger.info(f"[Option 9] Detected {num_pages} pages")

            screenshots = []

            # Take screenshot of each page
            for page_num in range(1, num_pages + 1):
                # Navigate to specific page
                await page.evaluate(
                    f"""
                    () => {{
                        if (typeof PDFViewerApplication !== 'undefined') {{
                            PDFViewerApplication.page = {page_num};
                        }}
                    }}
                """
                )

                await page.wait_for_timeout(2000)

                # Take screenshot
                screenshot = await page.screenshot(full_page=True)
                screenshots.append(screenshot)

                logger.debug(
                    f"[Option 9] Captured page {page_num}/{num_pages}"
                )

            if screenshots:
                # Convert screenshots to PDF using PIL/Pillow
                try:
                    import io

                    from PIL import Image

                    images = []
                    for screenshot in screenshots:
                        img = Image.open(io.BytesIO(screenshot))
                        # Convert to RGB if necessary
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        images.append(img)

                    # Save as PDF
                    if images:
                        images[0].save(
                            output_path,
                            save_all=True,
                            append_images=(
                                images[1:] if len(images) > 1 else []
                            ),
                            format="PDF",
                        )

                        size_MiB = output_path.stat().st_size / 1024 / 1024
                        logger.success(
                            f"[Option 9] Success via screenshots: {output_path} ({size_MiB:.2f} MiB)"
                        )
                        return output_path

                except ImportError:
                    logger.error(
                        "[Option 9] PIL/Pillow not installed - cannot combine screenshots"
                    )
                    # Save first page screenshot as fallback
                    with open(output_path.with_suffix(".png"), "wb") as f:
                        f.write(screenshots[0])
                    logger.warning(
                        f"[Option 9] Saved first page as PNG: {output_path.with_suffix('.png')}"
                    )

        except Exception as e:
            logger.error(f"[Option 9] Failed: {e}")
        finally:
            if page:
                await page.close()

    async def _wait_for_download_with_timeout(self, page, timeout_ms: int):
        """Helper to wait for download with timeout."""
        try:
            async with page.expect_download(
                timeout=timeout_ms
            ) as download_info:
                pass  # Just wait for the download event
            return download_info.value
        except:
            return None

    async def _try_download_from_url_with_option_10_manual_interaction(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 10: Manual interaction mode - opens browser and waits for user to download.
        Ultimate fallback when automation fails.
        """
        page = None
        try:
            logger.info(f"[Option 10] Manual download mode: {pdf_url}")
            logger.info(
                "Please manually click the download button in the browser window..."
            )

            # Use headed mode for manual interaction
            page = await self.context.new_page()

            # Set up download handler
            download_received = asyncio.Event()
            download_file = None

            async def handle_download(download):
                nonlocal download_file
                download_file = download
                download_received.set()

            page.on("download", handle_download)

            # Navigate to PDF
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)

            # Show instructions to user
            await page.evaluate(
                """
                () => {
                    const div = document.createElement('div');
                    div.innerHTML = `
                        <div style="
                            position: fixed;
                            top: 10px;
                            right: 10px;
                            background: yellow;
                            border: 2px solid red;
                            padding: 10px;
                            z-index: 999999;
                            font-family: Arial;
                            font-size: 14px;
                            color: black;
                        ">
                            📥 Please click the DOWNLOAD button in the PDF viewer toolbar<br>
                            (or press Ctrl+S to save the PDF)
                        </div>
                    `;
                    document.body.appendChild(div);
                }
            """
            )

            # Wait for user to trigger download (max 60 seconds)
            try:
                await asyncio.wait_for(download_received.wait(), timeout=60)

                if download_file:
                    await download_file.save_as(output_path)

                    if output_path.exists():
                        size_MiB = output_path.stat().st_size / 1024 / 1024
                        logger.success(
                            f"[Option 10] Manual download success: {output_path} ({size_MiB:.2f} MiB)"
                        )
                        return output_path
            except asyncio.TimeoutError:
                logger.warning(
                    "[Option 10] No download detected within 60 seconds"
                )

        except Exception as e:
            logger.error(f"[Option 10] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None

    async def _get_request_id_for_url(self, client, url: str) -> str:
        """Helper to get request ID for a specific URL from CDP."""
        # This is a simplified version - in production you'd track requests
        requests = {}

        def handle_request(params):
            requests[params["request"]["url"]] = params["requestId"]

        client.on("Network.requestWillBeSent", handle_request)

        # Wait a bit to collect requests
        await asyncio.sleep(2)

        if url in requests:
            return requests[url]

        raise Exception(f"Request ID not found for URL: {url}")

    # Integration with your PDF downloader
    async def _try_download_from_url_with_option_11_computer_vision(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """
        Option 11: Use computer vision to find and click download button.
        Works when DOM inspection fails due to shadow DOM or canvas rendering.
        """
        page = None
        try:
            logger.info(f"[Option 11] Computer vision download: {pdf_url}")

            page = await self.context.new_page()

            # Set up download handler
            download_promise = asyncio.create_task(
                self._wait_for_download_with_timeout(page, 30000)
            )

            # Navigate to PDF
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            # Initialize vision system
            vision = PlaywrightVision(page)

            # Try to find and click download button
            success = await vision.find_download_button_and_click()

            if not success:
                # Try looking for specific text
                logger.info("[Option 11] Trying to find 'Download' text...")
                success = await vision.find_text_and_click(
                    "Download", timeout=5000
                )

            if not success:
                # Try looking for save icon
                logger.info(
                    "[Option 11] Trying to find save/download icons..."
                )
                # You could provide actual icon images here
                # success = await vision.find_and_click_image("./download_icon.png")

            if success:
                try:
                    download = await download_promise
                    if download:
                        await download.save_as(output_path)

                        if output_path.exists():
                            size_MiB = output_path.stat().st_size / 1024 / 1024
                            logger.success(
                                f"[Option 11] Success via computer vision: {output_path} ({size_MiB:.2f} MiB)"
                            )
                            return output_path
                except asyncio.TimeoutError:
                    logger.warning(
                        "[Option 11] Download did not complete after visual click"
                    )

        except Exception as e:
            logger.error(f"[Option 11] Failed: {e}")
        finally:
            if page:
                await page.close()

        return None


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )

        browser_manager = ScholarBrowserManager(
            chrome_profile_name="system",
            browser_mode="interactive",
            # browser_mode="stealth",
            auth_manager=ScholarAuthManager(),
            use_zenrows_proxy=False,
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        pdf_downloader = ScholarPDFDownloader(context)

        # Parameters
        PDF_URL = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"  # Option 1 Response not OK: 403
        # PDF_URL = "https://www.cambridgeenglish.org/Images/269898-ielts-academic-faqs.pdf"  # Option 1 successed
        OUTPUT_PATH = "/tmp/hippocampal_ripples.pdf"

        # Main
        saved_path = await pdf_downloader.download_from_url(
            PDF_URL,
            output_path=OUTPUT_PATH,
        )

        if saved_path:
            logger.success(f"PDF downloaded successfully to: {saved_path}")
        else:
            logger.error("Failed to download PDF")

    asyncio.run(main_async())

# python -m scitex.scholar.download.ScholarPDFDownloader

# EOF
