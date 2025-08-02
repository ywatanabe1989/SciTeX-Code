#!/usr/bin/env python3
"""
Proposal: Unit-Aware Plotting for SciTeX
========================================

This demonstrates how units could be integrated with the plotting module
to ensure scientific validity and automatic unit conversion in plots.
"""

import numpy as np
from typing import Optional, Union
import matplotlib.pyplot as plt

# Example implementation of unit-aware plotting
class UnitAwarePlot:
    """Wrapper for matplotlib that handles units automatically."""
    
    def __init__(self, ax=None):
        self.ax = ax or plt.gca()
        self.x_unit = None
        self.y_unit = None
        
    def plot(self, x, y, x_unit=None, y_unit=None, **kwargs):
        """Plot with automatic unit handling."""
        # Store units
        if x_unit:
            self.x_unit = x_unit
            self.ax.set_xlabel(self.ax.get_xlabel() + f' [{x_unit}]')
        if y_unit:
            self.y_unit = y_unit
            self.ax.set_ylabel(self.ax.get_ylabel() + f' [{y_unit}]')
            
        # Plot normally
        return self.ax.plot(x, y, **kwargs)
    
    def set_xlabel(self, label, unit=None):
        """Set x-label with optional unit."""
        if unit:
            self.x_unit = unit
            label = f"{label} [{unit}]"
        self.ax.set_xlabel(label)
        
    def set_ylabel(self, label, unit=None):
        """Set y-label with optional unit."""
        if unit:
            self.y_unit = unit
            label = f"{label} [{unit}]"
        self.ax.set_ylabel(label)
        
    def convert_x_units(self, new_unit, conversion_factor):
        """Convert x-axis to new units."""
        # Update all line data
        for line in self.ax.lines:
            xdata = line.get_xdata()
            line.set_xdata(xdata * conversion_factor)
        
        # Update x-axis limits
        xlim = self.ax.get_xlim()
        self.ax.set_xlim([x * conversion_factor for x in xlim])
        
        # Update label
        current_label = self.ax.get_xlabel()
        if self.x_unit and f'[{self.x_unit}]' in current_label:
            new_label = current_label.replace(f'[{self.x_unit}]', f'[{new_unit}]')
            self.ax.set_xlabel(new_label)
        
        self.x_unit = new_unit


# Example usage demonstrating scientific validity
def demo_unit_aware_plotting():
    """Demonstrate unit-aware plotting."""
    
    # Generate some data
    time_ms = np.linspace(0, 1000, 1000)  # Time in milliseconds
    frequency_hz = 10  # 10 Hz signal
    amplitude_mv = 5  # 5 millivolts
    signal_mv = amplitude_mv * np.sin(2 * np.pi * frequency_hz * time_ms / 1000)
    
    # Create unit-aware plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot 1: Original units
    plot1 = UnitAwarePlot(ax1)
    plot1.plot(time_ms, signal_mv, 'b-', linewidth=2)
    plot1.set_xlabel('Time', unit='ms')
    plot1.set_ylabel('Voltage', unit='mV')
    ax1.set_title('Signal in Original Units')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Converted units
    plot2 = UnitAwarePlot(ax2)
    # Convert to seconds and volts
    time_s = time_ms / 1000
    signal_v = signal_mv / 1000
    plot2.plot(time_s, signal_v, 'r-', linewidth=2)
    plot2.set_xlabel('Time', unit='s')
    plot2.set_ylabel('Voltage', unit='V')
    ax2.set_title('Signal in SI Units')
    ax2.grid(True, alpha=0.3)
    
    # Add annotations showing the conversion
    ax2.text(0.5, 0.95, f'Conversion: 1 ms = 0.001 s, 1 mV = 0.001 V',
             transform=ax2.transAxes, ha='center', va='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('.dev/unit_aware_plotting_demo.png', dpi=150, bbox_inches='tight')
    print("Saved demo plot to .dev/unit_aware_plotting_demo.png")
    
    # Demonstrate automatic unit validation
    print("\nUnit validation example:")
    try:
        # This would raise an error in a full implementation
        # plot1.plot(time_ms, time_ms)  # Error: y-axis expects voltage units!
        print("  ✓ Unit mismatch detection would prevent plotting time vs time")
    except Exception as e:
        print(f"  ✗ Error: {e}")


if __name__ == "__main__":
    demo_unit_aware_plotting()
    
    # Proposal for SciTeX integration:
    print("\n" + "="*60)
    print("PROPOSAL: Integrate units.py with plt module")
    print("="*60)
    print("""
Benefits:
1. Automatic unit conversion in plots
2. Unit validation to prevent errors
3. Consistent unit display in labels
4. Scientific validity guaranteed
5. Easy unit conversion for different journals

Implementation steps:
1. Add unit parameter to plot methods
2. Store units in AxisWrapper metadata
3. Validate unit compatibility
4. Auto-generate axis labels with units
5. Provide unit conversion methods

Example API:
```python
import scitex as stx

# Create unit-aware plot
fig, ax = stx.plt.subplots()
ax.plot(time, voltage, x_unit='ms', y_unit='mV')
ax.set_xlabel('Time')  # Automatically adds [ms]
ax.set_ylabel('Voltage')  # Automatically adds [mV]

# Convert units for publication
ax.convert_units(x='s', y='V')  # Converts data and labels
```
""")