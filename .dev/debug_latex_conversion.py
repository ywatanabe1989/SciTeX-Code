#!/usr/bin/env python3
"""Debug LaTeX conversion."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.utils import TextNormalizer

def debug_latex():
    test_text = 'H{\"u}lsemann et al. studied neural networks'
    
    print(f"Original: {test_text}")
    print(f"Raw repr: {repr(test_text)}")
    
    # Test the internal method directly
    converted = TextNormalizer._convert_latex_to_unicode(test_text)
    print(f"Converted: {converted}")
    print(f"Converted repr: {repr(converted)}")
    
    # Let's check what patterns are being used
    print("\nChecking patterns:")
    pattern = r'\{\"u\}'
    print(f"Looking for: {repr(pattern)}")
    
    import re
    # Test individual pattern
    result = re.sub(r'\{\"u\}', 'ü', test_text)
    print(f"Pattern result: {result}")

if __name__ == "__main__":
    debug_latex()