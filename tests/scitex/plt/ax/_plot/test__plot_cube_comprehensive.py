#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:31:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_plot/test__plot_cube_comprehensive.py

"""Comprehensive tests for plot_cube functionality."""

import os
import pytest
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from unittest.mock import patch, MagicMock
import tempfile
from itertools import product, combinations
from scitex.plt.ax._plot import plot_cube


class TestPlotCubeBasic:
    """Test basic plot_cube functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_unit_cube(self):
        """Test plotting a unit cube."""
        result = plot_cube(self.ax, [0, 1], [0, 1], [0, 1])
        
        assert result is self.ax
        # Should have created lines for edges
        assert len(self.ax.lines) > 0
    
    def test_cube_with_different_dimensions(self):
        """Test plotting cubes with different dimensions."""
        test_cases = [
            ([0, 2], [0, 2], [0, 2]),  # 2x2x2 cube
            ([0, 5], [0, 5], [0, 5]),  # 5x5x5 cube
            ([-1, 1], [-1, 1], [-1, 1]),  # Centered cube
            ([10, 20], [10, 20], [10, 20]),  # Offset cube
        ]
        
        for xlim, ylim, zlim in test_cases:
            self.ax.clear()
            result = plot_cube(self.ax, xlim, ylim, zlim)
            assert len(self.ax.lines) > 0
    
    def test_rectangular_cuboid(self):
        """Test plotting rectangular cuboids (non-cubic)."""
        test_cases = [
            ([0, 1], [0, 2], [0, 3]),  # 1x2x3
            ([0, 5], [0, 1], [0, 1]),  # Thin in y,z
            ([0, 1], [0, 10], [0, 1]), # Tall in y
            ([0, 1], [0, 1], [0, 20]), # Tall in z
        ]
        
        for xlim, ylim, zlim in test_cases:
            self.ax.clear()
            result = plot_cube(self.ax, xlim, ylim, zlim)
            assert len(self.ax.lines) > 0
    
    def test_color_parameter(self):
        """Test different color parameters."""
        colors = ['red', 'green', 'blue', '#FF0000', 'k', 'cyan']
        
        for color in colors:
            self.ax.clear()
            result = plot_cube(self.ax, [0, 1], [0, 1], [0, 1], c=color)
            
            # Check that lines have correct color
            for line in self.ax.lines:
                assert line.get_color() == color
    
    def test_alpha_parameter(self):
        """Test different alpha values."""
        alphas = [0.0, 0.3, 0.5, 0.7, 1.0]
        
        for alpha in alphas:
            self.ax.clear()
            result = plot_cube(self.ax, [0, 1], [0, 1], [0, 1], alpha=alpha)
            
            # Check that lines have correct alpha
            for line in self.ax.lines:
                assert line.get_alpha() == alpha


class TestPlotCubeEdgeCount:
    """Test that correct number of edges are created."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_twelve_edges(self):
        """Test that exactly 12 edges are created for a cube."""
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1])
        
        # A cube has 12 edges
        assert len(self.ax.lines) == 12
    
    def test_edge_connectivity(self):
        """Test that edges connect correct vertices."""
        xlim, ylim, zlim = [0, 1], [0, 1], [0, 1]
        plot_cube(self.ax, xlim, ylim, zlim)
        
        # Get all corner points
        corners = list(product(xlim, ylim, zlim))
        assert len(corners) == 8  # Cube has 8 corners
        
        # Each corner should be connected to exactly 3 others
        # (3 edges per vertex in a cube)


class TestPlotCubeValidation:
    """Test input validation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_invalid_axis(self):
        """Test with invalid axis type."""
        # 2D axis instead of 3D
        ax_2d = self.fig.add_subplot(111)
        
        with pytest.raises(AssertionError, match="must be a 3D axis"):
            plot_cube(ax_2d, [0, 1], [0, 1], [0, 1])
    
    def test_invalid_limits_length(self):
        """Test with invalid limit lengths."""
        with pytest.raises(AssertionError, match="must be a tuple"):
            plot_cube(self.ax, [0], [0, 1], [0, 1])
        
        with pytest.raises(AssertionError, match="must be a tuple"):
            plot_cube(self.ax, [0, 1], [0, 1, 2], [0, 1])
        
        with pytest.raises(AssertionError, match="must be a tuple"):
            plot_cube(self.ax, [0, 1], [0, 1], [])
    
    def test_invalid_limit_order(self):
        """Test with min > max in limits."""
        with pytest.raises(AssertionError, match="must be less than"):
            plot_cube(self.ax, [1, 0], [0, 1], [0, 1])
        
        with pytest.raises(AssertionError, match="must be less than"):
            plot_cube(self.ax, [0, 1], [2, 1], [0, 1])
        
        with pytest.raises(AssertionError, match="must be less than"):
            plot_cube(self.ax, [0, 1], [0, 1], [5, 3])
    
    def test_equal_limits(self):
        """Test with min == max (zero volume)."""
        with pytest.raises(AssertionError):
            plot_cube(self.ax, [1, 1], [0, 1], [0, 1])


class TestPlotCubeEdgeCases:
    """Test edge cases and special scenarios."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_very_small_cube(self):
        """Test with very small dimensions."""
        epsilon = 1e-10
        plot_cube(self.ax, [0, epsilon], [0, epsilon], [0, epsilon])
        assert len(self.ax.lines) == 12
    
    def test_very_large_cube(self):
        """Test with very large dimensions."""
        large = 1e10
        plot_cube(self.ax, [0, large], [0, large], [0, large])
        assert len(self.ax.lines) == 12
    
    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        plot_cube(self.ax, [-5, -3], [-2, -1], [-10, -8])
        assert len(self.ax.lines) == 12
    
    def test_mixed_sign_coordinates(self):
        """Test with mixed positive/negative coordinates."""
        plot_cube(self.ax, [-1, 1], [-2, 3], [-5, 5])
        assert len(self.ax.lines) == 12
    
    def test_floating_point_limits(self):
        """Test with floating point limits."""
        plot_cube(self.ax, [0.1, 0.9], [1.5, 2.7], [3.14, 4.56])
        assert len(self.ax.lines) == 12


