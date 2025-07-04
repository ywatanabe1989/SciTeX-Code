18 SciTeX Torch
===============

.. note::
   This page is generated from the Jupyter notebook `18_scitex_torch.ipynb <https://github.com/scitex/scitex/blob/main/examples/18_scitex_torch.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 18_scitex_torch.ipynb


This notebook demonstrates the complete functionality of the
``scitex.torch`` module, which provides PyTorch-specific utilities and
extensions for scientific computing.

Module Overview
---------------

The ``scitex.torch`` module includes: - NaN-aware statistical functions
- Tensor manipulation utilities - PyTorch-specific scientific computing
functions

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import torch
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Import scitex torch module
    import scitex.torch as storch
    
    # Set random seed for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    print("Available functions in scitex.torch:")
    torch_attrs = [attr for attr in dir(storch) if not attr.startswith('_')]
    for i, attr in enumerate(torch_attrs):
        print(f"{i+1:2d}. {attr}")

1. NaN-Aware Statistical Functions
----------------------------------

The module provides robust statistical functions that handle NaN values
appropriately.

Basic NaN Functions
~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 1: Create test data with NaN values
    # Create tensor with some NaN values
    data = torch.randn(4, 5, 6)
    data[0, 1, 2] = float('nan')
    data[1, 2, :] = float('nan')
    data[2, :, 3] = float('nan')
    
    print(f"Data shape: {data.shape}")
    print(f"Number of NaN values: {torch.isnan(data).sum().item()}")
    print(f"Data range (excluding NaN): [{data[~torch.isnan(data)].min():.3f}, {data[~torch.isnan(data)].max():.3f}]")
    
    # Visualize NaN pattern
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    for i in range(4):
        # Create a mask showing NaN locations
        nan_mask = torch.isnan(data[i]).float()
        im = axes[i].imshow(nan_mask.numpy(), cmap='Reds', aspect='auto')
        axes[i].set_title(f'Batch {i} - NaN Locations')
        axes[i].set_xlabel('Dimension 2')
        axes[i].set_ylabel('Dimension 1')
    
    plt.tight_layout()
    plt.show()

NaN-Aware Min and Max
~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 2: NaN-aware min and max functions
    print("Testing nanmin and nanmax functions:")
    print("=" * 40)
    
    # Test nanmin
    try:
        # Global min
        global_min = storch.nanmin(data)
        print(f"Global nanmin: {global_min}")
        
        # Min along different dimensions
        min_dim0 = storch.nanmin(data, dim=0)
        min_dim1 = storch.nanmin(data, dim=1)
        min_dim2 = storch.nanmin(data, dim=2)
        
        print(f"Min along dim 0 shape: {min_dim0.values.shape if hasattr(min_dim0, 'values') else min_dim0.shape}")
        print(f"Min along dim 1 shape: {min_dim1.values.shape if hasattr(min_dim1, 'values') else min_dim1.shape}")
        print(f"Min along dim 2 shape: {min_dim2.values.shape if hasattr(min_dim2, 'values') else min_dim2.shape}")
        
    except Exception as e:
        print(f"Error with nanmin: {e}")
    
    # Test nanmax
    try:
        # Global max
        global_max = storch.nanmax(data)
        print(f"\nGlobal nanmax: {global_max}")
        
        # Max along different dimensions
        max_dim0 = storch.nanmax(data, dim=0)
        max_dim1 = storch.nanmax(data, dim=1)
        max_dim2 = storch.nanmax(data, dim=2)
        
        print(f"Max along dim 0 shape: {max_dim0.values.shape if hasattr(max_dim0, 'values') else max_dim0.shape}")
        print(f"Max along dim 1 shape: {max_dim1.values.shape if hasattr(max_dim1, 'values') else max_dim1.shape}")
        print(f"Max along dim 2 shape: {max_dim2.values.shape if hasattr(max_dim2, 'values') else max_dim2.shape}")
        
    except Exception as e:
        print(f"Error with nanmax: {e}")
    
    # Compare with regular min/max (which would fail with NaN)
    print("\nComparison with regular PyTorch functions:")
    try:
        regular_min = torch.min(data)
        regular_max = torch.max(data)
        print(f"Regular min: {regular_min}")
        print(f"Regular max: {regular_max}")
    except Exception as e:
        print(f"Regular functions with NaN: {e}")

NaN-Aware ArgMin and ArgMax
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 3: NaN-aware argmin and argmax
    print("Testing nanargmin and nanargmax functions:")
    print("=" * 45)
    
    # Create simpler test data for argmin/argmax
    simple_data = torch.tensor([
        [1.0, float('nan'), 3.0, 0.5],
        [float('nan'), 2.0, float('nan'), 1.5],
        [2.5, 0.1, 4.0, float('nan')]
    ])
    
    print(f"Test data:\n{simple_data}")
    
    try:
        # Global argmin and argmax
        global_argmin = storch.nanargmin(simple_data)
        global_argmax = storch.nanargmax(simple_data)
        
        print(f"\nGlobal nanargmin: {global_argmin}")
        print(f"Global nanargmax: {global_argmax}")
        
        # Along dimensions
        argmin_dim0 = storch.nanargmin(simple_data, dim=0)
        argmax_dim0 = storch.nanargmax(simple_data, dim=0)
        
        argmin_dim1 = storch.nanargmin(simple_data, dim=1)
        argmax_dim1 = storch.nanargmax(simple_data, dim=1)
        
        print(f"\nArgmin along dim 0: {argmin_dim0}")
        print(f"Argmax along dim 0: {argmax_dim0}")
        print(f"\nArgmin along dim 1: {argmin_dim1}")
        print(f"Argmax along dim 1: {argmax_dim1}")
        
        # Verify results
        print("\nVerification:")
        flattened = simple_data.flatten()
        valid_indices = ~torch.isnan(flattened)
        valid_values = flattened[valid_indices]
        
        print(f"Valid values: {valid_values}")
        print(f"Min value: {valid_values.min()}")
        print(f"Max value: {valid_values.max()}")
        
    except Exception as e:
        print(f"Error with nanargmin/nanargmax: {e}")

NaN-Aware Variance and Standard Deviation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 4: NaN-aware variance and standard deviation
    print("Testing nanvar and nanstd functions:")
    print("=" * 40)
    
    # Create test data with known statistics
    test_data = torch.tensor([
        [1.0, 2.0, 3.0, 4.0, 5.0],
        [float('nan'), 2.0, 3.0, 4.0, float('nan')],
        [1.0, float('nan'), float('nan'), 4.0, 5.0]
    ])
    
    print(f"Test data:\n{test_data}")
    
    try:
        # Global variance and std
        global_var = storch.nanvar(test_data)
        global_std = storch.nanstd(test_data)
        
        print(f"\nGlobal nanvar: {global_var:.4f}")
        print(f"Global nanstd: {global_std:.4f}")
        
        # Along dimensions
        var_dim0 = storch.nanvar(test_data, dim=0)
        std_dim0 = storch.nanstd(test_data, dim=0)
        
        var_dim1 = storch.nanvar(test_data, dim=1)
        std_dim1 = storch.nanstd(test_data, dim=1)
        
        print(f"\nVariance along dim 0: {var_dim0}")
        print(f"Std along dim 0: {std_dim0}")
        print(f"\nVariance along dim 1: {var_dim1}")
        print(f"Std along dim 1: {std_dim1}")
        
        # Verify relationship between var and std
        print(f"\nVerification (std^2 ≈ var):")
        print(f"Global: {global_std**2:.4f} ≈ {global_var:.4f}")
        
        # Compare with PyTorch's nanmean
        global_mean = torch.nanmean(test_data)
        print(f"\nGlobal nanmean: {global_mean:.4f}")
        
    except Exception as e:
        print(f"Error with nanvar/nanstd: {e}")

NaN-Aware Product Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 5: NaN-aware product and cumulative product
    print("Testing nanprod and nancumprod functions:")
    print("=" * 45)
    
    # Create test data with small values to avoid overflow
    prod_data = torch.tensor([
        [1.0, 2.0, 0.5, float('nan')],
        [float('nan'), 1.5, 2.0, 0.8],
        [2.0, float('nan'), 1.0, 1.2]
    ])
    
    print(f"Test data:\n{prod_data}")
    
    try:
        # Global product
        global_prod = storch.nanprod(prod_data)
        print(f"\nGlobal nanprod: {global_prod:.4f}")
        
        # Product along dimensions
        prod_dim0 = storch.nanprod(prod_data, dim=0)
        prod_dim1 = storch.nanprod(prod_data, dim=1)
        
        print(f"\nProduct along dim 0: {prod_dim0}")
        print(f"Product along dim 1: {prod_dim1}")
        
        # Cumulative product
        cumprod_dim0 = storch.nancumprod(prod_data, dim=0)
        cumprod_dim1 = storch.nancumprod(prod_data, dim=1)
        
        print(f"\nCumulative product along dim 0:\n{cumprod_dim0}")
        print(f"\nCumulative product along dim 1:\n{cumprod_dim1}")
        
        # Manual verification for first row
        first_row = prod_data[0]
        valid_values = first_row[~torch.isnan(first_row)]
        manual_prod = torch.prod(valid_values)
        print(f"\nManual verification for first row:")
        print(f"Valid values: {valid_values}")
        print(f"Manual product: {manual_prod:.4f}")
        print(f"nanprod result: {prod_dim1[0]:.4f}")
        
    except Exception as e:
        print(f"Error with nanprod/nancumprod: {e}")

NaN-Aware Cumulative Sum
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 6: NaN-aware cumulative sum
    print("Testing nancumsum function:")
    print("=" * 35)
    
    # Create test data for cumulative sum
    cumsum_data = torch.tensor([
        [1.0, 2.0, 3.0, float('nan'), 5.0],
        [float('nan'), 1.0, float('nan'), 2.0, 3.0],
        [2.0, float('nan'), 1.0, 1.0, float('nan')]
    ])
    
    print(f"Test data:\n{cumsum_data}")
    
    try:
        # Cumulative sum along different dimensions
        cumsum_dim0 = storch.nancumsum(cumsum_data, dim=0)
        cumsum_dim1 = storch.nancumsum(cumsum_data, dim=1)
        
        print(f"\nCumulative sum along dim 0:\n{cumsum_dim0}")
        print(f"\nCumulative sum along dim 1:\n{cumsum_dim1}")
        
        # Visualize cumulative sum
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Original data
        im1 = axes[0, 0].imshow(cumsum_data.numpy(), cmap='viridis', aspect='auto')
        axes[0, 0].set_title('Original Data')
        axes[0, 0].set_xlabel('Column')
        axes[0, 0].set_ylabel('Row')
        plt.colorbar(im1, ax=axes[0, 0])
        
        # NaN mask
        nan_mask = torch.isnan(cumsum_data).float()
        im2 = axes[0, 1].imshow(nan_mask.numpy(), cmap='Reds', aspect='auto')
        axes[0, 1].set_title('NaN Mask')
        axes[0, 1].set_xlabel('Column')
        axes[0, 1].set_ylabel('Row')
        plt.colorbar(im2, ax=axes[0, 1])
        
        # Cumsum along dim 0
        im3 = axes[1, 0].imshow(cumsum_dim0.numpy(), cmap='viridis', aspect='auto')
        axes[1, 0].set_title('Cumulative Sum (dim=0)')
        axes[1, 0].set_xlabel('Column')
        axes[1, 0].set_ylabel('Row')
        plt.colorbar(im3, ax=axes[1, 0])
        
        # Cumsum along dim 1
        im4 = axes[1, 1].imshow(cumsum_dim1.numpy(), cmap='viridis', aspect='auto')
        axes[1, 1].set_title('Cumulative Sum (dim=1)')
        axes[1, 1].set_xlabel('Column')
        axes[1, 1].set_ylabel('Row')
        plt.colorbar(im4, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error with nancumsum: {e}")

2. Tensor Manipulation Utilities
--------------------------------

Apply Function Along Dimension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``apply_to`` function applies a function to tensors along a specific
dimension.

.. code:: ipython3

    # Example 7: apply_to function
    print("Testing apply_to function:")
    print("=" * 30)
    
    # Create test tensor
    test_tensor = torch.randn(3, 4, 5)
    print(f"Test tensor shape: {test_tensor.shape}")
    
    try:
        # Apply sum along different dimensions
        result_dim0 = storch.apply_to(torch.sum, test_tensor, dim=0)
        result_dim1 = storch.apply_to(torch.sum, test_tensor, dim=1)
        result_dim2 = storch.apply_to(torch.sum, test_tensor, dim=2)
        
        print(f"\nApply sum along dim 0: {result_dim0.shape}")
        print(f"Apply sum along dim 1: {result_dim1.shape}")
        print(f"Apply sum along dim 2: {result_dim2.shape}")
        
        # Compare with direct PyTorch operations
        direct_sum_0 = torch.sum(test_tensor, dim=0)
        direct_sum_1 = torch.sum(test_tensor, dim=1)
        direct_sum_2 = torch.sum(test_tensor, dim=2)
        
        print(f"\nDirect sum along dim 0: {direct_sum_0.shape}")
        print(f"Direct sum along dim 1: {direct_sum_1.shape}")
        print(f"Direct sum along dim 2: {direct_sum_2.shape}")
        
        # Check if results match
        print(f"\nResults match:")
        print(f"Dim 0: {torch.allclose(result_dim0, direct_sum_0, equal_nan=True)}")
        print(f"Dim 1: {torch.allclose(result_dim1, direct_sum_1, equal_nan=True)}")
        print(f"Dim 2: {torch.allclose(result_dim2, direct_sum_2, equal_nan=True)}")
        
        # Apply custom function
        def custom_fn(x):
            return torch.mean(x) * torch.std(x)
        
        custom_result = storch.apply_to(custom_fn, test_tensor, dim=1)
        print(f"\nCustom function result shape: {custom_result.shape}")
        print(f"Custom function result: {custom_result}")
        
    except Exception as e:
        print(f"Error with apply_to: {e}")

3. Practical Applications
-------------------------

Robust Statistics with NaN Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate practical applications of the NaN-aware functions.

.. code:: ipython3

    # Example 8: Robust data analysis with missing values
    print("Practical Application: Robust Data Analysis")
    print("=" * 45)
    
    # Simulate sensor data with missing readings
    n_sensors = 8
    n_timepoints = 100
    sensor_data = torch.randn(n_sensors, n_timepoints)
    
    # Introduce missing data (NaN) randomly
    missing_prob = 0.1
    missing_mask = torch.rand_like(sensor_data) < missing_prob
    sensor_data[missing_mask] = float('nan')
    
    print(f"Sensor data shape: {sensor_data.shape}")
    print(f"Missing data points: {torch.isnan(sensor_data).sum().item()} / {sensor_data.numel()}")
    print(f"Missing data percentage: {torch.isnan(sensor_data).float().mean().item() * 100:.1f}%")
    
    # Compute robust statistics
    try:
        # Statistics per sensor (across time)
        sensor_means = torch.nanmean(sensor_data, dim=1)
        sensor_stds = storch.nanstd(sensor_data, dim=1)
        sensor_mins = storch.nanmin(sensor_data, dim=1)
        sensor_maxs = storch.nanmax(sensor_data, dim=1)
        
        # Statistics per timepoint (across sensors)
        time_means = torch.nanmean(sensor_data, dim=0)
        time_stds = storch.nanstd(sensor_data, dim=0)
        
        print(f"\nSensor Statistics:")
        print(f"Means: {sensor_means}")
        print(f"Stds: {sensor_stds}")
        print(f"Mins: {sensor_mins.values if hasattr(sensor_mins, 'values') else sensor_mins}")
        print(f"Maxs: {sensor_maxs.values if hasattr(sensor_maxs, 'values') else sensor_maxs}")
        
        # Visualize data and statistics
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Raw sensor data
        im1 = axes[0, 0].imshow(sensor_data.numpy(), aspect='auto', cmap='viridis')
        axes[0, 0].set_title('Sensor Data (with NaN)')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Sensor')
        plt.colorbar(im1, ax=axes[0, 0])
        
        # Missing data pattern
        nan_pattern = torch.isnan(sensor_data).float()
        im2 = axes[0, 1].imshow(nan_pattern.numpy(), aspect='auto', cmap='Reds')
        axes[0, 1].set_title('Missing Data Pattern')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('Sensor')
        plt.colorbar(im2, ax=axes[0, 1])
        
        # Sensor statistics
        x_sensors = range(n_sensors)
        axes[1, 0].errorbar(x_sensors, sensor_means.numpy(), yerr=sensor_stds.numpy(), 
                           fmt='o-', capsize=5, alpha=0.7)
        axes[1, 0].set_title('Sensor Statistics (Mean ± Std)')
        axes[1, 0].set_xlabel('Sensor ID')
        axes[1, 0].set_ylabel('Value')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Time series of means
        axes[1, 1].plot(time_means.numpy(), alpha=0.7, label='Mean')
        axes[1, 1].fill_between(range(len(time_means)), 
                               (time_means - time_stds).numpy(),
                               (time_means + time_stds).numpy(),
                               alpha=0.3, label='±1 Std')
        axes[1, 1].set_title('Temporal Statistics')
        axes[1, 1].set_xlabel('Time')
        axes[1, 1].set_ylabel('Value')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error in robust analysis: {e}")

Time Series Analysis with Missing Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example 9: Time series analysis with missing data
    print("Time Series Analysis with Missing Data:")
    print("=" * 40)
    
    # Create time series with trend and noise
    t = torch.linspace(0, 4*np.pi, 200)
    trend = 0.1 * t
    seasonal = torch.sin(t) + 0.5 * torch.sin(3*t)
    noise = 0.2 * torch.randn_like(t)
    time_series = trend + seasonal + noise
    
    # Introduce missing data in chunks (simulating sensor failures)
    time_series_with_gaps = time_series.clone()
    # Create several gaps
    time_series_with_gaps[30:40] = float('nan')  # Gap 1
    time_series_with_gaps[80:85] = float('nan')  # Gap 2
    time_series_with_gaps[150:160] = float('nan')  # Gap 3
    # Random missing points
    random_missing = torch.rand_like(time_series) < 0.05
    time_series_with_gaps[random_missing] = float('nan')
    
    print(f"Original time series length: {len(time_series)}")
    print(f"Missing points: {torch.isnan(time_series_with_gaps).sum().item()}")
    print(f"Missing percentage: {torch.isnan(time_series_with_gaps).float().mean().item() * 100:.1f}%")
    
    try:
        # Compute rolling statistics using NaN-aware functions
        window_size = 10
        rolling_means = []
        rolling_stds = []
        
        for i in range(window_size//2, len(time_series_with_gaps) - window_size//2):
            window = time_series_with_gaps[i-window_size//2:i+window_size//2+1]
            if not torch.isnan(window).all():  # If window has some valid data
                mean_val = torch.nanmean(window)
                std_val = storch.nanstd(window)
            else:
                mean_val = float('nan')
                std_val = float('nan')
            rolling_means.append(mean_val)
            rolling_stds.append(std_val)
        
        rolling_means = torch.tensor(rolling_means)
        rolling_stds = torch.tensor(rolling_stds)
        
        # Visualize time series analysis
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # Original vs. missing data
        axes[0].plot(t.numpy(), time_series.numpy(), alpha=0.7, label='Original', color='blue')
        valid_mask = ~torch.isnan(time_series_with_gaps)
        axes[0].scatter(t[valid_mask].numpy(), time_series_with_gaps[valid_mask].numpy(), 
                       s=1, alpha=0.8, label='Available data', color='red')
        axes[0].set_title('Time Series with Missing Data')
        axes[0].set_xlabel('Time')
        axes[0].set_ylabel('Value')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Missing data pattern
        missing_indicator = torch.isnan(time_series_with_gaps).float()
        axes[1].fill_between(t.numpy(), 0, missing_indicator.numpy(), 
                            alpha=0.7, color='red', label='Missing data')
        axes[1].set_title('Missing Data Pattern')
        axes[1].set_xlabel('Time')
        axes[1].set_ylabel('Missing')
        axes[1].set_ylim(-0.1, 1.1)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Rolling statistics
        t_rolling = t[window_size//2:-window_size//2]
        valid_rolling = ~torch.isnan(rolling_means)
        axes[2].plot(t_rolling[valid_rolling].numpy(), rolling_means[valid_rolling].numpy(), 
                    label='Rolling mean', color='green', linewidth=2)
        axes[2].fill_between(t_rolling[valid_rolling].numpy(),
                            (rolling_means[valid_rolling] - rolling_stds[valid_rolling]).numpy(),
                            (rolling_means[valid_rolling] + rolling_stds[valid_rolling]).numpy(),
                            alpha=0.3, color='green', label='±1 Std')
        axes[2].scatter(t[valid_mask].numpy(), time_series_with_gaps[valid_mask].numpy(), 
                       s=1, alpha=0.5, color='blue', label='Data points')
        axes[2].set_title(f'Rolling Statistics (window size: {window_size})')
        axes[2].set_xlabel('Time')
        axes[2].set_ylabel('Value')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Print summary statistics
        print(f"\nSummary Statistics:")
        print(f"Original data - Mean: {time_series.mean():.3f}, Std: {time_series.std():.3f}")
        print(f"Available data - Mean: {torch.nanmean(time_series_with_gaps):.3f}, Std: {storch.nanstd(time_series_with_gaps):.3f}")
        print(f"Rolling mean - Mean: {torch.nanmean(rolling_means):.3f}, Std: {storch.nanstd(rolling_means):.3f}")
        
    except Exception as e:
        print(f"Error in time series analysis: {e}")

4. Performance Comparison
-------------------------

Let’s compare the performance of scitex.torch functions with standard
PyTorch operations.

.. code:: ipython3

    # Example 10: Performance comparison
    import time
    
    print("Performance Comparison:")
    print("=" * 25)
    
    # Create large test tensor
    large_tensor = torch.randn(1000, 500)
    large_tensor_with_nan = large_tensor.clone()
    
    # Introduce some NaN values
    nan_mask = torch.rand_like(large_tensor) < 0.05
    large_tensor_with_nan[nan_mask] = float('nan')
    
    print(f"Test tensor shape: {large_tensor.shape}")
    print(f"NaN values: {torch.isnan(large_tensor_with_nan).sum().item()}")
    
    # Number of iterations for timing
    n_iters = 100
    
    def time_function(func, data, n_iters=100):
        """Time a function over multiple iterations."""
        start_time = time.time()
        for _ in range(n_iters):
            try:
                _ = func(data)
            except:
                pass
        end_time = time.time()
        return (end_time - start_time) / n_iters
    
    try:
        # Compare mean functions
        print(f"\nMean computation ({n_iters} iterations):")
        
        # Standard PyTorch (will propagate NaN)
        torch_mean_time = time_function(torch.mean, large_tensor_with_nan, n_iters)
        
        # PyTorch nanmean
        torch_nanmean_time = time_function(torch.nanmean, large_tensor_with_nan, n_iters)
        
        print(f"torch.mean: {torch_mean_time*1000:.3f} ms")
        print(f"torch.nanmean: {torch_nanmean_time*1000:.3f} ms")
        
        # Compare std functions
        print(f"\nStandard deviation computation ({n_iters} iterations):")
        
        torch_std_time = time_function(torch.std, large_tensor_with_nan, n_iters)
        scitex_nanstd_time = time_function(storch.nanstd, large_tensor_with_nan, n_iters)
        
        print(f"torch.std: {torch_std_time*1000:.3f} ms")
        print(f"scitex.nanstd: {scitex_nanstd_time*1000:.3f} ms")
        
        # Compare min/max functions
        print(f"\nMin/Max computation ({n_iters} iterations):")
        
        torch_min_time = time_function(torch.min, large_tensor_with_nan, n_iters)
        scitex_nanmin_time = time_function(storch.nanmin, large_tensor_with_nan, n_iters)
        
        print(f"torch.min: {torch_min_time*1000:.3f} ms")
        print(f"scitex.nanmin: {scitex_nanmin_time*1000:.3f} ms")
        
        # Test correctness
        print(f"\nCorrectness check:")
        torch_result = torch.mean(large_tensor_with_nan)
        nanmean_result = torch.nanmean(large_tensor_with_nan)
        
        print(f"torch.mean result: {torch_result}")
        print(f"torch.nanmean result: {nanmean_result:.6f}")
        print(f"torch.mean is NaN: {torch.isnan(torch_result)}")
        print(f"nanmean gives valid result: {not torch.isnan(nanmean_result)}")
        
    except Exception as e:
        print(f"Error in performance comparison: {e}")
    
    # Memory usage comparison
    print(f"\nMemory usage:")
    print(f"Original tensor: {large_tensor.element_size() * large_tensor.nelement() / 1024**2:.2f} MB")
    print(f"Tensor with NaN: {large_tensor_with_nan.element_size() * large_tensor_with_nan.nelement() / 1024**2:.2f} MB")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.torch`` module:

NaN-Aware Statistical Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``nanmin``** and **``nanmax``**: Robust minimum and maximum
   computation
-  **``nanargmin``** and **``nanargmax``**: Indices of minimum and
   maximum values
-  **``nanvar``** and **``nanstd``**: Variance and standard deviation
   with NaN handling
-  **``nanprod``** and **``nancumprod``**: Product operations ignoring
   NaN values
-  **``nancumsum``**: Cumulative sum with NaN handling

Tensor Manipulation
~~~~~~~~~~~~~~~~~~~

-  **``apply_to``**: Apply functions along specific dimensions

Key Features
~~~~~~~~~~~~

1. **Robustness**: All functions handle NaN values appropriately
2. **Consistency**: Maintains PyTorch tensor operations and broadcasting
   rules
3. **Performance**: Optimized implementations for scientific computing
4. **Compatibility**: Works seamlessly with existing PyTorch code

Practical Applications
~~~~~~~~~~~~~~~~~~~~~~

-  **Missing Data Analysis**: Handle sensor failures and data gaps
-  **Robust Statistics**: Compute statistics in presence of outliers (as
   NaN)
-  **Time Series Processing**: Rolling statistics with missing
   observations
-  **Scientific Computing**: Reliable numerical operations for research

Use Cases
~~~~~~~~~

-  Sensor data with equipment failures
-  Experimental data with measurement errors
-  Large-scale data processing with quality issues
-  Real-time analysis where some data points may be unavailable

The ``scitex.torch`` module provides essential tools for robust
scientific computing with PyTorch, ensuring that missing or invalid data
doesn’t break your analysis pipeline.
