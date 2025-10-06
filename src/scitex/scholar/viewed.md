10,539 lines & 30,038 words

# Repository View
#### Repository: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar`
#### Output: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/viewed.md`

## Configurations
##### Tree:
- Maximum depth: 3
- .gitignore respected
- Blacklist expresssions:
```plaintext
node_modules,.*,*.py[cod],__pycache__,*.elc,env,env-[0-9]*.[0-9]*,[1-2][0-9][0-9
][0-9]Y-*,htmlcov,*.sif,*.img,*.image,*.sandbox,*.log,logs,build,dist,*_back,*_b
ackup,*old*,.old,RUNNING,FINISHED
```

#### File content:
- Number of head: 50
- Whitelist extensions:
```plaintext
.txt,.md,.org,.el,.sh,.py,.yaml,.yml,.json,.def
```
- Blacklist expressions:
```plaintext
*.mat,*.npy,*.npz,*.csv,*.pkl,*.jpg,*.jpeg,*.mp4,*.pth,*.db*,*.out,*.err,*.cbm,*
.pt,*.egg-info,*.aux,*.pdf,*.png,*.tiff,*.wav
```


## Tree contents
.
├── auth
│   ├── _AuthenticationStrategyResolver.py
│   ├── _BrowserAuthenticator.py
│   ├── __init__.py
│   ├── library
│   │   ├── _AuthCacheManager.py
│   │   ├── _BaseAuthenticator.py
│   │   ├── _EZProxyAuthenticator.py
│   │   ├── __init__.py
│   │   ├── _LockManager.py
│   │   ├── _OpenAthensAuthenticator.py
│   │   ├── _OpenAthensPageAutomator.py
│   │   ├── _SessionManager.py
│   │   └── _ShibbolethAuthenticator.py
│   ├── README.md
│   ├── ScholarAuthManager.py
│   └── sso_automation
│       ├── _BaseSSOAutomator.py
│       ├── __init__.py
│       ├── README.md
│       ├── _SSOAutomator.py
│       └── _UniversityOfMelbourneSSOAutomator.py
├── browser
│   ├── BrowserUtils.py
│   ├── docs
│   │   └── ABOUT_PLAYWRIGHT.md
│   ├── __init__.py
│   ├── js
│   │   └── index.js
│   ├── local
│   │   ├── _BrowserMixin.py
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── ScholarBrowserManager.py
│   │   └── ScholarBrowserManager_v01-font-errros.py
│   ├── README.md
│   ├── remote
│   │   ├── _CaptchaHandler.py
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── _ZenRowsAPIBrowser.py
│   │   └── _ZenRowsRemoteBrowserManager.py
│   ├── suggestions.md
│   └── utils
│       ├── _click_and_wait.py
│       ├── _click_and_wait_v01-backup.py
│       ├── _click_and_wait_v02-with-monitor.py
│       ├── _click_center_async.py
│       ├── _click_download_button_from_chrome_pdf_viewer_async.py
│       ├── _click_with_fallbacks.py
│       ├── _close_unwanted_pages.py
│       ├── _detect_pdf_viewer_async.py
│       ├── _fill_with_fallbacks.py
│       ├── _handle_popups_async.py
│       ├── _highlight_element.py
│       ├── __init__.py
│       ├── JSLoader.py
│       ├── recommendation_for_separate_javascript_files.py
│       ├── RECOOMENDATIONS.md
│       ├── _show_grid_async.py
│       ├── _show_popup_message_async.py
│       ├── SUGGESTIONS.md
│       ├── _take_screenshot.py
│       ├── _wait_redirects.py
│       ├── _wait_redirects_v01-original.py
│       ├── _wait_redirects_v02-auth-aware.py
│       └── _wait_redirects_v03-too-fast-maybe.py
├── CLAUDE.md
├── cli
│   ├── bibtex.py
│   ├── bibtex_.py
│   ├── _CentralArgumentParser.py
│   ├── chrome.py
│   ├── download_pdf.py
│   ├── legacy
│   │   └── openurl_resolve_urls.py
│   ├── open_browser_auto.py
│   ├── open_browser_monitored.py
│   ├── open_browser.py
│   └── README.md
├── config
│   ├── _CascadeConfig.py
│   ├── default.yaml
│   ├── __init__.py
│   ├── _PathManager.py
│   ├── README.md
│   └── _ScholarConfig.py
├── core
│   ├── examples_typed_metadata.py
│   ├── __init__.py
│   ├── metadata_converters.py
│   ├── metadata_types.py
│   ├── Paper.py
│   ├── Papers.py
│   ├── README.md
│   ├── README_TYPED_METADATA.md
│   └── Scholar.py
├── data
│   ├── bibliography.bib
│   ├── neurovista.bib
│   ├── neurovista_enriched.20251004_100741.bak.bib
│   ├── neurovista_enriched.bib
│   ├── neurovista_enriched_enriched.bib
│   ├── neurovista_enriched_fixed.bib
│   ├── neurovista_enriched_test.bib
│   ├── neurovista_enriched_with_project.bib
│   ├── neurovista_test2_enriched.bib
│   ├── openaccess.bib
│   ├── pac.bib
│   ├── pac_enriched.bib
│   ├── pac-seizure_prediction_enriched.bib
│   ├── pac_titles.txt
│   ├── paywalled.bib
│   ├── related-papers-by-coauthors.bib
│   ├── related-papers-by-coauthors_enriched.bib
│   ├── seizure_prediction.bib
│   ├── test_complete_enriched.bib
│   ├── test_final_enriched.bib
│   └── test_seizure.bib
├── docs
│   ├── backup
│   │   ├── papers.bib.bak
│   │   ├── papers.bib.zip
│   │   └── papers-orig.bib
│   ├── bibfile.bib
│   ├── DETAILS_FOR_DEVELOPERS.md
│   ├── from_agents
│   │   ├── OPENATHENS_SECURITY.md
│   │   └── scholar_enhancements_summary.md
│   ├── from_user
│   │   ├── crawl4ai.md
│   │   ├── medium_article_on_logined_page_for_zenrows_1.md
│   │   ├── medium_article_on_logined_page_for_zenrows_2.md
│   │   ├── papers.bib
│   │   ├── renamed-async_functions.md
│   │   └── suggestions.md
│   ├── sample_data
│   │   ├── openaccess.json
│   │   ├── papers.bib.bak
│   │   ├── papers-enriched.bib
│   │   ├── papers-partial-enriched.bib
│   │   ├── PAYWALLED.json
│   │   ├── test_papers.bib
│   │   └── test_papers.bib.bak
│   ├── STORAGE_ARCHITECTURE.md
│   ├── SUMMARY.md
│   └── zenrows_official
│       ├── captcha_integration.md
│       ├── FAQ.md
│       ├── final_url.md
│       └── with_playwright.md
├── download
│   ├── __init__.py
│   ├── ParallelPDFDownloader.py
│   ├── README.md
│   ├── ScholarPDFDownloader.py
│   └── ScholarPDFDownloaderWithScreenshots.py
├── engines
│   ├── individual
│   │   ├── ArXivEngine.py
│   │   ├── _BaseDOIEngine.py
│   │   ├── CrossRefEngine.py
│   │   ├── CrossRefLocalEngine.py
│   │   ├── __init__.py
│   │   ├── OpenAlexEngine.py
│   │   ├── PubMedEngine.py
│   │   ├── SemanticScholarEngine.py
│   │   └── URLDOIEngine.py
│   ├── __init__.py
│   ├── JCRImpactFactorEngine.py
│   ├── README.md
│   ├── ScholarEngine.py
│   └── utils
│       ├── __init__.py
│       ├── _metadata2bibtex.py
│       ├── _PubMedConverter.py
│       ├── _standardize_metadata.py
│       ├── _TextNormalizer.py
│       └── _URLDOIExtractor.py
├── enricher
│   └── ImpactFactorEnricher.py
├── examples
│   ├── 00_config.py
│   ├── 01_auth.py
│   ├── 02_browser.py
│   ├── 03_01-engine.py
│   ├── 03_02-engine-for-bibtex.py
│   ├── 04_01-url.py
│   ├── 04_02-url-for-bibtex.py
│   ├── 04_02-url-for-dois.py
│   ├── 05_download_pdf.py
│   ├── 06_find_and_download.py
│   ├── 06_parse_bibtex.py
│   ├── 07_storage_integration.py
│   ├── 99_fullpipeline-for-bibtex.py
│   ├── 99_fullpipeline-for-one-entry.py
│   ├── 99_maintenance.py
│   ├── dev.py
│   ├── README.md
│   └── SUGGESTIONS.md
├── externals
│   ├── impact_factor_calculator
│   │   ├── LICENSE
│   │   ├── MANIFEST.in
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   └── setup.py
│   ├── impact_factor_jcr
│   │   ├── build.sh
│   │   ├── MANIFEST.in
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   └── setup.py
│   └── README.md
├── extra
│   ├── __init__.py
│   └── JournalMetrics.py
├── __init__.py
├── __main__.py
├── README.md
├── storage
│   ├── BibTeXHandler.py
│   ├── _calculate_similarity_score.py
│   ├── _DeduplicationManager.py
│   ├── __init__.py
│   ├── _LibraryCacheManager.py
│   ├── _LibraryManager.py
│   ├── _PDFExtractor.py
│   └── ScholarLibrary.py
├── tests
│   ├── cli_flags_combinations.py
│   ├── CLI_TEST_RESULTS.md
│   ├── coverage_analysis.py
│   ├── run_zotero_tests.py
│   ├── test_tiered_translators.py
│   ├── test_translator_javascript_patterns.py
│   ├── test_with_embedded_cases.py
│   └── test_zotero_translator_patterns.py
├── TODO.md
├── url
│   ├── docs
│   │   ├── CORE_URL_TYPES.md
│   │   └── URL_SCHEMA.md
│   ├── helpers
│   │   ├── __init__.py
│   │   └── TODO.md
│   ├── __init__.py
│   ├── README.md
│   └── ScholarURLFinder.py
├── utils
│   ├── deduplicate_library.py
│   ├── enrich_and_fix_library.py
│   ├── fix_metadata_and_symlinks.py
│   ├── fix_metadata_complete.py
│   ├── fix_metadata_standardized.py
│   ├── fix_metadata_with_crossref.py
│   ├── __init__.py
│   ├── migrate_pdfs_to_master.py
│   ├── papers_utils.py
│   ├── paper_utils.py
│   ├── _parse_bibtex.py
│   ├── refresh_symlinks.py
│   ├── _TextNormalizer.py
│   ├── update_symlinks.py
│   └── url_utils.py
└── viewed.md


## File contents

### `./auth/_AuthenticationStrategyResolver.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 04:41:22 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/_AuthenticationStrategyResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Authentication strategy resolver that determines the best approach based on user information."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class AuthenticationMethod(Enum):
    """Available authentication methods."""

    DIRECT_SSO = "direct_sso"  # Direct to institution SSO
    OPENATHENS_ONLY = "openathens_only"  # OpenAthens without SSO redirect
    OPENATHENS_TO_SSO = "openathens_sso"  # OpenAthens that redirects to SSO
    MANUAL = "manual"  # Manual intervention required


@dataclass
class AuthenticationStrategy:
    """Authentication strategy configuration."""

    method: AuthenticationMethod
    primary_url: str
    openathens_email: Optional[str] = None
    sso_automator_available: bool = False
    institution_name: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    fallback_methods: List[AuthenticationMethod] = None

    def __post_init__(self):
        if self.fallback_methods is None:
            self.fallback_methods = [AuthenticationMethod.MANUAL]


class AuthenticationStrategyResolver:

...
```


### `./auth/_BrowserAuthenticator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:47:29 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/_BrowserAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Browser-based authentication operations.

This module handles browser interactions for authentication,
including login detection, navigation, and session verification.
"""

import asyncio
from typing import Any, Dict, List, Optional

from playwright.async_api import Page, async_playwright

from scitex import logging

# from scitex.scholar.browser import BrowserUtils
from scitex.scholar.browser.utils import click_with_fallbacks, fill_with_fallbacks

from ..browser.local._BrowserMixin import BrowserMixin

logger = logging.getLogger(__name__)


class BrowserAuthenticator(BrowserMixin):
    """Handles browser-based authentication operations."""

    def __init__(
        self, mode: str = "interactive", timeout: int = 300, sso_automator=None
    ):
        """Initialize browser authenticator.

        Args:
            mode: Browser mode - 'interactive' for authentication, 'stealth' for scraping
            timeout: Timeout for browser operations in seconds
            sso_automator: Optional SSO automator instance for institution-specific handling
        """
        super().__init__(mode=mode)
        self.timeout = timeout
        self.sso_automator = sso_automator

    async def navigate_to_login_async(self, url: str) -> Page:

...
```


### `./auth/__init__.py`

```python
"""Authentication module for Scholar."""

from .ScholarAuthManager import ScholarAuthManager

__all__ = [
    "ScholarAuthManager",
]

# EOF

...
```


### `./auth/library/_AuthCacheManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-10 09:29:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/library/_AuthCacheManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Cache management for authentication sessions.

This module handles saving and loading authentication session data
to/from cache files with proper permissions and error handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ._SessionManager import SessionManager

logger = logging.getLogger(__name__)


class AuthCacheManager:
    """Handles session cache operations for authentication providers."""

    def __init__(
        self,
        cache_name: str,
        config: ScholarConfig,
        email: Optional[str] = None,
    ):
        """Initialize cache manager.

        Args:
            cache_name: Name for the cache file (e.g., "openathens")
            config: ScholarConfig instance for path management
            email: User email for validation
        """
        self.cache_name = cache_name
        self.config = config
        self.email = email
        self.cache_file, self.lock_file = self._setup_cache_files()

...
```


### `./auth/library/_BaseAuthenticator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 13:58:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/library/_BaseAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Abstract base class for authenticators.

This module provides the base interface that all authenticators
(OpenAthens, Lean Library, etc.) must implement.
"""

"""Imports"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from scitex import logging

from scitex.errors import AuthenticationError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""


class BaseAuthenticator(ABC):
    """
    Abstract base class for authentication providers.

    All authentication providers (OpenAthens, EZProxy, Shibboleth, etc.)
    should inherit from this class and implement the required methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication provider.

        Args:
            config: Authenticator-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace("Authentication", "")


...
```


### `./auth/library/_EZProxyAuthenticator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 12:30:00"
# Author: Yusuke Watanabe
# File: _EZProxyAuthenticator.py

"""
EZProxy authentication for institutional access to academic papers.

This module provides authentication through EZProxy systems
to enable legal PDF downloads via institutional subscriptions.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse

from scitex import logging

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    async_playwright = None
    Page = None
    Browser = None

from scitex.errors import ScholarError
from ._BaseAuthenticator import BaseAuthenticator

logger = logging.getLogger(__name__)


class EZProxyError(ScholarError):
    """Raised when EZProxy authentication fails."""
    pass


class EZProxyAuthenticator(BaseAuthenticator):
    """
    Handles EZProxy authentication for institutional access.

    EZProxy is a web proxy server used by libraries to provide remote access
    to restricted digital resources.

    This authenticator:
    1. Authenticates via institutional EZProxy server
    2. Maintains authenticate_async sessions

...
```


### `./auth/library/__init__.py`

```python

...
```


### `./auth/library/_LockManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:43:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_LockManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""File-based locking for authentication operations.

This module provides file-based locking to prevent concurrent
authentication attempts that could interfere with each other.
"""

import asyncio
import fcntl
import time
from pathlib import Path
from typing import Optional

from scitex import logging

from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class LockError(ScholarError):
    """Raised when lock operations fail."""
    pass


class LockManager:
    """Manages file-based locks for authentication operations."""

    def __init__(self, lock_file: Path, max_wait_seconds: int = 300):
        """Initialize lock manager.
        
        Args:
            lock_file: Path to the lock file
            max_wait_seconds: Maximum time to wait for lock acquisition
        """
        self.lock_file = lock_file
        self.max_wait_seconds = max_wait_seconds
        self._lock_fd: Optional[int] = None
        self._is_locked = False


...
```


### `./auth/library/_OpenAthensAuthenticator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 15:23:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/library/_OpenAthensAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""OpenAthens authentication for institutional access to academic papers.

This module provides authentication through OpenAthens single sign-on
to enable legal PDF downloads via institutional subscriptions.

This refactored version uses smaller, focused helper classes:
- SessionManager: Handles session state and validation
- AuthCacheManager: Handles session caching operations
- LockManager: Handles concurrent authentication prevention
- BrowserAuthenticator: Handles browser-based authentication
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

from scitex import logging

from scitex.errors import ScholarError
from scitex.scholar.config import ScholarConfig
from .._BrowserAuthenticator import BrowserAuthenticator
from ._BaseAuthenticator import BaseAuthenticator
from ._AuthCacheManager import AuthCacheManager
from ._LockManager import LockManager
from ._SessionManager import SessionManager

logger = logging.getLogger(__name__)


class OpenAthensError(ScholarError):
    """Raised when OpenAthens authentication fails."""

    pass


class OpenAthensAuthenticator(BaseAuthenticator):
    """Handles OpenAthens authentication for institutional access.

...
```


### `./auth/library/_OpenAthensPageAutomator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:43:52 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/library/_OpenAthensPageAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""OpenAthens page automation for institutional email entry and selection."""

import asyncio
from typing import Optional

from playwright.async_api import BrowserContext, Page

# from scitex.scholar.browser import BrowserUtils
from scitex.scholar.browser.utils import click_with_fallbacks
from scitex.scholar.config import ScholarConfig

from ..sso_automation._BaseSSOAutomator import BaseSSOAutomator


class OpenAthensPageAutomator(BaseSSOAutomator):
    """Automator for the initial OpenAthens page (my.openathens.net)."""

    def __init__(
        self,
        openathens_email: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
        **kwargs,
    ):
        """Initialize OpenAthens page automator.

        Args:
            openathens_email: Institutional email for OpenAthens
            config: ScholarConfig instance
            **kwargs: Additional arguments
        """
        if config is None:
            config = ScholarConfig()

        # Resolve email from config
        self.openathens_email = config.resolve(
            "openathens_email", openathens_email, default=""
        )

        super().__init__(**kwargs)

...
```


### `./auth/library/_SessionManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:43:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_SessionManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Session management for authentication providers.

This module handles session state, validation, and expiry management
for authentication providers like OpenAthens.
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Handles session state and validation for authentication providers."""

    def __init__(self, default_expiry_hours: int = 8):
        """Initialize session manager.
        
        Args:
            default_expiry_hours: Default session expiry time in hours
        """
        self.default_expiry_hours = default_expiry_hours
        self.reset_session()
        
        # Live verification cache
        self._last_live_verified_at: Optional[float] = None
        self._live_verification_cache_seconds = 300  # 5 minutes

    def reset_session(self) -> None:
        """Reset all session data."""
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []
        self._session_expiry: Optional[datetime] = None

    def set_session_data(
        self, 

...
```


### `./auth/library/_ShibbolethAuthenticator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 13:00:00"
# Author: Yusuke Watanabe
# File: _ShibbolethAuthenticator.py

"""
Shibboleth authentication for institutional access to academic papers.

This module provides authentication through Shibboleth single sign-on
to enable legal PDF downloads via institutional subscriptions.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin, parse_qs

from scitex import logging

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    async_playwright = None
    Page = None
    Browser = None

from scitex.errors import ScholarError
from ._BaseAuthenticator import BaseAuthenticator

logger = logging.getLogger(__name__)


class ShibbolethError(ScholarError):
    """Raised when Shibboleth authentication fails."""
    pass


class ShibbolethAuthenticator(BaseAuthenticator):
    """
    Handles Shibboleth authentication for institutional access.

    Shibboleth is a single sign-on (SSO) system that provides federated
    identity management and access control for academic resources.

    This authenticator:
    1. Authenticates via institutional Identity Provider (IdP)

...
```


### `./auth/README.md`

```markdown

# Authentication Module

This module provides authentication through various institutional systems:

1. **OpenAthens** - Single sign-on system (fully implemented)
2. **EZProxy** - Library proxy server (placeholder)  
3. **Shibboleth** - Federated identity management (placeholder)

## Quick Start

### ScholarAuthManager

```python
import os
from scitex.scholar.auth import ScholarAuthManager

# Setup authentication manager
auth_manager = ScholarAuthManager(email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"))

# Authenticate
await auth_manager.ensure_authenticate_async()

# Check status
is_authenticate_async = await auth_manager.is_authenticate_async()
```

## Authentication Workflow: [`./auth`](./auth)

``` mermaid
sequenceDiagram
    participant User
    participant ScholarAuthManager
    participant OpenAthensAuthenticator
    participant SessionManager
    participant AuthCacheManager
    participant LockManager
    participant BrowserAuthenticator

    User->>ScholarAuthManager: authenticate_async(force=False)
    ScholarAuthManager->>SessionManager: has_valid_session_data()
    SessionManager-->>ScholarAuthManager: returns session status
    alt Session is valid
        ScholarAuthManager-->>User: returns success
    else Session is invalid or force=True
        ScholarAuthManager->>LockManager: acquire_lock_async()
        LockManager-->>ScholarAuthManager: lock acquired
        ScholarAuthManager->>AuthCacheManager: load_session_async()
        AuthCacheManager-->>ScholarAuthManager: returns cached session if available
        alt Cached session is valid
```

...
```


### `./auth/ScholarAuthManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:28:44 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/ScholarAuthManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Authentication manager for coordinating multiple authentication providers.

This module manages different authentication methods and provides a unified
interface for authentication operations.
"""


from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.errors import AuthenticationError
from scitex.scholar.config import ScholarConfig

from .library._BaseAuthenticator import BaseAuthenticator
from .library._EZProxyAuthenticator import EZProxyAuthenticator
from .library._OpenAthensAuthenticator import OpenAthensAuthenticator
from .library._ShibbolethAuthenticator import ShibbolethAuthenticator

logger = logging.getLogger(__name__)


class ScholarAuthManager:
    """
    Manages multiple authentication providers.

    This class coordinates between different authentication methods
    (OpenAthens, Lean Library, etc.) and provides a unified interface.
    """

    def __init__(
        self,
        email_openathens: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_OPENATHENS_EMAIL"
        ),
        email_ezproxy: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_EZPROXY_EMAIL"
        ),
        email_shibboleth: Optional[str] = os.getenv(

...
```


### `./auth/sso_automation/_BaseSSOAutomator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 11:14:18 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/sso_automation/_BaseSSOAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Base class for SSO automation."""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext, Page

from scitex.logging import getLogger
from scitex.scholar.config import ScholarConfig

logger = getLogger(__name__)


class BaseSSOAutomator(ABC):
    """Abstract base class for SSO automation."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        mode: str = "interactive",
        use_persistent_session: bool = True,
        session_expiry_days: int = 7,
        notification_from_email_address=None,
        notification_from_email_password=None,
        notification_from_email_smtp_server=None,
        notification_from_email_smtp_port=None,
        notification_from_email_sender_name=None,
        notification_to_email_address=None,
        config=None,
    ):
        """Initialize SSO automator.

        Args:
            username: Username for authentication
            password: Password for authentication

...
```


### `./auth/sso_automation/__init__.py`

```python
# """SSO Automation module for academic institutions."""

# # Import base class
# from ._BaseSSOAutomator import BaseSSOAutomator

# Import factory
from ._SSOAutomator import SSOAutomator

# # Import specific automators
# from ._UniversityOfMelbourneSSOAutomator import UniversityOfMelbourneSSOAutomator

__all__ = [
    # "BaseSSOAutomator",
    "SSOAutomator",
    # "UniversityOfMelbourneSSOAutomator",
]

# # EOF

...
```


### `./auth/sso_automation/README.md`

```markdown

# SSO Automations

Automated Single Sign-On (SSO) handlers for academic institutions, enabling seamless authentication to access paywalled content through institutional subscriptions.

## Overview

This module provides an extensible framework for automating SSO login processes at different academic institutions. It handles the complex authentication flows required to access scholarly content through institutional subscriptions.

## Features

- 🔐 **Automated Authentication**: Handles complete SSO login flows including 2FA
- 🏛️ **Multi-Institution Support**: Extensible architecture for adding new institutions
- 💾 **Persistent Sessions**: Caches authenticate_async sessions to minimize login frequency
- 🔍 **Auto-Detection**: Automatically identifies institutions from URLs
- 🛡️ **Secure Credentials**: Environment-based credential management
- 🔄 **Session Management**: Automatic session refresh and validation

## Architecture

```
sso_automation/
├── __init__.py
├── _BaseSSOAutomator.py      # Abstract base class
├── _SSOAutomator.py   # Factory for creating automators
└── _UniversityOfMelbourneSSOAutomator.py  # Example implementation
```

## Usage

### Basic Usage with Auto-Detection

```python
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import ScholarAuthManager

# The resolver will auto-detect institution from URL
resolver = OpenURLResolver(
    auth_manager=ScholarAuthManager(),
    resolver_url="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
)

# SSO automation happens automatically during resolution
result = await resolver._resolve_single_async(doi="10.1038/nature12373")
```

### Manual Configuration

```python
from scitex.scholar.sso_automation import UniversityOfMelbourneSSOAutomator
```

...
```


### `./auth/sso_automation/_SSOAutomator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 11:25:43 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/sso_automation/_SSOAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Factory for creating SSO automators."""

from typing import Dict, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ._BaseSSOAutomator import BaseSSOAutomator

logger = logging.getLogger(__name__)


class SSOAutomator:
    """Factory for creating institution-specific SSO automators."""

    # Email domain mappings
    EMAIL_DOMAIN_MAP = {
        "@unimelb.edu.au": "UniversityOfMelbourne",
        "@student.unimelb.edu.au": "UniversityOfMelbourne",
    }

    # URL pattern mappings
    URL_PATTERN_MAP = {
        "unimelb": "UniversityOfMelbourne",
        "melbourne.edu.au": "UniversityOfMelbourne",
        "exlibrisgroup.com/sfxlcl41": "UniversityOfMelbourne",
    }

    # Institution name mappings
    INSTITUTION_NAME_MAP = {
        "unimelb": "UniversityOfMelbourne",
        "university of melbourne": "UniversityOfMelbourne",
        "melbourne": "UniversityOfMelbourne",
        "melbourne university": "UniversityOfMelbourne",
    }

    # Automator class mappings
    AUTOMATOR_CLASS_MAP = {
        "UniversityOfMelbourne": "_UniversityOfMelbourneSSOAutomator.UniversityOfMelbourneSSOAutomator",

...
```


### `./auth/sso_automation/_UniversityOfMelbourneSSOAutomator.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:44:29 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/sso_automation/_UniversityOfMelbourneSSOAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""University of Melbourne SSO automation."""

from typing import Optional

from playwright.async_api import Page, TimeoutError

# from scitex.scholar.browser import BrowserUtils
from scitex.scholar.browser.utils import click_with_fallbacks, fill_with_fallbacks
from scitex.scholar.config import ScholarConfig

from ._BaseSSOAutomator import BaseSSOAutomator


class UniversityOfMelbourneSSOAutomator(BaseSSOAutomator):
    """SSO automator for University of Melbourne."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
        **kwargs,
    ):
        """Initialize UniMelb SSO automator.

        Args:
            username: UniMelb username (defaults to UNIMELB_SSO_USERNAME env var)
            password: UniMelb password (defaults to UNIMELB_SSO_PASSWORD env var)
            config: ScholarConfig
            **kwargs: Additional arguments for BaseSSOAutomator
        """
        # Get credentials from environment if not provided
        if config is None:
            config = ScholarConfig()

        username = config.resolve("sso_username", username, default="")
        password = config.resolve("sso_password", password, default="")

        super().__init__(username=username, password=password, **kwargs)

...
```


### `./browser/BrowserUtils.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 18:40:35 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/BrowserUtils.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from typing import Any, Dict, List, Optional

"""Shared browser utilities to avoid circular dependencies.

This module contains browser automation utilities that can be used
by both BrowserAuthenticator and SSO automators without creating
circular dependencies.
"""

from playwright.async_api import Browser, BrowserContext, Page, TimeoutError

from scitex import logging

logger = logging.getLogger(__name__)


class BrowserUtils:
    """Shared browser automation utilities."""

    @staticmethod
    async def capture_debug_info(
        page: Page, prefix: str = "debug"
    ) -> Dict[str, str]:
        """Capture screenshot and HTML for debugging failed operations.

        Args:
            page: Browser page
            prefix: Filename prefix for debug files

        Returns:
            Dict with screenshot_path and html_path
        """
        import time

        timestamp = int(time.time())

        try:
            screenshot_path = f"/tmp/{prefix}_screenshot_{timestamp}.png"

...
```


### `./browser/docs/ABOUT_PLAYWRIGHT.md`

```markdown

## About Playwright

https://playwright.dev/python/docs/api/class-playwright

### Hierarchy
```
Browser (Chrome instance)
├── Context (isolated session - cookies, storage)
│   ├── Page (individual tab)
│   └── Page (individual tab)
└── Context (another isolated session)
    ├── Page (individual tab)
    └── Page (individual tab)
```

### Key Concepts
1. Browser - Single Chrome process
   - Can be headless or visible
   - Switching visibility requires new browser instance

2. Context - Isolated browsing session
   - Has own cookies, localStorage, sessionStorage
   - Multiple contexts = multiple user sessions
   - Contexts don't share data with each other

3. Page - Individual tab/window
   - Pages in same context share cookies/storage
   - Can navigate, interact, screenshot

### Common Patterns
```python
# Single context, multiple pages
browser = await playwright.chromium.launch()
context = await browser.new_context()
page1 = await context.new_page()
page2 = await context.new_page()  # Shares cookies with page1

# Multiple contexts (isolated sessions)
context1 = await browser.new_context()  # User session 1
context2 = await browser.new_context()  # User session 2 (isolated)
```


...
```


### `./browser/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 17:03:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .local.ScholarBrowserManager import ScholarBrowserManager
# from .BrowserUtils import BrowserUtils
# from .PlaywrightVision import PlaywrightVision
from .utils import (
    click_center_async,
    click_download_button_from_chrome_pdf_viewer_async,
    detect_pdf_viewer_async,
    show_grid_async,
    show_popup_message_async,
)

# from .remote._ZenRowsRemoteScholarBrowserManager import ZenRowsRemoteScholarBrowserManager
# from .remote._ZenRowsAPIBrowser import ZenRowsAPIBrowser

__all__ = [
    "ScholarBrowserManager",
    # "BrowserUtils",
    # "PlaywrightVision",
    "show_popup_message_async",
    "click_center_async",
    "click_download_button_from_chrome_pdf_viewer_async",
    "detect_pdf_viewer_async",
    "show_grid_async",
    "show_popup_message_async",
    # "ZenRowsRemoteScholarBrowserManager",
    # "ZenRowsAPIBrowser",
]

# EOF

...
```


### `./browser/local/_BrowserMixin.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 20:04:42 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/_BrowserMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import aiohttp
from playwright.async_api import Browser, async_playwright

from .utils._CaptchaHandler import CaptchaHandler
from .utils._CookieAutoAcceptor import CookieAutoAcceptor


class BrowserMixin:
    """Mixin for local browser-based strategies with common functionality.

    Browser Modes:
    - interactive: For human interaction (authentication, debugging) - 1280x720 viewport
    - stealth: For automated operations (scraping, downloading) - 1x1 viewport

    Note: Always runs browser in visible system mode (never truly headless)
    but uses viewport sizing to control interaction vs stealth behavior.
    """

    _shared_browser = None
    _shared_playwright = None

    def __init__(self, mode):
        """Initialize browser mixin.

        Args:
            mode: Browser mode - 'interactive' or 'stealth'
        """
        assert mode in ["interactive", "stealth"]

        self.cookie_acceptor = CookieAutoAcceptor()
        self.captcha_handler = CaptchaHandler()
        self.mode = mode
        self.contexts = []
        self.pages = []

    @classmethod
    async def get_shared_browser_async(cls) -> Browser:
        """Get or create shared browser instance (deprecated - use get_browser_async)."""
        if (

...
```


### `./browser/local/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 12:44:12 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .ScholarBrowserManager import ScholarBrowserManager
# from ._ChromeProfileManager import ChromeProfileManager
# from ._SeleniumScholarBrowserManager import SeleniumScholarBrowserManager
# from ._HybridScholarBrowserManager import HybridScholarBrowserManager

__all__ = [
    "ScholarBrowserManager",
    # "ZenRowsScholarBrowserManager",
    # "ChromeProfileManager",
    # "SeleniumScholarBrowserManager",
    # "HybridScholarBrowserManager"
]

# EOF

...
```


### `./browser/local/README.md`

```markdown

# Local Browser Managers

## Overview

- These managers launch and control a browser instance that runs on the local machine where the script is executed.

## ZenRowsProxyManager

- This manager routes a local browser's traffic through the ZenRows proxy service.
- It is ideal for scraping sites that have strong anti-bot measures, as it leverages ZenRows' residential IP network.

### Prerequisites

- You must configure your ZenRows credentials as environment variables. The manager will read them automatically.

1.  Set the username:
    `export SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME="YOUR_USERNAME"`

2.  Set the password:
    `export SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD="YOUR_PASSWORD"`

### Usage Example

- The following example demonstrates how to use the `ZenRowsProxyManager`.
- It navigates to `httpbin.org/ip`, which returns the client's IP address, to confirm the proxy is active.

```python
import asyncio
from scitex.scholar.browser.local import ZenRowsProxyManager

async def run_main():
    # Before running, ensure environment variables are set for the proxy
    #
    # SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME
    # SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD

    manager = ZenRowsProxyManager(headless=True)
    try:
        browser = await manager.get_browser_async()
        page = await browser.new_page()

        # Go to a site that reveals the IP address
        await page.goto("http://httpbin.org/ip", wait_until="domcontentloaded", timeout=30000)

        # The output should show_async an IP address from the ZenRows network
        content = await page.content()
        print(content)

        await page.close()
```

...
```


### `./browser/local/ScholarBrowserManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:22:08 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/ScholarBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Union

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging
from scitex.scholar.browser.utils import close_unwanted_pages
from scitex.scholar.config import ScholarConfig

from ._BrowserMixin import BrowserMixin
from .utils._ChromeProfileManager import ChromeProfileManager
from .utils._CookieAutoAcceptor import CookieAutoAcceptor
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)

"""
Browser Manager with persistent context support.

_persistent_context is a **persistent browser context** that stays alive across multiple operations.

## Regular vs Persistent Context

**Regular context** (new each time):
```python
browser = await playwright.chromium.launch()
context = await browser.new_context()  # New context each time
page = await context.new_page()
```

**Persistent context** (reused):
```python
# Created once in _launch_persistent_context_async()
self._persistent_context = await self._persistent_playwright.chromium.launch_persistent_context(
    user_data_dir=str(profile_dir),  # Persistent profile

...
```


### `./browser/local/ScholarBrowserManager_v01-font-errros.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 19:41:41 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/ScholarBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Union

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ._BrowserMixin import BrowserMixin
from .utils._ChromeProfileManager import ChromeProfileManager
from .utils._CookieAutoAcceptor import CookieAutoAcceptor
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)

