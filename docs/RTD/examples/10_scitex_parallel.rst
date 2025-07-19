10 SciTeX Parallel
==================

.. note::
   This page is generated from the Jupyter notebook `10_scitex_parallel.ipynb <https://github.com/scitex/scitex/blob/main/examples/10_scitex_parallel.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 10_scitex_parallel.ipynb


This notebook demonstrates the complete functionality of the
``scitex.parallel`` module, which provides parallel processing utilities
for scientific computing tasks.

Module Overview
---------------

The ``scitex.parallel`` module includes: - Parallel function execution
using ThreadPoolExecutor - Automatic CPU core detection and utilization
- Progress tracking with tqdm integration - Support for multiple return
values and tuple handling

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import time
    import numpy as np
    import pandas as pd
    import multiprocessing
    from functools import partial
    import matplotlib.pyplot as plt
    
    # Import scitex parallel module
    import scitex.parallel as spar
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("Available functions in scitex.parallel:")
    parallel_attrs = [attr for attr in dir(spar) if not attr.startswith('_')]
    for i, attr in enumerate(parallel_attrs):
        print(f"{i+1:2d}. {attr}")
    
    print(f"\nSystem Information:")
    print(f"CPU cores available: {multiprocessing.cpu_count()}")
    print(f"Default parallel jobs: {multiprocessing.cpu_count()}")

1. Basic Parallel Execution
---------------------------

Simple Mathematical Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s start with basic parallel execution of mathematical operations.

.. code:: ipython3

    # Example 1: Basic parallel mathematical operations
    print("Basic Parallel Mathematical Operations:")
    print("=" * 40)
    
    # Define simple mathematical functions
    def square(x):
        """Compute square of a number."""
        time.sleep(0.01)  # Simulate some computation time
        return x ** 2
    
    def add_numbers(x, y):
        """Add two numbers."""
        time.sleep(0.01)  # Simulate computation time
        return x + y
    
    def compute_stats(x):
        """Compute multiple statistics for a number."""
        time.sleep(0.01)  # Simulate computation time
        return x, x**2, x**3, np.sqrt(abs(x))
    
    # Test data
    test_numbers = list(range(1, 21))  # Numbers 1 to 20
    print(f"Test data: {test_numbers[:10]}... (20 numbers total)")
    
    # Example 1a: Single argument function
    print("\n1a. Single argument function (square):")
    args_list_single = [(x,) for x in test_numbers]  # Convert to tuple format
    
    # Sequential execution for comparison
    start_time = time.time()
    sequential_results = [square(x) for x in test_numbers]
    sequential_time = time.time() - start_time
    
    # Parallel execution
    start_time = time.time()
    parallel_results = spar.run(square, args_list_single, desc="Computing squares")
    parallel_time = time.time() - start_time
    
    print(f"Sequential results: {sequential_results[:5]}... (first 5)")
    print(f"Parallel results:   {parallel_results[:5]}... (first 5)")
    print(f"Results match: {sequential_results == parallel_results}")
    print(f"Sequential time: {sequential_time:.4f} seconds")
    print(f"Parallel time:   {parallel_time:.4f} seconds")
    print(f"Speedup: {sequential_time / parallel_time:.2f}x")
    
    # Example 1b: Two argument function
    print("\n1b. Two argument function (addition):")
    args_list_double = [(i, i+10) for i in test_numbers]  # (1,11), (2,12), etc.
    
    start_time = time.time()
    add_results = spar.run(add_numbers, args_list_double, desc="Adding numbers")
    add_time = time.time() - start_time
    
    print(f"Addition arguments: {args_list_double[:5]}... (first 5)")
    print(f"Addition results:   {add_results[:5]}... (first 5)")
    print(f"Parallel time: {add_time:.4f} seconds")
    
    # Verify results manually
    expected = [i + (i+10) for i in test_numbers]
    print(f"Manual verification: {add_results == expected}")

Multiple Return Values
~~~~~~~~~~~~~~~~~~~~~~

The parallel module handles functions that return multiple values
(tuples).

.. code:: ipython3

    # Example 2: Functions with multiple return values
    print("Functions with Multiple Return Values:")
    print("=" * 35)
    
    # Test with smaller dataset for clarity
    test_data = [1, 2, 3, 4, 5]
    args_list_stats = [(x,) for x in test_data]
    
    print(f"Test data: {test_data}")
    print(f"Function returns: (x, x^2, x^3, sqrt(|x|))")
    
    # Run parallel computation
    start_time = time.time()
    multi_results = spar.run(compute_stats, args_list_stats, desc="Computing statistics")
    multi_time = time.time() - start_time
    
    print(f"\nResults structure: {type(multi_results)}")
    print(f"Number of result arrays: {len(multi_results)}")
    
    if isinstance(multi_results, tuple):
        values, squares, cubes, sqrts = multi_results
        
        print(f"\nOriginal values: {values}")
        print(f"Squares:         {squares}")
        print(f"Cubes:           {cubes}")
        print(f"Square roots:    {[f'{x:.3f}' for x in sqrts]}")
        
        # Verify results
        print(f"\nVerification:")
        print(f"Values correct:  {values == test_data}")
        print(f"Squares correct: {squares == [x**2 for x in test_data]}")
        print(f"Cubes correct:   {cubes == [x**3 for x in test_data]}")
        
    else:
        print(f"Unexpected result format: {multi_results}")
    
    print(f"\nExecution time: {multi_time:.4f} seconds")

2. Scientific Computing Applications
------------------------------------

Numerical Integration
~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate parallel processing for numerical integration tasks.

.. code:: ipython3

    # Example 3: Parallel numerical integration
    print("Parallel Numerical Integration:")
    print("=" * 35)
    
    def monte_carlo_pi(n_samples):
        """Estimate π using Monte Carlo method."""
        # Generate random points in unit square
        x = np.random.uniform(-1, 1, n_samples)
        y = np.random.uniform(-1, 1, n_samples)
        
        # Count points inside unit circle
        inside_circle = (x**2 + y**2) <= 1
        pi_estimate = 4 * np.sum(inside_circle) / n_samples
        
        return pi_estimate, n_samples
    
    def integrate_function(a, b, n_points, func_name='sin'):
        """Integrate a function using trapezoidal rule."""
        x = np.linspace(a, b, n_points)
        
        if func_name == 'sin':
            y = np.sin(x)
        elif func_name == 'cos':
            y = np.cos(x)
        elif func_name == 'exp':
            y = np.exp(-x**2)  # Gaussian
        else:
            y = x**2  # Parabola
        
        # Trapezoidal integration
        integral = np.trapz(y, x)
        return integral, func_name, (a, b)
    
    # Example 3a: Monte Carlo π estimation with different sample sizes
    print("3a. Monte Carlo π estimation:")
    sample_sizes = [10000, 50000, 100000, 200000, 500000]
    mc_args = [(n,) for n in sample_sizes]
    
    print(f"Sample sizes: {sample_sizes}")
    
    start_time = time.time()
    pi_results = spar.run(monte_carlo_pi, mc_args, desc="Estimating π")
    mc_time = time.time() - start_time
    
    if isinstance(pi_results, tuple):
        pi_estimates, sample_counts = pi_results
        
        print(f"\nπ estimates: {[f'{pi:.6f}' for pi in pi_estimates]}")
        print(f"True π:      {np.pi:.6f}")
        print(f"Errors:      {[f'{abs(pi - np.pi):.6f}' for pi in pi_estimates]}")
        print(f"Sample sizes: {sample_counts}")
        
        # Show convergence
        plt.figure(figsize=(10, 6))
        plt.subplot(1, 2, 1)
        plt.semilogx(sample_counts, pi_estimates, 'bo-', label='Estimates')
        plt.axhline(y=np.pi, color='r', linestyle='--', label='True π')
        plt.xlabel('Sample Size')
        plt.ylabel('π Estimate')
        plt.title('Monte Carlo Convergence')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        errors = [abs(pi - np.pi) for pi in pi_estimates]
        plt.loglog(sample_counts, errors, 'ro-', label='Absolute Error')
        plt.xlabel('Sample Size')
        plt.ylabel('Absolute Error')
        plt.title('Error vs Sample Size')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    print(f"Monte Carlo execution time: {mc_time:.4f} seconds")
    
    # Example 3b: Numerical integration of different functions
    print("\n3b. Numerical integration of various functions:")
    integration_tasks = [
        (0, np.pi, 1000, 'sin'),      # ∫sin(x)dx from 0 to π = 2
        (0, np.pi/2, 1000, 'cos'),    # ∫cos(x)dx from 0 to π/2 = 1
        (-2, 2, 1000, 'exp'),         # ∫exp(-x²)dx from -2 to 2 ≈ √π
        (0, 2, 1000, 'parabola'),     # ∫x²dx from 0 to 2 = 8/3
    ]
    
    print(f"Integration tasks: {len(integration_tasks)}")
    for i, (a, b, n, func) in enumerate(integration_tasks):
        print(f"  {i+1}. ∫{func}(x)dx from {a} to {b} with {n} points")
    
    start_time = time.time()
    int_results = spar.run(integrate_function, integration_tasks, desc="Integrating functions")
    int_time = time.time() - start_time
    
    if isinstance(int_results, tuple):
        integrals, func_names, intervals = int_results
        
        print(f"\nIntegration Results:")
        expected_values = [2.0, 1.0, np.sqrt(np.pi), 8/3]
        
        for i, (integral, func, interval, expected) in enumerate(zip(integrals, func_names, intervals, expected_values)):
            error = abs(integral - expected)
            print(f"  {i+1}. {func}({interval}): {integral:.6f} (expected: {expected:.6f}, error: {error:.6f})")
    
    print(f"Integration execution time: {int_time:.4f} seconds")

Data Processing and Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate parallel processing for data analysis tasks.

.. code:: ipython3

    # Example 4: Parallel data processing and analysis
    print("Parallel Data Processing and Analysis:")
    print("=" * 40)
    
    def analyze_dataset(data_id, n_samples, noise_level):
        """Analyze a synthetic dataset."""
        # Generate synthetic data
        np.random.seed(data_id)  # Ensure reproducibility
        
        # Create synthetic time series with trend and noise
        t = np.linspace(0, 10, n_samples)
        signal = np.sin(2 * np.pi * t) + 0.5 * np.cos(4 * np.pi * t)
        noise = noise_level * np.random.randn(n_samples)
        data = signal + noise
        
        # Compute statistics
        mean_val = np.mean(data)
        std_val = np.std(data)
        min_val = np.min(data)
        max_val = np.max(data)
        
        # Compute frequency domain features
        fft = np.fft.fft(data)
        power_spectrum = np.abs(fft)**2
        dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
        
        return (data_id, mean_val, std_val, min_val, max_val, dominant_freq_idx, n_samples)
    
    def process_image_batch(batch_id, image_size, filter_type):
        """Process a batch of synthetic images."""
        np.random.seed(batch_id * 100)  # Ensure reproducibility
        
        # Generate synthetic image
        image = np.random.randn(image_size, image_size)
        
        # Apply different filters
        if filter_type == 'gaussian':
            # Simple Gaussian-like filter (moving average)
            from scipy import ndimage
            try:
                filtered = ndimage.gaussian_filter(image, sigma=1.0)
            except ImportError:
                # Fallback if scipy not available
                filtered = image  # No filtering
        elif filter_type == 'edge':
            # Simple edge detection (gradient)
            filtered = np.gradient(image)[0] + np.gradient(image)[1]
        else:
            # No filter
            filtered = image
        
        # Compute image statistics
        mean_intensity = np.mean(filtered)
        std_intensity = np.std(filtered)
        total_energy = np.sum(filtered**2)
        
        return (batch_id, filter_type, mean_intensity, std_intensity, total_energy, image_size)
    
    # Example 4a: Parallel time series analysis
    print("4a. Parallel time series analysis:")
    
    # Create analysis tasks with different parameters
    analysis_tasks = [
        (1, 1000, 0.1),   # Low noise
        (2, 1000, 0.3),   # Medium noise
        (3, 1000, 0.5),   # High noise
        (4, 2000, 0.2),   # More samples
        (5, 500, 0.2),    # Fewer samples
        (6, 1000, 0.0),   # No noise
    ]
    
    print(f"Analysis tasks: {len(analysis_tasks)}")
    for task in analysis_tasks:
        data_id, n_samples, noise_level = task
        print(f"  Dataset {data_id}: {n_samples} samples, noise level {noise_level}")
    
    start_time = time.time()
    analysis_results = spar.run(analyze_dataset, analysis_tasks, desc="Analyzing datasets")
    analysis_time = time.time() - start_time
    
    if isinstance(analysis_results, tuple):
        data_ids, means, stds, mins, maxs, dom_freqs, sample_counts = analysis_results
        
        print(f"\nAnalysis Results:")
        print(f"Dataset | Samples | Mean    | Std     | Range          | Dom.Freq")
        print("-" * 65)
        
        for i in range(len(data_ids)):
            range_val = maxs[i] - mins[i]
            print(f"   {data_ids[i]:2d}   |  {sample_counts[i]:4d}   | {means[i]:6.3f}  | {stds[i]:6.3f}  | {range_val:6.3f}        |   {dom_freqs[i]:3d}")
        
        # Visualize some results
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Plot means vs std
        axes[0, 0].scatter(means, stds)
        axes[0, 0].set_xlabel('Mean')
        axes[0, 0].set_ylabel('Standard Deviation')
        axes[0, 0].set_title('Mean vs Std Deviation')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot sample counts vs std
        axes[0, 1].scatter(sample_counts, stds)
        axes[0, 1].set_xlabel('Sample Count')
        axes[0, 1].set_ylabel('Standard Deviation')
        axes[0, 1].set_title('Sample Count vs Std Deviation')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot data ranges
        ranges = [maxs[i] - mins[i] for i in range(len(data_ids))]
        axes[1, 0].bar(data_ids, ranges)
        axes[1, 0].set_xlabel('Dataset ID')
        axes[1, 0].set_ylabel('Data Range')
        axes[1, 0].set_title('Data Range by Dataset')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot dominant frequencies
        axes[1, 1].bar(data_ids, dom_freqs)
        axes[1, 1].set_xlabel('Dataset ID')
        axes[1, 1].set_ylabel('Dominant Frequency Index')
        axes[1, 1].set_title('Dominant Frequency by Dataset')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    print(f"Time series analysis time: {analysis_time:.4f} seconds")
    
    # Example 4b: Parallel image processing
    print("\n4b. Parallel image processing:")
    
    image_tasks = [
        (1, 64, 'none'),      # Small image, no filter
        (2, 64, 'gaussian'),  # Small image, Gaussian filter
        (3, 64, 'edge'),      # Small image, edge detection
        (4, 128, 'none'),     # Medium image, no filter
        (5, 128, 'gaussian'), # Medium image, Gaussian filter
        (6, 128, 'edge'),     # Medium image, edge detection
    ]
    
    print(f"Image processing tasks: {len(image_tasks)}")
    for task in image_tasks:
        batch_id, size, filter_type = task
        print(f"  Batch {batch_id}: {size}x{size} image, {filter_type} filter")
    
    start_time = time.time()
    image_results = spar.run(process_image_batch, image_tasks, desc="Processing images")
    image_time = time.time() - start_time
    
    if isinstance(image_results, tuple):
        batch_ids, filter_types, mean_intensities, std_intensities, energies, sizes = image_results
        
        print(f"\nImage Processing Results:")
        print(f"Batch | Size  | Filter    | Mean    | Std     | Energy")
        print("-" * 55)
        
        for i in range(len(batch_ids)):
            print(f"  {batch_ids[i]:2d}  | {sizes[i]:3d}x{sizes[i]:3d} | {filter_types[i]:9s} | {mean_intensities[i]:6.3f}  | {std_intensities[i]:6.3f}  | {energies[i]:8.1f}")
    
    print(f"Image processing time: {image_time:.4f} seconds")

3. Performance Analysis and Optimization
----------------------------------------

Comparing Different Worker Counts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s analyze how performance scales with the number of workers.

.. code:: ipython3

    # Example 5: Performance analysis with different worker counts
    print("Performance Analysis with Different Worker Counts:")
    print("=" * 50)
    
    def cpu_intensive_task(task_id, n_iterations):
        """CPU-intensive task for performance testing."""
        # Simulate CPU-intensive computation
        result = 0
        for i in range(n_iterations):
            result += np.sin(i) * np.cos(i) * np.exp(-i/1000)
        
        return task_id, result, n_iterations
    
    # Create test tasks
    n_tasks = 20
    iterations_per_task = 50000
    test_tasks = [(i, iterations_per_task) for i in range(n_tasks)]
    
    print(f"Performance test setup:")
    print(f"  Number of tasks: {n_tasks}")
    print(f"  Iterations per task: {iterations_per_task:,}")
    print(f"  Total iterations: {n_tasks * iterations_per_task:,}")
    
    # Test different numbers of workers
    max_workers = min(multiprocessing.cpu_count(), 8)  # Limit to reasonable number
    worker_counts = [1, 2, 4] + ([max_workers] if max_workers > 4 else [])
    worker_counts = list(set(worker_counts))  # Remove duplicates
    worker_counts.sort()
    
    print(f"\nTesting with worker counts: {worker_counts}")
    
    performance_results = []
    
    for n_workers in worker_counts:
        print(f"\nTesting with {n_workers} workers:")
        
        start_time = time.time()
        results = spar.run(cpu_intensive_task, test_tasks, n_jobs=n_workers, desc=f"Workers: {n_workers}")
        execution_time = time.time() - start_time
        
        performance_results.append((n_workers, execution_time))
        
        print(f"  Execution time: {execution_time:.4f} seconds")
        if len(performance_results) > 1:
            baseline_time = performance_results[0][1]
            speedup = baseline_time / execution_time
            efficiency = speedup / n_workers * 100
            print(f"  Speedup vs 1 worker: {speedup:.2f}x")
            print(f"  Parallel efficiency: {efficiency:.1f}%")
    
    # Analyze and visualize performance results
    print(f"\nPerformance Summary:")
    print(f"Workers | Time (s) | Speedup | Efficiency")
    print("-" * 40)
    
    worker_nums = []
    times = []
    speedups = []
    efficiencies = []
    
    baseline_time = performance_results[0][1]
    
    for n_workers, exec_time in performance_results:
        speedup = baseline_time / exec_time
        efficiency = (speedup / n_workers) * 100
        
        worker_nums.append(n_workers)
        times.append(exec_time)
        speedups.append(speedup)
        efficiencies.append(efficiency)
        
        print(f"   {n_workers:2d}   | {exec_time:7.4f}  |  {speedup:5.2f}  |   {efficiency:5.1f}%")
    
    # Plot performance results
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Execution time
    axes[0].plot(worker_nums, times, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Number of Workers')
    axes[0].set_ylabel('Execution Time (seconds)')
    axes[0].set_title('Execution Time vs Workers')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xticks(worker_nums)
    
    # Speedup
    axes[1].plot(worker_nums, speedups, 'ro-', linewidth=2, markersize=8, label='Actual')
    axes[1].plot(worker_nums, worker_nums, 'k--', alpha=0.5, label='Ideal (linear)')
    axes[1].set_xlabel('Number of Workers')
    axes[1].set_ylabel('Speedup')
    axes[1].set_title('Speedup vs Workers')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xticks(worker_nums)
    
    # Efficiency
    axes[2].plot(worker_nums, efficiencies, 'go-', linewidth=2, markersize=8)
    axes[2].axhline(y=100, color='k', linestyle='--', alpha=0.5, label='Ideal (100%)')
    axes[2].set_xlabel('Number of Workers')
    axes[2].set_ylabel('Parallel Efficiency (%)')
    axes[2].set_title('Parallel Efficiency vs Workers')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xticks(worker_nums)
    axes[2].set_ylim(0, 110)
    
    plt.tight_layout()
    plt.show()
    
    # Find optimal number of workers
    optimal_idx = np.argmin(times)
    optimal_workers = worker_nums[optimal_idx]
    optimal_time = times[optimal_idx]
    
    print(f"\nOptimal configuration:")
    print(f"  Workers: {optimal_workers}")
    print(f"  Time: {optimal_time:.4f} seconds")
    print(f"  Speedup: {speedups[optimal_idx]:.2f}x")
    print(f"  Efficiency: {efficiencies[optimal_idx]:.1f}%")

Task Granularity Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s analyze how task size affects parallel performance.

.. code:: ipython3

    # Example 6: Task granularity analysis
    print("Task Granularity Analysis:")
    print("=" * 30)
    
    def variable_task(task_id, work_amount):
        """Task with variable amount of work."""
        # Simulate different amounts of computational work
        start_time = time.time()
        
        result = 0
        for i in range(work_amount):
            result += np.sin(i * 0.001) + np.cos(i * 0.001)
        
        execution_time = time.time() - start_time
        return task_id, result, execution_time, work_amount
    
    # Test different task granularities
    granularity_tests = {
        'Very Fine': (100, 1000),    # 100 tasks, 1k iterations each
        'Fine': (50, 2000),          # 50 tasks, 2k iterations each
        'Medium': (20, 5000),        # 20 tasks, 5k iterations each
        'Coarse': (10, 10000),       # 10 tasks, 10k iterations each
        'Very Coarse': (5, 20000),   # 5 tasks, 20k iterations each
    }
    
    print(f"Testing different task granularities:")
    for name, (n_tasks, work_per_task) in granularity_tests.items():
        total_work = n_tasks * work_per_task
        print(f"  {name:12s}: {n_tasks:3d} tasks × {work_per_task:5d} = {total_work:6d} total work")
    
    granularity_results = {}
    n_workers = min(4, multiprocessing.cpu_count())  # Use reasonable number of workers
    
    print(f"\nUsing {n_workers} workers for all tests:")
    
    for granularity_name, (n_tasks, work_per_task) in granularity_tests.items():
        # Create tasks
        tasks = [(i, work_per_task) for i in range(n_tasks)]
        
        # Run parallel execution
        start_time = time.time()
        results = spar.run(variable_task, tasks, n_jobs=n_workers, desc=f"{granularity_name} tasks")
        total_time = time.time() - start_time
        
        # Analyze results
        if isinstance(results, tuple):
            task_ids, task_results, task_times, work_amounts = results
            
            avg_task_time = np.mean(task_times)
            total_task_time = np.sum(task_times)
            overhead = total_time - avg_task_time  # Approximation
            
            granularity_results[granularity_name] = {
                'n_tasks': n_tasks,
                'work_per_task': work_per_task,
                'total_time': total_time,
                'avg_task_time': avg_task_time,
                'total_task_time': total_task_time,
                'overhead': overhead
            }
            
            print(f"  {granularity_name:12s}: {total_time:.4f}s total, {avg_task_time:.6f}s avg/task")
    
    # Analyze and visualize granularity results
    print(f"\nGranularity Analysis Results:")
    print(f"Granularity  | Tasks | Work/Task | Total Time | Avg Task Time | Efficiency")
    print("-" * 75)
    
    granularity_names = []
    total_times = []
    n_tasks_list = []
    avg_task_times = []
    
    for name, results in granularity_results.items():
        # Calculate efficiency as ratio of actual computation time to total time
        efficiency = (results['avg_task_time'] / results['total_time']) * 100
        
        granularity_names.append(name)
        total_times.append(results['total_time'])
        n_tasks_list.append(results['n_tasks'])
        avg_task_times.append(results['avg_task_time'])
        
        print(f"{name:12s} | {results['n_tasks']:5d} | {results['work_per_task']:9d} | {results['total_time']:9.4f}s | {results['avg_task_time']:11.6f}s | {efficiency:7.1f}%")
    
    # Plot granularity analysis
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Total execution time vs number of tasks
    axes[0].plot(n_tasks_list, total_times, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Number of Tasks')
    axes[0].set_ylabel('Total Execution Time (seconds)')
    axes[0].set_title('Total Time vs Task Count')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xscale('log')
    
    # Average task time vs number of tasks
    axes[1].plot(n_tasks_list, avg_task_times, 'ro-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Number of Tasks')
    axes[1].set_ylabel('Average Task Time (seconds)')
    axes[1].set_title('Avg Task Time vs Task Count')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xscale('log')
    axes[1].set_yscale('log')
    
    # Throughput (tasks per second)
    throughputs = [n_tasks / total_time for n_tasks, total_time in zip(n_tasks_list, total_times)]
    axes[2].plot(n_tasks_list, throughputs, 'go-', linewidth=2, markersize=8)
    axes[2].set_xlabel('Number of Tasks')
    axes[2].set_ylabel('Throughput (tasks/second)')
    axes[2].set_title('Throughput vs Task Count')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xscale('log')
    
    plt.tight_layout()
    plt.show()
    
    # Find optimal granularity
    optimal_idx = np.argmin(total_times)
    optimal_granularity = granularity_names[optimal_idx]
    optimal_n_tasks = n_tasks_list[optimal_idx]
    optimal_time = total_times[optimal_idx]
    
    print(f"\nOptimal task granularity: {optimal_granularity}")
    print(f"  Number of tasks: {optimal_n_tasks}")
    print(f"  Total time: {optimal_time:.4f} seconds")
    print(f"  Throughput: {optimal_n_tasks/optimal_time:.1f} tasks/second")

4. Error Handling and Edge Cases
--------------------------------

Testing Error Conditions
~~~~~~~~~~~~~~~~~~~~~~~~

Let’s test how the parallel module handles various error conditions.

.. code:: ipython3

    # Example 7: Error handling and edge cases
    print("Error Handling and Edge Cases:")
    print("=" * 35)
    
    def failing_function(task_id, should_fail):
        """Function that may fail based on parameters."""
        if should_fail and task_id % 3 == 0:  # Fail every 3rd task
            raise ValueError(f"Intentional failure for task {task_id}")
        
        # Simulate some work
        result = task_id ** 2
        return task_id, result
    
    def empty_function():
        """Function with no arguments."""
        return "no args"
    
    # Test Case 1: Empty argument list
    print("1. Testing empty argument list:")
    try:
        result = spar.run(lambda x: x * 2, [], desc="Empty test")
        print(f"  Unexpected success: {result}")
    except ValueError as e:
        print(f"  ✓ Expected error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {type(e).__name__}: {e}")
    
    # Test Case 2: Non-callable function
    print("\n2. Testing non-callable function:")
    try:
        result = spar.run("not a function", [(1,), (2,)], desc="Non-callable test")
        print(f"  Unexpected success: {result}")
    except ValueError as e:
        print(f"  ✓ Expected error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {type(e).__name__}: {e}")
    
    # Test Case 3: Invalid number of jobs
    print("\n3. Testing invalid number of jobs:")
    test_args = [(1,), (2,), (3,)]
    
    # Test n_jobs = 0
    try:
        result = spar.run(lambda x: x * 2, test_args, n_jobs=0, desc="Zero jobs test")
        print(f"  n_jobs=0: Unexpected success: {result}")
    except ValueError as e:
        print(f"  n_jobs=0: ✓ Expected error: {e}")
    except Exception as e:
        print(f"  n_jobs=0: ✗ Unexpected error: {type(e).__name__}: {e}")
    
    # Test very high n_jobs (should warn but work)
    try:
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = spar.run(lambda x: x * 2, test_args, n_jobs=100, desc="High jobs test")
            if w:
                print(f"  n_jobs=100: ✓ Warning issued: {w[0].message}")
            else:
                print(f"  n_jobs=100: No warning (might be expected on some systems)")
            print(f"  n_jobs=100: Results: {result}")
    except Exception as e:
        print(f"  n_jobs=100: ✗ Error: {type(e).__name__}: {e}")
    
    # Test Case 4: Function with inconsistent return types
    print("\n4. Testing function with inconsistent return types:")
    def inconsistent_function(x):
        if x % 2 == 0:
            return x  # Single value
        else:
            return (x, x*2)  # Tuple
    
    inconsistent_args = [(i,) for i in range(1, 6)]
    try:
        result = spar.run(inconsistent_function, inconsistent_args, desc="Inconsistent test")
        print(f"  ✓ Results: {result}")
        print(f"  Note: First result type determines tuple unpacking behavior")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    # Test Case 5: Very small tasks (overhead analysis)
    print("\n5. Testing very small tasks (overhead analysis):")
    def tiny_task(x):
        return x + 1
    
    tiny_args = [(i,) for i in range(1000)]  # 1000 tiny tasks
    
    # Sequential execution
    start_time = time.time()
    sequential_result = [tiny_task(i) for i in range(1000)]
    sequential_time = time.time() - start_time
    
    # Parallel execution
    start_time = time.time()
    parallel_result = spar.run(tiny_task, tiny_args, desc="Tiny tasks")
    parallel_time = time.time() - start_time
    
    print(f"  Sequential time: {sequential_time:.6f} seconds")
    print(f"  Parallel time:   {parallel_time:.6f} seconds")
    print(f"  Overhead factor: {parallel_time / sequential_time:.2f}x")
    print(f"  Results match: {sequential_result == parallel_result}")
    
    if parallel_time > sequential_time:
        print(f"  ⚠ Parallel execution slower due to overhead (expected for tiny tasks)")
    else:
        print(f"  ✓ Parallel execution faster despite overhead")
    
    # Test Case 6: Memory-intensive tasks
    print("\n6. Testing memory-intensive tasks:")
    def memory_task(size_mb):
        """Create and process a large array."""
        # Create array of specified size in MB
        n_elements = int(size_mb * 1024 * 1024 / 8)  # 8 bytes per float64
        large_array = np.random.randn(n_elements)
        
        # Perform some computation
        result = np.sum(large_array**2)
        
        # Clean up
        del large_array
        
        return size_mb, result
    
    # Use smaller arrays to avoid memory issues
    memory_args = [(1,), (2,), (3,), (4,)]  # 1-4 MB arrays
    
    try:
        start_time = time.time()
        memory_results = spar.run(memory_task, memory_args, desc="Memory-intensive tasks")
        memory_time = time.time() - start_time
        
        if isinstance(memory_results, tuple):
            sizes, results = memory_results
            print(f"  ✓ Memory tasks completed successfully")
            print(f"  Array sizes: {sizes} MB")
            print(f"  Results: {[f'{r:.2e}' for r in results]}")
            print(f"  Execution time: {memory_time:.4f} seconds")
        else:
            print(f"  ✓ Results: {memory_results}")
            
    except Exception as e:
        print(f"  ✗ Error with memory-intensive tasks: {type(e).__name__}: {e}")
    
    print(f"\nError handling and edge case testing complete.")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.parallel`` module:

Core Functionality
~~~~~~~~~~~~~~~~~~

-  **``run``**: Execute functions in parallel using ThreadPoolExecutor

   -  Support for functions with multiple arguments via tuple unpacking
   -  Automatic CPU core detection and utilization
   -  Progress tracking with tqdm integration
   -  Intelligent handling of multiple return values

Key Features
~~~~~~~~~~~~

1. **Ease of Use**: Simple interface requiring only function and
   argument list
2. **Flexibility**: Support for various function signatures and return
   types
3. **Robustness**: Comprehensive error handling and validation
4. **Performance**: Optimized for scientific computing workloads
5. **Monitoring**: Built-in progress tracking for long-running tasks

Demonstrated Applications
~~~~~~~~~~~~~~~~~~~~~~~~~

Basic Mathematical Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Simple arithmetic functions
-  Functions with multiple arguments
-  Functions returning multiple values (tuples)

Scientific Computing
^^^^^^^^^^^^^^^^^^^^

-  **Monte Carlo Methods**: Parallel π estimation with different sample
   sizes
-  **Numerical Integration**: Parallel integration of various
   mathematical functions
-  **Data Analysis**: Parallel processing of multiple datasets
-  **Image Processing**: Batch processing with different filters

Performance Analysis
^^^^^^^^^^^^^^^^^^^^

-  **Scalability Testing**: Performance vs number of workers
-  **Granularity Analysis**: Optimal task size determination
-  **Overhead Measurement**: Understanding parallel processing costs

Performance Insights
~~~~~~~~~~~~~~~~~~~~

1. **Worker Scaling**: Performance typically improves with more workers
   up to CPU count
2. **Task Granularity**: Medium-sized tasks often provide optimal
   performance
3. **Overhead Considerations**: Very small tasks may run slower in
   parallel
4. **Memory Constraints**: Large memory tasks may limit effective
   parallelism

Best Practices Illustrated
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Task Design**: Create tasks with sufficient computational work
-  **Worker Selection**: Use automatic CPU detection or tune based on
   workload
-  **Error Handling**: Implement robust error handling in task functions
-  **Memory Management**: Consider memory usage in parallel contexts
-  **Progress Monitoring**: Use descriptive progress messages for user
   feedback

Common Use Cases
~~~~~~~~~~~~~~~~

-  **Parameter Sweeps**: Running experiments with different parameter
   combinations
-  **Data Processing**: Parallel analysis of multiple datasets or files
-  **Simulation Studies**: Monte Carlo simulations and statistical
   sampling
-  **Image/Signal Processing**: Batch processing of multimedia data
-  **Model Training**: Parallel training of multiple model
   configurations
-  **Scientific Computing**: Numerical integration, optimization, and
   analysis

Integration Benefits
~~~~~~~~~~~~~~~~~~~~

-  **Scientific Workflows**: Seamless integration with NumPy, SciPy, and
   pandas
-  **Research Reproducibility**: Consistent parallel execution across
   platforms
-  **Development Efficiency**: Simple API reduces parallel programming
   complexity
-  **Performance Optimization**: Built-in tools for performance analysis
   and tuning

The ``scitex.parallel`` module provides essential parallel processing
capabilities for scientific computing, with emphasis on simplicity,
robustness, and performance optimization for research applications.
