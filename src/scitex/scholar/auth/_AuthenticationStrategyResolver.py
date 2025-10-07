#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-07 22:45:56 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_AuthenticationStrategyResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_AuthenticationStrategyResolver.py"
)
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
    """Resolves the best authentication strategy based on user information."""

    # Known institution configurations
    INSTITUTION_CONFIGS = {
        # University of Melbourne
        "unimelb.edu.au": {
            "name": "University of Melbourne",
            "openathens_supported": True,
            "direct_sso_url": "https://sso.unimelb.edu.au/",
            "openathens_redirects_to_sso": True,
            "sso_automator": "UniversityOfMelbourne",
        },
        # Add more institutions as needed
        "stanford.edu": {
            "name": "Stanford University",
            "openathens_supported": True,
            "direct_sso_url": "https://login.stanford.edu/",
            "openathens_redirects_to_sso": True,
            "sso_automator": None,
        },
        "mit.edu": {
            "name": "MIT",
            "openathens_supported": False,
            "direct_sso_url": "https://oidc.mit.edu/",
            "openathens_redirects_to_sso": False,
            "sso_automator": None,
        },
    }

    def __init__(self, config: Optional[ScholarConfig] = None):
        """Initialize resolver with configuration."""
        self.config = config or ScholarConfig()

    def resolve_strategy(
        self,
        openathens_email: Optional[str] = None,
        target_url: Optional[str] = None,
        institution_name: Optional[str] = None,
        prefer_openathens: bool = True,
    ) -> AuthenticationStrategy:
        """Resolve the best authentication strategy.

        Args:
            openathens_email: User's institutional email
            target_url: Target URL being accessed
            institution_name: Explicit institution name
            prefer_openathens: Whether to prefer OpenAthens when available

        Returns:
            AuthenticationStrategy with the recommended approach
        """
        logger.info("Resolving authentication strategy...")

        # Get email from config if not provided
        if not openathens_email:
            openathens_email = self.config.resolve(
                "openathens_email", None, None, str
            )

        if not openathens_email:
            logger.warn(
                "No email provided - defaulting to manual authentication"
            )
            return AuthenticationStrategy(
                method=AuthenticationMethod.MANUAL,
                primary_url=target_url
                or "https://my.openathens.net/?passiveLogin=false",
                confidence=0.0,
            )

        # Extract domain from email
        email_domain = self._extract_domain(openathens_email)
        institution_config = self.INSTITUTION_CONFIGS.get(email_domain)

        if institution_config:
            return self._resolve_known_institution_strategy(
                openathens_email,
                email_domain,
                institution_config,
                target_url,
                prefer_openathens,
            )
        else:
            return self._resolve_unknown_institution_strategy(
                openathens_email, email_domain, target_url, prefer_openathens
            )

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if "@" not in email:
            return email.lower()
        return email.split("@")[1].lower()

    def _resolve_known_institution_strategy(
        self,
        openathens_email: str,
        email_domain: str,
        institution_config: Dict[str, Any],
        target_url: Optional[str],
        prefer_openathens: bool,
    ) -> AuthenticationStrategy:
        """Resolve strategy for known institution."""

        institution_name = institution_config["name"]
        sso_automator_available = (
            institution_config.get("sso_automator") is not None
        )

        logger.info(
            f"Resolving strategy for known institution: {institution_name}"
        )

        # Determine primary method based on preferences and capabilities
        if prefer_openathens and institution_config.get(
            "openathens_supported", False
        ):
            if institution_config.get("openathens_redirects_to_sso", False):
                # OpenAthens → SSO flow
                method = AuthenticationMethod.OPENATHENS_TO_SSO
                primary_url = "https://my.openathens.net/?passiveLogin=false"
                confidence = 0.9 if sso_automator_available else 0.7
                fallback_methods = [
                    AuthenticationMethod.DIRECT_SSO,
                    AuthenticationMethod.MANUAL,
                ]
            else:
                # OpenAthens only
                method = AuthenticationMethod.OPENATHENS_ONLY
                primary_url = "https://my.openathens.net/?passiveLogin=false"
                confidence = 0.8
                fallback_methods = [
                    AuthenticationMethod.DIRECT_SSO,
                    AuthenticationMethod.MANUAL,
                ]
        else:
            # Direct SSO
            method = AuthenticationMethod.DIRECT_SSO
            primary_url = institution_config.get(
                "direct_sso_url", target_url or ""
            )
            confidence = 0.8 if sso_automator_available else 0.5
            fallback_methods = (
                [
                    AuthenticationMethod.OPENATHENS_TO_SSO,
                    AuthenticationMethod.MANUAL,
                ]
                if institution_config.get("openathens_supported", False)
                else [AuthenticationMethod.MANUAL]
            )

        return AuthenticationStrategy(
            method=method,
            primary_url=primary_url,
            openathens_email=openathens_email,
            sso_automator_available=sso_automator_available,
            institution_name=institution_name,
            confidence=confidence,
            fallback_methods=fallback_methods,
        )

    def _resolve_unknown_institution_strategy(
        self,
        openathens_email: str,
        email_domain: str,
        target_url: Optional[str],
        prefer_openathens: bool,
    ) -> AuthenticationStrategy:
        """Resolve strategy for unknown institution."""

        logger.info(
            f"Resolving strategy for unknown institution: {email_domain}"
        )

        # For unknown institutions, try OpenAthens first as it's most generic
        if prefer_openathens:
            method = AuthenticationMethod.OPENATHENS_TO_SSO
            primary_url = "https://my.openathens.net/?passiveLogin=false"
            confidence = 0.6  # Lower confidence for unknown institutions
            fallback_methods = [AuthenticationMethod.MANUAL]
        else:
            method = AuthenticationMethod.MANUAL
            primary_url = (
                target_url or "https://my.openathens.net/?passiveLogin=false"
            )
            confidence = 0.3
            fallback_methods = []

        return AuthenticationStrategy(
            method=method,
            primary_url=primary_url,
            openathens_email=openathens_email,
            sso_automator_available=False,
            institution_name=f"Unknown ({email_domain})",
            confidence=confidence,
            fallback_methods=fallback_methods,
        )

    def get_supported_institutions(self) -> List[str]:
        """Get list of supported institutions."""
        return [config["name"] for config in self.INSTITUTION_CONFIGS.values()]

    def add_institution_config(
        self,
        domain: str,
        name: str,
        openathens_supported: bool = True,
        direct_sso_url: Optional[str] = None,
        openathens_redirects_to_sso: bool = True,
        sso_automator: Optional[str] = None,
    ) -> None:
        """Add configuration for a new institution."""
        self.INSTITUTION_CONFIGS[domain.lower()] = {
            "name": name,
            "openathens_supported": openathens_supported,
            "direct_sso_url": direct_sso_url,
            "openathens_redirects_to_sso": openathens_redirects_to_sso,
            "sso_automator": sso_automator,
        }
        logger.info(f"Added institution configuration: {name} ({domain})")


if __name__ == "__main__":

    def main():
        """Test the authentication strategy resolver."""
        resolver = AuthenticationStrategyResolver()

        # Test known institution
        strategy = resolver.resolve_strategy(
            openathens_email="test@unimelb.edu.au"
        )
        print(
            f"UniMelb Strategy: {strategy.method.value}, URL: {strategy.primary_url}, Confidence: {strategy.confidence}"
        )

        # Test unknown institution
        strategy = resolver.resolve_strategy(
            openathens_email="test@unknown.edu"
        )
        print(
            f"Unknown Strategy: {strategy.method.value}, URL: {strategy.primary_url}, Confidence: {strategy.confidence}"
        )

        # Test manual fallback
        strategy = resolver.resolve_strategy()
        print(
            f"No Email Strategy: {strategy.method.value}, URL: {strategy.primary_url}, Confidence: {strategy.confidence}"
        )

    main()

# python -m scitex.scholar.auth._AuthenticationStrategyResolver

# EOF
