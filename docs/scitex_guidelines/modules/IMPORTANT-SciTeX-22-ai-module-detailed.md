# SciTeX AI Module - Detailed Reference Guide

## Overview

The `scitex.ai` module provides comprehensive artificial intelligence capabilities including:
- Generative AI integration (OpenAI, Anthropic, Google, etc.)
- Classical machine learning utilities
- Deep learning components
- Training utilities
- Metrics and loss functions
- Visualization tools for AI/ML

## Module Structure

```
scitex/ai/
├── genai/               # Generative AI providers and utilities
├── classification/      # Classification utilities
├── clustering/         # Clustering algorithms (UMAP, PCA)
├── feature_extraction/ # Feature extraction methods
├── layer/              # Neural network layers
├── loss/               # Loss functions
├── metrics/            # Evaluation metrics
├── optim/              # Optimizers
├── plt/                # AI-specific plotting
├── sk/                 # Scikit-learn integration
├── sklearn/            # Scikit-learn wrappers
├── training/           # Training utilities
└── utils/              # General AI utilities
```

## 1. Generative AI (genai)

### Overview
The genai submodule provides a unified interface for multiple AI providers.

### Basic Usage

```python
import scitex.ai

# Initialize with provider
genai = scitex.ai.GenAI(provider="openai", api_key="your-key")

# Simple completion
response = genai.complete("What is machine learning?")

# With system prompt
genai = scitex.ai.GenAI(
    provider="anthropic",
    api_key="your-key",
    system_prompt="You are a helpful scientific assistant."
)

# Streaming response
for chunk in genai.stream("Explain neural networks"):
    print(chunk, end="")
```

### Supported Providers

1. **OpenAI**
   - Models: gpt-3.5-turbo, gpt-4, gpt-4-turbo, o1
   - Features: Function calling, vision, streaming

2. **Anthropic**
   - Models: claude-3-opus, claude-3-sonnet, claude-3-haiku
   - Features: Long context, vision, streaming

3. **Google**
   - Models: gemini-pro, gemini-pro-vision
   - Features: Multimodal, streaming

4. **Groq**
   - Models: mixtral-8x7b, llama-70b
   - Features: Fast inference

5. **Perplexity**
   - Models: pplx-70b-online, pplx-7b-online
   - Features: Real-time web search

6. **DeepSeek**
   - Models: deepseek-coder, deepseek-chat
   - Features: Code generation

### Advanced Features

```python
# Cost tracking
genai = scitex.ai.GenAI(provider="openai", api_key="key")
response = genai.complete("Hello")
print(genai.cost_tracker.get_summary())

# Chat history management
genai.complete("What is Python?")
genai.complete("What are its main features?")  # Maintains context
print(genai.chat_history.messages)

# Image input (for vision models)
response = genai.complete(
    "What's in this image?",
    images=["path/to/image.jpg"]
)

# Provider switching
genai.switch_provider("anthropic", api_key="new-key")
```

### Configuration Options

```python
genai = scitex.ai.GenAI(
    provider="openai",
    api_key="key",
    model="gpt-4",              # Specific model
    temperature=0.7,            # Creativity (0-2)
    max_tokens=1000,           # Response length
    seed=42,                   # Reproducibility
    stream=False,              # Streaming mode
    n_draft=1,                 # Number of drafts
    system_prompt="...",       # System instructions
)
```

## 2. Classification

### Classification Reporter

```python
from scitex.ai import ClassificationReporter

# Initialize reporter
reporter = ClassificationReporter(
    classes=["cat", "dog", "bird"],
    save_dir="./results"
)

# Add predictions
reporter.add_batch(y_true, y_pred, phase="train")
reporter.add_batch(y_true_val, y_pred_val, phase="val")

# Generate report
report = reporter.generate_report()
reporter.save_figures()
```

### Classifier Server

```python
from scitex.ai import ClassifierServer

# Create server for model deployment
server = ClassifierServer(
    model=trained_model,
    preprocessor=data_preprocessor,
    classes=class_names
)

# Serve predictions
server.start(port=8000)
```

## 3. Clustering

### UMAP

```python
from scitex.ai.clustering import umap

# Basic UMAP
embedding = umap(data, n_components=2)

# With parameters
embedding = umap(
    data,
    n_components=3,
    n_neighbors=15,
    min_dist=0.1,
    metric='euclidean'
)
```

### PCA

```python
from scitex.ai.clustering import pca

# Principal Component Analysis
components = pca(data, n_components=10)
explained_variance = pca.explained_variance_ratio_
```

## 4. Training Utilities

### Early Stopping

```python
from scitex.ai.training import EarlyStopping

early_stopping = EarlyStopping(
    patience=10,
    min_delta=0.001,
    mode='min'  # or 'max'
)

for epoch in range(100):
    train_loss = train_epoch()
    val_loss = validate()
    
    if early_stopping.check(val_loss):
        print(f"Early stopping at epoch {epoch}")
        break
```

### Learning Curve Logger

```python
from scitex.ai.training import LearningCurveLogger

logger = LearningCurveLogger(
    save_dir="./logs",
    metrics=["loss", "accuracy", "f1_score"]
)

# Log metrics
logger.log(epoch=1, train_loss=0.5, val_loss=0.6)
logger.plot_curves()
```

## 5. Loss Functions

### Multi-Task Loss

```python
from scitex.ai.loss import MultiTaskLoss

# Weighted multi-task loss
mtl = MultiTaskLoss(
    task_weights={"segmentation": 1.0, "classification": 0.5}
)

total_loss = mtl(losses_dict)
```

