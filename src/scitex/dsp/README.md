<!-- ---
!-- title: ./scitex_repo/src/scitex/dsp/README.md
!-- author: ywatanabe
!-- date: 2024-11-08 09:20:11
!-- --- -->


# [`scitex.dsp`](https://github.com/ywatanabe1989/scitex/tree/main/src/scitex/dsp/)

## Overview
The `scitex.dsp` module provides Digital Signal Processing (DSP) utilities written in **PyTorch**, optimized for **CUDA** devices when available. This module offers efficient implementations of various DSP algorithms and techniques.

## Installation
```bash
pip install scitex
```

## Features
- PyTorch-based implementations for GPU acceleration
- Wavelet transforms and analysis
- Filtering operations (e.g., bandpass, lowpass, highpass)
- Spectral analysis tools
- Time-frequency analysis utilities
- Signal generation and manipulation functions
- Phase-Amplitude Coupling (PAC) analysis
- Modulation Index calculation
- Hilbert transform
- Power Spectral Density (PSD) estimation
- Resampling utilities

## Galleries
<div style="display: flex; justify-content: center; flex-wrap: wrap;">
  <img src="./_demo_sig/traces.png" height="300" style="border: 2px solid gray; margin: 5px;">
  <img src="./_resample/traces.png" height="300" style="border: 2px solid gray; margin: 5px;">
  <img src="./filt/traces.png" height="300" style="border: 2px solid gray; margin: 5px;">
  <img src="./filt/psd.png" height="300" style="border: 2px solid gray; margin: 5px;">
</div>

<div style="display: flex; justify-content: center; flex-wrap: wrap;">
  <img src="./_wavelet/wavelet.png" height="300" style="border: 2px solid gray; margin: 5px;">
  <img src="./_hilbert/traces.png" height="300" style="border: 2px solid gray; margin: 5px;">
  <img src="./_Modulation_index/Modulation_index.png" height="300" style="border: 2px solid gray; margin: 5px;">
  <img src="./_pac/pac_with_trainable_bandpass_fp32.png" height="300" style="border: 2px solid gray; margin: 5px;">
</div>

## Quick Start
```python
# Parameters
SRC_FS = 1024  # Source sampling frequency
TGT_FS = 512   # Target sampling frequency
FREQS_HZ = [10, 30, 100]  # Frequencies in Hz for periodic signals
LOW_HZ = 20    # Low frequency for bandpass filter
HIGH_HZ = 50   # High frequency for bandpass filter
SIGMA = 10     # Sigma for Gaussian filter
SIG_TYPES = [
    "uniform",
    "gauss",
    "periodic",
    "chirp",
    "ripple",
    "meg",
    "tensorpac",
] # Available signal types


# Demo Signal
xx, tt, fs = scitex.dsp.demo_sig(
    t_sec=T_SEC, fs=SRC_FS, freqs_hz=FREQS_HZ, sig_type="chirp"
)
# xx.shape (batch_size, n_chs, seq_len) 
# xx.shape (batch_size, n_chs, n_segments, seq_len) # when sig_type is "tensorpac" or "pac"


# # Various data types are automatically handled:
# xx = torch.tensor(xx).float()
# xx = torch.tensor(xx).float().cuda()
# xx = np.array(xx)
# xx = pd.DataFrame(xx)

# Normalization
xx_norm = scitex.dsp.norm.z(xx)
xx_minmax = scitex.dsp.norm.minmax(xx)

# Resampling
xx_resampled = scitex.dsp.resample(xx, fs, TGT_FS)

# Noise addition
xx_gauss = scitex.dsp.add_noise.gauss(xx)
xx_white = scitex.dsp.add_noise.white(xx)
xx_pink = scitex.dsp.add_noise.pink(xx)
xx_brown = scitex.dsp.add_noise.brown(xx)

# Filtering
xx_filted_bandpass = scitex.dsp.filt.bandpass(xx, fs, low_hz=LOW_HZ, high_hz=HIGH_HZ)
xx_filted_bandstop = scitex.dsp.filt.bandstop(xx, fs, low_hz=LOW_HZ, high_hz=HIGH_HZ)
xx_filted_gauss = scitex.dsp.filt.gauss(xx, sigma=SIGMA)

# Hilbert Transformation
phase, amplitude = scitex.dsp.hilbert(xx) # or envelope

# Wavelet Transformation
wavelet_coef, wavelet_freqs = scitex.dsp.wavelet(xx, fs)

# Power Spetrum Density
psd, psd_freqs = scitex.dsp.psd(xx, fs)

# Phase-Amplitude Coupling
pac, freqs_pha, freqs_amp = scitex.dsp.pac(xx, fs) # This process is computationally intensive. Please monitor RAM/VRAM usage.
```

## API Reference
- `scitex.dsp.wavelet_transform(signal, wavelet, level)`: Performs wavelet transform
- `scitex.dsp.bandpass_filter(signal, lowcut, highcut, fs)`: Applies bandpass filter
- `scitex.dsp.lowpass_filter(signal, cutoff, fs)`: Applies lowpass filter
- `scitex.dsp.highpass_filter(signal, cutoff, fs)`: Applies highpass filter
- `scitex.dsp.spectrogram(signal, fs, nperseg)`: Computes spectrogram
- `scitex.dsp.stft(signal, fs, nperseg)`: Performs Short-Time Fourier Transform
- `scitex.dsp.istft(stft, fs, nperseg)`: Performs Inverse Short-Time Fourier Transform
- `scitex.dsp.chirp(t, f0, f1, method)`: Generates chirp signal
- `scitex.dsp.hilbert(signal)`: Performs Hilbert transform
- `scitex.dsp.phase_amplitude_coupling(signal, fs)`: Calculates Phase-Amplitude Coupling
- `scitex.dsp.Modulation_index(signal, fs)`: Computes Modulation Index
- `scitex.dsp.psd(signal, fs)`: Estimates Power Spectral Density
- `scitex.dsp.resample(signal, orig_fs, new_fs)`: Resamples signal to new frequency
- `scitex.dsp.add_noise(signal, snr)`: Adds noise to signal with specified SNR

## Use Cases
- Audio signal processing
- Biomedical signal analysis
- Vibration analysis
- Communication systems
- Radar and sonar signal processing
- Neuroscience data analysis

## Performance
The `scitex.dsp` module leverages PyTorch's GPU acceleration capabilities, providing significant speedups for large-scale signal processing tasks when run on CUDA-enabled devices.

## Contributing
Contributions to improve `scitex.dsp` are welcome. Please submit pull requests or open issues on the GitHub repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

For more information and updates, please visit the [scitex GitHub repository](https://github.com/ywatanabe1989/scitex).
