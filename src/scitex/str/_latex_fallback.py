#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 21:37:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/str/_latex_fallback.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/str/_latex_fallback.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-06-05 12:00:00 (ywatanabe)"


"""
LaTeX Fallback Mechanism for SciTeX

This module provides a robust fallback system for LaTeX rendering issues.
When LaTeX compilation fails (e.g., missing fonts, Node.js conflicts),
it gracefully degrades to mathtext or plain text alternatives.

Functionality:
    - Detect LaTeX rendering capabilities
    - Convert LaTeX to mathtext equivalents
    - Provide plain text fallbacks
    - Cache LaTeX capability status
Input:
    LaTeX strings and matplotlib configuration
Output:
    Fallback-compatible strings for matplotlib
Prerequisites:
    matplotlib
"""

import functools
import re
from typing import Any, Callable, Dict

from scitex import logging

# matplotlib imports moved to functions that need them

# Configure logging
logger = logging.getLogger(__name__)

# Global state for LaTeX capability
_latex_available = None
_fallback_mode = "auto"  # "auto", "force_mathtext", "force_plain"


class LaTeXFallbackError(Exception):
    """Raised when LaTeX fallback mechanisms fail."""

    pass


def set_fallback_mode(mode: str) -> None:
    """
    Set the global fallback mode for LaTeX rendering.

    Parameters
    ----------
    mode : str
        Fallback mode: "auto" (detect capability), "force_mathtext", or "force_plain"
    """
    global _fallback_mode
    if mode not in ["auto", "force_mathtext", "force_plain"]:
        raise ValueError(f"Invalid fallback mode: {mode}")
    _fallback_mode = mode
    # Reset capability cache when mode changes
    global _latex_available
    _latex_available = None


def get_fallback_mode() -> str:
    """Get the current fallback mode."""
    return _fallback_mode


@functools.lru_cache(maxsize=1)
def check_latex_capability() -> bool:
    """
    Check if LaTeX rendering is available and working.

    Returns
    -------
    bool
        True if LaTeX is available, False otherwise
    """
    global _latex_available

    # Import matplotlib here when actually needed
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        _latex_available = False
        return False

    # If forcing a mode, return accordingly
    if _fallback_mode == "force_mathtext" or _fallback_mode == "force_plain":
        _latex_available = False
        return False

    # Cache the result if already determined
    if _latex_available is not None:
        return _latex_available

    try:
        # Test if LaTeX is configured
        if not plt.rcParams.get("text.usetex", False):
            _latex_available = False
            return False

        # Try a simple LaTeX rendering test
        fig, ax = plt.subplots(figsize=(1, 1))
        try:
            # Test with a simple LaTeX expression
            text_obj = ax.text(0.5, 0.5, r"$x^2$", usetex=True)
            fig.canvas.draw()  # Force rendering
            _latex_available = True
            result = True
        except Exception as e:
            logger.debug(f"LaTeX capability test failed: {e}")
            _latex_available = False
            result = False
        finally:
            plt.close(fig)

        return result

    except Exception as e:
        logger.debug(f"LaTeX capability check failed: {e}")
        _latex_available = False
        return False


