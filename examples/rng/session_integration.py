#!/usr/bin/env python3
"""
Session integration example for SciTeX RNG.

Shows how RNG integrates with scitex.session.start().
"""

import sys
import scitex as stx
import numpy as np


def data_pipeline(rng):
    """Example data processing pipeline."""
    
    # Different generators for different purposes
    load_gen = rng("data_loading")
    augment_gen = rng("augmentation")
    split_gen = rng("splitting")
    
    # Simulate data loading with random sampling
    n_total = 1000
    n_sample = 100
    indices = load_gen.integers(0, n_total, size=n_sample)
    print(f"Loaded samples: {indices[:5]}... (showing first 5 of {n_sample})")
    
    # Simulate augmentation
    noise_level = augment_gen.uniform(0.01, 0.1)
    print(f"Augmentation noise level: {noise_level:.4f}")
    
    # Simulate train/val split
    split_point = split_gen.uniform(0.7, 0.9)
    print(f"Train/val split: {split_point:.1%} / {1-split_point:.1%}")
    
    return indices, noise_level, split_point


def model_initialization(rng, architecture="small"):
    """Initialize model with reproducible weights."""
    
    init_gen = rng("model_init")
    
    if architecture == "small":
        layers = [
            init_gen.normal(0, 0.02, size=(784, 128)),
            init_gen.normal(0, 0.02, size=(128, 64)),
            init_gen.normal(0, 0.02, size=(64, 10))
        ]
    else:
        layers = [
            init_gen.normal(0, 0.02, size=(784, 256)),
            init_gen.normal(0, 0.02, size=(256, 128)),
            init_gen.normal(0, 0.02, size=(128, 64)),
            init_gen.normal(0, 0.02, size=(64, 10))
        ]
    
    total_params = sum(w.size for w in layers)
    print(f"Model initialized with {len(layers)} layers, {total_params:,} parameters")
    
    return layers


def training_loop(rng, n_epochs=3):
    """Simulate training with various random components."""
    
    dropout_gen = rng("dropout")
    shuffle_gen = rng("batch_shuffle")
    lr_gen = rng("learning_rate_schedule")
    
    for epoch in range(n_epochs):
        # Random learning rate scheduling
        lr_noise = lr_gen.uniform(0.9, 1.1)
        lr = 0.001 * lr_noise
        
        # Random batch ordering
        batch_order = np.arange(10)
        shuffle_gen.shuffle(batch_order)
        
        # Random dropout
        dropout_rate = dropout_gen.uniform(0.1, 0.3)
        
        print(f"Epoch {epoch+1}: lr={lr:.5f}, dropout={dropout_rate:.2f}, "
              f"first_batch={batch_order[0]}")


def main():
    """Main example showing session integration."""
    
    print("SciTeX RNG + Session Integration Example")
    print("=" * 60)
    
    # Start session with seed - returns 6 values including RNG
    CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(
        sys=sys,
        seed=2024,
        ID="rng_example",
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Session started successfully!")
    print(f"RNG type: {type(rng)}")
    print(f"RNG seed: {rng.seed}")
    print("=" * 60)
    
    # Verify RNG is properly initialized
    print("\n1. Testing RNG initialization:")
    test_gen = rng("test")
    test_values = test_gen.random(5)
    print(f"   Random values: {test_values}")
    
    # Verify all modules are fixed
    print("\n2. Verifying module fixing:")
    
    # Python random
    import random
    py_val = random.random()
    print(f"   Python random: {py_val:.6f}")
    
    # NumPy
    np_val = np.random.rand()
    print(f"   NumPy random: {np_val:.6f}")
    
    # Check if PyTorch is available
    try:
        import torch
        torch_val = torch.rand(1).item()
        print(f"   PyTorch random: {torch_val:.6f}")
    except ImportError:
        print("   PyTorch not installed")
    
    # Run workflow components
    print("\n3. Running workflow with RNG:")
    print("\n   Data Pipeline:")
    indices, noise, split = data_pipeline(rng)
    
    print("\n   Model Initialization:")
    model = model_initialization(rng, "small")
    
    print("\n   Training Simulation:")
    training_loop(rng, n_epochs=3)
    
    # Demonstrate verification
    print("\n4. Verification system:")
    
    # First call caches
    data = rng("verification_demo").random(100)
    verified = rng.verify(data, "demo_data")
    print(f"   First verification (caches): {verified}")
    
    # Second call verifies
    verified2 = rng.verify(data, "demo_data")
    print(f"   Second verification (matches): {verified2}")
    
    # Demonstrate checkpoint
    print("\n5. Checkpoint system:")
    checkpoint = rng.checkpoint("session_checkpoint")
    print(f"   Checkpoint saved: {checkpoint.name}")
    
    # Generate some values
    before = rng("checkpoint_test").random(3)
    print(f"   Values before: {before}")
    
    # Generate more values
    _ = rng("checkpoint_test").random(100)
    
    # Restore
    rng.restore(checkpoint)
    after = rng("checkpoint_test").random(3)
    print(f"   Values after restore: {after}")
    print(f"   Matches: {np.array_equal(before, after)}")
    
    # Close session
    print("\n6. Closing session...")
    stx.session.close(CONFIG, verbose=True)
    
    print("\n" + "=" * 60)
    print("✓ Session integration example completed successfully!")
    print("=" * 60)


def test_reproducibility():
    """Test that multiple runs give same results."""
    
    print("\n\nREPRODUCIBILITY TEST")
    print("=" * 60)
    
    results = []
    
    for run in range(2):
        print(f"\nRun {run + 1}:")
        
        # Start fresh session
        CONFIG, _, _, _, _, rng = stx.session.start(
            sys=sys,
            seed=999,
            ID=f"repro_test_{run}",
            verbose=False
        )
        
        # Generate values
        gen = rng("reproducibility")
        values = gen.random(5)
        results.append(values)
        print(f"   Generated: {values}")
        
        # Close session
        stx.session.close(CONFIG, verbose=False)
    
    # Check reproducibility
    matches = np.array_equal(results[0], results[1])
    print(f"\n   Results match: {'✓' if matches else '✗'}")
    
    if matches:
        print("\n✓ Reproducibility verified across sessions!")
    else:
        print("\n✗ Reproducibility broken - please check seed fixing!")


if __name__ == "__main__":
    main()
    test_reproducibility()