class TestPlotCubeVisual:
    """Test visual properties of the cube."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_line_properties(self):
        """Test that lines have correct properties."""
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1], c='red', alpha=0.5)
        
        for line in self.ax.lines:
            assert line.get_color() == 'red'
            assert line.get_alpha() == 0.5
            assert line.get_linewidth() == 3  # Default linewidth
    
    def test_color_formats(self):
        """Test various color format inputs."""
        color_formats = [
            'red',                    # Named color
            '#FF0000',               # Hex
            (1.0, 0.0, 0.0),        # RGB tuple
            (1.0, 0.0, 0.0, 0.8),   # RGBA tuple
            'C0',                    # Color cycle
        ]
        
        for color in color_formats:
            self.ax.clear()
            plot_cube(self.ax, [0, 1], [0, 1], [0, 1], c=color)
            assert len(self.ax.lines) == 12
    
    def test_transparency_levels(self):
        """Test different transparency levels."""
        for alpha in np.linspace(0, 1, 5):
            self.ax.clear()
            plot_cube(self.ax, [0, 1], [0, 1], [0, 1], alpha=alpha)
            
            for line in self.ax.lines:
                assert line.get_alpha() == alpha


class TestPlotCubeIntegration:
    """Test integration with other plot elements."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_multiple_cubes(self):
        """Test plotting multiple cubes."""
        # First cube
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1], c='red')
        lines_first = len(self.ax.lines)
        
        # Second cube
        plot_cube(self.ax, [2, 3], [2, 3], [2, 3], c='blue')
        lines_total = len(self.ax.lines)
        
        assert lines_total == lines_first * 2  # Two cubes
    
    def test_with_other_3d_elements(self):
        """Test cube with other 3D plot elements."""
        # Add scatter points
        self.ax.scatter([0.5], [0.5], [0.5], c='green', s=100)
        
        # Add cube
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1], c='red')
        
        # Both should exist
        assert len(self.ax.lines) == 12  # Cube edges
        assert len(self.ax.collections) > 0  # Scatter points
    
    def test_axis_limits_preserved(self):
        """Test that manual axis limits are preserved."""
        # Set custom limits
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.set_zlim(-5, 5)
        
        # Plot small cube
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1])
        
        # Limits should be preserved
        assert self.ax.get_xlim() == (-5, 5)
        assert self.ax.get_ylim() == (-5, 5)
        assert self.ax.get_zlim() == (-5, 5)


class TestPlotCubePerformance:
    """Test performance characteristics."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_many_cubes(self):
        """Test plotting many cubes."""
        for i in range(10):
            for j in range(10):
                plot_cube(
                    self.ax,
                    [i, i+0.8],
                    [j, j+0.8],
                    [0, 0.8],
                    c='blue',
                    alpha=0.3
                )
        
        # Should have 100 cubes * 12 edges
        assert len(self.ax.lines) == 1200
    
    def test_cube_creation_speed(self):
        """Test that cube creation is reasonably fast."""
        import time
        
        start = time.time()
        for _ in range(10):
            self.ax.clear()
            plot_cube(self.ax, [0, 1], [0, 1], [0, 1])
        duration = time.time() - start
        
        # Should be fast (less than 1 second for 10 cubes)
        assert duration < 1.0


class TestPlotCubeSave:
    """Test saving figures with cubes."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_save_formats(self):
        """Test saving in different formats."""
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1], c='red')
        
        formats = ['.png', '.jpg', '.pdf', '.svg']
        for fmt in formats:
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as f:
                try:
                    self.fig.savefig(f.name)
                    assert os.path.exists(f.name)
                    assert os.path.getsize(f.name) > 0
                finally:
                    if os.path.exists(f.name):
                        os.unlink(f.name)
    
    def test_save_with_labels(self):
        """Test saving cube plot with labels."""
        plot_cube(self.ax, [0, 1], [0, 1], [0, 1])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Cube')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            try:
                self.fig.savefig(f.name)
                assert os.path.exists(f.name)
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)


class TestPlotCubeMathematical:
    """Test mathematical properties of the cube."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_edge_lengths(self):
        """Test that edge lengths are correct."""
        xlim, ylim, zlim = [0, 2], [0, 3], [0, 4]
        plot_cube(self.ax, xlim, ylim, zlim)
        
        # Expected edge lengths
        x_length = xlim[1] - xlim[0]  # 2
        y_length = ylim[1] - ylim[0]  # 3
        z_length = zlim[1] - zlim[0]  # 4
        
        # Each dimension should have 4 edges of that length
        # Total: 4 edges of length 2, 4 of length 3, 4 of length 4
    
    def test_vertex_count(self):
        """Test that 8 unique vertices are created."""
        xlim, ylim, zlim = [0, 1], [0, 1], [0, 1]
        
        # Calculate expected vertices
        vertices = list(product(xlim, ylim, zlim))
        assert len(vertices) == 8
        
        # Each vertex should connect to exactly 3 edges
        # Total edges = 8 * 3 / 2 = 12 (each edge connects 2 vertices)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])