def latex_to_mathtext(latex_str: str) -> str:
    """
    Convert LaTeX syntax to matplotlib mathtext equivalent.

    Parameters
    ----------
    latex_str : str
        LaTeX string to convert

    Returns
    -------
    str
        Mathtext equivalent string
    """
    if not latex_str:
        return latex_str

    # Remove outer $ if present
    text = latex_str.strip()
    if text.startswith("$") and text.endswith("$"):
        text = text[1:-1]

    # Common LaTeX to mathtext conversions
    conversions = {
        # Greek letters
        r"\\alpha": r"\alpha",
        r"\\beta": r"\beta",
        r"\\gamma": r"\gamma",
        r"\\delta": r"\delta",
        r"\\epsilon": r"\epsilon",
        r"\\theta": r"\theta",
        r"\\lambda": r"\lambda",
        r"\\mu": r"\mu",
        r"\\pi": r"\pi",
        r"\\sigma": r"\sigma",
        r"\\tau": r"\tau",
        r"\\phi": r"\phi",
        r"\\omega": r"\omega",
        # Mathematical symbols
        r"\\sum": r"\sum",
        r"\\int": r"\int",
        r"\\partial": r"\partial",
        r"\\infty": r"\infty",
        r"\\pm": r"\pm",
        r"\\times": r"\times",
        r"\\cdot": r"\cdot",
        r"\\approx": r"\approx",
        r"\\neq": r"\neq",
        r"\\leq": r"\leq",
        r"\\geq": r"\geq",
        # Functions
        r"\\sin": r"\sin",
        r"\\cos": r"\cos",
        r"\\tan": r"\tan",
        r"\\log": r"\log",
        r"\\ln": r"\ln",
        r"\\exp": r"\exp",
        # Formatting (limited mathtext support)
        r"\\textbf\{([^}]+)\}": r"\mathbf{\1}",
        r"\\mathbf\{([^}]+)\}": r"\mathbf{\1}",
        r"\\textit\{([^}]+)\}": r"\mathit{\1}",
        r"\\mathit\{([^}]+)\}": r"\mathit{\1}",
        # Hats and accents
        r"\\hat\{([^}]+)\}": r"\hat{\1}",
        r"\\overrightarrow\{([^}]+)\}": r"\vec{\1}",
        r"\\vec\{([^}]+)\}": r"\vec{\1}",
        # Fractions (simple ones)
        r"\\frac\{([^}]+)\}\{([^}]+)\}": r"\frac{\1}{\2}",
        # Subscripts and superscripts (should work as-is)
        # Powers and indices are handled naturally by mathtext
    }

    # Apply conversions
    for latex_pattern, mathtext_replacement in conversions.items():
        text = re.sub(latex_pattern, mathtext_replacement, text)

    # Wrap in mathtext markers
    return f"${text}$"


