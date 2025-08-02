# scitex.ai Module Documentation

## Overview

The `scitex.ai` module provides comprehensive tools for artificial intelligence and machine learning workflows, including deep learning utilities, classification reporting, generative AI integration, and visualization tools. It's designed to support both research and production environments with a focus on reproducibility and ease of use.

## Module Structure

```
scitex.ai/
├── genai/            # Generative AI providers (NEW - refactored)
├── training/         # Training utilities (EarlyStopping, etc.)
├── classification/   # Classification reporting and tools
├── act/              # Activation functions
├── clustering/       # Dimensionality reduction and clustering
├── feature_extraction/ # Feature extraction methods
├── layer/            # Custom neural network layers
├── loss/             # Loss functions
├── metrics/          # Evaluation metrics
├── optim/            # Optimizers
├── plt/              # AI-specific plotting functions
├── sampling/         # Data sampling utilities
├── sklearn/          # Scikit-learn integration
└── utils/            # General AI utilities
```

## Core Components

### 1. Generative AI Integration (NEW)

The refactored GenAI module provides a unified interface for multiple providers with component-based architecture.

```python
from scitex.ai.genai import GenAI

# Basic usage
ai = GenAI(provider="openai")
response = ai.complete("Explain quantum computing")
print(ai.get_cost_summary())

# Advanced configuration
ai = GenAI(
    provider="anthropic",
    model="claude-3-opus-20240229",
    system_prompt="You are a helpful coding assistant."
)

# One-off completion
from scitex.ai.genai import complete
response = complete("Quick question", provider="openai")
```

**Key Features:**
- Unified interface for all providers
- Automatic cost tracking
- Conversation history management
- Type-safe provider selection
- Robust error handling

**Supported Providers:**
- OpenAI (GPT models)
- Anthropic (Claude)
- Google (Gemini)
- DeepSeek
- Groq
- Llama
- Perplexity

### 2. Classification and Reporting

#### ClassificationReporter
Comprehensive classification metrics evaluation and reporting system.

```python
from scitex.ai import ClassificationReporter

# Create a classification reporter
reporter = ClassificationReporter(
    name="experiment_1",
    save_dir="./results"
)

# Evaluate predictions
metrics = reporter.evaluate(y_true, y_pred)

# Save comprehensive report
reporter.save_report()
```

#### MultiClassificationReporter
Manages multiple classification reporters for multi-target tasks.

```python
# For multi-target classification
multi_reporter = MultiClassificationReporter(
    target_names=["task1", "task2", "task3"]
)
```

### 3. Deep Learning Components

#### Early Stopping
Prevent overfitting during training.

```python
from scitex.ai import EarlyStopping

early_stopper = EarlyStopping(
    patience=10,
    verbose=True,
    delta=0.001
)

for epoch in range(epochs):
    val_loss = train_epoch(...)
    
    early_stopper(val_loss, model)
    if early_stopper.early_stop:
        print("Early stopping triggered")
        break
```

#### Custom Layers
```python
from scitex.ai.layer import Pass, Switch

# Pass-through layer
pass_layer = Pass()

# Conditional switch layer
switch = Switch(condition_fn)
```

#### Loss Functions
```python
from scitex.ai.loss import MultiTaskLoss, L1L2Loss

# Multi-task loss
mtl_loss = MultiTaskLoss(task_weights=[1.0, 0.5, 0.3])

# Combined L1/L2 loss
l1l2_loss = L1L2Loss(l1_weight=0.1, l2_weight=0.9)
```

### 4. Dimensionality Reduction and Clustering

```python
from scitex.ai.clustering import pca, umap

# PCA
pca_result = pca(
    data,
    n_components=2,
    return_model=True
)

# UMAP
umap_result = umap(
    data,
    n_components=2,
    n_neighbors=15,
    min_dist=0.1
)
```

### 5. Metrics and Evaluation

