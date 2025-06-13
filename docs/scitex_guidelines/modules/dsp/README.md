# SciTeX DSP Module Documentation

## Overview

The `scitex.dsp` module provides comprehensive digital signal processing tools for scientific computing, with a focus on neural signal analysis. It includes filtering, spectral analysis, time-frequency decomposition, and specialized tools for neuroscience applications.

## Key Features

- **Signal Generation**: Demo signals for testing and development
- **Filtering**: Comprehensive filtering suite (bandpass, lowpass, highpass, Gaussian)
- **Spectral Analysis**: Power spectral density, Hilbert transform, wavelet analysis
- **Neural Analysis**: Ripple detection, phase-amplitude coupling, modulation index
- **Data Transformation**: Resampling, segmentation, format conversion

## Core Functions

### Signal Generation

#### `demo_sig()`
Generates demonstration signals for testing and development.

```python
import scitex.dsp

# Generate Gaussian noise
signal = scitex.dsp.demo_sig(
    sig_type="gauss",
    n_chs=32,
    samp_rate=1000,
    T_sec=10,
    batch_size=1
)
# Returns: (1, 32, 10000) tensor

# Generate periodic signal with specific frequencies
signal = scitex.dsp.demo_sig(
    sig_type="periodic", 
    freqs=[10, 20, 50],  # Hz
    n_chs=4,
    samp_rate=1000,
    T_sec=5
)

# Generate chirp signal (frequency sweep)
signal = scitex.dsp.demo_sig(
    sig_type="chirp",
    low_freq=1,
    high_freq=100,
    samp_rate=1000
)
```

### Filtering

#### `filt.bandpass()`
Apply bandpass filter to extract specific frequency bands.

```python
# Extract alpha band (8-12 Hz)
alpha_signal = scitex.dsp.filt.bandpass(
    signal,
    samp_rate=1000,
    bands=[[8, 12]]
)

# Extract multiple bands simultaneously
bands = [[1, 4], [4, 8], [8, 12], [12, 30], [30, 100]]  # Delta to gamma
filtered = scitex.dsp.filt.bandpass(signal, samp_rate, bands)
```

#### `filt.lowpass()` / `filt.highpass()`
Apply low-pass or high-pass filtering.

```python
# Remove high frequency noise
clean_signal = scitex.dsp.filt.lowpass(signal, samp_rate=1000, cutoff=100)

# Remove low frequency drift
detrended = scitex.dsp.filt.highpass(signal, samp_rate=1000, cutoff=0.5)
```

#### `filt.gauss()`
Apply Gaussian smoothing filter.

```python
# Smooth signal with 50ms window
smoothed = scitex.dsp.filt.gauss(signal, samp_rate=1000, sigma_ms=50)
```

### Spectral Analysis

#### `psd()`
Compute power spectral density.

```python
# Calculate PSD
power, freqs = scitex.dsp.psd(signal, samp_rate=1000)

# Get normalized probability distribution
power_prob, freqs = scitex.dsp.psd(signal, samp_rate=1000, prob=True)
```

#### `hilbert()`
Extract instantaneous phase and amplitude via Hilbert transform.

```python
# Get analytic signal components
phase, amplitude = scitex.dsp.hilbert(signal)

# Phase: instantaneous phase in radians (-π to π)
# Amplitude: instantaneous amplitude envelope
```

#### `wavelet()`
Perform wavelet decomposition for time-frequency analysis.

```python
# Morlet wavelet transform
tfr = scitex.dsp.wavelet(
    signal,
    samp_rate=1000,
    freqs=np.logspace(0, 2, 50),  # 1-100 Hz
    n_cycles=7
)
# Returns: (batch, channels, frequencies, time)
```

### Neural Signal Analysis

#### `detect_ripples()`
Detect sharp-wave ripples in neural recordings.

```python
# Detect ripples in hippocampal recordings
ripples = scitex.dsp.detect_ripples(
    lfp_signal,
    samp_rate=1000,
    freq_band=[80, 250],
    threshold_sd=3.0
)
# Returns: List of ripple events with timing and properties
```

#### `pac()`
Analyze phase-amplitude coupling between frequency bands.

```python
# Analyze theta-gamma coupling
pac_value = scitex.dsp.pac(
    signal,
    samp_rate=1000,
    fp=[4, 8],    # Phase frequency (theta)
    fa=[30, 100]  # Amplitude frequency (gamma)
)
```

#### `modulation_index()`
Calculate modulation index for phase-amplitude coupling.

```python
# Quantify coupling strength
mi = scitex.dsp.modulation_index(
    signal,
    samp_rate=1000,
    phase_band=[4, 8],
    amp_band=[30, 100]
)
```

### Signal Transformation

#### `resample()`
Change sampling rate of signals.