def latex_to_unicode(latex_str: str) -> str:
    """
    Convert LaTeX to Unicode plain text equivalent.

    Parameters
    ----------
    latex_str : str
        LaTeX string to convert

    Returns
    -------
    str
        Unicode plain text equivalent
    """
    if not latex_str:
        return latex_str

    # Remove outer $ if present
    text = latex_str.strip()
    if text.startswith("$") and text.endswith("$"):
        text = text[1:-1]

    # Greek letters to Unicode
    greek_conversions = {
        r"\\alpha": "α",
        r"\\beta": "β",
        r"\\gamma": "γ",
        r"\\delta": "δ",
        r"\\epsilon": "ε",
        r"\\zeta": "ζ",
        r"\\eta": "η",
        r"\\theta": "θ",
        r"\\iota": "ι",
        r"\\kappa": "κ",
        r"\\lambda": "λ",
        r"\\mu": "μ",
        r"\\nu": "ν",
        r"\\xi": "ξ",
        r"\\pi": "π",
        r"\\rho": "ρ",
        r"\\sigma": "σ",
        r"\\tau": "τ",
        r"\\upsilon": "υ",
        r"\\phi": "φ",
        r"\\chi": "χ",
        r"\\psi": "ψ",
        r"\\omega": "ω",
        # Capital Greek
        r"\\Gamma": "Γ",
        r"\\Delta": "Δ",
        r"\\Theta": "Θ",
        r"\\Lambda": "Λ",
        r"\\Xi": "Ξ",
        r"\\Pi": "Π",
        r"\\Sigma": "Σ",
        r"\\Upsilon": "Υ",
        r"\\Phi": "Φ",
        r"\\Psi": "Ψ",
        r"\\Omega": "Ω",
    }

    # Mathematical symbols to Unicode
    symbol_conversions = {
        r"\\pm": "±",
        r"\\times": "×",
        r"\\cdot": "·",
        r"\\div": "÷",
        r"\\neq": "≠",
        r"\\leq": "≤",
        r"\\geq": "≥",
        r"\\approx": "≈",
        r"\\infty": "∞",
        r"\\partial": "∂",
        r"\\sum": "∑",
        r"\\int": "∫",
        r"\\sqrt": "√",
        r"\\angle": "∠",
        r"\\degree": "°",
    }

    # Superscript numbers
    superscript_conversions = {
        r"\^0": "⁰",
        r"\^1": "¹",
        r"\^2": "²",
        r"\^3": "³",
        r"\^4": "⁴",
        r"\^5": "⁵",
        r"\^6": "⁶",
        r"\^7": "⁷",
        r"\^8": "⁸",
        r"\^9": "⁹",
        r"\^\{0\}": "⁰",
        r"\^\{1\}": "¹",
        r"\^\{2\}": "²",
        r"\^\{3\}": "³",
        r"\^\{4\}": "⁴",
        r"\^\{5\}": "⁵",
        r"\^\{6\}": "⁶",
        r"\^\{7\}": "⁷",
        r"\^\{8\}": "⁸",
        r"\^\{9\}": "⁹",
    }

    # Subscript numbers
    subscript_conversions = {
        r"_0": "₀",
        r"_1": "₁",
        r"_2": "₂",
        r"_3": "₃",
        r"_4": "₄",
        r"_5": "₅",
        r"_6": "₆",
        r"_7": "₇",
        r"_8": "₈",
        r"_9": "₉",
        r"_\{0\}": "₀",
        r"_\{1\}": "₁",
        r"_\{2\}": "₂",
        r"_\{3\}": "₃",
        r"_\{4\}": "₄",
        r"_\{5\}": "₅",
        r"_\{6\}": "₆",
        r"_\{7\}": "₇",
        r"_\{8\}": "₈",
        r"_\{9\}": "₉",
    }

    # Apply all conversions
    all_conversions = {
        **greek_conversions,
        **symbol_conversions,
        **superscript_conversions,
        **subscript_conversions,
    }

    for latex_pattern, unicode_char in all_conversions.items():
        text = re.sub(latex_pattern, unicode_char, text)

    # Remove remaining LaTeX commands (simple cleanup)
    text = re.sub(
        r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text
    )  # \command{content} -> content
    text = re.sub(r"\\[a-zA-Z]+", "", text)  # \command -> remove
    text = re.sub(r"[{}]", "", text)  # Remove remaining braces

    return text


def safe_latex_render(
    text: str, fallback_strategy: str = "auto", preserve_math: bool = True
) -> str:
    """
    Safely render LaTeX text with automatic fallback.

    Parameters
    ----------
    text : str
        Text that may contain LaTeX
    fallback_strategy : str, optional
        Strategy when LaTeX fails: "auto", "mathtext", "unicode", "plain"
    preserve_math : bool, optional
        Whether to preserve mathematical notation in fallbacks

    Returns
    -------
    str
        Safely rendered text
    """
    if not text or not isinstance(text, str):
        return text

    # Import matplotlib when needed
    import matplotlib.pyplot as plt

    # Determine if we should attempt LaTeX
    use_latex = _fallback_mode == "auto" and check_latex_capability()

    if use_latex:
        # Try LaTeX first
        try:
            # Test rendering capability with the actual text
            fig, ax = plt.subplots(figsize=(1, 1))
            try:
                ax.text(0.5, 0.5, text, usetex=True)
                fig.canvas.draw()
                plt.close(fig)
                return text  # LaTeX works
            except Exception:
                plt.close(fig)
                raise LaTeXFallbackError("LaTeX rendering failed")
        except Exception:
            # Fall through to fallback strategies
            pass

    # Apply fallback strategy
    if fallback_strategy == "auto":
        # Automatically choose best fallback
        if preserve_math and ("$" in text or "\\" in text):
            try:
                return latex_to_mathtext(text)
            except Exception:
                return latex_to_unicode(text)
        else:
            return latex_to_unicode(text)

    elif fallback_strategy == "mathtext":
        return latex_to_mathtext(text)

    elif fallback_strategy == "unicode":
        return latex_to_unicode(text)

    elif fallback_strategy == "plain":
        # Strip all LaTeX and return plain text
        plain = latex_to_unicode(text)
        # Remove any remaining special characters
        plain = re.sub(r"[^\w\s\(\)\[\].,;:!?-]", "", plain)
        return plain

    else:
        raise ValueError(f"Unknown fallback strategy: {fallback_strategy}")


