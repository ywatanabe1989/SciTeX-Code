#!/usr/bin/env python3
"""
Improved Multiple Tasks Classification Reporter with unified API.

Enhanced version that addresses all identified issues:
- Unified API interface matching SingleTaskClassificationReporter
- Lazy directory creation
- Numerical precision control
- Graceful plotting with error handling
- Consistent parameter names
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np

# Import base class and improved single reporter
from ._BaseClassificationReporter import BaseClassificationReporter, ReporterConfig
from ._SingleClassificationReporter import SingleTaskClassificationReporter
from .reporter_utils.storage import MetricStorage


class MultipleTasksClassificationReporter(BaseClassificationReporter):
    """
    Improved multi-task classification reporter with unified API.
    
    This reporter manages multiple SingleTaskClassificationReporter instances,
    one for each target/task, providing a unified interface for multi-task scenarios.
    
    Key improvements:
    - Same API as SingleTaskClassificationReporter (calculate_metrics method)
    - Lazy directory creation (no empty folders)
    - Numerical precision control
    - Graceful plotting with proper error handling
    - Consistent parameter names across all methods
    
    Parameters
    ----------
    name : str
        Base experiment name
    output_dir : Union[str, Path], optional
        Base directory for outputs
    target_classes : List[str], optional
        List of target class names or identifiers
    config : ReporterConfig, optional
        Configuration object for advanced settings
    **kwargs
        Additional arguments passed to base class
    """
    
    def __init__(
        self,
        name: str,
        output_dir: Union[str, Path] = None,
        target_classes: Optional[List[str]] = None,
        config: Optional[ReporterConfig] = None,
        **kwargs
    ):
        # Use config or create default
        if config is None:
            config = ReporterConfig()
        
        # Initialize base class
        super().__init__(
            name=name,
            output_dir=output_dir,
            create_dirs=not config.lazy_directories,
            precision=config.precision,
            enable_plotting=config.enable_plotting,
            **kwargs
        )
        
        self.config = config
        self.storage = MetricStorage(self.output_dir, precision=self.precision)
        
        # Setup target classes
        if target_classes is None:
            target_classes = ["default"]
        self.target_classes = target_classes
        
        # Create individual reporters for each target
        self.reporters: Dict[str, SingleTaskClassificationReporter] = {}
        self._setup_target_reporters()
        
        # Save configuration
        self._save_config()
        
        # Print initialization info
        print(f"\n{'='*70}")
        print(f"Multi-Task Classification Reporter Initialized")
        print(f"{'='*70}")
        print(f"Experiment: {name}")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print(f"Target Classes: {target_classes}")
        print(f"{'='*70}\n")
    
    def _setup_target_reporters(self) -> None:
        """Setup individual reporters for each target."""
        for target in self.target_classes:
            target_output_dir = self.output_dir / target
            
            # Create reporter with same config but no directory creation yet
            target_config = ReporterConfig(
                precision=self.config.precision,
                enable_plotting=self.config.enable_plotting,
                lazy_directories=True,  # Always lazy for sub-reporters
                required_metrics=self.config.required_metrics
            )
            
            self.reporters[target] = SingleTaskClassificationReporter(
                name=f"{self.name}_{target}",
                output_dir=target_output_dir,
                config=target_config
            )
    
    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        fold_idx: Optional[int] = None,
        target: Optional[str] = None,
        save: bool = True,
        plot: bool = None
    ) -> Dict[str, Any]:
        """
        Calculate metrics for a specific target using unified API.
        
        This method has the same signature as SingleTaskClassificationReporter
        but with an additional 'target' parameter to specify which task.
        
        Parameters
        ----------
        y_true : np.ndarray
            True class labels
        y_pred : np.ndarray
            Predicted class labels
        y_proba : np.ndarray, optional
            Prediction probabilities (required for AUC metrics)
        labels : List[str], optional
            Class labels for display
        fold_idx : int, optional
            Fold index for cross-validation
        target : str, optional
            Target class identifier. If None, uses first target.
        save : bool, default True
            Whether to save results to disk
        plot : bool, optional
            Whether to generate plots (uses instance setting if None)
            
        Returns
        -------
        Dict[str, Any]
            Dictionary of calculated metrics for the specified target
        """
        # Default to first target if not specified
        if target is None:
            target = self.target_classes[0]
        
        # Validate target
        if target not in self.reporters:
            raise ValueError(f"Unknown target '{target}'. Available targets: {list(self.reporters.keys())}")
        
        # Delegate to appropriate single-task reporter
        return self.reporters[target].calculate_metrics(
            y_true=y_true,
            y_pred=y_pred,
            y_proba=y_proba,
            labels=labels,
            fold_idx=fold_idx,
            save=save,
            plot=plot
        )
    
    def calculate_metrics_for_all_targets(
        self,
        targets_data: Dict[str, Dict[str, np.ndarray]],
        fold_idx: Optional[int] = None,
        save: bool = True,
        plot: bool = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate metrics for all targets in batch.
        
        Parameters
        ----------
        targets_data : Dict[str, Dict[str, np.ndarray]]
            Dictionary mapping target names to their data:
            {
                'target1': {
                    'y_true': np.array(...),
                    'y_pred': np.array(...),
                    'y_proba': np.array(...),  # optional
                    'labels': ['class1', 'class2']  # optional
                },
                'target2': {...}
            }
        fold_idx : int, optional
            Fold index for cross-validation
        save : bool, default True
            Whether to save results to disk
        plot : bool, optional
            Whether to generate plots
            
        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary mapping target names to their metrics
        """
        all_results = {}
        
        for target_name, data in targets_data.items():
            if target_name not in self.reporters:
                print(f"Warning: Unknown target '{target_name}', skipping")
                continue
            
            # Extract data with defaults
            y_true = data['y_true']
            y_pred = data['y_pred']
            y_proba = data.get('y_proba', None)
            labels = data.get('labels', None)
            
            # Calculate metrics for this target
            all_results[target_name] = self.calculate_metrics(
                y_true=y_true,
                y_pred=y_pred,
                y_proba=y_proba,
                labels=labels,
                fold_idx=fold_idx,
                target=target_name,
                save=save,
                plot=plot
            )
        
        return all_results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all calculated metrics across all targets.
        
        Returns
        -------
        Dict[str, Any]
            Summary statistics across all targets and folds
        """
        summary = {
            "experiment_name": self.name,
            "target_classes": self.target_classes,
            "targets_summary": {}
        }
        
        # Get summary from each target reporter
        for target_name, reporter in self.reporters.items():
            target_summary = reporter.get_summary()
            summary["targets_summary"][target_name] = target_summary
        
        return summary
    
    def save_summary(self, filename: str = "multi_task_summary.json") -> Path:
        """
        Save multi-task summary to file.
        
        Parameters
        ----------
        filename : str, default "multi_task_summary.json"
            Filename for summary
            
        Returns
        -------
        Path
            Path to saved summary file
        """
        summary = self.get_summary()
        return self.storage.save(summary, filename)
    
    def get_reporter_for_target(self, target: str) -> SingleTaskClassificationReporter:
        """
        Get the individual reporter for a specific target.
        
        Parameters
        ----------
        target : str
            Target identifier
            
        Returns
        -------
        SingleTaskClassificationReporter
            The reporter instance for the specified target
        """
        if target not in self.reporters:
            raise ValueError(f"Unknown target '{target}'. Available targets: {list(self.reporters.keys())}")
        return self.reporters[target]
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        config_data = {
            "name": self.name,
            "output_dir": str(self.output_dir),
            "target_classes": self.target_classes,
            "required_metrics": self.config.required_metrics
        }
        self.storage.save(config_data, "config.json")
    
    def __repr__(self) -> str:
        target_count = len(self.target_classes)
        return (f"MultipleTasksClassificationReporter("
               f"name='{self.name}', targets={target_count}, "
               f"output_dir='{self.output_dir}')")


def create_multi_task_reporter(
    name: str,
    target_classes: List[str],
    output_dir: Union[str, Path] = None,
    **kwargs
) -> MultipleTasksClassificationReporter:
    """
    Convenience function to create a multi-task reporter.
    
    Parameters
    ----------
    name : str
        Experiment name
    target_classes : List[str]
        List of target class names
    output_dir : Union[str, Path], optional
        Output directory
    **kwargs
        Additional arguments
        
    Returns
    -------
    MultipleTasksClassificationReporter
        Configured multi-task reporter
    """
    return MultipleTasksClassificationReporter(
        name=name,
        target_classes=target_classes,
        output_dir=output_dir,
        **kwargs
    )