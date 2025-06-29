#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:54:00 (ywatanabe)"
# File: ./mcp_servers/scitex-torch/server.py
# ----------------------------------------

"""MCP server for SciTeX PyTorch module translations and deep learning tools."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from scitex_base import ScitexBaseMCPServer, ScitexTranslatorMixin


class ScitexTorchMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX PyTorch module translations."""
    
    def __init__(self):
        super().__init__("torch", "0.1.0")
        
    def _register_module_tools(self):
        """Register torch-specific tools."""
        
        @self.app.tool()
        async def translate_torch_to_scitex(
            code: str,
            add_imports: bool = True
        ) -> Dict[str, Any]:
            """
            Translate standard PyTorch code to SciTeX format.
            
            Args:
                code: PyTorch code to translate
                add_imports: Whether to add necessary imports
                
            Returns:
                Dictionary with translated code and changes made
            """
            
            translated = code
            imports_needed = set()
            changes = []
            
            # Model saving/loading patterns
            model_patterns = [
                # Save patterns
                (r"torch\.save\(([^,]+),\s*['\"]([^'\"]+)['\"]\)", 
                 r"stx.torch.save_model(\1, '\2')",
                 "Model saving with metadata"),
                
                # Load patterns
                (r"torch\.load\(['\"]([^'\"]+)['\"]\)",
                 r"stx.torch.load_model('\1')",
                 "Model loading with validation"),
                
                # State dict patterns
                (r"model\.state_dict\(\)",
                 r"stx.torch.get_state_dict(model)",
                 "Enhanced state dict extraction"),
                
                # Checkpoint patterns
                (r"torch\.save\({[^}]+},\s*['\"]([^'\"]+)['\"]\)",
                 r"stx.torch.save_checkpoint(..., '\1')",
                 "Checkpoint saving with versioning"),
            ]
            
            # Training loop patterns
            training_patterns = [
                # Basic training loop
                (r"for epoch in range\(([^)]+)\):",
                 r"for epoch in stx.torch.training_loop(\1):",
                 "Enhanced training loop with monitoring"),
                
                # Loss tracking
                (r"loss\.backward\(\)",
                 r"stx.torch.backward_with_tracking(loss)",
                 "Gradient tracking and debugging"),
                
                # Optimizer step
                (r"optimizer\.step\(\)",
                 r"stx.torch.optimizer_step(optimizer)",
                 "Optimizer step with monitoring"),
            ]
            
            # Data loading patterns
            data_patterns = [
                # DataLoader creation
                (r"DataLoader\(([^)]+)\)",
                 r"stx.torch.create_dataloader(\1)",
                 "Enhanced DataLoader with monitoring"),
                
                # Dataset patterns
                (r"class\s+(\w+)\(.*Dataset\):",
                 r"class \1(stx.torch.BaseDataset):",
                 "Dataset with built-in validation"),
            ]
            
            # Apply model patterns
            for pattern, replacement, description in model_patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    imports_needed.add("stx.torch")
                    changes.append({
                        "type": "model_io",
                        "pattern": pattern,
                        "description": description
                    })
            
            # Apply training patterns
            for pattern, replacement, description in training_patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    imports_needed.add("stx.torch")
                    changes.append({
                        "type": "training",
                        "pattern": pattern,
                        "description": description
                    })
            
            # Apply data patterns
            for pattern, replacement, description in data_patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    imports_needed.add("stx.torch")
                    changes.append({
                        "type": "data",
                        "pattern": pattern,
                        "description": description
                    })
            
            # Add device management
            if "cuda" in translated or "cpu" in translated:
                device_replacements = [
                    (r"\.to\(['\"]cuda['\"]\)", ".to(stx.torch.get_device())"),
                    (r"torch\.cuda\.is_available\(\)", "stx.torch.cuda_available()"),
                    (r"device\s*=\s*['\"]cuda['\"]", "device = stx.torch.get_device()"),
                ]
                for pattern, replacement in device_replacements:
                    if re.search(pattern, translated):
                        translated = re.sub(pattern, replacement, translated)
                        imports_needed.add("stx.torch")
                        changes.append({
                            "type": "device",
                            "pattern": pattern,
                            "description": "Device management"
                        })
            
            # Add imports if needed
            if add_imports and imports_needed:
                import_lines = "import scitex as stx\n"
                if "import torch" not in translated:
                    import_lines += "import torch\n"
                translated = import_lines + "\n" + translated
            
            return {
                "translated_code": translated,
                "changes_made": len(changes),
                "change_details": changes,
                "imports_added": list(imports_needed)
            }
        
        @self.app.tool()
        async def generate_torch_training_template(
            model_type: str = "classification",
            dataset_name: str = "MyDataset",
            include_validation: bool = True,
            include_tensorboard: bool = True
        ) -> Dict[str, str]:
            """
            Generate a complete PyTorch training script following SciTeX patterns.
            
            Args:
                model_type: Type of model (classification, regression, etc.)
                dataset_name: Name for the dataset class
                include_validation: Include validation loop
                include_tensorboard: Include TensorBoard logging
                
            Returns:
                Complete training script
            """
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "{timestamp} (ywatanabe)"
# File: ./train_{model_type}.py
# ----------------------------------------

