# SciTeX AI Module

The AI module provides machine learning and artificial intelligence utilities for the SciTeX framework.

## Overview

The AI module is organized into several submodules:

### Core Components

- **`genai`** - Generative AI integration with multiple providers (OpenAI, Anthropic, Google, etc.)
- **`training`** - Training utilities (EarlyStopping, LearningCurveLogger)
- **`classification`** - Classification tools (ClassificationReporter, Classifier)

### Neural Network Components

- **`layer`** - Custom neural network layers
- **`loss`** - Loss functions for training
- **`act`** - Activation functions
- **`optim`** - Optimizers and optimization utilities

### Analysis & Visualization

- **`plt`** - AI-specific plotting utilities
- **`metrics`** - Performance metrics
- **`clustering`** - Clustering algorithms (UMAP, PCA)
- **`feature_extraction`** - Feature extraction methods

### Utilities

- **`utils`** - General AI/ML utilities
- **`sampling`** - Data sampling methods
- **`sklearn`** - Scikit-learn integration

## Installation

```bash
pip install scitex
```

## Quick Start

### Generative AI (GenAI)

The GenAI module provides a unified interface for multiple AI providers:

```python
from scitex.ai.genai import GenAI

# Basic usage
ai = GenAI(provider="openai")
response = ai.complete("What is machine learning?")
print(response)

# With specific model and configuration
ai = GenAI(
    provider="anthropic",
    model="claude-3-opus-20240229",
    system_prompt="You are a helpful AI assistant."
)
response = ai.complete("Explain neural networks")

# Check costs
print(ai.get_cost_summary())
```

For one-off completions:

```python
from scitex.ai.genai import complete

response = complete("Quick question", provider="openai")
```

### Training Utilities

```python
from scitex.ai import EarlyStopping, LearningCurveLogger

# Early stopping
early_stopper = EarlyStopping(patience=10, min_delta=0.001)

# Learning curve logging
logger = LearningCurveLogger(log_dir="./logs")
```

### Classification

```python
from scitex.ai import ClassificationReporter

reporter = ClassificationReporter()
report = reporter.generate_report(y_true, y_pred)
```

## GenAI Module Features

### Supported Providers

- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini)
- Groq
- DeepSeek
- Perplexity
- Local LLaMA models

### Key Features

1. **Unified Interface**: Same API for all providers
2. **Cost Tracking**: Automatic token counting and cost calculation
3. **Chat History**: Maintains conversation context
4. **Error Handling**: Robust error handling across providers
5. **Type Safety**: Provider enum for type-safe provider selection
6. **Streaming Support**: Stream responses (provider-dependent)
7. **Image Support**: Multi-modal capabilities (provider-dependent)

### Example: Multi-Provider Comparison

```python
from scitex.ai.genai import GenAI, Provider

prompt = "Explain quantum computing in simple terms"

# Compare different providers
for provider in [Provider.OPENAI, Provider.ANTHROPIC]:
    try:
        ai = GenAI(provider=provider)
        response = ai.complete(prompt)
        print(f"\n{provider.value}: {response[:100]}...")
        print(f"Cost: {ai.get_cost_summary()}")
    except Exception as e:
        print(f"{provider.value} error: {e}")
```

## Migration from Old API

If you're using the old `genai_factory` or `BaseGenAI`:

```python
# Old way (deprecated)
from scitex.ai._gen_ai import genai_factory
ai = genai_factory("gpt-4")
response = ai.run("Hello")

# New way
from scitex.ai.genai import GenAI
ai = GenAI(provider="openai", model="gpt-4")
response = ai.complete("Hello")
```

See [Migration Guide](genai/MIGRATION_GUIDE.md) for detailed migration instructions.

## Neural Network Components

### Custom Layers

```python
import torch.nn as nn
from scitex.ai.layer import Pass, Switch

model = nn.Sequential(
    nn.Linear(784, 256),
    Pass(),  # Identity layer
    Switch(lambda x: x > 0),  # Conditional switching
    nn.Linear(256, 10)
)
```

### Loss Functions

```python
from scitex.ai.loss import MultiTaskLoss, L1L2Loss

# Multi-task learning
criterion = MultiTaskLoss(task_weights=[1.0, 0.5])

# Combined L1 and L2 loss
criterion = L1L2Loss(l1_weight=0.1, l2_weight=0.9)
```

## Clustering & Dimensionality Reduction

```python
from scitex.ai.clustering import umap, pca

# UMAP embedding
embedding = umap(data, n_components=2)

# PCA
principal_components = pca(data, n_components=10)
```

## Classification Tools

### ClassificationReporter

Comprehensive classification metrics and reporting:

```python
from scitex.ai import ClassificationReporter

reporter = ClassificationReporter(save_dir="./results")
reporter.calc_metrics(y_true, y_pred, y_prob, labels=['class0', 'class1'])
reporter.summarize()
reporter.save()
```

### EarlyStopping

Monitor validation performance and stop training early:

```python
from scitex.ai import EarlyStopping

early_stopper = EarlyStopping(
    patience=10,
    verbose=True,
    delta=0.001,
    direction="minimize"
)

for epoch in range(100):
    val_loss = train_epoch()
    early_stopper(val_loss, model)
    if early_stopper.early_stop:
        print("Early stopping triggered")
        break
```

## Best Practices

1. **API Keys**: Set environment variables for API keys
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - etc.

2. **Cost Management**: Monitor costs with detailed tracking
   ```python
   costs = ai.get_detailed_costs()
   print(f"Total: ${costs['total_cost']:.4f}")
   ```

3. **Error Handling**: Always handle potential API errors
   ```python
   try:
       response = ai.complete(prompt)
   except ValueError as e:
       print(f"Configuration error: {e}")
   except Exception as e:
       print(f"API error: {e}")
   ```

4. **Memory Management**: Clear history when not needed
   ```python
   ai.clear_history()  # Free up memory
   ```

## Examples

See the [examples directory](../../../examples/scitex/ai/) for complete working examples:
- `genai_example.py` - Comprehensive GenAI usage examples
- More examples coming soon...

## API Reference

### Main Classes
- `GenAI` - Main generative AI interface
- `ClassificationReporter` - Classification metrics and reporting
- `EarlyStopping` - Early stopping for training
- `LearningCurveLogger` - Learning curve tracking

### Submodules
- `scitex.ai.genai` - Generative AI providers
- `scitex.ai.training` - Training utilities
- `scitex.ai.classification` - Classification tools
- `scitex.ai.clustering` - Clustering algorithms
- `scitex.ai.layer` - Custom layers
- `scitex.ai.loss` - Loss functions
- `scitex.ai.metrics` - Evaluation metrics
- `scitex.ai.optim` - Optimizers

## Contributing

When contributing to the AI module:
1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Consider backward compatibility

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

For more information and updates, please visit the [scitex GitHub repository](https://github.com/ywatanabe1989/scitex).