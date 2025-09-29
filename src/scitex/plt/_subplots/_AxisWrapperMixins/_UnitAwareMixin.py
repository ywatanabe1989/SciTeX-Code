#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 10:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_AxisWrapperMixins/_UnitAwareMixin.py
# ----------------------------------------

"""
Unit-Aware Plotting Mixin
=========================

This mixin adds unit handling capabilities to the AxisWrapper class,
ensuring scientific validity in plots.

Features:
- Automatic unit tracking for axes
- Unit validation for data compatibility
- Automatic unit conversion
- Unit-aware axis labels
"""

from typing import Optional, Dict, Tuple, Union, Any
import numpy as np
from ....units import Unit, Q, Units
from ....errors import SciTeXError


class UnitMismatchError(SciTeXError):
    """Raised when units are incompatible for an operation."""
    pass


class UnitAwareMixin:
    """Mixin that adds unit awareness to plotting operations."""
    
    def __init__(self):
        """Initialize unit tracking."""
        self._x_unit: Optional[Unit] = None
        self._y_unit: Optional[Unit] = None
        self._z_unit: Optional[Unit] = None
        self._unit_validation_enabled: bool = True
        
    def set_unit_validation(self, enabled: bool) -> None:
        """Enable or disable unit validation."""
        self._unit_validation_enabled = enabled
        
    def set_x_unit(self, unit: Union[str, Unit]) -> None:
        """Set the unit for the x-axis."""
        if isinstance(unit, str):
            unit_obj = getattr(Units, unit, None)
            if unit_obj is None:
                raise ValueError(f"Unknown unit: {unit}")
            unit = unit_obj
        self._x_unit = unit
        self._update_xlabel_with_unit()
        
    def set_y_unit(self, unit: Union[str, Unit]) -> None:
        """Set the unit for the y-axis."""
        if isinstance(unit, str):
            unit_obj = getattr(Units, unit, None)
            if unit_obj is None:
                raise ValueError(f"Unknown unit: {unit}")
            unit = unit_obj
        self._y_unit = unit
        self._update_ylabel_with_unit()
        
    def set_z_unit(self, unit: Union[str, Unit]) -> None:
        """Set the unit for the z-axis (for 3D plots)."""
        if isinstance(unit, str):
            unit_obj = getattr(Units, unit, None)
            if unit_obj is None:
                raise ValueError(f"Unknown unit: {unit}")
            unit = unit_obj
        self._z_unit = unit
        self._update_zlabel_with_unit()
        
    def get_x_unit(self) -> Optional[Unit]:
        """Get the current x-axis unit."""
        return self._x_unit
        
    def get_y_unit(self) -> Optional[Unit]:
        """Get the current y-axis unit."""
        return self._y_unit
        
    def get_z_unit(self) -> Optional[Unit]:
        """Get the current z-axis unit."""
        return self._z_unit
        
    def _update_xlabel_with_unit(self) -> None:
        """Update x-axis label to include unit."""
        if self._x_unit and hasattr(self, '_axes_mpl'):
            current_label = self._axes_mpl.get_xlabel()
            # Remove existing unit if present
            if '[' in current_label and ']' in current_label:
                current_label = current_label.split('[')[0].strip()
            if current_label:
                self._axes_mpl.set_xlabel(f"{current_label} [{self._x_unit.symbol}]")
                
    def _update_ylabel_with_unit(self) -> None:
        """Update y-axis label to include unit."""
        if self._y_unit and hasattr(self, '_axes_mpl'):
            current_label = self._axes_mpl.get_ylabel()
            # Remove existing unit if present
            if '[' in current_label and ']' in current_label:
                current_label = current_label.split('[')[0].strip()
            if current_label:
                self._axes_mpl.set_ylabel(f"{current_label} [{self._y_unit.symbol}]")
                
    def _update_zlabel_with_unit(self) -> None:
        """Update z-axis label to include unit (for 3D plots)."""
        if self._z_unit and hasattr(self, '_axes_mpl') and hasattr(self._axes_mpl, 'set_zlabel'):
            current_label = self._axes_mpl.get_zlabel()
            # Remove existing unit if present
            if '[' in current_label and ']' in current_label:
                current_label = current_label.split('[')[0].strip()
            if current_label:
                self._axes_mpl.set_zlabel(f"{current_label} [{self._z_unit.symbol}]")
                
    def plot_with_units(self, x, y, x_unit=None, y_unit=None, **kwargs):
        """Plot with automatic unit handling.
        
        Parameters
        ----------
        x : array-like or Quantity
            X-axis data
        y : array-like or Quantity
            Y-axis data
        x_unit : str or Unit, optional
            Unit for x-axis (overrides detected unit)
        y_unit : str or Unit, optional
            Unit for y-axis (overrides detected unit)
        **kwargs : dict
            Additional plotting parameters
            
        Returns
        -------
        lines : list of Line2D
            The plotted lines
        """
        # Extract values and units from Quantity objects
        x_val, x_detected_unit = self._extract_value_and_unit(x)
        y_val, y_detected_unit = self._extract_value_and_unit(y)
        
        # Use provided units or detected units
        if x_unit:
            self.set_x_unit(x_unit)
        elif x_detected_unit and not self._x_unit:
            self.set_x_unit(x_detected_unit)
            
        if y_unit:
            self.set_y_unit(y_unit)
        elif y_detected_unit and not self._y_unit:
            self.set_y_unit(y_detected_unit)
            
        # Validate units if enabled
        if self._unit_validation_enabled:
            self._validate_unit_compatibility(x_detected_unit, self._x_unit, "x")
            self._validate_unit_compatibility(y_detected_unit, self._y_unit, "y")
            
        # Plot using the standard method
        return self.plot(x_val, y_val, **kwargs)
        
    def _extract_value_and_unit(self, data) -> Tuple[np.ndarray, Optional[Unit]]:
        """Extract numerical value and unit from data."""
        if hasattr(data, 'value') and hasattr(data, 'unit'):
            # It's a Quantity object
            return data.value, data.unit
        else:
            # Regular array
            return np.asarray(data), None
            
    def _validate_unit_compatibility(self, data_unit: Optional[Unit], 
                                   axis_unit: Optional[Unit], 
                                   axis_name: str) -> None:
        """Validate that data unit is compatible with axis unit."""
        if not self._unit_validation_enabled:
            return
            
        if data_unit and axis_unit:
            # Check if units have same dimensions
            if data_unit.dimensions != axis_unit.dimensions:
                raise UnitMismatchError(
                    f"Unit mismatch on {axis_name}-axis: "
                    f"data has unit {data_unit.symbol} {data_unit.dimensions}, "
                    f"but axis expects {axis_unit.symbol} {axis_unit.dimensions}"
                )
                
    def convert_x_units(self, new_unit: Union[str, Unit], 
                       update_data: bool = True) -> float:
        """Convert x-axis to new units.
        
        Parameters
        ----------
        new_unit : str or Unit
            Target unit
        update_data : bool
            Whether to update plotted data
            
        Returns
        -------
        float
            Conversion factor applied
        """
        if isinstance(new_unit, str):
            new_unit = getattr(Units, new_unit)
            
        if not self._x_unit:
            raise ValueError("No x-axis unit set")
            
        # Calculate conversion factor
        factor = self._x_unit.scale / new_unit.scale
        
        if update_data and hasattr(self, '_axes_mpl'):
            # Update all line data
            for line in self._axes_mpl.lines:
                xdata = line.get_xdata()
                line.set_xdata(xdata * factor)
                
            # Update x-axis limits
            xlim = self._axes_mpl.get_xlim()
            self._axes_mpl.set_xlim([x * factor for x in xlim])
            
        # Update unit
        self.set_x_unit(new_unit)
        
        return factor
        
    def convert_y_units(self, new_unit: Union[str, Unit], 
                       update_data: bool = True) -> float:
        """Convert y-axis to new units.
        
        Parameters
        ----------
        new_unit : str or Unit
            Target unit
        update_data : bool
            Whether to update plotted data
            
        Returns
        -------
        float
            Conversion factor applied
        """
        if isinstance(new_unit, str):
            new_unit = getattr(Units, new_unit)
            
        if not self._y_unit:
            raise ValueError("No y-axis unit set")
            
        # Calculate conversion factor
        factor = self._y_unit.scale / new_unit.scale
        
        if update_data and hasattr(self, '_axes_mpl'):
            # Update all line data
            for line in self._axes_mpl.lines:
                ydata = line.get_ydata()
                line.set_ydata(ydata * factor)
                
            # Update y-axis limits
            ylim = self._axes_mpl.get_ylim()
            self._axes_mpl.set_ylim([y * factor for y in ylim])
            
        # Update unit
        self.set_y_unit(new_unit)
        
        return factor
        
    def set_xlabel(self, label: str, unit: Optional[Union[str, Unit]] = None) -> None:
        """Set x-axis label with optional unit.
        
        Parameters
        ----------
        label : str
            Axis label text
        unit : str or Unit, optional
            Unit to display
        """
        if unit:
            self.set_x_unit(unit)
            
        if self._x_unit:
            label = f"{label} [{self._x_unit.symbol}]"
            
        self._axes_mpl.set_xlabel(label)
        
    def set_ylabel(self, label: str, unit: Optional[Union[str, Unit]] = None) -> None:
        """Set y-axis label with optional unit.
        
        Parameters
        ----------
        label : str
            Axis label text
        unit : str or Unit, optional
            Unit to display
        """
        if unit:
            self.set_y_unit(unit)
            
        if self._y_unit:
            label = f"{label} [{self._y_unit.symbol}]"
            
        self._axes_mpl.set_ylabel(label)
        
    def set_zlabel(self, label: str, unit: Optional[Union[str, Unit]] = None) -> None:
        """Set z-axis label with optional unit (for 3D plots).
        
        Parameters
        ----------
        label : str
            Axis label text
        unit : str or Unit, optional
            Unit to display
        """
        if not hasattr(self._axes_mpl, 'set_zlabel'):
            raise ValueError("Z-axis labels only available for 3D plots")
            
        if unit:
            self.set_z_unit(unit)
            
        if self._z_unit:
            label = f"{label} [{self._z_unit.symbol}]"
            
        self._axes_mpl.set_zlabel(label)