### L1L2 Loss

```python
from scitex.ai.loss import L1L2Loss

# Combined L1 and L2 loss
loss_fn = L1L2Loss(l1_weight=0.5, l2_weight=0.5)
loss = loss_fn(pred, target)
```

## 6. Metrics

### Balanced Accuracy

```python
from scitex.ai.metrics import bACC

# Calculate balanced accuracy
balanced_acc = bACC(y_true, y_pred)
```

### Silhouette Score

```python
from scitex.ai.metrics import silhouette_score_block

# For clustering evaluation
score = silhouette_score_block(features, labels)
```

## 7. Optimizers

### Get/Set Optimizer States

```python
from scitex.ai.optim import get_optimizer_state, set_optimizer_state

# Save optimizer state
state = get_optimizer_state(optimizer)

# Restore optimizer state
set_optimizer_state(optimizer, state)
```

### Available Optimizers

```python
# Standard optimizers via torch
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Advanced optimizers (if pytorch-optimizer installed)
from pytorch_optimizer import Ranger21
optimizer = Ranger21(model.parameters(), lr=0.001)
```

## 8. Visualization

### Confusion Matrix

```python
from scitex.ai.plt import conf_mat

# Plot confusion matrix
conf_mat(cm_matrix, labels=class_names, ax=ax)
```

### Learning Curves

```python
from scitex.ai.plt import plot_learning_curve

# Plot training history
plot_learning_curve(
    train_losses,
    val_losses,
    train_accs,
    val_accs,
    save_path="./learning_curve.png"
)
```

### Optuna Study Visualization

```python
from scitex.ai.plt import plot_optuna_study

# Visualize hyperparameter optimization
plot_optuna_study(study, save_dir="./optuna_plots")
```

## 9. Scikit-learn Integration

### Classifier Wrapper

```python
from scitex.ai.sklearn import clf

# Unified interface for sklearn classifiers
model = clf("random_forest", n_estimators=100)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### Time Series Formatting

```python
from scitex.ai.sklearn import to_sktime

# Convert to sktime format
X_sktime, y_sktime = to_sktime(X, y)
```

## 10. Utilities

### Data Utilities

```python
from scitex.ai.utils import (
    under_sample,
    merge_labels,
    sliding_window_data_augmentation,
    format_samples_for_sktime
)

# Balance dataset
X_balanced, y_balanced = under_sample(X, y)

# Merge similar labels
y_merged = merge_labels(y, mapping={0: 0, 1: 0, 2: 1})

# Data augmentation
X_aug, y_aug = sliding_window_data_augmentation(X, y, window_size=100)
```

### Verification Utilities

```python
from scitex.ai.utils import verify_n_gpus, check_params

# Check GPU availability
verify_n_gpus(required=2)

# Validate parameters
check_params(params, required=["learning_rate", "batch_size"])
```

## Best Practices

1. **API Key Management**
   ```python
   # Use environment variables
   import os
   api_key = os.environ.get("OPENAI_API_KEY")
   
   # Or use auth manager
   from scitex.ai.genai import AuthManager
   auth = AuthManager(api_key, provider)
   ```

2. **Error Handling**
   ```python
   try:
       response = genai.complete(prompt)
   except RateLimitError:
       time.sleep(60)
       response = genai.complete(prompt)
   except APIError as e:
       print(f"API error: {e}")
   ```

3. **Cost Management**
   ```python
   # Monitor costs
   genai = scitex.ai.GenAI(provider="openai", api_key=key)
   
   # Set limits
   if genai.cost_tracker.total_cost > 10.0:
       print("Cost limit reached!")
   ```

4. **Context Management**
   ```python
   # Clear history when switching topics
   genai.chat_history.clear()
   
   # Or manage manually
   genai.chat_history.add_message("user", "New topic...")
   ```

## Common Issues and Solutions

1. **Import Errors**
   ```python
   # If provider-specific packages missing
   pip install openai anthropic google-generativeai
   ```

2. **Rate Limiting**
   ```python
   # Add retry logic
   from tenacity import retry, wait_exponential
   
   @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
   def safe_complete(prompt):
       return genai.complete(prompt)
   ```

3. **Memory Issues with Large Models**
   ```python
   # Use smaller models or streaming
   genai = scitex.ai.GenAI(
       provider="openai",
       model="gpt-3.5-turbo",  # Smaller model
       stream=True
   )
   ```

## Migration Guide

If migrating from old AI module structure:

1. **BaseGenAI → GenAI**
   ```python
   # Old
   from scitex.ai._gen_ai import BaseGenAI
   ai = BaseGenAI(api_key=key, model="gpt-4")
   
   # New
   from scitex.ai import GenAI
   ai = GenAI(provider="openai", api_key=key, model="gpt-4")
   ```

2. **Provider-specific classes → Unified interface**
   ```python
   # Old
   from scitex.ai._gen_ai import OpenAI, Anthropic
   openai = OpenAI(api_key=key1)
   anthropic = Anthropic(api_key=key2)
   
   # New
   from scitex.ai import GenAI
   genai = GenAI(provider="openai", api_key=key1)
   genai.switch_provider("anthropic", api_key=key2)
   ```

## See Also

- `scitex.nn` - Neural network layers and components
- `scitex.plt` - General plotting utilities
- `scitex.stats` - Statistical analysis tools
- `scitex.pd` - Data manipulation utilities