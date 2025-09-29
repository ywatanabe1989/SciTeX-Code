#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 09:15:59 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/_listen.py

import os
import sys

import matplotlib.pyplot as plt
import sounddevice as sd

os.environ["PULSE_SERVER"] = "unix:/mnt/wslg/PulseServer"

# # WSL2 Sound Support
# export PULSE_SERVER=unix:/mnt/wslg/PulseServer


def list_and_select_device() -> int:
    """
    List available audio devices and prompt user to select one.

    Example
    -------
    >>> device_id = list_and_select_device()
    Available audio devices:
    ...
    Enter the ID of the device you want to use:

    Returns
    -------
    int
        Selected device ID
    """
    try:
        print("Available audio devices:")
        devices = sd.query_devices()
        print(devices)
        device_id = int(input("Enter the ID of the device you want to use: "))
        if device_id not in range(len(devices)):
            raise ValueError(f"Invalid device ID: {device_id}")
        return device_id
    except (ValueError, sd.PortAudioError) as err:
        print(f"Error during device selection: {err}")
        return 0


if __name__ == "__main__":
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    signal, time_points, sampling_freq = scitex.dsp.demo_sig("chirp")

    device_id = list_and_select_device()
    sd.default.device = device_id

    listen(signal, sampling_freq)

    scitex.session.close(CONFIG)

# def play_audio(
#     samples: np.ndarray, fs: int = 44100, channels: int = 1
# ) -> None:
#     """Play audio using PyAudio"""
#     print("Initializing PyAudio...")
#     p = pyaudio.PyAudio()

#     # List available devices
#     print("\nAvailable audio devices:")
#     for i in range(p.get_device_count()):
#         dev = p.get_device_info_by_index(i)
#         print(f"Device {i}: {dev['name']}")

#     try:
#         # Rest of the code remains the same
#         if samples.dtype != np.float32:
#             print(f"Converting from {samples.dtype} to float32...")
#             samples = samples.astype(np.float32)

#         if len(samples) == 0:
#             print("No input samples, creating test tone...")
#             duration = 1
#             t = np.linspace(0, duration, int(fs * duration))
#             samples = np.sin(2 * np.pi * 440 * t)

#         print(f"Opening audio stream (fs={fs}Hz, channels={channels})...")
#         stream = p.open(
#             format=pyaudio.paFloat32, channels=channels, rate=fs, output=True
#         )

#         print("Playing audio...")
#         stream.write(samples.tobytes())

#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         print("Cleaning up...")
#         if "stream" in locals():
#             stream.stop_stream()
#             stream.close()
#         p.terminate()
#         print("Done.")

# if __name__ == "__main__":
#     # Test with a simple sine wave
#     duration = 2
#     fs = 44100
#     t = np.linspace(0, duration, int(fs * duration))
#     test_signal = np.sin(2 * np.pi * 440 * t)  # 440 Hz
#     play_audio(test_signal, fs)

# # def record_audio(
# #     duration: float = 5.0, fs: int = 44100, channels: int = 1
# # ) -> np.ndarray:
# #     """Record audio using PyAudio with WSL2 compatibility"""
# #     chunk = 1024
# #     format = pyaudio.paFloat32

# #     p = pyaudio.PyAudio()

# #     # List available devices
# #     for i in range(p.get_device_count()):
# #         print(p.get_device_info_by_index(i))

# #     try:
# #         stream = p.open(
# #             format=format,
# #             channels=channels,
# #             rate=fs,
# #             input=True,
# #             frames_per_buffer=chunk,
# #             input_device_index=None,  # Use default device
# #         )

# #         frames = []
# #         print("Recording...")

# #         for _ in range(0, int(fs / chunk * duration)):
# #             data = stream.read(chunk)
# #             frames.append(data)

# #         print("Done recording")
# #         return np.frombuffer(b"".join(frames), dtype=np.float32)

# #     finally:
# #         if "stream" in locals():
# #             stream.stop_stream()
# #             stream.close()
# #         p.terminate()

# # def record_audio(
# #     duration: float = 5.0, fs: int = 44100, channels: int = 1
# # ) -> np.ndarray:
# #     """
# #     Record audio using PyAudio.
# #     """
# #     chunk = 1024
# #     format = pyaudio.paFloat32

# #     p = pyaudio.PyAudio()

# #     stream = p.open(
# #         format=format,
# #         channels=channels,
# #         rate=fs,
# #         input=True,
# #         frames_per_buffer=chunk,
# #     )

# #     frames = []

# #     for _ in range(0, int(fs / chunk * duration)):
# #         data = stream.read(chunk)
# #         frames.append(data)

