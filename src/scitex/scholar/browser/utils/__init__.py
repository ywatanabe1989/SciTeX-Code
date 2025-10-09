# Scholar-specific utilities (stay here)
from ._wait_redirects import wait_redirects
from ._close_unwanted_pages import close_unwanted_pages
from ._click_and_wait import click_and_wait
# from .JSLoader import JSLoader

__all__ = [
    # Scholar-specific
    # "JSLoader",
    "wait_redirects",
    "close_unwanted_pages",
    "click_and_wait",  # Scholar-specific (uses wait_redirects)
]