"""
Browser Manager with persistent context support.

_persistent_context is a **persistent browser context** that stays alive across multiple operations.

## Regular vs Persistent Context

**Regular context** (new each time):
```python
browser = await playwright.chromium.launch()
context = await browser.new_context()  # New context each time
page = await context.new_page()
```

**Persistent context** (reused):
```python
# Created once in _launch_persistent_context_async()
self._persistent_context = await self._persistent_playwright.chromium.launch_persistent_context(
    user_data_dir=str(profile_dir),  # Persistent profile
    headless=False,

...
```


### `./browser/README.md`

```markdown

## Usage

```python
import asyncio
from scitex.scholar import ScholarBrowserManager, ScholarAuthManager

browser_manager = ScholarBrowserManager(
    chrome_profile_name="system",
    browser_mode="stealth", # "interactive"
    auth_manager=ScholarAuthManager(),
)

browser, context = (
    await browser_manager.get_authenticated_browser_and_context_async()
)

page = await context.new_page()
```

## Browser Extensions [./utils/_ChromeExtensionmanager](./utils/_ChromeExtensionmanager)

``` python
EXTENSIONS = {
    "zotero_connector": {
        "id": "ekhagklcjbdpajgpjgmbionohlpdbjgc",
        "name": "Zotero Connector",
    },
    "lean_library": {
        "id": "hghakoefmnkhamdhenpbogkeopjlkpoa",
        "name": "Lean Library",
    },
    "popup_blocker": {
        "id": "bkkbcggnhapdmkeljlodobbkopceiche",
        "name": "Pop-up Blocker",
    },
    "accept_cookies": {
        "id": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
        "name": "Accept all cookies",
    },
    # May be enough
    "captcha_solver": {
        "id": "hlifkpholllijblknnmbfagnkjneagid",
        "name": "CAPTCHA Solver",
    },
    # Might not be beneficial
    "2captcha_solver": {
        "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
        "name": "2Captcha Solver",
        "description": "reCAPTCHA v2/v3 solving (may need API for advanced features)",
```

...
```


### `./browser/remote/_CaptchaHandler.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-31 17:45:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/remote/_CaptchaHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/scholar/browser/remote/_CaptchaHandler.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Captcha handler for browser automation using 2Captcha service."""

import asyncio
import time
from typing import Optional, Dict, Any, Union
from playwright.async_api import Page, Frame
import aiohttp
import json

from scitex import logging
from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class CaptchaHandler:
    """Handles CAPTCHA solving using 2Captcha service."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with 2Captcha API key."""
        self.api_key = api_key or os.getenv("SCITEX_SCHOLAR_2CAPTCHA_API_KEY")
        if not self.api_key:
            logger.warn("2Captcha API key not configured - CAPTCHA solving disabled")
        
        self.base_url = "http://2captcha.com"
        self.timeout = 180  # 3 minutes max wait time
        
    async def handle_page_async(self, page: Page) -> bool:
        """Check and handle captcha on the current page.
        
        Returns:
            bool: True if captcha was found and solved, False otherwise
        """
        if not self.api_key:
            return False
            
        # Check for common captcha indicators
        captcha_found = await self._detect_captcha_async(page)

...
```


### `./browser/remote/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 22:34:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/remote/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Remote browser managers for ZenRows services

from ._ZenRowsRemoteScholarBrowserManager import ZenRowsRemoteScholarBrowserManager

__all__ = ["ZenRowsRemoteScholarBrowserManager"]

# EOF

...
```


### `./browser/remote/README.md`

```markdown

● Good question! Let me analyze the differences to help you decide:

  Do we need _ZenRowsAPIClient.py?

  Yes, keep it if you need:

  1. Guaranteed country routing
    - API mode 100% supports proxy_country='au'
    - WebSocket/Scraping Browser country support is experimental
  2. Simple HTTP requests without browser overhead
    - Faster for basic GET/POST requests
    - Lower resource usage
    - Better for high-volume, simple scraping
  3. Precise cost control
    - You know exactly what each request costs
    - Can disable features (JS rendering, premium proxy) per request
  4. No browser complexity
    - No page objects, no async context managers
    - Just simple request/response

  No, you can remove it if:

  1. All your use cases need browser interaction
    - Clicking buttons, filling forms, handling popups
    - Complex JavaScript sites
  2. Country routing isn't critical
    - The Scraping Browser seems to work without specific country control
    - Your IPs just need to be residential, not location-specific
  3. You want to simplify the codebase
    - One less module to maintain
    - Scraping Browser can handle most scenarios

  My Recommendation:

  Keep both because they serve different purposes:

  # Use Scraping Browser for complex sites
  if needs_javascript_interaction:
      manager = ZenRowsRemoteScholarBrowserManager()
      browser = await manager.get_browser_async()

  # Use API Client for simple requests with country needs  
  elif needs_specific_country:
      client = ZenRowsAPIClient(default_country='au')
      response = client.request(url)

  # Use regular browser for debugging
  else:
      manager = ScholarBrowserManager()

...
```


### `./browser/remote/_ZenRowsAPIBrowser.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-31 23:30:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/remote/_ZenRowsAPIBrowser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/scholar/browser/remote/_ZenRowsAPIBrowser.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
ZenRows API-based browser for reliable page rendering and screenshot capture.
This uses the ZenRows API directly instead of WebSocket for better reliability.
"""

import json
import base64
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import aiohttp

from scitex import logging
from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class ZenRowsAPIBrowser:
    """Browser-like interface using ZenRows API for page rendering.
    
    This provides a simpler, more reliable alternative to WebSocket-based
    browser connections. It's especially good for:
    - Taking screenshots
    - Handling CAPTCHAs automatically
    - Getting rendered HTML content
    - Bypassing anti-bot measures
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        proxy_country: str = "au",
        enable_antibot: bool = True,
        premium_proxy: bool = True
    ):
        """Initialize ZenRows API browser.
        

...
```


### `./browser/remote/_ZenRowsRemoteBrowserManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 22:08:31 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/remote/_ZenRowsRemoteScholarBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Browser manager specifically for the ZenRows Scraping Browser service.
This provides cloud-based Chrome instances with built-in anti-bot bypass.
"""
from typing import Any, Optional, Dict

from playwright.async_api import Browser, BrowserContext, async_playwright, Page

from scitex import logging
from scitex.scholar.browser.local.utils._CookieAutoAcceptor import CookieAutoAcceptor
from ._ZenRowsAPIBrowser import ZenRowsAPIBrowser

logger = logging.getLogger(__name__)


