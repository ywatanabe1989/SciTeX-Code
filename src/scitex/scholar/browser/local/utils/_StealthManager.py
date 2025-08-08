#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 20:01:40 (ywatanabe)"
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
    ):
        self.viewport_size = viewport_size
        self.spoof_dimension = spoof_dimension

    def get_random_user_agent(self) -> str:
        user_agents = [
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        ]
        user_agent = random.choice(user_agents)
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
            # viewport = {"width": 1, "height": 1}
            viewport = {"width": 1920, "height": 1080}
            logger.info(
                f"Viewport defined as spoof_dimension passed during Stealth Manager initiation: {viewport}"
            )
            return viewport

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
                "Sec-Ch-Ua": '"Google Chrome";v="132", "Chromium";v="132", "Not_A Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Linux"',
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
            # Core security and sandbox
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            # Critical automation detection bypass
            "--disable-blink-features=AutomationControlled",
            "--disable-features=UserAgentClientHint",
            "--disable-features=WebRtcHideLocalIpsWithMdns",
            "--disable-features=VizDisplayCompositor",
            "--disable-features=TranslateUI",
            "--disable-features=Translate",
            "--disable-features=MediaRouter",
            "--disable-features=OptimizationHints",
            "--disable-features=AudioServiceOutOfProcess",
            "--disable-features=VizServiceSharingEnabled",
            # Enhanced fingerprinting resistance
            "--disable-web-security",
            "--disable-site-isolation-trials",
            "--disable-cross-domain-blocking",
            "--disable-features=CrossOriginOpenerPolicy",
            "--disable-features=DocumentPolicy",
            "--disable-features=OriginPolicy",
            # Network and connectivity
            "--disable-background-networking",
            "--disable-client-side-phishing-detection",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-background-mode",
            # "--disable-extensions-http-throttling",
            "--disable-ipc-flooding-protection",
            # Browser behavior normalization
            "--disable-sync",
            "--disable-translate",
            "--disable-default-apps",
            "--enable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            # Performance and timing
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-hang-monitor",
            "--disable-plugins-discovery",
            "--disable-field-trial-config",
            # Media and hardware access
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            "--autoplay-policy=user-gesture-required",
            "--disable-audio-output",
            # Logging and debugging
            "--disable-logging",
            "--disable-gpu-logging",
            "--disable-dev-shm-usage",
            "--disable-renderer-code-integrity",
            # Memory optimization
            "--memory-pressure-off",
            "--max_old_space_size=4096",
            "--disable-low-res-tiling",
            "--disable-partial-raster",
            "--disable-checker-imaging",
            # TLS/SSL improvements
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--ignore-certificate-errors-spki-list",
            "--disable-web-security",
            # Additional anti-detection
            "--disable-features=VizHitTestSurfaceLayer",
            "--disable-features=TranslateSubFrames",
            "--disable-search-engine-choice-screen",
            "--disable-features=PrivacySandboxSettings4",
            "--disable-features=AutofillServerCommunication",
            # Keep this one:
            "--enable-extensions",
        ]
        # Apply window size and position based on mode
        if self.spoof_dimension:
            # 1x1 window completely off-screen for true invisibility
            stealth_args.extend(["--window-size=1,1", "--window-position=0,0"])
            logger.info(
                "Invisible mode: Window set to 1x1 at position 0,0 (off-screen)"
            )
        else:
            # Standard window or custom size
            if self.viewport_size:
                stealth_args.append(
                    f"--window-size={self.viewport_size[0]},{self.viewport_size[1]}"
                )
            else:
                stealth_args.append("--window-size=1920,1080")

        if self.spoof_dimension:
            config_desc = "Invisible (1x1)"
        elif self.viewport_size:
            config_desc = f"{self.viewport_size[0]}x{self.viewport_size[1]}"
        else:
            config_desc = "Default (1920x1080)"

        logger.info(f"Browser window configuration: {config_desc}")
        return stealth_args

    def get_network_evasion_headers(self) -> dict:
        """Generate realistic HTTP headers to avoid network-level detection."""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Sec-Ch-Ua": '"Google Chrome";v="132", "Chromium";v="132", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Ch-Ua-Platform-Version": '"5.15.0"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "X-Real-IP": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
        }

    def get_advanced_stealth_options(self) -> dict:
        """Get comprehensive stealth options for maximum evasion."""
        base_options = self.get_stealth_options()
        base_options.update(
            {
                "extra_http_headers": self.get_network_evasion_headers(),
                "bypass_csp": True,
                "ignore_default_args": ["--enable-automation"],
                "geolocation": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },  # NYC coordinates
                "timezone_id": "America/New_York",
                "locale": "en-US",
                "permissions": ["geolocation", "notifications"],
            }
        )
        return base_options

    # async def inject_stealth_scripts(self, page: Page):
    #     """Inject JavaScript to override browser fingerprinting detection."""
    #     logger.info(
    #         "Injecting advanced stealth scripts for Cloudflare evasion"
    #     )

    #     stealth_script = """
    #     // Override WebDriver detection
    #     Object.defineProperty(navigator, 'webdriver', {
    #         get: () => undefined,
    #     });

    #     // Override automation flags
    #     window.chrome = {
    #         runtime: {},
    #         webstore: {},
    #         app: {},
    #         csi: function() {},
    #         loadTimes: function() {},
    #     };

    #     // Override plugin detection
    #     Object.defineProperty(navigator, 'plugins', {
    #         get: () => [1, 2, 3, 4, 5].map(i => ({
    #             filename: `plugin${i}.dll`,
    #             description: `Plugin ${i}`,
    #             name: `Plugin ${i}`,
    #             length: 0,
    #             item: () => null,
    #             namedItem: () => null,
    #         })),
    #     });

    #     // Override languages
    #     Object.defineProperty(navigator, 'languages', {
    #         get: () => ['en-US', 'en'],
    #     });

    #     // Override permissions
    #     const originalQuery = window.navigator.permissions.query;
    #     window.navigator.permissions.query = (parameters) => (
    #         parameters.name === 'notifications' ?
    #             Promise.resolve({ state: Notification.permission }) :
    #             originalQuery(parameters)
    #     );

    #     // Override screen properties to match common resolutions
    #     Object.defineProperty(screen, 'width', { get: () => 1920 });
    #     Object.defineProperty(screen, 'height', { get: () => 1080 });
    #     Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
    #     Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
    #     Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
    #     Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });

    #     // Spoof timezone
    #     Intl.DateTimeFormat.prototype.resolvedOptions = function() {
    #         return { timeZone: 'America/New_York' };
    #     };

    #     // Override canvas fingerprinting
    #     const getContext = HTMLCanvasElement.prototype.getContext;
    #     HTMLCanvasElement.prototype.getContext = function(type) {
    #         if (type === '2d') {
    #             const context = getContext.call(this, type);
    #             const originalFillText = context.fillText;
    #             context.fillText = function() {
    #                 // Add slight randomization to avoid consistent fingerprints
    #                 arguments[1] += Math.random() * 0.1;
    #                 arguments[2] += Math.random() * 0.1;
    #                 return originalFillText.apply(this, arguments);
    #             };
    #             return context;
    #         }
    #         return getContext.call(this, type);
    #     };

    #     // Override WebGL fingerprinting
    #     const getParameter = WebGLRenderingContext.prototype.getParameter;
    #     WebGLRenderingContext.prototype.getParameter = function(parameter) {
    #         if (parameter === 37445) return 'Intel Inc.'; // UNMASKED_VENDOR_WEBGL
    #         if (parameter === 37446) return 'Intel(R) HD Graphics 630'; // UNMASKED_RENDERER_WEBGL
    #         return getParameter.call(this, parameter);
    #     };

    #     // Console log suppression (avoid debug traces)
    #     const originalLog = console.log;
    #     console.log = function() {
    #         if (arguments[0] && typeof arguments[0] === 'string') {
    #             if (arguments[0].includes('DevTools') || arguments[0].includes('automation')) {
    #                 return;
    #             }
    #         }
    #         return originalLog.apply(this, arguments);
    #     };

    #     // Mouse movement simulation (appear more human)
    #     let lastMouseMove = Date.now();
    #     document.addEventListener('mousemove', () => {
    #         lastMouseMove = Date.now();
    #     });

    #     // Simulate human-like behavior
    #     setTimeout(() => {
    #         if (Date.now() - lastMouseMove > 30000) {
    #             const event = new MouseEvent('mousemove', {
    #                 view: window,
    #                 bubbles: true,
    #                 cancelable: true,
    #                 clientX: Math.random() * window.innerWidth,
    #                 clientY: Math.random() * window.innerHeight
    #             });
    #             document.dispatchEvent(event);
    #         }
    #     }, 30000 + Math.random() * 10000);
    #     """

    #     await page.add_init_script(stealth_script)
    #     logger.info("Advanced stealth scripts injected successfully")

    async def add_human_behavior_async(self, page: Page):
        """Add human-like behavior patterns to avoid detection."""
        # Random delay before starting interactions
        delay = random.uniform(2, 5)
        logger.info(f"Adding human behavior delay: {delay:.2f} seconds")
        await asyncio.sleep(delay)

        # Simulate scrolling behavior
        try:
            await page.evaluate(
                """
                window.scrollTo({
                    top: Math.random() * 500,
                    behavior: 'smooth'
                });
            """
            )
            await asyncio.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.debug(f"Human behavior simulation failed: {e}")

    async def handle_cloudflare_challenge_async(
        self, page: Page, max_wait: int = 45
    ):
        """Enhanced Cloudflare challenge detection and handling."""
        logger.info("Checking for Cloudflare challenge...")

        cloudflare_indicators = [
            "Just a moment",
            "Checking your browser",
            "DDoS protection by Cloudflare",
            "Cloudflare Ray ID",
            "cf-browser-verification",
            "Please wait while we verify you're a human",
            "Verify you are human",
            "Security check",
            "Browser verification",
            "cf-challenge-running",
        ]

        try:
            # First check if we're on a Cloudflare challenge page
            page_content = await page.content()
            title = await page.title()

            is_challenge = any(
                indicator.lower() in page_content.lower()
                or indicator.lower() in title.lower()
                for indicator in cloudflare_indicators
            )

            if not is_challenge:
                logger.info("No Cloudflare challenge detected")
                return True

            logger.info(
                "Cloudflare challenge detected, waiting for completion..."
            )

            # Add human-like behavior during challenge
            await self.add_human_behavior_async(page)

            # Wait for challenge completion with multiple conditions
            await page.wait_for_function(
                """
                () => {
                    const content = document.documentElement.innerText.toLowerCase();
                    const title = document.title.toLowerCase();

                    // Challenge completion indicators
                    const challengeComplete = !content.includes('just a moment') &&
                                            !content.includes('checking your browser') &&
                                            !content.includes('ddos protection') &&
                                            !content.includes('please wait') &&
                                            !content.includes('verify you are human') &&
                                            !title.includes('just a moment');

                    // Also check if we've been redirected or if the URL changed
                    const urlChanged = window.location.href !== window.initialUrl;
                    window.initialUrl = window.initialUrl || window.location.href;

                    return challengeComplete || urlChanged;
                }
                """,
                timeout=max_wait * 1000,
            )

            # Additional wait to ensure page is fully loaded
            await asyncio.sleep(random.uniform(2, 4))

            logger.info("Cloudflare challenge passed successfully")
            return True

        except Exception as e:
            logger.warning(
                f"Cloudflare challenge handling timeout or error: {e}"
            )

            # Try to detect if we're still on challenge page
            try:
                final_content = await page.content()
                still_challenged = any(
                    indicator.lower() in final_content.lower()
                    for indicator in cloudflare_indicators
                )

                if still_challenged:
                    logger.error(
                        "Still on Cloudflare challenge page after timeout"
                    )
                    return False
                else:
                    logger.info("Challenge may have completed despite timeout")
                    return True

            except:
                return False

    def get_init_script(self) -> str:
        return """
(() => {
    'use strict';

    // === CORE WEBDRIVER DETECTION REMOVAL ===
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });

    // Remove all automation-related properties
    const automationProps = [
        'webdriver', '__driver_evaluate', '__webdriver_evaluate', '__selenium_evaluate',
        '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
        '__selenium_unwrapped', '__fxdriver_unwrapped', '__webdriver_script_function',
        '__webdriver_script_func', '__webdriver_script_fn', '__fxdriver_script_fn',
        '__selenium_script_fn', '__webdriver_func', '__webdriver_fn', '__$webdriverAsyncExecutor',
        '__lastWatirAlert', '__lastWatirConfirm', '__lastWatirPrompt', '_WEBDRIVER_ELEM_CACHE',
        'ChromeDriverw', 'driver-evaluate', 'webdriver-evaluate', 'selenium-evaluate',
        'webdriverCommand', 'webdriver-evaluate-response', '__webdriverFunc', '__webdriver_script_func',
        '__$webdriverAsyncExecutor', '$chrome_asyncScriptInfo', '$cdc_asdjflasutopfhvcZLmcfl_'
    ];

    automationProps.forEach(prop => {
        try {
            delete window[prop];
            delete document[prop];
            delete navigator[prop];
        } catch (e) {}
    });

    // === NAVIGATOR PROPERTIES ===
    // Mock realistic Chrome object with proper methods
    if (!window.chrome || Object.getPrototypeOf(window.chrome) === Object.prototype) {
        window.chrome = {
            app: {
                isInstalled: false,
                InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
            },
            runtime: {
                onConnect: null,
                onMessage: null,
                onConnectExternal: null,
                onMessageExternal: null,
                connect: () => {},
                sendMessage: () => {},
                getManifest: () => ({ name: 'Chrome', version: '132.0.6834.59' }),
                getURL: (path) => 'chrome-extension://invalid/' + path
            },
            webstore: {
                onInstallStageChanged: null,
                onDownloadProgress: null,
                install: () => {}
            },
            csi: () => ({ pageT: Math.random() * 1000, startE: Math.random() * 1000 }),
            loadTimes: () => ({
                requestTime: performance.now() / 1000,
                startLoadTime: performance.now() / 1000,
                commitLoadTime: performance.now() / 1000,
                finishDocumentLoadTime: performance.now() / 1000,
                finishLoadTime: performance.now() / 1000,
                firstPaintTime: performance.now() / 1000,
                firstPaintAfterLoadTime: 0,
                navigationType: 'Other'
            })
        };

        // Make chrome object non-enumerable to match real Chrome
        Object.defineProperty(window, 'chrome', {
            value: window.chrome,
            writable: false,
            enumerable: false,
            configurable: false
        });
    }

    // === LANGUAGE AND LOCALE ===
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
        configurable: true
    });

    Object.defineProperty(navigator, 'language', {
        get: () => 'en-US',
        configurable: true
    });

    // === REALISTIC PLUGINS ===
    const mockPlugins = [
        {
            0: { type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: null },
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        },
        {
            0: { type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: null },
            description: "Portable Document Format",
            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            length: 1,
            name: "Chrome PDF Viewer"
        },
        {
            0: { type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: null },
            1: { type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: null },
            description: "Native Client",
            filename: "internal-nacl-plugin",
            length: 2,
            name: "Native Client"
        }
    ];

    Object.defineProperty(navigator, 'plugins', {
        get: () => mockPlugins,
        configurable: true
    });

    // === HARDWARE CONCURRENCY ===
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => Math.max(2, Math.min(16, Math.floor(Math.random() * 8) + 4)),
        configurable: true
    });

    // === PERMISSIONS API ===
    if (navigator.permissions && navigator.permissions.query) {
        const originalQuery = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = async (parameters) => {
            const permission = parameters.name;
            if (permission === 'notifications') {
                return Promise.resolve({ state: 'default', onchange: null });
            }
            if (permission === 'geolocation') {
                return Promise.resolve({ state: 'prompt', onchange: null });
            }
            try {
                return await originalQuery(parameters);
            } catch (e) {
                return Promise.resolve({ state: 'prompt', onchange: null });
            }
        };
    }

    // === WEBGL FINGERPRINTING PROTECTION ===
    const glContexts = ['webgl', 'webgl2', 'experimental-webgl', 'experimental-webgl2'];

    glContexts.forEach(contextType => {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext(contextType);
            if (gl) {
                const getParameter = gl.getParameter.bind(gl);
                gl.getParameter = function(parameter) {
                    // Vendor and renderer spoofing
                    if (parameter === gl.VENDOR || parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === gl.RENDERER || parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    if (parameter === gl.VERSION) {
                        return 'OpenGL ES 2.0 (ANGLE 2.1.0.c8ea8ca4eb1a)';
                    }
                    if (parameter === gl.SHADING_LANGUAGE_VERSION) {
                        return 'OpenGL ES GLSL ES 1.0 (ANGLE 2.1.0.c8ea8ca4eb1a)';
                    }
                    return getParameter(parameter);
                };
            }
        } catch (e) {}
    });

    // === CANVAS FINGERPRINTING PROTECTION ===
    const getContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(contextType, ...args) {
        if (contextType === '2d') {
            const context = getContext.call(this, contextType, ...args);
            if (context) {
                const originalFillText = context.fillText;
                const originalStrokeText = context.strokeText;

                context.fillText = function(...args) {
                    // Add slight noise to prevent consistent fingerprints
                    if (args.length >= 3) {
                        args[1] += Math.random() * 0.01 - 0.005;
                        args[2] += Math.random() * 0.01 - 0.005;
                    }
                    return originalFillText.apply(this, args);
                };

                context.strokeText = function(...args) {
                    if (args.length >= 3) {
                        args[1] += Math.random() * 0.01 - 0.005;
                        args[2] += Math.random() * 0.01 - 0.005;
                    }
                    return originalStrokeText.apply(this, args);
                };
            }
            return context;
        }
        return getContext.call(this, contextType, ...args);
    };

    // === TIMEZONE AND LOCALE CONSISTENCY ===
    if (Intl && Intl.DateTimeFormat) {
        const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {
            const options = originalResolvedOptions.call(this);
            options.timeZone = 'America/New_York'; // Consistent timezone
            return options;
        };
    }

    // === SCREEN PROPERTIES ===
    const screenProps = {
        width: 1920,
        height: 1080,
        availWidth: 1920,
        availHeight: 1040,
        colorDepth: 24,
        pixelDepth: 24,
        orientation: {
            angle: 0,
            type: 'landscape-primary'
        }
    };

    Object.keys(screenProps).forEach(prop => {
        if (prop !== 'orientation') {
            Object.defineProperty(screen, prop, {
                get: () => screenProps[prop],
                configurable: true
            });
        }
    });

    // === PREVENT TIMING ATTACKS ===
    const originalNow = performance.now;
    performance.now = function() {
        return originalNow.call(this) + Math.random() * 0.1;
    };

    // === MEMORY INFO SPOOFING ===
    if (performance.memory) {
        Object.defineProperty(performance, 'memory', {
            get: () => ({
                jsHeapSizeLimit: 4294705152,
                totalJSHeapSize: Math.floor(Math.random() * 50000000) + 10000000,
                usedJSHeapSize: Math.floor(Math.random() * 30000000) + 5000000
            }),
            configurable: true
        });
    }

    // === PREVENT IFRAME DETECTION ===
    Object.defineProperty(window, 'top', {
        get: () => window,
        configurable: true
    });

    Object.defineProperty(window, 'parent', {
        get: () => window,
        configurable: true
    });

    // === CONSOLE CLEANING ===
    const originalConsole = { ...console };
    const cleanMethods = ['debug', 'log', 'info', 'warn', 'error'];
    cleanMethods.forEach(method => {
        console[method] = function(...args) {
            const text = args.join(' ').toLowerCase();
            if (text.includes('devtools') || text.includes('automation') ||
                text.includes('webdriver') || text.includes('selenium') ||
                text.includes('playwright') || text.includes('puppeteer')) {
                return;
            }
            return originalConsole[method](...args);
        };
    });

    // === MOUSE MOVEMENT SIMULATION ===
    let mouseActivity = Date.now();
    document.addEventListener('mousemove', () => {
        mouseActivity = Date.now();
    }, true);

    // Simulate natural mouse movements
    setInterval(() => {
        if (Date.now() - mouseActivity > 30000) {
            const event = new MouseEvent('mousemove', {
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        }
    }, 30000 + Math.random() * 15000);

    // === FINAL CLEANUP ===
    // Remove any remaining automation traces
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_;
    delete window.$cdc_asdjflasutopfhvcZLmcfl_;
    delete window.$chrome_asyncScriptInfo;
    delete window.__$webdriverAsyncExecutor;

    // Freeze important objects to prevent modification
    try {
        Object.freeze(navigator);
        Object.freeze(screen);
    } catch (e) {}
})();
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
})();
        """

    async def human_delay_async(self, min_ms: int = 1000, max_ms: int = 3000):
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)

    async def human_click_async(self, page: Page, element):
        await element.hover()
        await self.human_delay_async(200, 500)
        await element.click()

    async def human_mouse_move_async(self, page: Page):
        await page.mouse.move(
            random.randint(100, 800), random.randint(100, 600)
        )

    async def human_scroll_async(self, page: Page):
        scroll_distance = random.randint(300, 800)
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await self.human_delay_async(500, 1500)

    async def human_type_async(self, page: Page, selector: str, text: str):
        element = page.locator(selector)
        await element.click()
        for char in text:
            await element.type(char)
            await self.human_delay_async(50, 200)


