#!/usr/bin/env python3
"""
Machine learning example with SciTeX RNG.

Demonstrates reproducible ML workflows with checkpointing.
"""

import scitex as stx
import numpy as np


class SimpleNN:
    """Simple neural network with reproducible initialization."""
    
    def __init__(self, rng, input_size, hidden_size, output_size):
        """Initialize with reproducible weights."""
        self.rng = rng
        
        # Get dedicated generator for weight initialization
        init_gen = rng("weight_init")
        
        # Xavier/Glorot initialization
        scale1 = np.sqrt(2.0 / input_size)
        self.W1 = init_gen.normal(0, scale1, size=(input_size, hidden_size))
        self.b1 = np.zeros(hidden_size)
        
        scale2 = np.sqrt(2.0 / hidden_size)
        self.W2 = init_gen.normal(0, scale2, size=(hidden_size, output_size))
        self.b2 = np.zeros(output_size)
        
        print(f"Model initialized:")
        print(f"  W1: {self.W1.shape}, mean={self.W1.mean():.4f}, std={self.W1.std():.4f}")
        print(f"  W2: {self.W2.shape}, mean={self.W2.mean():.4f}, std={self.W2.std():.4f}")
    
    def forward(self, X, training=True):
        """Forward pass with optional dropout."""
        # Hidden layer
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1)  # ReLU
        
        if training:
            # Reproducible dropout
            dropout_gen = self.rng("dropout")
            dropout_mask = dropout_gen.random(self.a1.shape) > 0.2
            self.a1 = self.a1 * dropout_mask / 0.8
        
        # Output layer
        self.z2 = self.a1 @ self.W2 + self.b2
        
        # Softmax
        exp_scores = np.exp(self.z2 - np.max(self.z2, axis=1, keepdims=True))
        self.probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
        
        return self.probs
    
    def get_accuracy(self, X, y):
        """Calculate accuracy."""
        probs = self.forward(X, training=False)
        predictions = np.argmax(probs, axis=1)
        return np.mean(predictions == y)


def create_dataset(rng, n_samples=1000, n_features=20, n_classes=3):
    """Create a synthetic classification dataset."""
    
    data_gen = rng("dataset")
    
    # Generate features
    X = data_gen.normal(0, 1, size=(n_samples, n_features))
    
    # Generate separable classes
    centers = data_gen.normal(0, 2, size=(n_classes, n_features))
    
    # Assign samples to classes
    y = np.zeros(n_samples, dtype=int)
    samples_per_class = n_samples // n_classes
    
    for i in range(n_classes):
        start_idx = i * samples_per_class
        end_idx = (i + 1) * samples_per_class if i < n_classes - 1 else n_samples
        
        # Add class-specific pattern
        X[start_idx:end_idx] += centers[i]
        y[start_idx:end_idx] = i
    
    # Shuffle data
    shuffle_gen = rng("shuffle")
    indices = np.arange(n_samples)
    shuffle_gen.shuffle(indices)
    
    return X[indices], y[indices]


def create_batches(rng, X, y, batch_size=32):
    """Create mini-batches for training."""
    
    batch_gen = rng("batch_sampling")
    n_samples = len(X)
    
    # Shuffle indices
    indices = np.arange(n_samples)
    batch_gen.shuffle(indices)
    
    batches = []
    for start_idx in range(0, n_samples, batch_size):
        end_idx = min(start_idx + batch_size, n_samples)
        batch_indices = indices[start_idx:end_idx]
        batches.append((X[batch_indices], y[batch_indices]))
    
    return batches


