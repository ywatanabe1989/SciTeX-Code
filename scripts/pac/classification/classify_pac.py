#!/usr/bin/env python3
"""
PAC Classification - Research-focused script using SciTeX classification system.

This script focuses on PAC-specific research logic while delegating
general classification handling to scitex.ai.classification.
"""

import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import argparse

# Import SciTeX modules
from scitex.ai.classification import SingleTaskClassificationReporter, TimeSeriesSlidingWindowSplit
from scitex.logging import getLogger

# Import ML libraries
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

logger = getLogger(__name__)


def load_pac_data(data_path: Optional[Path] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Load PAC data for classification.

    Parameters
    ----------
    data_path : Path, optional
        Path to PAC data file

    Returns
    -------
    X : np.ndarray
        Features
    y : np.ndarray
        Labels
    timestamps : np.ndarray
        Timestamps for time series ordering
    metadata : Dict
        Data metadata
    """
    logger.info("Loading PAC data...")

    # For demo, generate synthetic PAC-like data with imbalanced classes
    # In real use, load actual PAC features here
    n_samples = 500
    n_features = 100  # e.g., frequency bands × time windows
    n_classes = 2  # Binary classification for better undersampling demo

    # Generate synthetic PAC features with class imbalance
    from sklearn.datasets import make_classification
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=30,
        n_redundant=20,
        n_classes=n_classes,
        weights=[0.8, 0.2],  # Imbalanced: 80% class 0, 20% class 1
        class_sep=1.5,
        random_state=42
    )

    # Generate timestamps (simulating temporal ordering)
    timestamps = np.arange(n_samples)

    # Define meaningful class names for PAC
    class_names = ['Normal', 'Abnormal_Coupling']

    # Create metadata with proper class names
    metadata = {
        'n_samples': n_samples,
        'n_features': n_features,
        'n_classes': n_classes,
        'feature_names': [f'pac_feature_{i}' for i in range(n_features)],
        'class_names': class_names
    }

    logger.info(f"Loaded {n_samples} samples with {n_features} features")
    logger.info(f"Classes: {metadata['class_names']}")
    logger.info(f"Class distribution: {np.bincount(y)}")

    return X, y, timestamps, metadata


def preprocess_features(
    X: np.ndarray,
    apply_scaling: bool = True,
    apply_pca: bool = False,
    n_components: int = 50
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Preprocess PAC features.

    Parameters
    ----------
    X : np.ndarray
        Raw features
    apply_scaling : bool
        Whether to apply standard scaling
    apply_pca : bool
        Whether to apply PCA
    n_components : int
        Number of PCA components

    Returns
    -------
    X_processed : np.ndarray
        Processed features
    preprocessing_info : Dict
        Preprocessing information
    """
    preprocessing_info = {}
    X_processed = X.copy()

    if apply_scaling:
        scaler = StandardScaler()
        X_processed = scaler.fit_transform(X_processed)
        preprocessing_info['scaling'] = 'StandardScaler'

    if apply_pca:
        pca = PCA(n_components=min(n_components, X.shape[1]))
        X_processed = pca.fit_transform(X_processed)
        preprocessing_info['pca'] = {
            'n_components': pca.n_components_,
            'explained_variance_ratio': pca.explained_variance_ratio_.sum()
        }
        logger.info(f"PCA: {pca.n_components_} components, "
                   f"{preprocessing_info['pca']['explained_variance_ratio']:.2%} variance explained")

    return X_processed, preprocessing_info


def get_pac_model(model_name: str = 'svm', **hyperparams):
    """
    Get PAC classification model with default or custom hyperparameters.

    Parameters
    ----------
    model_name : str
        Model type: 'svm', 'rf', or 'lr'
    **hyperparams
        Custom hyperparameters (override defaults)

    Returns
    -------
    model
        Configured model instance
    """
    # Default hyperparameters optimized for PAC data
    default_hyperparams = {
        'svm': {
            'C': 1.0,
            'kernel': 'rbf',
            'gamma': 'scale',
            'probability': True,
            'random_state': 42
        },
        'rf': {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'random_state': 42
        },
        'lr': {
            'C': 1.0,
            'max_iter': 1000,
            'solver': 'lbfgs',
            'random_state': 42
        }
    }

    # Merge with custom hyperparams
    params = default_hyperparams.get(model_name, default_hyperparams['svm'])
    params.update(hyperparams)

    # Create model
    models = {
        'svm': SVC,
        'rf': RandomForestClassifier,
        'lr': LogisticRegression
    }

    return models[model_name](**params)


def calculate_pac_specific_metrics(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    fold: int
) -> Dict[str, Any]:
    """
    Calculate PAC-specific metrics.

    This is research-specific logic that should remain in this script.
    Replace placeholder calculations with actual PAC metrics.

    Parameters
    ----------
    X_train, X_test : np.ndarray
        Training and test features
    y_train, y_test : np.ndarray
        Training and test labels
    fold : int
        Fold number

    Returns
    -------
    Dict[str, Any]
        PAC-specific metrics
    """
    return {
        'fold': fold,
        'coupling_strength_mean': np.random.rand(),  # TODO: Replace with actual PAC metric
        'coupling_strength_std': np.random.rand() * 0.1,
        'peak_frequency': np.random.rand() * 100,  # Hz
        'n_samples_train': len(X_train),
        'n_samples_test': len(X_test),
        'class_distribution_train': np.bincount(y_train).tolist(),
        'class_distribution_test': np.bincount(y_test).tolist()
    }


def run_pac_classification(
    X: np.ndarray,
    y: np.ndarray,
    timestamps: np.ndarray,
    metadata: Dict[str, Any],
    model_name: str = 'svm',
    n_folds: int = 5,
    output_dir: Optional[Path] = None,
    **model_kwargs
) -> Dict[str, Any]:
    """
    Run PAC classification experiment with time series CV.

    This is the main entry point focusing on PAC-specific research logic.
    General classification handling is delegated to SingleTaskClassificationReporter.
    Uses TimeSeriesSlidingWindowSplit with expanding window and undersampling.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix
    y : np.ndarray
        Labels
    timestamps : np.ndarray
        Timestamps for temporal ordering
    metadata : Dict[str, Any]
        Dataset metadata
    model_name : str
        Model type ('svm', 'rf', 'lr')
    n_folds : int
        Number of CV folds
    output_dir : Path, optional
        Output directory
    **model_kwargs
        Custom model hyperparameters

    Returns
    -------
    Dict[str, Any]
        Experiment results
    """
    logger.info("="*70)
    logger.info("PAC CLASSIFICATION EXPERIMENT")
    logger.info("="*70)

    # Set output directory
    if output_dir is None:
        output_dir = Path("./.dev/results/pac_classification")

    # Initialize reporter - handles all general classification logic
    reporter = SingleTaskClassificationReporter(
        output_dir=output_dir / model_name,
        verbose=True
    )

    # Save PAC experiment metadata
    experiment_metadata = {
        'experiment': 'PAC Classification',
        'dataset': metadata,
        'model_type': model_name,
        'cross_validation': {
            'n_folds': n_folds,
            'strategy': 'TimeSeriesSlidingWindowSplit',
            'expanding_window': True,
            'undersampling': True,
            'random_state': 42
        }
    }
    reporter.save(experiment_metadata, "experiment/metadata.json")

    # Time series cross-validation with expanding window and undersampling
    # Calculate appropriate window sizes based on n_folds
    n_samples = len(X)
    test_size = n_samples // (n_folds + 1)  # Reserve data for each fold
    window_size = test_size * 2  # Start with 2x test size

    cv = TimeSeriesSlidingWindowSplit(
        window_size=window_size,
        test_size=test_size,
        step_size=test_size,  # Non-overlapping folds
        gap=0,
        expanding_window=True,  # Training set grows over time
        undersample=True,  # Balance classes in training
        overlapping_tests=False,
        random_state=42
    )

    logger.info(f"Time Series CV: window={window_size}, test={test_size}, expanding+undersample")

    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y, timestamps)):
        logger.info(f"Fold {fold + 1}/{n_folds}")

        # Split data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Preprocess
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        model = get_pac_model(model_name, **model_kwargs)
        model.fit(X_train_scaled, y_train)

        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)

        # DELEGATED: Calculate standard metrics automatically
        # The reporter handles balanced_accuracy, MCC, confusion matrix,
        # classification report, ROC-AUC, PR-AUC, and all visualizations
        reporter.calculate_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            labels=metadata['class_names'],
            fold=fold
        )

        # RESEARCH-SPECIFIC: Calculate PAC-specific metrics
        pac_metrics = calculate_pac_specific_metrics(
            X_train, X_test, y_train, y_test, fold
        )
        reporter.save(pac_metrics, f"pac_metrics_fold_{fold:02d}.json", fold=fold)

    # DELEGATED: Generate comprehensive reports and visualizations
    # This automatically creates:
    # - CV summary plots (ROC, PR, confusion matrix)
    # - Per-fold plots
    # - Multi-format reports (Org, Markdown, LaTeX, PDF)
    # - All with proper fold aggregation
    reporter.save_summary()

    logger.info("="*70)
    logger.info("PAC Classification Complete")
    logger.info(f"Results saved to: {reporter.output_dir}")
    logger.info("="*70)

    return {
        'reporter': reporter,
        'output_dir': reporter.output_dir,
        'summary': reporter.get_summary()
    }


