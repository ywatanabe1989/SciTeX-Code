#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:11:00"
# File: /tests/scitex/ai/optim/conftest_enhanced.py
# ----------------------------------------
"""
Enhanced fixtures for optimizer testing.

This conftest provides comprehensive fixtures for testing optimizers:
- Various neural network architectures
- Training datasets and problems
- Loss landscapes for convergence testing
- Performance monitoring utilities
- Gradient patterns for edge case testing
"""

import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Callable
import time
from collections import defaultdict
from contextlib import contextmanager
import psutil
import os


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def linear_models():
    """Provide various linear models for testing."""
    return {
        'simple': nn.Linear(10, 1),
        'deep': nn.Sequential(
            nn.Linear(10, 50),
            nn.ReLU(),
            nn.Linear(50, 50),
            nn.ReLU(),
            nn.Linear(50, 1)
        ),
        'wide': nn.Sequential(
            nn.Linear(10, 200),
            nn.ReLU(),
            nn.Linear(200, 1)
        ),
        'multi_output': nn.Linear(10, 5),
    }


@pytest.fixture
def conv_models():
    """Provide various convolutional models for testing."""
    class SimpleCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(2),
            )
            self.classifier = nn.Sequential(
                nn.Linear(64 * 8 * 8, 128),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(128, 10)
            )
        
        def forward(self, x):
            x = self.features(x)
            x = x.view(x.size(0), -1)
            x = self.classifier(x)
            return x
    
    class ResBlock(nn.Module):
        def __init__(self, channels):
            super().__init__()
            self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
            self.bn1 = nn.BatchNorm2d(channels)
            self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
            self.bn2 = nn.BatchNorm2d(channels)
        
        def forward(self, x):
            residual = x
            x = F.relu(self.bn1(self.conv1(x)))
            x = self.bn2(self.conv2(x))
            x += residual
            return F.relu(x)
    
    class MiniResNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 64, 7, stride=2, padding=3)
            self.bn1 = nn.BatchNorm2d(64)
            self.maxpool = nn.MaxPool2d(3, stride=2, padding=1)
            self.layer1 = ResBlock(64)
            self.layer2 = ResBlock(64)
            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
            self.fc = nn.Linear(64, 10)
        
        def forward(self, x):
            x = self.maxpool(F.relu(self.bn1(self.conv1(x))))
            x = self.layer1(x)
            x = self.layer2(x)
            x = self.avgpool(x)
            x = x.view(x.size(0), -1)
            x = self.fc(x)
            return x
    
    return {
        'simple_cnn': SimpleCNN(),
        'mini_resnet': MiniResNet(),
        'single_conv': nn.Conv2d(3, 10, 3),
    }


@pytest.fixture
def rnn_models():
    """Provide various RNN models for testing."""
    class SimpleLSTM(nn.Module):
        def __init__(self, input_size=10, hidden_size=20, output_size=1):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)
        
        def forward(self, x):
            lstm_out, _ = self.lstm(x)
            # Use last timestep
            out = self.fc(lstm_out[:, -1, :])
            return out
    
    class GRUClassifier(nn.Module):
        def __init__(self, vocab_size=1000, embed_size=100, hidden_size=128, num_classes=5):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embed_size)
            self.gru = nn.GRU(embed_size, hidden_size, batch_first=True, bidirectional=True)
            self.fc = nn.Linear(hidden_size * 2, num_classes)
        
        def forward(self, x):
            x = self.embedding(x)
            gru_out, _ = self.gru(x)
            # Use last timestep
            out = self.fc(gru_out[:, -1, :])
            return out
    
    return {
        'lstm': SimpleLSTM(),
        'gru': GRUClassifier(),
        'simple_rnn': nn.RNN(10, 20, batch_first=True),
    }


# ============================================================================
# Dataset Fixtures
# ============================================================================

