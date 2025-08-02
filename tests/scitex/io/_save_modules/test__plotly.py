#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 14:20:05 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/io/_save_modules/test__plotly.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/io/_save_modules/test__plotly.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import os
import tempfile
import pytest
import re


def _is_plotly_available():
    """Check if Plotly is available."""
    try:
        import plotly
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _is_plotly_available(), reason="Plotly is not installed")
def test_save_plotly_html_simple():
    """Test saving a simple Plotly figure to HTML."""
    from scitex.io._save_modules import _save_plotly_html
    import plotly.graph_objects as go
    
    # Create a simple Plotly figure
    fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
    fig.update_layout(title="Test Figure")
    
    # Create temp file path
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        temp_path = tmp.name
        
    try:
        # Save the figure
        _save_plotly_html(fig, temp_path)
        
        # Verify the file exists
        assert os.path.exists(temp_path)
        
        # Read the HTML file and check for plotly elements
        with open(temp_path, 'r') as f:
            content = f.read()
            
            # Check that it's a proper HTML file
            assert '<html>' in content
            
            # Check for plotly-specific contents
            assert 'plotly' in content.lower()
            assert 'scatter' in content.lower()
            assert 'Test Figure' in content  # Title should be in the HTML
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.skipif(not _is_plotly_available(), reason="Plotly is not installed")
def test_save_plotly_html_complex():
    """Test saving a more complex Plotly figure to HTML."""
    from scitex.io._save_modules import _save_plotly_html
    import plotly.graph_objects as go
    
    # Create a more complex Plotly figure with multiple traces
    fig = go.Figure()
    
    # Add scatter trace
    fig.add_trace(go.Scatter(
        x=[0, 1, 2, 3, 4, 5],
        y=[0, 1, 4, 9, 16, 25],
        name='Quadratic'
    ))
    
    # Add bar trace
    fig.add_trace(go.Bar(
        x=[0, 1, 2, 3, 4, 5],
        y=[1, 2, 3, 4, 5, 6],
        name='Linear'
    ))
    
    # Update layout
    fig.update_layout(
        title='Test Complex Figure',
        xaxis_title='X Axis',
        yaxis_title='Y Axis',
        template='plotly_dark'
    )
    
    # Create temp file path
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        temp_path = tmp.name
        
    try:
        # Save the figure
        _save_plotly_html(fig, temp_path)
        
        # Verify the file exists
        assert os.path.exists(temp_path)
        
        # Read the HTML file and check for plotly elements
        with open(temp_path, 'r') as f:
            content = f.read()
            
            # Check for traces and layout elements
            assert 'Quadratic' in content
            assert 'Linear' in content
            assert 'Test Complex Figure' in content
            assert 'X Axis' in content
            assert 'Y Axis' in content
            
            # Check for both scatter and bar traces
            assert re.search(r'scatter', content, re.IGNORECASE)
            assert re.search(r'bar', content, re.IGNORECASE)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.skipif(not _is_plotly_available(), reason="Plotly is not installed")
def test_save_plotly_html_invalid_input():
    """Test that _save_plotly_html raises TypeError for non-Plotly figures."""
    from scitex.io._save_modules import _save_plotly_html
    
    # Create a non-Plotly object
    test_object = {"data": [1, 2, 3]}
    
    # Create temp file path
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        temp_path = tmp.name
        
    try:
        # Try to save the non-Plotly object, should raise TypeError
        with pytest.raises(TypeError):
            _save_plotly_html(test_object, temp_path)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_plotly.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:30:15 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_plotly.py
# 
# import plotly
# 
# 
# def _save_plotly_html(obj, spath):
#     """
#     Save a Plotly figure as an HTML file.
#     
#     Parameters
#     ----------
#     obj : plotly.graph_objs.Figure
#         The Plotly figure to save.
#     spath : str
#         Path where the HTML file will be saved.
#         
#     Returns
#     -------
#     None
#     """
#     if isinstance(obj, plotly.graph_objs.Figure):
#         obj.write_html(file=spath)
#     else:
#         raise TypeError("Object must be a plotly.graph_objs.Figure")
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_plotly.py
# --------------------------------------------------------------------------------
