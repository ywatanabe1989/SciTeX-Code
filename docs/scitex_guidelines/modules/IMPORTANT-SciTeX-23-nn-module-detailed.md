# SciTeX NN Module - Detailed Reference Guide

## Overview

The `scitex.nn` module provides specialized neural network layers and components for scientific computing, signal processing, and neuroscience applications. All components are PyTorch-compatible and can be integrated into standard PyTorch models.

## Module Structure

```
scitex/nn/
├── _AxiswiseDropout.py      # Dropout along specific axes
├── _BNet.py                 # Basic neural network
├── _BNet_Res.py            # Residual neural network
├── _ChannelGainChanger.py   # Channel-wise gain adjustment
├── _DropoutChannels.py      # Channel dropout
├── _Filters.py              # Signal filtering layers
├── _FreqGainChanger.py      # Frequency-specific gain
├── _GaussianFilter.py       # Gaussian smoothing
├── _Hilbert.py              # Hilbert transform layer
├── _MNet_1000.py           # 1000-class classification network
├── _ModulationIndex.py      # Phase-amplitude coupling
├── _PAC.py                  # Phase-amplitude coupling analysis
├── _PSD.py                  # Power spectral density
├── _ResNet1D.py            # 1D ResNet implementation
├── _SpatialAttention.py     # Spatial attention mechanism
├── _Spectrogram.py         # Spectrogram computation
├── _SwapChannels.py        # Channel swapping
├── _TransposeLayer.py      # Dimension transposition
└── _Wavelet.py             # Wavelet transform layer
```

## Core Components

### 1. Basic Networks

#### BNet - Basic Neural Network
```python
import scitex.nn
import torch.nn as nn

# Create basic network
model = scitex.nn.BNet(
    in_channels=64,
    out_channels=10,
    hidden_dims=[128, 64, 32],
    activation='relu',
    dropout=0.5
)

# Use in forward pass
output = model(input_tensor)
```

#### BNet_Res - Residual Network
```python
# Residual network with skip connections
model = scitex.nn.BNet_Res(
    in_channels=64,
    out_channels=10,
    hidden_dims=[128, 128, 64],
    n_res_blocks=3,
    activation='relu'
)
```

#### ResNet1D - 1D ResNet
```python
# 1D ResNet for time series
model = scitex.nn.ResNet1D(
    in_channels=32,
    num_classes=5,
    layers=[2, 2, 2, 2],  # ResNet-18 structure
    block_type='basic'
)
```

#### MNet1000 - Large-scale Classification
```python
# Pre-configured network for 1000 classes
model = scitex.nn.MNet1000(
    in_channels=3,
    pretrained=False
)
```

### 2. Signal Processing Layers

#### Filters - Digital Filtering
```python
# Learnable bandpass filter
filter_layer = scitex.nn.Filters(
    n_channels=64,
    sample_rate=1000,
    filter_type='bandpass',
    low_freq=1.0,
    high_freq=50.0,
    learnable=True
)

# Apply to signal
filtered = filter_layer(signal)
```

#### GaussianFilter - Gaussian Smoothing
```python
# Gaussian smoothing layer
smoother = scitex.nn.GaussianFilter(
    n_channels=32,
    sigma=2.0,
    kernel_size=11,
    learnable=False
)

smoothed = smoother(noisy_signal)
```

#### Hilbert - Hilbert Transform
```python
# Extract amplitude envelope
hilbert = scitex.nn.Hilbert(
    n_channels=64,
    axis=-1  # Time axis
)

analytic_signal = hilbert(signal)
amplitude = analytic_signal.abs()
phase = analytic_signal.angle()
```

### 3. Frequency Analysis Layers

#### PSD - Power Spectral Density
```python
# Compute PSD in neural network
psd_layer = scitex.nn.PSD(
    n_channels=32,
    n_fft=256,
    sample_rate=1000,
    window='hann',
    return_db=True
)

power_spectrum = psd_layer(signal)
```

#### Spectrogram - Time-Frequency Analysis
```python
# Spectrogram computation
spectrogram = scitex.nn.Spectrogram(
    n_channels=16,
    n_fft=512,
    hop_length=128,
    window='hamming',
    return_db=True
)

time_freq = spectrogram(signal)
```

#### Wavelet - Wavelet Transform
```python
# Continuous wavelet transform
wavelet = scitex.nn.Wavelet(
    n_channels=32,
    wavelet='morlet',
    scales=torch.logspace(-1, 2, 50),
    sample_rate=1000
)

wavelet_coeffs = wavelet(signal)
```

### 4. Neuroscience-Specific Layers

