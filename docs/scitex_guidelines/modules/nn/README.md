# scitex.nn Module Documentation

## Overview

The `scitex.nn` module provides specialized neural network layers and modules for PyTorch, with a focus on signal processing, neuroscience applications, and advanced deep learning architectures. It includes custom layers for time-series analysis, frequency domain operations, and attention mechanisms.

## Module Components

### 1. Network Architectures

#### BNet (Brain Network)
A specialized neural network architecture designed for brain signal analysis.

```python
import scitex.nn

# Create BNet with configuration
config = scitex.nn.BNet_config(
    input_channels=64,
    output_classes=4,
    hidden_dim=128
)

model = scitex.nn.BNet(config)

# Forward pass
output = model(eeg_data)  # Shape: [batch, channels, time]
```

#### MNet_1000
A deep network with 1000 layers for complex pattern recognition.

```python
config = scitex.nn.MNet_config(
    input_dim=256,
    output_dim=10,
    dropout_rate=0.5
)

model = scitex.nn.MNet_1000(config)
```

#### ResNet1D
1D ResNet for time-series and sequence data.

```python
# Create 1D ResNet
resnet = scitex.nn.ResNet1D(
    in_channels=1,
    num_classes=10,
    layers=[2, 2, 2, 2]  # ResNet-18 configuration
)

# For time-series classification
time_series = torch.randn(32, 1, 1000)  # [batch, channels, time]
output = resnet(time_series)
```

### 2. Signal Processing Layers

#### Filters
Various digital filters implemented as PyTorch layers.

```python
# Low-pass filter
lpf = scitex.nn.LowPassFilter(
    sampling_rate=1000,
    cutoff_freq=50,
    order=4
)

# Band-pass filter
bpf = scitex.nn.BandPassFilter(
    sampling_rate=1000,
    low_freq=8,
    high_freq=12,
    order=4
)

# Differentiable band-pass filter (trainable)
dbpf = scitex.nn.DifferentiableBandPassFilter(
    sampling_rate=1000,
    initial_low=8,
    initial_high=12
)

# Apply filters
filtered_signal = lpf(raw_signal)
alpha_band = bpf(eeg_signal)
```

#### Hilbert Transform
Extract instantaneous phase and amplitude.

```python
hilbert = scitex.nn.Hilbert()

# Get analytical signal
phase, amplitude = hilbert(signal)
```

#### Wavelet Transform
Continuous wavelet transform layer.

```python
wavelet = scitex.nn.Wavelet(
    wavelet_type='morlet',
    scales=torch.logspace(-1, 2, 50),
    sampling_rate=1000
)

# Get time-frequency representation
tfr = wavelet(signal)  # Shape: [batch, scales, time]
```

#### Spectrogram
Compute spectrograms as a neural network layer.

```python
spectrogram = scitex.nn.Spectrogram(
    n_fft=256,
    hop_length=128,
    window='hann'
)

# Get power spectrogram
spec = spectrogram(audio_signal)
```

### 3. Neuroscience-Specific Layers

#### PSD (Power Spectral Density)
Compute PSD features within the network.

```python
psd_layer = scitex.nn.PSD(
    sampling_rate=1000,
    fft_length=1024,
    overlap=0.5
)

psd_features = psd_layer(neural_signal)
```

#### PAC (Phase-Amplitude Coupling)
Analyze cross-frequency coupling.

```python
pac = scitex.nn.PAC(
    phase_freq_range=(4, 8),    # Theta
    amplitude_freq_range=(30, 50),  # Gamma
    sampling_rate=1000
)

coupling_strength = pac(signal)
```

#### ModulationIndex
Calculate modulation index for neural oscillations.

```python
mi = scitex.nn.ModulationIndex(
    n_bins=18,
    method='kullback-leibler'
)

modulation_index = mi(phase, amplitude)
```

### 4. Regularization and Augmentation Layers

#### AxiswiseDropout
Apply dropout along specific axes.

