#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Handling for Scientific Computing
======================================

This module provides unit handling capabilities for SciTeX, ensuring
scientific validity in computations with physical quantities.

Features:
- Unit conversion and validation
- Dimensional analysis
- Unit-aware arithmetic operations
- Common scientific unit presets

Author: SciTeX Development Team
Date: 2025-07-04
"""

from typing import Union, Optional, Dict, Any, Tuple
import numpy as np
from dataclasses import dataclass
import warnings


@dataclass
class Unit:
    """Represents a physical unit with dimensions."""
    
    name: str
    symbol: str
    dimensions: Dict[str, float]  # e.g., {'length': 1, 'time': -1} for m/s
    scale: float = 1.0  # Conversion factor to SI base unit
    
    def __mul__(self, other: 'Unit') -> 'Unit':
        """Multiply units."""
        new_dims = self.dimensions.copy()
        for dim, power in other.dimensions.items():
            new_dims[dim] = new_dims.get(dim, 0) + power
        
        # Clean up zero dimensions
        new_dims = {k: v for k, v in new_dims.items() if v != 0}
        
        return Unit(
            name=f"{self.name}*{other.name}",
            symbol=f"{self.symbol}·{other.symbol}",
            dimensions=new_dims,
            scale=self.scale * other.scale
        )
    
    def __truediv__(self, other: 'Unit') -> 'Unit':
        """Divide units."""
        new_dims = self.dimensions.copy()
        for dim, power in other.dimensions.items():
            new_dims[dim] = new_dims.get(dim, 0) - power
        
        # Clean up zero dimensions
        new_dims = {k: v for k, v in new_dims.items() if v != 0}
        
        return Unit(
            name=f"{self.name}/{other.name}",
            symbol=f"{self.symbol}/{other.symbol}",
            dimensions=new_dims,
            scale=self.scale / other.scale
        )
    
    def __pow__(self, exponent: float) -> 'Unit':
        """Raise unit to a power."""
        new_dims = {k: v * exponent for k, v in self.dimensions.items()}
        
        return Unit(
            name=f"{self.name}^{exponent}",
            symbol=f"{self.symbol}^{exponent}",
            dimensions=new_dims,
            scale=self.scale ** exponent
        )
    
    def is_compatible(self, other: 'Unit') -> bool:
        """Check if units have same dimensions."""
        return self.dimensions == other.dimensions


class Quantity:
    """A numeric value with associated units."""
    
    def __init__(self, value: Union[float, np.ndarray], unit: Unit):
        self.value = np.asarray(value)
        self.unit = unit
    
    def to(self, target_unit: Unit) -> 'Quantity':
        """Convert to different unit."""
        if not self.unit.is_compatible(target_unit):
            raise ValueError(
                f"Cannot convert {self.unit.symbol} to {target_unit.symbol}: "
                f"incompatible dimensions"
            )
        
        # Convert value
        conversion_factor = self.unit.scale / target_unit.scale
        new_value = self.value * conversion_factor
        
        return Quantity(new_value, target_unit)
    
    def __add__(self, other: 'Quantity') -> 'Quantity':
        """Add quantities (must have compatible units)."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only add Quantity to Quantity")
        
        if not self.unit.is_compatible(other.unit):
            raise ValueError(
                f"Cannot add {self.unit.symbol} and {other.unit.symbol}: "
                f"incompatible units"
            )
        
        # Convert other to self's units
        other_converted = other.to(self.unit)
        return Quantity(self.value + other_converted.value, self.unit)
    
    def __mul__(self, other: Union[float, 'Quantity']) -> 'Quantity':
        """Multiply quantities or by scalar."""
        if isinstance(other, Quantity):
            return Quantity(
                self.value * other.value,
                self.unit * other.unit
            )
        else:
            return Quantity(self.value * other, self.unit)
    
    def __truediv__(self, other: Union[float, 'Quantity']) -> 'Quantity':
        """Divide quantities or by scalar."""
        if isinstance(other, Quantity):
            return Quantity(
                self.value / other.value,
                self.unit / other.unit
            )
        else:
            return Quantity(self.value / other, self.unit)
    
    def __repr__(self) -> str:
        return f"{self.value} {self.unit.symbol}"


