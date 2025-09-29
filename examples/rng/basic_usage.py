#!/usr/bin/env python3
"""
Basic usage example for SciTeX RNG module.

Demonstrates the core functionality of RandomStateManager.
"""

import scitex as stx
import numpy as np


def main():
    """Demonstrate basic RNG usage."""
    
    # Create RandomStateManager instance
    print("Creating RandomStateManager with seed=42")
    rng = stx.rng.RandomStateManager(seed=42)
    
    # Get independent named generators
    print("\nGetting independent generators...")
    data_gen = rng("data")
    model_gen = rng("model")
    augment_gen = rng("augmentation")
    
    # Generate reproducible random values
    print("\nGenerating random values:")
    
    # Data sampling
    train_indices = data_gen.integers(0, 1000, size=10)
    print(f"Train indices: {train_indices}")
    
    # Model initialization
    weights = model_gen.normal(0, 0.02, size=(5, 3))
    print(f"Model weights shape: {weights.shape}")
    print(f"Weights mean: {weights.mean():.4f}, std: {weights.std():.4f}")
    
    # Data augmentation
    noise = augment_gen.normal(0, 0.1, size=10)
    print(f"Augmentation noise: {noise[:5]}...")
    
    # Verify reproducibility
    print("\n--- Reproducibility Verification ---")
    
    # First run caches the hash
    result1 = rng.verify(train_indices, "train_indices_example")
    print(f"First verification (caches): {result1}")
    
    # Second run with same data passes
    result2 = rng.verify(train_indices, "train_indices_example")
    print(f"Second verification (matches): {result2}")
    
    # Different data would fail
    different_data = np.array([1, 2, 3])
    result3 = rng.verify(different_data, "train_indices_example")
    print(f"Different data verification: {result3}")
    
    # Show that generators are independent
    print("\n--- Generator Independence ---")
    
    # Generate from model (doesn't affect data generator)
    _ = model_gen.random(1000)
    
    # Data generator continues from where it left off
    more_indices = data_gen.integers(0, 1000, size=5)
    print(f"More indices (unaffected by model gen): {more_indices}")
    
    # Using same name returns same generator
    data_gen_again = rng("data")
    assert data_gen is data_gen_again
    print("Same name returns same generator instance: ✓")
    
    print("\n--- Global Instance ---")
    
    # Get global instance
    global_rng = stx.rng.get()
    print(f"Global RNG seed: {global_rng.seed}")
    
    # Reset with new seed
    new_rng = stx.rng.reset(seed=123)
    print(f"Reset RNG seed: {new_rng.seed}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()