#!/usr/bin/env python3
"""
Centralized Browser Configuration System

Standardizes browser window modes across the entire Scholar system.
Ensures consistent invisible/visible/debug modes for different use cases.

Addresses user requirement: "we only need visible mode during when authentication 
is required manually and debug is needed"
"""

import os
from enum import Enum
from typing import Tuple, Optional
from dataclasses import dataclass
from scitex import logging

logger = logging.getLogger(__name__)


class BrowserMode(Enum):
    """Standardized browser window modes."""
    
    # Production mode: Completely invisible, automated operation
    INVISIBLE = "invisible"
    
    # Authentication mode: Visible for manual login/interaction
    AUTH = "auth"
    
    # Debug mode: Visible for development and troubleshooting
    DEBUG = "debug"
    
    # Test mode: Configurable for testing different scenarios
    TEST = "test"


@dataclass
class BrowserConfiguration:
    """Complete browser configuration for consistent setup."""
    
    mode: BrowserMode
    headless: bool
    invisible: bool
    viewport_size: Tuple[int, int]
    window_position: Optional[Tuple[int, int]]
    capture_screenshots: bool
    profile_name: str
    
    def __str__(self) -> str:
        return f"BrowserConfig({self.mode.value}, {self.viewport_size[0]}x{self.viewport_size[1]}, {'headless' if self.headless else 'visible'})"


class BrowserConfigManager:
    """
    Centralized manager for browser configuration across the Scholar system.
    
    This ensures all BrowserManager instances use consistent settings
    based on the current operational mode.
    """
    
    def __init__(self):
        """Initialize with environment-based default mode."""
        self._current_mode = self._detect_default_mode()
        self._override_settings = {}
        
    def _detect_default_mode(self) -> BrowserMode:
        """Detect appropriate default mode from environment."""
        
        # Check for explicit mode setting
        env_mode = os.getenv("SCITEX_SCHOLAR_BROWSER_MODE", "").lower()
        if env_mode:
            try:
                return BrowserMode(env_mode)
            except ValueError:
                logger.warning(f"Unknown browser mode '{env_mode}', using default")
        
        # Auto-detect based on environment
        debug_env_vars = [
            "SCITEX_SCHOLAR_DEBUG",
            "SCITEX_SCHOLAR_DEBUG_MODE", 
            "DEBUG"
        ]
        for debug_var in debug_env_vars:
            if os.getenv(debug_var, "").lower() in ("1", "true", "yes"):
                return BrowserMode.DEBUG
        
        if os.getenv("CI", "").lower() in ("1", "true"):
            return BrowserMode.INVISIBLE  # CI environment
            
        # Check if authentication is likely needed
        if not self._has_valid_auth_cache():
            logger.info("No auth cache found, using AUTH mode for initial setup")
            return BrowserMode.AUTH
        
        # Default to invisible for production use
        return BrowserMode.INVISIBLE
    
    def _has_valid_auth_cache(self) -> bool:
        """Check if valid authentication cache exists."""
        try:
            from ..utils._scholar_paths import scholar_paths
            # Check both new and legacy locations for user sessions
            user_sessions = scholar_paths.find_user_session_dirs()
            for session_dir in user_sessions:
                auth_cache = session_dir / "openathens_session.json"
                if auth_cache.exists() and auth_cache.stat().st_size > 100:
                    return True
            return False
        except:
            return False
    
    def get_config(
        self, 
        mode: Optional[BrowserMode] = None,
        profile_name: str = "scholar_default",
        capture_screenshots: bool = False
    ) -> BrowserConfiguration:
        """
        Get browser configuration for specified mode.
        
        Args:
            mode: Override mode (uses current mode if None)
            profile_name: Browser profile name
            capture_screenshots: Enable screenshot capture
            
        Returns:
            Complete browser configuration
        """
        active_mode = mode or self._current_mode
        
        # Apply any override settings
        overrides = self._override_settings.get(active_mode, {})
        
        # Generate configuration based on mode
        if active_mode == BrowserMode.INVISIBLE:
            config = BrowserConfiguration(
                mode=active_mode,
                headless=False,  # Must be False for dimension spoofing to work
                invisible=True,
                viewport_size=(1, 1),  # 1x1 pixel for complete invisibility
                window_position=(0, 0),  # Top-left corner
                capture_screenshots=capture_screenshots,
                profile_name=profile_name
            )
            
        elif active_mode == BrowserMode.AUTH:
            config = BrowserConfiguration(
                mode=active_mode,
                headless=False,  # Must be visible for manual interaction
                invisible=False,
                viewport_size=(1200, 800),  # Comfortable size for login
                window_position=(100, 100),  # Visible but not centered
                capture_screenshots=True,  # Always capture during auth
                profile_name=profile_name
            )
            
        elif active_mode == BrowserMode.DEBUG:
            config = BrowserConfiguration(
                mode=active_mode,
                headless=False,  # Visible for debugging
                invisible=False,
                viewport_size=(1920, 1080),  # Full desktop size
                window_position=None,  # Let window manager decide
                capture_screenshots=True,  # Always capture during debug
                profile_name=profile_name
            )
            
        elif active_mode == BrowserMode.TEST:
            config = BrowserConfiguration(
                mode=active_mode,
                headless=overrides.get('headless', False),
                invisible=overrides.get('invisible', True),
                viewport_size=overrides.get('viewport_size', (1, 1)),
                window_position=overrides.get('window_position', (0, 0)),
                capture_screenshots=overrides.get('capture_screenshots', True),
                profile_name=profile_name
            )
            
        else:
            raise ValueError(f"Unknown browser mode: {active_mode}")
        
        # Apply overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        logger.info(f"🔧 Browser configuration: {config}")
        return config
    
    def set_mode(self, mode: BrowserMode, temporary: bool = False):
        """
        Set the current browser mode.
        
        Args:
            mode: New browser mode
            temporary: If True, mode will reset after process restart
        """
        old_mode = self._current_mode
        self._current_mode = mode
        
        if not temporary:
            # Persist mode to environment for future runs
            os.environ["SCITEX_SCHOLAR_BROWSER_MODE"] = mode.value
        
        logger.info(f"🔄 Browser mode changed: {old_mode.value} → {mode.value}")
    
    def set_override(self, mode: BrowserMode, **overrides):
        """
        Set configuration overrides for specific mode.
        
        Args:
            mode: Mode to override
            **overrides: Configuration parameters to override
        """
        if mode not in self._override_settings:
            self._override_settings[mode] = {}
        
        self._override_settings[mode].update(overrides)
        logger.info(f"🔧 Override set for {mode.value}: {overrides}")
    
    def clear_overrides(self, mode: Optional[BrowserMode] = None):
        """Clear configuration overrides."""
        if mode:
            self._override_settings.pop(mode, None)
            logger.info(f"🧹 Cleared overrides for {mode.value}")
        else:
            self._override_settings.clear()
            logger.info("🧹 Cleared all overrides")
    
    def force_invisible_mode(self):
        """Force invisible mode for automated operation."""
        self.set_mode(BrowserMode.INVISIBLE)
    
    def force_visible_mode(self):
        """Force visible mode for manual interaction."""
        self.set_mode(BrowserMode.AUTH)
    
    def is_invisible(self) -> bool:
        """Check if current mode is invisible."""
        return self._current_mode == BrowserMode.INVISIBLE
    
    def is_visible(self) -> bool:
        """Check if current mode requires visible window."""
        return self._current_mode in (BrowserMode.AUTH, BrowserMode.DEBUG)
    
    def get_mode_description(self) -> str:
        """Get human-readable description of current mode."""
        descriptions = {
            BrowserMode.INVISIBLE: "🎭 Invisible mode (1x1 pixel, automated operation)",
            BrowserMode.AUTH: "🔐 Authentication mode (visible for manual login)",
            BrowserMode.DEBUG: "🐛 Debug mode (visible for development)",
            BrowserMode.TEST: "🧪 Test mode (configurable for testing)"
        }
        return descriptions.get(self._current_mode, f"Unknown mode: {self._current_mode}")


