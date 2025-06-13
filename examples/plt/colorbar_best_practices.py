#!/usr/bin/env python3
"""Best practices for using colorbars with scitex.plt"""

import numpy as np
import scitex.plt as plt

# Example 1: Default behavior - constrained_layout handles colorbars automatically
print("Example 1: Default constrained_layout")
fig1, axes1 = plt.subplots(2, 2, figsize=(10, 8))

for i, ax in enumerate(axes1.flat):
    data = np.random.randn(10, 10) * (i + 1)
    im = ax.imshow(data, aspect='auto', cmap='viridis')
    ax.set_title(f'Panel {i+1}')
    plt.colorbar(im, ax=ax)

# tight_layout() call is harmless but does nothing with constrained_layout
plt.tight_layout()
scitex.io.save(fig1, "./colorbar_example1_default.png")

# Example 2: Adjusting layout parameters for tighter spacing
print("\nExample 2: Adjusted spacing")
fig2, axes2 = plt.subplots(2, 2, figsize=(10, 8))

for i, ax in enumerate(axes2.flat):
    data = np.random.randn(10, 10) * (i + 1)
    im = ax.imshow(data, aspect='auto', cmap='plasma')
    ax.set_title(f'Panel {i+1}')
    plt.colorbar(im, ax=ax)

# Fine-tune the spacing
fig2.adjust_layout(w_pad=0.03, h_pad=0.03, wspace=0.01, hspace=0.01)
scitex.io.save(fig2, "./colorbar_example2_adjusted.png")

# Example 3: Shared colorbar for multiple axes
print("\nExample 3: Shared colorbar")
fig3, axes3 = plt.subplots(2, 2, figsize=(10, 8))

# Use same data range for all plots
vmin, vmax = -3, 3
images = []

for i, ax in enumerate(axes3.flat):
    data = np.random.randn(10, 10)
    im = ax.imshow(data, aspect='auto', cmap='RdBu_r', vmin=vmin, vmax=vmax)
    ax.set_title(f'Panel {i+1}')
    images.append(im)

# Create a single colorbar for all subplots
cbar = plt.colorbar(images[0], ax=axes3, location='right', shrink=0.8)
cbar.set_label('Values')

scitex.io.save(fig3, "./colorbar_example3_shared.png")

# Example 4: Disable constrained_layout for manual control
print("\nExample 4: Manual layout control")
fig4, axes4 = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=False)

for i, ax in enumerate(axes4.flat):
    data = np.random.randn(10, 10) * (i + 1)
    im = ax.imshow(data, aspect='auto', cmap='coolwarm')
    ax.set_title(f'Panel {i+1}')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# Use traditional tight_layout with custom rect
fig4.tight_layout(rect=[0, 0.03, 1, 0.95])
scitex.io.save(fig4, "./colorbar_example4_manual.png")

print("\nExamples saved!")
plt.close('all')