# #     stream.stop_stream()
# #     stream.close()
# #     p.terminate()

# #     return np.frombuffer(b"".join(frames), dtype=np.float32)

# # if __name__ == "__main__":
# #     # Test recording
# #     audio = record_audio(duration=3.0)
# #     print(f"Recorded {len(audio)} samples")

# # # #!/usr/bin/env python3
# # # # -*- coding: utf-8 -*-
# # # # Time-stamp: "2024-11-08 08:56:12 (ywatanabe)"
# # # # File: ./scitex_repo/src/scitex/dsp/_listen.py

# # # import os
# # # import sys
# # # from typing import Any, Dict, Literal, Tuple

# # # import matplotlib.pyplot as plt
# # # import scitex
# # # import numpy as np
# # # from scipy.signal import resample

# # # os.environ["DISPLAY"] = ":0"  # Set a default display

# # # # Avoid GUI/clipboard dependencies
# # # def dummy_clipboard_get():
# # #     raise NotImplementedError(
# # #         "Clipboard not available in headless environment"
# # #     )

# # # try:
# # #     from IPython import get_ipython

# # #     ipython = get_ipython()
# # #     if ipython is not None:
# # #         ipython.hooks.clipboard_get = dummy_clipboard_get
# # # except ImportError:
# # #     pass

# # # """
# # # Functionality:
# # #     - Provides audio playback and signal sonification functionality
# # #     - Supports multiple sonification methods (frequency shift, AM/FM Modulation)
# # #     - Includes device selection and audio information display utilities
# # # Input:
# # #     - Multichannel signal arrays (numpy.ndarray)
# # #     - Sampling frequency and sonification parameters
# # # Output:
# # #     - Audio playback through specified output device
# # # Prerequisites:
# # #     - PortAudio library (install with: sudo apt-get install portaudio19-dev)
# # #     - sounddevice package
# # # """

# # # """Imports"""
# # # """Config"""
# # # CONFIG = scitex.gen.load_configs()

# # # """Functions"""

# # # def frequency_shift(
# # #     signal: np.ndarray,
# # #     shift_factor: int = 200,
# # # ) -> np.ndarray:
# # #     """
# # #     Shift signal frequencies by resampling.

# # #     Example
# # #     -------
# # #     >>> signal = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000))
# # #     >>> shifted = frequency_shift(signal, shift_factor=200)

# # #     Parameters
# # #     ----------
# # #     signal : np.ndarray
# # #         Input signal to be frequency shifted
# # #     shift_factor : int
# # #         Frequency multiplication factor

# # #     Returns
# # #     -------
# # #     np.ndarray
# # #         Frequency shifted signal
# # #     """
# # #     num_samples = int(len(signal) * shift_factor)
# # #     return resample(signal, num_samples)

# # # def am_Modulation(
# # #     signal: np.ndarray, carrier_freq: float = 440, fs: int = 44_100
# # # ) -> np.ndarray:
# # #     """
# # #     Perform amplitude Modulation on input signal.

# # #     Example
# # #     -------
# # #     >>> signal = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000))
# # #     >>> modulated = am_Modulation(signal, carrier_freq=440, fs=44100)

# # #     Parameters
# # #     ----------
# # #     signal : np.ndarray
# # #         Input signal to modulate
# # #     carrier_freq : float
# # #         Carrier frequency in Hz
# # #     fs : int
# # #         Sampling frequency in Hz

# # #     Returns
# # #     -------
# # #     np.ndarray
# # #         Amplitude modulated signal
# # #     """
# # #     t = np.arange(len(signal)) / fs
# # #     carrier = np.sin(2 * np.pi * carrier_freq * t)
# # #     return (1 + signal) * carrier

# # # def fm_Modulation(
# # #     signal: np.ndarray,
# # #     carrier_freq: float = 440,
# # #     sensitivity: float = 0.5,
# # #     fs: int = 44_100,
# # # ) -> np.ndarray:
# # #     """
# # #     Perform frequency Modulation on input signal.

# # #     Example
# # #     -------
# # #     >>> signal = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 1000))
# # #     >>> modulated = fm_Modulation(signal, carrier_freq=440, sensitivity=0.5, fs=44100)

# # #     Parameters
# # #     ----------
# # #     signal : np.ndarray
# # #         Input signal to modulate
# # #     carrier_freq : float
# # #         Carrier frequency in Hz
# # #     sensitivity : float
# # #         Frequency sensitivity factor
# # #     fs : int
# # #         Sampling frequency in Hz