```python
# Downsample from 1000 Hz to 250 Hz
downsampled = scitex.dsp.resample(
    signal,
    orig_samp_rate=1000,
    targ_samp_rate=250
)

# Upsample with time vector
upsampled, new_time = scitex.dsp.resample(
    signal,
    orig_samp_rate=250,
    targ_samp_rate=1000,
    time=original_time
)
```

#### `to_segments()`
Segment continuous signals into epochs.

```python
# Create 2-second segments with 50% overlap
segments = scitex.dsp.to_segments(
    signal,
    segment_length=2000,  # samples
    overlap=0.5
)
```

#### `crop()`
Extract specific time windows from signals.

```python
# Extract 5-10 second window
cropped = scitex.dsp.crop(
    signal,
    samp_rate=1000,
    start_sec=5,
    end_sec=10
)
```

## Common Workflows

### 1. Preprocessing Pipeline
```python
# Load signal
signal = scitex.io.load("raw_signal.npy")
samp_rate = 1000

# Remove drift
signal = scitex.dsp.filt.highpass(signal, samp_rate, cutoff=0.5)

# Remove line noise
signal = scitex.dsp.filt.bandstop(signal, samp_rate, bands=[[48, 52], [98, 102]])

# Extract frequency bands
bands = {
    'delta': [1, 4],
    'theta': [4, 8], 
    'alpha': [8, 12],
    'beta': [12, 30],
    'gamma': [30, 100]
}

band_signals = {}
for name, band in bands.items():
    band_signals[name] = scitex.dsp.filt.bandpass(signal, samp_rate, [band])
```

### 2. Spectral Analysis
```python
# Time-frequency decomposition
freqs = np.logspace(0, 2, 100)  # 1-100 Hz
tfr = scitex.dsp.wavelet(signal, samp_rate, freqs)

# Average power spectrum
power, freq_axis = scitex.dsp.psd(signal, samp_rate)

# Plot results
fig, axes = plt.subplots(2, 1)
axes[0].imshow(tfr[0, 0], aspect='auto', origin='lower')
axes[0].set_title("Time-Frequency Representation")
axes[1].loglog(freq_axis, power[0, 0])
axes[1].set_title("Power Spectral Density")
```

### 3. Phase-Amplitude Coupling Analysis
```python
# Analyze coupling between theta phase and gamma amplitude
phase_signal = scitex.dsp.filt.bandpass(signal, samp_rate, [[4, 8]])
amp_signal = scitex.dsp.filt.bandpass(signal, samp_rate, [[30, 100]])

# Extract phase and amplitude
theta_phase, _ = scitex.dsp.hilbert(phase_signal)
_, gamma_amp = scitex.dsp.hilbert(amp_signal)

# Calculate coupling
pac_strength = scitex.dsp.pac(signal, samp_rate, fp=[4, 8], fa=[30, 100])
mi = scitex.dsp.modulation_index(signal, samp_rate, [4, 8], [30, 100])
```

## Integration with Other SciTeX Modules

### With scitex.plt for Visualization
```python
# Create publication-ready spectrograms
fig, ax = scitex.plt.subplots()
tfr = scitex.dsp.wavelet(signal, samp_rate, freqs)
im = ax.imshow(np.log10(tfr[0, 0]), aspect='auto')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Frequency (Hz)")
fig.colorbar(im, label="Power (log10)")
fig.save("spectrogram.png")
```

### With scitex.io for Data Management
```python
# Process and save results
results = {
    'raw': signal,
    'filtered': filtered_signal,
    'psd': (power, freqs),
    'pac': pac_values,
    'params': {
        'samp_rate': samp_rate,
        'filter_bands': bands
    }
}
scitex.io.save(results, "analysis_results.pkl")
```

## Best Practices

1. **Always specify sampling rate**: Most DSP functions require `samp_rate` parameter
2. **Check signal dimensions**: Expected format is `(batch, channels, time)`
3. **Use appropriate filter orders**: Higher orders give sharper cutoffs but may introduce artifacts
4. **Validate frequency parameters**: Ensure frequencies are below Nyquist (samp_rate/2)
5. **Handle edge effects**: Consider padding or windowing for short signals

## Troubleshooting

### Common Issues

**Issue**: `RuntimeError: Expected 3D tensor`
```python
# Solution: Ensure signal has correct dimensions
signal = signal.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
```

**Issue**: Filter produces NaN values
```python
# Solution: Check for appropriate filter parameters
# Cutoff frequency should be < samp_rate/2
# Band limits should be [low, high] with low < high
```

**Issue**: Memory error with large signals
```python
# Solution: Process in chunks
chunk_size = 10000
results = []
for i in range(0, signal.shape[-1], chunk_size):
    chunk = signal[..., i:i+chunk_size]
    results.append(process_chunk(chunk))
```

## API Reference

For detailed API documentation, see the individual function docstrings or the Sphinx-generated documentation.

## See Also

- `scitex.ai` - For machine learning with signal features
- `scitex.plt` - For signal visualization
- `scitex.stats` - For statistical analysis of signal properties