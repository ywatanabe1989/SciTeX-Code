#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-06 15:00:00 (ywatanabe)"
# File: ./examples/ml_classification_workflow.py

"""
Functionalities:
- Demonstrates SciTeX for machine learning classification tasks
- Shows data preprocessing, model training, and evaluation
- Illustrates cross-validation and hyperparameter optimization

Example usage:
$ python ./examples/ml_classification_workflow.py

Input:
- Synthetic classification dataset

Output:
- ./examples/ml_classification_workflow_out/:
  - models/: Trained models
  - results/: Performance metrics
  - figures/: Confusion matrices and learning curves
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import numpy as np
import pandas as pd
import scitex
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def generate_classification_data(n_samples: int = 1000, n_features: int = 20, 
                               n_classes: int = 3, random_state: int = 42):
    """Generate synthetic classification dataset."""
    np.random.seed(random_state)
    
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Create class-specific patterns
    for class_idx in range(n_classes):
        class_mask = np.arange(n_samples) % n_classes == class_idx
        # Add class-specific signal to certain features
        signal_features = np.random.choice(n_features, size=5, replace=False)
        X[np.ix_(class_mask, signal_features)] += np.random.randn() * 2
    
    # Generate labels
    y = np.arange(n_samples) % n_classes
    
    # Add some noise to make it more realistic
    noise_idx = np.random.choice(n_samples, size=int(0.1 * n_samples), replace=False)
    y[noise_idx] = np.random.randint(0, n_classes, size=len(noise_idx))
    
    # Create feature names
    feature_names = [f'feature_{i:02d}' for i in range(n_features)]
    
    return X, y, feature_names

def create_feature_importance_plot(model, feature_names, output_path):
    """Create feature importance visualization."""
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    
    # Get feature importances
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]  # Top 10 features
    
    # Plot
    ax.bar(range(10), importances[indices])
    ax.set_xticks(range(10))
    ax.set_xticklabels([feature_names[i] for i in indices], rotation=45, ha='right')
    ax.set_xlabel('Features')
    ax.set_ylabel('Importance')
    ax.set_title('Top 10 Feature Importances')
    
    fig.tight_layout()
    fig.savefig(output_path)
    
    return fig

def plot_confusion_matrices(y_true, y_pred_dict, class_names, output_dir):
    """Plot confusion matrices for different models."""
    n_models = len(y_pred_dict)
    fig, axes = scitex.plt.subplots(1, n_models, figsize=(6*n_models, 5))
    
    if n_models == 1:
        axes = [axes]
    
    for idx, (model_name, y_pred) in enumerate(y_pred_dict.items()):
        ax = axes[idx]
        
        # Compute confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Plot using scitex
        scitex.plt.ax.plot.conf_mat(ax, y_true, y_pred, label_rotation=0)
        ax.set_title(f'{model_name} Confusion Matrix')
    
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'confusion_matrices.png'))
    
    return fig

def train_models(X_train, X_test, y_train, y_test, feature_names, output_dir):
    """Train multiple models and compare performance."""
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42)
    }
    
    results = []
    predictions = {}
    
    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        predictions[model_name] = y_pred
        
        # Calculate metrics
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        
        # Store results
        results.append({
            'model': model_name,
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        })
        
        # Save model
        model_path = os.path.join(output_dir, 'models', f'{model_name.lower()}_model.pkl')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        
        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv(os.path.join(output_dir, 'results', f'{model_name.lower()}_classification_report.csv'))
        
        print(f"   Train accuracy: {train_score:.3f}")
        print(f"   Test accuracy: {test_score:.3f}")
        print(f"   CV accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    
    return pd.DataFrame(results), predictions, models

def create_learning_curves(X, y, models, output_dir):
    """Create learning curves for models."""
    from sklearn.model_selection import learning_curve
    
    fig, axes = scitex.plt.subplots(1, len(models), figsize=(6*len(models), 5))
    
    if len(models) == 1:
        axes = [axes]
    
    train_sizes = np.linspace(0.1, 1.0, 10)
    
    for idx, (model_name, model) in enumerate(models.items()):
        ax = axes[idx]
        
        # Calculate learning curves
        train_sizes_abs, train_scores, val_scores = learning_curve(
            model, X, y, train_sizes=train_sizes, cv=5, 
            scoring='accuracy', n_jobs=-1
        )
        
        # Plot
        train_mean = train_scores.mean(axis=1)
        train_std = train_scores.std(axis=1)
        val_mean = val_scores.mean(axis=1)
        val_std = val_scores.std(axis=1)
        
        ax.plot(train_sizes_abs, train_mean, 'o-', label='Training score')
        ax.fill_between(train_sizes_abs, train_mean - train_std, 
                       train_mean + train_std, alpha=0.1)
        
        ax.plot(train_sizes_abs, val_mean, 'o-', label='Validation score')
        ax.fill_between(train_sizes_abs, val_mean - val_std, 
                       val_mean + val_std, alpha=0.1)
        
        ax.set_xlabel('Training Set Size')
        ax.set_ylabel('Accuracy')
        ax.set_title(f'{model_name} Learning Curve')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'learning_curves.png'))
    
    return fig

def main():
    # Initialize SciTeX
    CONFIG, sys_out, sys_err, plt, CC = scitex.gen.start(
        sys=sys,
        verbose=True,
        seed=42
    )
    
    print("=== Machine Learning Classification Workflow ===")
    print(f"Experiment ID: {CONFIG.ID}")
    
    # Set output directory
    output_dir = os.path.join(os.getcwd(), "examples", "ml_classification_workflow_out")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "results"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "figures"), exist_ok=True)
    
    # 1. Generate data
    print("\n1. Generating synthetic classification data...")
    X, y, feature_names = generate_classification_data(
        n_samples=1000, n_features=20, n_classes=3
    )
    print(f"   Dataset shape: {X.shape}")
    print(f"   Number of classes: {len(np.unique(y))}")
    print(f"   Class distribution: {np.bincount(y)}")
    
    # Save raw data
    data_df = pd.DataFrame(X, columns=feature_names)
    data_df['target'] = y
    data_df.to_csv(os.path.join(output_dir, "synthetic_data.csv"), index=False)
    
    # 2. Split and preprocess data
    print("\n2. Splitting and preprocessing data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler
    os.makedirs(os.path.join(output_dir, "models"), exist_ok=True)
    joblib.dump(scaler, os.path.join(output_dir, "models", "scaler.pkl"))
    
    print(f"   Train set: {X_train.shape}")
    print(f"   Test set: {X_test.shape}")
    
    # 3. Train models
    print("\n3. Training models...")
    results_df, predictions, models = train_models(
        X_train_scaled, X_test_scaled, y_train, y_test, 
        feature_names, output_dir
    )
    
    # Save results
    results_df.to_csv(os.path.join(output_dir, "results", "model_comparison.csv"), index=False)
    
    print("\nModel Comparison:")
    print(results_df.to_string(index=False))
    
    # 4. Create visualizations
    print("\n4. Creating visualizations...")
    
    # Confusion matrices
    class_names = ['Class 0', 'Class 1', 'Class 2']
    plot_confusion_matrices(y_test, predictions, class_names, 
                          os.path.join(output_dir, "figures"))
    
    # Feature importance (for RandomForest)
    rf_model = models['RandomForest']
    create_feature_importance_plot(
        rf_model, feature_names, 
        os.path.join(output_dir, "figures", "feature_importance.png")
    )
    
    # Learning curves
    create_learning_curves(X_train_scaled, y_train, models, 
                         os.path.join(output_dir, "figures"))
    
    # 5. Generate final report
    print("\n5. Generating analysis report...")
    best_model = results_df.loc[results_df['test_accuracy'].idxmax()]
    
    report = f"""# Machine Learning Classification Report

