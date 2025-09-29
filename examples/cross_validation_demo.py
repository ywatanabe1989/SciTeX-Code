#!/usr/bin/env python3
"""
Demo of the CrossValidationExperiment helper class.

Shows how to run complete ML experiments with just a few lines of code.
"""

import sys
sys.path.insert(0, '/data/gpfs/projects/punim2354/ywatanabe/SciTeX-Code/src')

from sklearn.datasets import load_iris, load_wine, make_classification
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from scitex.ai.classification.cross_validation import (
    CrossValidationExperiment,
    quick_experiment
)


def demo_quick_experiment():
    """Demonstrate the quickest way to run an experiment."""
    
    print("\n" + "="*70)
    print("DEMO: Quick Experiment (One-liner style)")
    print("="*70)
    
    # Load data
    X, y = load_iris(return_X_y=True)
    
    # Run experiment with one line (after imports)
    results = quick_experiment(
        X, y,
        SVC(probability=True),
        name="iris_svm_quick",
        verbose=False  # Quick mode
    )
    
    print(f"\n✅ Quick experiment complete!")
    print(f"   Report: {results['paths']['final_report']}")
    
    return results


def demo_standard_experiment():
    """Demonstrate standard usage with hyperparameter tracking."""
    
    print("\n" + "="*70)
    print("DEMO: Standard Cross-Validation Experiment")
    print("="*70)
    
    # Load wine dataset
    from sklearn.datasets import load_wine
    data = load_wine()
    X, y = data.data, data.target
    
    # Define model with specific hyperparameters
    model_params = {
        'n_estimators': 100,
        'max_depth': 5,
        'min_samples_split': 5,
        'random_state': 42
    }
    
    # Create experiment
    experiment = CrossValidationExperiment(
        name="wine_rf_optimized",
        model_fn=lambda: RandomForestClassifier(**model_params),
        save_models=True,
        verbose=True
    )
    
    # Track hyperparameters
    experiment.set_hyperparameters(**model_params)
    
    # Run experiment with feature and class names
    results = experiment.run(
        X, y,
        feature_names=data.feature_names,
        class_names=data.target_names.tolist()
    )
    
    print(f"\n📊 Experiment Results:")
    print(f"   Total time: {results['timing']['total_time']:.2f}s")
    print(f"   Mean fold time: {results['timing']['mean_fold_time']:.2f}s")
    print(f"   Report: {results['paths']['final_report']}")
    
    return results


def demo_model_comparison():
    """Demonstrate comparing multiple models."""
    
    print("\n" + "="*70)
    print("DEMO: Model Comparison")
    print("="*70)
    
    # Generate synthetic dataset
    X, y = make_classification(
        n_samples=500,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=3,
        random_state=42
    )
    
    # Define models to compare
    models = {
        'SVM': SVC(probability=True, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    # Store results
    comparison_results = {}
    
    # Run experiment for each model
    for model_name, model in models.items():
        print(f"\n--- Testing {model_name} ---")
        
        experiment = CrossValidationExperiment(
            name=f"comparison_{model_name.lower()}",
            model_fn=lambda m=model: m.__class__(**m.get_params()),
            output_dir=f"./results/model_comparison/{model_name.lower()}",
            verbose=False  # Less verbose for comparison
        )
        
        # Track model hyperparameters
        experiment.set_hyperparameters(**model.get_params())
        
        # Run experiment
        results = experiment.run(X, y, calculate_curves=False)
        
        # Get summary
        summary = experiment.get_summary()
        
        # Extract key metrics
        if not summary.empty:
            mean_row = summary[summary['Fold'] == 'Mean']
            if not mean_row.empty:
                comparison_results[model_name] = {
                    'Balanced Accuracy': mean_row['Balanced Accuracy'].values[0],
                    'Mcc': mean_row['Mcc'].values[0],
                    'Report': results['paths']['final_report']
                }
                
                print(f"  BA: {comparison_results[model_name]['Balanced Accuracy']}")
                print(f"  MCC: {comparison_results[model_name]['Mcc']}")
    
    # Print comparison summary
    print("\n" + "="*60)
    print("MODEL COMPARISON SUMMARY")
    print("="*60)
    
    import pandas as pd
    comparison_df = pd.DataFrame(comparison_results).T
    print(comparison_df.to_string())
    
    # Find best model
    best_model = comparison_df['Balanced Accuracy'].idxmax()
    print(f"\n🏆 Best Model: {best_model}")
    print(f"   BA: {comparison_df.loc[best_model, 'Balanced Accuracy']}")
    print(f"   Report: {comparison_df.loc[best_model, 'Report']}")
    
    return comparison_results


def demo_custom_cv_strategy():
    """Demonstrate using custom cross-validation strategies."""
    
    print("\n" + "="*70)
    print("DEMO: Custom Cross-Validation Strategy")
    print("="*70)
    
    from sklearn.model_selection import RepeatedStratifiedKFold, LeaveOneOut, TimeSeriesSplit
    
    # Generate data
    X, y = make_classification(
        n_samples=200,
        n_features=10,
        n_classes=2,
        random_state=42
    )
    
    # Use repeated stratified k-fold for more robust estimates
    cv_strategy = RepeatedStratifiedKFold(
        n_splits=3,
        n_repeats=2,
        random_state=42
    )
    
    # Create experiment with custom CV
    experiment = CrossValidationExperiment(
        name="custom_cv_demo",
        model_fn=lambda: LogisticRegression(max_iter=500),
        cv=cv_strategy,
        verbose=True
    )
    
    # Run experiment
    results = experiment.run(X, y)
    
    print(f"\n✅ Custom CV experiment complete!")
    print(f"   Used {cv_strategy.get_n_splits()} total splits")
    print(f"   Report: {results['paths']['final_report']}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-Validation Demo")
    parser.add_argument(
        '--demo',
        choices=['quick', 'standard', 'comparison', 'custom', 'all'],
        default='quick',
        help='Which demo to run'
    )
    
    args = parser.parse_args()
    
    demos = {
        'quick': demo_quick_experiment,
        'standard': demo_standard_experiment,
        'comparison': demo_model_comparison,
        'custom': demo_custom_cv_strategy
    }
    
    if args.demo == 'all':
        for demo_fn in demos.values():
            demo_fn()
    else:
        demos[args.demo]()
    
    print("\n" + "="*70)
    print("🎉 All demos complete!")
    print("Check ./results/ for detailed reports")
    print("="*70)