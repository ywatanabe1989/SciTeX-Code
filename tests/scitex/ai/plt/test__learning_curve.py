#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 00:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/tests/scitex/ai/plt/test__learning_curve.py

"""
Comprehensive tests for learning curve plotting functionality
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock, call
import tempfile
import os


class TestLearningCurve:
    """Test class for learning curve plotting"""
    
    @pytest.fixture
    def sample_metrics_df(self):
        """Create sample metrics dataframe for testing"""
        # Create sample training data
        n_samples = 100
        data = {
            'step': ['Training'] * 40 + ['Validation'] * 30 + ['Test'] * 30,
            'i_global': list(range(40)) + list(range(10, 40)) + list(range(20, 50)),
            'i_epoch': [i // 10 for i in range(40)] + [i // 10 for i in range(10, 40)] + [i // 10 for i in range(20, 50)],
            'i_batch': [i % 10 for i in range(40)] + [i % 10 for i in range(10, 40)] + [i % 10 for i in range(20, 50)],
            'loss': np.random.exponential(0.5, 100),
            'accuracy': np.random.beta(5, 2, 100),
            'learning_rate': [0.001] * 50 + [0.0001] * 50
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def mock_plt(self):
        """Mock matplotlib.pyplot for testing"""
        mock = MagicMock()
        mock.subplots.return_value = (MagicMock(), [MagicMock(), MagicMock()])
        mock.rcParams = {'font.size': 12}
        return mock
    
    def test_basic_learning_curve(self, sample_metrics_df):
        """Test basic learning curve plotting"""
        from scitex.ai.plt import learning_curve
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_axes = [MagicMock(), MagicMock()]
                    mock_subplots.return_value = (mock_fig, mock_axes)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(sample_metrics_df, keys=['loss', 'accuracy'])
                    
        assert fig is not None
        assert mock_subplots.called
        assert mock_subplots.call_args[0] == (2, 1)  # 2 subplots for 2 keys
        
    def test_learning_curve_single_metric(self, sample_metrics_df):
        """Test learning curve with single metric"""
        from scitex.ai.plt import learning_curve
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(sample_metrics_df, keys=['loss'])
                    
        assert fig is not None
        # Single metric should still work properly
        
    def test_learning_curve_multiple_metrics(self, sample_metrics_df):
        """Test learning curve with multiple metrics"""
        from scitex.ai.plt import learning_curve
        
        keys = ['loss', 'accuracy', 'learning_rate']
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_axes = [MagicMock() for _ in range(3)]
                    mock_subplots.return_value = (mock_fig, mock_axes)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(sample_metrics_df, keys=keys)
                    
        # Verify that all axes were configured
        for ax in mock_axes:
            ax.set_ylabel.assert_called()
            ax.set_yscale.assert_called()
            
    def test_learning_curve_custom_title(self, sample_metrics_df):
        """Test learning curve with custom title"""
        from scitex.ai.plt import learning_curve
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(sample_metrics_df, keys=['loss'], title="Custom Title")
                    
        mock_fig.text.assert_called_with(0.5, 0.95, "Custom Title", ha="center")
        
    def test_learning_curve_log_scale(self, sample_metrics_df):
        """Test learning curve with logarithmic y-scale"""
        from scitex.ai.plt import learning_curve
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(sample_metrics_df, keys=['loss'], yscale='log')
                    
        mock_ax.set_yscale.assert_called_with('log')
        
    def test_learning_curve_custom_marker_sizes(self, sample_metrics_df):
        """Test learning curve with custom scatter and line sizes"""
        from scitex.ai.plt import learning_curve
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(
                        sample_metrics_df, 
                        keys=['loss'],
                        scattersize=10,
                        linewidth=3
                    )
                    
        # Verify plot was called with correct linewidth
        plot_calls = [call for call in mock_ax.plot.call_args_list]
        if plot_calls:
            assert any('linewidth' in call[1] and call[1]['linewidth'] == 3 for call in plot_calls)
            
    def test_learning_curve_save_to_file(self, sample_metrics_df):
        """Test saving learning curve to file"""
        from scitex.ai.plt import learning_curve
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            spath = tmp.name
            
        try:
            with patch('scitex.plt.configure_mpl') as mock_config:
                with patch('scitex.plt.subplots') as mock_subplots:
                    with patch('scitex.io.save') as mock_save:
                        mock_fig = MagicMock()
                        mock_ax = MagicMock()
                        mock_subplots.return_value = (mock_fig, mock_ax)
                        mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                        
                        fig = learning_curve(sample_metrics_df, keys=['loss'], spath=spath)
                        
                        # Verify save was called with correct arguments
                        mock_save.assert_called_once()
                        call_args = mock_save.call_args[0]
                        assert call_args[0] == mock_fig
                        assert call_args[1] == spath
        finally:
            if os.path.exists(spath):
                os.unlink(spath)
                
    def test_process_i_global(self):
        """Test process_i_global function"""
        from scitex.ai.plt import process_i_global
        
        # Test with i_global column
        df = pd.DataFrame({'i_global': [0, 1, 2], 'loss': [0.5, 0.4, 0.3]})
        result = process_i_global(df)
        assert result.index.name == 'i_global'
        assert 'i_global' in result.columns
        
        # Test with i_global already as index
        df = pd.DataFrame({'loss': [0.5, 0.4, 0.3]}, index=[0, 1, 2])
        df.index.name = 'i_global'
        result = process_i_global(df)
        assert result.index.name == 'i_global'
        assert 'i_global' in result.columns
        
    def test_set_yaxis_for_acc(self):
        """Test set_yaxis_for_acc function"""
        from scitex.ai.plt import set_yaxis_for_acc
        
        mock_ax = MagicMock()
        
        # Test with accuracy metric
        result = set_yaxis_for_acc(mock_ax, 'accuracy')
        mock_ax.set_ylim.assert_called_with(0, 1)
        mock_ax.set_yticks.assert_called_with([0, 0.5, 1.0])
        
        # Test with non-accuracy metric
        mock_ax.reset_mock()
        result = set_yaxis_for_acc(mock_ax, 'loss')
        mock_ax.set_ylim.assert_not_called()
        
    def test_plot_tra(self, sample_metrics_df):
        """Test plot_tra function for training data"""
        from scitex.ai.plt import plot_tra
        
        mock_ax = MagicMock()
        result = plot_tra(mock_ax, sample_metrics_df, 'loss', lw=2, color='blue')
        
        # Verify plot was called
        mock_ax.plot.assert_called()
        # Verify legend was added
        mock_ax.legend.assert_called()
        
    def test_scatter_val(self, sample_metrics_df):
        """Test scatter_val function for validation data"""
        from scitex.ai.plt import scatter_val
        
        mock_ax = MagicMock()
        result = scatter_val(mock_ax, sample_metrics_df, 'loss', s=5, color='green')
        
        # Verify scatter was called
        mock_ax.scatter.assert_called()
        # Verify legend was added
        mock_ax.legend.assert_called()
        
    def test_scatter_tes(self, sample_metrics_df):
        """Test scatter_tes function for test data"""
        from scitex.ai.plt import scatter_tes
        
        mock_ax = MagicMock()
        result = scatter_tes(mock_ax, sample_metrics_df, 'loss', s=5, color='red')
        
        # Verify scatter was called
        mock_ax.scatter.assert_called()
        # Verify legend was added
        mock_ax.legend.assert_called()
        
    def test_vline_at_epochs(self, sample_metrics_df):
        """Test vline_at_epochs function"""
        from scitex.ai.plt import vline_at_epochs
        
        mock_ax = MagicMock()
        result = vline_at_epochs(mock_ax, sample_metrics_df, color='grey')
        
        # Verify vlines was called
        mock_ax.vlines.assert_called()
        
    def test_select_ticks(self, sample_metrics_df):
        """Test select_ticks function"""
        from scitex.ai.plt import select_ticks
        
        selected_ticks, selected_labels = select_ticks(sample_metrics_df, max_n_ticks=4)
        
        assert len(selected_ticks) <= 4
        assert len(selected_labels) <= 4
        assert len(selected_ticks) == len(selected_labels)
        
    def test_learning_curve_empty_data(self):
        """Test learning curve with empty dataframe"""
        from scitex.ai.plt import learning_curve
        
        empty_df = pd.DataFrame(columns=['step', 'i_global', 'i_epoch', 'i_batch', 'loss'])
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(empty_df, keys=['loss'])
                    
        assert fig is not None
        
    def test_learning_curve_missing_column(self, sample_metrics_df):
        """Test learning curve with missing metric column"""
        from scitex.ai.plt import learning_curve
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    # This should handle the missing column gracefully
                    fig = learning_curve(sample_metrics_df, keys=['nonexistent_metric'])
                    
        assert fig is not None
        
    def test_learning_curve_single_step_type(self, sample_metrics_df):
        """Test learning curve with only one type of step (e.g., only training)"""
        from scitex.ai.plt import learning_curve
        
        # Filter to only training data
        train_only_df = sample_metrics_df[sample_metrics_df['step'] == 'Training'].copy()
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_ax = MagicMock()
                    mock_subplots.return_value = (mock_fig, mock_ax)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(train_only_df, keys=['loss'])
                    
        assert fig is not None
        
    def test_learning_curve_max_n_ticks(self, sample_metrics_df):
        """Test learning curve with different max_n_ticks values"""
        from scitex.ai.plt import learning_curve
        
        for max_ticks in [2, 4, 8]:
            with patch('scitex.plt.configure_mpl') as mock_config:
                with patch('scitex.plt.subplots') as mock_subplots:
                    with patch('scitex.io.save'):
                        mock_fig = MagicMock()
                        mock_ax = MagicMock()
                        mock_subplots.return_value = (mock_fig, mock_ax)
                        mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                        
                        fig = learning_curve(
                            sample_metrics_df, 
                            keys=['loss'], 
                            max_n_ticks=max_ticks
                        )
                        
            assert fig is not None
            
    def test_learning_curve_special_metrics(self, sample_metrics_df):
        """Test learning curve with accuracy-like metrics"""
        from scitex.ai.plt import learning_curve
        
        # Add some accuracy-like metrics
        sample_metrics_df['val_acc'] = np.random.beta(5, 2, len(sample_metrics_df))
        sample_metrics_df['train_accuracy'] = np.random.beta(5, 2, len(sample_metrics_df))
        
        with patch('scitex.plt.configure_mpl') as mock_config:
            with patch('scitex.plt.subplots') as mock_subplots:
                with patch('scitex.io.save'):
                    mock_fig = MagicMock()
                    mock_axes = [MagicMock(), MagicMock()]
                    mock_subplots.return_value = (mock_fig, mock_axes)
                    mock_config.return_value = (MagicMock(), {'blue': 'blue', 'green': 'green', 'red': 'red'})
                    
                    fig = learning_curve(
                        sample_metrics_df, 
                        keys=['val_acc', 'train_accuracy']
                    )
                    
        # Both axes should have been set with accuracy limits
        for ax in mock_axes:
            ax.set_ylim.assert_called_with(0, 1)
            ax.set_yticks.assert_called_with([0, 0.5, 1.0])
            
    def test_learning_curve_integration(self, sample_metrics_df):
        """Integration test with minimal mocking"""
        from scitex.ai.plt import learning_curve
        
        plt.ioff()  # Prevent display
        
        try:
            with patch('scitex.io.save'):
                # This should work with real matplotlib components where possible
                fig = learning_curve(sample_metrics_df, keys=['loss', 'accuracy'])
                
            assert fig is not None
            plt.close(fig)
        finally:
            plt.ion()


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/plt/_learning_curve.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-12 19:52:48 (ywatanabe)"
#
# import re
#
# import matplotlib
# import matplotlib.pyplot as plt
# import scitex
# import numpy as np
# import pandas as pd
#
#
# def process_i_global(metrics_df):
#     if metrics_df.index.name != "i_global":
#         try:
#             metrics_df = metrics_df.set_index("i_global")
#         except KeyError:
#             print(
#                 "Error: The DataFrame does not contain a column named 'i_global'. Please check the column names."
#             )
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
#     else:
#         print("The index is already set to 'i_global'.")
#     metrics_df["i_global"] = metrics_df.index  # alias
#     return metrics_df
#
#
# def set_yaxis_for_acc(ax, key_plt):
#     if re.search("[aA][cC][cC]", key_plt):  # acc, ylim, yticks
#         ax.set_ylim(0, 1)
#         ax.set_yticks([0, 0.5, 1.0])
#     return ax
#
#
# def plot_tra(ax, metrics_df, key_plt, lw=1, color="blue"):
#     indi_step = scitex.gen.search(
#         "^[Tt]rain(ing)?", metrics_df.step, as_bool=True
#     )[0]
#     step_df = metrics_df[indi_step]
#
#     if len(step_df) != 0:
#         ax.plot(
#             step_df.index,  # i_global
#             step_df[key_plt],
#             label="Training",
#             color=color,
#             linewidth=lw,
#         )
#         ax.legend()
#
#     return ax
#
#
# def scatter_val(ax, metrics_df, key_plt, s=3, color="green"):
#     indi_step = scitex.gen.search(
#         "^[Vv]alid(ation)?", metrics_df.step, as_bool=True
#     )[0]
#     step_df = metrics_df[indi_step]
#     if len(step_df) != 0:
#         ax.scatter(
#             step_df.index,
#             step_df[key_plt],
#             label="Validation",
#             color=color,
#             s=s,
#             alpha=0.9,
#         )
#         ax.legend()
#     return ax
#
#
# def scatter_tes(ax, metrics_df, key_plt, s=3, color="red"):
#     indi_step = scitex.gen.search("^[Tt]est", metrics_df.step, as_bool=True)[0]
#     step_df = metrics_df[indi_step]
#     if len(step_df) != 0:
#         ax.scatter(
#             step_df.index,
#             step_df[key_plt],
#             label="Test",
#             color=color,
#             s=s,
#             alpha=0.9,
#         )
#         ax.legend()
#     return ax
#
#
# def vline_at_epochs(ax, metrics_df, color="grey"):
#     # Determine the global iteration values where new epochs start
#     epoch_starts = metrics_df[metrics_df["i_batch"] == 0].index.values
#     epoch_labels = metrics_df[metrics_df["i_batch"] == 0].index.values
#     ax.vlines(
#         x=epoch_starts,
#         ymin=-1e4,  # ax.get_ylim()[0],
#         ymax=1e4,  # ax.get_ylim()[1],
#         linestyle="--",
#         color=color,
#     )
#     return ax
#
#
# def select_ticks(metrics_df, max_n_ticks=4):
#     # Calculate epoch starts and their corresponding labels for ticks
#     unique_epochs = metrics_df["i_epoch"].drop_duplicates().values
#     epoch_starts = (
#         metrics_df[metrics_df["i_batch"] == 0]["i_global"]
#         .drop_duplicates()
#         .values
#     )
#
#     # Given the performance issue, let's just select a few epoch starts for labeling
#     # We use MaxNLocator to pick ticks; however, it's used here to choose a reasonable number of epoch markers
#     if len(epoch_starts) > max_n_ticks:
#         selected_ticks = np.linspace(
#             epoch_starts[0], epoch_starts[-1], max_n_ticks, dtype=int
#         )
#         # Ensure selected ticks are within the epoch starts for accurate labeling
#         selected_labels = [
#             metrics_df[metrics_df["i_global"] == tick]["i_epoch"].iloc[0]
#             for tick in selected_ticks
#         ]
#     else:
#         selected_ticks = epoch_starts
#         selected_labels = unique_epochs
#     return selected_ticks, selected_labels
#
#
# def learning_curve(
#     metrics_df,
#     keys,
#     title="Title",
#     max_n_ticks=4,
#     scattersize=3,
#     linewidth=1,
#     yscale="linear",
#     spath=None,
# ):
#     _plt, cc = scitex.plt.configure_mpl(plt, show=False)
#     """
#     Example:
#         print(metrics_df)
#         #                 step  i_global  i_epoch  i_batch      loss
#         # 0       Training         0        0        0  0.717023
#         # 1       Training         1        0        1  0.703844
#         # 2       Training         2        0        2  0.696279
#         # 3       Training         3        0        3  0.685384
#         # 4       Training         4        0        4  0.670675
#         # ...          ...       ...      ...      ...       ...
#         # 123266      Test     66900      299      866  0.000067
#         # 123267      Test     66900      299      867  0.000067
#         # 123268      Test     66900      299      868  0.000067
#         # 123269      Test     66900      299      869  0.000067
#         # 123270      Test     66900      299      870  0.000068
#
#         # [123271 rows x 5 columns]
#     """
#     metrics_df = process_i_global(metrics_df)
#     selected_ticks, selected_labels = select_ticks(metrics_df)
#
#     # fig, axes = plt.subplots(len(keys), 1, sharex=True, sharey=False)
#     fig, axes = scitex.plt.subplots(len(keys), 1, sharex=True, sharey=False)
#     axes = axes if len(keys) != 1 else [axes]
#
#     axes[-1].set_xlabel("Iteration #")
#     fig.text(0.5, 0.95, title, ha="center")
#
#     for i_plt, key_plt in enumerate(keys):
#         ax = axes[i_plt]
#         ax.set_yscale(yscale)
#         ax.set_ylabel(key_plt)
#
#         ax = set_yaxis_for_acc(ax, key_plt)
#         ax = plot_tra(ax, metrics_df, key_plt, lw=linewidth, color=cc["blue"])
#         ax = scatter_val(
#             ax, metrics_df, key_plt, s=scattersize, color=cc["green"]
#         )
#         ax = scatter_tes(
#             ax, metrics_df, key_plt, s=scattersize, color=cc["red"]
#         )
#
#         # # Custom tick marks
#         # ax = scitex.plt.ax.map_ticks(
#         #     ax, selected_ticks, selected_labels, axis="x"
#         # )
#
#     if spath is not None:
#         scitex.io.save(fig, spath)
#
#     return fig
#
#
# if __name__ == "__main__":
#
#     plt, cc = scitex.plt.configure_mpl(plt)
#     # lpath = "./scripts/ml/.old/pretrain_EEGPT_old/2024-01-29-12-04_eDflsnWv_v8/metrics.csv"
#     lpath = "./scripts/ml/pretrain_EEGPT/[DEBUG] 2024-02-11-06-45_4uUpdfpb/metrics.csv"
#
#     sdir, _, _ = scitex.gen.split_fpath(lpath)
#     metrics_df = scitex.io.load(lpath)
#     fig = learning_curve(
#         metrics_df, title="Pretraining on db_v8", yscale="log"
#     )
#     # plt.show()
#     scitex.io.save(fig, sdir + "learning_curve.png")

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/plt/_learning_curve.py
# --------------------------------------------------------------------------------
