#!/usr/bin/env python3
"""
Storage utilities for classification metrics - decoupled from scitex.io.

Provides simple, standalone storage functions without external dependencies.
"""

import json
import pickle
from pathlib import Path
from typing import Any, Union, Dict, Optional
import pandas as pd
import numpy as np
import matplotlib.figure
import yaml


class MetricStorage:
    """
    Simple storage handler for metrics without external dependencies.
    
    This class handles saving different data types to appropriate formats
    without relying on scitex.io.save.
    """
    
    def __init__(self, base_dir: Union[str, Path]):
        """
        Initialize storage with base directory.
        
        Parameters
        ----------
        base_dir : Union[str, Path]
            Base directory for saving files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: Any, relative_path: Union[str, Path]) -> Path:
        """
        Save data to file with format determined by extension.
        
        Parameters
        ----------
        data : Any
            Data to save
        relative_path : Union[str, Path]
            Path relative to base_dir, including filename and extension
            
        Returns
        -------
        Path
            Absolute path to saved file
            
        Examples
        --------
        >>> storage = MetricStorage("./results")
        >>> storage.save({'accuracy': 0.95}, "metrics/fold_01.json")
        >>> storage.save(df, "tables/results.csv")
        >>> storage.save(fig, "plots/roc_curve.png")
        """
        # Construct full path
        full_path = self.base_dir / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format from extension
        extension = full_path.suffix.lower()
        
        # Special handling for confusion matrices - save as CSV instead of numpy
        if (isinstance(data, dict) and 
            data.get('metric') == 'confusion_matrix' and 
            extension == '.npy'):
            # Change extension to CSV for confusion matrices
            full_path = full_path.with_suffix('.csv')
            extension = '.csv'
        
        # Save based on extension
        if extension == '.json':
            self._save_json(data, full_path)
        elif extension == '.csv':
            self._save_csv(data, full_path)
        elif extension == '.pkl' or extension == '.pickle':
            self._save_pickle(data, full_path)
        elif extension == '.npy':
            self._save_numpy(data, full_path)
        elif extension == '.npz':
            self._save_numpy_compressed(data, full_path)
        elif extension in ['.yaml', '.yml']:
            self._save_yaml(data, full_path)
        elif extension in ['.png', '.jpg', '.jpeg', '.pdf', '.svg']:
            self._save_figure(data, full_path)
        elif extension == '.txt':
            self._save_text(data, full_path)
        else:
            # Default to pickle for unknown extensions
            self._save_pickle(data, full_path.with_suffix('.pkl'))
            
        return full_path
    
    def save_figure(self, fig: Any, relative_path: Union[str, Path]) -> Path:
        """
        Save a matplotlib figure.
        
        This is a convenience method that wraps the save method.
        
        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Figure to save
        relative_path : Union[str, Path]
            Path relative to base_dir
            
        Returns
        -------
        Path
            Absolute path to saved file
        """
        return self.save(fig, relative_path)
    
    def _save_json(self, data: Any, path: Path) -> None:
        """Save data as JSON."""
        # Convert numpy types to Python types
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient='records')
            elif isinstance(obj, pd.Series):
                return obj.to_dict()
            return obj
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=convert)
    
    def _save_csv(self, data: Any, path: Path) -> None:
        """Save data as CSV."""
        if isinstance(data, pd.DataFrame):
            data.to_csv(path, index=True)
        elif isinstance(data, pd.Series):
            data.to_csv(path)
        elif isinstance(data, np.ndarray):
            pd.DataFrame(data).to_csv(path, index=False)
        elif isinstance(data, dict) and data.get('metric') == 'confusion_matrix':
            # Special handling for confusion matrix dictionaries
            cm_array = data['value']
            labels = data.get('labels', [f'Class_{i}' for i in range(cm_array.shape[0])])
            
            # Create DataFrame with proper labels
            df = pd.DataFrame(cm_array, index=labels, columns=labels)
            
            # Add metadata as comments in the CSV
            with open(path, 'w') as f:
                f.write(f"# Confusion Matrix - Fold {data.get('fold', 'Unknown')}\n")
                f.write(f"# Labels: {', '.join(labels)}\n")
                f.write("# Rows: True Labels, Columns: Predicted Labels\n")
                df.to_csv(f, index=True)
        else:
            # Try to convert to DataFrame
            pd.DataFrame(data).to_csv(path, index=False)
    
    def _save_pickle(self, data: Any, path: Path) -> None:
        """Save data as pickle."""
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def _save_numpy(self, data: np.ndarray, path: Path) -> None:
        """Save numpy array."""
        np.save(path, data)
    
    def _save_numpy_compressed(self, data: Union[np.ndarray, Dict], path: Path) -> None:
        """Save compressed numpy array(s)."""
        if isinstance(data, dict):
            np.savez_compressed(path, **data)
        else:
            np.savez_compressed(path, data=data)
    
    def _save_yaml(self, data: Any, path: Path) -> None:
        """Save data as YAML."""
        # Convert numpy/pandas types
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient='records')
            elif isinstance(obj, pd.Series):
                return obj.to_dict()
            return obj
        
        # Recursively convert the data
        if isinstance(data, dict):
            converted = {k: convert(v) for k, v in data.items()}
        else:
            converted = convert(data)
            
        with open(path, 'w') as f:
            yaml.dump(converted, f, default_flow_style=False)
    
    def _save_figure(self, fig: matplotlib.figure.Figure, path: Path) -> None:
        """Save matplotlib figure."""
        if hasattr(fig, 'savefig'):
            fig.savefig(path, dpi=100, bbox_inches='tight')
        else:
            # Try to get current figure
            import matplotlib.pyplot as plt
            plt.savefig(path, dpi=100, bbox_inches='tight')
    
    def _save_text(self, data: str, path: Path) -> None:
        """Save text data."""
        with open(path, 'w') as f:
            f.write(str(data))
    
    def load(self, relative_path: Union[str, Path]) -> Any:
        """
        Load data from file based on extension.
        
        Parameters
        ----------
        relative_path : Union[str, Path]
            Path relative to base_dir
            
        Returns
        -------
        Any
            Loaded data
        """
        full_path = self.base_dir / relative_path
        extension = full_path.suffix.lower()
        
        if extension == '.json':
            with open(full_path, 'r') as f:
                return json.load(f)
        elif extension == '.csv':
            return pd.read_csv(full_path, index_col=0)
        elif extension in ['.pkl', '.pickle']:
            with open(full_path, 'rb') as f:
                return pickle.load(f)
        elif extension == '.npy':
            return np.load(full_path)
        elif extension == '.npz':
            return np.load(full_path)
        elif extension in ['.yaml', '.yml']:
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        elif extension == '.txt':
            with open(full_path, 'r') as f:
                return f.read()
        else:
            raise ValueError(f"Unknown file extension: {extension}")
    
    def exists(self, relative_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        return (self.base_dir / relative_path).exists()
    
    def list_files(self, pattern: str = "*") -> list:
        """List files matching pattern."""
        return list(self.base_dir.glob(pattern))


# Standalone convenience functions
def save_metric(
    metric_value: Union[float, Dict[str, float]], 
    path: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Save a metric value with optional metadata.
    
    Parameters
    ----------
    metric_value : Union[float, Dict[str, float]]
        Metric value(s) to save
    path : Union[str, Path]
        Path to save to
    metadata : Dict[str, Any], optional
        Additional metadata to include
        
    Examples
    --------
    >>> save_metric(0.95, "accuracy.json", {'fold': 1, 'dataset': 'test'})
    >>> save_metric({'acc': 0.95, 'mcc': 0.82}, "metrics.json")
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {}
    if isinstance(metric_value, dict):
        data.update(metric_value)
    else:
        data['value'] = metric_value
    
    if metadata:
        data.update(metadata)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return path


def save_figure(
    fig: matplotlib.figure.Figure,
    path: Union[str, Path],
    dpi: int = 100
) -> None:
    """
    Save matplotlib figure.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save
    path : Union[str, Path]
        Path to save to
    dpi : int
        Resolution for raster formats
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches='tight')


