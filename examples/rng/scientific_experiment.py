#!/usr/bin/env python3
"""
Scientific experiment example with SciTeX RNG.

Shows how to ensure reproducibility in scientific computing workflows.
"""

import scitex as stx
import numpy as np
from pathlib import Path


def generate_synthetic_data(rng, n_samples=100, n_features=10):
    """Generate synthetic dataset with controlled randomness."""
    
    # Get generators for different aspects
    data_gen = rng("synthetic_data")
    noise_gen = rng("measurement_noise")
    
    # Generate base signal
    X = data_gen.normal(0, 1, size=(n_samples, n_features))
    
    # Add realistic noise
    noise = noise_gen.normal(0, 0.1, size=(n_samples, n_features))
    X_noisy = X + noise
    
    # Generate labels with some pattern
    weights = data_gen.normal(0, 0.5, size=n_features)
    y = (X @ weights > 0).astype(int)
    
    return X_noisy, y, weights


def split_data(rng, X, y, train_ratio=0.8):
    """Reproducible train/test split."""
    
    split_gen = rng("data_split")
    n_samples = len(X)
    n_train = int(n_samples * train_ratio)
    
    # Generate reproducible shuffle
    indices = np.arange(n_samples)
    split_gen.shuffle(indices)
    
    train_idx = indices[:n_train]
    test_idx = indices[n_train:]
    
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def run_experiment(seed=42):
    """Run a complete reproducible experiment."""
    
    print(f"Starting experiment with seed={seed}")
    print("=" * 50)
    
    # Initialize RNG - automatically fixes all random modules
    rng = stx.rng.RandomStateManager(seed=seed)
    
    # Step 1: Generate data
    print("\n1. Generating synthetic data...")
    X, y, true_weights = generate_synthetic_data(rng, n_samples=200)
    print(f"   Data shape: {X.shape}")
    print(f"   Labels: {np.unique(y, return_counts=True)}")
    
    # Verify data reproducibility
    data_hash_ok = rng.verify(X, "experiment_data")
    print(f"   Data verification: {'✓' if data_hash_ok else '✗'}")
    
    # Step 2: Split data
    print("\n2. Splitting data...")
    X_train, X_test, y_train, y_test = split_data(rng, X, y)
    print(f"   Train set: {X_train.shape}")
    print(f"   Test set: {X_test.shape}")
    
    # Step 3: Checkpoint before model training
    print("\n3. Creating checkpoint...")
    checkpoint = rng.checkpoint("before_training")
    print(f"   Checkpoint saved: {checkpoint}")
    
    # Step 4: Initialize model with reproducible weights
    print("\n4. Initializing model...")
    model_gen = rng("model_init")
    model_weights = model_gen.normal(0, 0.1, size=X.shape[1])
    print(f"   Initial weights: mean={model_weights.mean():.4f}, std={model_weights.std():.4f}")
    
    # Step 5: Simulate training with dropout
    print("\n5. Simulating training...")
    dropout_gen = rng("dropout")
    
    for epoch in range(3):
        # Reproducible dropout mask
        dropout_mask = dropout_gen.random(X.shape[1]) > 0.2
        active_features = np.sum(dropout_mask)
        print(f"   Epoch {epoch+1}: {active_features}/{X.shape[1]} features active")
    
    # Step 6: Verify final state
    print("\n6. Final verification...")
    
    # Verify model weights are reproducible
    weights_ok = rng.verify(model_weights, "final_weights")
    print(f"   Model weights verification: {'✓' if weights_ok else '✗'}")
    
    # Show we can restore from checkpoint
    print("\n7. Testing checkpoint restore...")
    rng.restore(checkpoint)
    
    # After restore, regenerate same values
    test_gen = rng("model_init")
    restored_weights = test_gen.normal(0, 0.1, size=X.shape[1])
    
    weights_match = np.allclose(model_weights, restored_weights)
    print(f"   Weights match after restore: {'✓' if weights_match else '✗'}")
    
    return X, y, model_weights


def compare_runs():
    """Show that same seed gives identical results."""
    
    print("\n" + "=" * 50)
    print("REPRODUCIBILITY TEST")
    print("=" * 50)
    
    # Run 1
    print("\nRun 1:")
    X1, y1, w1 = run_experiment(seed=2024)
    
    # Run 2 with same seed
    print("\n" + "-" * 50)
    print("\nRun 2 (same seed):")
    X2, y2, w2 = run_experiment(seed=2024)
    
    # Compare results
    print("\n" + "=" * 50)
    print("COMPARISON:")
    print(f"Data identical: {np.array_equal(X1, X2)}")
    print(f"Labels identical: {np.array_equal(y1, y2)}")
    print(f"Weights identical: {np.array_equal(w1, w2)}")
    
    # Run 3 with different seed
    print("\n" + "-" * 50)
    print("\nRun 3 (different seed):")
    X3, y3, w3 = run_experiment(seed=9999)
    
    print("\n" + "=" * 50)
    print("COMPARISON WITH DIFFERENT SEED:")
    print(f"Data different: {not np.array_equal(X1, X3)}")
    print(f"Labels different: {not np.array_equal(y1, y3)}")
    print(f"Weights different: {not np.array_equal(w1, w3)}")


if __name__ == "__main__":
    compare_runs()
    print("\n✓ Scientific experiment example completed!")