```python
from scitex.ai.metrics import bACC, silhouette_score_block

# Balanced accuracy
bacc = bACC(y_true, y_pred)

# Silhouette score for clustering
score = silhouette_score_block(features, labels)
```

### 6. Visualization

```python
import scitex.ai.plt as aiplt

# Confusion matrix
aiplt.conf_mat(
    y_true,
    y_pred,
    class_names=["A", "B", "C"]
)

# Learning curves
aiplt.learning_curve(
    train_losses,
    val_losses,
    save_path="learning_curve.png"
)

# ROC curve with AUC
aiplt.aucs.roc_auc(
    y_true,
    y_scores,
    save_path="roc_curve.png"
)
```

## Common Workflows

### 1. Complete Classification Pipeline

```python
import scitex.ai
import numpy as np
from sklearn.model_selection import train_test_split

# Load and prepare data
X, y = load_data()
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Train model
model = train_classifier(X_train, y_train)
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)

# Create reporter
reporter = scitex.ai.ClassificationReporter(
    name="my_experiment",
    save_dir="./results"
)

# Evaluate and visualize
metrics = reporter.evaluate(y_test, y_pred, y_proba)

# Generate visualizations
scitex.ai.plt.conf_mat(y_test, y_pred)
scitex.ai.plt.aucs.roc_auc(y_test, y_proba[:, 1])

# Save comprehensive report
reporter.save_report()
```

### 2. Multi-Provider AI Comparison

```python
from scitex.ai.genai import GenAI, Provider

prompt = "Explain machine learning in simple terms"

# Compare different providers
results = {}
for provider in [Provider.OPENAI, Provider.ANTHROPIC]:
    try:
        ai = GenAI(provider=provider)
        response = ai.complete(prompt)
        results[provider.value] = {
            'response': response,
            'cost': ai.get_cost_summary()
        }
    except Exception as e:
        results[provider.value] = {'error': str(e)}

# Analyze results
for provider, result in results.items():
    print(f"\n{provider}:")
    if 'error' in result:
        print(f"  Error: {result['error']}")
    else:
        print(f"  Response: {result['response'][:100]}...")
        print(f"  {result['cost']}")
```

### 3. Conversational AI with History

```python
from scitex.ai.genai import GenAI

# Create conversational AI
ai = GenAI(
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    system_prompt="You are a helpful Python tutor."
)

# Have a conversation
questions = [
    "What are Python decorators?",
    "Can you show me an example?",
    "How do they differ from function wrappers?"
]

for question in questions:
    response = ai.complete(question)
    print(f"Q: {question}")
    print(f"A: {response}\n")

# Review conversation history
print("\nConversation Summary:")
for i, msg in enumerate(ai.get_history()):
    print(f"{i}. {msg.role}: {msg.content[:50]}...")

# Check total cost
print(f"\n{ai.get_cost_summary()}")
```

### 4. Dimensionality Reduction Pipeline

```python
import scitex.ai
import scitex.plt

# Reduce dimensions
reduced_data = scitex.ai.clustering.umap(
    high_dim_data,
    n_components=2
)

# Visualize
fig, ax = scitex.plt.subplots()
scatter = ax.scatter(
    reduced_data[:, 0],
    reduced_data[:, 1],
    c=labels,
    cmap='viridis'
)
ax.set_title("UMAP Projection")
scitex.plt.colorbar(scatter, ax=ax)
scitex.io.save(fig, "umap_visualization.png")
```

## Best Practices

### 1. API Key Management
Set environment variables for security:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Cost Management
Monitor AI API costs:
```python
from scitex.ai.genai import GenAI

ai = GenAI(provider="openai", model="gpt-4")

# Use the model...
for prompt in prompts:
    ai.complete(prompt)

# Get detailed cost breakdown
costs = ai.get_detailed_costs()
print(f"Total cost: ${costs['total_cost']:.4f}")
print(f"Cost by model: {costs['cost_by_model']}")
```