#### PAC - Phase-Amplitude Coupling
```python
# Analyze cross-frequency coupling
pac_layer = scitex.nn.PAC(
    n_channels=64,
    sample_rate=1000,
    low_freq_range=(4, 8),   # Theta
    high_freq_range=(30, 50), # Gamma
    method='tort'
)

coupling_strength = pac_layer(signal)
```

#### ModulationIndex - Modulation Strength
```python
# Compute modulation index
mi_layer = scitex.nn.ModulationIndex(
    n_channels=32,
    sample_rate=1000,
    phase_freq_range=(6, 10),
    amp_freq_range=(60, 80)
)

modulation_index = mi_layer(signal)
```

### 5. Data Augmentation Layers

#### AxiswiseDropout - Selective Dropout
```python
# Dropout along specific dimensions
dropout = scitex.nn.AxiswiseDropout(
    p=0.5,
    axis=1  # Drop along channel axis
)

augmented = dropout(data)
```

#### DropoutChannels - Channel Dropout
```python
# Randomly drop entire channels
channel_dropout = scitex.nn.DropoutChannels(
    p=0.3,
    n_channels=64
)

dropped = channel_dropout(data)
```

#### SwapChannels - Channel Permutation
```python
# Randomly swap channel pairs
swapper = scitex.nn.SwapChannels(
    n_channels=32,
    p=0.5  # Probability of swapping
)

swapped = swapper(data)
```

#### ChannelGainChanger - Amplitude Modulation
```python
# Random gain changes per channel
gain_changer = scitex.nn.ChannelGainChanger(
    n_channels=64,
    gain_range=(0.8, 1.2),
    p=0.5
)

augmented = gain_changer(data)
```

#### FreqGainChanger - Frequency-specific Gain
```python
# Modify specific frequency bands
freq_gain = scitex.nn.FreqGainChanger(
    n_channels=32,
    sample_rate=1000,
    freq_bands=[(8, 12), (20, 30)],
    gain_ranges=[(0.5, 1.5), (0.8, 1.2)]
)

modified = freq_gain(signal)
```

### 6. Attention Mechanisms

#### SpatialAttention - Spatial Focus
```python
# Spatial attention for multichannel data
attention = scitex.nn.SpatialAttention(
    n_channels=64,
    reduction_ratio=8
)

attended = attention(features)
```

### 7. Utility Layers

#### TransposeLayer - Dimension Permutation
```python
# Transpose dimensions in network
transpose = scitex.nn.TransposeLayer(
    dims=(0, 2, 1)  # (batch, time, channel) -> (batch, channel, time)
)

transposed = transpose(data)
```

## Complete Examples

### Example 1: EEG Classification Network
```python
import torch.nn as nn
import scitex.nn

class EEGClassifier(nn.Module):
    def __init__(self, n_channels=64, n_classes=4, sample_rate=250):
        super().__init__()
        
        # Preprocessing
        self.filters = scitex.nn.Filters(
            n_channels=n_channels,
            sample_rate=sample_rate,
            filter_type='bandpass',
            low_freq=0.5,
            high_freq=45.0
        )
        
        # Feature extraction
        self.psd = scitex.nn.PSD(
            n_channels=n_channels,
            n_fft=512,
            sample_rate=sample_rate
        )
        
        # Attention
        self.attention = scitex.nn.SpatialAttention(
            n_channels=n_channels
        )
        
        # Classification
        self.classifier = scitex.nn.BNet(
            in_channels=n_channels * 257,  # PSD bins
            out_channels=n_classes,
            hidden_dims=[512, 256, 128]
        )
        
    def forward(self, x):
        # x shape: (batch, channels, time)
        x = self.filters(x)
        x = self.psd(x)
        x = self.attention(x)
        x = x.flatten(1)
        x = self.classifier(x)
        return x

# Usage
model = EEGClassifier()
output = model(eeg_data)
```

### Example 2: Signal Processing Pipeline
```python
class SignalProcessor(nn.Module):
    def __init__(self, n_channels=32):
        super().__init__()
        
        # Augmentation
        self.augment = nn.Sequential(
            scitex.nn.ChannelGainChanger(n_channels, gain_range=(0.9, 1.1)),
            scitex.nn.DropoutChannels(p=0.1, n_channels=n_channels)
        )
        
        # Analysis
        self.hilbert = scitex.nn.Hilbert(n_channels)
        self.pac = scitex.nn.PAC(
            n_channels=n_channels,
            sample_rate=1000,
            low_freq_range=(4, 8),
            high_freq_range=(30, 50)
        )
        
        # Output network
        self.output = scitex.nn.BNet_Res(
            in_channels=n_channels * 2,  # Amplitude + PAC
            out_channels=1,
            hidden_dims=[64, 32, 16]
        )
        
    def forward(self, x):
        # Augmentation (training only)
        if self.training:
            x = self.augment(x)
        
        # Extract features
        analytic = self.hilbert(x)
        amplitude = analytic.abs()
        pac = self.pac(x)
        
        # Combine features
        features = torch.cat([amplitude.mean(dim=-1), pac], dim=1)
        
        # Predict
        output = self.output(features)
        return output
```