if __name__ == "__main__":
    import asyncio

    from playwright.async_api import async_playwright

    async def main():
        """Example usage of StealthManager for bot detection evasion."""
        stealth_manager = StealthManager()

        async with async_playwright() as p:
            # Launch browser with stealth args only
            browser = await p.chromium.launch(
                headless=False,  # Use visible mode to see the effect
                args=stealth_manager.get_stealth_options_additional(),
            )

            # Create context with stealth options (browser context options)
            stealth_options = stealth_manager.get_stealth_options()
            context = await browser.new_context(
                viewport=stealth_options["viewport"],
                user_agent=stealth_options["user_agent"],
                extra_http_headers=stealth_options["extra_http_headers"],
                ignore_https_errors=stealth_options["ignore_https_errors"],
                java_script_enabled=stealth_options["java_script_enabled"],
            )

            # Inject stealth scripts
            await context.add_init_script(stealth_manager.get_init_script())

            # Create a new page
            page = await context.new_page()

            # Test 1: Bot detection site
            print("Testing stealth on bot detection site...")
            await page.goto("https://bot.sannysoft.com/")
            await stealth_manager.human_delay_async(2000, 3000)

            # Take screenshot
            await page.screenshot(path="/tmp/stealth_test_results.png")
            print("Screenshot saved as /tmp/stealth_test_results.png")

            # Test 2: Human-like interactions
            print("\nTesting human-like behavior...")
            await page.goto("https://www.google.com")

            # Human-like mouse movement
            await stealth_manager.human_mouse_move_async(page)

            # Human-like scrolling
            await stealth_manager.human_scroll_async(page)

            # Human-like typing
            search_box = 'textarea[name="q"], input[name="q"]'
            if await page.locator(search_box).count() > 0:
                await stealth_manager.human_type_async(
                    page, search_box, "playwright stealth mode"
                )
                print("Typed search query with human-like delays")

            # Test 3: Check fingerprint
            await page.goto("https://fingerprintjs.github.io/fingerprintjs/")
            await stealth_manager.human_delay_async(3000, 4000)

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

# Test on `https://bot.sannysoft.com/` to see current detection rate.
# python -m scitex.scholar.browser.local.utils._StealthManager

# EOF