def latex_fallback_decorator(
    fallback_strategy: str = "auto", preserve_math: bool = True
):
    """
    Decorator to add LaTeX fallback capability to functions.

    Parameters
    ----------
    fallback_strategy : str, optional
        Fallback strategy to use
    preserve_math : bool, optional
        Whether to preserve mathematical notation

    Returns
    -------
    callable
        Decorated function with LaTeX fallback
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check if this is a LaTeX-related error
                error_str = str(e).lower()
                latex_error_indicators = [
                    "latex",
                    "tex",
                    "dvi",
                    "tfm",
                    "font",
                    "usetex",
                    "kpathsea",
                    "dvipng",
                    "ghostscript",
                ]

                if any(
                    indicator in error_str
                    for indicator in latex_error_indicators
                ):
                    logger.warning(f"LaTeX error in {func.__name__}: {e}")
                    logger.warning(
                        "Falling back to alternative text rendering"
                    )

                    # Try to apply fallback to string arguments
                    new_args = []
                    for arg in args:
                        if isinstance(arg, str):
                            new_args.append(
                                safe_latex_render(
                                    arg, fallback_strategy, preserve_math
                                )
                            )
                        else:
                            new_args.append(arg)

                    new_kwargs = {}
                    for key, value in kwargs.items():
                        if isinstance(value, str):
                            new_kwargs[key] = safe_latex_render(
                                value, fallback_strategy, preserve_math
                            )
                        else:
                            new_kwargs[key] = value

                    # Import matplotlib when needed
                    import matplotlib.pyplot as plt

                    # Temporarily disable LaTeX for this call
                    original_usetex = plt.rcParams.get("text.usetex", False)
                    plt.rcParams["text.usetex"] = False

                    try:
                        result = func(*new_args, **new_kwargs)
                        return result
                    finally:
                        plt.rcParams["text.usetex"] = original_usetex
                else:
                    # Re-raise non-LaTeX errors
                    raise

        return wrapper

    return decorator


def get_latex_status() -> Dict[str, Any]:
    """
    Get comprehensive LaTeX status information.

    Returns
    -------
    Dict[str, Any]
        Status information including capability, mode, and configuration
    """
    import matplotlib.pyplot as plt

    return {
        "latex_available": check_latex_capability(),
        "fallback_mode": get_fallback_mode(),
        "usetex_enabled": plt.rcParams.get("text.usetex", False),
        "mathtext_fontset": plt.rcParams.get("mathtext.fontset", "cm"),
        "font_family": plt.rcParams.get("font.family", ["serif"]),
        "cache_info": check_latex_capability.cache_info()._asdict(),
    }


# Convenience functions
def enable_latex_fallback(mode: str = "auto") -> None:
    """Enable LaTeX fallback with specified mode."""
    set_fallback_mode(mode)


def disable_latex_fallback() -> None:
    """Disable LaTeX fallback (force LaTeX usage)."""
    global _latex_available
    _latex_available = True  # Force LaTeX usage


def reset_latex_cache() -> None:
    """Reset the LaTeX capability cache."""
    check_latex_capability.cache_clear()
    global _latex_available
    _latex_available = None

# EOF
