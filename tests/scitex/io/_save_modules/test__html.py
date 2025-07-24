#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:55:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__html.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__html.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for HTML saving functionality (Plotly figures)
"""

import os
import tempfile
import pytest
from pathlib import Path

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

    from scitex.io._save_modules import save_html


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not installed")
class TestSaveHTML:
    """Test suite for save_html function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.html")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_plotly_figure(self):
        """Test saving simple Plotly figure"""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13])])
        fig.update_layout(title="Simple Plot")
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)
        
        # Check file contains expected content
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert 'plotly' in content.lower()
        assert 'Simple Plot' in content

    def test_save_interactive_scatter_plot(self):
        """Test saving interactive scatter plot"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[2, 4, 3, 5, 6],
            mode='markers+lines',
            name='Data',
            marker=dict(size=10, color='blue'),
            line=dict(width=2, color='blue')
        ))
        fig.update_layout(
            title="Interactive Scatter Plot",
            xaxis_title="X Axis",
            yaxis_title="Y Axis",
            hovermode='closest'
        )
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)
        assert os.path.getsize(self.test_file) > 1000  # Should have substantial content

    def test_save_3d_surface_plot(self):
        """Test saving 3D surface plot"""
        import numpy as np
        
        # Create 3D surface data
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=Z)])
        fig.update_layout(
            title="3D Surface Plot",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z"
            )
        )
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_save_multiple_subplots(self):
        """Test saving figure with subplots"""
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4")
        )
        
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]), row=1, col=1)
        fig.add_trace(go.Bar(x=[1, 2, 3], y=[6, 5, 4]), row=1, col=2)
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[2, 3, 4]), row=2, col=1)
        fig.add_trace(go.Bar(x=[1, 2, 3], y=[4, 3, 2]), row=2, col=2)
        
        fig.update_layout(title="Multiple Subplots", showlegend=False)
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_save_with_custom_config(self):
        """Test saving with custom Plotly config"""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
        }
        
        save_html(fig, self.test_file, config=config)
        
        assert os.path.exists(self.test_file)

    def test_save_with_auto_open(self):
        """Test saving with auto_open parameter"""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        
        # Set auto_open=False to prevent browser opening during tests
        save_html(fig, self.test_file, auto_open=False)
        
        assert os.path.exists(self.test_file)

    def test_save_animated_plot(self):
        """Test saving animated plot"""
        import numpy as np
        
        # Create animation frames
        frames = []
        for i in range(10):
            data = go.Scatter(
                x=np.arange(10),
                y=np.sin(np.arange(10) + i/2),
                mode='lines+markers'
            )
            frames.append(go.Frame(data=[data], name=str(i)))
        
        fig = go.Figure(
            data=[frames[0].data[0]],
            frames=frames,
            layout=go.Layout(
                title="Animated Plot",
                updatemenus=[{
                    'type': 'buttons',
                    'buttons': [
                        {'label': 'Play', 'method': 'animate', 'args': [None]}
                    ]
                }]
            )
        )
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_save_plotly_express_figure(self):
        """Test saving Plotly Express figure"""
        import pandas as pd
        
        # Create sample data
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 3, 5, 6],
            'category': ['A', 'B', 'A', 'B', 'A']
        })
        
        fig = px.scatter(df, x='x', y='y', color='category', 
                        title="Plotly Express Scatter")
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_save_with_include_plotlyjs(self):
        """Test different include_plotlyjs options"""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        
        # Test with CDN
        save_html(fig, self.test_file, include_plotlyjs='cdn')
        assert os.path.exists(self.test_file)
        
        # Test with inline
        inline_file = os.path.join(self.temp_dir, "inline.html")
        save_html(fig, inline_file, include_plotlyjs='inline')
        assert os.path.getsize(inline_file) > os.path.getsize(self.test_file)

    def test_save_heatmap(self):
        """Test saving heatmap"""
        import numpy as np
        
        z = np.random.randn(20, 20)
        fig = go.Figure(data=go.Heatmap(z=z, colorscale='Viridis'))
        fig.update_layout(title="Random Heatmap")
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_save_with_annotations(self):
        """Test saving figure with annotations"""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13])])
        
        fig.add_annotation(
            x=2, y=11,
            text="Important Point",
            showarrow=True,
            arrowhead=2
        )
        
        fig.update_layout(title="Plot with Annotations")
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_error_non_plotly_object(self):
        """Test error handling for non-Plotly objects"""
        with pytest.raises(ValueError, match="Object must be a Plotly figure"):
            save_html("not a figure", self.test_file)

    def test_save_empty_figure(self):
        """Test saving empty figure"""
        fig = go.Figure()
        fig.update_layout(title="Empty Figure")
        
        save_html(fig, self.test_file)
        
        assert os.path.exists(self.test_file)

    def test_save_with_custom_div_id(self):
        """Test saving with custom div ID"""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        
        save_html(fig, self.test_file, div_id="myplot")
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert 'myplot' in content


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_html.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-12 13:45:00 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/io/_save_modules/_html.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/io/_save_modules/_html.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# """
# HTML saving functionality for scitex.io.save
# """
# 
# import plotly
# 
# 
# def save_html(obj, spath, **kwargs):
#     """Handle HTML file saving (primarily for Plotly figures).
#     
#     Parameters
#     ----------
#     obj : plotly.graph_objs.Figure or str
#         Plotly figure object or HTML string to save
#     spath : str
#         Path where HTML file will be saved
#     **kwargs
#         Additional keyword arguments passed to plotly.io.write_html()
#         
#     Notes
#     -----
#     - Primarily designed for saving Plotly interactive figures
#     - Can also save raw HTML strings
#     """
#     if hasattr(obj, 'write_html'):
#         # Plotly figure object
#         obj.write_html(spath, **kwargs)
#     elif isinstance(obj, str):
#         # Raw HTML string
#         with open(spath, 'w') as f:
#             f.write(obj)
#     else:
#         # Try to convert to HTML using plotly
#         plotly.io.write_html(obj, spath, **kwargs)
# 
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_html.py
# --------------------------------------------------------------------------------