# Common unit definitions
class Units:
    """Common scientific units."""
    
    # Base SI units
    meter = Unit("meter", "m", {"length": 1})
    kilogram = Unit("kilogram", "kg", {"mass": 1})
    second = Unit("second", "s", {"time": 1})
    ampere = Unit("ampere", "A", {"current": 1})
    kelvin = Unit("kelvin", "K", {"temperature": 1})
    mole = Unit("mole", "mol", {"amount": 1})
    
    # Derived units
    newton = Unit("newton", "N", {"mass": 1, "length": 1, "time": -2})
    joule = Unit("joule", "J", {"mass": 1, "length": 2, "time": -2})
    watt = Unit("watt", "W", {"mass": 1, "length": 2, "time": -3})
    pascal = Unit("pascal", "Pa", {"mass": 1, "length": -1, "time": -2})
    
    # Length units
    millimeter = Unit("millimeter", "mm", {"length": 1}, scale=0.001)
    centimeter = Unit("centimeter", "cm", {"length": 1}, scale=0.01)
    kilometer = Unit("kilometer", "km", {"length": 1}, scale=1000)
    inch = Unit("inch", "in", {"length": 1}, scale=0.0254)
    foot = Unit("foot", "ft", {"length": 1}, scale=0.3048)
    mile = Unit("mile", "mi", {"length": 1}, scale=1609.344)
    
    # Time units
    millisecond = Unit("millisecond", "ms", {"time": 1}, scale=0.001)
    microsecond = Unit("microsecond", "μs", {"time": 1}, scale=1e-6)
    minute = Unit("minute", "min", {"time": 1}, scale=60)
    hour = Unit("hour", "h", {"time": 1}, scale=3600)
    day = Unit("day", "d", {"time": 1}, scale=86400)
    
    # Mass units
    gram = Unit("gram", "g", {"mass": 1}, scale=0.001)
    milligram = Unit("milligram", "mg", {"mass": 1}, scale=1e-6)
    pound = Unit("pound", "lb", {"mass": 1}, scale=0.453592)
    
    # Temperature (special handling needed for non-linear conversions)
    celsius = Unit("celsius", "°C", {"temperature": 1})
    fahrenheit = Unit("fahrenheit", "°F", {"temperature": 1})
    
    # Dimensionless
    dimensionless = Unit("dimensionless", "", {})
    percent = Unit("percent", "%", {}, scale=0.01)
    
    # Frequency
    hertz = Unit("hertz", "Hz", {"time": -1})
    kilohertz = Unit("kilohertz", "kHz", {"time": -1}, scale=1000)
    megahertz = Unit("megahertz", "MHz", {"time": -1}, scale=1e6)
    
    # Electrical units
    volt = Unit("volt", "V", {"mass": 1, "length": 2, "time": -3, "current": -1})
    millivolt = Unit("millivolt", "mV", {"mass": 1, "length": 2, "time": -3, "current": -1}, scale=0.001)
    microvolt = Unit("microvolt", "μV", {"mass": 1, "length": 2, "time": -3, "current": -1}, scale=1e-6)
    kilovolt = Unit("kilovolt", "kV", {"mass": 1, "length": 2, "time": -3, "current": -1}, scale=1000)
    
    ohm = Unit("ohm", "Ω", {"mass": 1, "length": 2, "time": -3, "current": -2})
    kiloohm = Unit("kiloohm", "kΩ", {"mass": 1, "length": 2, "time": -3, "current": -2}, scale=1000)
    
    farad = Unit("farad", "F", {"mass": -1, "length": -2, "time": 4, "current": 2})
    microfarad = Unit("microfarad", "μF", {"mass": -1, "length": -2, "time": 4, "current": 2}, scale=1e-6)
    nanofarad = Unit("nanofarad", "nF", {"mass": -1, "length": -2, "time": 4, "current": 2}, scale=1e-9)
    picofarad = Unit("picofarad", "pF", {"mass": -1, "length": -2, "time": 4, "current": 2}, scale=1e-12)
    
    # Common abbreviations
    s = second
    ms = millisecond
    Hz = hertz
    V = volt
    mV = millivolt
    mA = Unit("milliampere", "mA", {"current": 1}, scale=0.001)


def validate_units(func):
    """Decorator to validate unit compatibility in operations."""
    def wrapper(*args, **kwargs):
        # Extract quantities from args
        quantities = [arg for arg in args if isinstance(arg, Quantity)]
        
        # Check if all quantities have compatible units
        if len(quantities) > 1:
            base_unit = quantities[0].unit
            for q in quantities[1:]:
                if not base_unit.is_compatible(q.unit):
                    warnings.warn(
                        f"Unit mismatch: {base_unit.symbol} vs {q.unit.symbol}",
                        UserWarning
                    )
        
        return func(*args, **kwargs)
    
    return wrapper


# Convenience functions
def Q(value: Union[float, np.ndarray], unit: Unit) -> Quantity:
    """Create a quantity (shorthand)."""
    return Quantity(value, unit)


def ensure_units(value: Union[float, np.ndarray, Quantity], 
                default_unit: Unit) -> Quantity:
    """Ensure value has units, applying default if needed."""
    if isinstance(value, Quantity):
        return value
    else:
        return Quantity(value, default_unit)


def strip_units(quantity: Union[Quantity, float, np.ndarray]) -> np.ndarray:
    """Extract numeric value, removing units if present."""
    if isinstance(quantity, Quantity):
        return quantity.value
    else:
        return np.asarray(quantity)


# Example usage functions
def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between units (handles non-linear conversions)."""
    conversions = {
        ('C', 'F'): lambda c: c * 9/5 + 32,
        ('F', 'C'): lambda f: (f - 32) * 5/9,
        ('C', 'K'): lambda c: c + 273.15,
        ('K', 'C'): lambda k: k - 273.15,
        ('F', 'K'): lambda f: (f - 32) * 5/9 + 273.15,
        ('K', 'F'): lambda k: (k - 273.15) * 9/5 + 32
    }
    
    from_unit = from_unit.upper()[0]
    to_unit = to_unit.upper()[0]
    
    if from_unit == to_unit:
        return value
    
    key = (from_unit, to_unit)
    if key in conversions:
        return conversions[key](value)
    else:
        raise ValueError(f"Unknown temperature conversion: {from_unit} to {to_unit}")


# Export main components
__all__ = [
    'Unit', 'Quantity', 'Units', 'Q',
    'validate_units', 'ensure_units', 'strip_units',
    'convert_temperature'
]