def train_model(seed=42):
    """Train a model with reproducible randomness."""
    
    print("Machine Learning Training Example")
    print("=" * 50)
    
    # Initialize RNG
    rng = stx.rng.RandomStateManager(seed=seed)
    
    # Create dataset
    print("\n1. Creating dataset...")
    X, y = create_dataset(rng, n_samples=500, n_features=20, n_classes=3)
    print(f"   Dataset shape: {X.shape}")
    print(f"   Classes: {np.unique(y)}")
    
    # Split data
    split_gen = rng("train_test_split")
    n_train = int(0.8 * len(X))
    indices = np.arange(len(X))
    split_gen.shuffle(indices)
    
    train_idx, test_idx = indices[:n_train], indices[n_train:]
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    print(f"   Train: {X_train.shape}, Test: {X_test.shape}")
    
    # Initialize model
    print("\n2. Initializing model...")
    model = SimpleNN(rng, input_size=20, hidden_size=32, output_size=3)
    
    # Verify initial weights
    initial_weights_ok = rng.verify(model.W1, "initial_W1")
    print(f"   Initial weights verified: {'✓' if initial_weights_ok else '✗'}")
    
    # Training loop
    print("\n3. Training...")
    
    for epoch in range(3):
        print(f"\n   Epoch {epoch + 1}:")
        
        # Checkpoint at start of epoch
        checkpoint = rng.checkpoint(f"epoch_{epoch}")
        print(f"   - Checkpoint saved")
        
        # Create mini-batches
        batches = create_batches(rng, X_train, y_train, batch_size=32)
        
        # Simulate training on batches
        for batch_idx, (X_batch, y_batch) in enumerate(batches[:3]):  # Just first 3 batches
            # Forward pass with dropout
            probs = model.forward(X_batch, training=True)
            
            # Calculate loss (cross-entropy)
            correct_probs = probs[np.arange(len(y_batch)), y_batch]
            loss = -np.mean(np.log(correct_probs + 1e-10))
            
            if batch_idx == 0:
                print(f"   - Batch 1 loss: {loss:.4f}")
        
        # Evaluate
        train_acc = model.get_accuracy(X_train, y_train)
        test_acc = model.get_accuracy(X_test, y_test)
        print(f"   - Train acc: {train_acc:.3f}, Test acc: {test_acc:.3f}")
    
    return model, rng, X_test, y_test


def demonstrate_checkpointing():
    """Show how checkpointing enables exact reproduction."""
    
    print("\n" + "=" * 50)
    print("CHECKPOINT DEMONSTRATION")
    print("=" * 50)
    
    # Train model
    model1, rng1, X_test, y_test = train_model(seed=123)
    
    # Save checkpoint after training
    final_checkpoint = rng1.checkpoint("final_model")
    print(f"\nFinal checkpoint saved: {final_checkpoint}")
    
    # Continue training with different randomness
    print("\n4. Additional training (different random path)...")
    extra_gen = rng1("extra_training")
    extra_noise = extra_gen.normal(0, 0.01, size=model1.W1.shape)
    model1.W1 += extra_noise
    
    new_acc = model1.get_accuracy(X_test, y_test)
    print(f"   Accuracy after noise: {new_acc:.3f}")
    
    # Restore from checkpoint
    print("\n5. Restoring from checkpoint...")
    rng2 = stx.rng.RandomStateManager(seed=999)  # Different seed
    rng2.restore(final_checkpoint)
    
    # Recreate model with restored state
    model2 = SimpleNN(rng2, input_size=20, hidden_size=32, output_size=3)
    
    # Weights should be different (different restoration path)
    weights_different = not np.allclose(model1.W1, model2.W1)
    print(f"   Weights different after restore: {'✓' if weights_different else '✗'}")
    
    # But if we apply same "extra training" it should match
    extra_gen2 = rng2("extra_training")
    extra_noise2 = extra_gen2.normal(0, 0.01, size=model2.W1.shape)
    
    noise_matches = np.allclose(extra_noise, extra_noise2)
    print(f"   Same random sequence after restore: {'✓' if noise_matches else '✗'}")


def demonstrate_temporary_seed():
    """Show temporary seed for debugging."""
    
    print("\n" + "=" * 50)
    print("TEMPORARY SEED DEMONSTRATION")
    print("=" * 50)
    
    rng = stx.rng.RandomStateManager(seed=42)
    
    # Normal training randomness
    train_gen = rng("training")
    val1 = train_gen.random()
    print(f"\nNormal training value: {val1:.6f}")
    
    # Temporary seed for debugging
    print("\nEntering debug mode with temporary seed...")
    with rng.temporary_seed(999):
        import random
        debug_val = random.random()
        print(f"Debug value (seed 999): {debug_val:.6f}")
    
    # Back to normal flow
    print("\nBack to normal training...")
    val2 = train_gen.random()
    print(f"Next training value: {val2:.6f}")
    
    # Verify sequence continues correctly
    rng2 = stx.rng.RandomStateManager(seed=42)
    train_gen2 = rng2("training")
    val1_check = train_gen2.random()
    val2_check = train_gen2.random()
    
    sequence_correct = (val1 == val1_check) and (val2 == val2_check)
    print(f"Sequence unaffected by temporary seed: {'✓' if sequence_correct else '✗'}")


if __name__ == "__main__":
    # Basic training
    train_model(seed=42)
    
    # Checkpointing demo
    demonstrate_checkpointing()
    
    # Temporary seed demo
    demonstrate_temporary_seed()
    
    print("\n✓ Machine learning example completed!")