# # #     Returns
# # #     -------
# # #     np.ndarray
# # #         Frequency modulated signal
# # #     """
# # #     t = np.arange(len(signal)) / fs
# # #     phase = 2 * np.pi * carrier_freq * t + sensitivity * np.cumsum(signal) / fs
# # #     return np.sin(phase)

# # # def sonify_eeg(
# # #     signal_array: np.ndarray,
# # #     sampling_freq: int,
# # #     method: Literal["shift", "am", "fm"] = "shift",
# # #     channels: Tuple[int, ...] = (0, 1),
# # #     target_fs: int = 44_100,
# # #     **kwargs: Dict[str, Any],
# # # ) -> None:
# # #     """
# # #     Convert EEG signal to audio using various sonification methods.

# # #     Example
# # #     -------
# # #     >>> eeg_data = np.random.randn(1, 32, 1000)  # Mock EEG data
# # #     >>> sonify_eeg(eeg_data, 250, method='fm', channels=(0,1))

# # #     Parameters
# # #     ----------
# # #     signal_array : np.ndarray
# # #         EEG signal array of shape (batch_size, n_channels, sequence_length)
# # #     sampling_freq : int
# # #         Original sampling frequency of the EEG signal
# # #     method : {'shift', 'am', 'fm'}
# # #         Sonification method to use
# # #     channels : Tuple[int, ...]
# # #         Channels to include in sonification
# # #     target_fs : int
# # #         Target audio sampling frequency
# # #     **kwargs : Dict[str, Any]
# # #         Additional parameters for specific sonification methods

# # #     Returns
# # #     -------
# # #     None
# # #     """

# # #     if not isinstance(signal_array, np.ndarray):
# # #         signal_array = np.array(signal_array)

# # #     if len(signal_array.shape) != 3:
# # #         raise ValueError(f"Expected 3D array, got shape {signal_array.shape}")

# # #     if max(channels) >= signal_array.shape[1]:
# # #         raise ValueError(
# # #             f"Channel index {max(channels)} out of range (max: {signal_array.shape[1]-1})"
# # #         )

# # #     selected_channels = signal_array[:, channels, :].mean(axis=1)
# # #     signal = selected_channels.mean(axis=0)

# # #     # Normalize
# # #     signal = signal / np.max(np.abs(signal))

# # #     # Apply selected method
# # #     if method == "shift":
# # #         audio = frequency_shift(signal, kwargs.get("shift_factor", 200))
# # #     elif method == "am":
# # #         audio = am_Modulation(
# # #             signal, kwargs.get("carrier_freq", 440), target_fs
# # #         )
# # #     elif method == "fm":
# # #         audio = fm_Modulation(
# # #             signal,
# # #             kwargs.get("carrier_freq", 440),
# # #             kwargs.get("sensitivity", 0.5),
# # #             target_fs,
# # #         )
# # #     else:
# # #         raise ValueError(f"Unknown method: {method}")

# # #     if len(audio) < 100:
# # #         raise ValueError("Audio signal too short after processing")

# # #     sd.play(audio, target_fs)
# # #     sd.wait()

# # # def listen(
# # #     signal_array: np.ndarray,
# # #     sampling_freq: int,
# # #     channels: Tuple[int, ...] = (0, 1),
# # #     target_fs: int = 44_100,
# # # ) -> None:
# # #     """
# # #     Play selected channels of a multichannel signal array as audio.

# # #     Example
# # #     -------
# # #     >>> signal = np.random.randn(1, 2, 1000)  # Random stereo signal
# # #     >>> listen(signal, 16000, channels=(0, 1))

# # #     Parameters
# # #     ----------
# # #     signal_array : np.ndarray
# # #         Signal array of shape (batch_size, n_channels, sequence_length)
# # #     sampling_freq : int
# # #         Original sampling frequency of the signal
# # #     channels : Tuple[int, ...]
# # #         Tuple of channel indices to listen to
# # #     target_fs : int
# # #         Target sampling frequency for playback

# # #     Returns
# # #     -------
# # #     None
# # #     """
# # #     if not isinstance(signal_array, np.ndarray):
# # #         signal_array = np.array(signal_array)

# # #     if len(signal_array.shape) != 3:
# # #         raise ValueError(f"Expected 3D array, got shape {signal_array.shape}")

# # #     if max(channels) >= signal_array.shape[1]:
# # #         raise ValueError(
# # #             f"Channel index {max(channels)} out of range (max: {signal_array.shape[1]-1})"
# # #         )

# # #     selected_channels = signal_array[:, channels, :].mean(axis=1)
# # #     audio_signal = selected_channels.mean(axis=0)