```python
# Dropout along time axis
time_dropout = scitex.nn.AxiswiseDropout(
    p=0.5,
    axis=2  # Time axis
)

# Dropout along channel axis
channel_dropout = scitex.nn.AxiswiseDropout(
    p=0.3,
    axis=1  # Channel axis
)
```

#### DropoutChannels
Randomly drop entire channels during training.

```python
dropout_channels = scitex.nn.DropoutChannels(
    p=0.2,
    channel_last=False
)

# Drops entire channels
augmented = dropout_channels(multi_channel_data)
```

#### ChannelGainChanger
Randomly scale channel gains for augmentation.

```python
gain_changer = scitex.nn.ChannelGainChanger(
    gain_range=(0.8, 1.2),
    channel_wise=True
)

augmented_signal = gain_changer(signal)
```

#### FreqGainChanger
Modify gains in frequency domain.

```python
freq_augment = scitex.nn.FreqGainChanger(
    freq_bands=[(8, 12), (13, 30)],
    gain_ranges=[(0.9, 1.1), (0.8, 1.2)]
)

augmented = freq_augment(signal)
```

### 5. Utility Layers

#### SwapChannels
Randomly swap channels for augmentation.

```python
swap = scitex.nn.SwapChannels(p=0.5)
swapped_data = swap(multi_channel_data)
```

#### TransposeLayer
Transpose tensor dimensions.

```python
# Transpose from [batch, time, channels] to [batch, channels, time]
transpose = scitex.nn.TransposeLayer(dims=(0, 2, 1))
transposed = transpose(data)
```

#### SpatialAttention
Spatial attention mechanism for multi-channel data.

```python
attention = scitex.nn.SpatialAttention(
    in_channels=64,
    reduction_ratio=8
)

# Apply spatial attention
attended_features = attention(spatial_features)
```

## Common Workflows

### 1. EEG/MEG Analysis Pipeline

```python
import torch
import scitex.nn

class EEGAnalysisNet(torch.nn.Module):
    def __init__(self, n_channels=64, n_classes=4):
        super().__init__()
        
        # Preprocessing
        self.bandpass = scitex.nn.BandPassFilter(
            sampling_rate=1000,
            low_freq=1,
            high_freq=40
        )
        
        # Feature extraction
        self.psd = scitex.nn.PSD(sampling_rate=1000)
        self.pac = scitex.nn.PAC(
            phase_freq_range=(4, 8),
            amplitude_freq_range=(30, 50),
            sampling_rate=1000
        )
        
        # Spatial attention
        self.spatial_att = scitex.nn.SpatialAttention(n_channels)
        
        # Classification
        self.classifier = torch.nn.Linear(n_channels * 2, n_classes)
        
    def forward(self, x):
        # Filter signal
        x = self.bandpass(x)
        
        # Extract features
        psd_features = self.psd(x)
        pac_features = self.pac(x)
        
        # Concatenate features
        features = torch.cat([psd_features, pac_features], dim=1)
        
        # Apply attention
        features = self.spatial_att(features)
        
        # Classify
        return self.classifier(features.flatten(1))
```

### 2. Time-Frequency Analysis Network

```python
class TimeFreqNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        
        # Time-frequency representations
        self.wavelet = scitex.nn.Wavelet(
            wavelet_type='morlet',
            scales=torch.logspace(-1, 2, 50)
        )
        
        self.spectrogram = scitex.nn.Spectrogram(
            n_fft=256,
            hop_length=128
        )
        
        # Feature extraction
        self.conv1 = torch.nn.Conv2d(2, 32, kernel_size=3)
        self.conv2 = torch.nn.Conv2d(32, 64, kernel_size=3)
        self.pool = torch.nn.AdaptiveAvgPool2d((8, 8))
        
        self.fc = torch.nn.Linear(64 * 8 * 8, 10)
        
    def forward(self, x):
        # Get time-frequency representations
        wavelet_tfr = self.wavelet(x).unsqueeze(1)
        spec_tfr = self.spectrogram(x).unsqueeze(1)
        
        # Concatenate
        tfr = torch.cat([wavelet_tfr, spec_tfr], dim=1)
        
        # Extract features
        x = torch.relu(self.conv1(tfr))
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        
        return self.fc(x.flatten(1))
```