# Global configuration manager instance
browser_config = BrowserConfigManager()


def get_browser_config(
    mode: Optional[BrowserMode] = None,
    profile_name: str = "scholar_default", 
    capture_screenshots: bool = False
) -> BrowserConfiguration:
    """
    Convenience function to get browser configuration.
    
    This should be used by all components that create BrowserManager instances
    to ensure consistent configuration across the system.
    """
    return browser_config.get_config(mode, profile_name, capture_screenshots)


def set_browser_mode(mode: BrowserMode, temporary: bool = False):
    """Convenience function to set browser mode."""
    browser_config.set_mode(mode, temporary)


def force_invisible_mode():
    """Force system into invisible mode."""
    browser_config.force_invisible_mode()


def force_visible_mode():
    """Force system into visible mode."""
    browser_config.force_visible_mode()


if __name__ == "__main__":
    # Example usage and testing
    print("🔧 Browser Configuration System")
    print("=" * 50)
    
    # Test different modes
    for mode in BrowserMode:
        config = get_browser_config(mode)
        print(f"{mode.value:12} → {config}")
    
    print("\n📊 Current system mode:")
    print(f"Mode: {browser_config._current_mode.value}")
    print(f"Description: {browser_config.get_mode_description()}")
    print(f"Invisible: {browser_config.is_invisible()}")
    print(f"Visible: {browser_config.is_visible()}")