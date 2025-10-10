"""Core authentication modules."""

from .AuthenticationGateway import AuthenticationGateway, URLContext
from .BrowserAuthenticator import BrowserAuthenticator
from .StrategyResolver import AuthenticationStrategyResolver, AuthenticationStrategy, AuthenticationMethod

__all__ = [
    "AuthenticationGateway",
    "URLContext",
    "BrowserAuthenticator",
    "AuthenticationStrategyResolver",
    "AuthenticationStrategy",
    "AuthenticationMethod",
]

# EOF