@pytest.fixture
def regression_datasets():
    """Provide various regression datasets."""
    np.random.seed(42)
    
    # Linear regression
    X_linear = np.random.randn(1000, 10)
    w_true = np.random.randn(10, 1)
    y_linear = X_linear @ w_true + np.random.randn(1000, 1) * 0.1
    
    # Non-linear regression
    X_nonlinear = np.random.randn(1000, 10)
    y_nonlinear = np.sin(X_nonlinear[:, 0]) + np.cos(X_nonlinear[:, 1]) + np.random.randn(1000) * 0.1
    
    # High noise regression
    X_noisy = np.random.randn(1000, 10)
    y_noisy = X_noisy[:, 0] + np.random.randn(1000) * 2.0
    
    return {
        'linear': (torch.FloatTensor(X_linear), torch.FloatTensor(y_linear)),
        'nonlinear': (torch.FloatTensor(X_nonlinear), torch.FloatTensor(y_nonlinear.reshape(-1, 1))),
        'noisy': (torch.FloatTensor(X_noisy), torch.FloatTensor(y_noisy.reshape(-1, 1))),
    }


@pytest.fixture
def classification_datasets():
    """Provide various classification datasets."""
    np.random.seed(42)
    
    # Binary classification (linearly separable)
    X_binary = np.random.randn(1000, 10)
    w = np.random.randn(10)
    y_binary = (X_binary @ w > 0).astype(np.long)
    
    # Multi-class classification
    X_multi = np.random.randn(1000, 10)
    y_multi = np.random.randint(0, 5, 1000)
    
    # Imbalanced classification
    X_imbalanced = np.random.randn(1000, 10)
    y_imbalanced = np.random.choice([0, 1], 1000, p=[0.9, 0.1])
    
    return {
        'binary': (torch.FloatTensor(X_binary), torch.LongTensor(y_binary)),
        'multiclass': (torch.FloatTensor(X_multi), torch.LongTensor(y_multi)),
        'imbalanced': (torch.FloatTensor(X_imbalanced), torch.LongTensor(y_imbalanced)),
    }


@pytest.fixture
def image_datasets():
    """Provide synthetic image datasets."""
    # CIFAR-like dataset
    cifar_like = torch.randn(100, 3, 32, 32)
    cifar_labels = torch.randint(0, 10, (100,))
    
    # MNIST-like dataset
    mnist_like = torch.randn(100, 1, 28, 28)
    mnist_labels = torch.randint(0, 10, (100,))
    
    # High-res images
    highres = torch.randn(20, 3, 224, 224)
    highres_labels = torch.randint(0, 100, (20,))
    
    return {
        'cifar_like': (cifar_like, cifar_labels),
        'mnist_like': (mnist_like, mnist_labels),
        'highres': (highres, highres_labels),
    }


# ============================================================================
# Optimizer Configuration Fixtures
# ============================================================================

@pytest.fixture
def optimizer_hyperparams():
    """Provide various optimizer hyperparameter configurations."""
    return {
        'conservative': {'lr': 1e-4, 'weight_decay': 1e-4},
        'aggressive': {'lr': 1e-1, 'weight_decay': 0},
        'standard': {'lr': 1e-3, 'weight_decay': 1e-5},
        'fine_tuning': {'lr': 1e-5, 'weight_decay': 1e-3},
        'warmup': {'lr': 1e-6},  # Start with very low LR
    }