"""PyTorch {model_type} training with SciTeX patterns."""

import scitex as stx
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset
import numpy as np

# Load configuration
CONFIG = stx.io.load_configs()

# Set device
device = stx.torch.get_device()
print(f"Using device: {{device}}")

# Dataset definition
class {dataset_name}(stx.torch.BaseDataset):
    """Custom dataset for {model_type}."""
    
    def __init__(self, data_path, transform=None):
        super().__init__()
        self.data = stx.io.load(data_path)
        self.transform = transform
        
    def __len__(self):
        return len(self.data['X'])
        
    def __getitem__(self, idx):
        x = self.data['X'][idx]
        y = self.data['y'][idx]
        
        if self.transform:
            x = self.transform(x)
            
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y)

# Model definition
class {model_type.capitalize()}Model(nn.Module):
    """Neural network for {model_type}."""
    
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, output_dim)
        )
        
    def forward(self, x):
        return self.layers(x)

def train():
    """Main training function."""
    
    # Create datasets
    train_dataset = {dataset_name}(CONFIG.PATH.TRAIN_DATA)
    train_loader = stx.torch.create_dataloader(
        train_dataset, 
        batch_size=CONFIG.PARAMS.BATCH_SIZE,
        shuffle=True
    )
    '''
            
            if include_validation:
                script += f'''
    val_dataset = {dataset_name}(CONFIG.PATH.VAL_DATA)
    val_loader = stx.torch.create_dataloader(
        val_dataset,
        batch_size=CONFIG.PARAMS.BATCH_SIZE,
        shuffle=False
    )
    '''
            
            script += f'''
    # Initialize model
    model = {model_type.capitalize()}Model(
        input_dim=CONFIG.MODEL.INPUT_DIM,
        hidden_dim=CONFIG.MODEL.HIDDEN_DIM,
        output_dim=CONFIG.MODEL.OUTPUT_DIM
    ).to(device)
    
    # Loss and optimizer
    criterion = nn.{'CrossEntropyLoss' if model_type == 'classification' else 'MSELoss'}()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG.PARAMS.LR)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)
    '''
            
            if include_tensorboard:
                script += '''
    # TensorBoard logging
    writer = stx.torch.create_tensorboard_writer(CONFIG.PATH.LOG_DIR)
    '''
            
            script += f'''
    # Training loop
    best_val_loss = float('inf')
    
    for epoch in stx.torch.training_loop(CONFIG.PARAMS.EPOCHS):
        # Training phase
        model.train()
        train_loss = 0.0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            # Forward pass
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            
            # Backward pass
            stx.torch.backward_with_tracking(loss)
            stx.torch.optimizer_step(optimizer)
            
            train_loss += loss.item()
            
            # Log batch metrics
            if batch_idx % 10 == 0:
                stx.torch.log_batch_metrics({{
                    'loss': loss.item(),
                    'lr': optimizer.param_groups[0]['lr']
                }}, epoch, batch_idx)
        '''
            
            if include_validation:
                script += '''
        # Validation phase
        model.eval()
        val_loss = 0.0
        correct = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                val_loss += criterion(output, target).item()
                
                if model_type == "classification":
                    pred = output.argmax(dim=1, keepdim=True)
                    correct += pred.eq(target.view_as(pred)).sum().item()
        
        val_loss /= len(val_loader)
        accuracy = correct / len(val_dataset) if model_type == "classification" else None
        '''
            
            script += f'''
        # Epoch metrics
        epoch_metrics = {{
            'train_loss': train_loss / len(train_loader),'''
            
            if include_validation:
                script += '''
            'val_loss': val_loss,'''
                if model_type == "classification":
                    script += '''
            'accuracy': accuracy,'''
            
            script += '''
        }
        
        stx.torch.log_epoch_metrics(epoch_metrics, epoch)
        '''
            
            if include_validation:
                script += '''
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Model checkpointing
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            stx.torch.save_checkpoint({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_loss': best_val_loss,
                'config': CONFIG.to_dict()
            }, CONFIG.PATH.CHECKPOINT_DIR / f'best_model.pth')
        '''
            
            script += '''
    # Save final model
    stx.torch.save_model(model, CONFIG.PATH.MODEL_PATH)
    print(f"Training complete! Model saved to {CONFIG.PATH.MODEL_PATH}")
    '''
            
            if include_tensorboard:
                script += '''
    writer.close()
    '''
            
            script += '''
    return model

if __name__ == "__main__":
    stx.gen.start()
    
    model = train()
    
    # Evaluate on test set if available
    if hasattr(CONFIG.PATH, 'TEST_DATA'):
        print("\\nEvaluating on test set...")
        test_metrics = stx.torch.evaluate_model(
            model, 
            CONFIG.PATH.TEST_DATA,
            device=device
        )
        stx.io.save(test_metrics, './test_results.json')
    
    stx.gen.close()

# EOF'''
            
            return {
                "script": script,
                "model_type": model_type,
                "features_included": {
                    "validation": include_validation,
                    "tensorboard": include_tensorboard,
                    "checkpointing": include_validation,
                    "lr_scheduling": include_validation,
                    "scitex_patterns": True
                }
            }
        
        @self.app.tool()
        async def translate_model_architecture(
            code: str,
            add_tracking: bool = True
        ) -> Dict[str, str]:
            """
            Enhance PyTorch model definitions with SciTeX features.
            
            Args:
                code: Model definition code
                add_tracking: Add parameter tracking
                
            Returns:
                Enhanced model code
            """
            
            enhanced = code
            
            # Add parameter tracking to __init__
            if "def __init__" in enhanced and add_tracking:
                init_pattern = r"(def __init__.*?:.*?super\(\).__init__\(\))"
                replacement = r"\1\n        stx.torch.track_model_params(self)"
                enhanced = re.sub(init_pattern, replacement, enhanced, flags=re.DOTALL)
            
            # Add forward pass tracking
            if "def forward" in enhanced:
                forward_pattern = r"(def forward\(self,.*?\):)"
                replacement = r"\1\n        # Track forward pass\n        with stx.torch.track_forward_pass():"
                enhanced = re.sub(forward_pattern, replacement, enhanced)
                
                # Indent the forward pass content
                lines = enhanced.split('\n')
                in_forward = False
                new_lines = []
                
                for line in lines:
                    if "def forward" in line:
                        in_forward = True
                        new_lines.append(line)
                    elif in_forward and line.strip() and not line.startswith('        '):
                        in_forward = False
                        new_lines.append(line)
                    elif in_forward and line.strip():
                        # Add extra indentation for tracking context
                        if "with stx.torch.track_forward_pass():" not in line:
                            new_lines.append('    ' + line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                enhanced = '\n'.join(new_lines)
            
            return {
                "enhanced_code": enhanced,
                "tracking_added": add_tracking,
                "features": ["parameter_tracking", "forward_pass_monitoring"]
            }
        
        @self.app.tool()
        async def generate_data_pipeline(
            data_type: str = "image",
            augmentations: List[str] = ["normalize", "random_flip"]
        ) -> Dict[str, str]:
            """
            Generate SciTeX-compliant data pipeline.
            
            Args:
                data_type: Type of data (image, text, tabular)
                augmentations: List of augmentations to apply
                
            Returns:
                Data pipeline code
            """
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if data_type == "image":
                transforms_code = self._generate_image_transforms(augmentations)
            elif data_type == "text":
                transforms_code = self._generate_text_transforms(augmentations)
            else:
                transforms_code = self._generate_tabular_transforms(augmentations)
            
            pipeline = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "{timestamp} (ywatanabe)"
# File: ./data_pipeline.py
# ----------------------------------------

"""Data pipeline for {data_type} processing."""

import scitex as stx
import torch
from torch.utils.data import Dataset, DataLoader
{self._get_imports_for_data_type(data_type)}

class {data_type.capitalize()}Pipeline(stx.torch.BaseDataPipeline):
    """Data pipeline for {data_type} data."""
    
    def __init__(self, data_path, mode='train'):
        super().__init__()
        self.data_path = data_path
        self.mode = mode
        self.transforms = self.get_transforms()
        
    def get_transforms(self):
        """Get appropriate transforms for mode."""
        if self.mode == 'train':
            return {transforms_code['train']}
        else:
            return {transforms_code['val']}
    
    def load_data(self):
        """Load data from disk."""
        return stx.io.load(self.data_path)
    
    def preprocess(self, sample):
        """Preprocess a single sample."""
        # Apply transforms
        if self.transforms:
            sample = self.transforms(sample)
        
        # Convert to tensor if needed
        if not isinstance(sample, torch.Tensor):
            sample = torch.tensor(sample)
            
        return sample
    
    def create_dataloader(self, batch_size=32, num_workers=4):
        """Create DataLoader with monitoring."""
        dataset = self.create_dataset()
        
        return stx.torch.create_dataloader(
            dataset,
            batch_size=batch_size,
            shuffle=(self.mode == 'train'),
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )

# Usage example
if __name__ == "__main__":
    # Create pipelines
    train_pipeline = {data_type.capitalize()}Pipeline(
        CONFIG.PATH.TRAIN_DATA,
        mode='train'
    )
    val_pipeline = {data_type.capitalize()}Pipeline(
        CONFIG.PATH.VAL_DATA,
        mode='val'
    )
    
    # Create dataloaders
    train_loader = train_pipeline.create_dataloader(
        batch_size=CONFIG.PARAMS.BATCH_SIZE
    )
    val_loader = val_pipeline.create_dataloader(
        batch_size=CONFIG.PARAMS.BATCH_SIZE
    )
    
    # Verify data
    stx.torch.verify_dataloader(train_loader, "Training")
    stx.torch.verify_dataloader(val_loader, "Validation")
    
    print("Data pipeline ready!")

# EOF'''
            
            return {
                "pipeline_code": pipeline,
                "data_type": data_type,
                "augmentations": augmentations,
                "features": ["monitoring", "verification", "caching"]
            }
        
        @self.app.tool()
        async def validate_torch_code(
            code: str
        ) -> Dict[str, Any]:
            """
            Validate PyTorch code for best practices.
            
            Args:
                code: PyTorch code to validate
                
            Returns:
                Validation results and suggestions
            """
            
            issues = []
            suggestions = []
            
            # Check for model evaluation mode
            if "model.eval()" not in code and "torch.no_grad()" in code:
                issues.append("Using torch.no_grad() without model.eval()")
                suggestions.append("Add model.eval() before validation/testing")
            
            # Check for gradient accumulation
            if "loss.backward()" in code and "optimizer.zero_grad()" not in code:
                issues.append("Calling loss.backward() without optimizer.zero_grad()")
                suggestions.append("Clear gradients before backward pass")
            
            # Check for device management
            if ".cuda()" in code or "cuda:0" in code:
                issues.append("Hard-coded CUDA device")
                suggestions.append("Use stx.torch.get_device() for flexible device management")
            
            # Check for data loading
            if "DataLoader" in code and "num_workers" not in code:
                suggestions.append("Consider setting num_workers for faster data loading")
            
            # Check for model saving
            if "torch.save" in code and "state_dict" not in code:
                issues.append("Saving entire model instead of state_dict")
                suggestions.append("Save model.state_dict() for better portability")
            
            # Check for reproducibility
            if "train" in code.lower() and "torch.manual_seed" not in code:
                suggestions.append("Set random seeds for reproducibility")
            
            # Check for mixed precision
            if "float16" not in code and "autocast" not in code:
                suggestions.append("Consider using mixed precision training for faster training")
            
            # Check for checkpoint
            if "for epoch" in code and "save" not in code:
                suggestions.append("Add checkpointing to save progress during training")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "suggestions": suggestions,
                "best_practices_score": max(0, 100 - len(issues) * 15 - len(suggestions) * 5)
            }
        
        @self.app.tool()
        async def create_model_card(
            model_name: str,
            model_type: str,
            dataset: str,
            metrics: Dict[str, float],
            hyperparameters: Dict[str, Any]
        ) -> Dict[str, str]:
            """
            Generate a model card for documentation.
            
            Args:
                model_name: Name of the model
                model_type: Type of model
                dataset: Dataset used
                metrics: Performance metrics
                hyperparameters: Training hyperparameters
                
            Returns:
                Model card in markdown format
            """
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            metrics_table = "\n".join([f"| {k} | {v:.4f} |" for k, v in metrics.items()])
            params_table = "\n".join([f"| {k} | {v} |" for k, v in hyperparameters.items()])
            
            model_card = f"""# Model Card: {model_name}

**Generated**: {timestamp}  
**Framework**: PyTorch with SciTeX  

## Model Details

- **Model Type**: {model_type}
- **Architecture**: See `model_architecture.py`
- **Input Format**: Defined in CONFIG
- **Output Format**: Defined in CONFIG

## Training Data

- **Dataset**: {dataset}
- **Preprocessing**: See `data_pipeline.py`
- **Train/Val/Test Split**: 80/10/10

## Performance

| Metric | Value |
|--------|-------|
{metrics_table}

## Hyperparameters

| Parameter | Value |
|-----------|-------|
{params_table}

## Usage

```python
import scitex as stx

# Load model
model = stx.torch.load_model('./models/{model_name}.pth')

# Inference
model.eval()
with torch.no_grad():
    predictions = model(input_data)
```

## Limitations

- Trained on specific data distribution
- Performance may degrade on out-of-distribution data
- Requires GPU for optimal inference speed

## Citation

If you use this model, please cite:
```
@misc{{{model_name},
  author = {{Your Name}},
  title = {{{model_name}}},
  year = {{2025}},
  publisher = {{Your Organization}}
}}
```

## License

This model is released under [Your License].
"""
            
            return {
                "model_card": model_card,
                "model_name": model_name,
                "format": "markdown"
            }
    
    def _generate_image_transforms(self, augmentations: List[str]) -> Dict[str, str]:
        """Generate image transformation code."""
        train_transforms = ["transforms.Compose(["]
        val_transforms = ["transforms.Compose(["]
        
        # Always include these
        base_transforms = [
            "    transforms.ToTensor(),",
            "    transforms.Normalize(mean=CONFIG.DATA.MEAN, std=CONFIG.DATA.STD)"
        ]
        
        # Add augmentations for training
        aug_map = {
            "random_flip": "    transforms.RandomHorizontalFlip(p=0.5),",
            "random_crop": "    transforms.RandomCrop(CONFIG.DATA.CROP_SIZE),",
            "color_jitter": "    transforms.ColorJitter(brightness=0.2, contrast=0.2),",
            "random_rotation": "    transforms.RandomRotation(degrees=15),",
        }
        
        for aug in augmentations:
            if aug in aug_map and aug != "normalize":
                train_transforms.append(aug_map[aug])
        
        train_transforms.extend(base_transforms)
        train_transforms.append("])")
        
        val_transforms.extend(base_transforms)
        val_transforms.append("])")
        
        return {
            "train": "\n        ".join(train_transforms),
            "val": "\n        ".join(val_transforms)
        }
    
    def _generate_text_transforms(self, augmentations: List[str]) -> Dict[str, str]:
        """Generate text transformation code."""
        # Simplified for brevity
        return {
            "train": "stx.torch.text.get_train_transforms()",
            "val": "stx.torch.text.get_val_transforms()"
        }
    
    def _generate_tabular_transforms(self, augmentations: List[str]) -> Dict[str, str]:
        """Generate tabular transformation code."""
        return {
            "train": "stx.torch.tabular.get_train_transforms()",
            "val": "stx.torch.tabular.get_val_transforms()"
        }
    
    def _get_imports_for_data_type(self, data_type: str) -> str:
        """Get necessary imports for data type."""
        imports = {
            "image": "from torchvision import transforms",
            "text": "from transformers import AutoTokenizer",
            "tabular": "from sklearn.preprocessing import StandardScaler"
        }
        return imports.get(data_type, "")
    
    def get_module_description(self) -> str:
        """Get description of torch functionality."""
        return (
            "SciTeX torch server provides PyTorch enhancements including model I/O, "
            "training loop monitoring, data pipeline generation, architecture tracking, "
            "and best practices validation for deep learning workflows."
        )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "translate_torch_to_scitex",
            "generate_torch_training_template",
            "translate_model_architecture",
            "generate_data_pipeline",
            "validate_torch_code",
            "create_model_card",
            "get_module_info",
            "validate_code"
        ]
    
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate torch module usage."""
        issues = []
        
        # Check for common anti-patterns
        if "torch.save(model," in code:
            issues.append("Saving entire model instead of state_dict")
        
        if ".cuda()" in code and "stx.torch" not in code:
            issues.append("Using raw CUDA calls instead of stx.torch device management")
        
        if "DataLoader" in code and "stx.torch.create_dataloader" not in code:
            issues.append("Using raw DataLoader instead of stx.torch.create_dataloader")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "module": "torch"
        }


# Main entry point
if __name__ == "__main__":
    server = ScitexTorchMCPServer()
    asyncio.run(server.run())

# EOF