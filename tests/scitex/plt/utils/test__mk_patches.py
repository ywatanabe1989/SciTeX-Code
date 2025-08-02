#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-28 16:27:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/test__mk_patches.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/test__mk_patches.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pytest
import numpy as np


def test_mk_patches_basic():
    from scitex.plt.utils import mk_patches
    
    colors = ["#f00", "#0f0"]
    labels = ["a", "b"]
    patches = mk_patches(colors, labels)
    assert isinstance(patches, list)
    assert isinstance(patches[0], mpatches.Patch)
    assert patches[0].get_label() == "a"


def test_mk_patches_color_formats():
    """Test mk_patches with various color format inputs."""
    from scitex.plt.utils import mk_patches
    
    # Test different color formats
    color_formats = [
        (["red", "blue"], ["Red", "Blue"]),  # Named colors
        (["#FF0000", "#0000FF"], ["Hex Red", "Hex Blue"]),  # Hex colors
        ([(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)], ["RGB Red", "RGB Blue"]),  # RGB tuples
        ([(1.0, 0.0, 0.0, 0.5), (0.0, 0.0, 1.0, 0.8)], ["RGBA Red", "RGBA Blue"]),  # RGBA tuples
        (["r", "b"], ["Short Red", "Short Blue"]),  # Single letter colors
    ]
    
    for colors, labels in color_formats:
        patches = mk_patches(colors, labels)
        assert len(patches) == len(colors)
        assert all(isinstance(p, mpatches.Patch) for p in patches)
        
        # Check labels match
        for i, (patch, label) in enumerate(zip(patches, labels)):
            assert patch.get_label() == label


def test_mk_patches_empty_inputs():
    """Test mk_patches with empty inputs."""
    from scitex.plt.utils import mk_patches
    
    # Empty lists
    patches = mk_patches([], [])
    assert isinstance(patches, list)
    assert len(patches) == 0


def test_mk_patches_single_item():
    """Test mk_patches with single color and label."""
    from scitex.plt.utils import mk_patches
    
    colors = ["green"]
    labels = ["Single Item"]
    patches = mk_patches(colors, labels)
    
    assert len(patches) == 1
    assert patches[0].get_label() == "Single Item"
    assert patches[0].get_facecolor() is not None


def test_mk_patches_many_items():
    """Test mk_patches with many colors and labels."""
    from scitex.plt.utils import mk_patches
    
    # Create 20 colors and labels
    colors = plt.cm.tab20(np.linspace(0, 1, 20))
    labels = [f"Label {i}" for i in range(20)]
    
    patches = mk_patches(colors, labels)
    
    assert len(patches) == 20
    for i, patch in enumerate(patches):
        assert patch.get_label() == f"Label {i}"


def test_mk_patches_mismatched_lengths():
    """Test mk_patches behavior with mismatched color and label lengths."""
    from scitex.plt.utils import mk_patches
    
    # More colors than labels - should create patches for matching pairs
    colors = ["red", "blue", "green"]
    labels = ["Label 1", "Label 2"]
    patches = mk_patches(colors, labels)
    
    # zip stops at shortest list
    assert len(patches) == 2
    assert patches[0].get_label() == "Label 1"
    assert patches[1].get_label() == "Label 2"
    
    # More labels than colors
    colors = ["red", "blue"]
    labels = ["Label 1", "Label 2", "Label 3"]
    patches = mk_patches(colors, labels)
    
    assert len(patches) == 2


def test_mk_patches_special_characters():
    """Test mk_patches with special characters in labels."""
    from scitex.plt.utils import mk_patches
    
    colors = ["red", "blue", "green"]
    labels = ["α-test", "β_value", "γ²"]
    
    patches = mk_patches(colors, labels)
    
    assert len(patches) == 3
    assert patches[0].get_label() == "α-test"
    assert patches[1].get_label() == "β_value"
    assert patches[2].get_label() == "γ²"


