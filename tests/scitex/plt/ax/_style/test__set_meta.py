#!/usr/bin/env python3
"""Tests for scitex.plt.ax._style._set_meta module.

This module provides comprehensive tests for scientific metadata management
for figures with YAML export functionality.
"""

import os
import tempfile
import datetime
import yaml
import pytest
import matplotlib.pyplot as plt
from unittest.mock import MagicMock, patch

from scitex.plt.ax._style import (
    set_meta,
    set_figure_meta,
    export_metadata_yaml
)


class TestSetMeta:
    """Test set_meta function."""
    
    @pytest.fixture
    def setup_figure(self):
        """Create a test figure and axis."""
        fig, ax = plt.subplots()
        yield fig, ax
        plt.close(fig)
    
    def test_set_meta_basic_caption(self, setup_figure):
        """Test setting basic caption metadata."""
        fig, ax = setup_figure
        caption = "Test figure showing example data."
        
        result = set_meta(ax, caption=caption)
        
        assert result == ax
        assert hasattr(fig, '_scitex_metadata')
        assert ax in fig._scitex_metadata
        assert fig._scitex_metadata[ax]['caption'] == caption
    
    def test_set_meta_all_parameters(self, setup_figure):
        """Test setting all metadata parameters."""
        fig, ax = setup_figure
        
        metadata_params = {
            'caption': 'Comprehensive test figure.',
            'methods': 'Test methodology using synthetic data.',
            'stats': 'Statistical analysis with p < 0.05.',
            'keywords': ['test', 'synthetic', 'example'],
            'experimental_details': {
                'n_samples': 100,
                'temperature': 25,
                'duration': 300
            },
            'journal_style': 'nature',
            'significance': 'Demonstrates metadata functionality.'
        }
        
        result = set_meta(ax, **metadata_params)
        
        stored_meta = fig._scitex_metadata[ax]
        for key, value in metadata_params.items():
            if key == 'stats':
                assert stored_meta['statistical_analysis'] == value
            else:
                assert stored_meta[key] == value
    
    def test_set_meta_keywords_conversion(self, setup_figure):
        """Test that single keyword is converted to list."""
        fig, ax = setup_figure
        
        # Single keyword as string
        set_meta(ax, keywords='electrophysiology')
        assert fig._scitex_metadata[ax]['keywords'] == ['electrophysiology']
        
        # Multiple keywords as list
        set_meta(ax, keywords=['neural', 'recording'])
        assert fig._scitex_metadata[ax]['keywords'] == ['neural', 'recording']
    
    def test_set_meta_automatic_metadata(self, setup_figure):
        """Test automatic metadata addition."""
        fig, ax = setup_figure
        
        set_meta(ax, caption='Test')
        
        stored_meta = fig._scitex_metadata[ax]
        assert 'created_timestamp' in stored_meta
        assert 'scitex_version' in stored_meta
        
        # Verify timestamp format
        timestamp = stored_meta['created_timestamp']
        datetime.datetime.fromisoformat(timestamp)  # Should not raise
    
    def test_set_meta_additional_kwargs(self, setup_figure):
        """Test additional metadata through kwargs."""
        fig, ax = setup_figure
        
        set_meta(ax, 
                caption='Test',
                custom_field='custom_value',
                another_field=42)
        
        stored_meta = fig._scitex_metadata[ax]
        assert stored_meta['custom_field'] == 'custom_value'
        assert stored_meta['another_field'] == 42
    
    def test_set_meta_yaml_structure(self, setup_figure):
        """Test YAML metadata structure."""
        fig, ax = setup_figure
        
        set_meta(ax, caption='Test', methods='Test method')
        
        assert hasattr(fig, '_scitex_yaml_metadata')
        assert ax in fig._scitex_yaml_metadata
        assert fig._scitex_yaml_metadata[ax] == fig._scitex_metadata[ax]
    
    def test_set_meta_backward_compatibility(self, setup_figure):
        """Test backward compatibility with caption storage."""
        fig, ax = setup_figure
        caption = 'Backward compatible caption'
        
        set_meta(ax, caption=caption)
        
        assert hasattr(fig, '_scitex_captions')
        assert fig._scitex_captions[ax] == caption
    
    def test_set_meta_none_values_ignored(self, setup_figure):
        """Test that None values are not stored."""
        fig, ax = setup_figure
        
        set_meta(ax, 
                caption='Test',
                methods=None,
                stats=None)
        
        stored_meta = fig._scitex_metadata[ax]
        assert 'caption' in stored_meta
        assert 'methods' not in stored_meta
        assert 'statistical_analysis' not in stored_meta
    
    def test_set_meta_multiple_axes(self, setup_figure):
        """Test metadata on multiple axes."""
        fig, (ax1, ax2) = plt.subplots(1, 2)
        
        set_meta(ax1, caption='First panel')
        set_meta(ax2, caption='Second panel')
        
        assert len(fig._scitex_metadata) == 2
        assert fig._scitex_metadata[ax1]['caption'] == 'First panel'
        assert fig._scitex_metadata[ax2]['caption'] == 'Second panel'
        
        plt.close(fig)


