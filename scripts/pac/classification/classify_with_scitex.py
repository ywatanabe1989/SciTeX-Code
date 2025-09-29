#!/usr/bin/env python3
"""
PAC Classification using the new SciTeX classification system.

This script demonstrates how to use the new enhanced classification
reporter and cross-validation utilities for PAC analysis.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import argparse

# Import SciTeX modules
import scitex as stx
from scitex.ai.classification import (
    SingleClassificationReporter,  # This now uses v2 by default
    CrossValidationExperiment,
    quick_experiment
)

# Import ML libraries
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


def load_pac_data(data_path: Optional[Path] = None) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
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
    metadata : Dict
        Data metadata
    """
    # For demo, generate synthetic PAC-like data
    # In real use, load actual PAC features here
    
    print("Loading PAC data...")
    
    # Example: Generate synthetic data mimicking PAC features
    n_samples = 500
    n_features = 100  # e.g., frequency bands × time windows
    n_classes = 3  # e.g., low/medium/high coupling
    
    # Generate synthetic PAC features
    from sklearn.datasets import make_classification
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=30,
        n_redundant=20,
        n_classes=n_classes,
        class_sep=1.5,
        random_state=42
    )
    
    # Define meaningful class names for PAC
    class_names = ['Low_Coupling', 'Medium_Coupling', 'High_Coupling'][:n_classes]
    
    # Create metadata with proper class names
    metadata = {
        'n_samples': n_samples,
        'n_features': n_features,
        'n_classes': n_classes,
        'feature_names': [f'pac_feature_{i}' for i in range(n_features)],
        'class_names': class_names  # Make sure this is properly set
    }
    
    print(f"  Loaded {n_samples} samples with {n_features} features")
    print(f"  Classes: {metadata['class_names']}")
    print(f"  Class distribution: {np.bincount(y)}")
    
    return X, y, metadata


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
        print(f"  PCA: {pca.n_components_} components, "
              f"{preprocessing_info['pca']['explained_variance_ratio']:.2%} variance explained")
    
    return X_processed, preprocessing_info


def run_pac_classification_simple(
    X: np.ndarray,
    y: np.ndarray,
    metadata: Dict[str, Any],
    model_name: str = 'svm',
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run PAC classification using the simple quick_experiment function.
    
    This is the easiest way to get started.
    """
    print("\n" + "="*70)
    print("PAC CLASSIFICATION - Simple Mode")
    print("="*70)
    
    # Define models
    models = {
        'svm': SVC(probability=True, kernel='rbf', random_state=42),
        'rf': RandomForestClassifier(n_estimators=100, random_state=42),
        'lr': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    model = models.get(model_name, models['svm'])
    
    # Run experiment with one function call
    results = quick_experiment(
        X, y,
        model=model,
        name=f"pac_{model_name}_simple",
        n_folds=5
    )
    
    print(f"\n✅ Classification complete!")
    print(f"   Report: {results['paths']['final_report']}")
    
    return results


def run_pac_classification_advanced(
    X: np.ndarray,
    y: np.ndarray,
    metadata: Dict[str, Any],
    model_name: str = 'svm',
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run PAC classification using the advanced CrossValidationExperiment.
    
    This provides more control and tracking.
    """
    print("\n" + "="*70)
    print("PAC CLASSIFICATION - Advanced Mode")
    print("="*70)
    
    # Set output directory
    if output_dir is None:
        output_dir = Path("./results/pac_classification")
    
    # Define model with hyperparameters
    if model_name == 'svm':
        hyperparams = {
            'C': 1.0,
            'kernel': 'rbf',
            'gamma': 'scale',
            'probability': True,
            'random_state': 42
        }
        model_fn = lambda: SVC(**hyperparams)
    elif model_name == 'rf':
        hyperparams = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'random_state': 42
        }
        model_fn = lambda: RandomForestClassifier(**hyperparams)
    else:  # logistic regression
        hyperparams = {
            'C': 1.0,
            'max_iter': 1000,
            'solver': 'lbfgs',
            'random_state': 42
        }
        model_fn = lambda: LogisticRegression(**hyperparams)
    
    # Create experiment with custom settings
    experiment = CrossValidationExperiment(
        name=f"pac_{model_name}_advanced",
        model_fn=model_fn,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        output_dir=output_dir / model_name,
        metrics=['balanced_accuracy', 'mcc', 'roc_auc', 'pr_auc', 'confusion_matrix'],
        save_models=True,
        verbose=True
    )
    
    # Track hyperparameters
    experiment.set_hyperparameters(**hyperparams)
    
    # Run experiment
    results = experiment.run(
        X, y,
        feature_names=metadata.get('feature_names'),
        class_names=metadata.get('class_names'),
        calculate_curves=True  # Generate ROC and PR curves
    )
    
    # Get summary statistics
    summary = experiment.get_summary()
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(summary.to_string())
    
    return results


