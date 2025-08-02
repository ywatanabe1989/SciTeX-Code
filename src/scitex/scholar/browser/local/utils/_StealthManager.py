#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 12:38:21 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/utils/_StealthManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_StealthManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import random

from playwright.async_api import Browser, BrowserContext, Page

from scitex import logging

logger = logging.getLogger(__name__)


class StealthManager:
    def __init__(
        self,
        viewport_size: tuple = None,
        spoof_dimension: bool = False,
        window_position: tuple = None,
    ):
        self.viewport_size = viewport_size
        self.spoof_dimension = spoof_dimension
        self.window_position = window_position

    def get_random_user_agent(self) -> str:
        user_agent = random.choice(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            ]
        )
        logger.info(f"User Agent randomly selected: {user_agent}")
        return user_agent

    def get_random_viewport(self) -> dict:
        if self.viewport_size:
            viewport = {
                "width": self.viewport_size[0],
                "height": self.viewport_size[1],
            }
            logger.info(
                f"Viewport defined as specified in Stealth Manager initiation: {viewport}"
            )
            return viewport

        if self.spoof_dimension:
            viewport = {"width": 1, "height": 1}
            logger.info(
                f"Viewport defined as spoof_dimension passed during Stealth Manager initiation: {viewport}"
            )
            return

        else:
            viewport = random.choice(
                [
                    {"width": 1920, "height": 1080},
                    {"width": 1366, "height": 768},
                    {"width": 1440, "height": 900},
                    {"width": 1280, "height": 720},
                ]
            )
            logger.info(f"Viewport randomly selected: {viewport}")
            return viewport

    def get_stealth_options(self) -> dict:
        return {
            "viewport": self.get_random_viewport(),
            "user_agent": self.get_random_user_agent(),
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com/",
            },
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }

    def get_stealth_options_additional(self) -> list:
        stealth_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate",
            "--disable-default-apps",
            "--enable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-field-trial-config",
            "--disable-client-side-phishing-detection",
            "--disable-component-update",
            "--disable-plugins-discovery",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-domain-reliability",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
        ]
        # Apply window size and position based on mode
        if self.spoof_dimension:
            # 1x1 window for complete invisibility
            stealth_args.extend(["--window-size=1,1", "--window-position=0,0"])
            logger.info("🎭 Invisible mode: Window set to 1x1 at position 0,0")
        else:
            # Standard window or custom size
            if self.viewport_size:
                stealth_args.append(
                    f"--window-size={self.viewport_size[0]},{self.viewport_size[1]}"
                )
            else:
                stealth_args.append("--window-size=1920,1080")

            # Apply custom window position if specified
            if self.window_position:
                stealth_args.append(
                    f"--window-position={self.window_position[0]},{self.window_position[1]}"
                )
                logger.info(
                    f"📐 Window positioned at: {self.window_position[0]},{self.window_position[1]}"
                )

        logger.info(
            f"🖥️ Browser window configuration: {'Invisible (1x1)' if self.spoof_dimension else f'{self.viewport_size[0]}x{self.viewport_size[1]}'}"
        )
        return stealth_args

        return {
            "viewport": self.get_random_viewport(),
            "user_agent": self.get_random_user_agent(),
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com/",
            },
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }

    def get_init_script(self) -> str:
        return """
// Remove webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

// Set realistic languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Mock chrome object
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// Mock plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {
            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        },
        {
            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
            description: "Portable Document Format",
            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            length: 1,
            name: "Chrome PDF Viewer"
        }
    ],
});

// Set hardware concurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8,
});

// Mock permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// Mock WebGL vendor
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter(parameter);
};

// Hide automation indicators
['webdriver', '__driver_evaluate', '__webdriver_evaluate', '__selenium_evaluate',
 '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
 '__selenium_unwrapped', '__fxdriver_unwrapped', '__webdriver_script_function',
 '__webdriver_script_func', '__webdriver_script_fn', '__fxdriver_script_fn',
 '__selenium_script_fn', '__webdriver_func', '__webdriver_fn'].forEach(prop => {
    delete window[prop];
    delete document[prop];
});

// Fix toString issues
window.navigator.chrome = {
    runtime: {},
};

// Override the `languages` property
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// Fix Notification permission
Object.defineProperty(navigator, 'permissions', {
    get: () => {
        return {
            query: async (permissionDesc) => {
                if (permissionDesc.name === 'notifications') {
                    return Promise.resolve({ state: 'granted' });
                }
                return Promise.resolve({ state: 'prompt' });
            }
        };
    }
});
"""

    def get_dimension_spoofing_script(self) -> str:
        """
        Generate comprehensive JavaScript dimension spoofing script for invisible browser mode.

        This creates a dual-layer window configuration:
        - Physical window: 1x1 pixel (invisible to user)
        - Reported dimensions: 1920x1080 (natural desktop size for bot detection)

        The script is bulletproof and handles all dimension-related APIs that
        bot detectors commonly check.
        """
        logger.info("stealth_manager.get_dimension_spoofing_script called.")
        if not self.spoof_dimension:
            return ""

        return """
            (() => {
                // Target dimensions to report to JavaScript (natural desktop)
                const TARGET_WINDOW_WIDTH = 1920;
                const TARGET_WINDOW_HEIGHT = 1080;
                const TARGET_SCREEN_WIDTH = 1920;
                const TARGET_SCREEN_HEIGHT = 1080;
                const TARGET_AVAILABLE_WIDTH = 1920;
                const TARGET_AVAILABLE_HEIGHT = 1040; // Account for taskbar

                console.log('🎭 [Dimension Spoofing] Initializing comprehensive window spoofing...');

                // === WINDOW DIMENSIONS ===
                // Override all window size properties
                Object.defineProperty(window, 'innerWidth', {
                    get: () => TARGET_WINDOW_WIDTH,
                    configurable: true
                });

                Object.defineProperty(window, 'innerHeight', {
                    get: () => TARGET_WINDOW_HEIGHT,
                    configurable: true
                });

                Object.defineProperty(window, 'outerWidth', {
                    get: () => TARGET_WINDOW_WIDTH,
                    configurable: true
                });

                Object.defineProperty(window, 'outerHeight', {
                    get: () => TARGET_WINDOW_HEIGHT + 100, // Account for browser chrome
                    configurable: true
                });

                // Override client dimensions (commonly checked by bot detectors)
                if (document.documentElement) {
                    Object.defineProperty(document.documentElement, 'clientWidth', {
                        get: () => TARGET_WINDOW_WIDTH,
                        configurable: true
                    });

                    Object.defineProperty(document.documentElement, 'clientHeight', {
                        get: () => TARGET_WINDOW_HEIGHT,
                        configurable: true
                    });
                }

                // === SCREEN DIMENSIONS ===
                // Override all screen properties
                Object.defineProperty(window.screen, 'width', {
                    get: () => TARGET_SCREEN_WIDTH,
                    configurable: true
                });

                Object.defineProperty(window.screen, 'height', {
                    get: () => TARGET_SCREEN_HEIGHT,
                    configurable: true
                });

                Object.defineProperty(window.screen, 'availWidth', {
                    get: () => TARGET_AVAILABLE_WIDTH,
                    configurable: true
                });

                Object.defineProperty(window.screen, 'availHeight', {
                    get: () => TARGET_AVAILABLE_HEIGHT,
                    configurable: true
                });

                // === VIEWPORT AND VISUAL DIMENSIONS ===
                // Override visual viewport (modern API)
                if (window.visualViewport) {
                    Object.defineProperty(window.visualViewport, 'width', {
                        get: () => TARGET_WINDOW_WIDTH,
                        configurable: true
                    });

                    Object.defineProperty(window.visualViewport, 'height', {
                        get: () => TARGET_WINDOW_HEIGHT,
                        configurable: true
                    });
                }

                // === DOCUMENT DIMENSIONS ===
                // Override document element dimensions (wait for DOM to be ready)
                const overrideDocumentDimensions = () => {
                    if (document.documentElement) {
                        Object.defineProperty(document.documentElement, 'clientWidth', {
                            get: () => TARGET_WINDOW_WIDTH,
                            configurable: true
                        });

                        Object.defineProperty(document.documentElement, 'clientHeight', {
                            get: () => TARGET_WINDOW_HEIGHT,
                            configurable: true
                        });

                        Object.defineProperty(document.documentElement, 'offsetWidth', {
                            get: () => TARGET_WINDOW_WIDTH,
                            configurable: true
                        });

                        Object.defineProperty(document.documentElement, 'offsetHeight', {
                            get: () => TARGET_WINDOW_HEIGHT,
                            configurable: true
                        });

                        Object.defineProperty(document.documentElement, 'scrollWidth', {
                            get: () => TARGET_WINDOW_WIDTH,
                            configurable: true
                        });

                        Object.defineProperty(document.documentElement, 'scrollHeight', {
                            get: () => TARGET_WINDOW_HEIGHT,
                            configurable: true
                        });
                    }

                    if (document.body) {
                        Object.defineProperty(document.body, 'clientWidth', {
                            get: () => TARGET_WINDOW_WIDTH,
                            configurable: true
                        });

                        Object.defineProperty(document.body, 'clientHeight', {
                            get: () => TARGET_WINDOW_HEIGHT,
                            configurable: true
                        });
                    }
                };

                // Apply immediately if DOM is ready, otherwise wait
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', overrideDocumentDimensions);
                } else {
                    overrideDocumentDimensions();
                }

                // === MEDIA QUERIES ===
                // Override matchMedia for responsive design queries
                const originalMatchMedia = window.matchMedia;
                window.matchMedia = function(query) {
                    const result = originalMatchMedia.call(this, query);

                    // Override common responsive breakpoints based on our spoofed dimensions
                    if (query.includes('max-width')) {
                        const maxWidth = parseInt(query.match(/max-width:\\s*(\d+)px/)?.[1] || '0');
                        if (maxWidth < TARGET_WINDOW_WIDTH) {
                            Object.defineProperty(result, 'matches', { get: () => false });
                        }
                    }

                    if (query.includes('min-width')) {
                        const minWidth = parseInt(query.match(/min-width:\\s*(\d+)px/)?.[1] || '0');
                        if (minWidth <= TARGET_WINDOW_WIDTH) {
                            Object.defineProperty(result, 'matches', { get: () => true });
                        }
                    }

                    return result;
                };

                // === EVENT HANDLING ===
                // Override resize events to maintain consistency
                const originalAddEventListener = window.addEventListener;
                window.addEventListener = function(type, listener, options) {
                    if (type === 'resize') {
                        // Intercept resize events and provide spoofed dimensions
                        const wrappedListener = function(event) {
                            // Create a mock resize event with spoofed dimensions
                            const mockEvent = new Event('resize');
                            Object.defineProperty(mockEvent, 'target', {
                                value: {
                                    innerWidth: TARGET_WINDOW_WIDTH,
                                    innerHeight: TARGET_WINDOW_HEIGHT
                                }
                            });
                            return listener.call(this, mockEvent);
                        };
                        return originalAddEventListener.call(this, type, wrappedListener, options);
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };

                console.log('🎭 [Dimension Spoofing] Complete! Physical: 1x1px, Reported: 1920x1080px');
                console.log('🤖 [Bot Detection] Window dimensions appear natural to detection systems');
            })();
        """

    async def human_delay(self, min_ms: int = 1000, max_ms: int = 3000):
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)

    async def human_click(self, page: Page, element):
        await element.hover()
        await self.human_delay(200, 500)
        await element.click()

    async def human_mouse_move(self, page: Page):
        await page.mouse.move(
            random.randint(100, 800), random.randint(100, 600)
        )

    async def human_scroll(self, page: Page):
        scroll_distance = random.randint(300, 800)
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await self.human_delay(500, 1500)

    async def human_type(self, page: Page, selector: str, text: str):
        element = page.locator(selector)
        await element.click()
        for char in text:
            await element.type(char)
            await self.human_delay(50, 200)


