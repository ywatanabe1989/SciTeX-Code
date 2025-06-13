#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-06 18:00:00 (ywatanabe)"
# File: ./examples/library_integration.py

"""
Functionalities:
- Demonstrates SciTeX integration with popular scientific libraries
- Shows interoperability with scikit-learn, PyTorch, MNE, and more
- Provides templates for common integration patterns

Example usage:
$ python ./examples/library_integration.py

Input:
- Various test datasets for different libraries

Output:
- ./examples/library_integration_out/:
  - models/: Trained models from different frameworks
  - results/: Integration test results
  - figures/: Visualizations
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import numpy as np
import pandas as pd
import scitex

# Scientific libraries
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available, skipping torch examples")

try:
    from sklearn import datasets, model_selection, ensemble
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available, skipping sklearn examples")

try:
    import mne
    MNE_AVAILABLE = True
except ImportError:
    MNE_AVAILABLE = False
    print("MNE not available, skipping MNE examples")

try:
    import xarray as xr
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    print("xarray not available, skipping xarray examples")

def sklearn_integration_example(output_dir: str):
    """Demonstrate SciTeX with scikit-learn."""
    if not SKLEARN_AVAILABLE:
        return None
        
    print("\n=== Scikit-learn Integration ===")
    
    # Generate classification dataset
    X, y = datasets.make_classification(
        n_samples=1000, n_features=20, n_informative=15, 
        n_redundant=5, n_classes=3, random_state=42
    )
    
    # Split data
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = ensemble.RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    accuracy = (y_pred == y_test).mean()
    
    print(f"Accuracy: {accuracy:.3f}")
    
    # Save with SciTeX
    scitex.io.save(os.path.join(output_dir, "models", "sklearn_rf_model.pkl"), model)
    
    # Create confusion matrix with SciTeX
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    scitex.plt.ax.plot.conf_mat(ax, y_test, y_pred)
    ax.set_title('Random Forest Confusion Matrix')
    scitex.io.save(os.path.join(output_dir, "figures", "sklearn_confusion_matrix.png"), fig)
    
    # Save results
    results = pd.DataFrame({
        'y_true': y_test,
        'y_pred': y_pred,
        'correct': y_test == y_pred
    })
    scitex.io.save(os.path.join(output_dir, "results", "sklearn_predictions.csv"), results)
    
    return {'accuracy': accuracy, 'model': 'RandomForest'}

def pytorch_integration_example(output_dir: str):
    """Demonstrate SciTeX with PyTorch."""
    if not TORCH_AVAILABLE:
        return None
        
    print("\n=== PyTorch Integration ===")
    
    # Create simple neural network
    class SimpleNet(nn.Module):
        def __init__(self, input_dim=10, hidden_dim=32, output_dim=2):
            super().__init__()
            self.fc1 = nn.Linear(input_dim, hidden_dim)
            self.fc2 = nn.Linear(hidden_dim, output_dim)
            self.relu = nn.ReLU()
            
        def forward(self, x):
            x = self.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    # Generate synthetic data
    X = torch.randn(1000, 10)
    y = (X.sum(dim=1) > 0).long()
    
    # Create data loader
    dataset = torch.utils.data.TensorDataset(X, y)
    loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Initialize model
    model = SimpleNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    # Training loop
    model.train()
    for epoch in range(10):
        total_loss = 0
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if epoch % 5 == 0:
            print(f"Epoch {epoch}, Loss: {total_loss/len(loader):.4f}")
    
    # Save model with SciTeX
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'model_config': {'input_dim': 10, 'hidden_dim': 32, 'output_dim': 2}
    }
    scitex.io.save(os.path.join(output_dir, "models", "pytorch_model.pth"), checkpoint)
    
    # Evaluate
    model.eval()
    with torch.no_grad():
        outputs = model(X)
        _, predicted = torch.max(outputs, 1)
        accuracy = (predicted == y).float().mean().item()
    
    print(f"Final accuracy: {accuracy:.3f}")
    
    # Visualize learned features
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    weights = model.fc1.weight.data.numpy()
    im = ax.imshow(weights, cmap='RdBu_r', aspect='auto')
    ax.set_xlabel('Input Features')
    ax.set_ylabel('Hidden Units')
    ax.set_title('Learned Weights (First Layer)')
    fig.colorbar(im, ax=ax)
    scitex.io.save(os.path.join(output_dir, "figures", "pytorch_weights.png"), fig)
    
    return {'accuracy': accuracy, 'model': 'SimpleNet'}

def mne_integration_example(output_dir: str):
    """Demonstrate SciTeX with MNE-Python."""
    if not MNE_AVAILABLE:
        return None
        
    print("\n=== MNE-Python Integration ===")
    
    # Create synthetic EEG data
    n_channels = 64
    n_times = 1000
    sfreq = 250  # Hz
    
    # Generate synthetic EEG data
    times = np.arange(n_times) / sfreq
    data = np.random.randn(n_channels, n_times) * 1e-6  # Scale to microvolts
    
    # Add some signals
    for i in range(n_channels):
        # Add alpha rhythm (10 Hz) to some channels
        if i < 20:
            data[i] += 10e-6 * np.sin(2 * np.pi * 10 * times)
        # Add beta rhythm (20 Hz) to others
        elif i < 40:
            data[i] += 5e-6 * np.sin(2 * np.pi * 20 * times)
    
    # Create MNE info structure
    ch_names = [f'EEG{i+1:03d}' for i in range(n_channels)]
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
    
    # Create Raw object
    raw = mne.io.RawArray(data, info)
    
    # Apply SciTeX filtering
    filtered_data = scitex.dsp.filt.bandpass(data, fs=sfreq, bands=[[1, 40]])
    filtered_data = np.array(filtered_data).squeeze()
    
    # Compute PSD with SciTeX
    psd_values, freqs = scitex.dsp.psd(filtered_data[0], fs=sfreq)
    psd_values = np.array(psd_values).squeeze()
    freqs = np.array(freqs).squeeze()
    
    # Plot with SciTeX
    fig, axes = scitex.plt.subplots(2, 1, figsize=(10, 8))
    
    # Time series
    axes[0].plot(times[:250], data[0, :250] * 1e6, label='Original')
    axes[0].plot(times[:250], filtered_data[0, :250] * 1e6, label='Filtered')
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude (μV)')
    axes[0].set_title('EEG Signal Comparison')
    axes[0].legend()
    
    # PSD
    mask = freqs < 50
    axes[1].semilogy(freqs[mask], psd_values[mask])
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Power Spectral Density')
    axes[1].set_title('PSD of Filtered Signal')
    axes[1].grid(True, alpha=0.3)
    
    fig.tight_layout()
    scitex.io.save(os.path.join(output_dir, "figures", "mne_integration.png"), fig)
    
    # Save processed data
    processed_data = {
        'filtered': filtered_data,
        'sfreq': sfreq,
        'ch_names': ch_names,
        'info': {'n_channels': n_channels, 'duration': n_times/sfreq}
    }
    scitex.io.save(os.path.join(output_dir, "results", "mne_processed_data.pkl"), processed_data)
    
    return {'n_channels': n_channels, 'duration': n_times/sfreq}

def xarray_integration_example(output_dir: str):
    """Demonstrate SciTeX with xarray."""
    if not XARRAY_AVAILABLE:
        return None
        
    print("\n=== xarray Integration ===")
    
    # Create multi-dimensional dataset
    times = pd.date_range('2024-01-01', periods=100, freq='D')
    locations = ['Site_A', 'Site_B', 'Site_C']
    variables = ['temperature', 'humidity', 'pressure']
    
    # Generate synthetic environmental data
    data = np.random.randn(len(times), len(locations), len(variables))
    
    # Add trends
    for i, var in enumerate(variables):
        trend = np.linspace(0, 1, len(times))
        data[:, :, i] += trend[:, np.newaxis] * 5
    
    # Create xarray Dataset
    ds = xr.Dataset(
        {
            'measurements': (['time', 'location', 'variable'], data)
        },
        coords={
            'time': times,
            'location': locations,
            'variable': variables
        }
    )
    
    # Add attributes
    ds.attrs['description'] = 'Synthetic environmental monitoring data'
    ds.attrs['units'] = 'normalized'
    
    # Compute statistics
    daily_mean = ds.mean(dim='location')
    monthly_mean = ds.resample(time='M').mean()
    
    # Save with SciTeX
    scitex.io.save(os.path.join(output_dir, "results", "xarray_dataset.nc"), ds)
    
    # Visualize with SciTeX
    fig, axes = scitex.plt.subplots(1, 3, figsize=(15, 5))
    
    for i, var in enumerate(variables):
        ax = axes[i]
        
        # Plot time series for each location
        for loc in locations:
            data_slice = ds.sel(location=loc, variable=var)['measurements'].values
            ax.plot(times, data_slice, label=loc, alpha=0.7)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title(f'{var.capitalize()} Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotate x labels
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
    
    fig.tight_layout()
    scitex.io.save(os.path.join(output_dir, "figures", "xarray_timeseries.png"), fig)
    
    return {'n_times': len(times), 'n_locations': len(locations), 'n_variables': len(variables)}

def integration_with_custom_pipeline(output_dir: str):
    """Show how to integrate SciTeX into existing pipelines."""
    print("\n=== Custom Pipeline Integration ===")
    
    class DataProcessor:
        """Example of integrating SciTeX into a custom class."""
        
        def __init__(self, config_path=None):
            self.config = scitex.io.load(config_path) if config_path else {}
            self.results = []
            
        def process_batch(self, data_files):
            """Process multiple files with SciTeX I/O."""
            for file_path in data_files:
                # Load with SciTeX
                data = scitex.io.load(file_path)
                
                # Process
                if isinstance(data, np.ndarray):
                    result = self._process_array(data)
                elif isinstance(data, pd.DataFrame):
                    result = self._process_dataframe(data)
                else:
                    result = data
                    
                self.results.append(result)
                
            return self.results
            
        def _process_array(self, arr):
            """Process numpy arrays with SciTeX DSP."""
            if arr.ndim == 1:
                # Assume it's a signal
                filtered = scitex.dsp.filt.lowpass(arr, fs=1000, cutoffs_hz=50)
                return np.array(filtered).squeeze()
            return arr
            
        def _process_dataframe(self, df):
            """Process DataFrames with SciTeX pandas utilities."""
            # Example: find specific conditions
            if 'value' in df.columns:
                high_indices = scitex.pd.find_indi(df, conditions={'value': df[df['value'] > df['value'].mean()]['value'].tolist()})
                df['is_high'] = False
                df.loc[high_indices, 'is_high'] = True
            return df
            
        def save_results(self, output_path):
            """Save all results with SciTeX."""
            scitex.io.save(output_path, {
                'results': self.results,
                'config': self.config,
                'timestamp': pd.Timestamp.now()
            })
    
    # Example usage
    processor = DataProcessor()
    
    # Create test data
    test_files = []
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate test files
    for i in range(3):
        if i % 2 == 0:
            data = np.random.randn(1000)
        else:
            data = pd.DataFrame({'value': np.random.randn(100), 'id': range(100)})
        
        filepath = os.path.join(temp_dir, f'test_data_{i}.pkl')
        scitex.io.save(filepath, data)
        test_files.append(filepath)
    
    # Process
    results = processor.process_batch(test_files)
    processor.save_results(os.path.join(output_dir, "results", "pipeline_results.pkl"))
    
    print(f"Processed {len(results)} files")
    
    # Clean up
    for f in test_files:
        os.remove(f)
    
    return {'n_processed': len(results)}

def create_integration_report(results: dict, output_dir: str):
    """Generate integration summary report."""
    report = """# SciTeX Library Integration Report

