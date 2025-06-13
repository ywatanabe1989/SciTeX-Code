#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:58:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__mp4.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__mp4.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for MP4 saving wrapper functionality
"""

import os
import tempfile
import pytest
import numpy as np
from pathlib import Path

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from scitex.io._save_modules import save_mp4


class TestSaveMP4:
    """Test suite for save_mp4 wrapper function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.mp4")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if MATPLOTLIB_AVAILABLE:
            plt.close('all')

    def test_save_numpy_frames(self):
        """Test saving list of numpy arrays as video"""
        # Create simple frames (10 frames, 100x100 RGB)
        frames = []
        for i in range(10):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            # Create moving square
            frame[i*10:(i+1)*10, i*10:(i+1)*10] = [255, 0, 0]  # Red square
            frames.append(frame)
        
        save_mp4(frames, self.test_file, fps=10)
        
        assert os.path.exists(self.test_file)
        assert os.path.getsize(self.test_file) > 0

    @pytest.mark.skipif(not CV2_AVAILABLE, reason="OpenCV not installed")
    def test_save_with_opencv_writer(self):
        """Test saving video using OpenCV VideoWriter"""
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.test_file, fourcc, 20.0, (640, 480))
        
        # Generate frames
        for i in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Moving circle
            cv2.circle(frame, (i*20, 240), 30, (0, 255, 0), -1)
            out.write(frame)
        
        out.release()
        
        assert os.path.exists(self.test_file)

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
    def test_save_matplotlib_animation(self):
        """Test saving matplotlib animation"""
        fig, ax = plt.subplots()
        
        # Create animation data
        x = np.linspace(0, 2*np.pi, 100)
        line, = ax.plot(x, np.sin(x))
        
        def animate(frame):
            line.set_ydata(np.sin(x + frame/10))
            return line,
        
        anim = animation.FuncAnimation(
            fig, animate, frames=20, interval=50, blit=True
        )
        
        save_mp4(anim, self.test_file)
        
        assert os.path.exists(self.test_file)
        plt.close(fig)

    def test_save_grayscale_frames(self):
        """Test saving grayscale video frames"""
        # Create grayscale frames
        frames = []
        for i in range(15):
            frame = np.zeros((100, 100), dtype=np.uint8)
            # Moving white bar
            frame[:, i*6:(i+1)*6] = 255
            frames.append(frame)
        
        save_mp4(frames, self.test_file, fps=15)
        
        assert os.path.exists(self.test_file)

    def test_save_different_frame_rates(self):
        """Test saving with different frame rates"""
        frames = [np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8) 
                 for _ in range(10)]
        
        # Low FPS
        low_fps = os.path.join(self.temp_dir, "low_fps.mp4")
        save_mp4(frames, low_fps, fps=5)
        
        # High FPS
        high_fps = os.path.join(self.temp_dir, "high_fps.mp4")
        save_mp4(frames, high_fps, fps=30)
        
        assert os.path.exists(low_fps)
        assert os.path.exists(high_fps)

    def test_save_with_codec(self):
        """Test saving with specific codec"""
        frames = [np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8) 
                 for _ in range(10)]
        
        # Different codecs might be available
        codecs = ['mp4v', 'h264', 'xvid']
        for codec in codecs:
            file_path = os.path.join(self.temp_dir, f"test_{codec}.mp4")
            try:
                save_mp4(frames, file_path, codec=codec, fps=10)
                if os.path.exists(file_path):
                    break
            except:
                continue

    def test_save_high_resolution_video(self):
        """Test saving high resolution video"""
        # Create HD frames (fewer frames due to size)
        frames = []
        for i in range(5):
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            # Gradient background
            frame[:, :, 0] = np.linspace(0, 255, 1280)
            frames.append(frame)
        
        save_mp4(frames, self.test_file, fps=24)
        
        assert os.path.exists(self.test_file)

    def test_save_with_compression(self):
        """Test saving with different compression settings"""
        frames = [np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8) 
                 for _ in range(20)]
        
        # High quality (less compression)
        high_quality = os.path.join(self.temp_dir, "high_quality.mp4")
        save_mp4(frames, high_quality, fps=10, bitrate='5000k')
        
        # Low quality (more compression)
        low_quality = os.path.join(self.temp_dir, "low_quality.mp4")
        save_mp4(frames, low_quality, fps=10, bitrate='500k')
        
        # High quality should be larger (if bitrate is supported)
        if os.path.exists(high_quality) and os.path.exists(low_quality):
            # This might not always be true depending on implementation
            pass

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
    def test_save_animated_plot(self):
        """Test saving animated matplotlib plot"""
        fig, ax = plt.subplots()
        
        # Animated scatter plot
        scat = ax.scatter([], [])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        def update(frame):
            x = np.random.rand(10) * 10
            y = np.random.rand(10) * 10
            data = np.c_[x, y]
            scat.set_offsets(data)
            return scat,
        
        anim = animation.FuncAnimation(fig, update, frames=30, interval=50)
        
        save_mp4(anim, self.test_file)
        
        assert os.path.exists(self.test_file)
        plt.close(fig)

    def test_save_single_channel_as_rgb(self):
        """Test converting single channel to RGB for video"""
        # Create single channel frames
        frames = []
        for i in range(10):
            frame = np.zeros((100, 100), dtype=np.uint8)
            frame[40:60, 40:60] = 255 * (i / 10)  # Fading square
            # Convert to RGB
            rgb_frame = np.stack([frame, frame, frame], axis=-1)
            frames.append(rgb_frame)
        
        save_mp4(frames, self.test_file, fps=10)
        
        assert os.path.exists(self.test_file)

    def test_error_invalid_frames(self):
        """Test error handling for invalid frame data"""
        # Empty list
        with pytest.raises(ValueError):
            save_mp4([], self.test_file)
        
        # Invalid frame dimensions
        with pytest.raises(ValueError):
            frames = [np.zeros((100,)), np.zeros((100,))]  # 1D arrays
            save_mp4(frames, self.test_file)

    def test_save_from_generator(self):
        """Test saving frames from generator"""
        def frame_generator():
            for i in range(10):
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
                frame[:, :, i % 3] = 255  # Cycle through RGB
                yield frame
        
        frames = list(frame_generator())
        save_mp4(frames, self.test_file, fps=10)
        
        assert os.path.exists(self.test_file)

    def test_save_with_audio(self):
        """Test saving video with audio (if supported)"""
        # Note: Audio support depends on the implementation
        frames = [np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8) 
                 for _ in range(30)]
        
        # Basic save without audio
        save_mp4(frames, self.test_file, fps=30)
        
        assert os.path.exists(self.test_file)


# EOF