def main():
    """Main function for PAC classification."""
    parser = argparse.ArgumentParser(
        description="PAC Classification with SciTeX",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--model',
        choices=['svm', 'rf', 'lr'],
        default='svm',
        help='Model to use'
    )
    parser.add_argument(
        '--n-folds',
        type=int,
        default=5,
        help='Number of CV folds'
    )
    parser.add_argument(
        '--data-path',
        type=Path,
        help='Path to PAC data file (optional, uses synthetic data by default)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for results'
    )
    parser.add_argument(
        '--preprocess',
        action='store_true',
        help='Apply preprocessing (scaling + PCA)'
    )

    args = parser.parse_args()

    # Load PAC data with timestamps
    X, y, timestamps, metadata = load_pac_data(args.data_path)

    # Preprocess if requested
    if args.preprocess:
        logger.info("Applying preprocessing...")
        X, preprocessing_info = preprocess_features(
            X,
            apply_scaling=True,
            apply_pca=True,
            n_components=50
        )
        metadata['preprocessing'] = preprocessing_info

    # Run classification with time series CV
    results = run_pac_classification(
        X, y, timestamps, metadata,
        model_name=args.model,
        n_folds=args.n_folds,
        output_dir=args.output_dir
    )

    logger.info("Experiment completed successfully")
    logger.info(f"Check {results['output_dir']} for detailed reports")


if __name__ == "__main__":
    main()
