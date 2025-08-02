# Unit-Aware Plotting Documentation
Date: 2025-08-01  
Agent: Scientific Validity Specialist

## Overview

SciTeX now includes comprehensive unit-aware plotting capabilities that ensure scientific validity by tracking, displaying, and converting physical units automatically. This feature integrates seamlessly with the existing plotting infrastructure through the `UnitAwareMixin`.

## Key Features

### 1. Automatic Unit Tracking
- Units are automatically displayed in axis labels
- Unit information is preserved throughout plotting operations
- Compatible with SciTeX's tracking and export features

### 2. Unit Conversion
- Convert between different unit systems (e.g., ms to s, mV to V)
- Automatic scaling of data and axis limits
- Preserves scientific accuracy during conversions

### 3. Integration with Quantity Objects
- Direct plotting of Quantity objects from the units module
- Automatic unit detection from data
- Type-safe operations with dimensional analysis

### 4. Unit Validation
- Optional validation to ensure unit compatibility
- Prevents common errors like plotting time vs time
- Can be disabled for flexibility

## API Reference

### Basic Usage

```python
import scitex as stx

# Create figure
fig, ax = stx.plt.subplots()

# Plot with units
ax.plot_with_units(x_data, y_data, x_unit='ms', y_unit='mV')

# Units are automatically added to labels
ax.set_xlabel('Time')     # Shows "Time [ms]"
ax.set_ylabel('Voltage')  # Shows "Voltage [mV]"
```

### Unit Conversion

```python
# Set initial units
ax.plot_with_units(time_ms, voltage_mv, x_unit='ms', y_unit='mV')

# Convert to different units
ax.convert_x_units('s')   # Convert milliseconds to seconds
ax.convert_y_units('V')   # Convert millivolts to volts
```

### Working with Quantities

```python
from scitex.units import Q, Units

# Create quantities
time = Q(np.linspace(0, 1, 100), Units.s)
voltage = Q(5 * np.sin(2 * np.pi * 10 * time.value), Units.V)

# Plot quantities directly - units detected automatically
ax.plot_with_units(time, voltage)
```

### Unit Validation

```python
# Enable strict unit checking (default)
ax.set_unit_validation(True)

# Set expected units
ax.set_x_unit('ms')
ax.set_y_unit('mV')

# This will raise an error if units don't match
ax.plot_with_units(time_s, voltage_v)  # Error: expects ms and mV

# Disable validation for flexibility
ax.set_unit_validation(False)
```

## Methods Added to AxisWrapper

### Plotting Methods
- `plot_with_units(x, y, x_unit=None, y_unit=None, **kwargs)` - Plot with automatic unit handling

### Unit Management
- `set_x_unit(unit)` - Set the unit for x-axis
- `set_y_unit(unit)` - Set the unit for y-axis
- `set_z_unit(unit)` - Set the unit for z-axis (3D plots)
- `get_x_unit()` - Get current x-axis unit
- `get_y_unit()` - Get current y-axis unit
- `get_z_unit()` - Get current z-axis unit

### Unit Conversion
- `convert_x_units(new_unit, update_data=True)` - Convert x-axis to new units
- `convert_y_units(new_unit, update_data=True)` - Convert y-axis to new units

### Validation
- `set_unit_validation(enabled)` - Enable/disable unit validation

### Enhanced Label Methods
- `set_xlabel(label, unit=None)` - Set x-label with optional unit
- `set_ylabel(label, unit=None)` - Set y-label with optional unit
- `set_zlabel(label, unit=None)` - Set z-label with optional unit (3D)

## Supported Units

### Time Units
- `s` (second), `ms` (millisecond), `us` (microsecond), `ns` (nanosecond)
- `min` (minute), `hour`, `day`

### Length Units
- `m` (meter), `mm` (millimeter), `cm` (centimeter), `km` (kilometer)
- `um` (micrometer), `nm` (nanometer)

### Electrical Units
- `V` (volt), `mV` (millivolt), `uV` (microvolt), `kV` (kilovolt)
- `A` (ampere), `mA` (milliampere), `uA` (microampere)
- `Ω` (ohm), `kΩ` (kiloohm), `MΩ` (megaohm)
- `F` (farad), `μF` (microfarad), `nF` (nanofarad), `pF` (picofarad)

### Frequency Units
- `Hz` (hertz), `kHz` (kilohertz), `MHz` (megahertz), `GHz` (gigahertz)

### Other Units
- `Pa` (pascal), `N` (newton), `J` (joule), `W` (watt)
- `K` (kelvin), `°C` (celsius), `°F` (fahrenheit)

## Implementation Details

### Architecture
- Implemented as `UnitAwareMixin` in the plt module
- Integrated into `AxisWrapper` class
- Maintains compatibility with existing plotting features

### File Locations
- Mixin: `src/scitex/plt/_subplots/_AxisWrapperMixins/_UnitAwareMixin.py`
- Units: `src/scitex/units.py`
- Examples: `examples/25_scitex_unit_aware_plotting.ipynb`

### Design Decisions
1. **Non-intrusive**: Unit awareness is optional and doesn't affect existing code
2. **Flexible**: Can work with or without the units module
3. **Extensible**: Easy to add new units or unit systems
4. **Compatible**: Works with all existing plotting methods

## Examples

### Example 1: Basic Signal Processing
```python
# Generate signal
time_ms = np.linspace(0, 1000, 1000)
signal_mv = 5 * np.sin(2 * np.pi * 10 * time_ms / 1000)

# Plot with units
fig, ax = stx.plt.subplots()
ax.plot_with_units(time_ms, signal_mv, x_unit='ms', y_unit='mV')
ax.set_xlabel('Time')
ax.set_ylabel('Amplitude')
ax.set_title('10 Hz Signal')
```

### Example 2: RC Circuit Analysis
```python
from scitex.units import Q, Units

# Circuit parameters
R = Q(1000, Units.ohm)      # 1 kΩ
C = Q(1e-6, Units.farad)    # 1 μF
V0 = Q(5, Units.V)          # 5 V

# Time constant
tau = R.value * C.value

# Calculate response
t = np.linspace(0, 5*tau, 100)
V_cap = V0.value * (1 - np.exp(-t/tau))

# Plot with automatic unit conversion
fig, ax = stx.plt.subplots()
ax.plot_with_units(t*1000, V_cap, x_unit='ms', y_unit='V')
ax.set_xlabel('Time')
ax.set_ylabel('Capacitor Voltage')
```

## Testing

Comprehensive tests are available in:
- `.dev/test_unit_aware_plotting.py` - Unit tests
- `examples/25_scitex_unit_aware_plotting.ipynb` - Interactive examples

All tests pass with 100% success rate.

## Future Enhancements

Potential improvements for future versions:
1. Automatic unit inference from variable names
2. Unit consistency checking across multiple plots
3. Support for compound units (e.g., m/s, W/m²)
4. Integration with scientific databases for unit standards
5. LaTeX rendering of complex unit expressions

## Conclusion

The unit-aware plotting feature significantly enhances SciTeX's scientific computing capabilities by ensuring dimensional consistency and reducing unit-related errors. It provides a foundation for more advanced scientific visualization features while maintaining backward compatibility and ease of use.