# # #     if sampling_freq != target_fs:
# # #         num_samples = int(round(len(audio_signal) * target_fs / sampling_freq))
# # #         audio_signal = resample(audio_signal, num_samples)

# # #     sd.play(audio_signal, target_fs)
# # #     sd.wait()

# # # def print_device_info() -> None:
# # #     """
# # #     Display information about the default audio output device.

# # #     Example
# # #     -------
# # #     >>> print_device_info()
# # #     Default Output Device Info:
# # #     <device info details>
# # #     """
# # #     try:
# # #         device_info = sd.query_devices(kind="output")
# # #         print(f"Default Output Device Info: \n{device_info}")
# # #     except sd.PortAudioError as err:
# # #         print(f"Error querying audio devices: {err}")

# # # if __name__ == "__main__":
# # #     import scitex

# # #     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

# # #     # Generate a test signal if demo_sig fails
# # #     try:
# # #         signal, time_points, sampling_freq = scitex.dsp.demo_sig("chirp")
# # #     except Exception as err:
# # #         print(f"Failed to load demo signal: {err}")
# # #         # Generate a simple test signal
# # #         duration = 2  # seconds
# # #         sampling_freq = 1000  # Hz
# # #         t = np.linspace(0, duration, int(duration * sampling_freq))
# # #         test_signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz sine wave
# # #         signal = test_signal.reshape(1, 1, -1)

# # #     # Try to get audio device
# # #     try:
# # #         device_id = list_and_select_device()
# # #         sd.default.device = device_id
# # #     except Exception as err:
# # #         print(f"Failed to set audio device: {err}")
# # #         print("Using default audio device")
# # #         device_id = None

# # #     # Test different sonification methods with error handling
# # #     methods = ["shift", "am", "fm"]
# # #     for method in methods:
# # #         try:
# # #             print(f"\nTesting {method} sonification...")
# # #             sonify_eeg(signal, sampling_freq, method=method)
# # #         except Exception as err:
# # #             print(f"Failed to play {method} sonification: {err}")

# # #     scitex.session.close(CONFIG)

# # # # EOF

# # # # #!/usr/bin/env python3
# # # # # -*- coding: utf-8 -*-
# # # # # Time-stamp: "2024-11-07 18:58:37 (ywatanabe)"
# # # # # File: ./scitex_repo/src/scitex/dsp/_listen.py

# # # # import sys
# # # # from typing import Tuple

# # # # import matplotlib.pyplot as plt
# # # # import scitex
# # # # import numpy as np
# # # # import sounddevice as sd
# # # # from scipy.signal import resample

# # # # """
# # # # Functionality:
# # # #     - Provides audio playback functionality for multichannel signal arrays
# # # #     - Includes device selection and audio information display utilities
# # # # Input:
# # # #     - Multichannel signal arrays (numpy.ndarray)
# # # #     - Sampling frequency and channel selection
# # # # Output:
# # # #     - Audio playback through specified output device
# # # # Prerequisites:
# # # #     - PortAudio library (install with: sudo apt-get install portaudio19-dev)
# # # #     - sounddevice package
# # # # """

# # # # """Imports"""
# # # # """Config"""
# # # # CONFIG = scitex.gen.load_configs()

# # # # """Functions"""
# # # # def listen(
# # # #     signal_array: np.ndarray,
# # # #     sampling_freq: int,
# # # #     channels: Tuple[int, ...] = (0, 1),
# # # #     target_fs: int = 44_100,
# # # # ) -> None:
# # # #     """
# # # #     Play selected channels of a multichannel signal array as audio.

# # # #     Example
# # # #     -------
# # # #     >>> signal = np.random.randn(1, 2, 1000)  # Random stereo signal
# # # #     >>> listen(signal, 16000, channels=(0, 1))

# # # #     Parameters
# # # #     ----------
# # # #     signal_array : np.ndarray
# # # #         Signal array of shape (batch_size, n_channels, sequence_length)
# # # #     sampling_freq : int
# # # #         Original sampling frequency of the signal
# # # #     channels : Tuple[int, ...]
# # # #         Tuple of channel indices to listen to
# # # #     target_fs : int
# # # #         Target sampling frequency for playback

# # # #     Returns
# # # #     -------
# # # #     None
# # # #     """
# # # #     if not isinstance(signal_array, np.ndarray):
# # # #         signal_array = np.array(signal_array)

# # # #     if len(signal_array.shape) != 3:
# # # #         raise ValueError(f"Expected 3D array, got shape {signal_array.shape}")

# # # #     if max(channels) >= signal_array.shape[1]:
# # # #         raise ValueError(f"Channel index {max(channels)} out of range (max: {signal_array.shape[1]-1})")

