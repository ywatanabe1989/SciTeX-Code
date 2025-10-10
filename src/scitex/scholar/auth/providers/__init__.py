"""Authentication provider implementations."""

from .BaseAuthenticator import BaseAuthenticator
from .OpenAthensAuthenticator import OpenAthensAuthenticator, OpenAthensError
from .EZProxyAuthenticator import EZProxyAuthenticator, EZProxyError
from .ShibbolethAuthenticator import ShibbolethAuthenticator, ShibbolethError

__all__ = [
    "BaseAuthenticator",
    "OpenAthensAuthenticator",
    "OpenAthensError",
    "EZProxyAuthenticator",
    "EZProxyError",
    "ShibbolethAuthenticator",
    "ShibbolethError",
]

# EOF
