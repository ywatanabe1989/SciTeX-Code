#!/usr/bin/env python3
"""Demonstrate how to fix colorbar overlap issues with scitex.plt"""

import numpy as np
import scitex.plt as plt
import scitex

# Example 1: Default behavior with improved spacing
print("Example 1: Default improved spacing (should work better now)")
fig1, axes1 = plt.subplots(2, 2, figsize=(12, 10))

# Create some test data similar to ModulationIndex example
for i, ax in enumerate(axes1.flat[:3]):  # First 3 axes get heatmaps
    data = np.random.randn(10, 10) * (i + 1)
    im = ax.imshow(data, aspect='auto', cmap='viridis')
    ax.set_title(f'Heatmap {i+1}')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    # Use default colorbar - should have better spacing now
    plt.colorbar(im, ax=ax)

# Last axis gets scatter plot
ax_scatter = axes1[1, 1]
x = np.random.randn(100)
y = np.random.randn(100)
c = np.random.randn(100)
scatter = ax_scatter.scatter(x, y, c=c, cmap='RdBu_r', vmin=-3, vmax=3)
ax_scatter.set_title('Scatter Plot')
ax_scatter.set_xlabel('X values')
ax_scatter.set_ylabel('Y values')
ax_scatter.grid(True, alpha=0.3)

# Call tight_layout - should work seamlessly with constrained_layout
plt.tight_layout()
scitex.io.save(fig1, "./colorbar_fix_example1.png")

# Example 2: Manual adjustment if needed
print("\nExample 2: Manual spacing adjustment")
fig2, axes2 = plt.subplots(2, 2, figsize=(12, 10))

for i, ax in enumerate(axes2.flat[:3]):
    data = np.random.randn(10, 10) * (i + 1)
    im = ax.imshow(data, aspect='auto', cmap='plasma')
    ax.set_title(f'Heatmap {i+1}')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    plt.colorbar(im, ax=ax)

# Manually adjust layout for even more space if needed
fig2.adjust_layout(w_pad=0.15, h_pad=0.15)
scitex.io.save(fig2, "./colorbar_fix_example2.png")

# Example 3: Shared colorbar approach (most space-efficient)
print("\nExample 3: Shared colorbar for similar data")
fig3, axes3 = plt.subplots(2, 2, figsize=(12, 10))

# Use same scale for all heatmaps
vmin, vmax = -2, 2
images = []

for i, ax in enumerate(axes3.flat):
    data = np.random.randn(10, 10)
    im = ax.imshow(data, aspect='auto', cmap='RdBu_r', vmin=vmin, vmax=vmax)
    ax.set_title(f'Panel {i+1}')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    images.append(im)

# Add a single colorbar for all subplots
from scitex.plt.utils import add_shared_colorbar
cbar = add_shared_colorbar(fig3, axes3, images[0], location='right')
cbar.set_label('Shared Scale')

scitex.io.save(fig3, "./colorbar_fix_example3.png")

# Example 4: Fix for existing code pattern (like ModulationIndex)
print("\nExample 4: Direct fix for ModulationIndex-style layout")
fig4, axes4 = plt.subplots(2, 2, figsize=(12, 10), 
                           constrained_layout={'w_pad': 0.15, 'h_pad': 0.1})

# Simulate the ModulationIndex layout
ax_orig = axes4[0, 0]
ax_surr = axes4[0, 1]
ax_z = axes4[1, 0]
ax_scatter = axes4[1, 1]

# Original MI
orig_data = np.random.rand(10, 10) * 0.005
im1 = ax_orig.imshow(orig_data, aspect='auto', cmap='viridis')
ax_orig.set_title('Original MI')
ax_orig.set_xlabel('Amplitude Freq')
ax_orig.set_ylabel('Phase Freq')
plt.colorbar(im1, ax=ax_orig)

# Surrogate Mean MI
surr_data = np.random.rand(10, 10) * 0.02
im2 = ax_surr.imshow(surr_data, aspect='auto', cmap='viridis')
ax_surr.set_title('Surrogate Mean MI')
ax_surr.set_xlabel('Amplitude Freq')
ax_surr.set_ylabel('Phase Freq')
plt.colorbar(im2, ax=ax_surr)

# Z-scores
z_data = np.random.randn(10, 10) * 2
im3 = ax_z.imshow(z_data, aspect='auto', cmap='RdBu_r', vmin=-3, vmax=3)
ax_z.set_title('Z-scores')
ax_z.set_xlabel('Amplitude Freq')
ax_z.set_ylabel('Phase Freq')
plt.colorbar(im3, ax=ax_z)

# Scatter plot
ax_scatter.scatter(orig_data.flatten(), surr_data.flatten(), 
                  c=z_data.flatten(), cmap='RdBu_r', vmin=-3, vmax=3)
ax_scatter.plot([0, orig_data.max()], [0, orig_data.max()], 'k--', alpha=0.5)
ax_scatter.set_title('Original vs Surrogate')
ax_scatter.set_xlabel('Original MI')
ax_scatter.set_ylabel('Surrogate Mean MI')
ax_scatter.grid(True, alpha=0.3)

plt.tight_layout()  # This is now safe and won't cause issues
scitex.io.save(fig4, "./colorbar_fix_example4_modulation_index_style.png")

print("\nAll examples saved! Check the output images.")
plt.close('all')