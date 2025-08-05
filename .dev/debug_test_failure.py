#!/usr/bin/env python3
"""Debug test failure."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.utils import TextNormalizer

def debug_test():
    input_text = '<p>H{"u}lsemann et al. studied <i>neural networks</i></p>'
    expected = 'Hülsemann et al. studied neural networks'
    
    cleaned = TextNormalizer.clean_metadata_text(input_text)
    
    print(f"Input:    {repr(input_text)}")
    print(f"Expected: {repr(expected)}")
    print(f"Cleaned:  {repr(cleaned)}")
    print(f"Equal?    {cleaned == expected}")
    
    # Character by character comparison
    print("\nCharacter comparison:")
    for i, (c1, c2) in enumerate(zip(cleaned, expected)):
        if c1 != c2:
            print(f"  Diff at pos {i}: {repr(c1)} vs {repr(c2)}")
            break
    else:
        if len(cleaned) != len(expected):
            print(f"  Length diff: {len(cleaned)} vs {len(expected)}")

if __name__ == "__main__":
    debug_test()