if __name__ == "__main__":
    import asyncio

    from playwright.async_api import async_playwright

    async def main():
        """Example usage of StealthManager for bot detection evasion."""
        stealth_manager = StealthManager()

        async with async_playwright() as p:
            # Launch browser with stealth options
            browser = await p.chromium.launch(
                headless=False,  # Use visible mode to see the effect
                **stealth_manager.get_stealth_options(),
            )

            # Create context with stealth options
            context = await browser.new_context(
                **stealth_manager.get_stealth_options()
            )

            # Inject stealth scripts
            await context.add_init_script(stealth_manager.get_init_script())

            # Create a new page
            page = await context.new_page()

            # Test 1: Bot detection site
            print("Testing stealth on bot detection site...")
            await page.goto("https://bot.sannysoft.com/")
            await stealth_manager.human_delay(2000, 3000)

            # Take screenshot
            await page.screenshot(path="stealth_test_results.png")
            print("Screenshot saved as stealth_test_results.png")

            # Test 2: Human-like interactions
            print("\nTesting human-like behavior...")
            await page.goto("https://www.google.com")

            # Human-like mouse movement
            await stealth_manager.human_mouse_move(page)

            # Human-like scrolling
            await stealth_manager.human_scroll(page)

            # Human-like typing
            search_box = 'textarea[name="q"], input[name="q"]'
            if await page.locator(search_box).count() > 0:
                await stealth_manager.human_type(
                    page, search_box, "playwright stealth mode"
                )
                print("Typed search query with human-like delays")

            # Test 3: Check fingerprint
            await page.goto("https://fingerprintjs.github.io/fingerprintjs/")
            await stealth_manager.human_delay(3000, 4000)

            # Extract some detection results
            try:
                visitor_id = await page.locator(".visitor-id").inner_text()
                print(f"\nFingerprint visitor ID: {visitor_id}")
            except:
                print("\nCould not extract fingerprint data")

            # Clean up
            await browser.close()

        print("\nStealth manager test completed!")

    # Run the example
    asyncio.run(main())

# python -m scitex.scholar.browser.local.utils._StealthManager

# EOF