def save_dataframe(
    df: pd.DataFrame,
    path: Union[str, Path],
    index: bool = True
) -> None:
    """
    Save pandas DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save
    path : Union[str, Path]
        Path to save to (extension determines format)
    index : bool
        Whether to save index
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    extension = path.suffix.lower()
    if extension == '.csv':
        df.to_csv(path, index=index)
    elif extension == '.json':
        df.to_json(path, orient='records', indent=2)
    elif extension in ['.xlsx', '.xls']:
        df.to_excel(path, index=index)
    elif extension in ['.pkl', '.pickle']:
        df.to_pickle(path)
    else:
        # Default to CSV
        df.to_csv(path.with_suffix('.csv'), index=index)


def organize_outputs(
    base_dir: Union[str, Path],
    create_structure: bool = True
) -> Dict[str, Path]:
    """
    Create and return standard directory structure.
    
    Parameters
    ----------
    base_dir : Union[str, Path]
        Base directory for outputs
    create_structure : bool
        Whether to create directories
        
    Returns
    -------
    Dict[str, Path]
        Dictionary of directory paths
        
    Examples
    --------
    >>> dirs = organize_outputs("./results")
    >>> save_metric(0.95, dirs['metrics'] / "accuracy.json")
    """
    base_dir = Path(base_dir)
    
    structure = {
        'base': base_dir,
        'metrics': base_dir / 'metrics',
        'figures': base_dir / 'figures',
        'tables': base_dir / 'tables',
        'reports': base_dir / 'reports',
        'models': base_dir / 'models',
        'logs': base_dir / 'logs'
    }
    
    if create_structure:
        for dir_path in structure.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return structure