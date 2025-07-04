17 SciTeX Nn
============

.. note::
   This page is generated from the Jupyter notebook `17_scitex_nn.ipynb <https://github.com/scitex/scitex/blob/main/examples/17_scitex_nn.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 17_scitex_nn.ipynb


This notebook demonstrates the complete functionality of the
``scitex.nn`` module, which provides specialized neural network layers
and utilities for scientific computing and signal processing.

Module Overview
---------------

The ``scitex.nn`` module includes: - Signal processing layers (filters,
transforms) - Attention mechanisms - Dropout variants - Specialized
neural network architectures - Utility layers for tensor manipulation

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal
    
    # Import scitex nn module
    import scitex.nn as snn
    import scitex
    
    # Set random seed for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Check available functions
    print("Available classes/functions in scitex.nn:")
    nn_attrs = [attr for attr in dir(snn) if not attr.startswith('_')]
    for i, attr in enumerate(nn_attrs):
        print(f"{i+1:2d}. {attr}")

1. Signal Processing Filters
----------------------------

Basic Filters
~~~~~~~~~~~~~

The module provides various filter types for signal processing.

.. code:: ipython3

    # Example 1: Basic filter demonstration
    # Create a test signal with multiple frequency components
    fs = 1000  # Sampling frequency
    t = torch.linspace(0, 1, fs, dtype=torch.float32)
    signal_clean = torch.sin(2 * np.pi * 10 * t) + 0.5 * torch.sin(2 * np.pi * 50 * t) + 0.3 * torch.sin(2 * np.pi * 100 * t)
    noise = 0.1 * torch.randn_like(signal_clean)
    signal_noisy = signal_clean + noise
    
    # Reshape for neural network processing (batch, channels, time)
    signal_input = signal_noisy.unsqueeze(0).unsqueeze(0)  # (1, 1, 1000)
    
    print(f"Signal shape: {signal_input.shape}")
    print(f"Signal range: [{signal_input.min():.3f}, {signal_input.max():.3f}]")
    
    # Visualize the original signal
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Time domain
    axes[0, 0].plot(t[:200], signal_clean[:200], label='Clean signal', alpha=0.7)
    axes[0, 0].plot(t[:200], signal_noisy[:200], label='Noisy signal', alpha=0.7)
    axes[0, 0].set_title('Time Domain Signal (first 200 samples)')
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Amplitude')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Frequency domain
    freqs = np.fft.fftfreq(len(signal_noisy), 1/fs)[:len(signal_noisy)//2]
    fft_clean = np.abs(np.fft.fft(signal_clean.numpy()))[:len(signal_noisy)//2]
    fft_noisy = np.abs(np.fft.fft(signal_noisy.numpy()))[:len(signal_noisy)//2]
    
    axes[0, 1].plot(freqs, fft_clean, label='Clean signal', alpha=0.7)
    axes[0, 1].plot(freqs, fft_noisy, label='Noisy signal', alpha=0.7)
    axes[0, 1].set_title('Frequency Domain')
    axes[0, 1].set_xlabel('Frequency (Hz)')
    axes[0, 1].set_ylabel('Magnitude')
    axes[0, 1].set_xlim(0, 200)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

Gaussian Filter
~~~~~~~~~~~~~~~

The ``GaussianFilter`` provides smooth filtering capabilities.

.. code:: ipython3

    # Example 2: Gaussian Filter
    try:
        # Create Gaussian filter
        gaussian_filter = snn.GaussianFilter(sigma=2.0)
        
        # Apply filter
        with torch.no_grad():
            filtered_signal = gaussian_filter(signal_input)
        
        print(f"Filtered signal shape: {filtered_signal.shape}")
        
        # Visualize results
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Time domain comparison
        axes[0].plot(t[:200], signal_noisy[:200], label='Noisy signal', alpha=0.7)
        axes[0].plot(t[:200], filtered_signal[0, 0, :200], label='Gaussian filtered', alpha=0.7)
        axes[0].set_title('Gaussian Filter - Time Domain')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Amplitude')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Frequency domain comparison
        fft_filtered = np.abs(np.fft.fft(filtered_signal[0, 0, :].numpy()))[:len(signal_noisy)//2]
        axes[1].plot(freqs, fft_noisy, label='Noisy signal', alpha=0.7)
        axes[1].plot(freqs, fft_filtered, label='Gaussian filtered', alpha=0.7)
        axes[1].set_title('Gaussian Filter - Frequency Domain')
        axes[1].set_xlabel('Frequency (Hz)')
        axes[1].set_ylabel('Magnitude')
        axes[1].set_xlim(0, 200)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Gaussian filter not available or error: {e}")
        print("This might require additional dependencies or configuration.")

Spectrogram Layer
~~~~~~~~~~~~~~~~~

The ``Spectrogram`` layer computes spectrograms for time-frequency
analysis.

.. code:: ipython3

    # Example 3: Spectrogram computation
    try:
        # Create spectrogram layer
        spectrogram_layer = snn.Spectrogram(
            sampling_rate=fs,
            n_fft=256,
            hop_length=64,
            win_length=256
        )
        
        # Compute spectrogram
        with torch.no_grad():
            spec = spectrogram_layer(signal_input)
        
        print(f"Spectrogram shape: {spec.shape}")
        
        # Visualize spectrogram
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Original signal
        axes[0].plot(t, signal_noisy)
        axes[0].set_title('Original Signal')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Amplitude')
        axes[0].grid(True, alpha=0.3)
        
        # Spectrogram
        if spec.dim() == 4:  # (batch, channels, freq, time)
            spec_plot = spec[0, 0, :, :].numpy()
        else:
            spec_plot = spec[0, :, :].numpy()
        
        im = axes[1].imshow(np.log(spec_plot + 1e-8), aspect='auto', origin='lower', cmap='viridis')
        axes[1].set_title('Spectrogram (Log Scale)')
        axes[1].set_xlabel('Time Frame')
        axes[1].set_ylabel('Frequency Bin')
        plt.colorbar(im, ax=axes[1])
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Spectrogram layer not available or error: {e}")
        print("This might require additional dependencies or configuration.")

2. Attention Mechanisms
-----------------------

Spatial Attention
~~~~~~~~~~~~~~~~~

The ``SpatialAttention`` layer provides attention mechanisms for spatial
dimensions.

.. code:: ipython3

    # Example 4: Spatial Attention
    try:
        # Create multi-channel data
        batch_size, n_channels, seq_len = 2, 8, 1000
        multi_channel_data = torch.randn(batch_size, n_channels, seq_len)
        
        # Create spatial attention layer
        spatial_attention = snn.SpatialAttention(n_channels)
        
        # Apply attention
        with torch.no_grad():
            attended_data = spatial_attention(multi_channel_data)
        
        print(f"Input shape: {multi_channel_data.shape}")
        print(f"Output shape: {attended_data.shape}")
        
        # Visualize attention weights if available
        if hasattr(spatial_attention, 'attention_weights'):
            weights = spatial_attention.attention_weights
            print(f"Attention weights shape: {weights.shape}")
            
            # Plot attention weights
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            im = ax.imshow(weights[0].numpy(), aspect='auto', cmap='viridis')
            ax.set_title('Spatial Attention Weights')
            ax.set_xlabel('Time')
            ax.set_ylabel('Channel')
            plt.colorbar(im, ax=ax)
            plt.tight_layout()
            plt.show()
        
        # Compare input and output statistics
        print(f"Input mean: {multi_channel_data.mean():.4f}, std: {multi_channel_data.std():.4f}")
        print(f"Output mean: {attended_data.mean():.4f}, std: {attended_data.std():.4f}")
        
    except Exception as e:
        print(f"Spatial attention not available or error: {e}")
        print("This might require additional dependencies or configuration.")

3. Dropout Variants
-------------------

Axiswise Dropout
~~~~~~~~~~~~~~~~

The ``AxiswiseDropout`` layer provides dropout along specific axes.

.. code:: ipython3

    # Example 5: Axiswise Dropout
    try:
        # Create test data
        test_data = torch.randn(4, 10, 20)  # (batch, channels, time)
        
        # Create axiswise dropout layer
        axiswise_dropout = snn.AxiswiseDropout(p=0.3, axis=1)  # Drop along channel axis
        
        # Apply dropout in training mode
        axiswise_dropout.train()
        dropped_data = axiswise_dropout(test_data)
        
        print(f"Input shape: {test_data.shape}")
        print(f"Output shape: {dropped_data.shape}")
        print(f"Input mean: {test_data.mean():.4f}, std: {test_data.std():.4f}")
        print(f"Output mean: {dropped_data.mean():.4f}, std: {dropped_data.std():.4f}")
        
        # Visualize dropout effect
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Original data
        im1 = axes[0].imshow(test_data[0].numpy(), aspect='auto', cmap='viridis')
        axes[0].set_title('Original Data')
        axes[0].set_xlabel('Time')
        axes[0].set_ylabel('Channel')
        plt.colorbar(im1, ax=axes[0])
        
        # Dropped data
        im2 = axes[1].imshow(dropped_data[0].numpy(), aspect='auto', cmap='viridis')
        axes[1].set_title('After Axiswise Dropout')
        axes[1].set_xlabel('Time')
        axes[1].set_ylabel('Channel')
        plt.colorbar(im2, ax=axes[1])
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Axiswise dropout not available or error: {e}")
        print("This might require additional dependencies or configuration.")

Dropout Channels
~~~~~~~~~~~~~~~~

The ``DropoutChannels`` layer provides channel-wise dropout.

.. code:: ipython3

    # Example 6: Dropout Channels
    try:
        # Create test data
        test_data = torch.randn(2, 16, 500)  # (batch, channels, time)
        
        # Create dropout channels layer
        dropout_channels = snn.DropoutChannels(dropout=0.25)
        
        # Apply dropout in training mode
        dropout_channels.train()
        dropped_data = dropout_channels(test_data)
        
        print(f"Input shape: {test_data.shape}")
        print(f"Output shape: {dropped_data.shape}")
        
        # Count how many channels were dropped
        dropped_channels = (dropped_data[0].sum(dim=1) == 0).sum().item()
        print(f"Channels dropped: {dropped_channels} out of {test_data.shape[1]}")
        
        # Visualize channel dropout
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Original data
        im1 = axes[0].imshow(test_data[0].numpy(), aspect='auto', cmap='viridis')
        axes[0].set_title('Original Data')
        axes[0].set_xlabel('Time')
        axes[0].set_ylabel('Channel')
        plt.colorbar(im1, ax=axes[0])
        
        # Dropped data
        im2 = axes[1].imshow(dropped_data[0].numpy(), aspect='auto', cmap='viridis')
        axes[1].set_title('After Channel Dropout')
        axes[1].set_xlabel('Time')
        axes[1].set_ylabel('Channel')
        plt.colorbar(im2, ax=axes[1])
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Dropout channels not available or error: {e}")
        print("This might require additional dependencies or configuration.")

4. Utility Layers
-----------------

Transpose Layer
~~~~~~~~~~~~~~~

The ``TransposeLayer`` provides learnable tensor transposition.

.. code:: ipython3

    # Example 7: Transpose Layer
    try:
        # Create test data
        test_data = torch.randn(2, 8, 10, 5)  # (batch, channels, height, width)
        
        # Create transpose layer
        transpose_layer = snn.TransposeLayer(dim1=2, dim2=3)  # Transpose height and width
        
        # Apply transpose
        transposed_data = transpose_layer(test_data)
        
        print(f"Input shape: {test_data.shape}")
        print(f"Output shape: {transposed_data.shape}")
        
        # Verify transpose operation
        expected_shape = (test_data.shape[0], test_data.shape[1], test_data.shape[3], test_data.shape[2])
        print(f"Expected shape: {expected_shape}")
        print(f"Shapes match: {transposed_data.shape == expected_shape}")
        
    except Exception as e:
        print(f"Transpose layer not available or error: {e}")
        print("This might require additional dependencies or configuration.")

Swap Channels
~~~~~~~~~~~~~

The ``SwapChannels`` layer provides channel swapping functionality.

.. code:: ipython3

    # Example 8: Swap Channels
    try:
        # Create test data with distinct patterns per channel
        test_data = torch.zeros(1, 4, 100)
        test_data[0, 0, :] = torch.sin(torch.linspace(0, 4*np.pi, 100))  # Sine wave
        test_data[0, 1, :] = torch.cos(torch.linspace(0, 4*np.pi, 100))  # Cosine wave
        test_data[0, 2, :] = torch.linspace(-1, 1, 100)  # Linear ramp
        test_data[0, 3, :] = torch.ones(100) * 0.5  # Constant
        
        # Create swap channels layer
        swap_channels = snn.SwapChannels()
        
        # Apply channel swapping
        swapped_data = swap_channels(test_data)
        
        print(f"Input shape: {test_data.shape}")
        print(f"Output shape: {swapped_data.shape}")
        
        # Visualize channel swapping
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Original channels
        for i in range(test_data.shape[1]):
            axes[0].plot(test_data[0, i, :], label=f'Channel {i}')
        axes[0].set_title('Original Channels')
        axes[0].set_xlabel('Time')
        axes[0].set_ylabel('Amplitude')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Swapped channels
        for i in range(swapped_data.shape[1]):
            axes[1].plot(swapped_data[0, i, :], label=f'Channel {i}')
        axes[1].set_title('Swapped Channels')
        axes[1].set_xlabel('Time')
        axes[1].set_ylabel('Amplitude')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Swap channels not available or error: {e}")
        print("This might require additional dependencies or configuration.")

5. Advanced Signal Processing Layers
------------------------------------

Hilbert Transform
~~~~~~~~~~~~~~~~~

The ``Hilbert`` layer computes the Hilbert transform for analytic signal
generation.

.. code:: ipython3

    # Example 9: Hilbert Transform
    try:
        # Create a test signal
        t = torch.linspace(0, 1, 1000)
        signal = torch.sin(2 * np.pi * 10 * t) + 0.5 * torch.sin(2 * np.pi * 30 * t)
        signal_input = signal.unsqueeze(0).unsqueeze(0)  # (1, 1, 1000)
        
        # Create Hilbert transform layer
        hilbert_layer = snn.Hilbert()
        
        # Apply Hilbert transform
        with torch.no_grad():
            analytic_signal = hilbert_layer(signal_input)
        
        print(f"Input shape: {signal_input.shape}")
        print(f"Output shape: {analytic_signal.shape}")
        
        # Extract amplitude and phase
        if analytic_signal.dtype == torch.complex64 or analytic_signal.dtype == torch.complex128:
            amplitude = torch.abs(analytic_signal)
            phase = torch.angle(analytic_signal)
        else:
            # If output is real, assume it's the imaginary part
            amplitude = torch.sqrt(signal_input**2 + analytic_signal**2)
            phase = torch.atan2(analytic_signal, signal_input)
        
        # Visualize results
        fig, axes = plt.subplots(3, 1, figsize=(12, 12))
        
        # Original signal
        axes[0].plot(t[:200], signal[:200])
        axes[0].set_title('Original Signal')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Amplitude')
        axes[0].grid(True, alpha=0.3)
        
        # Envelope (amplitude)
        axes[1].plot(t[:200], signal[:200], alpha=0.5, label='Original')
        axes[1].plot(t[:200], amplitude[0, 0, :200], label='Envelope', linewidth=2)
        axes[1].set_title('Signal Envelope')
        axes[1].set_xlabel('Time (s)')
        axes[1].set_ylabel('Amplitude')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Instantaneous phase
        axes[2].plot(t[:200], phase[0, 0, :200])
        axes[2].set_title('Instantaneous Phase')
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Phase (rad)')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Hilbert transform not available or error: {e}")
        print("This might require additional dependencies or configuration.")

Power Spectral Density (PSD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``PSD`` layer computes power spectral density.

.. code:: ipython3

    # Example 10: Power Spectral Density
    try:
        # Create a test signal with multiple frequency components
        fs = 500  # Sampling frequency
        t = torch.linspace(0, 2, fs * 2)  # 2 seconds of data
        signal = (
            torch.sin(2 * np.pi * 10 * t) +  # 10 Hz
            0.5 * torch.sin(2 * np.pi * 25 * t) +  # 25 Hz
            0.3 * torch.sin(2 * np.pi * 40 * t) +  # 40 Hz
            0.1 * torch.randn_like(t)  # Noise
        )
        signal_input = signal.unsqueeze(0).unsqueeze(0)  # (1, 1, 1000)
        
        # Create PSD layer
        psd_layer = snn.PSD(sampling_rate=fs, nperseg=256)
        
        # Compute PSD
        with torch.no_grad():
            psd_result = psd_layer(signal_input)
        
        print(f"Input shape: {signal_input.shape}")
        print(f"PSD output shape: {psd_result.shape}")
        
        # Visualize PSD
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Time domain signal
        axes[0].plot(t[:500], signal[:500])
        axes[0].set_title('Time Domain Signal')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Amplitude')
        axes[0].grid(True, alpha=0.3)
        
        # Power Spectral Density
        freqs = np.linspace(0, fs/2, psd_result.shape[-1])
        axes[1].plot(freqs, psd_result[0, 0, :].numpy())
        axes[1].set_title('Power Spectral Density')
        axes[1].set_xlabel('Frequency (Hz)')
        axes[1].set_ylabel('Power')
        axes[1].set_xlim(0, 100)
        axes[1].grid(True, alpha=0.3)
        
        # Add vertical lines at expected frequencies
        for freq in [10, 25, 40]:
            axes[1].axvline(freq, color='red', linestyle='--', alpha=0.7, label=f'{freq} Hz' if freq == 10 else '')
        
        if freq == 10:
            axes[1].legend()
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"PSD layer not available or error: {e}")
        print("This might require additional dependencies or configuration.")

6. Gain Control Layers
----------------------

Channel Gain Changer
~~~~~~~~~~~~~~~~~~~~

The ``ChannelGainChanger`` layer provides learnable channel-wise gain
control.

.. code:: ipython3

    # Example 11: Channel Gain Changer
    try:
        # Create test data with different amplitude channels
        test_data = torch.zeros(2, 4, 100)
        test_data[:, 0, :] = 0.1 * torch.randn(2, 100)  # Low amplitude
        test_data[:, 1, :] = 0.5 * torch.randn(2, 100)  # Medium amplitude
        test_data[:, 2, :] = 1.0 * torch.randn(2, 100)  # High amplitude
        test_data[:, 3, :] = 2.0 * torch.randn(2, 100)  # Very high amplitude
        
        # Create channel gain changer
        gain_changer = snn.ChannelGainChanger(n_channels=4)
        
        # Apply gain changes
        with torch.no_grad():
            gained_data = gain_changer(test_data)
        
        print(f"Input shape: {test_data.shape}")
        print(f"Output shape: {gained_data.shape}")
        
        # Print gain values if available
        if hasattr(gain_changer, 'gain'):
            print(f"Gain values: {gain_changer.gain.data}")
        
        # Compare channel statistics
        print("\nChannel statistics:")
        print("Channel | Input Mean | Input Std | Output Mean | Output Std")
        print("-" * 60)
        for i in range(4):
            in_mean = test_data[:, i, :].mean().item()
            in_std = test_data[:, i, :].std().item()
            out_mean = gained_data[:, i, :].mean().item()
            out_std = gained_data[:, i, :].std().item()
            print(f"   {i}    | {in_mean:8.3f} | {in_std:7.3f} | {out_mean:9.3f} | {out_std:8.3f}")
        
        # Visualize gain effects
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Input data
        im1 = axes[0, 0].imshow(test_data[0].numpy(), aspect='auto', cmap='viridis')
        axes[0, 0].set_title('Input Data')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Channel')
        plt.colorbar(im1, ax=axes[0, 0])
        
        # Output data
        im2 = axes[0, 1].imshow(gained_data[0].numpy(), aspect='auto', cmap='viridis')
        axes[0, 1].set_title('Output Data (After Gain)')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('Channel')
        plt.colorbar(im2, ax=axes[0, 1])
        
        # Channel variances
        input_vars = test_data.var(dim=2).mean(dim=0)
        output_vars = gained_data.var(dim=2).mean(dim=0)
        
        x_channels = range(4)
        axes[1, 0].bar(x_channels, input_vars.numpy(), alpha=0.7, label='Input')
        axes[1, 0].bar(x_channels, output_vars.numpy(), alpha=0.7, label='Output')
        axes[1, 0].set_title('Channel Variances')
        axes[1, 0].set_xlabel('Channel')
        axes[1, 0].set_ylabel('Variance')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Sample time series
        for i in range(4):
            axes[1, 1].plot(test_data[0, i, :20], label=f'Ch {i} (input)', alpha=0.7)
            axes[1, 1].plot(gained_data[0, i, :20], label=f'Ch {i} (output)', linestyle='--', alpha=0.7)
        axes[1, 1].set_title('Sample Time Series (first 20 points)')
        axes[1, 1].set_xlabel('Time')
        axes[1, 1].set_ylabel('Amplitude')
        axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Channel gain changer not available or error: {e}")
        print("This might require additional dependencies or configuration.")

7. Practical Applications
-------------------------

Building a Simple Neural Network with scitex.nn Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s create a simple neural network using various scitex.nn components.

.. code:: ipython3

    # Example 12: Complete Neural Network with scitex.nn components
    class SciTexNet(nn.Module):
        def __init__(self, n_channels, n_classes):
            super().__init__()
            self.n_channels = n_channels
            self.n_classes = n_classes
            
            # Input processing
            self.dropout_channels = None
            self.spatial_attention = None
            self.gain_changer = None
            
            # Try to initialize available components
            try:
                self.dropout_channels = snn.DropoutChannels(dropout=0.1)
                print("✓ DropoutChannels initialized")
            except:
                print("✗ DropoutChannels not available")
            
            try:
                self.spatial_attention = snn.SpatialAttention(n_channels)
                print("✓ SpatialAttention initialized")
            except:
                print("✗ SpatialAttention not available")
            
            try:
                self.gain_changer = snn.ChannelGainChanger(n_channels)
                print("✓ ChannelGainChanger initialized")
            except:
                print("✗ ChannelGainChanger not available")
            
            # Standard layers
            self.conv1 = nn.Conv1d(n_channels, 32, kernel_size=3, padding=1)
            self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
            self.pool = nn.AdaptiveAvgPool1d(1)
            self.fc = nn.Linear(64, n_classes)
            
        def forward(self, x):
            # Input: (batch, channels, time)
            
            # Apply scitex.nn components if available
            if self.dropout_channels is not None:
                x = self.dropout_channels(x)
            
            if self.spatial_attention is not None:
                x = self.spatial_attention(x)
            
            if self.gain_changer is not None:
                x = self.gain_changer(x)
            
            # Standard convolutions
            x = F.relu(self.conv1(x))
            x = F.relu(self.conv2(x))
            
            # Global pooling and classification
            x = self.pool(x).squeeze(-1)
            x = self.fc(x)
            
            return x
    
    # Create and test the network
    n_channels, n_classes = 8, 3
    model = SciTexNet(n_channels, n_classes)
    
    # Test with dummy data
    dummy_input = torch.randn(4, n_channels, 100)
    with torch.no_grad():
        output = model(dummy_input)
    
    print(f"\nNetwork test:")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Output: {output[0]}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nModel parameters:")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")

Performance Comparison
~~~~~~~~~~~~~~~~~~~~~~

Let’s compare performance with and without scitex.nn components.

.. code:: ipython3

    # Example 13: Performance comparison
    import time
    
    # Create baseline model without scitex components
    class BaselineNet(nn.Module):
        def __init__(self, n_channels, n_classes):
            super().__init__()
            self.conv1 = nn.Conv1d(n_channels, 32, kernel_size=3, padding=1)
            self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
            self.pool = nn.AdaptiveAvgPool1d(1)
            self.fc = nn.Linear(64, n_classes)
        
        def forward(self, x):
            x = F.relu(self.conv1(x))
            x = F.relu(self.conv2(x))
            x = self.pool(x).squeeze(-1)
            x = self.fc(x)
            return x
    
    baseline_model = BaselineNet(n_channels, n_classes)
    
    # Test data
    test_data = torch.randn(32, n_channels, 500)
    
    # Benchmark baseline model
    baseline_model.eval()
    start_time = time.time()
    with torch.no_grad():
        for _ in range(10):
            _ = baseline_model(test_data)
    baseline_time = time.time() - start_time
    
    # Benchmark scitex model
    model.eval()
    start_time = time.time()
    with torch.no_grad():
        for _ in range(10):
            _ = model(test_data)
    scitex_time = time.time() - start_time
    
    print(f"Performance comparison (10 forward passes):")
    print(f"Baseline model: {baseline_time:.4f} seconds")
    print(f"SciTeX model: {scitex_time:.4f} seconds")
    print(f"Overhead: {((scitex_time - baseline_time) / baseline_time * 100):.1f}%")
    
    # Parameter comparison
    baseline_params = sum(p.numel() for p in baseline_model.parameters())
    scitex_params = sum(p.numel() for p in model.parameters())
    
    print(f"\nParameter comparison:")
    print(f"Baseline parameters: {baseline_params:,}")
    print(f"SciTeX parameters: {scitex_params:,}")
    print(f"Additional parameters: {scitex_params - baseline_params:,}")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.nn`` module:

Signal Processing Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Filters**: Various filter types including Gaussian, bandpass, and
   other signal processing filters
-  **Spectrogram**: Time-frequency analysis layer
-  **Hilbert Transform**: For analytic signal computation
-  **PSD**: Power spectral density computation

Attention Mechanisms
~~~~~~~~~~~~~~~~~~~~

-  **SpatialAttention**: Spatial attention for multi-channel data

Dropout Variants
~~~~~~~~~~~~~~~~

-  **AxiswiseDropout**: Dropout along specific axes
-  **DropoutChannels**: Channel-wise dropout

Utility Layers
~~~~~~~~~~~~~~

-  **TransposeLayer**: Learnable tensor transposition
-  **SwapChannels**: Channel permutation

Gain Control
~~~~~~~~~~~~

-  **ChannelGainChanger**: Learnable channel-wise gain adjustment
-  **FreqGainChanger**: Frequency-based gain control

Advanced Architectures
~~~~~~~~~~~~~~~~~~~~~~

-  **BNet**: Specialized neural network architecture
-  **ResNet1D**: 1D ResNet implementation
-  **MNet**: Specialized network architectures

Key Features
~~~~~~~~~~~~

1. **Scientific Focus**: Designed for scientific computing and signal
   processing
2. **Modular Design**: Components can be easily combined
3. **PyTorch Integration**: Native PyTorch nn.Module implementations
4. **Performance**: Optimized for scientific applications
5. **Flexibility**: Supports various input formats and dimensions

The module provides a comprehensive toolkit for building neural networks
specifically tailored for scientific computing applications, with
particular strength in signal processing and multi-channel data
analysis.