### 3. Error Handling
Use appropriate error handling:
```python
from scitex.ai.genai import GenAI

try:
    ai = GenAI(provider="openai")
    response = ai.complete(prompt)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
    # Use fallback provider
    ai = GenAI(provider="anthropic")
    response = ai.complete(prompt)
```

### 4. Reproducibility
Always set random seeds:
```python
import scitex.repro
scitex.repro.fix_seeds(42)
```

### 5. Memory Management
Clear conversation history when needed:
```python
ai = GenAI(provider="openai")

# After completing a task
ai.clear_history()  # Free up memory
ai.reset_costs()    # Reset cost tracking
```

## Migration Guide

### From Old to New GenAI API

```python
# Old way (deprecated)
from scitex.ai._gen_ai import genai_factory
ai = genai_factory("gpt-4")
response = ai.run("Hello")
costs = ai.calc_costs()

# New way
from scitex.ai.genai import GenAI
ai = GenAI(provider="openai", model="gpt-4")
response = ai.complete("Hello")
costs = ai.get_cost_summary()
```

See [GenAI Migration Guide](../../src/scitex/ai/genai/MIGRATION_GUIDE.md) for detailed instructions.

## Integration with Other SciTeX Modules

### With scitex.io
```python
# Save model artifacts
scitex.io.save(model.state_dict(), "model_weights.pth")
scitex.io.save(metrics, "evaluation_metrics.json")

# Load configurations
config = scitex.io.load_configs("experiment_config.yaml")
```

### With scitex.plt
```python
# Enhanced plotting
fig, axes = scitex.plt.subplots(2, 2, figsize=(10, 10))

# Use scitex.plt features
scitex.ai.plt.conf_mat(y_true, y_pred, ax=axes[0, 0])
scitex.ai.plt.learning_curve(history, ax=axes[0, 1])
```

### With scitex.gen
```python
# Experiment management
exp_id = scitex.gen.gen_ID()
timestamp = scitex.gen.gen_timestamp()

# Start experiment
scitex.gen.start(
    sys_=f"experiment_{exp_id}",
    sdir=f"./results/{timestamp}"
)
```

## Advanced Features

### 1. Custom Metrics
Extend the metrics system:
```python
class CustomMetric(scitex.ai.metrics.BaseMetric):
    def calculate(self, y_true, y_pred):
        # Custom metric implementation
        return custom_score
```

### 2. Model Deployment
Deploy models as services:
```python
from scitex.ai import ClassifierServer

server = ClassifierServer(
    model=trained_model,
    preprocessor=data_preprocessor,
    port=8080
)

server.start()
```

### 3. Batch Processing
Process multiple items efficiently:
```python
from scitex.ai.genai import GenAI

ai = GenAI(provider="openai")

# Process in batches
batch_size = 10
results = []

for i in range(0, len(prompts), batch_size):
    batch = prompts[i:i + batch_size]
    for prompt in batch:
        result = ai.complete(prompt)
        results.append(result)
    
    # Check costs periodically
    if i % 50 == 0:
        print(ai.get_cost_summary())
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**
   ```python
   import time
   
   def retry_with_backoff(func, max_retries=3):
       for i in range(max_retries):
           try:
               return func()
           except Exception as e:
               if i < max_retries - 1:
                   time.sleep(2 ** i)
               else:
                   raise
   ```

2. **Memory Issues with Large Datasets**
   - Use data generators
   - Process in chunks
   - Clear unused variables

3. **Cost Overruns**
   - Set budget limits
   - Use cheaper models for testing
   - Cache responses when possible

### Debug Mode
Enable verbose logging:
```python
from scitex import logging
logging.getLogger('scitex.ai').setLevel(logging.DEBUG)
```

## References

- [SciTeX AI Module Source](https://github.com/ywatanabe1989/scitex/tree/main/src/scitex/ai/)
- [GenAI Module Documentation](../../src/scitex/ai/genai/README.md)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Anthropic API Documentation](https://docs.anthropic.com/)