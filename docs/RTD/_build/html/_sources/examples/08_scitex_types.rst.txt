08 SciTeX Types
===============

.. note::
   This page is generated from the Jupyter notebook `08_scitex_types.ipynb <https://github.com/scitex/scitex/blob/main/examples/08_scitex_types.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 08_scitex_types.ipynb


This comprehensive notebook demonstrates the SciTeX types module,
covering type definitions, type checking utilities, and validation
functions for scientific computing workflows.

Features Covered
----------------

Type Definitions
~~~~~~~~~~~~~~~~

-  ArrayLike - Union type for array-like objects
-  ColorLike - Union type for color representations

Type Checking Functions
~~~~~~~~~~~~~~~~~~~~~~~

-  is_array_like - Check if object is array-like
-  is_listed_X - Check if list contains specific types
-  is_list_of_type - Conventional alias for type checking

Applications
~~~~~~~~~~~~

-  Input validation for scientific functions
-  Type safety in data processing pipelines
-  Flexible parameter handling
-  Cross-library compatibility checks

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    import time
    from typing import List, Tuple, Union, Any
    
    # Try to import optional dependencies
    try:
        import torch
        TORCH_AVAILABLE = True
    except ImportError:
        TORCH_AVAILABLE = False
        print("PyTorch not available - some examples will be skipped")
    
    try:
        import xarray as xr
        XARRAY_AVAILABLE = True
    except ImportError:
        XARRAY_AVAILABLE = False
        print("XArray not available - some examples will be skipped")
    
    print("SciTeX Type Handling Utilities Tutorial - Ready to begin!")

Part 1: ArrayLike Type and Validation
-------------------------------------

1.1 Understanding ArrayLike
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ArrayLike type union allows functions to accept various array-like
objects:

.. code:: ipython3

    # Create different types of array-like objects
    test_objects = {
        'python_list': [1, 2, 3, 4, 5],
        'python_tuple': (1, 2, 3, 4, 5),
        'numpy_array': np.array([1, 2, 3, 4, 5]),
        'pandas_series': pd.Series([1, 2, 3, 4, 5]),
        'pandas_dataframe': pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]}),
        'nested_list': [[1, 2], [3, 4], [5, 6]],
        'string': "not an array",
        'integer': 42,
        'float': 3.14,
        'dictionary': {'a': 1, 'b': 2}
    }
    
    # Add optional objects if available
    if TORCH_AVAILABLE:
        test_objects['torch_tensor'] = torch.tensor([1, 2, 3, 4, 5])
    
    if XARRAY_AVAILABLE:
        test_objects['xarray_dataarray'] = xr.DataArray([1, 2, 3, 4, 5], dims=['x'])
    
    # Test is_array_like function
    print("Testing is_array_like function:")
    print("=" * 40)
    
    array_like_results = {}
    for name, obj in test_objects.items():
        is_array_like = scitex.types.is_array_like(obj)
        array_like_results[name] = is_array_like
        status = "✓ Array-like" if is_array_like else "✗ Not array-like"
        obj_type = type(obj).__name__
        print(f"{name:20} ({obj_type:15}): {status}")
    
    # Summary
    array_like_count = sum(array_like_results.values())
    total_count = len(array_like_results)
    print(f"\nSummary: {array_like_count}/{total_count} objects are array-like")

1.2 Array-like Operations and Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate operations with different array-like types
    def process_array_like(data, operation="sum"):
        """
        Process array-like data with type checking.
        
        Args:
            data: ArrayLike object
            operation: Operation to perform ('sum', 'mean', 'max', 'min')
        
        Returns:
            Result of operation or None if data is not array-like
        """
        if not scitex.types.is_array_like(data):
            print(f"Error: Input is not array-like (type: {type(data).__name__})")
            return None
        
        # Convert to numpy array for consistent operations
        try:
            if isinstance(data, pd.DataFrame):
                # For DataFrames, operate on all numeric columns
                numeric_data = data.select_dtypes(include=[np.number])
                if numeric_data.empty:
                    print("Error: DataFrame contains no numeric data")
                    return None
                data_array = numeric_data.values
            elif isinstance(data, pd.Series):
                data_array = data.values
            elif TORCH_AVAILABLE and torch.is_tensor(data):
                data_array = data.numpy()
            elif XARRAY_AVAILABLE and isinstance(data, xr.DataArray):
                data_array = data.values
            else:
                data_array = np.array(data)
            
            # Perform operation
            if operation == "sum":
                result = np.sum(data_array)
            elif operation == "mean":
                result = np.mean(data_array)
            elif operation == "max":
                result = np.max(data_array)
            elif operation == "min":
                result = np.min(data_array)
            else:
                result = f"Unknown operation: {operation}"
            
            return result
            
        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    
    # Test the function with different array-like objects
    print("Testing array-like processing function:")
    print("=" * 50)
    
    operations = ['sum', 'mean', 'max', 'min']
    processing_results = {}
    
    # Select only array-like objects for processing
    array_like_objects = {name: obj for name, obj in test_objects.items() 
                         if array_like_results[name]}
    
    for op in operations:
        print(f"\nOperation: {op.upper()}")
        print("-" * 30)
        
        operation_results = {}
        for name, obj in array_like_objects.items():
            result = process_array_like(obj, op)
            operation_results[name] = result
            
            if result is not None:
                print(f"{name:20}: {result:.3f}" if isinstance(result, (int, float)) else f"{name:20}: {result}")
            else:
                print(f"{name:20}: Failed")
        
        processing_results[op] = operation_results
    
    # Test with non-array-like objects
    print("\nTesting with non-array-like objects:")
    non_array_objects = {name: obj for name, obj in test_objects.items() 
                        if not array_like_results[name]}
    
    for name, obj in non_array_objects.items():
        result = process_array_like(obj, 'sum')
        print(f"{name:20}: {'Correctly rejected' if result is None else 'Unexpected acceptance'}")

1.3 Cross-library Compatibility Demonstration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate seamless conversion between different array-like types
    def convert_array_like(data, target_type):
        """
        Convert array-like data to specified target type.
        
        Args:
            data: ArrayLike object
            target_type: Target type ('numpy', 'pandas_series', 'pandas_dataframe', 'list', 'torch', 'xarray')
        
        Returns:
            Converted data or None if conversion fails
        """
        if not scitex.types.is_array_like(data):
            print(f"Input is not array-like: {type(data).__name__}")
            return None
        
        try:
            # First convert to numpy array as intermediate format
            if isinstance(data, pd.DataFrame):
                # For DataFrames, use the first numeric column or all numeric data
                numeric_data = data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    if numeric_data.shape[1] == 1:
                        np_array = numeric_data.iloc[:, 0].values
                    else:
                        np_array = numeric_data.values
                else:
                    np_array = np.array(data.values)
            elif isinstance(data, pd.Series):
                np_array = data.values
            elif TORCH_AVAILABLE and torch.is_tensor(data):
                np_array = data.detach().numpy() if data.requires_grad else data.numpy()
            elif XARRAY_AVAILABLE and isinstance(data, xr.DataArray):
                np_array = data.values
            else:
                np_array = np.array(data)
            
            # Convert to target type
            if target_type == 'numpy':
                return np_array
            elif target_type == 'list':
                return np_array.tolist()
            elif target_type == 'pandas_series':
                return pd.Series(np_array.flatten() if np_array.ndim > 1 else np_array)
            elif target_type == 'pandas_dataframe':
                if np_array.ndim == 1:
                    return pd.DataFrame({'data': np_array})
                else:
                    return pd.DataFrame(np_array)
            elif target_type == 'torch' and TORCH_AVAILABLE:
                return torch.from_numpy(np_array.astype(np.float32))
            elif target_type == 'xarray' and XARRAY_AVAILABLE:
                if np_array.ndim == 1:
                    return xr.DataArray(np_array, dims=['x'])
                else:
                    return xr.DataArray(np_array, dims=['x', 'y'])
            else:
                return f"Unsupported target type: {target_type}"
        
        except Exception as e:
            print(f"Conversion error: {e}")
            return None
    
    # Test conversions with sample data
    sample_data = np.random.randn(5, 3)
    target_types = ['numpy', 'list', 'pandas_series', 'pandas_dataframe']
    
    if TORCH_AVAILABLE:
        target_types.append('torch')
    if XARRAY_AVAILABLE:
        target_types.append('xarray')
    
    print("Array-like type conversion demonstration:")
    print("=" * 45)
    print(f"Original data shape: {sample_data.shape}")
    print(f"Original data type: {type(sample_data).__name__}")
    
    conversion_results = {}
    for target in target_types:
        converted = convert_array_like(sample_data, target)
        conversion_results[target] = converted
        
        if converted is not None and not isinstance(converted, str):
            converted_type = type(converted).__name__
            if hasattr(converted, 'shape'):
                shape_info = f"shape: {converted.shape}"
            elif hasattr(converted, '__len__'):
                shape_info = f"length: {len(converted)}"
            else:
                shape_info = "scalar"
            
            # Check if converted object is array-like
            is_still_array_like = scitex.types.is_array_like(converted)
            array_like_status = "✓" if is_still_array_like else "✗"
            
            print(f"{target:15} -> {converted_type:15} ({shape_info:12}) Array-like: {array_like_status}")
        else:
            print(f"{target:15} -> Conversion failed")
    
    # Demonstrate round-trip conversions
    print("\nRound-trip conversion test:")
    print("-" * 30)
    
    original_list = [1, 2, 3, 4, 5]
    print(f"Original: {original_list} (type: {type(original_list).__name__})")
    
    # Convert through different types and back to list
    conversion_chain = ['numpy', 'pandas_series', 'pandas_dataframe', 'list']
    current_data = original_list
    
    for i, target in enumerate(conversion_chain):
        current_data = convert_array_like(current_data, target)
        if current_data is not None:
            data_preview = str(current_data)[:50] + "..." if len(str(current_data)) > 50 else str(current_data)
            print(f"Step {i+1}: {target:15} -> {data_preview}")
        else:
            print(f"Step {i+1}: {target:15} -> Conversion failed")
            break
    
    # Check if we got back to the original
    if current_data is not None and isinstance(current_data, list):
        success = current_data == original_list
        print(f"\nRound-trip successful: {success}")
        if success:
            print(f"Final result: {current_data}")
    else:
        print("\nRound-trip failed")

Part 2: ColorLike Type and Color Handling
-----------------------------------------

2.1 Understanding ColorLike
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ColorLike type allows flexible color specification in scientific
plotting:

.. code:: ipython3

    # Create different types of color specifications
    color_examples = {
        'named_color': 'red',
        'hex_color': '#FF5733',
        'rgb_tuple': (0.2, 0.6, 0.8),
        'rgba_tuple': (0.2, 0.6, 0.8, 0.7),
        'rgb_list': [0.9, 0.3, 0.1],
        'rgba_list': [0.9, 0.3, 0.1, 0.5],
        'matplotlib_color': 'C0',  # Matplotlib color cycle
        'grayscale': '0.5',  # Grayscale value
        'invalid_string': 'not_a_color',
        'invalid_tuple': (1, 2),  # Wrong number of elements
        'invalid_list': [1, 2, 3, 4, 5],  # Too many elements
        'invalid_type': 42
    }
    
    def is_valid_color(color):
        """
        Check if a color specification is valid according to ColorLike type.
        
        Args:
            color: Color specification to validate
        
        Returns:
            bool: True if color is valid ColorLike, False otherwise
        """
        # Check string colors
        if isinstance(color, str):
            return True  # We'll assume string validation is done by matplotlib
        
        # Check tuple colors
        if isinstance(color, tuple):
            if len(color) == 3:  # RGB
                return all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color)
            elif len(color) == 4:  # RGBA
                return all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color)
            else:
                return False
        
        # Check list colors
        if isinstance(color, list):
            if len(color) == 3:  # RGB
                return all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color)
            elif len(color) == 4:  # RGBA
                return all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color)
            else:
                return False
        
        return False
    
    def normalize_color(color):
        """
        Normalize a ColorLike object to RGBA tuple.
        
        Args:
            color: ColorLike object
        
        Returns:
            tuple: RGBA tuple (r, g, b, a) or None if invalid
        """
        if not is_valid_color(color):
            return None
        
        try:
            # Use matplotlib to convert color to RGBA
            import matplotlib.colors as mcolors
            
            if isinstance(color, str):
                try:
                    rgba = mcolors.to_rgba(color)
                    return rgba
                except ValueError:
                    return None
            elif isinstance(color, (tuple, list)):
                if len(color) == 3:
                    return (*color, 1.0)  # Add alpha=1.0
                elif len(color) == 4:
                    return tuple(color)
            
            return None
        except ImportError:
            # Fallback without matplotlib
            if isinstance(color, (tuple, list)):
                if len(color) == 3:
                    return (*color, 1.0)
                elif len(color) == 4:
                    return tuple(color)
            return None
    
    # Test color validation
    print("Testing ColorLike validation:")
    print("=" * 40)
    
    color_validation_results = {}
    for name, color in color_examples.items():
        is_valid = is_valid_color(color)
        normalized = normalize_color(color)
        color_validation_results[name] = {'valid': is_valid, 'normalized': normalized}
        
        status = "✓ Valid" if is_valid else "✗ Invalid"
        color_repr = str(color)[:30] + "..." if len(str(color)) > 30 else str(color)
        print(f"{name:18} {color_repr:25} -> {status}")
        
        if normalized:
            print(f"{'':44} RGBA: ({normalized[0]:.3f}, {normalized[1]:.3f}, {normalized[2]:.3f}, {normalized[3]:.3f})")
    
    # Summary
    valid_colors = sum(1 for result in color_validation_results.values() if result['valid'])
    total_colors = len(color_validation_results)
    print(f"\nSummary: {valid_colors}/{total_colors} color specifications are valid")

2.2 Color Processing and Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate color processing and visualization
    def create_color_palette(base_colors, n_variations=5):
        """
        Create color variations from base ColorLike objects.
        
        Args:
            base_colors: List of ColorLike objects
            n_variations: Number of variations per base color
        
        Returns:
            dict: Dictionary of color variations
        """
        palette = {}
        
        for i, color in enumerate(base_colors):
            normalized = normalize_color(color)
            if normalized is None:
                continue
            
            r, g, b, a = normalized
            variations = []
            
            # Create variations by adjusting brightness
            for j in range(n_variations):
                factor = 0.3 + (0.7 * j / (n_variations - 1))  # Range from 0.3 to 1.0
                var_r = min(1.0, r * factor + 0.1 * (1 - factor))
                var_g = min(1.0, g * factor + 0.1 * (1 - factor))
                var_b = min(1.0, b * factor + 0.1 * (1 - factor))
                variations.append((var_r, var_g, var_b, a))
            
            palette[f'color_{i+1}'] = {
                'original': normalized,
                'variations': variations,
                'input': color
            }
        
        return palette
    
    # Create a color palette from valid colors
    valid_color_examples = [
        'red', 
        (0.2, 0.6, 0.8), 
        [0.9, 0.3, 0.1], 
        '#FF5733'
    ]
    
    color_palette = create_color_palette(valid_color_examples, n_variations=5)
    
    print("Generated Color Palette:")
    print("=" * 30)
    
    for color_name, color_data in color_palette.items():
        print(f"\n{color_name}:")
        print(f"  Input: {color_data['input']}")
        print(f"  Original RGBA: ({color_data['original'][0]:.3f}, {color_data['original'][1]:.3f}, {color_data['original'][2]:.3f}, {color_data['original'][3]:.3f})")
        print(f"  Variations: {len(color_data['variations'])} shades")
    
    # Visualize the color palette
    fig, axes = plt.subplots(len(color_palette), 1, figsize=(10, 2 * len(color_palette)))
    if len(color_palette) == 1:
        axes = [axes]
    
    for i, (color_name, color_data) in enumerate(color_palette.items()):
        # Create a color bar showing variations
        variations = color_data['variations']
        colors_array = np.array(variations)[:, :3]  # Remove alpha for visualization
        
        # Create a horizontal color bar
        axes[i].imshow(colors_array.reshape(1, -1, 3), aspect='auto', extent=[0, len(variations), 0, 1])
        axes[i].set_title(f"{color_name} - Input: {color_data['input']}")
        axes[i].set_xticks(np.arange(len(variations)) + 0.5)
        axes[i].set_xticklabels([f'V{j+1}' for j in range(len(variations))])
        axes[i].set_yticks([])
        axes[i].set_xlabel('Variations')
    
    plt.tight_layout()
    plt.show()
    
    # Demonstrate color distance calculation
    def color_distance(color1, color2):
        """
        Calculate Euclidean distance between two colors in RGB space.
        
        Args:
            color1, color2: ColorLike objects
        
        Returns:
            float: Distance between colors (0-√3)
        """
        rgba1 = normalize_color(color1)
        rgba2 = normalize_color(color2)
        
        if rgba1 is None or rgba2 is None:
            return None
        
        # Calculate Euclidean distance in RGB space
        r_diff = rgba1[0] - rgba2[0]
        g_diff = rgba1[1] - rgba2[1]
        b_diff = rgba1[2] - rgba2[2]
        
        distance = np.sqrt(r_diff**2 + g_diff**2 + b_diff**2)
        return distance
    
    # Test color distances
    print("\nColor Distance Analysis:")
    print("=" * 30)
    
    test_color_pairs = [
        ('red', 'blue'),
        ('red', '#FF0000'),  # Same color, different representation
        ((1, 0, 0), (0.9, 0.1, 0.1)),  # Similar reds
        ('black', 'white'),
        ((0.5, 0.5, 0.5), '0.5')  # Same gray, different representation
    ]
    
    for color1, color2 in test_color_pairs:
        distance = color_distance(color1, color2)
        if distance is not None:
            print(f"{str(color1):20} <-> {str(color2):20}: {distance:.3f}")
        else:
            print(f"{str(color1):20} <-> {str(color2):20}: Invalid color(s)")

Part 3: List Type Checking with is_listed_X
-------------------------------------------

3.1 Basic Type Checking for Lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create test lists with different types
    test_lists = {
        'integers': [1, 2, 3, 4, 5],
        'floats': [1.1, 2.2, 3.3, 4.4, 5.5],
        'strings': ['a', 'b', 'c', 'd', 'e'],
        'mixed_numbers': [1, 2.5, 3, 4.0, 5],
        'mixed_types': [1, 'two', 3.0, [4], {'five': 5}],
        'booleans': [True, False, True, True, False],
        'nested_lists': [[1, 2], [3, 4], [5, 6]],
        'empty_list': [],
        'single_element': [42],
        'none_values': [None, None, None],
        'numpy_arrays': [np.array([1, 2]), np.array([3, 4])],
        'pandas_objects': [pd.Series([1, 2]), pd.DataFrame({'a': [1]})]
    }
    
    # Also test non-list objects
    non_list_objects = {
        'tuple': (1, 2, 3),
        'string': "hello",
        'integer': 42,
        'numpy_array': np.array([1, 2, 3]),
        'dict': {'a': 1, 'b': 2}
    }
    
    # Test different type specifications
    type_tests = [
        (int, "integers only"),
        (float, "floats only"),
        (str, "strings only"),
        ((int, float), "numbers (int or float)"),
        ([int, float], "numbers (list of types)"),
        (bool, "booleans only"),
        (list, "lists only"),
        (type(None), "None values only"),
        (np.ndarray, "numpy arrays only")
    ]
    
    print("Testing is_listed_X function:")
    print("=" * 50)
    
    # Test all combinations
    for type_spec, type_desc in type_tests:
        print(f"\nTesting for {type_desc}:")
        print("-" * 40)
        
        # Test with list objects
        for name, test_list in test_lists.items():
            result = scitex.types.is_listed_X(test_list, type_spec)
            alternative_result = scitex.types.is_list_of_type(test_list, type_spec)
            
            # Verify both functions give same result
            assert result == alternative_result, f"Functions disagree for {name}"
            
            status = "✓" if result else "✗"
            preview = str(test_list)[:30] + "..." if len(str(test_list)) > 30 else str(test_list)
            print(f"  {name:15} {preview:25} -> {status}")
        
        # Test with non-list objects (should all be False)
        print("  Non-list objects:")
        for name, obj in non_list_objects.items():
            result = scitex.types.is_listed_X(obj, type_spec)
            status = "✓" if result else "✗"
            print(f"    {name:13} -> {status} (should be ✗)")

3.2 Advanced List Validation for Scientific Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create scientific data validation functions
    def validate_numeric_list(data, allow_nan=False, min_length=1, max_length=None):
        """
        Validate a list contains only numeric data with optional constraints.
        
        Args:
            data: List to validate
            allow_nan: Whether to allow NaN values
            min_length: Minimum required length
            max_length: Maximum allowed length (None for no limit)
        
        Returns:
            dict: Validation results
        """
        results = {
            'is_list': isinstance(data, list),
            'length': len(data) if isinstance(data, list) else 0,
            'is_numeric': False,
            'has_nan': False,
            'length_valid': False,
            'overall_valid': False,
            'errors': []
        }
        
        if not results['is_list']:
            results['errors'].append("Input is not a list")
            return results
        
        # Check if all elements are numeric
        results['is_numeric'] = scitex.types.is_list_of_type(data, (int, float))
        
        if not results['is_numeric']:
            results['errors'].append("List contains non-numeric elements")
        
        # Check for NaN values
        if results['is_numeric']:
            results['has_nan'] = any(np.isnan(x) for x in data if isinstance(x, float))
            if results['has_nan'] and not allow_nan:
                results['errors'].append("List contains NaN values")
        
        # Check length constraints
        if results['length'] < min_length:
            results['errors'].append(f"List too short (minimum: {min_length})")
        elif max_length is not None and results['length'] > max_length:
            results['errors'].append(f"List too long (maximum: {max_length})")
        else:
            results['length_valid'] = True
        
        # Overall validation
        results['overall_valid'] = (
            results['is_list'] and 
            results['is_numeric'] and 
            results['length_valid'] and
            (allow_nan or not results['has_nan'])
        )
        
        return results
    
    def validate_coordinate_list(data):
        """
        Validate a list of coordinate tuples/lists.
        
        Args:
            data: List of coordinates [(x1, y1), (x2, y2), ...]
        
        Returns:
            dict: Validation results
        """
        results = {
            'is_list': isinstance(data, list),
            'all_coordinates': False,
            'consistent_dimensions': False,
            'dimensions': None,
            'count': len(data) if isinstance(data, list) else 0,
            'overall_valid': False,
            'errors': []
        }
        
        if not results['is_list']:
            results['errors'].append("Input is not a list")
            return results
        
        if len(data) == 0:
            results['errors'].append("List is empty")
            return results
        
        # Check if all elements are coordinate-like (tuples or lists)
        results['all_coordinates'] = scitex.types.is_list_of_type(data, (tuple, list))
        
        if not results['all_coordinates']:
            results['errors'].append("Not all elements are coordinate-like (tuple/list)")
            return results
        
        # Check dimension consistency
        first_dim = len(data[0]) if len(data) > 0 else 0
        results['dimensions'] = first_dim
        
        for i, coord in enumerate(data):
            if len(coord) != first_dim:
                results['errors'].append(f"Inconsistent dimensions at index {i}")
                return results
            
            # Check if all coordinate components are numeric
            if not all(isinstance(c, (int, float)) for c in coord):
                results['errors'].append(f"Non-numeric coordinate at index {i}")
                return results
        
        results['consistent_dimensions'] = True
        results['overall_valid'] = True
        
        return results
    
    # Test scientific data validation
    scientific_test_data = {
        'valid_measurements': [1.2, 3.4, 5.6, 7.8, 9.0],
        'with_nan': [1.2, 3.4, float('nan'), 7.8, 9.0],
        'mixed_numbers': [1, 2.5, 3, 4.0, 5],
        'with_strings': [1.2, '3.4', 5.6, 7.8, 9.0],
        'too_short': [1.2],
        'empty': [],
        'coordinates_2d': [(0, 1), (2, 3), (4, 5)],
        'coordinates_3d': [(0, 1, 2), (3, 4, 5), (6, 7, 8)],
        'mixed_dimensions': [(0, 1), (2, 3, 4), (5, 6)],
        'invalid_coordinates': [(0, 1), 'not_coord', (4, 5)],
        'non_numeric_coords': [('a', 'b'), ('c', 'd')]
    }
    
    print("Scientific Data Validation Tests:")
    print("=" * 40)
    
    # Test numeric validation
    print("\nNumeric List Validation:")
    print("-" * 25)
    
    numeric_tests = [
        'valid_measurements', 'with_nan', 'mixed_numbers', 
        'with_strings', 'too_short', 'empty'
    ]
    
    for test_name in numeric_tests:
        data = scientific_test_data[test_name]
        
        # Test with different constraints
        result_strict = validate_numeric_list(data, allow_nan=False, min_length=3)
        result_lenient = validate_numeric_list(data, allow_nan=True, min_length=1)
        
        print(f"\n{test_name}:")
        print(f"  Data: {data}")
        print(f"  Strict validation: {'✓' if result_strict['overall_valid'] else '✗'}")
        if result_strict['errors']:
            print(f"    Errors: {', '.join(result_strict['errors'])}")
        print(f"  Lenient validation: {'✓' if result_lenient['overall_valid'] else '✗'}")
        if result_lenient['errors']:
            print(f"    Errors: {', '.join(result_lenient['errors'])}")
    
    # Test coordinate validation
    print("\n\nCoordinate List Validation:")
    print("-" * 27)
    
    coordinate_tests = [
        'coordinates_2d', 'coordinates_3d', 'mixed_dimensions',
        'invalid_coordinates', 'non_numeric_coords'
    ]
    
    for test_name in coordinate_tests:
        data = scientific_test_data[test_name]
        result = validate_coordinate_list(data)
        
        print(f"\n{test_name}:")
        print(f"  Data: {data}")
        print(f"  Valid: {'✓' if result['overall_valid'] else '✗'}")
        if result['overall_valid']:
            print(f"  Dimensions: {result['dimensions']}D, Count: {result['count']}")
        if result['errors']:
            print(f"  Errors: {', '.join(result['errors'])}")

Part 4: Practical Applications and Integration
----------------------------------------------

4.1 Type-Safe Scientific Function Design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Design type-safe scientific functions using SciTeX types
    def safe_statistical_analysis(data, method='mean', confidence_level=0.95):
        """
        Perform statistical analysis with comprehensive type checking.
        
        Args:
            data: ArrayLike - Numeric data for analysis
            method: str - Statistical method ('mean', 'median', 'std', 'var')
            confidence_level: float - Confidence level for intervals
        
        Returns:
            dict: Analysis results or error information
        """
        result = {
            'success': False,
            'method': method,
            'data_info': {},
            'statistics': {},
            'errors': []
        }
        
        # Type checking
        if not scitex.types.is_array_like(data):
            result['errors'].append(f"Data is not array-like (type: {type(data).__name__})")
            return result
        
        # Convert to numpy for analysis
        try:
            if isinstance(data, pd.DataFrame):
                numeric_data = data.select_dtypes(include=[np.number])
                if numeric_data.empty:
                    result['errors'].append("DataFrame contains no numeric columns")
                    return result
                np_data = numeric_data.values.flatten()
            elif isinstance(data, pd.Series):
                if not pd.api.types.is_numeric_dtype(data):
                    result['errors'].append("Series is not numeric")
                    return result
                np_data = data.values
            else:
                np_data = np.array(data, dtype=float)
        except (ValueError, TypeError) as e:
            result['errors'].append(f"Cannot convert data to numeric array: {e}")
            return result
        
        # Remove NaN values and validate
        clean_data = np_data[~np.isnan(np_data)]
        
        if len(clean_data) == 0:
            result['errors'].append("No valid numeric data after removing NaN values")
            return result
        
        # Store data info
        result['data_info'] = {
            'original_size': len(np_data),
            'valid_size': len(clean_data),
            'nan_count': len(np_data) - len(clean_data),
            'data_type': type(data).__name__
        }
        
        # Perform statistical analysis
        try:
            if method == 'mean':
                stat_value = np.mean(clean_data)
                # Calculate confidence interval for mean
                sem = np.std(clean_data, ddof=1) / np.sqrt(len(clean_data))
                from scipy.stats import t
                t_val = t.ppf((1 + confidence_level) / 2, len(clean_data) - 1)
                margin = t_val * sem
                ci_lower = stat_value - margin
                ci_upper = stat_value + margin
                
            elif method == 'median':
                stat_value = np.median(clean_data)
                # Simple confidence interval for median (bootstrap approximation)
                n = len(clean_data)
                sorted_data = np.sort(clean_data)
                z_val = 1.96  # For 95% confidence
                margin = z_val * np.sqrt(n) / 2
                lower_idx = max(0, int(n/2 - margin))
                upper_idx = min(n-1, int(n/2 + margin))
                ci_lower = sorted_data[lower_idx]
                ci_upper = sorted_data[upper_idx]
                
            elif method == 'std':
                stat_value = np.std(clean_data, ddof=1)
                # Chi-square confidence interval for standard deviation
                from scipy.stats import chi2
                n = len(clean_data)
                chi2_lower = chi2.ppf((1 - confidence_level) / 2, n - 1)
                chi2_upper = chi2.ppf((1 + confidence_level) / 2, n - 1)
                ci_lower = np.sqrt((n - 1) * stat_value**2 / chi2_upper)
                ci_upper = np.sqrt((n - 1) * stat_value**2 / chi2_lower)
                
            elif method == 'var':
                stat_value = np.var(clean_data, ddof=1)
                # Chi-square confidence interval for variance
                from scipy.stats import chi2
                n = len(clean_data)
                chi2_lower = chi2.ppf((1 - confidence_level) / 2, n - 1)
                chi2_upper = chi2.ppf((1 + confidence_level) / 2, n - 1)
                ci_lower = (n - 1) * stat_value / chi2_upper
                ci_upper = (n - 1) * stat_value / chi2_lower
                
            else:
                result['errors'].append(f"Unknown method: {method}")
                return result
            
            result['statistics'] = {
                'value': stat_value,
                'confidence_interval': (ci_lower, ci_upper),
                'confidence_level': confidence_level
            }
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(f"Statistical calculation failed: {e}")
        
        return result
    
    def safe_plotting_function(x_data, y_data, colors=None, markers=None, title="Plot"):
        """
        Create a plot with comprehensive type checking.
        
        Args:
            x_data: ArrayLike - X coordinates
            y_data: ArrayLike - Y coordinates  
            colors: List of ColorLike objects or single ColorLike
            markers: List of strings or single string
            title: str - Plot title
        
        Returns:
            dict: Plot creation results
        """
        result = {
            'success': False,
            'errors': [],
            'warnings': [],
            'plot_info': {}
        }
        
        # Type checking for coordinates
        if not scitex.types.is_array_like(x_data):
            result['errors'].append("x_data is not array-like")
            return result
        
        if not scitex.types.is_array_like(y_data):
            result['errors'].append("y_data is not array-like")
            return result
        
        # Convert to numpy arrays
        try:
            x_array = np.array(x_data, dtype=float)
            y_array = np.array(y_data, dtype=float)
        except (ValueError, TypeError) as e:
            result['errors'].append(f"Cannot convert coordinates to numeric arrays: {e}")
            return result
        
        # Check dimensions match
        if len(x_array) != len(y_array):
            result['errors'].append(f"Coordinate arrays have different lengths: {len(x_array)} vs {len(y_array)}")
            return result
        
        # Validate colors if provided
        processed_colors = None
        if colors is not None:
            if isinstance(colors, (list, tuple)):
                # Check if it's a list of colors
                if scitex.types.is_list_of_type(colors, str):
                    processed_colors = colors
                else:
                    # Check if each element is a valid color
                    valid_colors = []
                    for i, color in enumerate(colors):
                        normalized = normalize_color(color)
                        if normalized:
                            valid_colors.append(normalized)
                        else:
                            result['warnings'].append(f"Invalid color at index {i}: {color}")
                    processed_colors = valid_colors if valid_colors else None
            else:
                # Single color
                normalized = normalize_color(colors)
                if normalized:
                    processed_colors = [normalized]
                else:
                    result['warnings'].append(f"Invalid color: {colors}")
        
        # Validate markers if provided
        processed_markers = None
        if markers is not None:
            if isinstance(markers, str):
                processed_markers = [markers]
            elif scitex.types.is_list_of_type(markers, str):
                processed_markers = markers
            else:
                result['warnings'].append("Invalid markers - must be string or list of strings")
        
        # Create the plot
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Plot data
            n_points = len(x_array)
            
            if processed_colors and processed_markers:
                # Use both colors and markers
                for i in range(n_points):
                    color_idx = i % len(processed_colors)
                    marker_idx = i % len(processed_markers)
                    ax.scatter(x_array[i], y_array[i], 
                              c=[processed_colors[color_idx]], 
                              marker=processed_markers[marker_idx],
                              s=50)
            elif processed_colors:
                # Use colors only
                for i in range(n_points):
                    color_idx = i % len(processed_colors)
                    ax.scatter(x_array[i], y_array[i], 
                              c=[processed_colors[color_idx]], s=50)
            elif processed_markers:
                # Use markers only
                for i in range(n_points):
                    marker_idx = i % len(processed_markers)
                    ax.scatter(x_array[i], y_array[i], 
                              marker=processed_markers[marker_idx], s=50)
            else:
                # Default plotting
                ax.scatter(x_array, y_array, s=50)
            
            ax.set_title(title)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            result['success'] = True
            result['plot_info'] = {
                'n_points': n_points,
                'x_range': (np.min(x_array), np.max(x_array)),
                'y_range': (np.min(y_array), np.max(y_array)),
                'colors_used': len(processed_colors) if processed_colors else 0,
                'markers_used': len(processed_markers) if processed_markers else 0
            }
            
        except Exception as e:
            result['errors'].append(f"Plot creation failed: {e}")
        
        return result
    
    # Test the type-safe functions
    print("Testing Type-Safe Scientific Functions:")
    print("=" * 45)
    
    # Test statistical analysis
    test_datasets = {
        'valid_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'numpy_array': np.random.normal(10, 2, 50),
        'pandas_series': pd.Series(np.random.exponential(2, 30)),
        'with_nan': [1, 2, float('nan'), 4, 5, 6, 7, 8, 9, 10],
        'invalid_data': 'not_array_like'
    }
    
    print("\nStatistical Analysis Tests:")
    print("-" * 30)
    
    for name, data in test_datasets.items():
        result = safe_statistical_analysis(data, method='mean')
        print(f"\n{name}:")
        print(f"  Success: {'✓' if result['success'] else '✗'}")
        
        if result['success']:
            stats = result['statistics']
            data_info = result['data_info']
            print(f"  Mean: {stats['value']:.3f}")
            print(f"  95% CI: ({stats['confidence_interval'][0]:.3f}, {stats['confidence_interval'][1]:.3f})")
            print(f"  Data: {data_info['valid_size']}/{data_info['original_size']} valid points")
        
        if result['errors']:
            print(f"  Errors: {', '.join(result['errors'])}")
    
    # Test plotting function
    print("\n\nPlotting Function Tests:")
    print("-" * 25)
    
    # Generate test data
    x_test = np.linspace(0, 10, 20)
    y_test = np.sin(x_test) + np.random.normal(0, 0.1, 20)
    
    test_colors = ['red', (0.2, 0.6, 0.8), '#FF5733']
    test_markers = ['o', 's', '^']
    
    plot_result = safe_plotting_function(
        x_test, y_test, 
        colors=test_colors, 
        markers=test_markers,
        title="Type-Safe Plotting Demo"
    )
    
    print(f"Plot creation: {'✓' if plot_result['success'] else '✗'}")
    if plot_result['success']:
        info = plot_result['plot_info']
        print(f"Points plotted: {info['n_points']}")
        print(f"X range: ({info['x_range'][0]:.2f}, {info['x_range'][1]:.2f})")
        print(f"Y range: ({info['y_range'][0]:.2f}, {info['y_range'][1]:.2f})")
        print(f"Colors used: {info['colors_used']}")
        print(f"Markers used: {info['markers_used']}")
    
    if plot_result['errors']:
        print(f"Errors: {', '.join(plot_result['errors'])}")
    if plot_result['warnings']:
        print(f"Warnings: {', '.join(plot_result['warnings'])}")

4.2 Performance Comparison and Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Performance comparison of type checking approaches
    import time
    from typing import get_type_hints
    
    def benchmark_type_checking():
        """
        Compare performance of different type checking approaches.
        """
        # Create test data
        test_data = {
            'small_list': list(range(100)),
            'large_list': list(range(10000)),
            'numpy_array': np.random.randn(10000),
            'pandas_series': pd.Series(range(10000)),
            'nested_list': [[i, i+1] for i in range(1000)]
        }
        
        # Type checking functions to compare
        def scitex_is_array_like(obj):
            return scitex.types.is_array_like(obj)
        
        def scitex_is_list_of_type(obj):
            return scitex.types.is_list_of_type(obj, int) if isinstance(obj, list) else False
        
        def manual_type_check(obj):
            return isinstance(obj, (list, tuple, np.ndarray, pd.Series, pd.DataFrame))
        
        def hasattr_check(obj):
            return hasattr(obj, '__iter__') and hasattr(obj, '__len__')
        
        # Benchmark functions
        functions_to_test = [
            ('SciTeX is_array_like', scitex_is_array_like),
            ('Manual isinstance', manual_type_check),
            ('hasattr check', hasattr_check)
        ]
        
        results = {}
        n_iterations = 1000
        
        print("Type Checking Performance Benchmark:")
        print("=" * 40)
        print(f"Iterations per test: {n_iterations}")
        
        for data_name, data in test_data.items():
            print(f"\nTesting with {data_name} (size: {len(data)}):")
            print("-" * 30)
            
            data_results = {}
            
            for func_name, func in functions_to_test:
                # Warm up
                for _ in range(10):
                    func(data)
                
                # Benchmark
                start_time = time.time()
                for _ in range(n_iterations):
                    result = func(data)
                end_time = time.time()
                
                total_time = end_time - start_time
                avg_time = total_time / n_iterations * 1000000  # microseconds
                
                data_results[func_name] = {
                    'total_time': total_time,
                    'avg_time_us': avg_time,
                    'result': result
                }
                
                print(f"  {func_name:20}: {avg_time:.2f} μs/call -> {result}")
            
            results[data_name] = data_results
        
        # Test list type checking performance
        print(f"\n\nList Type Checking Performance:")
        print("-" * 35)
        
        list_test_data = {
            'small_int_list': list(range(10)),
            'large_int_list': list(range(1000)),
            'mixed_list': [1, 'two', 3.0, [4]],
            'string_list': ['a', 'b', 'c', 'd', 'e'] * 100
        }
        
        for data_name, data in list_test_data.items():
            print(f"\n{data_name} (size: {len(data)}):")
            
            # SciTeX approach
            start_time = time.time()
            for _ in range(n_iterations):
                result_scitex = scitex.types.is_list_of_type(data, int)
            scitex_time = (time.time() - start_time) / n_iterations * 1000000
            
            # Manual approach
            start_time = time.time()
            for _ in range(n_iterations):
                result_manual = isinstance(data, list) and all(isinstance(x, int) for x in data)
            manual_time = (time.time() - start_time) / n_iterations * 1000000
            
            print(f"  SciTeX is_list_of_type: {scitex_time:.2f} μs/call -> {result_scitex}")
            print(f"  Manual check:           {manual_time:.2f} μs/call -> {result_manual}")
            print(f"  Speedup factor:         {scitex_time/manual_time:.2f}x")
        
        return results
    
    def demonstrate_best_practices():
        """
        Demonstrate best practices for using SciTeX type utilities.
        """
        print("\n\nSciTeX Types Best Practices:")
        print("=" * 35)
        
        print("\n1. Input Validation Pattern:")
        print("-" * 25)
        
        def robust_function(data, colors=None):
            """Example of robust input validation."""
            errors = []
            
            # Check main data
            if not scitex.types.is_array_like(data):
                errors.append("Data must be array-like")
                return {'success': False, 'errors': errors}
            
            # Check optional parameters
            if colors is not None:
                if isinstance(colors, list):
                    if not all(normalize_color(c) for c in colors):
                        errors.append("Some colors are invalid")
                else:
                    if not normalize_color(colors):
                        errors.append("Color is invalid")
            
            if errors:
                return {'success': False, 'errors': errors}
            
            return {'success': True, 'message': 'All inputs valid'}
        
        # Test the pattern
        test_cases = [
            ([1, 2, 3], 'red'),
            ('not_array', 'blue'),
            ([1, 2, 3], 'invalid_color'),
            (np.array([1, 2, 3]), ['red', 'blue', 'green'])
        ]
        
        for data, colors in test_cases:
            result = robust_function(data, colors)
            status = "✓" if result['success'] else "✗"
            print(f"  Data: {str(data)[:20]}, Colors: {colors} -> {status}")
            if not result['success']:
                print(f"    Errors: {', '.join(result['errors'])}")
        
        print("\n2. Type Conversion Pattern:")
        print("-" * 27)
        
        def flexible_array_function(data):
            """Example of flexible array handling."""
            if not scitex.types.is_array_like(data):
                return None
            
            # Convert to numpy for processing
            try:
                if isinstance(data, pd.DataFrame):
                    # Handle DataFrames specially
                    numeric_cols = data.select_dtypes(include=[np.number])
                    if not numeric_cols.empty:
                        array_data = numeric_cols.values
                    else:
                        return None
                else:
                    array_data = np.asarray(data)
                
                # Process the array
                result = np.sum(array_data)
                return result
                
            except Exception:
                return None
        
        # Test flexible handling
        flexible_test_data = [
            [1, 2, 3, 4, 5],
            np.array([1, 2, 3, 4, 5]),
            pd.Series([1, 2, 3, 4, 5]),
            pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]}),
            "not_array"
        ]
        
        for data in flexible_test_data:
            result = flexible_array_function(data)
            data_str = str(data)[:30] + "..." if len(str(data)) > 30 else str(data)
            if result is not None:
                print(f"  {data_str:35} -> Sum: {result}")
            else:
                print(f"  {data_str:35} -> Cannot process")
        
        print("\n3. Performance Tips:")
        print("-" * 17)
        print("  • Cache type checking results for repeated use")
        print("  • Use isinstance() for simple, known types")
        print("  • Use SciTeX types for flexible, cross-library compatibility")
        print("  • Validate inputs early in function execution")
        print("  • Provide clear error messages for type mismatches")
    
    # Run benchmarks and demonstrations
    benchmark_results = benchmark_type_checking()
    demonstrate_best_practices()

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive type handling capabilities
of the SciTeX types module:

Key Components Covered:
~~~~~~~~~~~~~~~~~~~~~~~

1. **ArrayLike Type Union**:

   -  Supports lists, tuples, NumPy arrays, Pandas Series/DataFrames,
      PyTorch tensors, XArray DataArrays
   -  Enables cross-library compatibility
   -  Provides flexible input handling for scientific functions

2. **ColorLike Type Union**:

   -  Supports string colors, RGB/RGBA tuples, RGB/RGBA lists
   -  Enables flexible color specification for plotting
   -  Integrates with matplotlib color systems

3. **List Type Checking Functions**:

   -  ``is_listed_X`` and ``is_list_of_type`` for validating list
      contents
   -  Support for multiple type specifications
   -  Robust error handling for edge cases

4. **Type Validation Functions**:

   -  ``is_array_like`` for checking array-like objects
   -  Consistent behavior across different data types
   -  Integration with scientific computing workflows

Best Practices:
~~~~~~~~~~~~~~~

Input Validation:
^^^^^^^^^^^^^^^^^

-  **Always validate inputs early** in function execution
-  **Provide clear error messages** that help users understand type
   requirements
-  **Use SciTeX type checking** for cross-library compatibility
-  **Handle edge cases** like empty arrays, NaN values, and mixed types

Performance Considerations:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **Cache type checking results** when performing repeated operations
-  **Use isinstance()** for simple, known types when performance is
   critical
-  **Leverage SciTeX types** for flexible, user-friendly APIs
-  **Convert to NumPy arrays** early for consistent numerical operations

Design Patterns:
^^^^^^^^^^^^^^^^

-  **Graceful degradation**: Handle type mismatches without crashing
-  **Flexible input handling**: Accept multiple array-like types
-  **Consistent output formats**: Return standardized result structures
-  **Comprehensive validation**: Check all aspects of input data

Scientific Applications:
^^^^^^^^^^^^^^^^^^^^^^^^

-  **Data pipeline validation**: Ensure data integrity through
   processing steps
-  **Plotting functions**: Accept flexible color and marker
   specifications
-  **Statistical analysis**: Validate numeric data before computation
-  **Machine learning**: Type-check features, labels, and model
   parameters

When to Use SciTeX Types:
~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Multi-library environments** where users may provide different
   array types
-  **User-facing APIs** that need to be flexible and forgiving
-  **Scientific computing** where data comes in various formats
-  **Plotting and visualization** where color/marker specifications vary
-  **Data validation** in research pipelines

The SciTeX types module provides essential tools for building robust,
flexible scientific computing applications that work seamlessly across
the Python data science ecosystem.

.. code:: ipython3

    print("SciTeX Type Handling Utilities Tutorial Complete!")
    print("\nKey takeaways:")
    print("1. ArrayLike enables seamless cross-library array handling")
    print("2. ColorLike provides flexible color specification for plotting")
    print("3. is_listed_X validates list contents with type safety")
    print("4. Type checking improves function robustness and user experience")
    print("5. SciTeX types balance flexibility with performance")
    print("6. Proper input validation prevents runtime errors in scientific workflows")
    print("7. Type-safe design patterns enhance code maintainability")
