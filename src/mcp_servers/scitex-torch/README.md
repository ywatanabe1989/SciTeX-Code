# SciTeX Torch MCP Server

PyTorch deep learning translations and tools for SciTeX.

## Features

### 1. Model I/O Translation
- Enhanced model saving with metadata
- Checkpoint management with versioning
- State dict extraction and validation
- Model loading with device handling

### 2. Training Loop Enhancement
- Monitored training loops with progress tracking
- Gradient tracking and debugging
- Optimizer step monitoring
- Automatic metric logging

### 3. Data Pipeline Generation
- Image, text, and tabular data pipelines
- Configurable augmentations
- DataLoader with monitoring
- Dataset validation

### 4. Architecture Tracking
- Parameter tracking in models
- Forward pass monitoring
- Architecture enhancement
- Performance profiling

### 5. Best Practices Validation
- Code quality checks
- Device management validation
- Reproducibility checks
- Mixed precision suggestions

## Tools

- `translate_torch_to_scitex`: Convert PyTorch code to SciTeX patterns
- `generate_torch_training_template`: Create complete training scripts
- `translate_model_architecture`: Enhance model definitions
- `generate_data_pipeline`: Create data processing pipelines
- `validate_torch_code`: Check for best practices
- `create_model_card`: Generate model documentation

## Usage Examples

### Basic Translation
```python
# From standard PyTorch
code = """
torch.save(model.state_dict(), 'model.pth')
model = torch.load('model.pth')
"""
# Becomes:
stx.torch.save_model(model, 'model.pth')
model = stx.torch.load_model('model.pth')
```

### Training Template
```python
# Generate complete training script
generate_torch_training_template(
    model_type="classification",
    dataset_name="CIFAR10Dataset",
    include_validation=True,
    include_tensorboard=True
)
```

### Data Pipeline
```python
# Generate image data pipeline
generate_data_pipeline(
    data_type="image",
    augmentations=["normalize", "random_flip", "random_crop"]
)
```

## Installation

```bash
cd mcp_servers/scitex-torch
pip install -e .
```

## Configuration

Add to your MCP settings:
```json
{
  "mcpServers": {
    "scitex-torch": {
      "command": "python",
      "args": ["-m", "scitex_torch.server"]
    }
  }
}
```

## Key Benefits

1. **Simplified Model Management**: Automatic versioning and metadata tracking
2. **Enhanced Training**: Built-in monitoring and debugging capabilities
3. **Reproducibility**: Enforced best practices for reproducible research
4. **Performance**: Automatic optimization suggestions
5. **Documentation**: Auto-generated model cards and documentation