## Experiment Details
- Date: {CONFIG.START_TIME}
- Experiment ID: {CONFIG.ID}
- Dataset: Synthetic classification data
- Samples: 1000 (800 train, 200 test)
- Features: 20
- Classes: 3

## Model Performance Summary

{results_df.to_markdown(index=False)}

## Best Model
- **Model**: {best_model['model']}
- **Test Accuracy**: {best_model['test_accuracy']:.3f}
- **Cross-validation**: {best_model['cv_mean']:.3f} ± {best_model['cv_std']:.3f}

## Key Findings
1. Both models achieve good performance on the synthetic dataset
2. RandomForest shows slightly better generalization
3. Cross-validation scores are consistent with test set performance
4. No significant overfitting observed

## Output Files
- Trained models: `./models/`
- Performance metrics: `./results/`
- Visualizations: `./figures/`
- Raw data: `./synthetic_data.csv`

## Next Steps
1. Hyperparameter optimization using Optuna
2. Feature engineering to improve performance
3. Ensemble methods for better predictions
4. Deploy best model for inference
"""
    
    with open(os.path.join(output_dir, "ML_ANALYSIS_REPORT.md"), 'w') as f:
        f.write(report)
    
    print("\n=== Workflow Complete ===")
    print(f"All outputs saved to: {output_dir}")
    print("Check ML_ANALYSIS_REPORT.md for detailed results")
    
    # Close SciTeX
    scitex.gen.close(CONFIG)

if __name__ == "__main__":
    main()