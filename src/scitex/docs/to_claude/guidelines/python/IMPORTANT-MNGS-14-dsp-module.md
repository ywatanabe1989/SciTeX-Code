<!-- ---
!-- Timestamp: 2025-05-29 20:33:25
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/MNGS-14-mngs-dsp-module.md
!-- --- -->

## `mngs.dsp`

- `mngs.dsp` is a module for digital signal processing

### `mngs.dsp` Module (Digital Signal Processing)

#### Signal Processing Functions

```python
# Filtering
filtered = mngs.dsp.filt.bandpass(signal, fs=1000, f_range=[8, 12])
filtered = mngs.dsp.filt.lowpass(signal, fs=1000, f_cutoff=30)

# Transforms
envelope = mngs.dsp.hilbert(signal, get='envelope')
phase = mngs.dsp.hilbert(signal, get='phase')
wavelet_output = mngs.dsp.wavelet(signal, fs=1000)

# Analysis
freqs, psd = mngs.dsp.psd(signal, fs=1000)
mi = mngs.dsp.pac(signal, fs=1000, f_phase=[2, 6], f_amp=[30, 90])
```

## Example: Signal Processing

```python
import numpy as np
import mngs

# Generate test signal (10 Hz sine wave with 1000 Hz sampling rate)
fs = 1000  # Sampling frequency in Hz
t = np.arange(0, 1, 1/fs)  # 1 second of data
signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz sine wave

# Apply bandpass filter
filtered_signal = mngs.dsp.filt.bandpass(signal, fs=fs, f_range=[8, 12])

# Calculate power spectral density
freqs, psd = mngs.dsp.psd(filtered_signal, fs=fs)

# Extract signal envelope
envelope = mngs.dsp.hilbert(filtered_signal, get='envelope')

# Plot results
fig, axes = mngs.plt.subplots(nrows=3, ncols=1, figsize=(10, 8))

# Plot signals
axes[0].plot(t[:500], signal[:500], label='Original')
axes[0].plot(t[:500], filtered_signal[:500], label='Filtered (8-12 Hz)')
axes[0].set_xyt('Time (s)', 'Amplitude', 'Time Domain')
axes[0].legend()

# Plot PSD
axes[1].plot(freqs, psd)
axes[1].set_xyt('Frequency (Hz)', 'Power/Frequency (dB/Hz)', 'Frequency Domain')
axes[1].set_xlim(0, 50)  # Display up to 50 Hz

# Plot envelope
axes[2].plot(t[:500], filtered_signal[:500], label='Filtered')
axes[2].plot(t[:500], envelope[:500], label='Envelope')
axes[2].set_xyt('Time (s)', 'Amplitude', 'Signal Envelope')
axes[2].legend()

# Save figure with automatic CSV export
mngs.io.save(fig, './data/figures/signal_analysis.png', symlink_from_cwd=True)
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->