### 3. Signal Augmentation Pipeline

```python
class SignalAugmentation(torch.nn.Module):
    def __init__(self, training=True):
        super().__init__()
        self.training = training
        
        # Augmentation layers
        self.time_dropout = scitex.nn.AxiswiseDropout(p=0.2, axis=2)
        self.channel_dropout = scitex.nn.DropoutChannels(p=0.1)
        self.channel_gain = scitex.nn.ChannelGainChanger(
            gain_range=(0.8, 1.2)
        )
        self.freq_gain = scitex.nn.FreqGainChanger(
            freq_bands=[(1, 4), (4, 8), (8, 12), (13, 30)],
            gain_ranges=[(0.9, 1.1)] * 4
        )
        self.swap_channels = scitex.nn.SwapChannels(p=0.3)
        
    def forward(self, x):
        if self.training:
            x = self.time_dropout(x)
            x = self.channel_dropout(x)
            x = self.channel_gain(x)
            x = self.freq_gain(x)
            x = self.swap_channels(x)
        return x
```

## Best Practices

### 1. Signal Preprocessing
Always preprocess signals appropriately:
```python
# Remove DC offset
signal = signal - signal.mean(dim=-1, keepdim=True)

# Normalize
signal = signal / signal.std(dim=-1, keepdim=True)

# Apply filters
filtered = bandpass_filter(signal)
```

### 2. Handling Different Sampling Rates
Many layers require sampling rate specification:
```python
# Ensure consistent sampling rates
SAMPLING_RATE = 1000  # Hz

psd = scitex.nn.PSD(sampling_rate=SAMPLING_RATE)
pac = scitex.nn.PAC(sampling_rate=SAMPLING_RATE)
filters = scitex.nn.BandPassFilter(sampling_rate=SAMPLING_RATE)
```

### 3. GPU Memory Management
For long time-series:
```python
# Process in chunks
chunk_size = 10000
outputs = []

for i in range(0, signal.shape[-1], chunk_size):
    chunk = signal[..., i:i+chunk_size]
    output = model(chunk)
    outputs.append(output)

final_output = torch.cat(outputs, dim=-1)
```

### 4. Numerical Stability
Use appropriate data types:
```python
# Use float32 for most applications
signal = signal.float()

# Use float64 for high-precision requirements
signal = signal.double()
```

## Integration with Other SciTeX Modules

### With scitex.dsp
```python
import scitex.dsp
import scitex.nn

# Preprocess with DSP module
signal = scitex.dsp.norm(raw_signal)
signal = scitex.dsp.filt.bandpass(signal, low=1, high=40, fs=1000)

# Then use NN layers
psd_features = scitex.nn.PSD(sampling_rate=1000)(signal)
```

### With scitex.ai
```python
# Use with classification reporter
from scitex.ai import ClassificationReporter

model = EEGAnalysisNet()
reporter = ClassificationReporter()

# Train and evaluate
predictions = model(test_data)
metrics = reporter.evaluate(y_true, predictions)
```

## Troubleshooting

### Common Issues

1. **Dimension Mismatch**
   ```python
   # Check expected input dimensions
   print(f"Expected: [batch, channels, time]")
   print(f"Got: {input_tensor.shape}")
   ```

2. **Filter Instability**
   - Use appropriate filter orders
   - Check Nyquist frequency constraints
   - Consider using SOS (Second-Order Sections) format

3. **Memory Issues with Long Sequences**
   - Use gradient checkpointing
   - Process in smaller chunks
   - Reduce model complexity

### Debug Mode
Enable detailed logging:
```python
from scitex import logging
logging.getLogger('scitex.nn').setLevel(logging.DEBUG)
```

## References

- [PyTorch Documentation](https://pytorch.org/docs/)
- [Digital Signal Processing Guide](http://www.dspguide.com/)
- [Neuroscience Signal Processing](https://www.sciencedirect.com/topics/neuroscience/signal-processing)
- [Time-Frequency Analysis Methods](https://en.wikipedia.org/wiki/Time%E2%80%93frequency_analysis)