def run_pac_classification_custom_reporter(
    X: np.ndarray,
    y: np.ndarray,
    metadata: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run PAC classification with manual control using SingleClassificationReporter.
    
    This provides maximum flexibility for custom workflows.
    """
    print("\n" + "="*70)
    print("PAC CLASSIFICATION - Custom Reporter Mode")
    print("="*70)
    
    # Initialize reporter with comprehensive metrics
    reporter = SingleClassificationReporter(
        name="pac_custom_analysis",
        output_dir=output_dir,
        required_metrics=['balanced_accuracy', 'mcc', 'confusion_matrix', 'classification_report', 'roc_auc', 'pr_auc']
    )
    
    # Add experiment metadata using the new path-based API
    experiment_metadata = {
        'experiment': 'PAC Classification',
        'dataset': metadata,
        'preprocessing': {
            'scaling': 'StandardScaler',
            'feature_selection': None
        },
        'model_type': 'SVM',
        'cross_validation': {
            'n_folds': 3,
            'strategy': 'StratifiedKFold',
            'shuffle': True,
            'random_state': 42
        }
    }
    
    # Save metadata using storage system
    reporter.storage.save(experiment_metadata, "experiment/metadata.json")
    
    # Manual cross-validation
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    
    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
        print(f"\n--- Fold {fold_idx + 1} ---")
        
        # Start fold
        reporter.start_fold(fold_idx)
        
        # Split data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = SVC(probability=True, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)
        
        # Calculate comprehensive metrics using new reporter
        ba = reporter.calc_balanced_accuracy(y_test, y_pred)
        mcc = reporter.calc_mcc(y_test, y_pred)
        
        # Enable plotting for confusion matrix (now works correctly!)
        cm = reporter.calc_confusion_matrix(
            y_test, y_pred,
            labels=metadata.get('class_names'),
            plot=True,  # Enable plotting with the fixed visualization
            save=True
        )
        
        # Calculate additional metrics
        cr = reporter.calc_classification_report(y_test, y_pred, labels=metadata.get('class_names'))
        roc_auc = reporter.calc_roc_auc(y_test, y_proba)
        pr_auc = reporter.calc_pr_auc(y_test, y_proba)
        
        # Add custom PAC-specific analysis
        pac_analysis = {
            'fold': fold_idx,
            'coupling_strength_mean': np.random.rand(),  # Replace with actual PAC metric
            'coupling_strength_std': np.random.rand() * 0.1,
            'peak_frequency': np.random.rand() * 100,  # Hz
            'n_samples_train': len(X_train),
            'n_samples_test': len(X_test),
            'class_distribution_train': np.bincount(y_train).tolist(),
            'class_distribution_test': np.bincount(y_test).tolist()
        }
        
        # Use the new storage system for custom metrics
        reporter.storage.save(pac_analysis, f"analysis/pac_metrics_fold_{fold_idx:02d}.json")
        
        # Save preprocessor parameters
        scaler_info = {
            'scaler_params': scaler.get_params(),
            'feature_means': scaler.mean_.tolist() if hasattr(scaler, 'mean_') else None,
            'feature_scales': scaler.scale_.tolist() if hasattr(scaler, 'scale_') else None
        }
        reporter.storage.save(scaler_info, f"models/scaler_fold_{fold_idx:02d}.json")
        
        print(f"  BA: {ba:.3f}, MCC: {mcc:.3f}, ROC-AUC: {roc_auc:.3f}, PR-AUC: {pr_auc:.3f}")
        
        # End fold
        reporter.end_fold(fold_idx)
    
    # Generate final reports
    paths = reporter.save()
    
    return {'paths': paths, 'reporter': reporter}


def compare_models(
    X: np.ndarray,
    y: np.ndarray,
    metadata: Dict[str, Any]
) -> pd.DataFrame:
    """
    Compare multiple models for PAC classification.
    """
    print("\n" + "="*70)
    print("MODEL COMPARISON FOR PAC CLASSIFICATION")
    print("="*70)
    
    models = ['svm', 'rf', 'lr']
    results = {}
    
    for model_name in models:
        print(f"\n--- Testing {model_name.upper()} ---")
        
        # Run simple experiment for each model
        model_results = run_pac_classification_simple(
            X, y, metadata,
            model_name=model_name
        )
        
        # Extract key metrics from the report
        # In practice, you would parse the actual results
        results[model_name] = {
            'report_path': model_results['paths']['final_report'],
            'output_dir': model_results['paths']['base']
        }
    
    # Create comparison table
    comparison_df = pd.DataFrame(results).T
    
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(comparison_df.to_string())
    
    return comparison_df


def main():
    """Main function for PAC classification."""
    
    parser = argparse.ArgumentParser(description="PAC Classification with SciTeX")
    parser.add_argument(
        '--mode',
        choices=['simple', 'advanced', 'custom', 'compare'],
        default='simple',
        help='Classification mode'
    )
    parser.add_argument(
        '--model',
        choices=['svm', 'rf', 'lr'],
        default='svm',
        help='Model to use'
    )
    parser.add_argument(
        '--data-path',
        type=Path,
        help='Path to PAC data file'
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
    
    # Load data
    X, y, metadata = load_pac_data(args.data_path)
    
    # Preprocess if requested
    if args.preprocess:
        print("\nApplying preprocessing...")
        X, preprocessing_info = preprocess_features(
            X,
            apply_scaling=True,
            apply_pca=True,
            n_components=50
        )
        metadata['preprocessing'] = preprocessing_info
    
    # Run classification based on mode
    if args.mode == 'simple':
        results = run_pac_classification_simple(
            X, y, metadata,
            model_name=args.model,
            output_dir=args.output_dir
        )
    elif args.mode == 'advanced':
        results = run_pac_classification_advanced(
            X, y, metadata,
            model_name=args.model,
            output_dir=args.output_dir
        )
    elif args.mode == 'custom':
        results = run_pac_classification_custom_reporter(
            X, y, metadata,
            output_dir=args.output_dir
        )
    elif args.mode == 'compare':
        comparison = compare_models(X, y, metadata)
    
    print("\n" + "="*70)
    print("🎉 PAC Classification Complete!")
    print("Check ./results/ for detailed reports")
    print("="*70)


if __name__ == "__main__":
    main()