class TestSetFigureMeta:
    """Test set_figure_meta function."""
    
    @pytest.fixture
    def setup_figure(self):
        """Create a test figure and axis."""
        fig, ax = plt.subplots()
        yield fig, ax
        plt.close(fig)
    
    def test_set_figure_meta_basic(self, setup_figure):
        """Test basic figure-level metadata."""
        fig, ax = setup_figure
        
        result = set_figure_meta(ax, 
                               caption='Main figure caption',
                               significance='Important findings')
        
        assert result == ax
        assert hasattr(fig, '_scitex_figure_metadata')
        assert fig._scitex_figure_metadata['main_caption'] == 'Main figure caption'
        assert fig._scitex_figure_metadata['significance'] == 'Important findings'
    
    def test_set_figure_meta_all_parameters(self, setup_figure):
        """Test all figure metadata parameters."""
        fig, ax = setup_figure
        
        metadata = {
            'caption': 'Comprehensive analysis',
            'methods': 'Overall methodology',
            'stats': 'Statistical approach',
            'significance': 'Key findings',
            'funding': 'NIH grant R01-12345',
            'conflicts': 'No conflicts',
            'data_availability': 'Data at doi:10.5061/example'
        }
        
        set_figure_meta(ax, **metadata)
        
        fig_meta = fig._scitex_figure_metadata
        assert fig_meta['main_caption'] == metadata['caption']
        assert fig_meta['overall_methods'] == metadata['methods']
        assert fig_meta['overall_statistics'] == metadata['stats']
        assert fig_meta['significance'] == metadata['significance']
        assert fig_meta['funding'] == metadata['funding']
        assert fig_meta['conflicts_of_interest'] == metadata['conflicts']
        assert fig_meta['data_availability'] == metadata['data_availability']
    
    def test_set_figure_meta_timestamp(self, setup_figure):
        """Test automatic timestamp addition."""
        fig, ax = setup_figure
        
        set_figure_meta(ax, caption='Test')
        
        assert 'created_timestamp' in fig._scitex_figure_metadata
        timestamp = fig._scitex_figure_metadata['created_timestamp']
        datetime.datetime.fromisoformat(timestamp)  # Should not raise
    
    def test_set_figure_meta_backward_compatibility(self, setup_figure):
        """Test backward compatibility for main caption."""
        fig, ax = setup_figure
        caption = 'Main caption for compatibility'
        
        set_figure_meta(ax, caption=caption)
        
        assert hasattr(fig, '_scitex_main_caption')
        assert fig._scitex_main_caption == caption
    
    def test_set_figure_meta_additional_fields(self, setup_figure):
        """Test additional metadata fields through kwargs."""
        fig, ax = setup_figure
        
        set_figure_meta(ax,
                       caption='Test',
                       custom_field='value',
                       numeric_field=42)
        
        fig_meta = fig._scitex_figure_metadata
        assert fig_meta['custom_field'] == 'value'
        assert fig_meta['numeric_field'] == 42
    
    def test_set_figure_meta_from_different_axes(self):
        """Test that figure metadata can be set from any axis."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        
        # Set from different axes
        set_figure_meta(ax3, caption='Set from ax3')
        
        assert fig._scitex_figure_metadata['main_caption'] == 'Set from ax3'
        
        plt.close(fig)


class TestExportMetadataYaml:
    """Test export_metadata_yaml function."""
    
    @pytest.fixture
    def setup_figure_with_metadata(self):
        """Create figure with both panel and figure metadata."""
        fig, (ax1, ax2) = plt.subplots(1, 2)
        
        # Set panel metadata
        set_meta(ax1, 
                caption='Panel 1 caption',
                methods='Panel 1 methods',
                keywords=['panel1', 'test'])
        
        set_meta(ax2,
                caption='Panel 2 caption',
                experimental_details={'samples': 50})
        
        # Set figure metadata
        set_figure_meta(ax1,
                       caption='Main figure caption',
                       significance='Important results',
                       funding='Test grant')
        
        yield fig
        plt.close(fig)
    
    def test_export_metadata_yaml_basic(self, setup_figure_with_metadata):
        """Test basic YAML export."""
        fig = setup_figure_with_metadata
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            filepath = f.name
        
        try:
            export_metadata_yaml(fig, filepath)
            
            # Load and verify YAML
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            assert 'figure_metadata' in data
            assert 'panel_metadata' in data
            assert 'export_info' in data
            
            # Check figure metadata
            assert data['figure_metadata']['main_caption'] == 'Main figure caption'
            assert data['figure_metadata']['significance'] == 'Important results'
            
            # Check panel metadata
            assert 'panel_1' in data['panel_metadata']
            assert 'panel_2' in data['panel_metadata']
            assert data['panel_metadata']['panel_1']['caption'] == 'Panel 1 caption'
            assert data['panel_metadata']['panel_2']['caption'] == 'Panel 2 caption'
            
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_export_metadata_yaml_empty_figure(self):
        """Test export with figure having no metadata."""
        fig, ax = plt.subplots()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            filepath = f.name
        
        try:
            export_metadata_yaml(fig, filepath)
            
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            assert data['figure_metadata'] == {}
            assert data['panel_metadata'] == {}
            assert 'export_info' in data
            
        finally:
            plt.close(fig)
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_export_metadata_yaml_structure(self, setup_figure_with_metadata):
        """Test exported YAML structure."""
        fig = setup_figure_with_metadata
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            filepath = f.name
        
        try:
            export_metadata_yaml(fig, filepath)
            
            # Read raw YAML to check formatting
            with open(filepath, 'r') as f:
                yaml_content = f.read()
            
            # Should be properly formatted
            assert 'figure_metadata:' in yaml_content
            assert 'panel_metadata:' in yaml_content
            assert 'export_info:' in yaml_content
            assert '  timestamp:' in yaml_content  # Proper indentation
            
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_export_metadata_yaml_export_info(self, setup_figure_with_metadata):
        """Test export info in YAML."""
        fig = setup_figure_with_metadata
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            filepath = f.name
        
        try:
            export_metadata_yaml(fig, filepath)
            
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            export_info = data['export_info']
            assert 'timestamp' in export_info
            assert 'scitex_version' in export_info
            
            # Verify timestamp format
            datetime.datetime.fromisoformat(export_info['timestamp'])
            
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestIntegration:
    """Integration tests for metadata system."""
    
    def test_complete_workflow(self):
        """Test complete metadata workflow."""
        # Create multi-panel figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        
        # Set panel metadata
        for i, ax in enumerate([ax1, ax2, ax3, ax4], 1):
            set_meta(ax,
                    caption=f'Panel {i} showing data',
                    methods=f'Method for panel {i}',
                    keywords=[f'panel{i}', 'test'],
                    experimental_details={'panel_number': i})
        
        # Set figure metadata
        set_figure_meta(ax1,
                       caption='Complete multi-panel analysis',
                       significance='Demonstrates metadata system',
                       data_availability='Test data available')
        
        # Export to YAML
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            filepath = f.name
        
        try:
            export_metadata_yaml(fig, filepath)
            
            # Verify complete export
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            # Should have all panels
            assert len(data['panel_metadata']) == 4
            
            # Each panel should have complete metadata
            for i in range(1, 5):
                panel_data = data['panel_metadata'][f'panel_{i}']
                assert panel_data['caption'] == f'Panel {i} showing data'
                assert panel_data['experimental_details']['panel_number'] == i
            
            # Figure metadata should be complete
            assert data['figure_metadata']['main_caption'] == 'Complete multi-panel analysis'
            
        finally:
            plt.close(fig)
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_metadata_persistence(self):
        """Test that metadata persists across operations."""
        fig, ax = plt.subplots()
        
        # Set metadata
        set_meta(ax, caption='Test caption', methods='Test methods')
        
        # Perform some plot operations
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        # Metadata should still be there
        assert fig._scitex_metadata[ax]['caption'] == 'Test caption'
        assert fig._scitex_metadata[ax]['methods'] == 'Test methods'
        
        plt.close(fig)
    
    def test_timestamp_consistency(self):
        """Test timestamp consistency across metadata."""
        fig, ax = plt.subplots()
        
        # Set metadata close together
        set_meta(ax, caption='Test')
        panel_time = fig._scitex_metadata[ax]['created_timestamp']
        
        set_figure_meta(ax, caption='Figure test')
        figure_time = fig._scitex_figure_metadata['created_timestamp']
        
        # Parse timestamps
        panel_dt = datetime.datetime.fromisoformat(panel_time)
        figure_dt = datetime.datetime.fromisoformat(figure_time)
        
        # They should be very close (within 1 second)
        time_diff = abs((figure_dt - panel_dt).total_seconds())
        assert time_diff < 1.0, f"Timestamps differ by {time_diff} seconds"
        
        plt.close(fig)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_set_meta.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-06-04 11:35:00 (ywatanabe)"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
# 
# """
# Scientific metadata management for figures with YAML export.
# """
# 
# # Imports
# import yaml
# from typing import Optional, List, Dict, Any
# 
# 
# # Functions
# def set_meta(ax, caption=None, methods=None, stats=None, keywords=None, 
#              experimental_details=None, journal_style=None, 
#              significance=None, **kwargs):
#     """Set comprehensive scientific metadata for figures with YAML export
#     
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes or scitex AxisWrapper
#         The axes to modify
#     caption : str, optional
#         Figure caption text
#     methods : str, optional
#         Experimental methods description
#     stats : str, optional
#         Statistical analysis details
#     keywords : List[str], optional
#         Keywords for categorization and search
#     experimental_details : Dict[str, Any], optional
#         Structured experimental parameters (n_samples, temperature, etc.)
#     journal_style : str, optional
#         Target journal style ('nature', 'science', 'ieee', 'cell', etc.)
#     significance : str, optional
#         Significance statement or implications
#     **kwargs : additional metadata
#         Any additional metadata fields
#         
#     Returns
#     -------
#     ax : matplotlib.axes.Axes or scitex AxisWrapper
#         The modified axes
#         
#     Examples
#     --------
#     >>> fig, ax = scitex.plt.subplots()
#     >>> ax.plot(x, y, id='neural_data')
#     >>> ax.set_xyt(x='Time (ms)', y='Voltage (mV)', t='Neural Recording')
#     >>> ax.set_meta(
#     ...     caption='Intracellular recording showing action potentials.',
#     ...     methods='Whole-cell patch-clamp in acute brain slices.',
#     ...     stats='Statistical analysis using paired t-test (p<0.05).',
#     ...     keywords=['electrophysiology', 'neural_recording', 'patch_clamp'],
#     ...     experimental_details={
#     ...         'n_samples': 15,
#     ...         'temperature': 32,
#     ...         'recording_duration': 600,
#     ...         'electrode_resistance': '3-5 MΩ'
#     ...     },
#     ...     journal_style='nature',
#     ...     significance='Demonstrates novel neural dynamics in layer 2/3 pyramidal cells.'
#     ... )
#     >>> scitex.io.save(fig, 'neural_recording.png')  # YAML metadata auto-saved
#     """
#     
#     # Build comprehensive metadata dictionary
#     metadata = {}
#     
#     if caption is not None:
#         metadata['caption'] = caption
#     if methods is not None:
#         metadata['methods'] = methods
#     if stats is not None:
#         metadata['statistical_analysis'] = stats
#     if keywords is not None:
#         metadata['keywords'] = keywords if isinstance(keywords, list) else [keywords]
#     if experimental_details is not None:
#         metadata['experimental_details'] = experimental_details
#     if journal_style is not None:
#         metadata['journal_style'] = journal_style
#     if significance is not None:
#         metadata['significance'] = significance
#     
#     # Add any additional metadata
#     for key, value in kwargs.items():
#         if value is not None:
#             metadata[key] = value
#     
#     # Add automatic metadata
#     import datetime
#     metadata['created_timestamp'] = datetime.datetime.now().isoformat()
#     metadata['scitex_version'] = '1.11.0'  # TODO: Get from __version__
#     
#     # Store metadata in figure for automatic saving
#     fig = ax.get_figure()
#     if not hasattr(fig, '_scitex_metadata'):
#         fig._scitex_metadata = {}
#     
#     # Use axis as key for panel-specific metadata
#     fig._scitex_metadata[ax] = metadata
#     
#     # Also store as YAML-ready structure
#     if not hasattr(fig, '_scitex_yaml_metadata'):
#         fig._scitex_yaml_metadata = {}
#     fig._scitex_yaml_metadata[ax] = metadata
#     
#     # Backward compatibility - store simple caption
#     if caption is not None:
#         if not hasattr(fig, '_scitex_captions'):
#             fig._scitex_captions = {}
#         fig._scitex_captions[ax] = caption
#     
#     return ax
# 
# 
# def set_figure_meta(ax, caption=None, methods=None, stats=None, significance=None,
#                    funding=None, conflicts=None, data_availability=None, **kwargs):
#     """Set figure-level metadata for multi-panel figures
#     
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes or scitex AxisWrapper
#         Any axis in the figure (figure accessed via ax.get_figure())
#     caption : str, optional
#         Figure-level caption
#     methods : str, optional
#         Overall experimental methods
#     stats : str, optional
#         Overall statistical approach
#     significance : str, optional
#         Significance and implications
#     funding : str, optional
#         Funding acknowledgments
#     conflicts : str, optional
#         Conflict of interest statement
#     data_availability : str, optional
#         Data availability statement
#     **kwargs : additional metadata
#         Any additional figure-level metadata
#         
#     Returns
#     -------
#     ax : matplotlib.axes.Axes or scitex AxisWrapper
#         The modified axes
#         
#     Examples
#     --------
#     >>> fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2)
#     >>> # Set individual panel metadata...
#     >>> ax1.set_meta(caption='Panel A analysis...')
#     >>> ax2.set_meta(caption='Panel B comparison...')
#     >>> 
#     >>> # Set figure-level metadata
#     >>> ax1.set_figure_meta(
#     ...     caption='Comprehensive analysis of neural dynamics...',
#     ...     significance='This work demonstrates novel therapeutic targets.',
#     ...     funding='Supported by NIH grant R01-NS123456.',
#     ...     data_availability='Data available at doi:10.5061/dryad.example'
#     ... )
#     """
#     
#     # Build figure-level metadata
#     figure_metadata = {}
#     
#     if caption is not None:
#         figure_metadata['main_caption'] = caption
#     if methods is not None:
#         figure_metadata['overall_methods'] = methods
#     if stats is not None:
#         figure_metadata['overall_statistics'] = stats
#     if significance is not None:
#         figure_metadata['significance'] = significance
#     if funding is not None:
#         figure_metadata['funding'] = funding
#     if conflicts is not None:
#         figure_metadata['conflicts_of_interest'] = conflicts
#     if data_availability is not None:
#         figure_metadata['data_availability'] = data_availability
#     
#     # Add any additional metadata
#     for key, value in kwargs.items():
#         if value is not None:
#             figure_metadata[key] = value
#     
#     # Add automatic metadata
#     import datetime
#     figure_metadata['created_timestamp'] = datetime.datetime.now().isoformat()
#     
#     # Store in figure
#     fig = ax.get_figure()
#     fig._scitex_figure_metadata = figure_metadata
#     
#     # Backward compatibility
#     if caption is not None:
#         fig._scitex_main_caption = caption
#     
#     return ax
# 
# 
# def export_metadata_yaml(fig, filepath):
#     """Export all figure metadata to YAML file
#     
#     Parameters
#     ----------
#     fig : matplotlib.figure.Figure
#         Figure with metadata
#     filepath : str
#         Output YAML file path
#     """
#     import datetime
#     
#     # Collect all metadata
#     export_data = {
#         'figure_metadata': {},
#         'panel_metadata': {},
#         'export_info': {
#             'timestamp': datetime.datetime.now().isoformat(),
#             'scitex_version': '1.11.0'
#         }
#     }
#     
#     # Figure-level metadata
#     if hasattr(fig, '_scitex_figure_metadata'):
#         export_data['figure_metadata'] = fig._scitex_figure_metadata
#     
#     # Panel-level metadata
#     if hasattr(fig, '_scitex_yaml_metadata'):
#         for i, (ax, metadata) in enumerate(fig._scitex_yaml_metadata.items()):
#             panel_key = f'panel_{i+1}'
#             export_data['panel_metadata'][panel_key] = metadata
#     
#     # Write YAML file
#     with open(filepath, 'w') as f:
#         yaml.dump(export_data, f, default_flow_style=False, sort_keys=False, indent=2)
# 
# 
# if __name__ == "__main__":
#     # Start
#     import sys
#     import matplotlib.pyplot as plt
#     import scitex
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     # Example usage
#     fig, ax = plt.subplots()
#     ax.plot([1, 2, 3], [1, 4, 2])
#     
#     set_meta(ax, 
#              caption='Example figure showing data trends.',
#              methods='Synthetic data generated for demonstration.',
#              keywords=['example', 'demo', 'synthetic'],
#              experimental_details={'n_samples': 3, 'data_type': 'synthetic'})
#     
#     export_metadata_yaml(fig, 'example_metadata.yaml')
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_set_meta.py
# --------------------------------------------------------------------------------
