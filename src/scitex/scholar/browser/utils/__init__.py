# Scholar-specific utilities (stay here)
from ._take_screenshot import take_screenshot
from ._wait_redirects import wait_redirects
from ._close_unwanted_pages import close_unwanted_pages
from .JSLoader import JSLoader

# Import universal utilities from elevated scitex.browser location
from scitex.browser.debugging import (
    show_popup_and_capture,
    show_grid,
    show_grid_async,
    highlight_element,
)
from scitex.browser.pdf import (
    detect_chrome_pdf_viewer,
    detect_chrome_pdf_viewer_async,
    click_download_for_chrome_pdf_viewer,
    click_download_for_chrome_pdf_viewer_async,
)
from scitex.browser.interaction import (
    click_center,
    click_center_async,
    click_and_wait,
    click_with_fallbacks,
    fill_with_fallbacks,
)

# Backward compatibility aliases
show_popup_message_async = show_popup_and_capture
show_popup_and_capture_async = show_popup_and_capture

__all__ = [
    # Scholar-specific
    "JSLoader",
    "take_screenshot",
    "wait_redirects",
    "close_unwanted_pages",

    # Universal utilities (re-exported from scitex.browser)
    "show_popup_and_capture",
    "show_popup_message_async",  # Backward compatibility
    "show_popup_and_capture_async",  # Backward compatibility
    "show_grid",
    "show_grid_async",
    "highlight_element",
    "detect_chrome_pdf_viewer",
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer",
    "click_download_for_chrome_pdf_viewer_async",
    "click_center",
    "click_center_async",
    "click_and_wait",
    "click_with_fallbacks",
    "fill_with_fallbacks",
]