class ZenRowsRemoteScholarBrowserManager:
    """
    Manages a connection to the remote ZenRows Scraping Browser service.
    """

    def __init__(
        self,
        auth_manager=None,
        zenrows_api_key: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_API_KEY"
        ),
        proxy_country: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY"
        ),
        **kwargs,
    ):
        """
        Initialize ZenRows browser manager.

        Args:
            auth_manager: Authentication manager for cookie injection.
            zenrows_api_key: ZenRows API key.
            proxy_country: Country code for proxy routing (e.g., 'au', 'us').
                          Note: Country routing may only work with certain endpoints.

...
```


### `./browser/suggestions.md`

```markdown

# SciTeX JavaScript Module Structure

## Complete Directory Structure

```
js/
├── config/
│   ├── index.js
│   ├── constants.js
│   └── selectors.js
├── core/
│   ├── index.js
│   ├── browser_context.js
│   ├── page_manager.js
│   └── script_injector.js
├── index.js
├── integrations/
│   ├── crawl4ai/
│   │   ├── index.js
│   │   └── crawler.js
│   ├── puppeteer/
│   │   ├── index.js
│   │   └── page_utils.js
│   └── zotero/
│       ├── index.js
│       ├── zotero_environment.js
│       └── zotero_translator_executor.js
├── utils/
│   ├── auth/
│   │   ├── index.js
│   │   ├── cookie_manager.js
│   │   └── session_handler.js
│   ├── dom/
│   │   ├── index.js
│   │   ├── element_selector.js
│   │   ├── element_highlighter.js
│   │   ├── click_handler.js
│   │   ├── fill_handler.js
│   │   ├── scroll_manager.js
│   │   └── wait_for_element.js
│   ├── network/
│   │   ├── index.js
│   │   ├── request_interceptor.js
│   │   ├── redirect_monitor.js
│   │   └── download_monitor.js
│   └── popup/
│       ├── index.js
│       ├── popup_detector.js
│       ├── popup_blocker.js
```

...
```


### `./browser/utils/_click_and_wait.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:22:06 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_and_wait.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Dict, Optional

from playwright.async_api import Locator

from scitex import logging

logger = logging.getLogger(__name__)


async def click_and_wait(
    link: Locator,
    message: str = "Clicking link...",
    wait_redirects_options: Optional[Dict] = None,
) -> dict:
    """
    Click link with visual feedback and wait for redirect chain to complete.

    This function combines clicking logic with redirect waiting using the
    standalone wait_redirects function for better modularity.

    Args:
        link: Playwright locator for the element to click
        message: Message to display during clicking
        wait_redirects_options: Options to pass to wait_redirects function
            - timeout: Maximum wait time in milliseconds (default: 30000)
            - max_redirects: Maximum number of redirects to follow (default: 10)
            - show_progress: Show popup messages during redirects (default: False)
            - track_chain: Whether to track detailed redirect chain (default: True)
            - wait_for_idle: Whether to wait for network idle (default: True)

    Returns:
        dict: {
            'success': bool,
            'final_url': str,
            'page': Page,
            'new_page_opened': bool,
            'redirect_count': int,
            'redirect_chain': list,  # if track_chain=True
            'total_time_ms': float,

...
```


### `./browser/utils/_click_and_wait_v01-backup.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:22:06 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_and_wait.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Dict, Optional

from playwright.async_api import Locator

from scitex import logging

logger = logging.getLogger(__name__)


async def click_and_wait(
    link: Locator,
    message: str = "Clicking link...",
    wait_redirects_options: Optional[Dict] = None,
) -> dict:
    """
    Click link with visual feedback and wait for redirect chain to complete.

    This function combines clicking logic with redirect waiting using the
    standalone wait_redirects function for better modularity.

    Args:
        link: Playwright locator for the element to click
        message: Message to display during clicking
        wait_redirects_options: Options to pass to wait_redirects function
            - timeout: Maximum wait time in milliseconds (default: 30000)
            - max_redirects: Maximum number of redirects to follow (default: 10)
            - show_progress: Show popup messages during redirects (default: False)
            - track_chain: Whether to track detailed redirect chain (default: True)
            - wait_for_idle: Whether to wait for network idle (default: True)

    Returns:
        dict: {
            'success': bool,
            'final_url': str,
            'page': Page,
            'new_page_opened': bool,
            'redirect_count': int,
            'redirect_chain': list,  # if track_chain=True
            'total_time_ms': float,

...
```


### `./browser/utils/_click_and_wait_v02-with-monitor.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _click_and_wait_v02-with-monitor.py
# ----------------------------------------

"""
Enhanced click and wait with JavaScript redirect monitor integration.

This version uses the JavaScript RedirectMonitor for better tracking.
"""

from typing import Dict, Optional
import asyncio

from playwright.async_api import Locator

from scitex import logging
from scitex.scholar.browser.utils.JSLoader import JSLoader

logger = logging.getLogger(__name__)


async def click_and_wait(
    link: Locator,
    message: str = "Clicking link...",
    wait_redirects_options: Optional[Dict] = None,
) -> dict:
    """
    Click link with JavaScript redirect monitoring for complete tracking.
    
    This enhanced version uses the RedirectMonitor JavaScript module for
    comprehensive redirect chain tracking including client-side redirects.
    
    Args:
        link: Playwright locator for the element to click
        message: Message to display during clicking
        wait_redirects_options: Options for redirect waiting
            - timeout: Maximum wait time in milliseconds (default: 30000)
            - use_js_monitor: Use JavaScript RedirectMonitor (default: True)
            - wait_for_article: Wait for article URL pattern (default: True)
    
    Returns:
        dict with redirect information and final URL
    """
    from ._highlight_element import highlight_element
    from ._show_popup_message_async import show_popup_message_async
    from ._wait_redirects import wait_redirects
    
    page = link.page
    context = page.context

...
```


### `./browser/utils/_click_center_async.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 06:49:04 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_center_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

async def click_center_async(page):
    from . import show_popup_message_async

    await show_popup_message_async(page, "Clicking the center of the page...")
    viewport_size = page.viewport_size
    center_x = viewport_size["width"] // 2
    center_y = viewport_size["height"] // 2
    clicked = await page.mouse.click(center_x, center_y)
    await page.wait_for_timeout(1_000)
    return clicked

# EOF

...
```


### `./browser/utils/_click_download_button_from_chrome_pdf_viewer_async.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 10:55:39 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_download_button_from_chrome_pdf_viewer_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path
from typing import Optional

from scitex import logging

logger = logging.getLogger(__name__)


async def click_download_button_from_chrome_pdf_viewer_async(
    page, spath_pdf
) -> Optional[Path]:
    """Download PDF from Chrome PDF viewer with dynamic waiting."""
    from . import show_popup_message_async

    try:
        spath_pdf = Path(spath_pdf)
        viewport = page.viewport_size
        width = viewport["width"]
        height = viewport["height"]

        x_download = int(width * 95 / 100)
        y_download = int(height * 3 / 100)

        async with page.expect_download(timeout=120_000) as download_info:
            await page.mouse.click(x_download, y_download)

        download = await download_info.value

        # Monitor download progress
        await show_popup_message_async(page, "Monitoring download process...")
        download_path = await download.path()
        await page.wait_for_timeout(10_000)
        if download_path:
            # Wait for download to finish
            await download.save_as(spath_pdf)

            if spath_pdf.exists() and spath_pdf.stat().st_size > 1024:
                file_size_MB = spath_pdf.stat().st_size / 1e6
                logger.success(

...
```


### `./browser/utils/_click_with_fallbacks.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 11:09:38 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_with_fallbacks.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


async def click_with_fallbacks(
    page: Page, selector: str, method: str = "auto"
) -> bool:
    """Click element using multiple fallback methods."""
    if method == "auto":
        methods_order = ["playwright", "force", "js"]
    else:
        methods_order = [method]

    methods = {
        "playwright": _click_with_playwright,
        "force": _click_with_force,
        "js": _click_with_js,
    }

    for method_name in methods_order:
        if method_name in methods:
            success = await methods[method_name](page, selector)
            if success:
                logger.debug(
                    f"Click successful with {method_name}: {selector}"
                )
                return True

    logger.error(f"All click methods failed for {selector}")
    return False


async def _click_with_playwright(page: Page, selector: str) -> bool:
    try:
        await page.click(selector, timeout=5000)
        return True

...
```


### `./browser/utils/_close_unwanted_pages.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:00:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_close_unwanted_pages.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from playwright.async_api import BrowserContext, Page

from scitex import logging

logger = logging.getLogger(__name__)


async def close_unwanted_pages(
    context: BrowserContext, max_attempts: int = 20
):
    """Close unwanted extension and blank pages while keeping at least one page open."""
    await asyncio.sleep(1)

    for attempt in range(max_attempts):
        try:
            unwanted_pages = [
                page
                for page in context.pages
                if (
                    "chrome-extension://" in page.url
                    or "app.pbapi.xyz" in page.url
                    or "options.html" in page.url
                    # or page.url == "about:blank"
                )
            ]

            if not unwanted_pages:
                logger.debug("Extension cleanup completed")
                break

            # Ensure context stays alive
            if len(context.pages) == len(unwanted_pages):
                await context.new_page()

            for page in unwanted_pages:
                try:
                    await page.close()

...
```


### `./browser/utils/_detect_pdf_viewer_async.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 10:05:53 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_detect_pdf_viewer_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging

logger = logging.getLogger(__name__)


async def detect_pdf_viewer_async(page):
    from . import show_popup_message_async

    await page.wait_for_load_state("networkidle")
    await show_popup_message_async(page, "Detecting Chrome PDF Viewer...")
    detected = await page.evaluate(
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
    if detected:
        logger.debug("PDF viewer detected")
        return True
    else:
        logger.debug("PDF viewer not detected")
        return False

# EOF

...
```


### `./browser/utils/_fill_with_fallbacks.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:40:50 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_fill_with_fallbacks.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


async def fill_with_fallbacks(
    page: Page, selector: str, value: str, method: str = "auto"
) -> bool:
    """Fill element using multiple fallback methods."""
    if method == "auto":
        methods_order = ["playwright", "type", "js"]
    else:
        methods_order = [method]

    methods = {
        "playwright": _fill_with_playwright,
        "type": _fill_with_typing,
        "js": _fill_with_js,
    }

    for method_name in methods_order:
        if method_name in methods:
            success = await methods[method_name](page, selector, value)
            if success:
                logger.debug(f"Fill successful with {method_name}: {selector}")
                return True

    logger.error(f"All fill methods failed for {selector}")
    return False


async def _fill_with_playwright(page: Page, selector: str, value: str) -> bool:
    try:
        await page.fill(selector, value, timeout=5000)
        return True
    except Exception:
        return False

...
```


### `./browser/utils/_handle_popups_async.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _handle_popups_async.py
# ----------------------------------------

"""
Comprehensive popup handler for browser automation.

Detects and closes various types of popups including:
- Cookie consent banners
- Newsletter/subscription modals
- AI assistant promotions
- Authentication prompts
- General modal dialogs
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from playwright.async_api import Page, ElementHandle

from scitex import logging

logger = logging.getLogger(__name__)


class PopupHandler:
    """Handle various types of popups on web pages."""
    
    # Common selectors for different popup types
    COOKIE_SELECTORS = [
        'button#onetrust-accept-btn-handler',
        'button#onetrust-pc-btn-handler',
        'button[id*="accept-cookie"]',
        'button[id*="accept-all"]',
        'button[aria-label*="accept cookie"]',
        'button[aria-label*="Accept cookie"]',
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("I agree")',
        'button:has-text("I Agree")',
        'button:has-text("Accept")',
        '.cookie-notice button.accept',
        '[class*="cookie"] button[class*="accept"]',
    ]
    
    CLOSE_SELECTORS = [
        'button[aria-label="Close"]',
        'button[aria-label="close"]',
        'button[aria-label*="Close"]',
        'button[aria-label*="close"]',

...
```


### `./browser/utils/_highlight_element.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 08:51:47 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_highlight_element.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Locator


async def highlight_element(element: Locator, duration_ms: int = 1_000):
    """Highlight element with red overlay rectangle."""
    await element.evaluate(
        """(element, duration) => {
            // Get element position and size
            const rect = element.getBoundingClientRect();

            // Create overlay div
            const overlay = document.createElement('div');
            overlay.id = 'highlight-overlay-' + Date.now();
            overlay.style.cssText = `
                position: fixed;
                top: ${rect.top}px;
                left: ${rect.left}px;
                width: ${rect.width}px;
                height: ${rect.height}px;
                border: 5px solid red;
                background-color: rgba(255, 0, 0, 0.2);
                pointer-events: none;
                z-index: 999999;
                box-shadow: 0 0 20px red;
            `;

            document.body.appendChild(overlay);

            // Scroll element into view
            element.scrollIntoView({behavior: 'smooth', block: 'center'});

            // Remove overlay after duration
            setTimeout(() => {
                if (overlay && overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, duration);
        }""",
        duration_ms,

...
```


### `./browser/utils/__init__.py`

```python
from ._click_center_async import click_center_async
from ._click_download_button_from_chrome_pdf_viewer_async import click_download_button_from_chrome_pdf_viewer_async
from ._detect_pdf_viewer_async import detect_pdf_viewer_async
from ._show_grid_async import show_grid_async
from ._show_popup_message_async import show_popup_message_async
from ._take_screenshot import take_screenshot
from ._click_and_wait import click_and_wait
from ._highlight_element import highlight_element
from ._wait_redirects import wait_redirects
from ._close_unwanted_pages import close_unwanted_pages
from ._click_with_fallbacks import click_with_fallbacks
from ._fill_with_fallbacks import fill_with_fallbacks
from .JSLoader import JSLoader

__all__ = [
    "JSLoader",
    "click_center_async",
    "click_download_button_from_chrome_pdf_viewer_async",
    "click_and_wait",
    "detect_pdf_viewer_async",
    "show_grid_async",
    "show_popup_message_async",
    "take_screenshot",
    "highlight_element",
    "wait_redirects",
    "close_unwanted_pages",
    "click_with_fallbacks",
    "fill_with_fallbacks",
]

...
```


### `./browser/utils/JSLoader.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: JSLoader.py
# ----------------------------------------

"""
JavaScript loader for managing and caching JavaScript files.

Provides efficient loading and parameter injection for JavaScript utilities.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from scitex import logging

logger = logging.getLogger(__name__)


class JSLoader:
    """Load and manage JavaScript files for browser automation."""
    
    def __init__(self, js_dir: Optional[Path] = None):
        """Initialize with JavaScript directory."""
        if js_dir is None:
            # Default to js directory relative to this file
            js_dir = Path(__file__).parent.parent / "js"
        
        self.js_dir = Path(js_dir)
        self._cache: Dict[str, str] = {}
        
        if not self.js_dir.exists():
            logger.warning(f"JavaScript directory not found: {self.js_dir}")
    
    def load(self, script_path: str) -> str:
        """
        Load JavaScript file with caching.
        
        Args:
            script_path: Relative path to JavaScript file
            
        Returns:
            JavaScript code as string
        """
        if script_path not in self._cache:
            full_path = self.js_dir / script_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"JavaScript file not found: {full_path}")

...
```


### `./browser/utils/recommendation_for_separate_javascript_files.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 10:14:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/recommendation_for_separate_javascript_files.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Does XYZ
  - Does XYZ
  - Does XYZ
  - Saves XYZ

Dependencies:
  - scripts:
    - /path/to/script1
    - /path/to/script2
  - packages:
    - package1
    - package2
IO:
  - input-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

  - output-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

(Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
"""

"""Imports"""
import argparse

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from stx.io import load_configs
# CONFIG = load_configs()


...
```


### `./browser/utils/RECOOMENDATIONS.md`

```markdown

# Browser JavaScript Utilities for Playwright

## Directory Structure
```
src/scitex/scholar/browser/js/
├── ui/
│   ├── popup_message.js
│   ├── highlight_element.js
│   ├── show_grid.js
│   └── progress_indicator.js
├── pdf/
│   ├── detect_pdf_viewer.js
│   ├── extract_pdf_metadata.js
│   └── monitor_pdf_download.js
├── navigation/
│   ├── scroll_utilities.js
│   ├── wait_for_element.js
│   └── detect_redirects.js
├── interaction/
│   ├── click_fallbacks.js
│   ├── fill_fallbacks.js
│   └── element_visibility.js
├── data/
│   ├── extract_links.js
│   ├── extract_tables.js
│   └── extract_metadata.js
└── debug/
    ├── console_logger.js
    ├── performance_monitor.js
    └── network_monitor.js
```

## 1. UI Utilities

### `ui/popup_message.js`
```javascript
// Show customizable popup message
function showPopupMessage(message, options = {}) {
    const defaults = {
        duration: 5000,
        position: 'top',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        textColor: 'white',
        fontSize: '20px',
        zIndex: 10000
    };
    
    const config = { ...defaults, ...options };
    
```

...
```


### `./browser/utils/_show_grid_async.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 10:06:43 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_show_grid_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

async def show_grid_async(page):
    from . import show_popup_message_async

    await show_popup_message_async(page, "Showing Grid...")
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

...
```


### `./browser/utils/_show_popup_message_async.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 18:02:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_show_popup_message_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging

logger = logging.getLogger(__name__)


async def show_popup_message_async(
    page, message: str, duration_ms: int = 5_000
):
    """Show popup message on page."""
    try:
        if page is not None and not page.is_closed():
            await page.evaluate(
                f"""() => {{
                const popup = document.createElement('div');
                popup.innerHTML = `{message}`;
                popup.style.cssText = `
                    position: fixed;
                    top: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 15px 25px;
                    border-radius: 8px;
                    font-size: 20px;
                    font-family: Arial, sans-serif;
                    z-index: 10000;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                `;
                document.body.appendChild(popup);
                setTimeout(() => {{
                    if (popup.parentNode) {{
                        popup.parentNode.removeChild(popup);
                    }}
                }}, {duration_ms});
            }}"""
            )
            return True
        else:

...
```


### `./browser/utils/SUGGESTIONS.md`

```markdown

but we cannot find PDF url from science direct...



(.env-3.11) (wsl) SciTeX-Code $ /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url.py -nc



----------------------------------------

Namespace(doi='10.1016/j.smrv.2020.101353', no_cache=True)

----------------------------------------





########################################

## scitex v2.0.0

## 2025Y-08M-22D-02h07m08s_t0Kf (PID: 934998)

########################################





========================================

./src/scitex/scholar/examples/04_01-url.py

Namespace(doi='10.1016/j.smrv.2020.101353', no_cache=True)

========================================



🔗 Scholar URL Finder Demonstration

========================================

🌐 Initializing authenticated browser context...

SUCCESS: Loaded session from cache (/home/ywatanabe/.scitex/scholar/cache/auth/openathens.json): 14 cookies (expires in 3h 44m)

SUCCESS: Verified live authentication at https://my.openathens.net/account

...
```


### `./browser/utils/_take_screenshot.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 13:30:34 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_take_screenshot.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from datetime import datetime

from playwright.async_api import Page

from scitex import logging
from scitex.scholar import ScholarConfig

logger = logging.getLogger(__name__)


async def take_screenshot(
    page: Page,
    category: str,
    message: str,
    full_page: bool = False,
    config: ScholarConfig = None,
):
    """Take screenshot for debugging purposes."""
    try:
        config = config or ScholarConfig()
        screenshot_category_dir = config.get_screenshots_dir(category)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = (
            screenshot_category_dir / f"{message}-{timestamp}.png"
        )

        # Main
        await page.screenshot(
            path=str(screenshot_path), full_page=full_page, timeout=10_000
        )
        logger.success(f"Screenshot saved: {str(screenshot_path)}")
    except Exception as e:
        logger.fail(f"Screenshot not saved: {str(screenshot_path)}\n{str(e)}")

# EOF

...
```


### `./browser/utils/_wait_redirects.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:11:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_wait_redirects.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Enhanced redirect waiter that handles authentication endpoints properly.

This version continues waiting even after receiving 200 status from auth endpoints,
as they often perform client-side redirects.
"""

import asyncio
from typing import Dict
from urllib.parse import urlparse

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)

# Known authentication/intermediate endpoints that perform client-side redirects
AUTH_ENDPOINTS = [
    "auth.elsevier.com",
    "login.elsevier.com",
    "idp.nature.com",
    "secure.jbs.elsevierhealth.com",
    "go.openathens.net",
    "login.openathens.net",
    "shibboleth",
    "saml",
    "/ShibAuth/",
    "/authenticate",
    "/login",
    "/signin",
    "/sso/",
]


def is_auth_endpoint(url: str) -> bool:
    """Check if URL is likely an authentication/intermediate endpoint."""
    url_lower = url.lower()
    parsed = urlparse(url_lower)

...
```


### `./browser/utils/_wait_redirects_v01-original.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 15:28:12 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_wait_redirects.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from typing import Dict

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)


async def wait_redirects(
    page: Page,
    timeout: int = 30000,
    max_redirects: int = 30,
    show_progress: bool = False,
    track_chain: bool = True,
    wait_for_idle: bool = True,
) -> Dict:
    """
    Wait for redirect chain to complete after navigation has been initiated.

    This function should be called AFTER clicking a link or navigating, not before.
    It will wait for all redirects to complete and return detailed information.

    Args:
        page: Playwright page object
        timeout: Maximum wait time in milliseconds
        max_redirects: Maximum number of redirects to follow
        show_progress: Show popup messages during redirects (requires show_popup_message_async)
        track_chain: Whether to track detailed redirect chain
        wait_for_idle: Whether to wait for network idle after redirects

    Returns:
        dict: {
            'success': bool,
            'final_url': str,
            'redirect_count': int,
            'redirect_chain': list,  # if track_chain=True
            'total_time_ms': float,

...
```


### `./browser/utils/_wait_redirects_v02-auth-aware.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _wait_redirects_v02-auth-aware.py
# ----------------------------------------

"""
Enhanced redirect waiter that handles authentication endpoints properly.

This version continues waiting even after receiving 200 status from auth endpoints,
as they often perform client-side redirects.
"""

import asyncio
from typing import Dict, List
from urllib.parse import urlparse

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)

# Known authentication/intermediate endpoints that perform client-side redirects
AUTH_ENDPOINTS = [
    "auth.elsevier.com",
    "login.elsevier.com",
    "idp.nature.com",
    "secure.jbs.elsevierhealth.com",
    "go.openathens.net",
    "login.openathens.net",
    "shibboleth",
    "saml",
    "/ShibAuth/",
    "/authenticate",
    "/login",
    "/signin",
    "/sso/",
]

def is_auth_endpoint(url: str) -> bool:
    """Check if URL is likely an authentication/intermediate endpoint."""
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    
    # Check hostname
    for auth_pattern in AUTH_ENDPOINTS:
        if auth_pattern in parsed.hostname:
            return True
    
    # Check path

...
```


### `./browser/utils/_wait_redirects_v03-too-fast-maybe.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _wait_redirects_v02-auth-aware.py
# ----------------------------------------

"""
Enhanced redirect waiter that handles authentication endpoints properly.

This version continues waiting even after receiving 200 status from auth endpoints,
as they often perform client-side redirects.
"""

import asyncio
from typing import Dict, List
from urllib.parse import urlparse

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)

# Known authentication/intermediate endpoints that perform client-side redirects
AUTH_ENDPOINTS = [
    "auth.elsevier.com",
    "login.elsevier.com",
    "idp.nature.com",
    "secure.jbs.elsevierhealth.com",
    "go.openathens.net",
    "login.openathens.net",
    "shibboleth",
    "saml",
    "/ShibAuth/",
    "/authenticate",
    "/login",
    "/signin",
    "/sso/",
]

def is_auth_endpoint(url: str) -> bool:
    """Check if URL is likely an authentication/intermediate endpoint."""
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    
    # Check hostname
    for auth_pattern in AUTH_ENDPOINTS:
        if parsed.hostname and auth_pattern in parsed.hostname:
            return True
    
    # Check path

...
```


### `./CLAUDE.md`

```markdown

## Develop Scholar module
Now we are facing challenges with automating literature search, which is one of the modules for automatic scientific research project, SciTeX (https://scitex.ai).

Scholar related temporal files, including auth cookies and cache files, should be placed under `~/.scitex/scholar` (= "$SCITEX_DIR/scholar")

Planned workflow is:
1. Manual Login to OpenAthens (Unimelb)
   - `scitex.scholar.auth`
   - `python -m scitex.scholar.authenticate openathens`

2. Keep the authentication info to cookies
   - `scitex.scholar.auth`
   - [ ] Cookie is stored at: `` (find the actual json file here)
   - [ ] Especially, in the cookifile, which entry is important?

3. Use AI2 products to get related articles as bib file
   - e.g., `./src/scitex/scholar/docs/papers.bib`

4. Resolve DOIs from piece of information such as title in a resumable manner
   - `python -m scitex.scholar.resolve_dois --title ...`
   - `python -m scitex.scholar.resolve_dois --bibtex /path/to/bibtex-file.bib`
   - `python -m scitex.scholar.resolve_dois --bibtex src/scitex/scholar/docs/papers.bib --resume`
     - I think this should be more intuitively work for resumablly
   - Resume to handle rate limit
   - Progress and ETA should be shown like rsync
   - Performance enhancement by reducing overlaps, optimizing retry logics
     - [ ] All the 75 entires are resolved their dois

5. Resolve publisher url using OpenURL for OpenAthens (Unimelb) in a resumable manner
   - `scitex.scholar.open_url.OpenURLResolver`
   - We wanted to use ZenRows but it seems difficult to pass auth info to remote browsers
   - For local version, it seems ZenRows functionality like stealth access are limited
   - Progress and ETA should be shown like rsync

### !!! IMPORTANT: Maybe this step is not fully incorporated yet!!!
6. Enrich the bib file to add metadata in a resumable manner
   - `python -m scitex.scholar.enrich_bibtex /path/to/bibtex-file.bib`
   - `scitex.scholar.Papers.from_bibtex`
   - `scitex.scholar.enrich_bibtex`
   - `/path/to/.tmp-bibtex-file.bib` would be intuitive
   - [ ] Enriching metadata using google scholar and crawl4ai might be also another method
   - Progress and ETA should be shown like rsync
   - [ ] `./src/scitex/scholar/docs/papers-enriched.bib`
   - [ ] `./src/scitex/scholar/docs/papers-enriched.csv`
     - [ ] All the 75 entires are enriched
   - All metadata should have their source explicitly in the bib files
     - `title` should have `title_source` as well
     - In the same way, `xxxx` should have `xxxx_source` all the time


...
```


### `./cli/bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/bibtex.py
# ----------------------------------------
"""Unified CLI for BibTeX operations (merge and enrich).

Usage:
    # Enrich single file
    python -m scitex.scholar.cli.bibtex --bibtex file.bib --enrich

    # Merge multiple files
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

    # Merge and enrich in one step
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib file3.bib --merge --enrich

    # Specify output
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge --enrich -o output.bib
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

from scitex import logging
from scitex.scholar import Scholar
from scitex.scholar.storage import BibTeXHandler

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Unified BibTeX operations: merge and enrich",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Enrich single file
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich

# Merge multiple files
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

# Merge and enrich
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib file3.bib --merge --enrich -o output.bib
""",
    )


...
```


### `./cli/bibtex_.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/bibtex.py
# ----------------------------------------
"""Unified CLI for BibTeX operations (merge and enrich).

Usage:
    # Enrich single file
    python -m scitex.scholar.cli.bibtex --bibtex file.bib --enrich

    # Merge multiple files
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

    # Merge and enrich in one step
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib file3.bib --merge --enrich

    # Specify output
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge --enrich -o output.bib
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

from scitex import logging
from scitex.scholar import Scholar
from scitex.scholar.storage import BibTeXHandler

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Unified BibTeX operations: merge and enrich",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Enrich single file
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich

# Merge multiple files
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

# Merge and enrich
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib file3.bib --merge --enrich -o output.bib
""",
    )


...
```


### `./cli/_CentralArgumentParser.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 22:26:23 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/_CentralArgumentParser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Single source of truth for command-line argument configurations."""

from dataclasses import dataclass
from typing import Any, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


@dataclass
class ArgumentConfig:
    """Configuration for a single argument."""

    name: str
    help_text: str
    type_: type = str
    default: Any = None
    action: Optional[str] = None
    nargs: Optional[str] = None
    choices: Optional[List[str]] = None
    required: bool = False
    mutually_exclusive_group: Optional[str] = None


class CentralArgumentParser:

    @classmethod
    def get_command_parsers(cls):
        """Import and get parsers with descriptions from command modules."""
        parsers = {}
        descriptions = {}

        try:
            from .chrome import create_parser

            parser = create_parser()
            parsers["chrome"] = parser
            descriptions["chrome"] = parser.description

...
```


### `./cli/chrome.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 23:46:05 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/chrome.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio

from scitex import logging

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Launch browser with chrome extensions and academic authentication for manual configuration"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://google.com",
        help="URL to launch (default: https://google.com)",
    )
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=3600,
        help="Timeout in seconds (default: 3600)",
    )
    parser.add_argument(
        "--profile_name",
        type=str,
        default="system",
        help="Profile name to use (default: system)",
    )
    return parser


async def main_async():
    """Manually open ScholarBrowserManager with extensions and authentications."""
    from scitex.scholar.auth import ScholarAuthManager
    from scitex.scholar.browser import ScholarBrowserManager

    parser = create_parser()

...
```


### `./cli/download_pdf.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 23:56:08 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line interface for paywalled PDF downloads.

Usage:
    python -m scitex.scholar.download bibtex <file.bib> [--project NAME]
    python -m scitex.scholar.download paper --doi <DOI> [--title TITLE]
    python -m scitex.scholar.download paper --url <URL>
    python -m scitex.scholar.download info
"""

import argparse
import sys

from scitex import logging
from scitex.scholar.core import Paper
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader

logger = logging.getLogger(__name__)


def create_parser():
    """Create argument parser for download_pdf command."""
    parser = argparse.ArgumentParser(
        description="Download PDFs from paywalled journals using institutional authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Download PDFs from BibTeX file
python -m scitex.scholar download bibtex pac.bib --project myproject

# Download single paper by DOI
python -m scitex.scholar download paper --doi 10.1038/nature12345

# Download single paper by URL
python -m scitex.scholar download paper --url https://www.nature.com/articles/nature12345

# Show system info
python -m scitex.scholar download info""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

...
```


### `./cli/legacy/openurl_resolve_urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 13:43:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/openurl_resolve_urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-08-01 02:43:00 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/resolve_urls/__main__.py
# # ----------------------------------------
# from __future__ import annotations
# import os
# __FILE__ = (
#     "./src/scitex/scholar/open_url/resolve_urls/__main__.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------

# """Command-line interface for resumable OpenURL resolution.

# Usage:
#     python -m scitex.scholar.open_url.resolve_urls dois.txt [--output results.json] [--progress progress.json]

# Examples:
#     # Resolve URLs from DOI list
#     python -m scitex.scholar.open_url.resolve_urls dois.txt

#     # Resume interrupted resolution
#     python -m scitex.scholar.open_url.resolve_urls dois.txt --progress openurl_20250801.progress.json

#     # Save results to JSON
#     python -m scitex.scholar.open_url.resolve_urls dois.txt --output resolved_urls.json

#     # Use specific resolver
#     python -m scitex.scholar.open_url.resolve_urls dois.txt --resolver https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# """

# import argparse
# import asyncio
# import json
# import sys
# from pathlib import Path

# from scitex import log
# from scitex.scholar.auth import ScholarAuthManager

...
```


### `./cli/open_browser_auto.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open browser with automatic PDF download tracking and linking.

This CLI tool uses Playwright's download API to track which paper each
download belongs to, enabling automatic organization without filesystem monitoring.

Usage:
    # Auto-track and link downloads
    python -m scitex.scholar.cli.open_browser_auto --project neurovista

    # Include pending papers
    python -m scitex.scholar.cli.open_browser_auto --project neurovista --all
"""

import argparse
import json
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.config import ScholarConfig
from scitex.scholar.utils.url_utils import get_best_url
from scitex.logging import getLogger

logger = getLogger(__name__)


def get_failed_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get papers with failed downloads."""
    from scitex.scholar.cli.open_browser import get_failed_papers as _get_failed
    return _get_failed(project, config)


def get_pending_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get papers with pending downloads."""
    from scitex.scholar.cli.open_browser import get_pending_papers as _get_pending
    return _get_pending(project, config)


def generate_proper_filename(metadata: dict) -> str:
    """Generate proper filename from metadata.

    Args:
        metadata: Paper metadata dict

...
```


### `./cli/open_browser_monitored.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open browser with download monitoring and auto-linking.

This CLI tool opens a visible browser and monitors downloads, automatically
moving downloaded PDFs to the correct library location.

Usage:
    # Monitor downloads and auto-link
    python -m scitex.scholar.cli.open_browser_monitored --project neurovista

    # Monitor pending papers only
    python -m scitex.scholar.cli.open_browser_monitored --project neurovista --pending
"""

import argparse
import json
import sys
import time
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.config import ScholarConfig
from scitex.logging import getLogger

logger = getLogger(__name__)


class DownloadMonitor(FileSystemEventHandler):
    """Monitor downloads folder and link PDFs to library."""

    def __init__(self, paper_id_map: Dict[str, str], library_manager, config: ScholarConfig):
        """
        Args:
            paper_id_map: Maps download filenames to paper_ids
            library_manager: LibraryManager instance for organizing files
            config: Scholar configuration
        """
        self.paper_id_map = paper_id_map
        self.library_manager = library_manager
        self.config = config
        self.processed_files = set()


...
```


### `./cli/open_browser.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open browser with failed PDF URLs for manual download.

This CLI tool opens a visible browser with tabs for all papers that failed
to download automatically, allowing manual download with Zotero connector
or other browser extensions.

Usage:
    # Open failed PDFs for a project
    python -m scitex.scholar.cli.open_browser --project neurovista

    # Open only pending (not attempted) PDFs
    python -m scitex.scholar.cli.open_browser --project neurovista --pending

    # Open all PDFs (failed + pending)
    python -m scitex.scholar.cli.open_browser --project neurovista --all

    # Use specific browser profile
    python -m scitex.scholar.cli.open_browser --project neurovista --profile myprofile
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.config import ScholarConfig
from scitex.scholar.utils.url_utils import get_best_url
from scitex.logging import getLogger

logger = getLogger(__name__)


def get_failed_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get list of papers with failed PDF downloads.

    Args:
        project: Project name
        config: Scholar configuration

    Returns:
        List of paper metadata dicts with DOI, title, URL info
    """
    library_dir = config.path_manager.get_library_master_dir()
    failed_papers = []

...
```


### `./cli/README.md`

```markdown

# SciTeX Scholar CLI Documentation

## 🚀 Overview

The SciTeX Scholar CLI provides a **unified, flexible command-line interface** for managing scientific literature. Unlike traditional CLIs with rigid subcommands, our design allows **combinable operations** in a single command.

## Command Structure

```bash
python -m scitex.scholar [INPUT] [OPERATIONS] [OPTIONS]
```

Where:
- **INPUT**: Source of papers (--bibtex, --doi, --dois, --title)
- **OPERATIONS**: Actions to perform (--enrich, --download, --list, --search, --export)
- **OPTIONS**: Filters and settings (--project, --year-min, --min-citations, etc.)

## 📋 Complete CLI Reference

### 🎯 Input Sources

| Option | Description | Example |
|--------|-------------|---------|
| `--bibtex FILE` | Path to BibTeX file | `--bibtex papers.bib` |
| `--doi DOI` | Single DOI string | `--doi "10.1038/nature12373"` |
| `--dois DOI [DOI ...]` | Multiple DOIs | `--dois "10.1038/xxx" "10.1126/yyy"` |
| `--title TITLE` | Paper title for resolution | `--title "Deep learning review"` |

### 📚 Project Management

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--project NAME` | `-p` | Project for persistent storage | `--project neurovista` |
| `--create-project` | | Create new project | `--create-project` |
| `--description TEXT` | | Project description | `--description "Seizure research"` |

### ⚡ Operations

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--enrich` | `-e` | Enrich with metadata (DOIs, abstracts, citations) | `--enrich` |
| `--download` | `-d` | Download PDFs to MASTER library | `--download` |
| `--list` | `-l` | List papers in project | `--list` |
| `--search QUERY` | `-s` | Search papers in library | `--search "EEG"` |
| `--stats` | | Show library statistics | `--stats` |
| `--export FORMAT` | | Export project (bibtex/csv/json) | `--export bibtex` |

### 🔍 Filtering Options


...
```


### `./config/_CascadeConfig.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 18:36:53 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/config/_CascadeConfig.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging

logger = logging.getLogger(__name__)


class CascadeConfig:
    """Universal config resolver with precedence: direct → config → env → default

    # Usage examples:
    # Django-style
    django_config = CascadeConfig(config_dict={}, env_prefix="DJANGO_", auto_uppercase=True)
    debug = django_config.resolve("debug", direct_debug, default=False, type=bool)

    # Custom app
    app_config = CascadeConfig(yaml_data, "MYAPP_")
    port = app_config.resolve("port", direct_port, default=8000, type=int)

    # Sensitive data (auto-detected or explicit)
    secret = app_config.resolve("secret_key", direct_secret, default="")
    api_key = app_config.resolve("api_key", direct_api, default="", mask=False)

    # No prefix
    simple_config = CascadeConfig(config_data, "")
    host = simple_config.resolve("HOST", direct_host, default="localhost")
    """

    SENSITIVE_EXPRESSIONS = [
        "API",
        "PASSWORD",
        "SECRET",
        "TOKEN",
        "KEY",
        "PASS",
        "AUTH",
        "CREDENTIAL",
        "PRIVATE",
        "CERT",
    ]


...
```


### `./config/default.yaml`

```yaml
# Timestamp: "2025-09-30 20:15:03 (ywatanabe)"
# File: ./src/scitex/scholar/config/default.yaml

# ----------------------------------------
# feature
# ----------------------------------------
scholar_dir: ${SCITEX_DIR:-"~/.scitex"}
project: ${SCITEX_SCHOLAR_PROJECT:-"MASTER"}
debug_mode: ${SCITEX_SCHOLAR_DEBUG_MODE:-false}
enable_auto_enrich: ${SCITEX_SCHOLAR_AUTO_ENRICH:-true}
enable_auto_download: ${SCITEX_SCHOLAR_AUTO_DOWNLOAD:-false}

# ----------------------------------------
# Search Engines
# ----------------------------------------
engines:
  - URL
  - CrossRefLocal
  - Semantic_Scholar
  - CrossRef
  - OpenAlex
  - PubMed
  - arXiv

default_search_limit: 20
max_workers: 4
verify_ssl: true

# ----------------------------------------
# PDF Download
# ----------------------------------------
pdf_download:
  max_parallel: ${SCITEX_SCHOLAR_PDF_MAX_PARALLEL:-3}  # Max concurrent Chrome instances
  use_parallel: ${SCITEX_SCHOLAR_PDF_USE_PARALLEL:-true}  # Enable parallel downloads
  delay_between_starts: 5  # Seconds between starting workers
  default_delay: 10  # Default delay between downloads
  retry_attempts: 3
  timeout: 60  # Seconds per download attempt

# ----------------------------------------
# cache
# ----------------------------------------
use_cache_search: true
use_cache_url_finder: true
use_cache_pdf_downloader: true


# ----------------------------------------
# api
# ----------------------------------------

...
```


### `./config/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 04:46:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from ._ScholarConfig import ScholarConfig

__all__ = ["ScholarConfig"]

# EOF

...
```


### `./config/_PathManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 09:04:15 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/config/_PathManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


@dataclass
class TidinessConstraints:
    """Configuration for directory tidiness constraints."""

    # File naming constraints
    max_filename_length: int = 100
    allowed_filename_chars: str = r"[a-zA-Z0-9._-]"
    forbidden_filename_patterns: List[str] = field(
        default_factory=lambda: [
            r"^\.",  # No hidden files in main directories
            r"^~",  # No temporary files
            r"\s{2,}",  # No multiple spaces
            r"[<>:\"/\\|?*]",  # No Windows forbidden chars
        ]
    )

    # Directory size constraints (in MB)
    max_cache_size_mb: int = 1000  # 1GB cache
    max_workspace_size_mb: int = 2000  # 2GB workspace
    max_screenshots_size_mb: int = 500  # 500MB screenshots
    max_downloads_size_mb: int = 1000  # 1GB downloads

    # File age constraints (in days)
    cache_retention_days: int = 30
    workspace_retention_days: int = 7
    screenshots_retention_days: int = 14

...
```


### `./config/README.md`

```markdown

## Cascading Config Environment Variables
Configurations has precedence of:
1. Direct Specification
2. Configuration
3. Environmental Varibales
Example can be seen at `./config/default.yaml`

## Usage
```python
config = ScholarConfig()
api_key = config.cascade.resolve("semantic_scholar_api_key")
is_debug = config.cascade.resolve("debug_mode", type=bool)
download_dir = config.path_manager.get_downloads_dir()
```

## Modules
1. `CascadeConfig` - Universal config resolver with precedence hierarchy
2. `ScholarConfig` - Scholar-specific wrapper using CascadeConfig
3. `PathManager` - Directory structure management
4. Flattened YAML - No unnecessary nesting


...
```


### `./config/_ScholarConfig.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 18:36:29 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/config/_ScholarConfig.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re
from pathlib import Path
from typing import Optional, Union

import yaml

from scitex.errors import ScholarError
from scitex.logging import getLogger

from ._CascadeConfig import CascadeConfig
from ._PathManager import PathManager

logger = getLogger(__name__)


class ScholarConfig:
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        if config_path and Path(config_path).exists():
            config_data = self.load_yaml(config_path)
        else:
            default_path = Path(__file__).parent / "default.yaml"
            config_data = self.load_yaml(default_path)

        self.cascade = CascadeConfig(config_data, "SCITEX_SCHOLAR_")
        self._setup_path_manager()

    def __getattr__(self, name):
        """Delegate all get_ methods to path_manager"""
        if name.startswith("get_") and hasattr(self.path_manager, name):
            return getattr(self.path_manager, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __dir__(self):
        """Include path_manager's get_ methods in dir() output"""
        own_attrs = object.__dir__(self)
        path_manager_get_methods = [
            attr

...
```


### `./core/examples_typed_metadata.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examples of using typed metadata structures.

This demonstrates how to use the new type-safe metadata system.
"""

from metadata_types import (
    CompletePaperMetadata,
    PaperMetadataStructure,
    IDMetadata,
    BasicMetadata,
    ContainerMetadata,
)
from metadata_converters import (
    dict_to_typed_metadata,
    typed_to_dict_metadata,
    validate_and_normalize_engines,
    add_source_to_engines,
    merge_metadata_sources,
)
import json


def example_1_create_typed_metadata():
    """Example 1: Create typed metadata from scratch."""
    print("=" * 60)
    print("Example 1: Create typed metadata from scratch")
    print("=" * 60)

    # Create a paper with typed metadata
    paper = CompletePaperMetadata()

    # Set ID information
    paper.metadata.id.doi = "10.1234/example.2024"
    paper.metadata.id.doi_engines.append("input")

    # Set basic information
    paper.metadata.basic.title = "Example Paper on Typed Metadata"
    paper.metadata.basic.title_engines.append("input")

    paper.metadata.basic.authors = ["John Doe", "Jane Smith"]
    paper.metadata.basic.authors_engines.append("input")

    paper.metadata.basic.year = 2024
    paper.metadata.basic.year_engines.append("input")

    # Set publication information
    paper.metadata.publication.journal = "Journal of Type Safety"

...
```


### `./core/__init__.py`

```python
from .Paper import Paper
from .Papers import Papers
from .Scholar import Scholar

__all__ = [
    "Paper",
    "Papers",
    "Scholar",
]

...
```


### `./core/metadata_converters.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converters between typed metadata structures and dict/DotDict formats.

Provides bidirectional conversion to maintain backward compatibility
while enabling type-safe operations.
"""

from __future__ import annotations
from typing import Dict, Any, Union

try:
    from .metadata_types import (
        CompletePaperMetadata,
        PaperMetadataStructure,
        IDMetadata,
        BasicMetadata,
        CitationCountMetadata,
        PublicationMetadata,
        URLMetadata,
        PathMetadata,
        SystemMetadata,
        ContainerMetadata,
    )
except ImportError:
    from metadata_types import (
        CompletePaperMetadata,
        PaperMetadataStructure,
        IDMetadata,
        BasicMetadata,
        CitationCountMetadata,
        PublicationMetadata,
        URLMetadata,
        PathMetadata,
        SystemMetadata,
        ContainerMetadata,
    )


def dict_to_typed_metadata(data: Dict[str, Any]) -> CompletePaperMetadata:
    """
    Convert dictionary to typed metadata structure.

    Args:
        data: Dictionary containing metadata and container sections

    Returns:
        CompletePaperMetadata: Typed metadata structure
    """

...
```


### `./core/metadata_types.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Type-safe metadata structures for Scholar papers.

This module defines strongly-typed dataclasses for paper metadata,
ensuring type safety and clear structure throughout the pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class IDMetadata:
    """Identification metadata with source tracking."""

    doi: Optional[str] = None
    doi_engines: List[str] = field(default_factory=list)

    arxiv_id: Optional[str] = None
    arxiv_id_engines: List[str] = field(default_factory=list)

    pmid: Optional[str] = None
    pmid_engines: List[str] = field(default_factory=list)

    semantic_id: Optional[str] = None
    semantic_id_engines: List[str] = field(default_factory=list)

    ieee_id: Optional[str] = None
    ieee_id_engines: List[str] = field(default_factory=list)

    scholar_id: Optional[str] = None
    scholar_id_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "doi": self.doi,
            "doi_engines": self.doi_engines,
            "arxiv_id": self.arxiv_id,
            "arxiv_id_engines": self.arxiv_id_engines,
            "pmid": self.pmid,
            "pmid_engines": self.pmid_engines,
            "semantic_id": self.semantic_id,
            "semantic_id_engines": self.semantic_id_engines,
            "ieee_id": self.ieee_id,
            "ieee_id_engines": self.ieee_id_engines,

...
```


### `./core/Paper.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 21:02:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Paper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Paper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""Paper class for SciTeX Scholar module.

Paper is a DotDict-based container that mirrors BASE_STRUCTURE exactly.
This ensures single source of truth - Paper structure IS BASE_STRUCTURE.
All operations are handled by utility functions in scitex.scholar.utils.paper_utils.
"""

import copy
from datetime import datetime
from typing import Dict, Optional, Union

from scitex.dict import DotDict
from scitex.scholar.engines.utils import BASE_STRUCTURE


class Paper(DotDict):
    """A scientific paper - DotDict container matching BASE_STRUCTURE exactly.

    This class inherits from DotDict and initializes with BASE_STRUCTURE.
    All operations on papers are handled by:
    - Scholar class for high-level operations
    - Utility functions in paper_utils for conversions

    Usage:
        # Create empty paper with BASE_STRUCTURE
        paper = Paper()

        # Access nested fields naturally
        paper.id.doi = "10.1234/test"
        paper.basic.title = "My Paper"
        paper.basic.authors = ["Smith, J.", "Doe, A."]
        paper.citation_count.total = 85
        paper.citation_count.y2025 = 10
        paper.url.openurl_resolved = "https://..."
        paper.container.library_id = "C74FDF10"

...
```


### `./core/Papers.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 22:24:29 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/Papers.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Papers class for SciTeX Scholar module.

Papers is a simple collection of Paper objects.
All business logic is handled by Scholar or utility functions.

This is a simplified version - reduced from 39 methods to ~15 methods.
Business logic has been moved to Scholar and utility functions.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.core.Paper import Paper

logger = logging.getLogger(__name__)


class Papers:
    """A simple collection of Paper objects.

    This is a minimal collection class. Most business logic
    (loading, saving, enrichment, etc.) is handled by Scholar.

    Methods have been reduced from 39 to ~15 for simplicity.
    Complex operations should use Scholar or utility functions.
    """

    def __init__(
        self,
        papers: Optional[Union[List[Paper], List[Dict]]] = None,
        project: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize Papers collection.

        Args:
            papers: List of Paper objects or dicts to convert to Papers

...
```


### `./core/README.md`

```markdown

# Scholar Module - Global Entry Point

## Quick Start

```python
from scitex.scholar import Scholar

# 1. Initialize with project name
scholar = Scholar(
    project="neurovista",
    project_description="Seizure prediction from the NeuroVista dataset, especially using phase-amplitude coupling features"
)
# INFO: Project created: neurovista at /home/ywatanabe/.scitex/scholar/library/neurovista
# INFO: Scholar initialized (project: neurovista, workspace: /home/ywatanabe/.scitex/scholar/workspace)

# 2. Download bib file with AI2 Scholar (https://scholarqa.allen.ai/chat/)
# Assuming `./data/seizure_prediction.bib` is downloaded

# 3. Load papers from BibTeX
papers = scholar.load_bibtex("./data/seizure_prediction.bib")
# INFO: Loaded 75 BibTeX entries from data/seizure_prediction.bib
# INFO: Created 75 papers from BibTeX file

# 4. Filter papers (optional)
recent_papers = papers.filter(lambda p: p.year >= 2020)
# INFO: Lambda filter: 75 -> 50 papers

# 5. Enrich with metadata (DOI, abstract, citations, etc.)
enriched_papers = scholar.enrich_papers(recent_papers)

# 6. Save to your collection
scholar.save_papers_to_library(enriched_papers)

# 7. Export to BibTeX with enrichment
scholar.save_papers_as_bibtex(enriched_papers, "enriched.bib")

# 8. Search your saved papers
results = scholar.search_library("transformer")

# 9. Download PDFs using Browser Automation
scholar.download_pdfs(dois, dir)
```

## Filtering Papers

``` python
# Filter by impact factor
high_impact = papers.filter(lambda p: p.journal_impact_factor and p.journal_impact_factor > 10)

```

...
```


### `./core/README_TYPED_METADATA.md`

```markdown
# Typed Metadata System

## Overview

The typed metadata system provides **type-safe** data structures for Scholar paper metadata, replacing the previous dict/DotDict approach with strongly-typed dataclasses.

## Benefits

### 1. Type Safety
```python
# ❌ Old way - no type checking
paper = {"basic": {"year": "2024"}}  # Wrong type, but no error

# ✅ New way - type checked
paper = CompletePaperMetadata()
paper.metadata.basic.year = "2024"  # Type checker catches this error
paper.metadata.basic.year = 2024    # ✓ Correct
```

### 2. IDE Autocomplete
```python
# With typed metadata, your IDE shows:
paper.metadata.  # -> Autocomplete: id, basic, citation_count, publication, url, path, system
paper.metadata.basic.  # -> Autocomplete: title, authors, year, abstract, keywords, type
```

### 3. Clear Structure Documentation
The dataclass definitions serve as **living documentation** of the metadata structure.

### 4. Source Tracking with Lists
All `_engines` fields are now **lists** to support multiple sources:
```python
paper.metadata.basic.title_engines = ["input", "CrossRef", "OpenAlex"]
```

## Structure

```
CompletePaperMetadata
├── metadata: PaperMetadataStructure
│   ├── id: IDMetadata
│   │   ├── doi: Optional[str]
│   │   ├── doi_engines: List[str]
│   │   ├── arxiv_id: Optional[str]
│   │   ├── arxiv_id_engines: List[str]
│   │   └── ...
│   ├── basic: BasicMetadata
│   │   ├── title: Optional[str]
│   │   ├── title_engines: List[str]
│   │   ├── authors: Optional[List[str]]
```

...
```


### `./core/Scholar.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-04 10:10:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Unified Scholar class for scientific literature management.

This is the main entry point for all scholar functionality, providing:
- Simple, intuitive API
- Smart defaults
- Method chaining
- Progressive disclosure of advanced features
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from scitex import logging

# PDF extraction is now handled by scitex.io
from scitex.errors import ScholarError
from scitex.scholar.config import ScholarConfig

# Updated imports for current architecture
from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.storage import LibraryManager
from scitex.scholar.storage import ScholarLibrary
from scitex.scholar.engines.ScholarEngine import ScholarEngine

from .Papers import Papers

logger = logging.getLogger(__name__)


class Scholar:
    """

...
```


### `./data/pac_titles.txt`

```plaintext
'Estimating Phase Amplitude Coupling between Neural Oscillations Based on Permutation and Entropy'
'Oscillatory Activity and Phase–Amplitude Coupling in the Human Medial Frontal Cortex during Decision Making'
'A Canonical Circuit for Generating Phase-Amplitude Coupling'
'What Can Local Transfer Entropy Tell Us about Phase-Amplitude Coupling in Electrophysiological Signals?'
'Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations'
'Measuring phase-amplitude coupling between neuronal oscillations of different frequencies.'
'Parametric estimation of spectrum driven by an exogenous signal'
'Influence of White and Gray Matter Connections on Endogenous Human Cortical Oscillations'
'The olfactory bulb theta rhythm follows all frequencies of diaphragmatic respiration in the freely behaving rat'
'Phase‐amplitude coupling of sleep slow oscillatory and spindle activity correlates with overnight memory consolidation'
'Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit'
'Cross-frequency coupling within and between the human thalamus and neocortex'
'Event-Related Phase-Amplitude Coupling During Working Memory of Musical Chords'
'Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling'
'Alpha and high gamma phase amplitude coupling during motor imagery and weighted cross-frequency coupling to extract discriminative cross-frequency patterns'
'Different Methods to Estimate the Phase of Neural Rhythms Agree But Only During Times of Low Uncertainty'
'Untangling cross-frequency coupling in neuroscience'
'Direct modulation index: A measure of phase amplitude coupling for neurophysiology data'
'The bispectrum and its relationship to phase-amplitude coupling'
'Addressing Pitfalls in Phase-Amplitude Coupling Analysis with an Extended Modulation Index Toolbox'
'Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical Column'
'Seizure Onset Zone Identification Based on Phase-Amplitude Coupling of Interictal Electrocorticogram'
'Understanding phase-amplitude coupling from bispectral analysis'
'Cross-Frequency Phase-Amplitude Coupling between Hippocampal Theta and Gamma Oscillations during Recall Destabilizes Memory and Renders It Susceptible to Reconsolidation Disruption'
'Toward a proper estimation of phase–amplitude coupling in neural oscillations'
'Phase-Amplitude Coupling in Autism Spectrum Disorder: Results from the Autism Biomarkers Consortium for Clinical Trials'
'Discriminating Valid from Spurious Indices of Phase-Amplitude Coupling'
'Phase-amplitude coupling in neuronal oscillator networks'
'REPAC: Reliable Estimation of Phase-Amplitude Coupling in Brain Networks'
'Generation of phase-amplitude coupling of neurophysiological signals in a neural mass model of a cortical column'
'Multitaper estimates of phase-amplitude coupling'
'How to design optimal brain stimulation to modulate phase-amplitude coupling?'
'Shifts in Gamma Phase–Amplitude Coupling Frequency from Theta to Alpha Over Posterior Cortex During Visual Tasks'
'Phase-Amplitude Coupling in Spontaneous Mouse Behavior'
'Cross‐Frequency Couplings Reveal Mice Visual Cortex Selectivity to Grating Orientations'
'Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence'
'Phase-Amplitude Coupling and Phase Synchronization Between Medial Temporal, Frontal and Posterior Brain Regions Support Episodic Autobiographical Memory Recall'
'Heterogeneous profiles of coupled sleep oscillations in human hippocampus'
'Phase-amplitude coupling profiles differ in frontal and auditory cortices'
'Long term effects of cueing procedural memory reactivation during NREM sleep'
'Phase–Amplitude Coupling in Human Electrocorticography Is Spatially Distributed and Phase Diverse'
'CFC delta-beta is related with mixed features and response to treatment in bipolar II depression'
'Phase-dependent Stimulation for Modulating Phase-amplitude Coupling: A Computational Modeling Approach'
'Modeling the Generation of Phase-Amplitude Coupling in Cortical Circuits: From Detailed Networks to Neural Mass Models'
'Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals'
'Temporal-spatial characteristics of phase-amplitude coupling in electrocorticogram for human temporal lobe epilepsy'
'EEG phase-amplitude coupling to stratify encephalopathy severity in the developing brain'
'Variational Phase-Amplitude Coupling Characterizes Signatures of Anterior Cortex Under Emotional Processing'
'Statistical Inference for Modulation Index in Phase-Amplitude Coupling'
'Measuring Phase-Amplitude Coupling Based on the Jensen-Shannon Divergence and Correlation Matrix'

...
```


### `./docs/DETAILS_FOR_DEVELOPERS.md`

```markdown


# SciTeX Scholar

## Usage

1. Access to [AI2 Asta](https://asta.allen.ai/chat/) and download bib file for your query by clicking `Export All Citations`
2. Copy the downloaded bib file (`~/donwloads/papers.bib`) to `./data/descriptive_name.bib`
3. 
```bash
./examples/99_fullpipeline-for-bibtex.py \
    --bibtex_path ./data/descriptive_name.bib 
    --browser_mode interactive
```

./examples/99_fullpipeline-for-bibtex.py \
    --bibtex_path ./data/seizure_prediction.bib \
    --browser_mode interactive


```



``` mermaid
graph TD
    subgraph " "
        direction LR
        subgraph "Layer 1: Entrypoints"
            direction TB
            CLI("<b>CLI</b><br>Command-line interfaces for<br>users to interact with the library.")
            Examples("<b>Examples</b><br>Demonstration scripts showcasing<br>how to use various features.")
        end

        subgraph "Layer 2: Core Orchestration"
            direction TB
            Core("<b>Core</b> (Paper, Papers, Scholar)<br>Central classes that model<br>academic papers and orchestrate<br>the main workflows.")
        end

        subgraph "Layer 3: Functional Modules (Services)"
            direction TB
            Download("<b>Download</b><br>Handles the downloading of<br>PDF files from URLs.")
            URL("<b>URL Finder</b><br>Resolves DOIs and other identifiers<br>to find article and PDF URLs.")
            Auth("<b>Auth</b><br>Manages authentication with<br>institutional providers like OpenAthens.")
        end

        subgraph "Layer 4: Data & Interaction Layer"
            direction TB
            Engines("<b>Engines</b><br>Fetches metadata from various<br>academic sources like CrossRef, PubMed, etc.")
            Storage("<b>Storage</b><br>Manages the local library,<br>caching, and BibTeX handling.")

...
```


### `./docs/from_agents/OPENATHENS_SECURITY.md`

```markdown
# OpenAthens Security and Cookie Storage

## Cookie Storage Location

OpenAthens session cookies are stored in:
```
~/.scitex/scholar/openathens_sessions/
```

The exact filename depends on your institution:
- `openathens_unimelb_edu_au_session.enc` (for user@unimelb.edu.au)
- `openathens_harvard_edu_session.enc` (for user@harvard.edu)
- `openathens_default_session.enc` (if no email specified)

## Security Features

### 1. Encryption at Rest

All session cookies are encrypted using:
- **Algorithm**: Fernet (symmetric encryption)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: Machine-specific, stored in `~/.scitex/.scitex_salt`

### 2. File Permissions

- Session files: `0600` (read/write by owner only)
- Salt file: `0600` (read/write by owner only)

### 3. Automatic Migration

If you have existing unencrypted session files (`.json`), they will be:
1. Automatically encrypted on first use
2. Original unencrypted file deleted
3. No action required from you

### 4. Session Expiry

- Sessions expire after ~8 hours
- Expired sessions are automatically detected
- Re-authentication required when expired

## Security Best Practices

1. **Don't share session files** - They're encrypted with your email
2. **Keep your email secure** - It's used to derive the encryption key
3. **Machine-bound** - Sessions only work on the machine where created
4. **Regular cleanup** - Old session files can be safely deleted

## Manual Session Management

...
```


### `./docs/from_agents/scholar_enhancements_summary.md`

```markdown
# Scholar Module Enhancements Summary

## Date: 2025-07-24
## Agent: 5db30af0-6862-11f0-928a-00155d8642b8

### Completed Enhancements

#### 1. Fixed PDF Download Return Value Issue ✅
**Problem**: `Scholar.download_pdf_asyncs()` was returning an empty Papers collection even though PDFs were downloading successfully.

**Solution**: 
- Added logic to create Paper objects when DOI strings are provided as input
- Properly maps download PDFs back to Paper objects
- Returns a populated Papers collection with pdf_path set for successful downloads

**Code changes**: `_Scholar.py` lines 445-470

#### 2. Enhanced OpenAthens Authentication with Email Auto-fill ✅
**Problem**: Users had to manually type their institutional email in the OpenAthens login form.

**Solution**:
- Implemented automatic email field detection and filling
- Uses multiple CSS selectors to find the email input field
- Types with human-like delay for better compatibility
- Triggers autocomplete dropdown after filling
- Shows "(auto-filled)" in instructions when email is provided

**Code changes**: `_OpenAthensAuthenticator.py` lines 218-264

#### 3. Fixed Environment Variable Naming Convention ✅
**Problem**: Some environment variables in the default config YAML were missing the SCITEX_SCHOLAR_ prefix.

**Solution**:
- Updated all environment variable references to use consistent SCITEX_SCHOLAR_ prefix
- Added missing configuration options for OpenAthens and auto-download features
- Updated documentation in default_config.yaml

**Files changed**: 
- `config/default_config.yaml`

### Configuration Methods Supported

The OpenAthens email can now be configured in three ways (priority order):
1. **Direct parameter**: `scholar.configure_openathens(email="your.email@institution.edu")`
2. **YAML config file**: `openathens_email: "your.email@institution.edu"`
3. **Environment variable**: `SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@institution.edu"`

### Testing

Created comprehensive test scripts to verify:

...
```


### `./docs/from_user/crawl4ai.md`

```markdown

# https://github.com/unclecode/crawl4ai

docker pull unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g crawl4ai-fixed

# Visit the playground at http://localhost:11235/playground


...
```


### `./docs/from_user/medium_article_on_logined_page_for_zenrows_1.md`

```markdown

How to Scrape a Website that Requires a Login with Python
ZenRows
ZenRows

Follow
11 min read
·
Oct 12, 2023
95


1



While web scraping, you might find some data available only after you’ve signed in. In this tutorial, we’ll learn the security measures used and three effective methods to scrape_async a website that requires a login with Python.

Let’s find a solution!


Can You Scrape Websites that Require a Login?
Yes, it’s technically possible to scrape_async behind a login. But you must be mindful of the target site’s scraping rules and laws like GDPR to comply with personal data and privacy matters.

To get started, it’s essential to have some general knowledge about HTTP Request Methods. And if web scraping is new for you, read our beginner-friendly guide on web scraping with Python to master the fundamentals.

How Do You Log into a Website with Python?
The first step to scraping a login-protected website with Python is figuring out your target domain’s login type. Some old websites just require sending a username and password. However, modern ones use more advanced security measures. These include:

Client-side validations
CSRF tokens
Web Application Firewalls (WAFs)
Keep reading to learn the techniques to get around these strict security protections.

How Do You Scrape a Website behind a Login in Python?
Time to explore each step of scraping data behind site logins with Python. We’ll start with forms requiring only a username and password and then increase the difficulty progressively.

Remember that the methods show_asynccased in this tutorial are for educational purposes only.

Three, two, one… let’s code!

Sites Requiring a Simple Username and Password Login
We assume you’ve already set up Python 3 and Pip; otherwise, you should check a guide on properly installing Python.

As dependencies, we’ll use the Requests and Beautiful Soup libraries. Start by installing them:

pip install requests beautifulsoup4
Tip: If you need any help during the installation, visit this page for Requests and this one for Beautiful Soup.

Now, go to Acunetix’s User Information. This is a test page explicitly made for learning purposes and protected by a simple login, so you’ll be redirected to a login page.

...
```


### `./docs/from_user/medium_article_on_logined_page_for_zenrows_2.md`

```markdown

In simple terms, ZenRows cannot use your personal login session because it's a separate, remote service. It's like giving a delivery driver a photocopy of your ID—they can show_async it, but they can't pass the real identity check.

The Analogy: A Magic Wristband at a Festival 🎟️
Your Local Browser (with OpenURLResolver): You go to the festival gate and show_async your ticket and ID (you log in via OpenAthens). They give you a secure, non-transferable "magic wristband" (an authenticate_async session). Now you can walk around the festival, and every stall (publisher website) can see your wristband and knows you're allowed to be there.

The ZenRows API (with ZenRowsOpenURLResolver): You are outside the festival. You ask a delivery driver (the ZenRows API 🚚) to go to a specific stall for you. You can give them a picture of your wristband (your auth cookies), but when the security guard at the stall (the resolver's JavaScript 🔐) tries to scan it, their machine says it's invalid because it's not the real wristband from the main gate. The driver is stuck.

The Technical Reason
Your ScholarAuthManager uses a real browser (Playwright) to log you in. This creates a rich authentication context, which includes:

Cookies

Session Storage

Local Storage

A specific browser fingerprint

When your OpenURLResolver clicks a "View Full Text" link, the website's JavaScript doesn't just look for a cookie. It often checks the entire session context to verify you are who you say you are before redirecting you.

The ZenRowsOpenURLResolver sends a URL to a completely different browser running on ZenRows' servers. Even when you pass your cookies along, that remote browser is missing the rest of the essential authentication context. The resolver page's JavaScript detects this and refuses to perform the redirect, leaving ZenRows stuck on the resolver page.

The Solution
Your agent's conclusion is the correct approach:

For subscription content that needs your institutional login: Use the standard, browser-based OpenURLResolver. It keeps everything inside the same browser where you logged in (the one with the "magic wristband").

For public content blocked by bot detection/CAPTCHAs: Use the ZenRowsOpenURLResolver. It's perfect for scraping sites that don't require your personal login but are difficult to access.






in that case, i do not have any benefits by using zenrows and 2captcha.



how about this info? https://medium.com/@zenrows/web-scraping-login-python-948c2f4a4662



How to Scrape a Website that Requires a Login with Python



ZenRows

Follow

...
```


### `./docs/from_user/renamed-async_functions.md`

```markdown

# This works
rename.sh run_all_checks_async run_all_checks_async ./src/scitex/scholar

# Let's apply rename.sh using shell script, loop through
for func_name in ...; do rename.sh "$func_name" "$func_name"_async ./src/scitex/scholar

File: validation/_PreflightChecker.py
  36   5     async def run_all_checks_async(
  77   5     async def _check_python_version_async(self):
  92   5     async def _check_required_packages_async(self):
 122   5     async def _check_optional_features_async(
 183   5     async def _check_download_directory_async(self, download_dir: Optional[Path]):
 217   5     async def _check_network_connectivity_async(self):
 248   5     async def _check_authentication_status_async(
 295   5     async def _check_system_resources_async(self):
 373   1 async def run_preflight_checks_async(**kwargs) -> Dict[str, Any]:

File: validation/_PDFValidator.py
 203   5     async def validate_batch_async(

File: enrichment/_CitationEnricher.py
  63   7     # async def _enrich_async(self, papers: List[Paper]) -> None:
  86   7     # async def _enrich_async(self, papers):
 106   5     async def _enrich_async(self, papers):
 126   5     async def _get_citations_async(
 140   9         async def fetch_crossref_async():

File: enrichment/_BibTeXEnricher.py
 137   5     async def _fetch_crossref_async_metadata(self, doi: str) -> Dict[str, Any]:
 161   5     async def _fetch_pubmed_metadata_async(
 184   5     async def _fetch_semantic_scholar_metadata_async(
 219   5     async def _enrich_single_entry_async(
 320   5     async def enrich_bibtex_async(
 388   9         async def enrich_with_limit_async(entry: Dict, index: int):
 466   1 async def main():

File: docs/from_agents/feature-requests/scholar-openathens-authentication.md
  44   5     async def authenticate_async(self, username: str, password: str) -> Session:
  47   5     async def download_with_auth_async(self, url: str, session: Session) -> bytes:
  55   1 async def download_pdf_async(self, doi: str) -> Optional[Path]:

File: docs/zenrows_official/with_playwright.md
  60   1 async def scrape_asyncr_async():
 111   1 async def scrape_asyncr_async(url):

File: docs/from_user/suggestions.md
  48   1 async def main():

File: search_engine/_BaseSearchEngine.py

...
```


### `./docs/from_user/suggestions.md`

```markdown

Of course. It's easy to get lost when an automated process creates many files. Your agent is working hard but has made one critical mistake that is causing all the timeouts and confusion.

Here is the suggestion to get everything working.

The Core Problem: Separating Authentication from Action
Your agent's critical mistake is that it's running the authentication in one script, and then trying to run the DOI resolution in a separate, second script.

An authenticate_async session (your login "cookie") only exists for the script that creates it. When the first script finishes, the session is gone. The second script starts fresh, unauthenticate_async, and immediately hits the login wall, causing it to time out.

Analogy: It's like buying a concert ticket 🎟️ online, closing your browser, then show_asyncing up to the concert gate with nothing in your hand and expecting them to know you bought a ticket. You need to use the ticket (the authenticate_async session) in the same process where you acquired it.

The Solution: One Consolidated Script
The solution is to use a single script that performs both steps in the correct order:

Authenticate first.

Then, using that same authenticate_async session, resolve the DOIs.

Please have your agent delete the other test scripts (check_doi_resolution.py, interactive_auth_and_resolve.py, debug_auth_session.py, etc.) 🗑️.

Use this single, clean script as the correct way forward.

New File Suggestion: run_full_workflow.py
Python

#!/usr/bin/env python
"""
A single, consolidated script to perform the full workflow:
1. Authenticate using a local, visible browser with ZenRows proxy.
2. Resolve a list of DOIs using the authenticate_async session.
"""
import os
import asyncio
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import ScholarAuthManager
from scitex import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main execution function."""
    
    # 1. Initialize the Authentication Manager
    # This will use the local browser + ZenRows proxy method.
    auth_manager = ScholarAuthManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )

...
```


### `./docs/sample_data/openaccess.json`

```json
{
  "open_access_papers": [
    {
      "doi": "10.3389/fnins.2019.00573",
      "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations",
      "journal": "Frontiers in Neuroscience",
      "year": 2019,
      "note": "Frontiers journals are open access"
    },
    {
      "doi": "10.1371/journal.pcbi.1008739",
      "title": "Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement",
      "journal": "PLoS Computational Biology",
      "year": 2020,
      "note": "PLoS journals are open access"
    },
    {
      "doi": "10.1523/ENEURO.0494-18.2019",
      "title": "Different Methods to Estimate the Phase of Neural Rhythms",
      "journal": "eNeuro",
      "year": 2023,
      "note": "eNeuro is open access"
    },
    {
      "doi": "10.1038/s41598-019-48870-2",
      "title": "Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations",
      "journal": "Scientific Reports",
      "year": 2019,
      "note": "Scientific Reports is open access"
    },
    {
      "doi": "10.3390/e23081016",
      "title": "Estimating Phase Amplitude Coupling between Neural Oscillations Based on Permutation and Entropy",
      "journal": "Entropy",
      "year": 2021,
      "note": "MDPI Entropy is open access"
    },
    {
      "doi": "10.3390/brainsci12020274",
      "title": "The Functional Interactions between Cortical Regions through Theta-Gamma Coupling",
      "journal": "Brain Sciences",
      "year": 2022,
      "note": "MDPI Brain Sciences is open access"
    },
    {
      "doi": "10.3389/fnhum.2010.00191",
      "title": "Shifts in Gamma Phase–Amplitude Coupling Frequency from Theta to Alpha",
      "journal": "Frontiers in Human Neuroscience",
      "year": 2010,
      "note": "Frontiers journals are open access"

...
```


### `./docs/sample_data/PAYWALLED.json`

```json
{
  "paywalled_papers": [
    {
      "doi": "10.1016/j.neubiorev.2020.07.005",
      "title": "Generative models, linguistic communication and active inference",
      "journal": "Neuroscience and Biobehavioral Reviews",
      "year": 2020,
      "publisher": "Elsevier",
      "note": "Elsevier journal, typically paywalled"
    },
    {
      "doi": "10.1016/j.tics.2010.09.001",
      "title": "The functional role of cross-frequency coupling",
      "journal": "Trends in Cognitive Sciences",
      "year": 2010,
      "publisher": "Elsevier",
      "note": "High-impact Elsevier journal"
    },
    {
      "doi": "10.1016/j.conb.2014.08.002",
      "title": "Untangling cross-frequency coupling in neuroscience",
      "journal": "Current Opinion in Neurobiology",
      "year": 2014,
      "publisher": "Elsevier",
      "note": "Elsevier review journal"
    },
    {
      "doi": "10.1152/jn.00106.2010",
      "title": "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies",
      "journal": "Journal of Neurophysiology",
      "year": 2010,
      "publisher": "American Physiological Society",
      "note": "Physiology journal, typically paywalled"
    },
    {
      "doi": "10.1016/j.jneumeth.2014.01.003",
      "title": "Toward a proper estimation of phase–amplitude coupling in neural oscillations",
      "journal": "Journal of Neuroscience Methods",
      "year": 2014,
      "publisher": "Elsevier",
      "note": "Elsevier methods journal"
    },
    {
      "doi": "10.1002/hbm.26190",
      "title": "Direct modulation index: A measure of phase amplitude coupling",
      "journal": "Human Brain Mapping",
      "year": 2022,
      "publisher": "Wiley",
      "note": "Wiley journal, typically paywalled"
    },

...
```


### `./docs/STORAGE_ARCHITECTURE.md`

```markdown
# SciTeX Scholar Storage Architecture

## Summary: No More Manual pdfs Directory!

**Answer to your question**: Yes, you're correct! With the new unified CLI and MASTER storage architecture, **we don't need the manual `pdfs` directory anymore**.

## Old Structure (No Longer Needed)
```
neurovista/
├── pdfs/                     ❌ Manual PDF storage - NOT NEEDED
│   ├── 10.1093_brain_awx098.pdf
│   └── 10.1371_journal.pone.0081920.pdf
└── DOI_10.1038_xxx           ❌ DOI-based symlinks
```

## New Structure (Automatic & Organized)
```
library/
├── MASTER/
│   ├── AECB5227/             # Hash-based ID from DOI
│   │   ├── metadata.json     # Complete metadata
│   │   └── Cook-2013-LancetNeurology.pdf  # Properly named PDF
│   └── B4030896/
│       ├── metadata.json
│       └── Grigorovsky-2020-BrainCommunications.pdf
└── neurovista/
    ├── Cook-2013-LancetNeurology -> ../MASTER/AECB5227  ✅ Human-readable
    └── Grigorovsky-2020-BrainCommunications -> ../MASTER/B4030896

```

## Key Improvements

### 1. **Centralized MASTER Storage**
- All PDFs stored once in MASTER/{8-char-hash}/
- No duplicates across projects
- Consistent metadata.json tracking

### 2. **Human-Readable Symlinks**
- Format: `Author-Year-Journal` (e.g., `Cook-2013-LancetNeurology`)
- NOT: `DOI_10.1038_xxx` format
- Easy to browse and understand

### 3. **Automatic Management**
```bash
# Everything handled automatically:
python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download
```

## Migration from Old Structure

...
```


### `./docs/SUMMARY.md`

```markdown
# SciTeX Scholar - Summary of Updates

## ✅ What We've Accomplished

### 1. **Unified CLI Interface**
```bash
# Everything in one flexible command
python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download

# Instead of rigid subcommands
python -m scitex.scholar enrich --input papers.bib  # OLD - NOT NEEDED
```

### 2. **MASTER Storage Architecture**
```
library/
├── MASTER/                           # Centralized storage
│   ├── AECB5227/                    # Hash from DOI
│   │   ├── DOI_10.1038_xxx.pdf     # Original filename preserved
│   │   └── metadata.json           # Full enriched metadata
│   └── B4030896/
│       ├── DOI_10.1093_xxx.pdf
│       └── metadata.json
└── project_name/
    ├── Author-Year-Journal -> ../MASTER/AECB5227  # Human-readable symlinks
    └── Author2-Year2-Journal2 -> ../MASTER/B4030896
```

**Key Points:**
- **No more manual `pdfs` directory** - everything automated
- **PDF filenames preserved** as `DOI_xxx.pdf` for tracking
- **Symlinks use human-readable names** like `Cook-2013-LancetNeurology`
- **Metadata.json contains full enriched data**

### 3. **Enhanced Filtering**
```python
# Papers object now supports:
papers.filter(
    min_citations=100,
    min_impact_factor=10.0,
    year_min=2020,
    has_pdf=True
)
```

### 4. **Improved Help System**
```bash
python -m scitex.scholar --help
# Shows:
# - Organized argument groups
```

...
```


### `./docs/zenrows_official/captcha_integration.md`

```markdown

JavaScript Rendering (Headless browser)
Many modern websites use JavaScript to dynamically load content, meaning that the data you need might not be available in the initial HTML response. To handle such cases, you can use our JavaScript rendering feature, which simulates a real browser environment to fully load and render the page before extracting the data.
​
Enabling JavaScript Rendering
To activate JavaScript rendering, append js_render=true to the request. This tells our system to process the page using a headless browser, allowing you to scrape_async content that is loaded dynamically by JavaScript.
Enabling JavaScript rendering incurs a higher cost than standard requests. Five times the cost of a standard request

Python

Node.js

Java

PHP

Go

Ruby

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://httpbin.io/anything'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
​
Features Requiring JavaScript Rendering
Several features rely on js_render being set to true. These include:
Wait: Introduces a delay before proceeding with the request. Useful for scenarios where you need to allow time for JavaScript to load content.
Wait For: Waits for a specific element to appear on the page before proceeding. When used with js_render, this parameter will cause the request to fail if the selector is not found.
JSON Response: Retrieves the rendered page content in JSON format, including data loaded dynamically via JavaScript.
Block Resources: Block specific types of resources from being loaded.
JavaScript Instructions: Allows you to execute custom JavaScript code on the page. This includes additional parameters.
Screenshot: Capture an above-the-fold screenshot of the target page by adding screenshot=true to the request.
​
Wait Milliseconds
For websites that take longer to load, you might need to introduce a fixed delay to ensure that all content is fully loaded before retrieving the HTML. You can specify this delay in milliseconds using the wait=10000 parameter.
In this example, wait=10000 will cause ZenRows to wait for 10,000 milliseconds (or 10 seconds) before returning the HTML content. You can adjust this value based on your needs, with a maximum total allowable wait time of 30 seconds.

...
```


### `./docs/zenrows_official/FAQ.md`

```markdown


ZenRows Docs home pagedark logo
Search...



Navigation
Frequently Asked Questions
Frequently Asked Questions
Can I Get Cookies from the Responses?

Headers, including cookies, returned by the target website are prefixed with Zr- and included in all our responses.
Suppose you are scraping a website that requires session cookies for authentication. By capturing the Zr-Cookies header from the initial response, you can include these cookies in your subsequent requests to maintain the session and access authenticate_async content.

Copy

Ask AI
Zr-Content-Encoding: gzip
Zr-Content-Type: text/html
Zr-Cookies: _pxhd=Bq7P4CRaW1B...
Zr-Final-Url: https://www.example.com/
You could send those cookies in a subsequent request as Custom Headers and also use session_id to keep the same IP for up to 10 minutes.
By following this process, you can handle sessions and access restricted areas of the website seamlessly.
Can I Logging In/Register and Access Content Behind Login?

If you need to scrape_async data from a website that requires login authentication, you can log in or register and access content behind a login. However, due to privacy and legal reasons, we offer limited support for these cases.
Login and registration work like regular forms and can be treated as such. There are two main methods to send forms:
Send POST requests.
Fill in and submit a form using JavaScript Instructions.

Copy

Ask AI
{"fill": [".input-selector", "website_username"]} // Fill the username input
{"fill": [".input-selector", "website_password"]} // Fill the password input
All requests will return headers, including the session cookies. By using these cookies in subsequent requests, you can operate as a logged-in user. Additionally, you can include a Session ID to maintain the same IP address for up to 10 minutes.
ZenRows is a scraping tool, not a VPN. If your goal is to log in once and browse the internet with the same IP, you may need a different service.
Can I Maintain Sessions/IPs Between Requests

Suppose you need to perform multiple actions on a website that requires maintaining the same session/IP. You can use the Session ID parameter to maintain the same IP between requests. ZenRows will store the IP for 10 minutes from the first request with that ID. All subsequent requests with that ID will use the same IP.
However, session_id will not store any other request data, such as session cookies. You will receive those cookies as usual and can decide which ones to send on the next request.
Multiple Session IDs can run concurrently, with no limit to the number of sessions.
Can I Run the API/Proxy in Multiple Threads to Improve Speed?

Each plan comes with a concurrency limit. For example, the Developer plan allows 10 concurrent requests, meaning you can have up to 10 requests running simultaneously, significantly improving speed.
Sending requests above that limit will result in a 429 Too Many Requests error.
We wrote a guide on using concurrency that provides more details, including examples in Python and JavaScript. The same principles apply to other languages and libraries.
Can I Send/Submit Forms?


...
```


### `./docs/zenrows_official/final_url.md`

```markdown

Introduction to the Universal Scraper API
The ZenRows® Universal Scraper API is a versatile tool designed to simplify and enhance the process of extracting data from websites. Whether you’re dealing with static or dynamic content, our API provides a range of features to meet your scraping needs efficiently.
With Premium Proxies, ZenRows gives you access to over 55 million residential IPs from 190+ countries, ensuring 99.9% uptime and highly reliable scraping sessions. Our system also handles advanced fingerprinting, header rotation, and IP management, enabling you to scrape_async even the most protected sites without needing to manually configure these elements.
ZenRows makes it easy to bypass complex anti-bot measures, handle JavaScript-heavy sites, and interact with web elements dynamically — all with the right features enabled.
​
Key Features
​
JavaScript Rendering
Render JavaScript on web pages using a headless browser to scrape_async dynamic content that traditional methods might miss.
When to use: Use this feature when targeting modern websites built with JavaScript frameworks (React, Vue, Angular), single-page applications (SPAs), or any site that loads content dynamically after the initial page load.
Real-world scenarios:
E-commerce product listings that load items as you scroll
Dashboards and analytics platforms that render charts/data with JavaScript
Social media feeds that dynamically append content
Sites that hide_async certain content until JavaScript is rendered
Additional options:
Wait times to ensure elements are fully loaded
Interaction with the page to click buttons, fill forms, or scroll
Screenshot capabilities for visual verification
CSS-based extraction of specific elements
​
Premium Proxies
Leverage a vast network of residential IP addresses across 190+ countries, ensuring a 99.9% uptime for uninterrupted scraping.
When to use: Essential for accessing websites with sophisticated anti-bot systems, geo-restricted content, or when you consistently encounter blocks with standard datacenter IPs.
Real-world scenarios:
Scraping major e-commerce platforms (Amazon, Walmart)
Accessing real estate listings (Zillow, Redfin)
Gathering pricing data from travel sites (Expedia, Booking.com)
Collecting data from financial or investment platforms
Additional options:
Geolocation selection to access region-specific content
Automatic IP rotation to prevent detection
​
Custom Headers
Add custom HTTP headers to your requests for more control over how your requests appear to target websites.
When to use: When you need to mimic specific browser behavior, set cookies, or a referer.
Real-world scenarios:
Setting language preferences to get content in specific languages
Adding a referer to avoid being blocked by bot detection systems
​
Session Management
Use a session ID to maintain the same IP address across multiple requests for up to 10 minutes.
When to use: When scraping multi-page flows or processes that require maintaining the same IP across multiple requests.
Real-world scenarios:
Multi-step forms processes
Maintaining consistent session for search results and item visits
​
Advanced Data Extraction
Extract only the data you need with CSS selectors or automatic parsing.

...
```


### `./docs/zenrows_official/with_playwright.md`

```markdown

Integrating ZenRows Scraping Browser with Playwright
Learn to extract data from any website using ZenRows’ Scraping Browser with Playwright. This guide walks you through creating your first browser-based scraping request that can handle complex JavaScript-heavy sites with full browser automation.
ZenRows’ Scraping Browser provides cloud-based Chrome instances you can control using Playwright. Whether dealing with dynamic content, complex user interactions, or sophisticated anti-bot protection, you can get started in minutes with Playwright’s powerful automation capabilities.
​
1. Set Up Your Project
​
Set Up Your Development Environment
Before diving in, ensure you have the proper development environment and Playwright installed. The Scraping Browser works seamlessly with both Python and Node.js versions of Playwright.
While previous versions may work, we recommend using the latest stable versions for optimal performance and security.
Python
Node.js
Python 3+ installed (latest stable version recommended). Using an IDE like PyCharm or Visual Studio Code with the Python extension is recommended.

Copy

Ask AI
# Install Python (if not already installed)
# Visit https://www.python.org/downloads/ or use package managers:

# macOS (using Homebrew)
brew install python

# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Windows (using Chocolatey)
choco install python

# Install Playwright
pip install playwright
playwright install
If you need help setting up your environment, check out our detailed Playwright web scraping guide
​
Get Your API Key and Connection URL
Sign Up for a free ZenRows account and get your API key from the Scraping Browser dashboard. You’ll need this key to authenticate_async your WebSocket connection.
​
2. Make Your First Request
Start with a simple request to understand how the Scraping Browser works with Playwright. We’ll use the E-commerce Challenge page to demonstrate how to connect to the browser and extract the page title.

Python

Node.js

Copy

Ask AI
# pip install playwright
import asyncio
from playwright.async_api import async_playwright

...
```


### `./download/__init__.py`

```python
from .ScholarPDFDownloader import ScholarPDFDownloader

...
```


### `./download/ParallelPDFDownloader.py`

```python
#!/usr/bin/env python3
"""Parallel PDF downloader with multiple Chrome instances for improved performance."""

import asyncio
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import random

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.browser.local.ScholarBrowserManager import ScholarBrowserManager
from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader
from scitex.scholar.storage._LibraryManager import LibraryManager

# Try to import screenshot-enabled downloader
try:
    from scitex.scholar.download.ScholarPDFDownloaderWithScreenshots import ScholarPDFDownloaderWithScreenshots
    USE_SCREENSHOTS = True
except ImportError:
    USE_SCREENSHOTS = False

logger = logging.getLogger(__name__)

# Log screenshot availability at module load
if USE_SCREENSHOTS:
    logger.info("Screenshot-enabled PDF downloader is available")
else:
    logger.warning("Screenshot-enabled PDF downloader is NOT available")


# Publisher-specific rate limits to avoid detection
PUBLISHER_LIMITS = {
    "elsevier.com": {"max_parallel": 2, "delay": 15, "retry_delay": 30},
    "sciencedirect.com": {"max_parallel": 2, "delay": 15, "retry_delay": 30},
    "nature.com": {"max_parallel": 3, "delay": 10, "retry_delay": 20},
    "springer.com": {"max_parallel": 3, "delay": 10, "retry_delay": 20},
    "ieee.org": {"max_parallel": 2, "delay": 20, "retry_delay": 40},
    "wiley.com": {"max_parallel": 2, "delay": 15, "retry_delay": 30},
    "plos.org": {"max_parallel": 5, "delay": 5, "retry_delay": 10},
    "frontiersin.org": {"max_parallel": 4, "delay": 8, "retry_delay": 15},
    "mdpi.com": {"max_parallel": 4, "delay": 8, "retry_delay": 15},
    "arxiv.org": {"max_parallel": 5, "delay": 3, "retry_delay": 5},
    "biorxiv.org": {"max_parallel": 4, "delay": 5, "retry_delay": 10},
    "default": {"max_parallel": 3, "delay": 10, "retry_delay": 20}

...
```


### `./download/README.md`

```markdown

## Science Direct
● The key issue is that the authenticated PDF URLs (from pdf.sciencedirectassets.com) contain session-specific tokens that are
  only valid within the browser context where they were generated. When you try to access them directly in a new session, they
  redirect back to the publisher page.

  The solution is to download the PDF within the same browser context where we obtained the URL. Let me check how the
  ScholarPDFDownloader handles this:


## Usage

``` python
async def main_async():
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarURLFinder,
    )

    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=ScholarAuthManager(),
        use_zenrows_proxy=False,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )
    pdf_downloader = ScholarPDFDownloader(context)

    # Parameters
    PDF_URL = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"
    OUTPUT_PATH = "/tmp/hippocampal_ripples-by-stealth.pdf"

    # Main
    saved_path = await pdf_downloader.download_from_url(
        PDF_URL,
        output_path=OUTPUT_PATH,
    )

    if saved_path:
        logger.success(f"PDF downloaded successfully to: {saved_path}")
    else:
        logger.error("Failed to download PDF")

import asyncio
asyncio.run(main_async())
```


...
```


### `./download/ScholarPDFDownloader.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-04 09:50:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import base64
import hashlib
from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import BrowserContext, Page, async_playwright

from scitex import logging
from scitex.scholar import ScholarConfig, ScholarURLFinder
from scitex.scholar.browser import (
    click_center_async,
    click_download_button_from_chrome_pdf_viewer_async,
    detect_pdf_viewer_async,
    show_grid_async,
    show_popup_message_async,
)
from scitex.scholar.browser.local.utils._HumanBehavior import HumanBehavior

logger = logging.getLogger(__name__)

# Timing differences:
# 1. `timeout=60_000` - Maximum wait time for operation to complete
# 2. `page.wait_for_timeout(5_000)` - Fixed delay (like sleep but async)
# 3. `time.sleep()` - Blocks entire thread (avoid in async code)


class ScholarPDFDownloader:
    def __init__(
        self,
        context: BrowserContext,
        config: ScholarConfig = None,
        use_cache=False,
    ):
        self.config = config if config else ScholarConfig()
        self.context = context
        self.url_finder = ScholarURLFinder(self.context, config=config)
        self.use_cache = self.config.resolve(
            "use_cache_pdf_downloader", use_cache

...
```


### `./download/ScholarPDFDownloaderWithScreenshots.py`

```python
#!/usr/bin/env python3
"""Enhanced PDF downloader with screenshot capture capabilities for debugging."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union, Dict, Tuple

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader

logger = logging.getLogger(__name__)


class ScholarPDFDownloaderWithScreenshots(ScholarPDFDownloader):
    """PDF downloader that captures screenshots at intervals and on failure."""

    def __init__(
        self,
        context: BrowserContext,
        config: ScholarConfig = None,
        use_cache=False,
        screenshot_interval: float = 2.0,  # seconds between screenshots
        capture_on_failure: bool = True,
        capture_during_success: bool = True,  # Always capture for documentation
    ):
        super().__init__(context, config, use_cache)
        self.screenshot_interval = screenshot_interval
        self.capture_on_failure = capture_on_failure
        self.capture_during_success = capture_during_success
        self.screenshot_tasks = {}  # Track screenshot tasks per page

    def _get_screenshot_dir(self, doi: str = None, paper_id: str = None) -> Path:
        """Get the screenshot directory for a paper.

        WARNING: paper_id should always be provided to ensure consistency.
        Generating paper_id from DOI alone can cause ID mismatches.
        """
        library_dir = self.config.get_library_dir()

        if paper_id:
            # Use paper ID directly if provided (PREFERRED)
            screenshot_dir = library_dir / "MASTER" / paper_id / "screenshots"
        elif doi:
            # DEPRECATED: Generating paper ID from DOI alone
            # This can cause inconsistencies - caller should use PathManager._generate_paper_id()
            logger.warning(

...
```


### `./engines/individual/ArXivEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:01:18 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/ArXivEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Dict, List, Optional, Union

import feedparser
import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)
import json


class ArXivEngine(BaseDOIEngine):
    """ArXiv engine for open access papers."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()
        self.email = email
        self.base_url = "http://export.arxiv.org/api/query"

    def _get_user_agent(self) -> str:
        """Get ArXiv-specific user agent."""
        return f"SciTeX Scholar (mailto:{self.email})"

    @property
    def name(self) -> str:
        return "arXiv"

    @property

...
```


### `./engines/individual/_BaseDOIEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 23:54:23 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/_BaseDOIEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
from typing import Dict

"""
Abstract base class for DOI engines with enhanced rate limit handling.

This module defines the interface that all DOI engines must implement,
including automatic rate limit detection and retry mechanisms.
"""

import asyncio
import re
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import requests

from scitex import logging

from ..utils import (
    PubMedConverter,
    TextNormalizer,
    URLDOIExtractor,
    standardize_metadata,
)

logger = logging.getLogger(__name__)


class BaseDOIEngine(ABC):
    """Abstract base class for DOI engines with enhanced rate limit handling."""

    def __init__(self, email: str = "research@example.com"):
        """Initialize base engine."""
        self.email = email
        self.rate_limit_handler = None  # Will be injected by SingleDOIResolver
        self.last_request_time = 0.0
        self._request_count = 0

...
```


### `./engines/individual/CrossRefEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 07:29:03 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/individual/CrossRefEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
from typing import Dict, List, Optional, Union

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class CrossRefEngine(BaseDOIEngine):
    """CrossRef DOI engine - no API key required, generous rate limits."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__(email)
        self.base_url = "https://api.crossref.org/works"

    @property
    def name(self) -> str:
        return "CrossRef"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=5,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """When doi is provided, all the information other than doi is ignored"""
        if doi:

...
```


### `./engines/individual/CrossRefLocalEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 07:29:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/individual/CrossRefLocalEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
import urllib.parse
from typing import Dict, List, Optional, Union

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class CrossRefLocalEngine(BaseDOIEngine):
    """CrossRef Local Engine using local Django API"""

    def __init__(
        self,
        email: str = "research@example.com",
        api_url: str = "http://127.0.0.1:3333",
    ):
        super().__init__(email)
        self.api_url = api_url.rstrip("/")

    @property
    def name(self) -> str:
        return "CrossRefLocal"

    @property
    def rate_limit_delay(self) -> float:
        return 0.01

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=1,

...
```


### `./engines/individual/__init__.py`

```python
from .ArXivEngine import ArXivEngine
from .CrossRefEngine import CrossRefEngine
from .CrossRefLocalEngine import CrossRefLocalEngine
from .OpenAlexEngine import OpenAlexEngine
from .PubMedEngine import PubMedEngine
from .SemanticScholarEngine import SemanticScholarEngine
from .URLDOIEngine import URLDOIEngine

...
```


### `./engines/individual/OpenAlexEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:00:41 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/OpenAlexEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
from typing import Dict, List, Optional, Union

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class OpenAlexEngine(BaseDOIEngine):
    """OpenAlex - free and open alternative to proprietary databases."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__(email)
        self.base_url = "https://api.openalex.org/works"

    @property
    def name(self) -> str:
        return "OpenAlex"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """When doi is provided, all the information other than doi is ignored"""
        if doi:

...
```


### `./engines/individual/PubMedEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:00:20 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/PubMedEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import time
from typing import Any, Dict

"""
PubMed DOI engine implementation.

This module provides DOI resolution through the PubMed/NCBI E-utilities API.
"""

import json
import xml.etree.ElementTree as ET
from typing import List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class PubMedEngine(BaseDOIEngine):
    """PubMed DOI engine - free, no API key required."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()  # Initialize base class to access utilities
        self.email = email
        self._session = None

    @property
    def name(self) -> str:
        return "PubMed"

...
```


### `./engines/individual/SemanticScholarEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:00:02 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/SemanticScholarEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
from functools import lru_cache
from typing import Dict, List, Optional, Union

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class SemanticScholarEngine(BaseDOIEngine):
    """Combined Semantic Scholar engine with enhanced features."""

    def __init__(
        self, email: str = "research@example.com", api_key: str = None
    ):
        super().__init__(email)
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self._rate_limit_delay = 0.5 if self.api_key else 1.2

    def _get_user_agent(self) -> str:
        return f"SciTeX/1.0 (mailto:{self.email})"

    @property
    def name(self) -> str:
        return "Semantic_Scholar"

...
```


### `./engines/individual/URLDOIEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 23:59:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/URLDOIEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import random
import re
import time
from typing import Dict, List, Optional, Union

import requests

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class URLDOIEngine(BaseDOIEngine):
    """Extract DOIs from URL fields - immediate recovery for papers."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__(email)
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

        self.ieee_patterns = [
            r"ieeexplore\.ieee\.org/document/(\d+)",
            r"ieeexplore\.ieee\.org/abstract/document/(\d+)",
            r"ieeexplore\.ieee\.org/stamp/stamp\.jsp\?arnumber=(\d+)",
        ]

        self.pubmed_patterns = [
            r"pubmed/(\d+)",
            r"ncbi\.nlm\.nih\.gov/pubmed/(\d+)",
            r"PMID:(\d+)",
        ]

        self.semantic_patterns = [
            r"semanticscholar\.org/paper/([^/?]+)",
            r"CorpusId:(\d+)",
        ]

...
```


### `./engines/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 15:38:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/engines/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
DOI engines for the SingleDOIResolver.

This module provides different engines for resolving DOIs including
CrossRef, PubMed, OpenAlex, and Semantic Scholar.
"""

from .ScholarEngine import ScholarEngine

# EOF

...
```


### `./engines/JCRImpactFactorEngine.py`

```python
#!/usr/bin/env python3
"""JCR Impact Factor Engine using local SQLite database."""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from scitex import logging

logger = logging.getLogger(__name__)

class JCRImpactFactorEngine:
    """Fast impact factor lookups using JCR database."""

    def __init__(self):
        """Initialize with JCR database path."""
        self.name = "JCR Impact Factor"

        # Path to the JCR database
        self.db_path = Path(__file__).parent.parent / "externals" / "impact_factor_jcr" / "impact_factor" / "data" / "impact_factor.sqlite3"

        if not self.db_path.exists():
            logger.warning(f"JCR database not found at {self.db_path}")
            self.db_path = None

    def get_impact_factor(self, journal_name: str) -> Optional[float]:
        """Get impact factor for a journal.

        Args:
            journal_name: Journal name to search for

        Returns:
            Impact factor if found, None otherwise
        """
        if not self.db_path:
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Try exact match first (case-insensitive)
                cursor.execute(
                    "SELECT factor FROM factor WHERE LOWER(journal) = LOWER(?) LIMIT 1",
                    (journal_name,)
                )
                result = cursor.fetchone()

                if result:
                    return float(result[0]) if result[0] else None


...
```


### `./engines/README.md`

```markdown

## Usage
``` python
import asyncio
from pprint import pprint
from scitex.scholar import ScholarEngine

async def main_async():
    # Query
    TITLE = "Attention is All You Need"
    DOI = "10.1038/nature14539"

    # Example: Unified Engine
    engine = ScholarEngine()
    outputs = {}

    # Search by Title
    outputs["metadata_by_title"] = await engine.search_async(
        title=TITLE,
    )
     
    # Search by DOI
    outputs["metadata_by_doi"] = await engine.search_async(
        doi=DOI,
    )

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)

asyncio.run(main_async())
```


...
```


### `./engines/ScholarEngine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 00:09:04 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/ScholarEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import hashlib
import re
import time
from typing import Dict, List

from tqdm import tqdm

from scitex import logging
from scitex.scholar import ScholarConfig

from .individual import (
    ArXivEngine,
    CrossRefEngine,
    CrossRefLocalEngine,
    OpenAlexEngine,
    PubMedEngine,
    SemanticScholarEngine,
    URLDOIEngine,
)

logger = logging.getLogger(__name__)


class ScholarEngine:
    """Aggregates metadata from multiple engines for enrichment."""

    def __init__(
        self,
        engines: List[str] = None,
        config: ScholarConfig = None,
        use_cache=True,
        clear_cache=False,
    ):
        self.config = config if config else ScholarConfig()
        self.engines = self.config.resolve("engines", engines)
        self.use_cache = self.config.resolve("use_cache_search", use_cache)
        self._engine_instances = {}
        self.rotation_manager = None

...
```


### `./engines/utils/__init__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 08:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/utils/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from ._PubMedConverter import PubMedConverter, pmid2doi
# from ._RateLimitHandler import RateLimitHandler
from ._TextNormalizer import TextNormalizer
from ._URLDOIExtractor import URLDOIExtractor
from ._standardize_metadata import standardize_metadata, BASE_STRUCTURE
from ._metadata2bibtex import metadata2bibtex
from ...storage import BibTeXHandler

__all__ = [
    "PubMedConverter",
    "pmid2doi",
    # "RateLimitHandler",
    "TextNormalizer",
    "URLDOIExtractor",
    "standardize_metadata",
    "metadata2bibtex",
    "BASE_STRUCTURE",
    "BibTeXHandler",
]


# EOF

...
```


### `./engines/utils/_metadata2bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 22:12:13 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/utils/_metadata2bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

def metadata2bibtex(metadata, key=None):
    """Convert complete metadata structure to BibTeX entry."""
    if not key:
        key = _generate_bibtex_key(metadata)

    entry_type = _determine_entry_type(metadata)
    lines = [f"@{entry_type}{{{key},"]

    # Core fields
    _add_bibtex_field(lines, "title", metadata["basic"]["title"])
    _add_bibtex_authors(lines, metadata["basic"]["authors"])
    _add_bibtex_field(lines, "year", metadata["basic"]["year"])

    # Publication details
    _add_bibtex_field(lines, "journal", metadata["publication"]["journal"])
    _add_bibtex_field(lines, "volume", metadata["publication"]["volume"])
    _add_bibtex_field(lines, "pages", _format_pages(metadata["publication"]))

    # Identifiers
    _add_bibtex_field(lines, "doi", metadata["id"]["doi"])
    _add_bibtex_arxiv(lines, metadata["id"]["arxiv_id"])

    # Optional fields
    _add_bibtex_field(lines, "abstract", metadata["basic"]["abstract"])

    lines.append("}")
    return "\n".join(lines)


def _generate_bibtex_key(metadata):
    """Generate BibTeX key from metadata."""
    authors = metadata["basic"]["authors"]
    year = metadata["basic"]["year"] or "0000"

    if authors:
        first_author = authors[0].split()[-1].lower()
    else:
        first_author = "unknown"


...
```


### `./engines/utils/_PubMedConverter.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 05:35:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/utils/_PubMedConverter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PubMedConverter: Convert PubMed IDs (PMIDs) to DOIs using NCBI E-utilities API.

This utility provides DOI recovery for papers that have PubMed IDs
but no explicit DOI field. Uses the reliable government API.

Examples:
    PMID: 25821343 → DOI: 10.1038/ng.3234
    PMID: 23962674 → DOI: 10.1126/science.1241224
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from scitex import logging
from scitex.scholar import ScholarConfig

logger = logging.getLogger(__name__)


class PubMedConverter:
    """Convert PubMed IDs to DOIs using NCBI E-utilities API."""

    # NCBI E-utilities endpoints
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    EFETCH_URL = f"{BASE_URL}/efetch.fcgi"

    # Rate limiting (NCBI allows 3 requests/second without API key)
    REQUEST_DELAY = 0.34  # ~3 requests per second

    # PubMed ID patterns
    PMID_PATTERNS = [

...
```


### `./engines/utils/_standardize_metadata.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 23:18:02 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/utils/_to_complete_metadata_structure.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from collections import OrderedDict

BASE_STRUCTURE = OrderedDict(
    [
        (
            "id",
            OrderedDict(
                [
                    ("doi", None),
                    ("doi_engines", []),
                    ("arxiv_id", None),
                    ("arxiv_id_engines", []),
                    ("pmid", None),
                    ("pmid_engines", []),
                    ("semantic_id", None),
                    ("semantic_id_engines", []),
                    ("ieee_id", None),
                    ("ieee_id_engines", []),
                    ("scholar_id", None),
                    ("scholar_id_engines", []),
                ]
            ),
        ),
        (
            "basic",
            OrderedDict(
                [
                    ("title", None),
                    ("title_engines", []),
                    ("authors", None),
                    ("authors_engines", []),
                    ("year", None),
                    ("year_engines", []),
                    ("abstract", None),
                    ("abstract_engines", []),
                    ("keywords", None),
                    ("keywords_engines", []),
                    ("type", None),
                    ("type_engines", []),

...
```


### `./engines/utils/_TextNormalizer.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 09:27:59 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/utils/_TextNormalizer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
TextNormalizer: Fix LaTeX encoding and Unicode issues for better search accuracy.

This utility normalizes text to improve matching accuracy when searching
academic databases that may have different encoding representations.

Examples:
    H{\"u}lsemann → Hülsemann
    Dvořák → Dvorak (optional ASCII fallback)
    García-López → Garcia-Lopez (optional ASCII fallback)
    {\\textquoteright} → '
"""

import re
import string
import unicodedata
from typing import Dict, List

from scitex import logging

logger = logging.getLogger(__name__)


class TextNormalizer:
    """Normalize text by fixing LaTeX encoding and Unicode issues."""

    # LaTeX to Unicode mappings
    LATEX_TO_UNICODE = {
        # Accented characters
        r"\{\\\"a\}": "ä",
        r"\{\\\"A\}": "Ä",
        r"\{\\\"e\}": "ë",
        r"\{\\\"E\}": "Ë",
        r"\{\\\"i\}": "ï",
        r"\{\\\"I\}": "Ï",
        r"\{\\\"o\}": "ö",
        r"\{\\\"O\}": "Ö",
        r"\{\\\"u\}": "ü",
        r"\{\\\"U\}": "Ü",

...
```


### `./engines/utils/_URLDOIExtractor.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 06:25:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/utils/_URLDOIExtractor.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URLDOIEngine: Extract DOIs directly from URL fields in BibTeX entries.

This utility provides immediate DOI recovery for papers that have
DOI URLs in their URL field but no explicit DOI field.

Examples:
    https://doi.org/10.1002/hbm.26190 → 10.1002/hbm.26190
    http://dx.doi.org/10.1038/nature12373 → 10.1038/nature12373
    https://www.doi.org/10.1126/science.aao0702 → 10.1126/science.aao0702
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from scitex import logging

logger = logging.getLogger(__name__)


class URLDOIExtractor:
    """Extract DOIs from URL fields with comprehensive pattern matching."""

    # DOI patterns for different URL formats
    DOI_URL_PATTERNS = [
        # Standard DOI URLs
        r"https?://(?:www\.)?doi\.org/(.+)",
        r"https?://dx\.doi\.org/(.+)",
        r"https?://(?:www\.)?dx\.doi\.org/(.+)",
        # Publisher-specific DOI URLs
        r"https?://doi\.wiley\.com/(.+)",
        r"https?://doi\.nature\.com/(.+)",
        r"https?://doi\.apa\.org/(.+)",
        # General DOI pattern in URLs (more permissive)
        r"(?:doi[\.:/]|DOI[\.:/])([0-9]{2}\.[0-9]{4,}/[^\s\?&#]+)",
    ]

    # Valid DOI pattern for validation

...
```


### `./enricher/ImpactFactorEnricher.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 17:05:21 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/enricher/ImpactFactorEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Does XYZ
  - Does XYZ
  - Does XYZ
  - Saves XYZ

Dependencies:
  - scripts:
    - /path/to/script1
    - /path/to/script2
  - packages:
    - package1
    - package2
IO:
  - input-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

  - output-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

(Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
"""

"""Imports"""
import sys
import argparse

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from stx.io import load_configs
# CONFIG = load_configs()

...
```


### `./examples/00_config.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:10:39 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/00_config.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates comprehensive ScholarConfig functionality
- Shows directory structure and path resolution methods
- Tests configuration cascade behavior (direct -> config -> env -> default)
- Displays storage statistics and maintenance capabilities
- Validates directory structure integrity

Dependencies:
- scripts:
  - None
- packages:
  - scitex

Input:
- Configuration files from scitex.scholar.config
- Environment variables with SCITEX_SCHOLAR_ prefix
- System Chrome profile (if exists)

Output:
- Console output showing configuration paths and values
- Directory structure visualization
- Storage statistics and maintenance results
"""

"""Imports"""
import argparse
from pathlib import Path

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
def demonstrate_basic_paths(config) -> None:
    """Show basic directory paths and creation.


...
```


### `./examples/01_auth.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 20:01:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/01_auth.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarAuthManager authentication workflow
- Shows authentication setup and status checking
- Validates authentication state for scholar access

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Authentication credentials from environment or interactive prompts
- Cached authentication tokens if available

Output:
- Console output showing authentication status
- Updated authentication cache
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def setup_authentication() -> bool:
    """Set up and validate ScholarAuthManager authentication.

    Example
    -------
    >>> auth_success = await setup_authentication()
    >>> print(f"Authentication successful: {auth_success}")

...
```


### `./examples/02_browser.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:00:58 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/02_browser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarBrowserManager usage with authentication
- Shows browser initialization and basic navigation
- Validates authenticated browser context creation

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Authentication credentials from environment or cache
- Chrome profile configuration

Output:
- Console output showing browser initialization status
- Opens browser window navigating to scitex.ai
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_browser_usage() -> bool:
    """Demonstrate browser manager with authentication.
    
    Returns
    -------
    bool
        True if successful, False otherwise

...
```


### `./examples/03_01-engine.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 19:24:28 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/03_01-engine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarEngine unified search capabilities
- Shows metadata retrieval by title and DOI
- Validates multi-engine aggregation results
- Displays comprehensive paper metadata structures

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Paper titles and DOIs for search queries
- Search engine configurations

Output:
- Console output with detailed metadata from multiple engines
- Structured metadata showing engine sources and aggregated results
"""

"""Imports"""
import argparse
import asyncio
import time
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def search_by_queries(
    title: str = None, doi: str = None, use_cache: bool = False
) -> dict:
    """Demonstrate unified search capabilities.

...
```


### `./examples/03_02-engine-for-bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 00:10:19 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/03_02-engine-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Parses BibTeX files and extracts academic paper titles
- Uses ScholarEngine to search for metadata of papers in batch
- Supports caching and sampling for efficient processing
- Saves metadata results as JSON with symbolic linking

Dependencies:
- scripts:
  - None
- packages:
  - scitex, numpy, asyncio

Input:
- ./data/scholar/openaccess.bib
- ./data/scholar/paywalled.bib
- ./data/scholar/pac.bib

Output:
- ./data/scholar/pac_metadata.json
- Console output of search results
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import numpy as _np

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def search_bibtex_metadata(
    bibtex_path: str, use_cache: bool = True, n_samples: int = None

...
```


### `./examples/04_01-url.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:02:27 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarURLFinder capabilities for PDF discovery
- Shows URL resolution through multiple methods (DOI, OpenURL, Zotero translators)
- Validates authenticated browser context for URL finding
- Displays comprehensive URL finding results

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- DOI for URL resolution
- Authenticated browser context

Output:
- Console output with discovered URLs and their sources
- PDF URLs from multiple discovery methods
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_url_finding(
    doi: str = None, use_cache: bool = False
) -> dict:
    """Demonstrate URL finding capabilities.


...
```


### `./examples/04_02-url-for-bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 06:52:13 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_02-url-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates batch URL finding workflow for BibTeX files
- Shows integration of ScholarEngine and ScholarURLFinder
- Processes multiple papers from BibTeX format efficiently
- Validates complete metadata-to-URL pipeline

Dependencies:
- scripts:
  - None
- packages:
  - scitex, numpy, asyncio

Input:
- ./data/scholar/openaccess.bib
- ./data/scholar/paywalled.bib
- ./data/scholar/pac.bib

Output:
- Console output showing metadata and URL finding progress
- Batch results for all papers in selected BibTeX file
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import numpy as np

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def process_bibtex_urls(
    bibtex_path: str,

...
```


### `./examples/04_02-url-for-dois.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: 04_02-url-for-dois.py
# ----------------------------------------

"""
Test URL finding for multiple DOIs from CSV.

This script loads DOIs from a CSV file and tests the URL finder
to check if the OpenURL resolution works across different publishers.
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

import scitex as stx
from scitex import logging
from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarURLFinder,
)

logger = logging.getLogger(__name__)


async def test_doi_url_finding(
    doi: str,
    url_finder: ScholarURLFinder,
    use_cache: bool = True
) -> Dict:
    """
    Test URL finding for a single DOI.
    
    Returns:
        dict with URL results and timing
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Testing DOI: {doi}")
        
        # Find URLs
        result = await url_finder.find_urls(doi=doi)
        

...
```


### `./examples/05_download_pdf.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 01:33:01 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/05_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarPDFDownloader capabilities
- Shows authenticated PDF downloading with multiple fallback methods
- Validates stealth browser integration for protected content
- Tests PDF download with Chrome PDF viewer detection

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- PDF URL to download from
- Output path for downloaded file

Output:
- Downloaded PDF file at specified location
- Console output showing download progress and method used
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_pdf_download(
    pdf_url: str = None, output_path: str = None, browser_mode: str = "stealth"
) -> str:
    """Demonstrate PDF downloading capabilities.

    Parameters

...
```


### `./examples/06_find_and_download.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:21:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_find_and_download.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Integrated example: Find PDF URL and download immediately.

This demonstrates the complete workflow:
1. Find PDF URL with navigation to get authenticated URL
2. Download PDF immediately in the same browser context
3. Avoid session expiration issues
"""

import argparse
import asyncio
from pathlib import Path

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


async def find_and_download_pdf(
    doi: str, output_dir: str = "/tmp", browser_mode: str = "stealth"
) -> Path:
    """
    Find PDF URL and download it immediately in the same session.

    This avoids the redirect issue when trying to use authenticated URLs later.
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarPDFDownloader,
        ScholarURLFinder,
    )

    logger.info(f"Processing DOI: {doi}")

    # Initialize browser with authentication
    logger.info(f"Initializing browser ({browser_mode} mode)...")
    auth_manager = ScholarAuthManager()

...
```


### `./examples/06_parse_bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:02:15 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_parse_bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates BibTeX parsing utilities in Scholar module
- Shows parsing of different BibTeX file formats (openaccess, paywalled)
- Validates BibTeX entry structure and field extraction
- Displays sample entries with detailed metadata

Dependencies:
- scripts:
  - None
- packages:
  - scitex

Input:
- ./data/scholar/openaccess.bib
- ./data/scholar/paywalled.bib

Output:
- Console output showing parsed BibTeX entries
- Sample entries with authors, titles, journals, and metadata
"""

"""Imports"""
import argparse
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
def demonstrate_bibtex_parsing(
    openaccess_path: str = "./data/scholar/openaccess.bib",
    paywalled_path: str = "./data/scholar/paywalled.bib",
    n_samples: int = 3
) -> dict:
    """Demonstrate BibTeX parsing capabilities.

...
```


### `./examples/07_storage_integration.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 15:22:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/07_storage_integration.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates enhanced Paper, Papers, and Scholar storage integration
- Shows individual paper storage operations
- Demonstrates project-level collection management
- Tests global Scholar library operations

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Scholar library configuration
- Sample paper metadata

Output:
- Console output showing storage operations
- Papers stored in Scholar library with proper organization
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_paper_storage() -> None:
    """Demonstrate individual Paper storage capabilities."""
    from scitex.scholar.core import Paper
    from scitex.scholar.config import ScholarConfig
    

...
```


### `./examples/99_fullpipeline-for-bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-24 21:47:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Executes full scholar pipeline for BibTeX processing
- Searches metadata for papers from BibTeX entries
- Finds URLs for academic papers using DOIs
- Downloads PDFs from discovered URLs with authentication
- Manages browser sessions with auth for paywalled content

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio, numpy, pathlib

Input:
- BibTeX files with academic paper entries
- Browser profile for authentication

Output:
- Downloaded PDF files to /tmp/scholar_pipeline/
- Metadata and URL information for papers
"""

"""Imports"""
import argparse
import asyncio
from pathlib import Path
from pprint import pprint

import numpy as _np

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def process_bibtex_entries(

...
```


### `./examples/99_fullpipeline-for-one-entry.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:02:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-one-entry.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates complete Scholar workflow for single paper processing
- Shows end-to-end pipeline from search to PDF download
- Integrates all Scholar components in sequence
- Tests full automated academic paper acquisition workflow

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio, pathlib

Input:
- Paper title for search query
- Browser and caching configuration

Output:
- Downloaded PDF files in specified directory
- Console output showing pipeline progress
- Comprehensive metadata and URL information
"""

"""Imports"""
import argparse
import asyncio
from pathlib import Path
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def run_full_pipeline(
    title: str,
    use_cache: bool = False,

...
```


### `./examples/99_maintenance.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 03:04:54 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_maintenance.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

"""
Functionalities:
  - Does XYZ
  - Does XYZ
  - Does XYZ
  - Saves XYZ

Dependencies:
  - scripts:
    - /path/to/script1
    - /path/to/script2
  - packages:
    - package1
    - package2
IO:
  - input-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

  - output-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

(Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
"""

"""Imports"""
import argparse

import pandas as pd

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)


...
```


### `./examples/dev.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 11:48:05 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/dev.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar import ScholarAuthManager
from scitex.scholar import ScholarBrowserManager
from scitex.scholar import ScholarURLFinder
from scitex.scholar.url.helpers._find_functions import (
    _find_pdf_urls_by_zotero_translators,
)

# Initialize with authenticated browser context
auth_manager = ScholarAuthManager()
browser_manager = ScholarBrowserManager(
    auth_manager=auth_manager,
    # browser_mode="stealth",
    browser_mode="interactive",
    chrome_profile_name="system",
)
browser, context = (
    await browser_manager.get_authenticated_browser_and_context_async()
)
page = await context.new_page()

await page.goto("https://www.science.org/doi/10.1126/science.aao0702")


translator_urls = await _find_pdf_urls_by_zotero_translators(
    page, "https://doi.org/10.1016/j.neubiorev.2020.07.005"
)

# EOF

...
```


### `./examples/README.md`

```markdown

EXAMPLE_DIR=/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples
"$EXAMPLE_DIR"/00_config.py
"$EXAMPLE_DIR"/01_auth.py
"$EXAMPLE_DIR"/02_browser.py
"$EXAMPLE_DIR"/03_01-engine.py
"$EXAMPLE_DIR"/03_02-engine-for-bibtex.py --no-cache
"$EXAMPLE_DIR"/04_01-url.py --no-cache
"$EXAMPLE_DIR"/04_02-url-for-bibtex.py --no-cache-url-finder --n-samples 10 --browser-mode stealth
"$EXAMPLE_DIR"/05_download_pdf.py --pdf-url
"$EXAMPLE_DIR"/06_find_and_download.py


...
```


### `./examples/SUGGESTIONS.md`

```markdown

You've hit another excellent and distinct debugging case. The error has changed, which tells us we are making progress and uncovering the complexities of running these translators outside their native environment.

The new key error is:
ERROR: Translator error: em.doWeb is not a function

This is different and more informative than the previous one. It's not just a data format issue; it's a structural problem with how the translator code is being executed.

## What's Happening Here?
Zotero translators have evolved, and not all of them follow the simple, global detectWeb() and doWeb() function pattern. The "Frontiers" translator uses a more modern, object-oriented approach.

When the Frontiers.js code is executed, it doesn't just define global functions. Instead, it likely creates an instance of an object (let's call it em).

The main logic, including the doWeb function, is a method of this em object.

Your current JavaScript wrapper and executor (zotero_wrapper.js) are not aware of this. They blindly look for a global doWeb function, which doesn't exist. The function they need to call is em.doWeb().

Because this first step fails, the script execution halts, and the subsequent SyntaxError: Unexpected token '<' is likely a red herring—a downstream consequence of the initial failure.

## The Solution: A More Intelligent Executor
To solve this, your JavaScript executor needs to be smarter. It must first run the translator's code and then inspect the global scope to find out how that specific translator needs to be called. It needs to check for a global doWeb function, and if that doesn't exist, it should look for a common object pattern (like an object named em with a doWeb method).

Here is an updated, more robust version of the execution logic for your _ZoteroTranslatorRunner.py. This change centralizes the execution logic within the page.evaluate call, making it more adaptable.

Replace the page.evaluate block in the extract_urls_pdf_async method of _ZoteroTranslatorRunner.py with this:

Python

# In _ZoteroTranslatorRunner.py -> extract_urls_pdf_async method

# ... after injecting the Zotero environment JS ...

result = await page.evaluate(
    """
    async ([translatorCode, translatorLabel]) => {
        // This is the main execution function, now running entirely in the browser.
        // It's a combination of your wrapper and the execution logic.
        const urls = new Set();
        const items = [];
        let translatorError = null;

        // --- Start: Mock Zotero Environment (condensed from your zotero_wrapper.js) ---
        window.Zotero = {
            Item: function(type) {
                this.itemType = type;
                this.attachments = [];
                this.url = null;
                this.DOI = null;
                this.complete = function() {
                    if (this.url) urls.add(this.url);

...
```


### `./externals/impact_factor_calculator/LICENSE`

```plaintext
MIT License

Copyright (c) 2025 SciTeX Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
...
```


### `./externals/impact_factor_calculator/README.md`

```markdown

# Impact Factor Calculator

A comprehensive, legally compliant impact factor calculation system using open APIs from OpenAlex, Crossref, and Semantic Scholar. This package provides transparent, verifiable impact factor calculations without relying on proprietary databases or restricted access systems.

## 🌟 Key Features

- **Legal & Transparent**: Uses only publicly available APIs and open data sources
- **Multi-Source Integration**: Combines data from OpenAlex, Crossref, and Semantic Scholar
- **Advanced Matching**: Sophisticated journal matching algorithms across data sources
- **Efficient Caching**: Intelligent caching system with configurable TTL and size limits
- **Batch Processing**: Support for bulk calculations with progress tracking
- **CLI Interface**: Full-featured command-line interface
- **Export Formats**: JSON, CSV, and human-readable output formats
- **Comprehensive Documentation**: Examples and detailed methodology explanations

## 📊 Impact Factor Calculation Methods

### 1. Classical 2-Year Impact Factor
```
IF = Citations in year Y to papers from years (Y-1) and (Y-2) / Papers published in years (Y-1) and (Y-2)
```

### 2. H-Index Based Impact Indicator
```  
H-IF = H-index / 10 (normalized)
```

### 3. Citation Per Paper Ratio
```
CPP = Total citations / Total papers (estimated for 2-year window)
```

### 4. Confidence Score
Based on data availability across sources (0.0 - 1.0 scale)

## 🚀 Installation

```bash
cd /path/to/this/package
pip install -e .
```

## 📈 Quick Start

### Basic Usage

```python
from impact_factor import ImpactFactorCalculator

```

...
```


### `./externals/impact_factor_calculator/requirements.txt`

```plaintext
requests>=2.25.1
scitex
...
```


### `./externals/impact_factor_calculator/setup.py`

```python
from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent

setup(
    name="impact-factor-calculator",
    version="1.0.0",
    author="Yusuke Watanabe",
    author_email="ywatanabe@scitex.ai",
    description="Legal impact factor calculator using OpenAlex, Crossref, and Semantic Scholar",
    long_description=BASE_DIR.joinpath("README_LEGAL.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/scitex/impact-factor-calculator",
    project_urls={
        "Documentation": "https://scitex.ai/docs/impact-factor",
        "Repository": "https://github.com/scitex/impact-factor-calculator",
        "Issues": "https://github.com/scitex/impact-factor-calculator/issues",
    },
    license="MIT License",
    install_requires=BASE_DIR.joinpath("requirements.txt")
    .read_text()
    .strip()
    .split("\n"),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "scitex-impact-factor = impact_factor.cli:main",
            "impact-factor-calc = impact_factor.cli:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",

...
```


### `./externals/impact_factor_jcr/build.sh`

```bash
rm -rf dist build *egg-info

python3 setup.py sdist bdist_wheel

rm -rf build *egg-info

...
```


### `./externals/impact_factor_jcr/README.md`

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7539859.svg)](https://doi.org/10.5281/zenodo.7539859)

[![Downloads](https://pepy.tech/badge/impact-factor)](https://pepy.tech/project/impact-factor)
![PyPI - License](https://img.shields.io/pypi/l/mi?style=plastic)
![PyPI](https://img.shields.io/pypi/v/impact_factor)
![PyPI - Status](https://img.shields.io/pypi/status/impact_factor)


# ***最新SCI期刊影响因子查询系统***
- *已更新 **[2024年数据](https://www.researchgate.net/publication/381580823_Journal_Citation_Reports_JCR_Impact_Factor_2024_PDF_Web_of_Science)***
- *包含JCR分区表数据*

## Installation
```bash
python3 -m pip install -U impact_factor
```

## Use in CMD
```bash
impact_factor -h
```
![](https://suqingdong.github.io/impact_factor/src/help.png)

### `build`
> build/update the database

```bash
# optional, only required when you need build or update the database
impact_factor build -i tests/IF.xlsx

# with a ncbi api_key
impact_factor build -k YOUR_NCBI_API_KEY

# use a new dbfile [*recommend*]
impact_factor -d test.db build -i tests/IF.xlsx

# without nlm_catalog
impact_factor -d test.db build -i tests/IF.xlsx -n
```

### `search`
> search with `journal`, `journal_abbr`, `issn`, `eissn` or `nlm_id`

```bash
impact_factor search nature         # search journal
impact_factor search 'nature c%'    # like search journal
impact_factor search 0028-0836      # search ISSN
impact_factor search 1476-4687      # search eISSN
impact_factor search 0410462        # search nlm_id
impact_factor search nature --color # colorful output
```

...
```


### `./externals/impact_factor_jcr/requirements.txt`

```plaintext
lxml
click
openpyxl
pygments
webrequests
sql_manager

...
```


### `./externals/impact_factor_jcr/setup.py`

```python
import json
from pathlib import Path
from setuptools import setup, find_packages


BASE_DIR = Path(__file__).resolve().parent
version_info = json.load(BASE_DIR.joinpath('impact_factor', 'version.json').open())

setup(
    name=version_info['prog'],
    version=version_info['version'],
    author=version_info['author'],
    author_email=version_info['author_email'],
    description=version_info['desc'],
    long_description=BASE_DIR.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    url=version_info['url'],
    project_urls={
        'Documentation': 'https://impact_factor.readthedocs.io',
        'Tracker': 'https://github.com/suqingdong/impact_factor/issues',
    },
    license='MIT License',
    install_requires=BASE_DIR.joinpath('requirements.txt').read_text().strip().split(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': [
        'IF = impact_factor.bin.cli:main',
        'impact_factor = impact_factor.bin.cli:main',
    ]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ]
)

...
```


### `./externals/README.md`

```markdown

# Legal
git clone git@github.com:ywatanabe1989/impact_factor_calculator.git

# When you have access to JCR data
git clone git@github.com:suqingdong/impact_factor.git impact_factor_jcr


...
```


### `./extra/__init__.py`

```python
from .JournalMetrics import JournalMetrics

...
```


### `./extra/JournalMetrics.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 16:49:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/extra/JournalMetrics.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Retrieves journal impact factors and quartiles
- Provides standalone journal metrics lookup
- Caches results for performance optimization

Dependencies:
- packages:
  - impact_factor

Input:
- Journal names as strings

Output:
- Dictionary containing impact factor and quartile data
"""

"""Imports"""
from functools import lru_cache
from typing import Dict, Optional

from impact_factor.core import Factor

"""Parameters"""

"""Functions & Classes"""
class JournalMetrics:
    """Standalone journal metrics retrieval using impact_factor package."""

    def __init__(self, cache_size: int = 1000):
        """Initialize with optional cache size."""
        self.factor_instance = Factor()
        self.get_metrics = lru_cache(maxsize=cache_size)(
            self._get_metrics_uncached
        )

    def _get_jcr_year(self) -> str:
        """Extract JCR year from database or package metadata."""
        try:

...
```


### `./__init__.py`

```python
"""
SciTeX Scholar - Scientific Literature Management Made Simple

This module provides a unified interface for:
- Searching scientific literature across multiple sources
- Automatic paper enrichment with journal metrics
- PDF downloads and local library management
- Bibliography generation in multiple formats

Quick Start:
    from scitex.scholar import Scholar

    scholar = Scholar()
    papers = scholar.search("deep learning")
    papers.save("pac.bib")
"""

# # Import main class
# from .core._Scholar import Scholar, search, search_quick, enrich_bibtex

# Import configuration
from scitex.scholar.config import ScholarConfig
from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.engines import ScholarEngine
from scitex.scholar.url import ScholarURLFinder
from scitex.scholar.download import ScholarPDFDownloader
from scitex.scholar.storage import ScholarLibrary
from scitex.scholar.core import Paper, Papers, Scholar
from . import utils

__all__ = [
    "ScholarConfig",
    "ScholarEngine",
    "ScholarURLFinder",
    "ScholarAuthManager",
    "ScholarBrowserManager",

    "Paper",
    "Papers",
    "Scholar",

    "utils",
]

# # Import core classes for advanced users
# from scitex.scholar.core import Paper
# from .core.Papers import Papers

# # DOI resolver is available via: python -m scitex.scholar.resolve_doi_asyncs

...
```


### `./__main__.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 10:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from scitex import logging

logger = logging.getLogger(__name__)


def cleanup_scholar_processes(signal_num=None, frame=None):
    """Cleanup function to stop all Scholar browser processes gracefully."""
    if signal_num:
        logger.info(f"Received signal {signal_num}, cleaning up Scholar processes...")

    try:
        import subprocess
        # Kill Chrome/Chromium processes (suppress stderr)
        subprocess.run(
            ["pkill", "-f", "chrome"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False
        )
        subprocess.run(
            ["pkill", "-f", "chromium"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False
        )

        # Kill Xvfb displays
        subprocess.run(
            ["pkill", "Xvfb"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,

...
```


### `./README.md`

```markdown

# SciTeX Scholar

A comprehensive Python library for scientific literature management with automatic enrichment, PDF download capabilities, and persistent storage organization.

## 🌟 Key Features

- **Unified CLI** - Flexible command-line interface with combinable operations
- **Automatic Enrichment** - Resolve DOIs, abstracts, citations, and impact factors
- **PDF Downloads** - Authenticated browser automation for institutional access
- **MASTER Storage** - Centralized storage with project-based organization
- **Project Management** - Persistent library with metadata tracking
- **Smart Caching** - Resume interrupted operations seamlessly

## 📚 Storage Architecture

```
~/.scitex/scholar/library/
├── MASTER/                     # Centralized storage
│   ├── 8DIGIT01/              # Hash-based unique ID from DOI
│   │   ├── metadata.json      # Complete paper metadata
│   │   └── paper.pdf          # Downloaded PDF
│   └── 8DIGIT02/
│       ├── metadata.json
│       └── paper.pdf
├── project_name/               # Project-specific symlinks
│   ├── Author-Year-Journal -> ../MASTER/8DIGIT01
│   └── Author-Year-Journal -> ../MASTER/8DIGIT02
└── neurovista/
    ├── Cook-2013-Lancet -> ../MASTER/8DIGIT03
    └── ...
```

## 🚀 Quick Start

### Installation

```bash
# From SciTeX repository
cd /home/ywatanabe/proj/scitex_repo
pip install -e .

# Or for development
cd /home/ywatanabe/proj/SciTeX-Code
pip install -e .
```

### Basic Workflow

```bash
```

...
```


### `./storage/BibTeXHandler.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 23:01:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/_BibTeXHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


class BibTeXHandler:
    """Handles BibTeX parsing and conversion to Paper objects."""

    def __init__(self, project: str = None, config=None):
        self.project = project
        self.config = config

    def _extract_primitive(self, value):
        """Extract primitive value from DotDict or nested structure."""
        from scitex.dict import DotDict

        if value is None:
            return None
        if isinstance(value, DotDict):
            # Convert DotDict to plain dict first
            value = dict(value)
        if isinstance(value, dict):
            # For nested dict structures, return as-is
            return value
        # Return primitive types as-is
        return value

    def papers_from_bibtex(
        self, bibtex_input: Union[str, Path]
    ) -> List["Paper"]:
        """Create Papers from BibTeX file or content."""
        is_path = False
        input_str = str(bibtex_input)

        if len(input_str) < 500:
            if (

...
```


### `./storage/_calculate_similarity_score.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 22:42:59 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/_calculate_similarity_score.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from difflib import SequenceMatcher


def calculate_similarity_score(paper1: "Paper", paper2: "Paper") -> float:
    """Calculate similarity score between two papers."""
    if paper1.doi and paper2.doi and paper1.doi == paper2.doi:
        return 1.0

    title_sim = 0
    if paper1.title and paper2.title:
        title_sim = (
            SequenceMatcher(
                None, paper1.title.lower(), paper2.title.lower()
            ).ratio()
            * 0.4
        )

    author_sim = 0
    if paper1.authors and paper2.authors:
        author_sim = (
            0.2
            if paper1.authors[0].lower() == paper2.authors[0].lower()
            else 0
        )

    abstract_sim = 0
    if paper1.abstract and paper2.abstract:
        abstract_sim = (
            SequenceMatcher(
                None,
                paper1.abstract[:200].lower(),
                paper2.abstract[:200].lower(),
            ).ratio()
            * 0.3
        )

    year_sim = 0
    if paper1.year and paper2.year:
        year_diff = abs(int(paper1.year) - int(paper2.year))

...
```


### `./storage/_DeduplicationManager.py`

```python
#!/usr/bin/env python3
"""Deduplication manager for handling duplicate papers in the library."""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class DeduplicationManager:
    """Manages deduplication of papers in the MASTER library."""

    def __init__(self, config: ScholarConfig = None):
        self.config = config or ScholarConfig()
        self.library_dir = self.config.get_library_dir()
        self.master_dir = self.library_dir / "MASTER"

    def find_duplicate_papers(self) -> Dict[str, List[Path]]:
        """Find all duplicate papers in MASTER library.

        Returns:
            Dictionary mapping paper fingerprint to list of duplicate paths
        """
        logger.info("Scanning MASTER library for duplicates...")

        paper_groups = {}  # fingerprint -> list of paths
        papers_by_title = {}  # normalized_title -> list of (path, metadata)

        if not self.master_dir.exists():
            return paper_groups

        # First pass: collect all papers
        all_papers = []
        for paper_dir in self.master_dir.iterdir():
            if not paper_dir.is_dir():
                continue

            metadata_file = paper_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:

...
```


### `./storage/__init__.py`

```python
from ._LibraryManager import LibraryManager
from ._LibraryCacheManager import LibraryCacheManager
from .ScholarLibrary import ScholarLibrary
from ._calculate_similarity_score import calculate_similarity_score
from .BibTeXHandler import BibTeXHandler

...
```


### `./storage/_LibraryCacheManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 14:26:28 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryCacheManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Result caching and Scholar library management for DOI resolution."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class LibraryCacheManager:
    """Handles DOI caching, result persistence, and retrieval.

    Responsibilities:
    - Scholar library checking and DOI retrieval
    - DOI caching and result persistence
    - Unresolved entry tracking
    - Project symlink management
    - Library integration and file management
    """

    def __init__(
        self,
        project: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize result cache manager.

        Args:
            config: ScholarConfig instance
            project: Project name for library organization
        """
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        logger.debug(f"LibraryCacheManager initialized for project: {project}")

...
```


### `./storage/_LibraryManager.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 16:01:08 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import OrderedDict
import copy

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.utils import TextNormalizer
from scitex.scholar.storage._DeduplicationManager import DeduplicationManager
from scitex.scholar.engines.utils import standardize_metadata, BASE_STRUCTURE

logger = logging.getLogger(__name__)


class LibraryManager:
    """Unified manager for Scholar library structure and paper storage."""

    def __init__(
        self,
        project: str = None,
        single_doi_resolver=None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize library manager."""
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        self.library_master_dir = self.config.get_library_dir() / "MASTER"
        self.single_doi_resolver = single_doi_resolver
        self._source_filename = "papers"
        self.dedup_manager = DeduplicationManager(config=self.config)

    def _dotdict_to_dict(self, obj):
        """Recursively convert DotDict to plain dict for JSON serialization."""
        from scitex.dict import DotDict


...
```


### `./storage/_PDFExtractor.py`

```python
#!/usr/bin/env python3
"""PDF content extractor for Scholar library papers."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extracts and saves text and figures from PDFs in the Scholar library."""

    def __init__(self):
        """Initialize PDF extractor."""
        pass

    def extract_pdf_content(
        self,
        pdf_path: Path,
        output_dir: Optional[Path] = None,
        extract_text: bool = True,
        extract_figures: bool = True,
        extract_tables: bool = True,
        mode: str = "full"
    ) -> Dict[str, Any]:
        """Extract content from a PDF file.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted content (defaults to PDF's parent)
            extract_text: Extract text content
            extract_figures: Extract figures/images
            extract_tables: Extract tables
            mode: Extraction mode ('full', 'text', 'structured')

        Returns:
            Dictionary with extraction results and paths to saved files
        """
        if not pdf_path.exists():
            logger.warning(f"PDF not found: {pdf_path}")
            return {"error": "PDF not found"}

        if not output_dir:
            output_dir = pdf_path.parent


...
```


### `./storage/ScholarLibrary.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 04:18:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/ScholarLibrary.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex.scholar.config import ScholarConfig

from ._LibraryCacheManager import LibraryCacheManager
from ._LibraryManager import LibraryManager
from .BibTeXHandler import BibTeXHandler


class ScholarLibrary:
    """Unified Scholar library management combining cache and storage operations."""

    def __init__(
        self, project: str = None, config: Optional[ScholarConfig] = None
    ):
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        self._cache_manager = LibraryCacheManager(
            project=self.project, config=self.config
        )
        self._library_manager = LibraryManager(
            project=self.project, config=self.config
        )
        self.bibtex_handler = BibTeXHandler(
            project=self.project, config=self.config
        )

    def load_paper(self, library_id: str) -> Dict[str, Any]:
        """Load paper metadata from library."""
        return self._cache_manager.load_paper_metadata(library_id)

    def _extract_primitive(self, value):
        """Extract primitive value from DotDict or nested structure."""
        from scitex.dict import DotDict

        if value is None:
            return None
        if isinstance(value, DotDict):

...
```


### `./tests/cli_flags_combinations.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 12:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/tests/cli_flags_combinations.py
# ----------------------------------------
"""
Test various CLI flag combinations for SciTeX Scholar.

This module tests that different combinations of flags and arguments
work correctly together in the unified CLI interface.

Examples:
    # Run all tests
    python -m scitex.scholar.tests.cli_flags_combinations

    # Run specific test category
    python -m scitex.scholar.tests.cli_flags_combinations --test-category input
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tempfile
import json

from scitex import logging

logger = logging.getLogger(__name__)


class CLIFlagTester:
    """Test various CLI flag combinations for SciTeX Scholar."""

    def __init__(self):
        self.base_cmd = [sys.executable, "-m", "scitex.scholar"]
        self.test_results = []

        # Create test data directory
        self.test_dir = Path(tempfile.mkdtemp(prefix="scitex_scholar_test_"))
        logger.info(f"Test directory: {self.test_dir}")

        # Create minimal test BibTeX file
        self.test_bibtex = self.test_dir / "test.bib"
        self.test_bibtex.write_text("""
@article{Test2024,
  title = {Test Article},
  author = {Test Author},
  year = {2024},

...
```


### `./tests/CLI_TEST_RESULTS.md`

```markdown
# SciTeX Scholar CLI Flag Combinations Test Results

## Summary

The unified CLI for SciTeX Scholar successfully handles various flag combinations with proper error handling and graceful failure modes.

## Test Categories

### ✅ Input Combinations (71% Pass Rate)
- **Working**: Single DOI, Multiple DOIs, Title search, BibTeX with enrichment
- **Edge Cases**: BibTeX-only and DOI download operations properly show error messages when dependencies are missing

### ✅ Operation Combinations (75% Pass Rate)
- **Working**: Statistics, project listing, search, enrichment with output, project export
- **Edge Cases**: Download operations require proper authentication setup (expected behavior)

### ✅ Filter Combinations (100% Pass Rate)
- All filter combinations work correctly with operations
- Filters properly propagate through the pipeline

### ✅ Edge Cases (83% Pass Rate)
- Proper help display when no arguments provided
- Graceful handling of invalid inputs with instructive error messages
- Correct validation of argument types (year, impact factor)
- Debug mode works correctly

### ✅ Key Findings

1. **Successful Patterns**:
   ```bash
   # Enrichment workflows
   python -m scitex.scholar --bibtex file.bib --enrich --output enriched.bib

   # Project management
   python -m scitex.scholar --project myproject --create-project --description "Description"

   # Filtering with operations
   python -m scitex.scholar --bibtex file.bib --min-citations 50 --enrich

   # Export with filters
   python -m scitex.scholar --project myproject --year-min 2020 --export bibtex
   ```

2. **Error Handling**:
   - Invalid file paths → Clear "file not found" message
   - Missing required args → Helpful usage instructions
   - Invalid types → Proper type validation errors
   - Authentication required → Instructions to authenticate

## Conclusion

...
```


### `./tests/coverage_analysis.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coverage Analysis for Zotero Translator Standardization.

This script analyzes what patterns and publishers are covered by our solution.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

def analyze_translator_coverage():
    """Analyze which publishers and patterns are covered."""
    
    translator_dir = Path(__file__).parent.parent / "url/helpers/finders/zotero_translators"
    js_executor = Path(__file__).parent.parent / "browser/js/integrations/zotero/zotero_translator_executor.js"
    
    print("=" * 60)
    print("ZOTERO TRANSLATOR COVERAGE ANALYSIS")
    print("=" * 60)
    
    # 1. Count translators
    translators = list(translator_dir.glob("*.js"))
    translators = [t for t in translators if not t.name.startswith("_")]
    print(f"\n📚 Total Zotero Translators Available: {len(translators)}")
    
    # 2. Analyze publisher coverage
    publishers = {}
    patterns_found = {
        "global_functions": [],
        "object_oriented": [],
        "async_patterns": [],
        "nested_translators": []
    }
    
    for translator_file in translators[:50]:  # Sample first 50 for analysis
        try:
            content = translator_file.read_text(encoding='utf-8')
            
            # Extract metadata
            lines = content.split("\n")
            json_end = -1
            brace_count = 0
            
            for i, line in enumerate(lines):
                if line.strip() == "{":
                    brace_count = 1
                elif brace_count > 0:

...
```


### `./tests/run_zotero_tests.py`

```python
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

from scitex.logging import getLogger

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

...
```


### `./tests/test_tiered_translators.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Tiered Zotero Translators

Tests the standardized Zotero translator system across all tiers,
verifying that each tier's translators work correctly with our
unified execution approach.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.log import getLogger

logger = getLogger(__name__)


class TieredTranslatorTester:
    """Test suite for tiered Zotero translators."""
    
    # Test URLs for each tier
    TIER_TEST_CASES = {
        "TIER_1_CORE_GIANTS": [
            {
                "publisher": "ScienceDirect",
                "url": "https://www.sciencedirect.com/science/article/pii/S0149763420304668",
                "doi": "10.1016/j.neubiorev.2020.07.005",
                "expected_pdf": True
            },
            {
                "publisher": "Springer",
                "url": "https://link.springer.com/article/10.1007/s11229-020-02724-x",
                "doi": "10.1007/s11229-020-02724-x",
                "expected_pdf": None  # Depends on access
            },
            {
                "publisher": "Wiley",
                "url": "https://onlinelibrary.wiley.com/doi/10.1002/hbm.25001",
                "doi": "10.1002/hbm.25001",
                "expected_pdf": None
            },
            {
                "publisher": "Taylor & Francis",
                "url": "https://www.tandfonline.com/doi/full/10.1080/00273171.2020.1743630",
                "doi": "10.1080/00273171.2020.1743630",

...
```


### `./tests/test_translator_javascript_patterns.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct JavaScript pattern validation for Zotero translators.

This test ensures our JavaScript executor can handle ANY translator pattern
by testing the JavaScript code directly without network dependencies.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List

from playwright.async_api import async_playwright

from scitex.log import getLogger

logger = getLogger(__name__)


# Mock translator patterns to test
MOCK_TRANSLATORS = {
    "pattern_1_global": """
        // Pattern 1: Classic global functions
        function detectWeb(doc, url) {
            if (url.includes('article')) return 'journalArticle';
            return false;
        }
        
        function doWeb(doc, url) {
            var item = new Zotero.Item('journalArticle');
            item.title = 'Test Article - Global Pattern';
            item.url = url;
            item.attachments.push({
                url: 'https://example.com/test_global.pdf',
                mimeType: 'application/pdf',
                title: 'Full Text PDF'
            });
            item.complete();
        }
    """,
    
    "pattern_2_object_em": """
        // Pattern 2: Object-oriented with 'em'
        var em = {
            detectWeb: function(doc, url) {
                if (url.includes('article')) return 'journalArticle';
                return false;
            },

...
```


### `./tests/test_with_embedded_cases.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Test Suite using Zotero's Built-in Test Cases.

This script automatically discovers and runs test cases embedded in the
Zotero translator JavaScript files, providing comprehensive coverage
without manually maintaining test URLs.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scitex.log import getLogger

logger = getLogger(__name__)


class ZoteroEmbeddedTestRunner:
    """Extract and run test cases embedded in Zotero translator files."""
    
    def __init__(self, translator_dir: Path = None):
        """Initialize with translator directory."""
        self.translator_dir = translator_dir or (
            Path(__file__).parent.parent / "url/helpers/finders/zotero_translators"
        )
        self.test_cases = []
        self.results = []
    
    def extract_test_cases_from_file(self, js_file: Path) -> List[Dict]:
        """Extract test cases from a single translator file."""
        try:
            content = js_file.read_text(encoding='utf-8')
            
            # Find test cases block
            match = re.search(
                r'/\*\* BEGIN TEST CASES \*\*/\s*(.*?)\s*/\*\* END TEST CASES \*\*/',
                content,
                re.DOTALL
            )
            
            if not match:
                return []
            
            test_json = match.group(1).strip()
            
            # Parse JSON

...
```


### `./tests/test_zotero_translator_patterns.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite to ensure Zotero translators work in a standardized manner across all publishers.

This test validates that our JavaScript executor can handle:
1. Classic global function patterns (detectWeb/doWeb)
2. Object-oriented patterns (em.detectWeb/em.doWeb)
3. Various translator architectures
4. Edge cases and error handling
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Tuple

from playwright.async_api import Page, async_playwright

from scitex.log import getLogger

logger = getLogger(__name__)


class ZoteroTranslatorPatternTester:
    """Test Zotero translator patterns across diverse publishers."""
    
    # Test cases covering major publishers and translator patterns
    TEST_CASES = [
        {
            "name": "Frontiers (Open Access)",
            "url": "https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full",
            "doi": "10.3389/fnins.2019.00573",
            "expected_pattern": "object",  # Uses em object pattern
            "should_find_pdf": True,
            "publisher": "Frontiers"
        },
        {
            "name": "Nature (Mixed Access)",
            "url": "https://www.nature.com/articles/s41593-018-0209-y",
            "doi": "10.1038/s41593-018-0209-y",
            "expected_pattern": "global",
            "should_find_pdf": None,  # Depends on access
            "publisher": "Nature"
        },
        {
            "name": "ScienceDirect/Elsevier",
            "url": "https://www.sciencedirect.com/science/article/pii/S0149763420304668",
            "doi": "10.1016/j.neubiorev.2020.07.005",
            "expected_pattern": "global",

...
```


### `./TODO.md`

```markdown


/home/ywatanabe/proj/scitex_repo/.dev/download_neurovista_pdfs.py


...
```


### `./url/docs/CORE_URL_TYPES.md`

```markdown

# Core URL Types for Scholar Metadata

## Essential URLs in Resolution Order

## Usage

``` python
from scitex.scholar.metadata.urls import ScholarURLFinder
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.auth import ScholarAuthManager

browser_manager = ScholarBrowserManager(
    chrome_profile_name="system",
    browser_mode="interactive",
    auth_manager=ScholarAuthManager(),
)

browser, context = (
    await browser_manager.get_authenticated_browser_and_context_async()
)

url_finder = ScholarURLFinder(context)
urls = await url_handler.find_urls(doi="10.1523/jneurosci.2929-12.2012")
print(urls)
# {'url_doi': 'https://doi.org/10.1523/jneurosci.2929-12.2012',
#  'url_publisher': 'https://www.jneurosci.org/content/32/44/15467',
#  'url_pdf': ['https://www.jneurosci.org/content/jneuro/32/44/15467.full.pdf',
#   'https://www.jneurosci.org/content/32/44.toc.pdf',
#   'https://www.jneurosci.org/content/jneuro/32/44/local/advertising.pdf',
#   'https://www.jneurosci.org/content/jneuro/32/44/local/ed-board.pdf',
#   'https://www.jneurosci.org/content/jneuro/32/44/15467.full-text.pdf',
#   'https://www.jneurosci.org/content/32/44/15467.full.pdf']}

## Download article PDF
from playwright.async_api import BrowserContext
from pathlib import Path
from scitex import logging

logger = logging.getLogger(__name__)


async def download_from_url(context: BrowserContext, pdf_url: str, output_path: Path):
    """
    Download PDF using request context (bypasses Chrome PDF viewer).
    
    This sends HTTP requests with the browser's cookies/auth,
    but doesn't render the response in the browser.
    """
    response = await context.request.get(pdf_url)
```

...
```


### `./url/docs/URL_SCHEMA.md`

```markdown
# URL Schema for Scholar Metadata

## Overview
Each paper entry in the Scholar library needs to track multiple types of URLs for different purposes. This document defines the comprehensive URL schema.

## URL Types and Their Purposes

### 1. Identification URLs
- **`url_doi`**: The DOI resolver URL (e.g., `https://doi.org/10.1038/s41593-025-01990-7`)
  - Purpose: Permanent identifier, always redirects to current publisher location
  - Source: DOI resolver services (CrossRef, DataCite)
  
- **`canonical_url`**: The canonical/preferred URL for the article
  - Purpose: The "official" URL that should be cited
  - Source: Publisher metadata or DOI resolution

### 2. Access URLs
- **`article_url`**: The article landing page URL
  - Purpose: Human-readable page with abstract, metadata, and download options
  - Example: `https://www.nature.com/articles/s41593-025-01990-7`
  - Source: Original input, DOI resolution, or search results

- **`url_publisher`**: The final publisher URL after authentication
  - Purpose: The actual URL after SSO/proxy authentication
  - Example: `https://www-nature-com.eu1.proxy.openathens.net/articles/...`
  - Source: Browser after authentication

- **`openurl`**: The library OpenURL resolver link
  - Purpose: Institution-specific link that handles authentication
  - Example: `https://unimelb.hosted.exlibrisgroup.com/openurl/61UNIMELB/...`
  - Source: OpenURL resolver

### 3. Download URLs
- **`urls_pdf`**: Array of direct PDF download URLs
  - Purpose: Direct links to PDF files (may require authentication)
  - Examples: 
    - `https://www.nature.com/articles/s41593-025-01990-7.pdf`
    - `https://www.nature.com/articles/s41593-025-01990-7.pdf?proof=t`
  - Source: Zotero translators, page scraping, publisher patterns

- **`pdf_viewer_url`**: URL of the PDF viewer page
  - Purpose: Browser-based PDF viewer (not direct download)
  - Example: `https://www.nature.com/articles/s41593-025-01990-7.pdf#view`
  - Source: Browser navigation

### 4. Alternative Access URLs
- **`preprint_url`**: Link to preprint version (if available)
  - Purpose: Free access to early version
  - Examples: 
    - `https://arxiv.org/abs/2303.12345`

...
```


### `./url/helpers/__init__.py`

```python
from .finders import find_pdf_urls, find_supplementary_urls
from .resolvers._resolve_functions import (
    normalize_doi_as_http,
    resolve_publisher_url_by_navigating_to_doi_page,
    extract_doi_from_url,
    resolve_openurl,
)

...
```


### `./url/helpers/TODO.md`

```markdown

# Resolve DOIs from various directions
10.1126/science.aao0702


...
```


### `./url/__init__.py`

```python
from .ScholarURLFinder import ScholarURLFinder

__all__ = [
    "ScholarURLFinder",
]

# EOF

...
```


### `./url/README.md`

```markdown

## TODO
PDF URL Detection on Science Direct pages are not specific to targets.
  https://doi.org/10.1016/j.neubiorev.2020.07.005
  https://doi.org/10.1016/j.smrv.2020.101353
  https://doi.org/10.1016/j.neuroimage.2021.118403
  https://doi.org/10.1016/j.neuroimage.2021.118573
  https://doi.org/10.1523/eneuro.0334-16.2016
  https://doi.org/10.1016/j.neuroimage.2019.116178


## Workflow
1. Resolve DOI → Publisher URL (always works)
2. Try PDF extraction from Publisher URL first
  - If PDF found → Done! (skip OpenURL)
  - If no PDF → Continue to OpenURL
3. Only if needed: OpenURL resolution → Authenticated URL
4. Try PDF extraction from OpenURL-resolved URL

This would be much more efficient because:
- Many publisher pages have PDFs directly accessible
- OpenURL resolution takes time (10-15 seconds with redirects)
- We avoid unnecessary authentication redirects when not needed


## Usage

```python
import asyncio

from scitex.scholar import ScholarURLFinder
from scitex.scholar import ScholarBrowserManager
from scitex.scholar import ScholarAuthManager


async def main_async():
    # Initialize with authenticated browser context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Create URL handler
    url_finder = ScholarURLFinder(context)

```

...
```


### `./url/ScholarURLFinder.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 15:25:29 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/ScholarURLFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
ScholarURLFinder - Main entry point for URL operations

Provides a clean API that wraps the functional modules.
Users can use this for convenience or directly import the functions.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar.config import ScholarConfig

from .helpers import (
    find_pdf_urls,
    normalize_doi_as_http,
    resolve_openurl,
    resolve_publisher_url_by_navigating_to_doi_page,
)

logger = logging.getLogger(__name__)


from scitex.scholar.browser.utils import take_screenshot


class ScholarURLFinder:
    """Main entry point for all URL operations."""

    URL_TYPES = [
        "urls_pdf",
        "url_doi",
        "url_openurl_query",
        "url_openurl_resolved",
        "url_publisher",

...
```


### `./utils/deduplicate_library.py`

```python
#!/usr/bin/env python3
"""CLI utility for deduplicating the Scholar library."""

import argparse
from pathlib import Path

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._DeduplicationManager import DeduplicationManager

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point for library deduplication."""
    parser = argparse.ArgumentParser(
        description="Deduplicate papers in the Scholar MASTER library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be deduplicated
  python -m scitex.scholar.utils.deduplicate_library --dry-run

  # Actually perform deduplication
  python -m scitex.scholar.utils.deduplicate_library

  # Verbose output
  python -m scitex.scholar.utils.deduplicate_library --verbose
"""
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report what would be done without making changes"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Initialize config and deduplication manager
    config = ScholarConfig()
    dedup_manager = DeduplicationManager(config=config)

    library_dir = config.get_library_dir()

...
```


### `./utils/enrich_and_fix_library.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 17:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/enrich_and_fix_library.py
# ----------------------------------------
"""
Enrich library metadata and fix symlinks using existing Scholar modules.

This properly reuses existing components:
- Scholar.load_bibtex() for loading BibTeX
- Scholar.enrich_papers() for enrichment
- Scholar.save_papers_as_bibtex() for saving
- JCRImpactFactorEngine for impact factors
- Library structure from ScholarLibrary

Usage:
    python -m scitex.scholar.utils.enrich_and_fix_library --project neurovista
    python -m scitex.scholar.utils.enrich_and_fix_library --bibtex data/neurovista_enriched.bib --project neurovista
"""

import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
import asyncio
import sys
import os

# Add parent directory to path to import standardize_metadata
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scitex.scholar.engines.utils._standardize_metadata import standardize_metadata

from scitex import logging
from scitex.scholar.core.Scholar import Scholar
from scitex.scholar.core.Paper import Paper
from scitex.scholar.core.Papers import Papers

logger = logging.getLogger(__name__)


async def enrich_and_fix_library(
    project_name: str,
    bibtex_file: Optional[Path] = None,
    dry_run: bool = False
):
    """Enrich library metadata and fix symlinks.

    Args:

...
```


### `./utils/fix_metadata_and_symlinks.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 14:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/fix_metadata_and_symlinks.py
# ----------------------------------------
"""
Fix metadata enrichment and symlink names for existing library entries.

This script:
1. Enriches metadata for papers with empty fields
2. Recreates symlinks with proper Author-Year-Journal format
3. Updates metadata.json with full enriched data

Usage:
    python -m scitex.scholar.utils.fix_metadata_and_symlinks --project neurovista
"""

import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path
import asyncio

from scitex import logging
from scitex.scholar.core.Scholar import Scholar
from scitex.scholar.core.Paper import Paper
from scitex.scholar.core.Papers import Papers

logger = logging.getLogger(__name__)


async def fix_project_metadata_and_symlinks(project_name: str, dry_run: bool = False):
    """Fix metadata and symlinks for a project.

    Args:
        project_name: Name of project to fix
        dry_run: If True, only show what would be done
    """
    library_dir = Path("/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/library")
    project_dir = library_dir / project_name
    master_dir = library_dir / "MASTER"

    if not project_dir.exists():
        logger.error(f"Project directory not found: {project_dir}")
        return

    logger.info(f"Fixing metadata and symlinks for project: {project_name}")
    if dry_run:
        logger.warning("DRY RUN - No changes will be made")

...
```


### `./utils/fix_metadata_complete.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 16:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/fix_metadata_complete.py
# ----------------------------------------
"""
Complete metadata enrichment with CrossRef, Semantic Scholar, and JCR Impact Factors.

This script:
1. Gets basic metadata from CrossRef
2. Gets citation counts from Semantic Scholar
3. Gets journal impact factors from JCR database
4. Updates metadata.json with complete data
5. Fixes symlinks with proper Author-Year-Journal format

Usage:
    python -m scitex.scholar.utils.fix_metadata_complete --project neurovista
"""

import argparse
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
import time

from scitex import logging
from scitex.scholar.engines.JCRImpactFactorEngine import JCRImpactFactorEngine

logger = logging.getLogger(__name__)


def get_metadata_from_crossref(doi: str) -> dict:
    """Get metadata from CrossRef API."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()["message"]

            metadata = {
                "title": data.get("title", [""])[0] if data.get("title") else "",
                "authors": [],
                "year": None,
                "journal": data.get("container-title", [""])[0] if data.get("container-title") else "",
                "publisher": data.get("publisher", ""),
                "abstract": data.get("abstract", ""),
                "url": data.get("URL", ""),
            }

...
```


### `./utils/fix_metadata_standardized.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 17:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/fix_metadata_standardized.py
# ----------------------------------------
"""
Complete metadata enrichment using standardized structure.

This script:
1. Converts flat metadata to standardized structure
2. Gets basic metadata from CrossRef
3. Gets citation counts from Semantic Scholar
4. Gets journal impact factors from JCR database
5. Updates metadata.json with standardized structure
6. Fixes symlinks with proper Author-Year-Journal format

Usage:
    python -m scitex.scholar.utils.fix_metadata_standardized --project neurovista
"""

import argparse
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
import time
import sys
import os

# Add parent directory to path to import standardize_metadata
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scitex.scholar.engines.utils._standardize_metadata import standardize_metadata

from scitex import logging
from scitex.scholar.engines.JCRImpactFactorEngine import JCRImpactFactorEngine

logger = logging.getLogger(__name__)


def get_metadata_from_crossref(doi: str) -> dict:
    """Get metadata from CrossRef API."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()["message"]

            metadata = {
                "title": data.get("title", [""])[0] if data.get("title") else "",

...
```


### `./utils/fix_metadata_with_crossref.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 15:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/fix_metadata_with_crossref.py
# ----------------------------------------
"""
Fix metadata and symlinks using CrossRef API for direct DOI resolution.

This script:
1. Uses CrossRef API to get metadata directly from DOI
2. Updates metadata.json with full enriched data
3. Recreates symlinks with proper Author-Year-Journal format

Usage:
    python -m scitex.scholar.utils.fix_metadata_with_crossref --project neurovista
"""

import argparse
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)


def get_metadata_from_crossref(doi: str) -> dict:
    """Get metadata from CrossRef API.

    Args:
        doi: DOI string

    Returns:
        Dictionary with metadata fields
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()["message"]

            # Extract metadata
            metadata = {
                "title": data.get("title", [""])[0] if data.get("title") else "",
                "authors": [],
                "year": None,
                "journal": data.get("container-title", [""])[0] if data.get("container-title") else "",

...
```


### `./utils/__init__.py`

```python
from ._parse_bibtex import parse_bibtex
from ._TextNormalizer import TextNormalizer

...
```


### `./utils/migrate_pdfs_to_master.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 13:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/migrate_pdfs_to_master.py
# ----------------------------------------
"""
Migrate PDFs from old project/pdfs directories to MASTER storage architecture.

This script:
1. Moves PDFs from project/pdfs/ to MASTER/8DIGITID/
2. Creates proper Author-Year-Journal symlinks
3. Updates metadata.json files

Usage:
    python -m scitex.scholar.utils.migrate_pdfs_to_master --project neurovista
"""

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from scitex import logging
from scitex.scholar.core.Scholar import Scholar
from scitex.scholar.core.Paper import Paper

logger = logging.getLogger(__name__)


def migrate_project_pdfs(project_name: str, dry_run: bool = False):
    """Migrate PDFs from project/pdfs to MASTER storage.

    Args:
        project_name: Name of project to migrate
        dry_run: If True, only show what would be done
    """
    library_dir = Path.home() / ".scitex/scholar/library"
    project_dir = library_dir / project_name
    pdfs_dir = project_dir / "pdfs"
    master_dir = library_dir / "MASTER"

    if not pdfs_dir.exists():
        logger.info(f"No pdfs directory found at {pdfs_dir}")
        return

    logger.info(f"Migrating PDFs from {pdfs_dir}")
    if dry_run:
        logger.warning("DRY RUN - No changes will be made")

...
```


### `./utils/papers_utils.py`

```python
#!/usr/bin/env python3
"""
Utility functions for Papers operations.

These functions handle operations that were removed from Papers class
to keep it as a simple collection.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import pandas as pd
from dataclasses import asdict


def papers_to_dataframe(papers: "Papers") -> pd.DataFrame:
    """Convert Papers collection to pandas DataFrame.

    Args:
        papers: Papers collection

    Returns:
        DataFrame with papers data
    """
    if len(papers) == 0:
        return pd.DataFrame()

    # Convert each paper to dict
    data = []
    for paper in papers:
        paper_dict = asdict(paper) if hasattr(paper, '__dataclass_fields__') else paper.to_dict()
        # Flatten for DataFrame
        flat_dict = {
            'title': paper_dict.get('title', ''),
            'authors': ', '.join(paper_dict.get('authors', [])),
            'year': paper_dict.get('year'),
            'journal': paper_dict.get('journal'),
            'doi': paper_dict.get('doi'),
            'citation_count': paper_dict.get('citation_count'),
            'abstract': paper_dict.get('abstract', '')[:100] + '...' if paper_dict.get('abstract') else '',
        }
        data.append(flat_dict)

    return pd.DataFrame(data)


def papers_to_bibtex(papers: "Papers", output_path: Optional[str] = None) -> str:
    """Convert Papers collection to BibTeX format.

    Args:
        papers: Papers collection

...
```


### `./utils/paper_utils.py`

```python
#!/usr/bin/env python3
"""
Utility functions for Paper operations.

All operations on Paper dataclass are handled here.
This keeps Paper as a pure data container.
"""

from __future__ import annotations
from dataclasses import asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


def paper_from_structured(
    basic: Optional[Dict[str, Any]] = None,
    id: Optional[Dict[str, Any]] = None,
    publication: Optional[Dict[str, Any]] = None,
    citation_count: Optional[Dict[str, Any]] = None,
    url: Optional[Dict[str, Any]] = None,
    path: Optional[Dict[str, Any]] = None,
    system: Optional[Dict[str, Any]] = None,
    library_id: Optional[str] = None,
    project: Optional[str] = None,
    config: Optional[Any] = None,  # Config is not stored in Paper anymore
) -> "Paper":
    """Create Paper from structured data (backward compatible).

    This function maintains backward compatibility with the old
    Paper constructor that used structured arguments.
    """
    from scitex.scholar.core.Paper import Paper

    # Initialize with defaults
    paper_data = {
        'title': '',
        'authors': [],
        'year': None,
        'abstract': None,
        'keywords': [],
        'doi': None,
        'pmid': None,
        'arxiv_id': None,
        'library_id': library_id,
        'journal': None,
        'volume': None,
        'issue': None,
        'pages': None,
        'publisher': None,

...
```


### `./utils/_parse_bibtex.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 04:46:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/_parse_bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re

import bibtexparser

from scitex import logging

logger = logging.getLogger(__name__)


def parse_bibtex(bibtex_path):
    """Safely parse BibTeX file, handling comment lines."""

    with open(bibtex_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove comment lines starting with %
    lines = content.split("\n")
    cleaned_lines = [line for line in lines if not re.match(r"^\s*%", line)]
    cleaned_content = "\n".join(cleaned_lines)

    try:
        # Try standard parser first
        logger.info(f"Parsing {bibtex_path} using bibtexparser...")
        bib_db = bibtexparser.loads(cleaned_content)
        if len(bib_db.entries) > 0:
            logger.info(f"Parsed to {len(bib_db.entries)} entries.")
            return bib_db.entries
    except Exception as e:
        logger.fail(f"Parsing with bibtexparser failed {str(e)}")

    try:
        # Manual parsing fallback
        logger.info(f"Parsing {bibtex_path} using Regular Expressions...")
        entries = []
        pattern = r"@(article|inproceedings|book)\s*\{\s*([^,\s]+)\s*,(.*?)(?=\n@|\Z)"
        matches = re.findall(
            pattern, cleaned_content, re.DOTALL | re.IGNORECASE
        )


...
```


### `./utils/refresh_symlinks.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh project symlinks based on current MASTER metadata.

This utility regenerates all symlinks in a project directory based on the
current state of metadata in MASTER, without running any downloads or enrichment.

Usage:
    python -m scitex.scholar.utils.refresh_symlinks neurovista
    python -m scitex.scholar.utils.refresh_symlinks --project pac
"""

from pathlib import Path
import argparse
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.core.Scholar import Scholar
from scitex.logging import getLogger

logger = getLogger(__name__)


def refresh_project_symlinks(project: str) -> dict:
    """Refresh all symlinks in a project based on current MASTER metadata.

    Args:
        project: Project name

    Returns:
        Statistics dict with counts of refreshed, created, removed symlinks
    """
    scholar = Scholar(project=project)
    library_manager = scholar._library_manager

    project_dir = scholar.config.path_manager.get_library_dir(project)
    master_dir = scholar.config.path_manager.get_library_master_dir()

    stats = {
        "refreshed": 0,
        "created": 0,
        "removed": 0,
        "errors": 0,
    }

    # Remove all existing CC_ symlinks
    logger.info(f"Removing old symlinks in {project}...")

...
```


### `./utils/_TextNormalizer.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 18:30:00 (ywatanabe)"
# File: ./src/scitex/scholar/utils/_TextNormalizer.py
# ----------------------------------------
from __future__ import annotations

"""Text normalization utilities for improved DOI resolution.

This module provides utilities to normalize text for better matching
in DOI resolution, handling Unicode, LaTeX, and encoding issues.
"""

import re
import unicodedata
from typing import Dict, List


class TextNormalizer:
    """Normalize text for better matching in academic paper searches."""
    
    # LaTeX to Unicode mappings
    LATEX_UNICODE_MAP = {
        # Common accented characters
        r'\{\\\"u\}': 'ü', r'\{\\\"U\}': 'Ü',
        r'\{\\\"o\}': 'ö', r'\{\\\"O\}': 'Ö', 
        r'\{\\\"a\}': 'ä', r'\{\\\"A\}': 'Ä',
        r'\{\\\"e\}': 'ë', r'\{\\\"E\}': 'Ë',
        r'\{\\\"i\}': 'ï', r'\{\\\"I\}': 'Ï',
        
        # Circumflex
        r'\{\\^e\}': 'ê', r'\{\\^E\}': 'Ê',
        r'\{\\^a\}': 'â', r'\{\\^A\}': 'Â',
        r'\{\\^o\}': 'ô', r'\{\\^O\}': 'Ô',
        r'\{\\^u\}': 'û', r'\{\\^U\}': 'Û',
        r'\{\\^i\}': 'î', r'\{\\^I\}': 'Î',
        
        # Grave accent
        r'\{\\`e\}': 'è', r'\{\\`E\}': 'È',
        r'\{\\`a\}': 'à', r'\{\\`A\}': 'À',
        r'\{\\`o\}': 'ò', r'\{\\`O\}': 'Ò',
        r'\{\\`u\}': 'ù', r'\{\\`U\}': 'Ù',
        r'\{\\`i\}': 'ì', r'\{\\`I\}': 'Ì',
        
        # Acute accent
        r'\{\\\'e\}': 'é', r'\{\\\'E\}': 'É',
        r'\{\\\'a\}': 'á', r'\{\\\'A\}': 'Á',
        r'\{\\\'o\}': 'ó', r'\{\\\'O\}': 'Ó',
        r'\{\\\'u\}': 'ú', r'\{\\\'U\}': 'Ú',
        r'\{\\\'i\}': 'í', r'\{\\\'I\}': 'Í',

...
```


### `./utils/update_symlinks.py`

```python
#!/usr/bin/env python3
"""
Update symlinks utility for Scholar library.
This utility updates all symlinks in a project to reflect current status:
- Citation count (CITED)
- PDF availability (PDFo/PDFx)
- Impact factor (IF)
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._LibraryManager import LibraryManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SymlinkUpdater:
    """Utility to update Scholar library symlinks with current status."""

    def __init__(self, project: str = None):
        """Initialize the symlink updater.

        Args:
            project: Project name to update symlinks for. If None, updates all projects.
        """
        self.config = ScholarConfig()
        self.library_dir = self.config.get_library_dir()
        self.library_manager = LibraryManager(self.config)
        self.project = project

    def get_projects(self) -> List[str]:
        """Get list of projects to update.

        Returns:
            List of project directory names.
        """
        if self.project:
            project_dir = self.library_dir / self.project
            if not project_dir.exists():
                logger.error(f"Project {self.project} does not exist")
                return []
            return [self.project]

...
```


### `./utils/url_utils.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""URL utilities for Scholar.

Provides URL validation, normalization, and standardization functions.
"""

from typing import Optional
from urllib.parse import urlparse, urlunparse


def is_valid_url(url: Optional[str]) -> bool:
    """Check if URL is valid.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid and starts with http:// or https://

    Examples:
        >>> is_valid_url("https://doi.org/10.1038/nature12373")
        True
        >>> is_valid_url("10.1038/nature12373")
        False
        >>> is_valid_url(None)
        False
    """
    if not url:
        return False

    url_str = str(url).strip()

    # Must start with http:// or https://
    if not (url_str.startswith("https://") or url_str.startswith("http://")):
        return False

    # Basic URL parsing validation
    try:
        result = urlparse(url_str)
        # Must have scheme and netloc (domain)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def standardize_url(url: Optional[str]) -> Optional[str]:
    """Standardize URL format.

    - Ensures https:// scheme (upgrades http://)

...
```