## Overview

This report demonstrates SciTeX integration with popular scientific Python libraries.

## Integration Results

"""
    
    for lib_name, result in results.items():
        if result is None:
            report += f"\n### {lib_name}\n**Status**: Not available (library not installed)\n"
        else:
            report += f"\n### {lib_name}\n**Status**: ✅ Successfully integrated\n\n"
            report += "**Results**:\n"
            for key, value in result.items():
                report += f"- {key}: {value}\n"
    
    report += """

## Integration Patterns

### 1. Model Persistence
```python
# Save any model with SciTeX
scitex.io.save("./model.pkl", sklearn_model)
scitex.io.save("./model.pth", {'state_dict': torch_model.state_dict()})
```

### 2. Data Processing
```python
# Use SciTeX for preprocessing, then pass to any library
data = scitex.io.load("./data.npy")
filtered = scitex.dsp.filt.bandpass(data, fs, bands)
filtered_np = np.array(filtered).squeeze()

# Now use with any library
model.fit(filtered_np)
```

### 3. Visualization
```python
# Use SciTeX plotting with any results
fig, ax = scitex.plt.subplots()
# Plot results from any library
ax.plot(sklearn_predictions)
scitex.io.save("./figure.png", fig)
```

## Benefits

1. **Unified I/O**: Single interface for all file formats
2. **Consistent Logging**: All operations tracked
3. **Path Management**: Automatic directory creation
4. **Enhanced Plotting**: Built-in data export

