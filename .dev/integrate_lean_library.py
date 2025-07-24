#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 03:30:00 (ywatanabe)"
# File: ./.dev/integrate_lean_library.py
# ----------------------------------------

"""
Script to integrate Lean Library into Scholar module as the primary institutional access method.

This script:
1. Adds Lean Library configuration to ScholarConfig
2. Updates PDFDownloader to use Lean Library as primary strategy
3. Updates documentation
"""

import re
from pathlib import Path

# Step 1: Add Lean Library configuration to ScholarConfig
config_file = Path("src/scitex/scholar/_Config.py")
config_content = config_file.read_text()

# Find the position after OpenAthens configuration
openathens_end = config_content.find('user_agent: str = "SciTeX-Scholar/1.0"')
if openathens_end == -1:
    print("Error: Could not find insertion point in Config.py")
    exit(1)

# Add Lean Library configuration before user_agent
lean_library_config = '''    
    # Lean Library browser extension support
    use_lean_library: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_USE_LEAN_LIBRARY", "true").lower() == "true"
    )
    lean_library_browser_profile: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_LEAN_LIBRARY_BROWSER_PROFILE")
    )
    '''

# Insert the config
config_lines = config_content.split('\n')
for i, line in enumerate(config_lines):
    if 'user_agent: str = "SciTeX-Scholar/1.0"' in line:
        # Insert before this line
        config_lines[i:i] = lean_library_config.strip().split('\n')
        break

# Update to_dict method to include lean library settings
for i, line in enumerate(config_lines):
    if '"user_agent": self.user_agent,' in line:
        config_lines.insert(i, '            "use_lean_library": self.use_lean_library,')
        config_lines.insert(i+1, '            "lean_library_browser_profile": self.lean_library_browser_profile,')
        break

config_file.write_text('\n'.join(config_lines))
print("✅ Updated ScholarConfig with Lean Library settings")

# Step 2: Update PDFDownloader to import and use Lean Library
downloader_file = Path("src/scitex/scholar/_PDFDownloader.py")
downloader_content = downloader_file.read_text()

# Add import
import_line = "from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner"
import_idx = downloader_content.find(import_line)
if import_idx != -1:
    import_end = import_idx + len(import_line)
    new_import = "\nfrom ._LeanLibraryAuthenticator import LeanLibraryAuthenticator"
    downloader_content = downloader_content[:import_end] + new_import + downloader_content[import_end:]
    print("✅ Added LeanLibraryAuthenticator import")

# Initialize Lean Library in __init__
init_section = downloader_content.find("# Track downloads to avoid duplicates")
if init_section != -1:
    lean_init = '''        # Lean Library browser extension support
        self.use_lean_library = getattr(config, 'use_lean_library', True) if config else True
        self.lean_library_authenticator = None
        if self.use_lean_library:
            try:
                self.lean_library_authenticator = LeanLibraryAuthenticator(config)
                logger.info("Lean Library authenticator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Lean Library: {e}")
                self.use_lean_library = False

        '''
    downloader_content = downloader_content[:init_section] + lean_init + downloader_content[init_section:]
    print("✅ Added Lean Library initialization")

# Add Lean Library strategy method
strategy_methods = downloader_content.find("    async def _try_openathens_async(")
if strategy_methods != -1:
    lean_method = '''    async def _try_lean_library_async(
        self, identifier: str, url: str, output_path: Path
    ) -> Optional[Path]:
        """Try downloading using Lean Library browser extension."""
        if not self.lean_library_authenticator:
            return None
            
        try:
            logger.info("Attempting download with Lean Library...")
            
            # Check if Lean Library is available
            if not await self.lean_library_authenticator.is_available_async():
                logger.warning("Lean Library not available (no browser profile found)")
                return None
            
            # Try to download with extension
            result = await self.lean_library_authenticator.download_with_extension_async(
                url, output_path, timeout=self.timeout * 1000
            )
            
            if result:
                logger.info(f"Successfully downloaded with Lean Library: {output_path}")
                return output_path
            else:
                logger.warning("Lean Library could not access the PDF")
                return None
                
        except Exception as e:
            logger.error(f"Lean Library download failed: {e}")
            return None

    '''
    downloader_content = downloader_content[:strategy_methods] + lean_method + downloader_content[strategy_methods:]
    print("✅ Added _try_lean_library_async method")

# Update download strategies to include Lean Library as primary
strategies_section = downloader_content.find('strategies = [')
if strategies_section != -1:
    # Find both strategy blocks and update them
    # First block (with OpenAthens)
    auth_strategies = re.search(
        r'if auth_session and self\.use_openathens.*?strategies = \[(.*?)\]',
        downloader_content,
        re.DOTALL
    )
    if auth_strategies:
        old_block = auth_strategies.group(0)
        new_block = old_block.replace(
            'strategies = [',
            '''strategies = [
                ("Lean Library", self._try_lean_library_async),  # Primary - browser extension'''
        )
        downloader_content = downloader_content.replace(old_block, new_block)
    
    # Second block (without OpenAthens)
    else_strategies = re.search(
        r'else:\s*strategies = \[(.*?)\]',
        downloader_content,
        re.DOTALL
    )
    if else_strategies:
        old_block = else_strategies.group(0)
        new_block = old_block.replace(
            'strategies = [',
            '''strategies = [
                ("Lean Library", self._try_lean_library_async),  # Primary - browser extension'''
        )
        downloader_content = downloader_content.replace(old_block, new_block)
    
    print("✅ Updated download strategies to prioritize Lean Library")

# Update _should_use_strategy to include Lean Library
should_use = downloader_content.find('def _should_use_strategy(self, name: str) -> bool:')
if should_use != -1:
    # Find the method body
    method_end = downloader_content.find('return True', should_use)
    if method_end != -1:
        # Insert before the final return True
        lean_check = '''        if name == "Lean Library":
            return self.use_lean_library and self.lean_library_authenticator is not None
        '''
        downloader_content = downloader_content[:method_end] + lean_check + downloader_content[method_end:]
        print("✅ Updated _should_use_strategy for Lean Library")

# Save the updated PDFDownloader
downloader_file.write_text(downloader_content)

# Step 3: Update default config YAML
config_yaml = Path("src/scitex/scholar/config/default_config.yaml")
if config_yaml.exists():
    yaml_content = config_yaml.read_text()
    
    # Add Lean Library section after OpenAthens
    openathens_section = yaml_content.find("# OpenAthens")
    if openathens_section != -1:
        # Find the end of OpenAthens section
        next_section = yaml_content.find("\n# ", openathens_section + 1)
        if next_section == -1:
            next_section = len(yaml_content)
        
        lean_section = '''
# Lean Library browser extension support
# Lean Library is a browser extension that provides automatic institutional access
# It's used by many universities and provides a better experience than OpenAthens
use_lean_library: true
# Optional: specify browser profile path if auto-detection fails
# lean_library_browser_profile: /path/to/browser/profile

'''
        yaml_content = yaml_content[:next_section] + lean_section + yaml_content[next_section:]
        config_yaml.write_text(yaml_content)
        print("✅ Updated default_config.yaml")

print("\n✅ Lean Library integration complete!")
print("\nNext steps:")
print("1. Test the integration with: python examples/scholar/lean_library_example.py")
print("2. Update README with Lean Library installation instructions")
print("3. Create user documentation for Lean Library setup")