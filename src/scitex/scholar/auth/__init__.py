"""Authentication module for Scholar."""

from .ScholarAuthManager import ScholarAuthManager
from .core.AuthenticationGateway import AuthenticationGateway, URLContext

__all__ = [
    "ScholarAuthManager",
    "AuthenticationGateway",
    "URLContext",
]

# EOF
