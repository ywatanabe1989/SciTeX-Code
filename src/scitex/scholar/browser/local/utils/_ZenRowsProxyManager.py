#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 20:04:59 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/utils/_ZenRowsProxyManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_ZenRowsProxyManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Dict

from playwright.async_api import Browser, BrowserContext, async_playwright

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class ZenRowsProxyManager:
    def __init__(
        self,
        zenrows_proxy_username=None,
        zenrows_proxy_password=None,
        zenrows_proxy_domain=None,
        zenrows_proxy_port=None,
        zenrows_proxy_country=None,
        config: ScholarConfig = None,
    ):
        self.config = config or ScholarConfig()

        self.proxy_username = self.config.resolve(
            "zenrows_proxy_username", zenrows_proxy_username
        )
        self.proxy_password = self.config.resolve(
            "zenrows_proxy_password", zenrows_proxy_password
        )
        self.proxy_domain = self.config.resolve(
            "zenrows_proxy_domain", zenrows_proxy_domain
        )
        self.proxy_port = self.config.resolve(
            "zenrows_proxy_port", zenrows_proxy_port
        )
        self.proxy_country = self.config.resolve(
            "zenrows_proxy_country", zenrows_proxy_country
        )

    def get_proxy_config(self) -> Dict[str, Any]:
        if self.proxy_username and self.proxy_password:
            username = self.proxy_username

            if self.proxy_country:
                logger.debug(
                    f"Using ZenRows proxy with country routing: {self.proxy_country.upper()}"
                )
                proxy_url = f"http://{self.proxy_username}:{self.proxy_password}_country-{self.proxy_country}@{self.proxy_domain}:{self.proxy_port}"

            else:
                raise NotImplementedError

            return {
                "server": proxy_url,
                "username": username,
                "password": self.proxy_password,
            }
        raise ValueError("ZenRows proxy credentials required")


if __name__ == "__main__":
    print(ZenRowsProxyManager().get_proxy_config())


# python -m scitex.scholar.browser.local.utils._ZenRowsProxyManager

# EOF
