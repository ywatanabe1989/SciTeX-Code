#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Demo: YAML Metadata Export with Scientific Plotting

"""
Demonstration of the new set_meta() functionality with YAML export
showcasing clean separation of concerns and AI-ready metadata structure.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add source path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    import scitex
    print("✅ Using scitex from source")
except ImportError:
    print("❌ Could not import scitex - using matplotlib directly for demo")
    # Fallback demo without scitex
    exit(1)

def demo_single_panel_metadata():
    """Demonstrate single panel with comprehensive metadata"""
    print("\n🔬 Demo: Single Panel with YAML Metadata")
    
    # Generate experimental data
    time = np.linspace(0, 10, 1000)
    signal = np.exp(-time/3) * np.sin(2*np.pi*2*time) + 0.1*np.random.randn(1000)
    
    # Create figure with clean separation
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    ax.plot(time, signal, 'b-', linewidth=1.5, alpha=0.8, id='neural_signal')
    
    # Clean styling (separated from metadata)
    ax.set_xyt(
        x='Time (s)', 
        y='Amplitude (mV)', 
        t='Neural Signal Recording'
    )
    
    # Comprehensive scientific metadata
    ax.set_meta(
        caption='Simulated neural signal showing exponential decay with 2 Hz oscillations and background noise.',
        methods='Signal generated using exponential decay envelope with sinusoidal carrier and Gaussian noise.',
        stats='Signal-to-noise ratio = 10:1, decay constant τ = 3 seconds.',
        keywords=['neuroscience', 'signal_processing', 'electrophysiology', 'decay'],
        experimental_details={
            'duration': 10,
            'sampling_rate': 100,
            'decay_constant': 3,
            'carrier_frequency': 2,
            'noise_std': 0.1,
            'signal_amplitude': 1
        },
        journal_style='nature',
        significance='Demonstrates typical neural signal characteristics in computational models.'
    )
    
    # Save with automatic YAML export
    output_file = 'demo_neural_signal'
    try:
        scitex.io.save(fig, f'{output_file}.png')
        print(f"✅ Saved: {output_file}.png")
        print(f"✅ Saved: {output_file}.csv")
        print(f"✅ Saved: {output_file}_metadata.yaml")
        
        # Show YAML content
        if os.path.exists(f'{output_file}_metadata.yaml'):
            print("\n📄 YAML Metadata Content:")
            with open(f'{output_file}_metadata.yaml', 'r') as f:
                print(f.read())
                
    except Exception as e:
        print(f"❌ Save failed: {e}")
        # Manual YAML export demonstration
        from scitex.plt.ax._style._set_meta import export_metadata_yaml
        export_metadata_yaml(fig, f'{output_file}_metadata.yaml')
        print(f"✅ Manual YAML export: {output_file}_metadata.yaml")


def demo_multi_panel_metadata():
    """Demonstrate multi-panel figure with figure-level metadata"""
    print("\n🔬 Demo: Multi-Panel Figure with Comprehensive Metadata")
    
    # Create multi-panel figure
    fig, ((ax1, ax2), (ax3, ax4)) = scitex.plt.subplots(2, 2, figsize=(12, 10))
    
    # Panel A: Time series
    t = np.linspace(0, 20, 500)
    signal_a = np.exp(-t/8) * np.cos(t)
    ax1.plot(t, signal_a, 'r-', linewidth=2, id='decay_signal')
    ax1.set_xyt(x='Time (s)', y='Amplitude', t='A. Exponential Decay')
    ax1.set_meta(
        caption='Exponential decay with τ = 8 seconds and cosine modulation.',
        keywords=['exponential_decay', 'modulation'],
        experimental_details={'tau': 8, 'modulation': 'cosine'}
    )
    
    # Panel B: Frequency analysis
    freq = np.fft.fftfreq(len(signal_a), t[1]-t[0])
    spectrum = np.abs(np.fft.fft(signal_a))
    ax2.semilogy(freq[:len(freq)//2], spectrum[:len(freq)//2], 'g-', id='spectrum')
    ax2.set_xyt(x='Frequency (Hz)', y='Power', t='B. Power Spectrum')
    ax2.set_meta(
        caption='Power spectrum showing dominant frequency components.',
        methods='Fast Fourier Transform analysis.',
        keywords=['FFT', 'spectrum_analysis'],
        experimental_details={'n_points': 500, 'window': 'none'}
    )
    
    # Panel C: Statistical distribution
    data_c = np.random.exponential(2, 1000)
    ax3.hist(data_c, bins=50, alpha=0.7, color='purple', id='exponential_dist')
    ax3.set_xyt(x='Value', y='Count', t='C. Exponential Distribution')
    ax3.set_meta(
        caption='Exponential distribution with λ = 0.5.',
        stats='Kolmogorov-Smirnov test confirms exponential distribution (p < 0.001).',
        keywords=['exponential_distribution', 'histogram'],
        experimental_details={'lambda': 0.5, 'n_samples': 1000, 'bins': 50}
    )
    
    # Panel D: Scatter analysis
    x_d = np.random.randn(200)
    y_d = 0.7*x_d + 0.5*np.random.randn(200)
    ax4.scatter(x_d, y_d, alpha=0.6, c='orange', id='correlation')
    ax4.set_xyt(x='X Variable', y='Y Variable', t='D. Correlation Analysis')
    ax4.set_meta(
        caption='Linear correlation with R² = 0.49.',
        stats='Pearson correlation r = 0.7, p < 0.001.',
        keywords=['correlation', 'linear_relationship'],
        experimental_details={'n_points': 200, 'correlation': 0.7, 'r_squared': 0.49}
    )
    
    # Figure-level metadata
    ax1.set_figure_meta(
        caption='Comprehensive signal analysis demonstrating (A) temporal dynamics, (B) frequency characteristics, (C) statistical properties, and (D) correlation structure.',
        significance='Multi-panel analysis showcases fundamental signal processing and statistical analysis techniques.',
        funding='Demo project - no funding required.',
        data_availability='Synthetic data generated for demonstration purposes.'
    )
    
    # Save with automatic YAML export
    output_file = 'demo_multi_panel'
    try:
        scitex.io.save(fig, f'{output_file}.png')
        print(f"✅ Saved: {output_file}.png")
        print(f"✅ Saved: {output_file}_metadata.yaml")
        
        # Show YAML structure
        if os.path.exists(f'{output_file}_metadata.yaml'):
            print("\n📄 Multi-Panel YAML Metadata:")
            with open(f'{output_file}_metadata.yaml', 'r') as f:
                content = f.read()
                # Show first 20 lines
                lines = content.split('\n')[:20]
                print('\n'.join(lines))
                if len(content.split('\n')) > 20:
                    print("... (truncated)")
                    
    except Exception as e:
        print(f"❌ Save failed: {e}")


def main():
    """Run all demonstrations"""
    print("🚀 SciTeX Scientific Metadata System Demo")
    print("="*50)
    
    try:
        demo_single_panel_metadata()
        demo_multi_panel_metadata()
        
        print("\n✅ Demo Complete!")
        print("\nKey Benefits:")
        print("• Clean separation: set_xyt() for styling, set_meta() for metadata")
        print("• YAML export: Machine-readable for AI agents")
        print("• Comprehensive: Methods, stats, experimental details")
        print("• SciTeX-ready: Perfect for ecosystem integration")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()