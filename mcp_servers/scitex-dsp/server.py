#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 11:20:00 (ywatanabe)"
# File: ./mcp_servers/scitex-dsp/server.py
# ----------------------------------------

"""MCP server for SciTeX DSP (Digital Signal Processing) module translations."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from scitex_base.base_server import ScitexBaseMCPServer
from scitex_base.translator_mixin import ScitexTranslatorMixin


class ScitexDspMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX DSP module translations."""
    
    def __init__(self):
        super().__init__("dsp", "0.1.0")
        
    def _register_module_tools(self):
        """Register DSP-specific tools."""
        
        @self.app.tool()
        async def translate_signal_filtering(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate signal filtering operations between scipy.signal and SciTeX.
            
            Args:
                code: Python code containing signal filtering operations
                direction: "to_scitex" or "from_scitex"
                
            Returns:
                Dictionary with translated_code and conversions made
            """
            
            if direction == "to_scitex":
                patterns = [
                    # Filter design
                    (r"scipy\.signal\.butter\(([^)]+)\)", r"stx.dsp.filt.butter(\1)"),
                    (r"scipy\.signal\.cheby1\(([^)]+)\)", r"stx.dsp.filt.cheby1(\1)"),
                    (r"scipy\.signal\.cheby2\(([^)]+)\)", r"stx.dsp.filt.cheby2(\1)"),
                    (r"scipy\.signal\.ellip\(([^)]+)\)", r"stx.dsp.filt.ellip(\1)"),
                    (r"scipy\.signal\.bessel\(([^)]+)\)", r"stx.dsp.filt.bessel(\1)"),
                    
                    # Filter application
                    (r"scipy\.signal\.filtfilt\(([^)]+)\)", r"stx.dsp.filt.apply(\1, method='filtfilt')"),
                    (r"scipy\.signal\.lfilter\(([^)]+)\)", r"stx.dsp.filt.apply(\1, method='lfilter')"),
                    (r"scipy\.signal\.sosfilt\(([^)]+)\)", r"stx.dsp.filt.apply_sos(\1)"),
                    (r"scipy\.signal\.sosfiltfilt\(([^)]+)\)", r"stx.dsp.filt.apply_sos(\1, method='filtfilt')"),
                    
                    # Convenience filters
                    (r"scipy\.signal\.savgol_filter\(([^)]+)\)", r"stx.dsp.filt.savgol(\1)"),
                    (r"scipy\.signal\.medfilt\(([^)]+)\)", r"stx.dsp.filt.median(\1)"),
                    (r"scipy\.signal\.wiener\(([^)]+)\)", r"stx.dsp.filt.wiener(\1)"),
                    
                    # Frequency response
                    (r"scipy\.signal\.freqz\(([^)]+)\)", r"stx.dsp.filt.freq_response(\1)"),
                    (r"scipy\.signal\.sosfreqz\(([^)]+)\)", r"stx.dsp.filt.sos_freq_response(\1)"),
                    
                    # Filter transformation
                    (r"scipy\.signal\.bilinear\(([^)]+)\)", r"stx.dsp.filt.bilinear_transform(\1)"),
                    (r"scipy\.signal\.zpk2sos\(([^)]+)\)", r"stx.dsp.filt.zpk_to_sos(\1)"),
                ]
                
                # Add imports if needed
                if "scipy.signal" in code and "import scitex as stx" not in code:
                    code = "import scitex as stx\n" + code
                    
            else:  # from_scitex
                patterns = [
                    # Reverse patterns
                    (r"stx\.dsp\.filt\.butter\(([^)]+)\)", r"scipy.signal.butter(\1)"),
                    (r"stx\.dsp\.filt\.apply\(([^,]+),\s*method='filtfilt'\)", r"scipy.signal.filtfilt(\1)"),
                    (r"stx\.dsp\.filt\.apply\(([^,]+),\s*method='lfilter'\)", r"scipy.signal.lfilter(\1)"),
                    (r"stx\.dsp\.filt\.savgol\(([^)]+)\)", r"scipy.signal.savgol_filter(\1)"),
                    (r"stx\.dsp\.filt\.median\(([^)]+)\)", r"scipy.signal.medfilt(\1)"),
                ]
                
                # Add imports if needed
                if "stx.dsp" in code and "import scipy.signal" not in code:
                    code = "from scipy import signal\n" + code
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                matches = re.findall(pattern, translated)
                if matches:
                    translated = re.sub(pattern, replacement, translated)
                    conversions.append(f"{pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions,
                "filter_operations": len(conversions)
            }
        
        @self.app.tool()
        async def translate_frequency_analysis(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate frequency analysis operations.
            
            Args:
                code: Code containing frequency analysis operations
                direction: Translation direction
                
            Returns:
                Translated code
            """
            
            if direction == "to_scitex":
                patterns = [
                    # Fourier transforms
                    (r"scipy\.fft\.fft\(([^)]+)\)", r"stx.dsp.fft(\1)"),
                    (r"scipy\.fft\.ifft\(([^)]+)\)", r"stx.dsp.ifft(\1)"),
                    (r"scipy\.fft\.rfft\(([^)]+)\)", r"stx.dsp.rfft(\1)"),
                    (r"scipy\.fft\.irfft\(([^)]+)\)", r"stx.dsp.irfft(\1)"),
                    (r"scipy\.fft\.fft2\(([^)]+)\)", r"stx.dsp.fft2d(\1)"),
                    (r"np\.fft\.fft\(([^)]+)\)", r"stx.dsp.fft(\1)"),
                    
                    # Spectral analysis
                    (r"scipy\.signal\.welch\(([^)]+)\)", r"stx.dsp.psd(\1, method='welch')"),
                    (r"scipy\.signal\.periodogram\(([^)]+)\)", r"stx.dsp.psd(\1, method='periodogram')"),
                    (r"scipy\.signal\.spectrogram\(([^)]+)\)", r"stx.dsp.spectrogram(\1)"),
                    (r"scipy\.signal\.stft\(([^)]+)\)", r"stx.dsp.stft(\1)"),
                    (r"scipy\.signal\.istft\(([^)]+)\)", r"stx.dsp.istft(\1)"),
                    
                    # Coherence and correlation
                    (r"scipy\.signal\.coherence\(([^)]+)\)", r"stx.dsp.coherence(\1)"),
                    (r"scipy\.signal\.csd\(([^)]+)\)", r"stx.dsp.cross_spectral_density(\1)"),
                    
                    # Frequency utilities
                    (r"scipy\.fft\.fftfreq\(([^)]+)\)", r"stx.dsp.fft_frequencies(\1)"),
                    (r"scipy\.fft\.rfftfreq\(([^)]+)\)", r"stx.dsp.rfft_frequencies(\1)"),
                    (r"scipy\.signal\.find_peaks\(([^)]+)\)", r"stx.dsp.find_peaks(\1)"),
                    
                    # Hilbert transform
                    (r"scipy\.signal\.hilbert\(([^)]+)\)", r"stx.dsp.hilbert(\1)"),
                    (r"np\.abs\(scipy\.signal\.hilbert\(([^)]+)\)\)", r"stx.dsp.envelope(\1)"),
                    (r"np\.angle\(scipy\.signal\.hilbert\(([^)]+)\)\)", r"stx.dsp.instantaneous_phase(\1)"),
                ]
            else:
                patterns = [
                    # Reverse patterns
                    (r"stx\.dsp\.fft\(([^)]+)\)", r"scipy.fft.fft(\1)"),
                    (r"stx\.dsp\.psd\(([^,]+),\s*method='welch'\)", r"scipy.signal.welch(\1)"),
                    (r"stx\.dsp\.spectrogram\(([^)]+)\)", r"scipy.signal.spectrogram(\1)"),
                    (r"stx\.dsp\.hilbert\(([^)]+)\)", r"scipy.signal.hilbert(\1)"),
                    (r"stx\.dsp\.envelope\(([^)]+)\)", r"np.abs(scipy.signal.hilbert(\1))"),
                ]
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    conversions.append(f"Frequency: {pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions,
                "frequency_operations": len(conversions)
            }
        
        @self.app.tool()
        async def translate_signal_generation(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate signal generation and manipulation operations.
            
            Args:
                code: Code containing signal generation
                direction: Translation direction
                
            Returns:
                Translated code
            """
            
            if direction == "to_scitex":
                patterns = [
                    # Waveform generation
                    (r"scipy\.signal\.chirp\(([^)]+)\)", r"stx.dsp.signals.chirp(\1)"),
                    (r"scipy\.signal\.sweep_poly\(([^)]+)\)", r"stx.dsp.signals.sweep_poly(\1)"),
                    (r"scipy\.signal\.gausspulse\(([^)]+)\)", r"stx.dsp.signals.gaussian_pulse(\1)"),
                    (r"scipy\.signal\.square\(([^)]+)\)", r"stx.dsp.signals.square(\1)"),
                    (r"scipy\.signal\.sawtooth\(([^)]+)\)", r"stx.dsp.signals.sawtooth(\1)"),
                    
                    # Window functions
                    (r"scipy\.signal\.get_window\(([^)]+)\)", r"stx.dsp.window(\1)"),
                    (r"scipy\.signal\.windows\.hann\(([^)]+)\)", r"stx.dsp.window('hann', \1)"),
                    (r"scipy\.signal\.windows\.hamming\(([^)]+)\)", r"stx.dsp.window('hamming', \1)"),
                    (r"scipy\.signal\.windows\.blackman\(([^)]+)\)", r"stx.dsp.window('blackman', \1)"),
                    (r"scipy\.signal\.windows\.kaiser\(([^)]+)\)", r"stx.dsp.window('kaiser', \1)"),
                    
                    # Resampling
                    (r"scipy\.signal\.resample\(([^)]+)\)", r"stx.dsp.resample(\1)"),
                    (r"scipy\.signal\.resample_poly\(([^)]+)\)", r"stx.dsp.resample_poly(\1)"),
                    (r"scipy\.signal\.decimate\(([^)]+)\)", r"stx.dsp.decimate(\1)"),
                    (r"scipy\.signal\.upfirdn\(([^)]+)\)", r"stx.dsp.upfirdn(\1)"),
                    
                    # Convolution
                    (r"scipy\.signal\.convolve\(([^)]+)\)", r"stx.dsp.convolve(\1)"),
                    (r"scipy\.signal\.correlate\(([^)]+)\)", r"stx.dsp.correlate(\1)"),
                    (r"scipy\.signal\.fftconvolve\(([^)]+)\)", r"stx.dsp.fft_convolve(\1)"),
                ]
            else:
                patterns = [
                    # Reverse patterns
                    (r"stx\.dsp\.signals\.chirp\(([^)]+)\)", r"scipy.signal.chirp(\1)"),
                    (r"stx\.dsp\.window\('hann',\s*([^)]+)\)", r"scipy.signal.windows.hann(\1)"),
                    (r"stx\.dsp\.resample\(([^)]+)\)", r"scipy.signal.resample(\1)"),
                    (r"stx\.dsp\.convolve\(([^)]+)\)", r"scipy.signal.convolve(\1)"),
                ]
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    conversions.append(f"Signal: {pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions
            }
        
        @self.app.tool()
        async def generate_filter_pipeline(
            signal_var: str,
            sampling_rate: float,
            filter_specs: List[Dict[str, Any]]
        ) -> Dict[str, str]:
            """
            Generate a complete signal filtering pipeline.
            
            Args:
                signal_var: Variable name containing the signal
                sampling_rate: Sampling rate in Hz
                filter_specs: List of filter specifications
                    Each spec should have: type, cutoff, order, etc.
                
            Returns:
                Filter pipeline code
            """
            
            pipeline = f'''#!/usr/bin/env python3
"""Signal filtering pipeline."""

import scitex as stx
import numpy as np
import matplotlib.pyplot as plt

# Signal parameters
signal = {signal_var}
fs = {sampling_rate}  # Sampling rate
nyquist = fs / 2

# Filter pipeline results
filtered_signals = {{}}
filter_responses = {{}}

'''
            
            for i, spec in enumerate(filter_specs):
                filter_type = spec.get('type', 'butterworth')
                cutoff = spec.get('cutoff', [])
                order = spec.get('order', 4)
                btype = spec.get('btype', 'lowpass')
                
                pipeline += f'''# Filter {i+1}: {filter_type} {btype}
print("\\nApplying {filter_type} {btype} filter...")
'''
                
                if filter_type == 'butterworth':
                    pipeline += f'''
# Design Butterworth filter
b, a = stx.dsp.filt.butter({order}, {cutoff}, btype='{btype}', fs=fs)
'''
                elif filter_type == 'chebyshev1':
                    rp = spec.get('rp', 1)  # Passband ripple
                    pipeline += f'''
# Design Chebyshev Type I filter
b, a = stx.dsp.filt.cheby1({order}, {rp}, {cutoff}, btype='{btype}', fs=fs)
'''
                elif filter_type == 'elliptic':
                    rp = spec.get('rp', 1)  # Passband ripple
                    rs = spec.get('rs', 40)  # Stopband attenuation
                    pipeline += f'''
# Design Elliptic filter
b, a = stx.dsp.filt.ellip({order}, {rp}, {rs}, {cutoff}, btype='{btype}', fs=fs)
'''
                
                pipeline += f'''
# Apply filter (zero-phase)
filtered_signal = stx.dsp.filt.apply(b, a, signal, method='filtfilt')
filtered_signals['filter_{i+1}'] = filtered_signal

# Compute frequency response
w, h = stx.dsp.filt.freq_response(b, a, fs=fs)
filter_responses['filter_{i+1}'] = {{'w': w, 'h': h}}

# Print filter characteristics
print(f"  Cutoff: {cutoff} Hz")
print(f"  Order: {order}")
print(f"  Attenuation at cutoff: {{20*np.log10(np.abs(h[np.argmin(np.abs(w - {cutoff[0] if isinstance(cutoff, list) else cutoff}))])):,.1f}} dB")
'''
                
                # Update signal for cascaded filtering if needed
                if i < len(filter_specs) - 1:
                    pipeline += f'\n# Use filtered signal for next stage\nsignal = filtered_signal\n'
            
            pipeline += '''
# Visualization
fig, axes = stx.plt.subplots(2, 2, figsize=(12, 10))

# 1. Original vs Filtered Signal (time domain)
ax = axes[0, 0]
time = np.arange(len({signal_var})) / fs
ax.plot(time[:1000], {signal_var}[:1000], 'b-', alpha=0.7, label='Original')
for i, (name, sig) in enumerate(filtered_signals.items()):
    ax.plot(time[:1000], sig[:1000], f'C{i+1}-', alpha=0.7, label=name)
ax.set_xyt('Time (s)', 'Amplitude', 'Time Domain Comparison')
ax.legend()
ax.grid(True)

# 2. Frequency Response of Filters
ax = axes[0, 1]
for name, resp in filter_responses.items():
    ax.plot(resp['w'], 20 * np.log10(np.abs(resp['h'])), label=name)
ax.set_xyt('Frequency (Hz)', 'Magnitude (dB)', 'Filter Frequency Response')
ax.grid(True, which='both', alpha=0.3)
ax.legend()

# 3. Power Spectral Density Comparison
ax = axes[1, 0]
f_orig, psd_orig = stx.dsp.psd({signal_var}, fs=fs, method='welch')
ax.semilogy(f_orig, psd_orig, 'b-', alpha=0.7, label='Original')
for i, (name, sig) in enumerate(filtered_signals.items()):
    f, psd = stx.dsp.psd(sig, fs=fs, method='welch')
    ax.semilogy(f, psd, f'C{i+1}-', alpha=0.7, label=name)
ax.set_xyt('Frequency (Hz)', 'PSD', 'Power Spectral Density')
ax.legend()
ax.grid(True)

# 4. Phase Response
ax = axes[1, 1]
for name, resp in filter_responses.items():
    phase = np.unwrap(np.angle(resp['h']))
    ax.plot(resp['w'], phase * 180 / np.pi, label=name)
ax.set_xyt('Frequency (Hz)', 'Phase (degrees)', 'Filter Phase Response')
ax.grid(True)
ax.legend()

plt.tight_layout()
stx.io.save(fig, './filter_analysis.jpg', symlink_from_cwd=True)

# Save filtered signals
for name, sig in filtered_signals.items():
    stx.io.save(sig, f'./{name}_signal.npy', symlink_from_cwd=True)

# Generate filter report
report = {{
    'sampling_rate': fs,
    'filter_specs': {filter_specs},
    'signal_length': len({signal_var}),
    'filters_applied': len(filter_specs)
}}

stx.io.save(report, './filter_report.json', symlink_from_cwd=True)
print("\\nFiltering complete! Check output files.")
'''
            
            return {
                "pipeline_code": pipeline,
                "signal_var": signal_var,
                "sampling_rate": sampling_rate,
                "num_filters": len(filter_specs)
            }
        
        @self.app.tool()
        async def generate_spectral_analysis(
            signal_var: str,
            sampling_rate: float,
            analysis_types: List[str] = ["fft", "psd", "spectrogram"]
        ) -> Dict[str, str]:
            """
            Generate comprehensive spectral analysis code.
            
            Args:
                signal_var: Variable containing the signal
                sampling_rate: Sampling rate in Hz
                analysis_types: Types of analysis to perform
                
            Returns:
                Spectral analysis script
            """
            
            script = f'''#!/usr/bin/env python3
"""Spectral analysis of signal."""

import scitex as stx
import numpy as np
import matplotlib.pyplot as plt

# Signal parameters
signal = {signal_var}
fs = {sampling_rate}
N = len(signal)
duration = N / fs

print(f"Signal info:")
print(f"  Length: {{N}} samples")
print(f"  Duration: {{duration:.2f}} seconds")
print(f"  Sampling rate: {{fs}} Hz")

# Results storage
results = {{}}

'''
            
            if "fft" in analysis_types:
                script += '''# FFT Analysis
print("\\nPerforming FFT analysis...")
fft_result = stx.dsp.fft(signal)
frequencies = stx.dsp.fft_frequencies(N, fs)

# Magnitude and phase
magnitude = np.abs(fft_result)
phase = np.angle(fft_result)

# Find dominant frequencies
peaks, properties = stx.dsp.find_peaks(magnitude[:N//2], height=np.max(magnitude)*0.1)
dominant_freqs = frequencies[peaks]

results['dominant_frequencies'] = dominant_freqs[:5].tolist()
print(f"Dominant frequencies: {dominant_freqs[:5]} Hz")

# Plot FFT
fig, (ax1, ax2) = stx.plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(frequencies[:N//2], magnitude[:N//2])
ax1.plot(frequencies[peaks], magnitude[peaks], 'ro', markersize=8)
ax1.set_xyt('Frequency (Hz)', 'Magnitude', 'FFT Magnitude Spectrum')
ax1.grid(True)

ax2.plot(frequencies[:N//2], phase[:N//2])
ax2.set_xyt('Frequency (Hz)', 'Phase (radians)', 'FFT Phase Spectrum')
ax2.grid(True)

stx.io.save(fig, './fft_analysis.jpg', symlink_from_cwd=True)

'''
            
            if "psd" in analysis_types:
                script += '''# Power Spectral Density
print("\\nComputing PSD...")

# Welch's method
f_welch, psd_welch = stx.dsp.psd(signal, fs=fs, method='welch', nperseg=1024)

# Periodogram for comparison
f_periodo, psd_periodo = stx.dsp.psd(signal, fs=fs, method='periodogram')

# Plot PSD comparison
fig, ax = stx.plt.subplots(figsize=(10, 6))
ax.semilogy(f_welch, psd_welch, 'b-', label='Welch method', linewidth=2)
ax.semilogy(f_periodo, psd_periodo, 'r-', alpha=0.3, label='Periodogram')
ax.set_xyt('Frequency (Hz)', 'Power/Frequency', 'Power Spectral Density')
ax.legend()
ax.grid(True, which='both', alpha=0.3)

stx.io.save(fig, './psd_analysis.jpg', symlink_from_cwd=True)

# Find peak power frequency
peak_freq = f_welch[np.argmax(psd_welch)]
results['peak_power_frequency'] = peak_freq
print(f"Peak power at: {peak_freq:.2f} Hz")

'''
            
            if "spectrogram" in analysis_types:
                script += '''# Spectrogram Analysis
print("\\nGenerating spectrogram...")

# STFT parameters
window_length = int(0.05 * fs)  # 50ms window
overlap = int(0.9 * window_length)  # 90% overlap

# Compute spectrogram
f_spec, t_spec, Sxx = stx.dsp.spectrogram(signal, fs=fs, 
                                          nperseg=window_length, 
                                          noverlap=overlap)

# Plot spectrogram
fig, ax = stx.plt.subplots(figsize=(12, 6))
pcm = ax.pcolormesh(t_spec, f_spec, 10 * np.log10(Sxx), 
                    shading='gouraud', cmap='viridis')
ax.set_ylabel('Frequency (Hz)')
ax.set_xlabel('Time (s)')
ax.set_title('Spectrogram (dB)')
ax.set_ylim([0, fs/2])
cbar = plt.colorbar(pcm, ax=ax)
cbar.set_label('Power (dB)')

stx.io.save(fig, './spectrogram.jpg', symlink_from_cwd=True)

# Time-frequency ridge extraction
ridge_frequencies = []
for t_idx in range(Sxx.shape[1]):
    ridge_frequencies.append(f_spec[np.argmax(Sxx[:, t_idx])])

results['time_frequency_ridge'] = {
    'times': t_spec.tolist(),
    'frequencies': ridge_frequencies
}

'''
            
            if "hilbert" in analysis_types:
                script += '''# Hilbert Transform Analysis
print("\\nPerforming Hilbert transform analysis...")

# Compute envelope and instantaneous phase
envelope = stx.dsp.envelope(signal)
inst_phase = stx.dsp.instantaneous_phase(signal)
inst_freq = np.diff(np.unwrap(inst_phase)) * fs / (2 * np.pi)

# Plot Hilbert analysis
fig, axes = stx.plt.subplots(3, 1, figsize=(12, 10))

# Original signal with envelope
ax = axes[0]
time = np.arange(N) / fs
ax.plot(time, signal, 'b-', alpha=0.7, label='Signal')
ax.plot(time, envelope, 'r-', linewidth=2, label='Envelope')
ax.plot(time, -envelope, 'r-', linewidth=2)
ax.set_xyt('Time (s)', 'Amplitude', 'Signal and Envelope')
ax.legend()
ax.grid(True)

# Instantaneous phase
ax = axes[1]
ax.plot(time, inst_phase)
ax.set_xyt('Time (s)', 'Phase (radians)', 'Instantaneous Phase')
ax.grid(True)

# Instantaneous frequency
ax = axes[2]
ax.plot(time[:-1], inst_freq)
ax.set_xyt('Time (s)', 'Frequency (Hz)', 'Instantaneous Frequency')
ax.set_ylim([0, fs/2])
ax.grid(True)

plt.tight_layout()
stx.io.save(fig, './hilbert_analysis.jpg', symlink_from_cwd=True)

results['envelope_stats'] = {
    'mean': float(np.mean(envelope)),
    'std': float(np.std(envelope)),
    'max': float(np.max(envelope))
}

'''
            
            script += f'''# Save analysis results
results['signal_info'] = {{
    'length': N,
    'duration': duration,
    'sampling_rate': fs,
    'analysis_types': {analysis_types}
}}

stx.io.save(results, './spectral_analysis_results.json', symlink_from_cwd=True)

print("\\nSpectral analysis complete!")
print(f"Generated {{len({analysis_types})}} analysis types")
print("Check output directory for results and visualizations")
'''
            
            return {
                "analysis_script": script,
                "signal_var": signal_var,
                "sampling_rate": sampling_rate,
                "analysis_types": analysis_types
            }
        
        @self.app.tool()
        async def validate_dsp_code(
            code: str
        ) -> Dict[str, Any]:
            """
            Validate DSP code for best practices.
            
            Args:
                code: DSP code to validate
                
            Returns:
                Validation results with suggestions
            """
            
            issues = []
            suggestions = []
            
            # Check for proper sampling rate handling
            if "filter" in code.lower() and "fs=" not in code and "sampling_rate" not in code:
                issues.append("Filter design without explicit sampling rate")
                suggestions.append("Always specify sampling rate for filter design")
            
            # Check for aliasing prevention
            if "resample" in code and "filter" not in code:
                suggestions.append("Consider anti-aliasing filter before resampling")
            
            # Check for window function in spectral analysis
            if "fft(" in code and "window" not in code:
                suggestions.append("Consider applying window function before FFT to reduce spectral leakage")
            
            # Check for proper normalization
            if "psd" in code and "nperseg" not in code:
                suggestions.append("Specify nperseg for consistent PSD estimation")
            
            # Check for zero-phase filtering
            if "lfilter(" in code and "filtfilt" not in code:
                suggestions.append("Consider using filtfilt for zero-phase filtering")
            
            # Check for numerical stability
            if "butter(" in code and re.search(r"butter\(\s*(\d+)", code):
                match = re.search(r"butter\(\s*(\d+)", code)
                order = int(match.group(1))
                if order > 10:
                    issues.append(f"High filter order ({order}) may cause numerical instability")
                    suggestions.append("Consider using SOS format for high-order filters")
            
            # Check for proper frequency specifications
            if re.search(r"cutoff\s*=\s*\d+[^.]", code) and "normalize" not in code:
                suggestions.append("Ensure frequency specifications are normalized or in Hz")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "suggestions": suggestions,
                "best_practices_score": max(0, 100 - len(issues) * 15 - len(suggestions) * 5)
            }
    
    def get_module_description(self) -> str:
        """Get description of DSP functionality."""
        return (
            "SciTeX DSP server provides digital signal processing translations, "
            "filter design and application, frequency analysis tools, signal generation, "
            "and comprehensive spectral analysis capabilities for scientific computing."
        )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "translate_signal_filtering",
            "translate_frequency_analysis",
            "translate_signal_generation",
            "generate_filter_pipeline",
            "generate_spectral_analysis",
            "validate_dsp_code",
            "get_module_info",
            "validate_code"
        ]
    
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate DSP module usage."""
        issues = []
        
        # Check for common anti-patterns
        if "scipy.signal" in code and "stx.dsp" not in code and "scitex" in code:
            issues.append("Using scipy.signal directly instead of stx.dsp")
        
        if "np.fft" in code and "stx.dsp.fft" not in code and "scitex" in code:
            issues.append("Using numpy FFT instead of stx.dsp.fft")
        
        # Check for proper imports
        if "stx.dsp" in code and "import scitex as stx" not in code:
            issues.append("Missing scitex import")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "module": "dsp"
        }


# Main entry point
if __name__ == "__main__":
    server = ScitexDspMCPServer()
    asyncio.run(server.run())

# EOF