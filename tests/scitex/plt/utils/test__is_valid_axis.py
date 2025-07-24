#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 15:29:11 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/plt/utils/test__is_valid_axis.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/plt/utils/test__is_valid_axis.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import pytest

# Import the assertion function
from scitex.plt.utils import assert_valid_axis, is_valid_axis


class TestAxisValidation:
    def test_matplotlib_axis_is_valid(self):
        """Test that a standard matplotlib axis is valid."""
        # Create a matplotlib figure and axis
        fig, ax = plt.subplots()
        
        # Test the validation function
        assert is_valid_axis(ax) is True
        
        # Test the assertion function (should not raise)
        assert_valid_axis(ax, "Test message")
        
        # Clean up
        plt.close(fig)
    
    def test_scitex_axis_wrapper_is_valid(self):
        """Test that an SciTeX AxisWrapper is valid."""
        # Create an SciTeX figure and axis
        import scitex.plt as mplt
        fig, ax = mplt.subplots()
        
        # Test the validation function
        assert is_valid_axis(ax) is True
        
        # Test the assertion function (should not raise)
        assert_valid_axis(ax, "Test message")
        
        # Clean up - need to use the underlying matplotlib figure
        plt.close(fig._fig_mpl)
    
    def test_non_axis_is_invalid(self):
        """Test that a non-axis object is correctly identified as invalid."""
        # Create a non-axis object
        not_an_axis = "I am not an axis"
        
        # Test the validation function
        assert is_valid_axis(not_an_axis) is False
        
        # Test the assertion function (should raise AssertionError)
        with pytest.raises(AssertionError):
            assert_valid_axis(not_an_axis, "Test message")

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_is_valid_axis.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-18 15:12:10 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/utils/_is_valid_axis.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/utils/_is_valid_axis.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import inspect
# import matplotlib
# 
# def is_valid_axis(axis):
#     """
#     Check if the provided object is a valid axis (matplotlib Axes or scitex AxisWrapper).
#     
#     Parameters
#     ----------
#     axis : object
#         The object to check
#         
#     Returns
#     -------
#     bool
#         True if the object is a valid axis, False otherwise
#         
#     Examples
#     --------
#     >>> import matplotlib.pyplot as plt
#     >>> import scitex
#     >>> fig, ax = plt.subplots()
#     >>> is_valid_axis(ax)
#     True
#     >>> mfig, max = scitex.plt.subplots()
#     >>> is_valid_axis(max)
#     True
#     """
#     # Check if it's a matplotlib Axes directly
#     if isinstance(axis, matplotlib.axes._axes.Axes):
#         return True
#     
#     # Check if it's an AxisWrapper from scitex
#     # This checks the class hierarchy to see if it has an AxisWrapper in its inheritance chain
#     for cls in inspect.getmro(type(axis)):
#         if cls.__name__ == 'AxisWrapper':
#             return True
#             
#     # Check if it has common axis methods (fallback check)
#     axis_methods = ['plot', 'scatter', 'set_xlabel', 'set_ylabel', 'get_figure']
#     has_methods = all(hasattr(axis, method) for method in axis_methods)
#     
#     return has_methods
# 
# def assert_valid_axis(axis, error_message=None):
#     """
#     Assert that the provided object is a valid axis (matplotlib Axes or scitex AxisWrapper).
#     
#     Parameters
#     ----------
#     axis : object
#         The object to check
#     error_message : str, optional
#         Custom error message if assertion fails
#         
#     Raises
#     ------
#     AssertionError
#         If the provided object is not a valid axis
#     """
#     if error_message is None:
#         error_message = "First argument must be a matplotlib axis or scitex axis wrapper"
#         
#     assert is_valid_axis(axis), error_message
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_is_valid_axis.py
# --------------------------------------------------------------------------------