def test_mk_patches_color_properties():
    """Test that patch color properties are set correctly."""
    from scitex.plt.utils import mk_patches
    
    colors = ["red", "blue"]
    labels = ["Red Patch", "Blue Patch"]
    
    patches = mk_patches(colors, labels)
    
    # Check red patch
    red_color = patches[0].get_facecolor()
    assert red_color[0] > 0.9  # High red component
    assert red_color[1] < 0.1  # Low green component
    assert red_color[2] < 0.1  # Low blue component
    
    # Check blue patch
    blue_color = patches[1].get_facecolor()
    assert blue_color[0] < 0.1  # Low red component
    assert blue_color[1] < 0.1  # Low green component
    assert blue_color[2] > 0.9  # High blue component


def test_mk_patches_with_legend():
    """Test mk_patches integration with matplotlib legend."""
    from scitex.plt.utils import mk_patches
    
    fig, ax = plt.subplots()
    
    colors = ["red", "blue", "green"]
    labels = ["Category A", "Category B", "Category C"]
    
    patches = mk_patches(colors, labels)
    legend = ax.legend(handles=patches)
    
    # Check legend was created
    assert legend is not None
    assert len(legend.get_patches()) == 3
    
    # Check legend labels
    texts = legend.get_texts()
    assert len(texts) == 3
    assert texts[0].get_text() == "Category A"
    assert texts[1].get_text() == "Category B"
    assert texts[2].get_text() == "Category C"
    
    plt.close(fig)


def test_mk_patches_patch_properties():
    """Test individual patch properties."""
    from scitex.plt.utils import mk_patches
    
    colors = ["red"]
    labels = ["Test Patch"]
    
    patches = mk_patches(colors, labels)
    patch = patches[0]
    
    # Check patch properties
    assert patch.get_label() == "Test Patch"
    assert patch.get_edgecolor() == (0, 0, 0, 1)  # Default black edge
    assert patch.get_linewidth() == 1.0  # Default linewidth
    assert patch.get_linestyle() == '-'  # Default solid line
    assert patch.get_visible() is True


def test_mk_patches_invalid_colors():
    """Test mk_patches with invalid color specifications."""
    from scitex.plt.utils import mk_patches
    
    # Invalid color names should raise ValueError in matplotlib
    colors = ["invalid_color_name"]
    labels = ["Test"]
    
    with pytest.raises(ValueError):
        patches = mk_patches(colors, labels)
        # Force color validation by accessing facecolor
        _ = patches[0].get_facecolor()


def test_mk_patches_numeric_labels():
    """Test mk_patches with numeric labels."""
    from scitex.plt.utils import mk_patches
    
    colors = ["red", "blue", "green"]
    labels = [1, 2.5, 3]  # Numeric labels
    
    patches = mk_patches(colors, labels)
    
    # Matplotlib converts numeric labels to strings
    assert patches[0].get_label() == "1"
    assert patches[1].get_label() == "2.5"
    assert patches[2].get_label() == "3"


def test_mk_patches_none_values():
    """Test mk_patches with None values in labels."""
    from scitex.plt.utils import mk_patches
    
    colors = ["red", "blue"]
    labels = ["Label 1", None]
    
    patches = mk_patches(colors, labels)
    
    assert patches[0].get_label() == "Label 1"
    assert patches[1].get_label() == "None"  # Matplotlib converts None to string


def test_mk_patches_transparency():
    """Test mk_patches with transparent colors."""
    from scitex.plt.utils import mk_patches
    
    # RGBA colors with transparency
    colors = [(1, 0, 0, 0.5), (0, 0, 1, 0.3)]
    labels = ["Semi-transparent Red", "Semi-transparent Blue"]
    
    patches = mk_patches(colors, labels)
    
    # Check alpha values
    assert patches[0].get_facecolor()[3] == 0.5
    assert patches[1].get_facecolor()[3] == 0.3

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_mk_patches.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 21:18:45 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_mk_patches.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/_mk_patches.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import matplotlib.patches as mpatches
# 
# 
# def mk_patches(colors, labels):
#     """
#     colors = ["red", "blue"]
#     labels = ["label_1", "label_2"]
#     ax.legend(handles=scitex.plt.mk_patches(colors, labels))
#     """
# 
#     patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors, labels)]
#     return patches
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_mk_patches.py
# --------------------------------------------------------------------------------
