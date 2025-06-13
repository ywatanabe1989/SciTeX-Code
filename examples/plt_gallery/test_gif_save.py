#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test GIF saving functionality."""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import numpy as np
import scitex

# Create a simple plot
fig, ax = scitex.plt.subplots(figsize=(8, 6))
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='sin(x)', id='sin_wave')
ax.plot(x, np.cos(x), label='cos(x)', id='cos_wave')
ax.set_xyt(x='X-axis', y='Y-axis', t='Test GIF Export')
ax.legend()

# Save as GIF
output_path = "/data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/examples/plt_gallery/figures/test_export.gif"
scitex.io.save(fig, output_path)

print("GIF saving test completed!")