### Example 3: Multi-scale Analysis
```python
class MultiScaleAnalyzer(nn.Module):
    def __init__(self, n_channels=16):
        super().__init__()
        
        # Multiple frequency bands
        self.filters = nn.ModuleList([
            scitex.nn.Filters(n_channels, 1000, 'bandpass', 1, 4),    # Delta
            scitex.nn.Filters(n_channels, 1000, 'bandpass', 4, 8),    # Theta
            scitex.nn.Filters(n_channels, 1000, 'bandpass', 8, 13),   # Alpha
            scitex.nn.Filters(n_channels, 1000, 'bandpass', 13, 30),  # Beta
            scitex.nn.Filters(n_channels, 1000, 'bandpass', 30, 100)  # Gamma
        ])
        
        # Wavelet analysis
        self.wavelet = scitex.nn.Wavelet(
            n_channels=n_channels,
            wavelet='morlet',
            sample_rate=1000
        )
        
        # Combine features
        self.combiner = scitex.nn.BNet(
            in_channels=n_channels * (5 + 50),  # 5 bands + 50 wavelet scales
            out_channels=128,
            hidden_dims=[256, 128]
        )
        
    def forward(self, x):
        # Filter into bands
        band_features = []
        for filt in self.filters:
            filtered = filt(x)
            power = (filtered ** 2).mean(dim=-1)
            band_features.append(power)
        
        # Wavelet features
        wavelet_coefs = self.wavelet(x)
        wavelet_power = (wavelet_coefs.abs() ** 2).mean(dim=-1)
        
        # Combine all features
        all_features = torch.cat(band_features + [wavelet_power], dim=1)
        output = self.combiner(all_features)
        
        return output
```

## Integration with PyTorch

All SciTeX neural network components are standard PyTorch modules and can be freely mixed with PyTorch layers:

```python
import torch.nn as nn
import scitex.nn

model = nn.Sequential(
    # SciTeX preprocessing
    scitex.nn.Filters(32, 1000, 'bandpass', 1, 50),
    scitex.nn.GaussianFilter(32, sigma=1.0),
    
    # Standard PyTorch layers
    nn.Conv1d(32, 64, kernel_size=5),
    nn.ReLU(),
    nn.MaxPool1d(2),
    
    # SciTeX analysis
    scitex.nn.PSD(64, n_fft=256, sample_rate=1000),
    
    # More PyTorch layers
    nn.Flatten(),
    nn.Linear(64 * 129, 10),
    nn.Softmax(dim=1)
)
```

## Performance Considerations

1. **GPU Acceleration**: All layers support GPU computation
   ```python
   model = scitex.nn.BNet(64, 10).cuda()
   output = model(input_tensor.cuda())
   ```

2. **Batch Processing**: All layers handle batched inputs efficiently
   ```python
   # Input shape: (batch_size, n_channels, n_samples)
   batch_output = model(batch_input)
   ```

3. **Memory Efficiency**: For large signals, use chunking:
   ```python
   # Process in chunks for memory efficiency
   chunk_size = 10000
   outputs = []
   for i in range(0, signal.shape[-1], chunk_size):
       chunk = signal[..., i:i+chunk_size]
       outputs.append(model(chunk))
   result = torch.cat(outputs, dim=-1)
   ```

## Common Issues and Solutions

1. **Dimension Mismatch**
   ```python
   # Ensure correct input dimensions
   # Expected: (batch, channels, time)
   if len(input.shape) == 2:
       input = input.unsqueeze(0)  # Add batch dimension
   ```

2. **Sample Rate Consistency**
   ```python
   # Ensure all frequency-based layers use same sample rate
   sample_rate = 1000
   model = nn.Sequential(
       scitex.nn.Filters(32, sample_rate, 'bandpass', 1, 50),
       scitex.nn.PSD(32, 256, sample_rate),  # Same sample_rate
       scitex.nn.PAC(32, sample_rate, (4, 8), (30, 50))  # Same sample_rate
   )
   ```

3. **Numerical Stability**
   ```python
   # For very small signals, add epsilon
   psd_layer = scitex.nn.PSD(
       n_channels=32,
       n_fft=256,
       sample_rate=1000,
       return_db=True,
       epsilon=1e-10  # Prevent log(0)
   )
   ```

## See Also

- `scitex.ai` - AI and machine learning utilities
- `scitex.dsp` - Digital signal processing functions
- `torch.nn` - PyTorch neural network modules
- `scitex.plt` - Visualization tools