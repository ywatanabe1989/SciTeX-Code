#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-30 21:25:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/_ProxyBrowserManager.py
# ----------------------------------------
"""Browser manager with ZenRows residential proxy support.

Based on suggestions from suggestions.md, this implements the proxy
configuration for routing all browser traffic through ZenRows proxies.
"""

import os
from typing import Optional
from playwright.async_api import Browser, async_playwright

from scitex import logging
from ._BrowserManager import BrowserManager

logger = logging.getLogger(__name__)


class ProxyBrowserManager(BrowserManager):
    """Browser manager with ZenRows residential proxy support."""
    
    def __init__(
        self,
        headless: bool = True,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        proxy_domain: Optional[str] = None,
        proxy_port: Optional[str] = None,
        **kwargs
    ):
        """Initialize proxy browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            proxy_username: ZenRows proxy username (or from env)
            proxy_password: ZenRows proxy password (or from env)
            proxy_domain: ZenRows proxy domain (or from env)
            proxy_port: ZenRows proxy port (or from env)
            **kwargs: Additional arguments for parent class
        """
        super().__init__(headless=headless, **kwargs)
        
        # Get proxy credentials from env if not provided
        self.proxy_username = proxy_username or os.environ.get("SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME")
        self.proxy_password = proxy_password or os.environ.get("SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD")
        self.proxy_domain = proxy_domain or os.environ.get("SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN")
        self.proxy_port = proxy_port or os.environ.get("SCITEX_SCHOLAR_ZENROWS_PROXY_PORT")
        
        # Check if proxy is configured
        self.use_proxy = all([
            self.proxy_username,
            self.proxy_password,
            self.proxy_domain,
            self.proxy_port
        ])
        
        if self.use_proxy:
            logger.info("ProxyBrowserManager initialized with ZenRows proxy")
        else:
            logger.warning("ProxyBrowserManager initialized without proxy (missing credentials)")
            
    async def get_browser(self) -> Browser:
        """Get or create a browser instance with proxy configuration.
        
        This overrides the parent method to add proxy settings when launching
        the browser, routing all traffic through ZenRows residential proxies.
        """
        if (
            self._shared_browser is None
            or self._shared_browser.is_connected() is False
        ):
            if self._shared_playwright is None:
                self._shared_playwright = await async_playwright().start()
                
            # Build launch options
            launch_options = {
                "headless": self.headless,
                "args": ["--no-sandbox", "--disable-dev-shm-usage"],
            }
            
            # Add proxy configuration if available
            if self.use_proxy:
                proxy_server = f"http://{self.proxy_domain}:{self.proxy_port}"
                proxy_settings = {
                    "server": proxy_server,
                    "username": self.proxy_username,
                    "password": self.proxy_password,
                }
                launch_options["proxy"] = proxy_settings
                logger.info(f"Launching browser with proxy: {self.proxy_domain}")
            else:
                logger.info("Launching browser without proxy")
                
            self._shared_browser = await self._shared_playwright.chromium.launch(
                **launch_options
            )
            
        return self._shared_browser
        
    def get_proxy_url(self) -> Optional[str]:
        """Get the full proxy URL for direct usage.
        
        Returns:
            Proxy URL in format http://username:password@domain:port
            or None if proxy is not configured
        """
        if self.use_proxy:
            return f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_domain}:{self.proxy_port}"
        return None
        
    def __repr__(self) -> str:
        """String representation."""
        if self.use_proxy:
            return f"ProxyBrowserManager(proxy={self.proxy_domain}, headless={self.headless})"
        return f"ProxyBrowserManager(no_proxy, headless={self.headless})"