# # # #     selected_channels = signal_array[:, channels, :].mean(axis=1)
# # # #     audio_signal = selected_channels.mean(axis=0)

# # # #     if sampling_freq != target_fs:
# # # #         num_samples = int(round(len(audio_signal) * target_fs / sampling_freq))
# # # #         audio_signal = resample(audio_signal, num_samples)

# # # #     sd.play(audio_signal, target_fs)
# # # #     sd.wait()

# # # # def print_device_info() -> None:
# # # #     """
# # # #     Display information about the default audio output device.

# # # #     Example
# # # #     -------
# # # #     >>> print_device_info()
# # # #     Default Output Device Info:
# # # #     <device info details>
# # # #     """
# # # #     try:
# # # #         device_info = sd.query_devices(kind="output")
# # # #         print(f"Default Output Device Info: \n{device_info}")
# # # #     except sd.PortAudioError as err:
# # # #         print(f"Error querying audio devices: {err}")

# # # # def list_and_select_device() -> int:
# # # #     """
# # # #     List available audio devices and prompt user to select one.

# # # #     Example
# # # #     -------
# # # #     >>> device_id = list_and_select_device()
# # # #     Available audio devices:
# # # #     ...
# # # #     Enter the ID of the device you want to use:

# # # #     Returns
# # # #     -------
# # # #     int
# # # #         Selected device ID
# # # #     """
# # # #     try:
# # # #         print("Available audio devices:")
# # # #         devices = sd.query_devices()
# # # #         print(devices)
# # # #         device_id = int(input("Enter the ID of the device you want to use: "))
# # # #         if device_id not in range(len(devices)):
# # # #             raise ValueError(f"Invalid device ID: {device_id}")
# # # #         return device_id
# # # #     except (ValueError, sd.PortAudioError) as err:
# # # #         print(f"Error during device selection: {err}")
# # # #         return 0

# # # # def frequency_shift(signal: np.ndarray, shift_factor: int = 200) -> np.ndarray:
# # # #     """Direct frequency shifting"""
# # # #     num_samples = int(len(signal) * shift_factor)
# # # #     return resample(signal, num_samples)

# # # # def am_Modulation(signal: np.ndarray, carrier_freq: float = 440, fs: int = 44100) -> np.ndarray:
# # # #     """Amplitude Modulation"""
# # # #     t = np.arange(len(signal)) / fs
# # # #     carrier = np.sin(2 * np.pi * carrier_freq * t)
# # # #     return (1 + signal) * carrier

# # # # def fm_Modulation(signal: np.ndarray, carrier_freq: float = 440, sens: float = 0.5, fs: int = 44100) -> np.ndarray:
# # # #     """Frequency Modulation"""
# # # #     t = np.arange(len(signal)) / fs
# # # #     phase = 2 * np.pi * carrier_freq * t + sens * np.cumsum(signal) / fs
# # # #     return np.sin(phase)

# # # # def sonify_eeg(
# # # #     signal_array: np.ndarray,
# # # #     sampling_freq: int,
# # # #     method: str = 'shift',
# # # #     channels: Tuple[int, ...] = (0, 1),
# # # #     target_fs: int = 44100,
# # # #     **kwargs
# # # # ) -> None:
# # # #     """Main sonification function"""
# # # #     selected_channels = signal_array[:, channels, :].mean(axis=1)
# # # #     signal = selected_channels.mean(axis=0)

# # # #     # Normalize
# # # #     signal = signal / np.max(np.abs(signal))

# # # #     # Apply selected method
# # # #     if method == 'shift':
# # # #         audio = frequency_shift(signal, kwargs.get('shift_factor', 200))
# # # #     elif method == 'am':
# # # #         audio = am_Modulation(signal, kwargs.get('carrier_freq', 440), target_fs)
# # # #     elif method == 'fm':
# # # #         audio = fm_Modulation(signal, kwargs.get('carrier_freq', 440), kwargs.get('sensitivity', 0.5), target_fs)
# # # #     else:
# # # #         raise ValueError(f"Unknown method: {method}")

# # # #     sd.play(audio, target_fs)
# # # #     sd.wait()

# # # # if __name__ == "__main__":
# # # #     import scitex

# # # #     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

# # # #     signal, time_points, sampling_freq = scitex.dsp.demo_sig("chirp")

# # # #     device_id = list_and_select_device()
# # # #     sd.default.device = device_id

# # # #     listen(signal, sampling_freq)

# # # #     scitex.session.close(CONFIG)

# # # #

# # #

# #

#

# EOF
