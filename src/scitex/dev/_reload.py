#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 17:17:06 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dev/_reload.py


import importlib
import sys
import threading
import time
from typing import Any, Optional

_reload_thread: Optional[threading.Thread] = None
_running: bool = False


def reload() -> Any:  # Changed return type hint to Any
    """Reloads scitex package and its submodules."""
    import scitex

    scitex_modules = [mod for mod in sys.modules if mod.startswith("scitex")]
    for module in scitex_modules:
        try:
            importlib.reload(sys.modules[module])
        except Exception:
            pass
    return importlib.reload(scitex)


def reload_auto(interval: int = 10) -> None:
    """Start auto-reload in background thread."""
    global _reload_thread, _running

    if _reload_thread and _reload_thread.is_alive():
        return

    _running = True
    _reload_thread = threading.Thread(
        target=_auto_reload_loop, args=(interval,), daemon=True
    )
    _reload_thread.start()


def reload_stop() -> None:
    """Stop auto-reload."""
    global _running
    _running = False


def _auto_reload_loop(interval: int) -> None:
    while _running:
        try:
            reload()
        except Exception as e:
            print(f"Reload failed: {e}")
        time.sleep(interval)


# EOF
