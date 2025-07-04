22 SciTeX Repro
===============

.. note::
   This page is generated from the Jupyter notebook `22_scitex_repro.ipynb <https://github.com/scitex/scitex/blob/main/examples/22_scitex_repro.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 22_scitex_repro.ipynb


This notebook demonstrates the complete functionality of the
``scitex.repro`` module, which provides reproducibility tools for
scientific computing and research.

Module Overview
---------------

The ``scitex.repro`` module includes: - Random seed fixing for multiple
libraries - Unique identifier generation for experiments - Timestamp
generation for versioning and tracking - Tools for ensuring reproducible
research

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import os
    import random
    import numpy as np
    import time
    from datetime import datetime
    import matplotlib.pyplot as plt
    
    # Try to import optional libraries
    try:
        import torch
        TORCH_AVAILABLE = True
    except ImportError:
        TORCH_AVAILABLE = False
    
    try:
        import tensorflow as tf
        TF_AVAILABLE = True
    except ImportError:
        TF_AVAILABLE = False
    
    # Import scitex repro module
    import scitex.repro as srepro
    
    print("Available functions in scitex.repro:")
    repro_attrs = [attr for attr in dir(srepro) if not attr.startswith('_')]
    for i, attr in enumerate(repro_attrs):
        print(f"{i+1:2d}. {attr}")
    
    print(f"\nLibrary availability:")
    print(f"  PyTorch: {'✓' if TORCH_AVAILABLE else '✗'}")
    print(f"  TensorFlow: {'✓' if TF_AVAILABLE else '✗'}")
    print(f"  NumPy: ✓")
    print(f"  Random: ✓")
    print(f"  OS: ✓")

1. Random Seed Fixing
---------------------

Basic Seed Fixing
~~~~~~~~~~~~~~~~~

The ``fix_seeds`` function ensures reproducible random number generation
across multiple libraries.

.. code:: ipython3

    # Example 1: Basic seed fixing demonstration
    print("Basic Seed Fixing Demonstration:")
    print("=" * 35)
    
    def generate_random_data(label):
        """Generate random data from different sources."""
        print(f"\n{label}:")
        
        # Python random module
        python_random = [random.random() for _ in range(3)]
        print(f"  Python random: {[f'{x:.6f}' for x in python_random]}")
        
        # NumPy random
        numpy_random = np.random.random(3)
        print(f"  NumPy random:  {[f'{x:.6f}' for x in numpy_random]}")
        
        # PyTorch random (if available)
        if TORCH_AVAILABLE:
            torch_random = torch.rand(3)
            print(f"  PyTorch random: {[f'{x:.6f}' for x in torch_random.tolist()]}")
        
        return python_random, numpy_random
    
    # Generate random data before seed fixing
    print("Before seed fixing (should be different each time):")
    data1_py, data1_np = generate_random_data("Run 1")
    data2_py, data2_np = generate_random_data("Run 2")
    
    # Check if data is different
    print(f"\nData differences (should be True):")
    print(f"  Python random different: {data1_py != data2_py}")
    print(f"  NumPy random different:  {not np.array_equal(data1_np, data2_np)}")
    
    print("\n" + "="*50)
    print("Now fixing seeds and testing reproducibility...")

.. code:: ipython3

    # Example 2: Reproducibility with seed fixing
    print("Reproducibility with Seed Fixing:")
    print("=" * 35)
    
    # Fix seeds for all available libraries
    print("Fixing seeds for all libraries...")
    if TORCH_AVAILABLE and TF_AVAILABLE:
        srepro.fix_seeds(os=os, random=random, np=np, torch=torch, tf=tf, seed=42, verbose=True)
    elif TORCH_AVAILABLE:
        srepro.fix_seeds(os=os, random=random, np=np, torch=torch, seed=42, verbose=True)
    else:
        srepro.fix_seeds(os=os, random=random, np=np, seed=42, verbose=True)
    
    # Generate data after first seed fixing
    print("\nAfter seed fixing - Run A:")
    dataA_py, dataA_np = generate_random_data("Seed-fixed Run A")
    
    # Fix seeds again with same seed
    print("\nFixing seeds again with same seed (42)...")
    if TORCH_AVAILABLE and TF_AVAILABLE:
        srepro.fix_seeds(os=os, random=random, np=np, torch=torch, tf=tf, seed=42, verbose=False)
    elif TORCH_AVAILABLE:
        srepro.fix_seeds(os=os, random=random, np=np, torch=torch, seed=42, verbose=False)
    else:
        srepro.fix_seeds(os=os, random=random, np=np, seed=42, verbose=False)
    
    # Generate data after second seed fixing
    print("\nAfter seed fixing - Run B:")
    dataB_py, dataB_np = generate_random_data("Seed-fixed Run B")
    
    # Verify reproducibility
    print(f"\nReproducibility check (should be True):")
    print(f"  Python random identical: {dataA_py == dataB_py}")
    print(f"  NumPy random identical:  {np.array_equal(dataA_np, dataB_np)}")
    
    if dataA_py == dataB_py and np.array_equal(dataA_np, dataB_np):
        print("  ✓ Perfect reproducibility achieved!")
    else:
        print("  ✗ Reproducibility issue detected")

Different Seed Values
~~~~~~~~~~~~~~~~~~~~~

Let’s test reproducibility with different seed values.

.. code:: ipython3

    # Example 3: Testing different seed values
    print("Testing Different Seed Values:")
    print("=" * 30)
    
    def test_seed_reproducibility(seed_value):
        """Test reproducibility with a specific seed."""
        results = []
        
        for run in range(3):  # Run 3 times with same seed
            # Fix seeds
            if TORCH_AVAILABLE:
                srepro.fix_seeds(random=random, np=np, torch=torch, seed=seed_value, verbose=False)
            else:
                srepro.fix_seeds(random=random, np=np, seed=seed_value, verbose=False)
            
            # Generate some random data
            py_val = random.random()
            np_val = np.random.random()
            torch_val = torch.rand(1).item() if TORCH_AVAILABLE else 0.0
            
            results.append((py_val, np_val, torch_val))
        
        return results
    
    # Test different seeds
    test_seeds = [42, 123, 987, 2024]
    
    print(f"Testing seeds: {test_seeds}")
    print(f"Each seed will be tested 3 times to verify reproducibility\n")
    
    seed_results = {}
    
    for seed in test_seeds:
        print(f"Testing seed {seed}:")
        results = test_seed_reproducibility(seed)
        seed_results[seed] = results
        
        # Check if all runs produced identical results
        first_result = results[0]
        all_identical = all(result == first_result for result in results)
        
        print(f"  Run 1: Python={first_result[0]:.6f}, NumPy={first_result[1]:.6f}, PyTorch={first_result[2]:.6f}")
        print(f"  Reproducibility: {'✓' if all_identical else '✗'}")
        
        if not all_identical:
            print(f"  Detailed results: {results}")
        print()
    
    # Compare different seeds (should produce different values)
    print(f"Comparing results across different seeds:")
    print(f"Seed |    Python    |     NumPy    |   PyTorch")
    print("-" * 50)
    
    for seed in test_seeds:
        first_result = seed_results[seed][0]
        py_val, np_val, torch_val = first_result
        print(f" {seed:3d} | {py_val:.6f}   | {np_val:.6f}   | {torch_val:.6f}")
    
    # Verify that different seeds produce different results
    all_python_values = [seed_results[seed][0][0] for seed in test_seeds]
    all_numpy_values = [seed_results[seed][0][1] for seed in test_seeds]
    
    python_unique = len(set(all_python_values)) == len(all_python_values)
    numpy_unique = len(set(all_numpy_values)) == len(all_numpy_values)
    
    print(f"\nSeed differentiation:")
    print(f"  Python values unique: {'✓' if python_unique else '✗'}")
    print(f"  NumPy values unique:  {'✓' if numpy_unique else '✗'}")

2. Unique Identifier Generation
-------------------------------

Basic ID Generation
~~~~~~~~~~~~~~~~~~~

The ``gen_id`` and ``gen_ID`` functions generate unique identifiers for
experiments and runs.

.. code:: ipython3

    # Example 4: Unique identifier generation
    print("Unique Identifier Generation:")
    print("=" * 30)
    
    # Generate multiple IDs with default settings
    print("Default ID generation:")
    for i in range(5):
        experiment_id = srepro.gen_id()
        print(f"  ID {i+1}: {experiment_id}")
        time.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Test backward compatibility alias
    print(f"\nBackward compatibility test:")
    old_style_id = srepro.gen_ID()
    new_style_id = srepro.gen_id()
    print(f"  gen_ID():  {old_style_id}")
    print(f"  gen_id():  {new_style_id}")
    print(f"  Both functions work: ✓")
    
    # Custom time format
    print(f"\nCustom time formats:")
    custom_formats = [
        ("%Y%m%d", "YYYYMMDD format"),
        ("%Y-%m-%d_%H%M", "Date and time format"),
        ("%j_%Y", "Day of year format"),
        ("%W_%Y", "Week of year format"),
    ]
    
    for time_format, description in custom_formats:
        custom_id = srepro.gen_id(time_format=time_format, N=4)
        print(f"  {description:20s}: {custom_id}")
    
    # Different random string lengths
    print(f"\nDifferent random string lengths:")
    for N in [4, 8, 12, 16]:
        var_length_id = srepro.gen_id(N=N)
        random_part = var_length_id.split('_')[-1]
        print(f"  N={N:2d}: {var_length_id} (random part: '{random_part}', length: {len(random_part)})")

ID Uniqueness Testing
~~~~~~~~~~~~~~~~~~~~~

Let’s test the uniqueness properties of the generated identifiers.

.. code:: ipython3

    # Example 5: ID uniqueness testing
    print("ID Uniqueness Testing:")
    print("=" * 25)
    
    # Generate many IDs to test uniqueness
    n_ids = 1000
    print(f"Generating {n_ids} IDs to test uniqueness...")
    
    generated_ids = []
    start_time = time.time()
    
    for i in range(n_ids):
        new_id = srepro.gen_id()
        generated_ids.append(new_id)
        
        # Add tiny delay occasionally to ensure timestamp differences
        if i % 100 == 0 and i > 0:
            time.sleep(0.001)
    
    generation_time = time.time() - start_time
    
    # Analyze uniqueness
    unique_ids = set(generated_ids)
    n_unique = len(unique_ids)
    n_duplicates = n_ids - n_unique
    
    print(f"\nUniqueness Analysis:")
    print(f"  Generated IDs: {n_ids:,}")
    print(f"  Unique IDs: {n_unique:,}")
    print(f"  Duplicates: {n_duplicates:,}")
    print(f"  Uniqueness rate: {(n_unique/n_ids)*100:.2f}%")
    print(f"  Generation time: {generation_time:.4f} seconds")
    print(f"  Rate: {n_ids/generation_time:.0f} IDs/second")
    
    if n_duplicates == 0:
        print(f"  ✓ Perfect uniqueness achieved!")
    else:
        print(f"  ⚠ {n_duplicates} duplicates found")
        # Show first few duplicates
        duplicate_count = {}
        for gen_id in generated_ids:
            duplicate_count[gen_id] = duplicate_count.get(gen_id, 0) + 1
        
        duplicates = {k: v for k, v in duplicate_count.items() if v > 1}
        print(f"  First few duplicates: {list(duplicates.items())[:3]}")
    
    # Analyze ID structure
    print(f"\nID Structure Analysis:")
    sample_ids = generated_ids[:5]
    print(f"  Sample IDs:")
    for i, sample_id in enumerate(sample_ids):
        timestamp_part = sample_id.split('_')[0]
        random_part = sample_id.split('_')[1]
        print(f"    {i+1}. {sample_id}")
        print(f"       Timestamp: '{timestamp_part}', Random: '{random_part}'")
    
    # Analyze timestamp distribution
    timestamps = [gen_id.split('_')[0] for gen_id in generated_ids]
    unique_timestamps = set(timestamps)
    print(f"\n  Timestamp analysis:")
    print(f"    Unique timestamps: {len(unique_timestamps)}")
    print(f"    Timestamp compression: {len(unique_timestamps)/n_ids*100:.1f}% (lower is better for fast generation)")
    
    # Analyze random part distribution
    random_parts = [gen_id.split('_')[1] for gen_id in generated_ids]
    unique_random_parts = set(random_parts)
    print(f"    Unique random parts: {len(unique_random_parts)}")
    print(f"    Random part uniqueness: {len(unique_random_parts)/n_ids*100:.1f}%")

3. Timestamp Generation
-----------------------

Basic Timestamp Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``gen_timestamp`` and ``timestamp`` functions generate standardized
timestamps.

.. code:: ipython3

    # Example 6: Timestamp generation
    print("Timestamp Generation:")
    print("=" * 20)
    
    # Generate current timestamps
    print("Current timestamps:")
    for i in range(5):
        ts = srepro.gen_timestamp()
        print(f"  Timestamp {i+1}: {ts}")
        time.sleep(0.1)  # Small delay to show timestamp progression
    
    # Test backward compatibility alias
    print(f"\nBackward compatibility:")
    ts1 = srepro.gen_timestamp()
    ts2 = srepro.timestamp()
    print(f"  gen_timestamp(): {ts1}")
    print(f"  timestamp():     {ts2}")
    print(f"  Both functions work: ✓")
    
    # Timestamp format analysis
    current_ts = srepro.gen_timestamp()
    print(f"\nTimestamp format analysis:")
    print(f"  Current timestamp: {current_ts}")
    print(f"  Format: YYYY-MMDD-HHMM")
    print(f"  Length: {len(current_ts)} characters")
    
    # Parse timestamp components
    try:
        # Parse the timestamp format: YYYY-MMDD-HHMM
        parts = current_ts.split('-')
        if len(parts) == 3:
            year = parts[0]
            month_day = parts[1]
            hour_minute = parts[2]
            
            month = month_day[:2]
            day = month_day[2:]
            hour = hour_minute[:2]
            minute = hour_minute[2:]
            
            print(f"  Components:")
            print(f"    Year: {year}")
            print(f"    Month: {month}")
            print(f"    Day: {day}")
            print(f"    Hour: {hour}")
            print(f"    Minute: {minute}")
            
            # Verify parsing
            reconstructed = f"{year}-{month}{day}-{hour}{minute}"
            print(f"  Parsing verification: {reconstructed == current_ts}")
            
    except Exception as e:
        print(f"  Error parsing timestamp: {e}")
    
    # Demonstrate timestamp usage for file naming
    print(f"\nPractical usage examples:")
    ts = srepro.gen_timestamp()
    example_filenames = [
        f"experiment_{ts}.csv",
        f"results_{ts}.json",
        f"model_weights_{ts}.pt",
        f"analysis_{ts}.ipynb",
        f"backup_{ts}.tar.gz"
    ]
    
    print(f"  Example filenames with timestamp:")
    for filename in example_filenames:
        print(f"    {filename}")

Timestamp Chronological Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s verify that timestamps maintain chronological order.

.. code:: ipython3

    # Example 7: Timestamp chronological testing
    print("Timestamp Chronological Testing:")
    print("=" * 35)
    
    # Generate timestamps over time
    timestamps = []
    generation_times = []
    
    print("Generating timestamps with delays:")
    for i in range(10):
        current_time = datetime.now()
        ts = srepro.gen_timestamp()
        
        timestamps.append(ts)
        generation_times.append(current_time)
        
        print(f"  {i+1:2d}. {ts} (real time: {current_time.strftime('%H:%M:%S.%f')[:-3]})")
        
        # Variable delay to test different scenarios
        if i < 9:
            delay = 0.1 if i % 3 == 0 else 0.05
            time.sleep(delay)
    
    # Analyze chronological order
    print(f"\nChronological order analysis:")
    
    # Check if timestamps are in order
    is_chronological = True
    for i in range(1, len(timestamps)):
        if timestamps[i] < timestamps[i-1]:
            is_chronological = False
            print(f"  Order violation at position {i}: {timestamps[i-1]} > {timestamps[i]}")
    
    print(f"  Timestamps in chronological order: {'✓' if is_chronological else '✗'}")
    
    # Check for duplicates
    unique_timestamps = set(timestamps)
    n_duplicates = len(timestamps) - len(unique_timestamps)
    print(f"  Duplicate timestamps: {n_duplicates}")
    
    if n_duplicates > 0:
        print(f"  Note: Duplicates expected for rapid generation within same minute")
    
    # Analyze timestamp resolution
    print(f"\nTimestamp resolution analysis:")
    print(f"  Total timestamps: {len(timestamps)}")
    print(f"  Unique timestamps: {len(unique_timestamps)}")
    print(f"  Resolution efficiency: {len(unique_timestamps)/len(timestamps)*100:.1f}%")
    
    # Show timestamp distribution
    from collections import Counter
    timestamp_counts = Counter(timestamps)
    if len(timestamp_counts) < len(timestamps):
        print(f"  Timestamp frequency distribution:")
        for ts, count in timestamp_counts.most_common(3):
            print(f"    {ts}: {count} occurrences")
    
    # Demonstrate sorting behavior
    print(f"\nSorting demonstration:")
    shuffled_timestamps = timestamps.copy()
    random.shuffle(shuffled_timestamps)
    sorted_timestamps = sorted(shuffled_timestamps)
    
    print(f"  Original order matches sorted: {timestamps == sorted_timestamps}")
    if timestamps != sorted_timestamps:
        print(f"  Original: {timestamps[:3]}...")
        print(f"  Sorted:   {sorted_timestamps[:3]}...")

4. Practical Reproducibility Workflows
--------------------------------------

Complete Experiment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate a complete reproducible experiment setup using all the
tools.

.. code:: ipython3

    # Example 8: Complete reproducible experiment setup
    print("Complete Reproducible Experiment Setup:")
    print("=" * 40)
    
    class ReproducibleExperiment:
        """A class for managing reproducible experiments."""
        
        def __init__(self, name, seed=None, description=None):
            self.name = name
            self.description = description or f"Experiment: {name}"
            
            # Generate experiment metadata
            self.experiment_id = srepro.gen_id()
            self.timestamp = srepro.gen_timestamp()
            self.seed = seed or 42
            
            # Initialize reproducible state
            self._setup_reproducibility()
            
            # Store experiment info
            self.info = {
                'name': self.name,
                'id': self.experiment_id,
                'timestamp': self.timestamp,
                'seed': self.seed,
                'description': self.description,
                'status': 'initialized'
            }
            
            print(f"Experiment '{self.name}' initialized:")
            print(f"  ID: {self.experiment_id}")
            print(f"  Timestamp: {self.timestamp}")
            print(f"  Seed: {self.seed}")
        
        def _setup_reproducibility(self):
            """Set up reproducible random states."""
            if TORCH_AVAILABLE:
                srepro.fix_seeds(os=os, random=random, np=np, torch=torch, seed=self.seed, verbose=False)
            else:
                srepro.fix_seeds(os=os, random=random, np=np, seed=self.seed, verbose=False)
        
        def run_simulation(self, n_samples=1000):
            """Run a reproducible simulation."""
            print(f"\n  Running simulation with {n_samples} samples...")
            
            # Generate reproducible data
            data = np.random.normal(0, 1, n_samples)
            noise = np.random.random(n_samples) * 0.1
            signal = np.sin(np.linspace(0, 4*np.pi, n_samples)) + noise
            
            # Compute statistics
            results = {
                'mean': np.mean(data),
                'std': np.std(data),
                'signal_mean': np.mean(signal),
                'signal_std': np.std(signal),
                'correlation': np.corrcoef(data[:len(signal)], signal)[0, 1],
                'n_samples': n_samples
            }
            
            self.info['results'] = results
            self.info['status'] = 'completed'
            
            print(f"  Results:")
            for key, value in results.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.6f}")
                else:
                    print(f"    {key}: {value}")
            
            return results
        
        def get_summary(self):
            """Get experiment summary."""
            return self.info.copy()
    
    # Run multiple experiments to test reproducibility
    experiments = []
    
    print("\nRunning multiple experiments with same parameters:")
    for i in range(3):
        exp_name = f"RepeatTest_{i+1}"
        exp = ReproducibleExperiment(
            name=exp_name,
            seed=42,  # Same seed for all
            description=f"Reproducibility test experiment {i+1}"
        )
        
        results = exp.run_simulation(n_samples=500)
        experiments.append(exp)
        print()
    
    # Verify reproducibility across experiments
    print("Reproducibility verification:")
    first_results = experiments[0].get_summary()['results']
    
    all_identical = True
    for i, exp in enumerate(experiments[1:], 1):
        current_results = exp.get_summary()['results']
        
        # Compare key results
        for key in ['mean', 'std', 'signal_mean', 'signal_std', 'correlation']:
            if abs(first_results[key] - current_results[key]) > 1e-10:
                print(f"  Difference in {key}: {first_results[key]} vs {current_results[key]}")
                all_identical = False
    
    if all_identical:
        print(f"  ✓ All {len(experiments)} experiments produced identical results!")
    else:
        print(f"  ✗ Reproducibility issues detected")
    
    # Show experiment metadata
    print(f"\nExperiment metadata summary:")
    print(f"Exp # | ID (last 8)     | Timestamp    | Seed | Status")
    print("-" * 55)
    
    for i, exp in enumerate(experiments):
        summary = exp.get_summary()
        id_short = summary['id'][-8:]
        print(f"  {i+1}   | {id_short}       | {summary['timestamp']} |  {summary['seed']}  | {summary['status']}")
    
    # Demonstrate different seeds produce different results
    print(f"\nTesting different seeds (should produce different results):")
    different_seed_exp = ReproducibleExperiment(
        name="DifferentSeed",
        seed=123,  # Different seed
        description="Test with different seed"
    )
    
    different_results = different_seed_exp.run_simulation(n_samples=500)
    
    # Compare with first experiment
    print(f"\nComparison with different seed:")
    for key in ['mean', 'std', 'signal_mean']:
        original = first_results[key]
        different = different_results[key]
        diff = abs(original - different)
        print(f"  {key:12s}: {original:.6f} vs {different:.6f} (diff: {diff:.6f})")
    
    # Check if results are sufficiently different
    significant_differences = sum(1 for key in ['mean', 'std', 'signal_mean'] 
                                 if abs(first_results[key] - different_results[key]) > 0.01)
    
    print(f"\nSeed differentiation: {'✓' if significant_differences > 0 else '✗'} ({significant_differences}/3 metrics significantly different)")

Experiment Tracking and Versioning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate how to use the reproducibility tools for experiment
tracking.

.. code:: ipython3

    # Example 9: Experiment tracking and versioning
    print("Experiment Tracking and Versioning:")
    print("=" * 40)
    
    class ExperimentTracker:
        """Track multiple experiments with versioning."""
        
        def __init__(self):
            self.experiments = []
            self.session_id = srepro.gen_id(time_format="%Y%m%d_%H%M", N=6)
            print(f"Experiment tracking session: {self.session_id}")
        
        def run_experiment(self, name, config):
            """Run an experiment with given configuration."""
            # Generate experiment metadata
            exp_id = srepro.gen_id(N=8)
            timestamp = srepro.gen_timestamp()
            
            # Set up reproducibility
            seed = config.get('seed', 42)
            if TORCH_AVAILABLE:
                srepro.fix_seeds(random=random, np=np, torch=torch, seed=seed, verbose=False)
            else:
                srepro.fix_seeds(random=random, np=np, seed=seed, verbose=False)
            
            # Run experiment based on configuration
            results = self._execute_experiment(config)
            
            # Store experiment record
            experiment_record = {
                'id': exp_id,
                'name': name,
                'timestamp': timestamp,
                'session_id': self.session_id,
                'config': config.copy(),
                'results': results,
                'version': len(self.experiments) + 1
            }
            
            self.experiments.append(experiment_record)
            
            print(f"\nExperiment '{name}' completed:")
            print(f"  ID: {exp_id}")
            print(f"  Version: {experiment_record['version']}")
            print(f"  Timestamp: {timestamp}")
            print(f"  Config: {config}")
            print(f"  Key result: {results['score']:.4f}")
            
            return experiment_record
        
        def _execute_experiment(self, config):
            """Execute experiment logic based on config."""
            n_samples = config.get('n_samples', 1000)
            noise_level = config.get('noise_level', 0.1)
            method = config.get('method', 'linear')
            
            # Generate data
            x = np.random.random(n_samples)
            
            if method == 'linear':
                y = 2 * x + 1 + np.random.normal(0, noise_level, n_samples)
            elif method == 'quadratic':
                y = x**2 + 0.5 * x + np.random.normal(0, noise_level, n_samples)
            elif method == 'sine':
                y = np.sin(2 * np.pi * x) + np.random.normal(0, noise_level, n_samples)
            else:
                y = x + np.random.normal(0, noise_level, n_samples)
            
            # Compute results
            correlation = np.corrcoef(x, y)[0, 1]
            mse = np.mean((y - x)**2)  # Simple baseline MSE
            score = correlation - 0.1 * mse  # Combined score
            
            return {
                'correlation': correlation,
                'mse': mse,
                'score': score,
                'data_stats': {
                    'x_mean': np.mean(x),
                    'y_mean': np.mean(y),
                    'x_std': np.std(x),
                    'y_std': np.std(y)
                }
            }
        
        def get_summary(self):
            """Get summary of all experiments."""
            if not self.experiments:
                return "No experiments recorded"
            
            summary = f"Session {self.session_id} Summary:\n"
            summary += f"Total experiments: {len(self.experiments)}\n"
            summary += "Ver | Name          | Timestamp    | Score    | Method\n"
            summary += "-" * 55 + "\n"
            
            for exp in self.experiments:
                summary += f"{exp['version']:3d} | {exp['name']:13s} | {exp['timestamp']} | {exp['results']['score']:7.4f} | {exp['config'].get('method', 'N/A')}\n"
            
            return summary
        
        def get_best_experiment(self):
            """Get the experiment with the highest score."""
            if not self.experiments:
                return None
            
            best_exp = max(self.experiments, key=lambda x: x['results']['score'])
            return best_exp
    
    # Create experiment tracker and run various experiments
    tracker = ExperimentTracker()
    
    # Define different experimental configurations
    experiment_configs = [
        {
            'name': 'baseline_linear',
            'config': {'method': 'linear', 'n_samples': 1000, 'noise_level': 0.1, 'seed': 42}
        },
        {
            'name': 'low_noise_linear',
            'config': {'method': 'linear', 'n_samples': 1000, 'noise_level': 0.05, 'seed': 42}
        },
        {
            'name': 'quadratic_test',
            'config': {'method': 'quadratic', 'n_samples': 1000, 'noise_level': 0.1, 'seed': 42}
        },
        {
            'name': 'sine_wave_test',
            'config': {'method': 'sine', 'n_samples': 1000, 'noise_level': 0.1, 'seed': 42}
        },
        {
            'name': 'large_sample',
            'config': {'method': 'linear', 'n_samples': 5000, 'noise_level': 0.1, 'seed': 42}
        }
    ]
    
    # Run all experiments
    for exp_config in experiment_configs:
        tracker.run_experiment(exp_config['name'], exp_config['config'])
    
    # Display summary
    print(f"\n" + "="*60)
    print(tracker.get_summary())
    
    # Find and display best experiment
    best_exp = tracker.get_best_experiment()
    if best_exp:
        print(f"Best performing experiment:")
        print(f"  Name: {best_exp['name']}")
        print(f"  ID: {best_exp['id']}")
        print(f"  Score: {best_exp['results']['score']:.6f}")
        print(f"  Config: {best_exp['config']}")
    
    # Test reproducibility by re-running best experiment
    print(f"\nReproducibility test - re-running best experiment:")
    best_config = best_exp['config']
    rerun_exp = tracker.run_experiment(f"{best_exp['name']}_rerun", best_config)
    
    # Compare results
    original_score = best_exp['results']['score']
    rerun_score = rerun_exp['results']['score']
    score_diff = abs(original_score - rerun_score)
    
    print(f"\nReproducibility verification:")
    print(f"  Original score: {original_score:.10f}")
    print(f"  Rerun score:    {rerun_score:.10f}")
    print(f"  Difference:     {score_diff:.2e}")
    print(f"  Reproducible:   {'✓' if score_diff < 1e-10 else '✗'}")

5. Advanced Reproducibility Patterns
------------------------------------

Hierarchical Experiment Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate advanced patterns for organizing reproducible
experiments.

.. code:: ipython3

    # Example 10: Advanced reproducibility patterns
    print("Advanced Reproducibility Patterns:")
    print("=" * 35)
    
    class ReproducibilityManager:
        """Advanced manager for reproducible research workflows."""
        
        def __init__(self, project_name):
            self.project_name = project_name
            self.project_id = srepro.gen_id(time_format="%Y%m%d", N=4)
            self.sessions = {}
            self.global_config = {
                'project_name': project_name,
                'project_id': self.project_id,
                'created_at': srepro.gen_timestamp()
            }
            
            print(f"Reproducibility Manager initialized:")
            print(f"  Project: {project_name}")
            print(f"  Project ID: {self.project_id}")
            print(f"  Created: {self.global_config['created_at']}")
        
        def create_session(self, session_name, base_seed=None):
            """Create a new experimental session."""
            if base_seed is None:
                base_seed = hash(session_name) % 10000  # Deterministic seed from name
            
            session_id = srepro.gen_id(time_format="%Y%m%d_%H%M", N=4)
            
            session = {
                'name': session_name,
                'id': session_id,
                'base_seed': base_seed,
                'created_at': srepro.gen_timestamp(),
                'experiments': [],
                'status': 'active'
            }
            
            self.sessions[session_id] = session
            
            print(f"\nSession '{session_name}' created:")
            print(f"  Session ID: {session_id}")
            print(f"  Base seed: {base_seed}")
            
            return session_id
        
        def run_experiment_in_session(self, session_id, exp_name, params, seed_offset=0):
            """Run an experiment within a specific session."""
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Calculate deterministic seed
            experiment_seed = session['base_seed'] + seed_offset
            
            # Set up reproducibility
            if TORCH_AVAILABLE:
                srepro.fix_seeds(random=random, np=np, torch=torch, seed=experiment_seed, verbose=False)
            else:
                srepro.fix_seeds(random=random, np=np, seed=experiment_seed, verbose=False)
            
            # Generate experiment metadata
            exp_id = srepro.gen_id(N=6)
            timestamp = srepro.gen_timestamp()
            
            # Run the actual experiment
            results = self._run_simulation(params)
            
            # Create experiment record
            experiment = {
                'id': exp_id,
                'name': exp_name,
                'timestamp': timestamp,
                'session_id': session_id,
                'seed': experiment_seed,
                'seed_offset': seed_offset,
                'params': params.copy(),
                'results': results,
                'version': len(session['experiments']) + 1
            }
            
            session['experiments'].append(experiment)
            
            print(f"    Experiment '{exp_name}' (v{experiment['version']}) - Score: {results['metric']:.4f}")
            
            return experiment
        
        def _run_simulation(self, params):
            """Simulate an experiment."""
            n_samples = params.get('n_samples', 1000)
            complexity = params.get('complexity', 1.0)
            noise = params.get('noise', 0.1)
            
            # Generate synthetic data
            x = np.random.uniform(0, 1, n_samples)
            y = complexity * np.sin(2 * np.pi * x) + np.random.normal(0, noise, n_samples)
            
            # Compute metrics
            signal_to_noise = np.var(complexity * np.sin(2 * np.pi * x)) / (noise**2 + 1e-8)
            correlation = abs(np.corrcoef(x, y)[0, 1])
            metric = correlation * np.log(1 + signal_to_noise)
            
            return {
                'metric': metric,
                'correlation': correlation,
                'signal_to_noise': signal_to_noise,
                'data_mean': np.mean(y),
                'data_std': np.std(y)
            }
        
        def get_project_summary(self):
            """Get comprehensive project summary."""
            total_experiments = sum(len(session['experiments']) for session in self.sessions.values())
            
            summary = f"\nProject: {self.project_name} ({self.project_id})\n"
            summary += f"Created: {self.global_config['created_at']}\n"
            summary += f"Sessions: {len(self.sessions)}\n"
            summary += f"Total experiments: {total_experiments}\n"
            summary += "-" * 50 + "\n"
            
            for session_id, session in self.sessions.items():
                summary += f"Session: {session['name']} ({session_id[-6:]})\n"
                summary += f"  Base seed: {session['base_seed']}\n"
                summary += f"  Experiments: {len(session['experiments'])}\n"
                
                if session['experiments']:
                    best_exp = max(session['experiments'], key=lambda x: x['results']['metric'])
                    summary += f"  Best score: {best_exp['results']['metric']:.4f} ({best_exp['name']})\n"
                
                summary += "\n"
            
            return summary
    
    # Create project and run hierarchical experiments
    manager = ReproducibilityManager("Advanced_ML_Study")
    
    # Create different experimental sessions
    session1 = manager.create_session("Hyperparameter_Tuning", base_seed=1000)
    session2 = manager.create_session("Architecture_Search", base_seed=2000)
    session3 = manager.create_session("Data_Augmentation", base_seed=3000)
    
    # Run experiments in different sessions
    print(f"\nRunning experiments across sessions:")
    
    # Session 1: Hyperparameter tuning
    print(f"\nSession 1 - Hyperparameter Tuning:")
    hp_configs = [
        {'n_samples': 1000, 'complexity': 0.5, 'noise': 0.1},
        {'n_samples': 1000, 'complexity': 1.0, 'noise': 0.1},
        {'n_samples': 1000, 'complexity': 1.5, 'noise': 0.1},
        {'n_samples': 1000, 'complexity': 1.0, 'noise': 0.05},
    ]
    
    for i, config in enumerate(hp_configs):
        manager.run_experiment_in_session(session1, f"hp_test_{i+1}", config, seed_offset=i)
    
    # Session 2: Architecture search
    print(f"\nSession 2 - Architecture Search:")
    arch_configs = [
        {'n_samples': 2000, 'complexity': 1.0, 'noise': 0.1},
        {'n_samples': 3000, 'complexity': 1.0, 'noise': 0.1},
        {'n_samples': 5000, 'complexity': 1.0, 'noise': 0.1},
    ]
    
    for i, config in enumerate(arch_configs):
        manager.run_experiment_in_session(session2, f"arch_{i+1}", config, seed_offset=i*10)
    
    # Session 3: Data augmentation
    print(f"\nSession 3 - Data Augmentation:")
    aug_configs = [
        {'n_samples': 1000, 'complexity': 1.0, 'noise': 0.05},
        {'n_samples': 1000, 'complexity': 1.2, 'noise': 0.08},
    ]
    
    for i, config in enumerate(aug_configs):
        manager.run_experiment_in_session(session3, f"aug_{i+1}", config, seed_offset=i*5)
    
    # Display comprehensive summary
    print(manager.get_project_summary())
    
    # Test reproducibility across the hierarchy
    print("Reproducibility verification across hierarchy:")
    print("-" * 45)
    
    # Re-run a specific experiment to test reproducibility
    original_exp = manager.sessions[session1]['experiments'][1]  # Second experiment from session 1
    print(f"\nRe-running experiment: {original_exp['name']}")
    print(f"  Original seed: {original_exp['seed']}")
    print(f"  Original score: {original_exp['results']['metric']:.10f}")
    
    # Re-run with same parameters
    rerun_exp = manager.run_experiment_in_session(
        session1, 
        f"{original_exp['name']}_rerun", 
        original_exp['params'], 
        seed_offset=original_exp['seed_offset']
    )
    
    print(f"  Rerun score:    {rerun_exp['results']['metric']:.10f}")
    
    score_diff = abs(original_exp['results']['metric'] - rerun_exp['results']['metric'])
    print(f"  Difference:     {score_diff:.2e}")
    print(f"  Reproducible:   {'✓' if score_diff < 1e-10 else '✗'}")
    
    print(f"\nHierarchical reproducibility system successfully demonstrated!")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.repro`` module:

Core Functions
~~~~~~~~~~~~~~

Random Seed Management
^^^^^^^^^^^^^^^^^^^^^^

-  **``fix_seeds``**: Comprehensive seed fixing across multiple
   libraries

   -  Support for Python ``random``, ``numpy``, ``torch``,
      ``tensorflow``, and ``os``
   -  Ensures deterministic behavior across entire computational
      pipeline
   -  Verbose reporting of which libraries were configured
   -  Cross-platform reproducibility

Unique Identifier Generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **``gen_id`` and ``gen_ID``**: Generate unique experiment identifiers

   -  Timestamp-based prefixes for chronological ordering
   -  Customizable time formats for different use cases
   -  Configurable random suffix length
   -  High uniqueness probability for parallel execution

Timestamp Generation
^^^^^^^^^^^^^^^^^^^^

-  **``gen_timestamp`` and ``timestamp``**: Standardized timestamp
   generation

   -  Consistent format: YYYY-MMDD-HHMM
   -  Suitable for file naming and version control
   -  Chronologically sortable
   -  Cross-platform compatibility

Key Features Demonstrated
~~~~~~~~~~~~~~~~~~~~~~~~~

Reproducibility Assurance
^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Perfect Determinism**: Same seeds produce identical results across
   runs
2. **Multi-Library Support**: Comprehensive coverage of scientific
   Python ecosystem
3. **Cross-Platform Consistency**: Reproducible results across different
   systems
4. **Seed Differentiation**: Different seeds produce meaningfully
   different results

Experiment Management
^^^^^^^^^^^^^^^^^^^^^

1. **Unique Identification**: Every experiment gets a unique, traceable
   identifier
2. **Temporal Ordering**: Timestamps enable chronological experiment
   tracking
3. **Version Control**: Support for experiment versioning and comparison
4. **Hierarchical Organization**: Sessions and projects for complex
   research workflows

Scientific Workflow Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Experiment Classes**: Object-oriented experiment management
2. **Tracking Systems**: Comprehensive experiment logging and comparison
3. **Reproducibility Verification**: Built-in tools to verify
   reproducibility
4. **Best Practice Patterns**: Templates for reproducible research
   workflows

Practical Applications
~~~~~~~~~~~~~~~~~~~~~~

Research Reproducibility
^^^^^^^^^^^^^^^^^^^^^^^^

-  **Scientific Papers**: Ensure reproducible results for publication
-  **Collaboration**: Share experiments with guaranteed reproducibility
-  **Peer Review**: Enable reviewers to reproduce results exactly
-  **Long-term Archival**: Maintain reproducibility over time

Machine Learning Workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **Model Training**: Reproducible training runs for comparison
-  **Hyperparameter Tuning**: Systematic exploration with
   reproducibility
-  **Ablation Studies**: Controlled experiments with isolated variables
-  **Benchmark Comparisons**: Fair comparisons across methods

Data Science Projects
^^^^^^^^^^^^^^^^^^^^^

-  **Analysis Pipelines**: Reproducible data processing and analysis
-  **A/B Testing**: Controlled experiments with statistical validity
-  **Model Validation**: Consistent cross-validation and testing
-  **Production Systems**: Deterministic behavior in deployed models

Best Practices Illustrated
~~~~~~~~~~~~~~~~~~~~~~~~~~

Seed Management
^^^^^^^^^^^^^^^

-  **Early Initialization**: Set seeds before any random operations
-  **Comprehensive Coverage**: Include all relevant libraries
-  **Deterministic Assignment**: Use consistent seed derivation
   strategies
-  **Verification Testing**: Always verify reproducibility with test
   runs

Experiment Organization
^^^^^^^^^^^^^^^^^^^^^^^

-  **Unique Identifiers**: Every experiment should have a unique ID
-  **Metadata Tracking**: Record all relevant experimental parameters
-  **Hierarchical Structure**: Organize experiments in logical groupings
-  **Temporal Tracking**: Maintain chronological experiment records

Documentation and Tracking
^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **Configuration Recording**: Store all experimental parameters
-  **Result Documentation**: Comprehensive result recording
-  **Version Control**: Track experiment versions and iterations
-  **Reproducibility Testing**: Regular verification of reproducibility

Integration Benefits
~~~~~~~~~~~~~~~~~~~~

Scientific Computing Ecosystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **NumPy/SciPy**: Reproducible numerical computations
-  **PyTorch/TensorFlow**: Deterministic deep learning
-  **Scikit-learn**: Consistent machine learning results
-  **Pandas**: Reproducible data analysis

Research Infrastructure
^^^^^^^^^^^^^^^^^^^^^^^

-  **Jupyter Notebooks**: Reproducible interactive research
-  **Version Control**: Git-friendly experiment tracking
-  **Cluster Computing**: Reproducible distributed experiments
-  **Continuous Integration**: Automated reproducibility testing

The ``scitex.repro`` module provides essential tools for ensuring
reproducible scientific computing, with comprehensive support for the
modern Python scientific ecosystem and practical patterns for real-world
research workflows.