@pytest.fixture
def learning_rate_schedules():
    """Provide various learning rate schedule functions."""
    def constant_lr(epoch):
        return 1.0
    
    def step_lr(epoch, step_size=30, gamma=0.1):
        return gamma ** (epoch // step_size)
    
    def exponential_lr(epoch, gamma=0.95):
        return gamma ** epoch
    
    def cosine_lr(epoch, T_max=100):
        return 0.5 * (1 + np.cos(np.pi * epoch / T_max))
    
    def warmup_lr(epoch, warmup_epochs=5):
        if epoch < warmup_epochs:
            return (epoch + 1) / warmup_epochs
        return 1.0
    
    return {
        'constant': constant_lr,
        'step': step_lr,
        'exponential': exponential_lr,
        'cosine': cosine_lr,
        'warmup': warmup_lr,
    }


# ============================================================================
# Gradient Pattern Fixtures
# ============================================================================

@pytest.fixture
def gradient_patterns():
    """Provide various gradient patterns for testing."""
    def generate_gradient_pattern(shape, pattern_type):
        if pattern_type == 'zero':
            return torch.zeros(shape)
        elif pattern_type == 'constant':
            return torch.ones(shape) * 0.1
        elif pattern_type == 'random':
            return torch.randn(shape)
        elif pattern_type == 'sparse':
            grad = torch.zeros(shape)
            mask = torch.rand(shape) < 0.1
            grad[mask] = torch.randn(mask.sum())
            return grad
        elif pattern_type == 'large':
            return torch.randn(shape) * 100
        elif pattern_type == 'small':
            return torch.randn(shape) * 1e-8
        elif pattern_type == 'nan':
            grad = torch.randn(shape)
            grad[0] = float('nan')
            return grad
        elif pattern_type == 'inf':
            grad = torch.randn(shape)
            grad[0] = float('inf')
            return grad
        elif pattern_type == 'oscillating':
            return torch.randn(shape) * (-1) ** torch.arange(shape[0]).reshape(-1, 1)
    
    return generate_gradient_pattern


@pytest.fixture
def gradient_noise_functions():
    """Provide functions to add noise to gradients."""
    def add_gaussian_noise(grad, std=0.01):
        return grad + torch.randn_like(grad) * std
    
    def add_uniform_noise(grad, scale=0.01):
        return grad + (torch.rand_like(grad) - 0.5) * 2 * scale
    
    def add_sparse_noise(grad, prob=0.1, scale=1.0):
        mask = torch.rand_like(grad) < prob
        noise = torch.randn_like(grad) * scale
        return grad + noise * mask
    
    def add_structured_noise(grad, pattern='stripes'):
        noise = torch.zeros_like(grad)
        if pattern == 'stripes':
            noise[::2] = torch.randn(grad.shape[0] // 2 + grad.shape[0] % 2, *grad.shape[1:])
        elif pattern == 'checkerboard':
            for i in range(0, grad.shape[0], 2):
                for j in range(0, grad.shape[1] if len(grad.shape) > 1 else 1, 2):
                    if len(grad.shape) == 1:
                        noise[i] = torch.randn(1)
                    else:
                        noise[i, j] = torch.randn(1)
        return grad + noise * 0.1
    
    return {
        'gaussian': add_gaussian_noise,
        'uniform': add_uniform_noise,
        'sparse': add_sparse_noise,
        'structured': add_structured_noise,
    }


# ============================================================================
# Performance Monitoring Fixtures
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Provide a performance monitoring context manager."""
    @contextmanager
    def monitor():
        metrics = {
            'time': 0,
            'memory': 0,
            'cpu_percent': 0,
            'gpu_memory': 0,
        }
        
        # Start monitoring
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            start_gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
        
        yield metrics
        
        # End monitoring
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        metrics['time'] = end_time - start_time
        metrics['memory'] = end_memory - start_memory
        metrics['cpu_percent'] = process.cpu_percent()
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            end_gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
            metrics['gpu_memory'] = end_gpu_memory - start_gpu_memory
    
    return monitor


@pytest.fixture
def convergence_tracker():
    """Provide a convergence tracking utility."""
    class ConvergenceTracker:
        def __init__(self):
            self.losses = []
            self.gradients = []
            self.parameters = []
            self.learning_rates = []
            self.timestamps = []
        
        def update(self, loss, model, optimizer):
            self.losses.append(loss)
            self.timestamps.append(time.time())
            
            # Track gradient norms
            grad_norm = 0
            param_norm = 0
            for p in model.parameters():
                if p.grad is not None:
                    grad_norm += p.grad.norm().item() ** 2
                param_norm += p.norm().item() ** 2
            
            self.gradients.append(grad_norm ** 0.5)
            self.parameters.append(param_norm ** 0.5)
            
            # Track learning rates
            lrs = [group['lr'] for group in optimizer.param_groups]
            self.learning_rates.append(lrs)
        
        def is_converged(self, patience=10, min_delta=1e-4):
            if len(self.losses) < patience:
                return False
            
            recent_losses = self.losses[-patience:]
            return all(
                abs(recent_losses[i] - recent_losses[i-1]) < min_delta 
                for i in range(1, len(recent_losses))
            )
        
        def get_summary(self):
            return {
                'final_loss': self.losses[-1] if self.losses else None,
                'best_loss': min(self.losses) if self.losses else None,
                'total_iterations': len(self.losses),
                'converged': self.is_converged(),
                'final_grad_norm': self.gradients[-1] if self.gradients else None,
                'time_elapsed': self.timestamps[-1] - self.timestamps[0] if len(self.timestamps) > 1 else 0,
            }
    
    return ConvergenceTracker


# ============================================================================
# Loss Landscape Fixtures
# ============================================================================

@pytest.fixture
def loss_landscapes():
    """Provide various loss landscape functions for testing."""
    def convex_loss(params):
        """Simple convex quadratic loss."""
        return torch.sum(params ** 2)
    
    def non_convex_loss(params):
        """Non-convex loss with multiple minima."""
        return torch.sum(torch.sin(params) + 0.1 * params ** 2)
    
    def sharp_loss(params):
        """Loss with sharp minima."""
        return torch.sum(torch.abs(params) ** 0.5)
    
    def noisy_loss(params, noise_level=0.1):
        """Loss with added noise."""
        base_loss = torch.sum(params ** 2)
        noise = torch.randn(1) * noise_level
        return base_loss + noise
    
    def plateau_loss(params):
        """Loss with plateaus."""
        return torch.sum(torch.tanh(params ** 2))
    
    return {
        'convex': convex_loss,
        'non_convex': non_convex_loss,
        'sharp': sharp_loss,
        'noisy': noisy_loss,
        'plateau': plateau_loss,
    }


# ============================================================================
# Training Loop Fixtures
# ============================================================================

@pytest.fixture
def training_loop():
    """Provide a standard training loop for testing optimizers."""
    def train(model, optimizer, data_loader, loss_fn, epochs=10, 
              callback=None, device='cpu'):
        model.to(device)
        history = defaultdict(list)
        
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_idx, (data, target) in enumerate(data_loader):
                data, target = data.to(device), target.to(device)
                
                optimizer.zero_grad()
                output = model(data)
                loss = loss_fn(output, target)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                
                if callback:
                    callback(model, optimizer, loss.item(), epoch, batch_idx)
            
            avg_loss = epoch_loss / len(data_loader)
            history['loss'].append(avg_loss)
            history['epoch'].append(epoch)
        
        return history
    
    return train


@pytest.fixture
def create_data_loader():
    """Factory for creating data loaders."""
    def _create_loader(X, y, batch_size=32, shuffle=True):
        dataset = torch.utils.data.TensorDataset(X, y)
        return torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=shuffle
        )
    
    return _create_loader


# ============================================================================
# Validation Utilities
# ============================================================================

@pytest.fixture
def optimizer_validator():
    """Provide validation utilities for optimizer behavior."""
    class OptimizerValidator:
        @staticmethod
        def check_parameter_update(model, optimizer, loss_fn, data, target):
            """Check if parameters are updated correctly."""
            # Store initial parameters
            initial_params = {
                name: param.clone() 
                for name, param in model.named_parameters()
            }
            
            # Forward and backward pass
            optimizer.zero_grad()
            output = model(data)
            loss = loss_fn(output, target)
            loss.backward()
            
            # Check gradients exist
            for name, param in model.named_parameters():
                if param.requires_grad:
                    assert param.grad is not None, f"No gradient for {name}"
            
            # Optimizer step
            optimizer.step()
            
            # Check parameters were updated
            params_updated = False
            for name, param in model.named_parameters():
                if param.requires_grad:
                    if not torch.equal(param, initial_params[name]):
                        params_updated = True
                        break
            
            return params_updated
        
        @staticmethod
        def check_convergence(losses, threshold=0.01, window=10):
            """Check if training has converged."""
            if len(losses) < window:
                return False
            
            recent = losses[-window:]
            return np.std(recent) < threshold
        
        @staticmethod
        def check_gradient_flow(model):
            """Check for vanishing/exploding gradients."""
            grad_norms = []
            for name, param in model.named_parameters():
                if param.grad is not None:
                    grad_norm = param.grad.norm().item()
                    grad_norms.append(grad_norm)
            
            if not grad_norms:
                return "no_gradients"
            
            max_grad = max(grad_norms)
            min_grad = min(grad_norms)
            
            if max_grad > 100:
                return "exploding"
            elif max_grad < 1e-6:
                return "vanishing"
            else:
                return "normal"
    
    return OptimizerValidator()


if __name__ == "__main__":
    # Test fixtures
    pytest.main([__file__])

# EOF