## Recommendations

- Use SciTeX as a wrapper around existing workflows
- Leverage SciTeX for I/O and visualization
- Keep core computations in specialized libraries
- Use SciTeX for experiment management

## Conclusion

SciTeX integrates seamlessly with the scientific Python ecosystem, providing a consistent interface while leveraging the strengths of specialized libraries.
"""
    
    with open(os.path.join(output_dir, 'integration_report.md'), 'w') as f:
        f.write(report)

def main():
    # Initialize SciTeX
    CONFIG, sys_out, sys_err, plt, CC = scitex.gen.start(
        sys=sys,
        verbose=True
    )
    
    print("=== SciTeX Library Integration Examples ===")
    print(f"Experiment ID: {CONFIG.ID}")
    
    # Set output directory
    output_dir = os.path.join(os.getcwd(), "examples", "library_integration_out")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "models"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "results"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "figures"), exist_ok=True)
    
    # Run integration examples
    results = {}
    
    # Scikit-learn
    results['scikit-learn'] = sklearn_integration_example(output_dir)
    
    # PyTorch
    results['PyTorch'] = pytorch_integration_example(output_dir)
    
    # MNE-Python
    results['MNE-Python'] = mne_integration_example(output_dir)
    
    # xarray
    results['xarray'] = xarray_integration_example(output_dir)
    
    # Custom pipeline
    results['Custom Pipeline'] = integration_with_custom_pipeline(output_dir)
    
    # Generate report
    print("\n=== Generating Integration Report ===")
    create_integration_report(results, output_dir)
    
    # Summary
    print("\n=== Integration Summary ===")
    successful = sum(1 for r in results.values() if r is not None)
    print(f"Successfully integrated with {successful}/{len(results)} libraries")
    
    print(f"\nAll outputs saved to: {output_dir}")
    print("Check integration_report.md for details")
    
    # Close SciTeX
    scitex.gen.close(CONFIG)

if __name__ == "__main__":
    main()