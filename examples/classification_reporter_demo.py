#!/usr/bin/env python3
"""
Demo script showing how to use the enhanced SingleTaskClassificationReporter.

This example demonstrates:
1. Basic usage with automatic output directory
2. Cross-validation workflow
3. Custom object addition
4. Final report generation
"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.insert(0, '/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src')

# Import the new reporter
from scitex.ai.classification._SingleClassificationReporter_v2 import SingleTaskClassificationReporter


def demo_basic_usage():
    """Demonstrate basic usage of the classification reporter."""
    
    print("\n" + "="*70)
    print("DEMO: Basic Classification Reporter Usage")
    print("="*70)
    
    # Generate synthetic data
    X, y = make_classification(
        n_samples=300,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=3,
        random_state=42
    )
    
    # Initialize reporter (auto-creates timestamped output directory)
    reporter = SingleTaskClassificationReporter(
        name="demo_experiment",
        # output_dir is optional - will create ./results/demo_experiment_TIMESTAMP/
    )
    
    # Show where results will be saved
    paths = reporter.get_output_paths()
    print(f"\nResults will be saved to: {paths['base']}")
    
    # Perform 5-fold cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n--- Processing Fold {fold_idx} ---")
        
        # Split data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train model
        clf = SVC(probability=True, random_state=42)
        clf.fit(X_train, y_train)
        
        # Get predictions
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)
        
        # Calculate all metrics at once (automatically saves and validates)
        metrics = reporter.calculate_all_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            labels=['Class_0', 'Class_1', 'Class_2'],
            fold_idx=fold_idx,
            save=True,
            plot=True
        )
        
        print(f"  Balanced Accuracy: {metrics['balanced_accuracy']:.3f}")
        print(f"  MCC: {metrics['mcc']:.3f}")
        if 'roc_auc' in metrics:
            print(f"  ROC AUC: {metrics['roc_auc']:.3f}")
    
    # Save everything and generate reports
    final_paths = reporter.save()
    
    print("\n✨ Demo complete! Check the results at:")
    print(f"   {final_paths['final_report']}")
    
    return reporter


def demo_advanced_usage():
    """Demonstrate advanced features with custom additions."""
    
    print("\n" + "="*70)
    print("DEMO: Advanced Classification Reporter Usage")
    print("="*70)
    
    # Generate data
    X, y = make_classification(
        n_samples=500,
        n_features=30,
        n_informative=20,
        n_classes=4,
        random_state=42
    )
    
    # Initialize reporter with custom output directory
    reporter = SingleTaskClassificationReporter(
        name="advanced_demo",
        output_dir="./results/advanced_demo_custom",
        required_metrics=[
            'balanced_accuracy',
            'mcc',
            'confusion_matrix',
            'roc_auc',
            'pr_auc'
        ]
    )
    
    # Track hyperparameters
    hyperparams = {
        'model': 'RandomForestClassifier',
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
    reporter.add(hyperparams, "models/hyperparameters.json")
    
    # Perform cross-validation
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n--- Fold {fold_idx} ---")
        
        # Start fold
        reporter.start_fold(fold_idx)
        
        # Split data
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train model
        clf = RandomForestClassifier(**hyperparams)
        clf.fit(X_train, y_train)
        
        # Get predictions
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)
        
        # Calculate metrics individually (for more control)
        ba = reporter.calc_balanced_accuracy(y_test, y_pred)
        mcc = reporter.calc_mcc(y_test, y_pred)
        cm = reporter.calc_confusion_matrix(y_test, y_pred, plot=True)
        roc = reporter.calc_roc_auc(y_test, y_proba, plot=True)
        pr = reporter.calc_pr_auc(y_test, y_proba, plot=True)
        
        # Add custom analysis
        import pandas as pd
        feature_importance = pd.DataFrame({
            'feature': [f'feature_{i}' for i in range(X.shape[1])],
            'importance': clf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        reporter.add(
            feature_importance,
            f"analysis/feature_importance_fold_{fold_idx:02d}.csv"
        )
        
        # Save model
        import pickle
        model_path = f"models/model_fold_{fold_idx:02d}.pkl"
        reporter.add(clf, model_path)
        
        # End fold
        reporter.end_fold(fold_idx)
        
        print(f"  ✓ Fold {fold_idx} complete")
        print(f"    BA: {ba:.3f}, MCC: {mcc:.3f}, ROC: {roc:.3f}, PR: {pr:.3f}")
    
    # Generate final reports
    final_paths = reporter.save()
    
    print("\n🎉 Advanced demo complete!")
    print(f"   Full results at: {final_paths['base']}")
    
    return reporter


def demo_minimal_usage():
    """Demonstrate minimal usage for quick experiments."""
    
    print("\n" + "="*70)
    print("DEMO: Minimal Classification Reporter Usage")
    print("="*70)
    
    # Quick setup
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    
    # Load data
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Train model
    clf = LogisticRegression(max_iter=200)
    clf.fit(X_train, y_train)
    
    # Initialize reporter
    reporter = SingleTaskClassificationReporter("iris_quick_test")
    
    # Calculate all metrics with one call
    metrics = reporter.calculate_all_metrics(
        y_true=y_test,
        y_pred=clf.predict(X_test),
        y_proba=clf.predict_proba(X_test),
        labels=['setosa', 'versicolor', 'virginica']
    )
    
    # Save and show results
    paths = reporter.save()
    
    print(f"\n✅ Quick test complete! Report at: {paths['final_report']}")
    
    return reporter


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Classification Reporter Demo")
    parser.add_argument(
        '--demo',
        choices=['basic', 'advanced', 'minimal', 'all'],
        default='basic',
        help='Which demo to run'
    )
    
    args = parser.parse_args()
    
    if args.demo == 'basic' or args.demo == 'all':
        demo_basic_usage()
    
    if args.demo == 'advanced' or args.demo == 'all':
        demo_advanced_usage()
    
    if args.demo == 'minimal' or args.demo == 'all':
        demo_minimal_usage()
    
    print("\n" + "="*70)
    print("All demos complete! 🎉")
    print("Check the ./results/ directory for outputs")
    print("="*70)