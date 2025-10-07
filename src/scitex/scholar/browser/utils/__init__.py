# Scholar-specific utilities (stay here)
from ._take_screenshot import take_screenshot
from ._wait_redirects import wait_redirects
from ._close_unwanted_pages import close_unwanted_pages
from ._click_and_wait import click_and_wait
from .JSLoader import JSLoader

# Import universal utilities from elevated scitex.browser location
from scitex.browser.debugging import (
    show_popup_and_capture_async,
    show_grid_async,
    highlight_element_async,
)
from scitex.browser.pdf import (
    detect_chrome_pdf_viewer_async,
    click_download_for_chrome_pdf_viewer_async,
)
from scitex.browser.interaction import (
    click_center_async,
    click_with_fallbacks_async,
    fill_with_fallbacks_async,
)

# Backward compatibility aliases (old names without _async suffix)
show_popup_message_async = show_popup_and_capture_async
show_popup_and_capture = show_popup_and_capture_async
show_grid = show_grid_async
highlight_element = highlight_element_async
detect_chrome_pdf_viewer = detect_chrome_pdf_viewer_async
click_download_for_chrome_pdf_viewer = click_download_for_chrome_pdf_viewer_async
click_center = click_center_async
click_with_fallbacks = click_with_fallbacks_async
fill_with_fallbacks = fill_with_fallbacks_async

__all__ = [
    # Scholar-specific
    "JSLoader",
    "take_screenshot",
    "wait_redirects",
    "close_unwanted_pages",
    "click_and_wait",  # Scholar-specific (uses wait_redirects)

    # Universal utilities (re-exported from scitex.browser)
    "show_popup_and_capture_async",
    "show_grid_async",
    "highlight_element_async",
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer_async",
    "click_center_async",
    "click_with_fallbacks_async",
    "fill_with_fallbacks_async",
    # Backward compatibility (old names without _async suffix)
    "show_popup_message_async",
    "show_popup_and_capture",
    "show_grid",
    "highlight_element",
    "detect_chrome_pdf_viewer",
    "click_download_for_chrome_pdf_viewer",
    "click_center",
    "click_with_fallbacks",
    "fill_with_fallbacks",
]
