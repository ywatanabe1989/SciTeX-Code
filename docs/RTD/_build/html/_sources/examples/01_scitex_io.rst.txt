01 SciTeX Io
============

.. note::
   This page is generated from the Jupyter notebook `01_scitex_io.ipynb <https://github.com/scitex/scitex/blob/main/examples/01_scitex_io.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 01_scitex_io.ipynb


This comprehensive notebook demonstrates the SciTeX I/O module
capabilities, combining features from basic operations, advanced
functionality, and complete workflow examples.

Features Covered
----------------

Basic I/O Operations
~~~~~~~~~~~~~~~~~~~~

-  Unified save/load interface with automatic format detection
-  Symlink creation and management
-  Basic file operations

Advanced I/O Features
~~~~~~~~~~~~~~~~~~~~~

-  Compression support (gzip, bz2, xz)
-  HDF5 operations
-  Configuration file management
-  Performance comparisons across formats

Complete Workflows
~~~~~~~~~~~~~~~~~~

-  Caching mechanisms
-  Batch operations
-  Experiment pipeline integration
-  Real-world data processing examples

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import matplotlib.pyplot as plt
    import time
    
    # Set up example data directory
    data_dir = Path("./io_examples")
    data_dir.mkdir(exist_ok=True)
    
    print("SciTeX I/O Tutorial - Ready to begin!")


.. parsed-literal::

    SciTeX I/O Tutorial - Ready to begin!


Part 1: Basic I/O Operations
----------------------------

1.1 Unified Save/Load Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SciTeX provides a unified interface that automatically detects file
formats:

.. code:: ipython3

    # Create sample data
    sample_data = {
        'array': np.random.randn(100, 50),
        'dataframe': pd.DataFrame({
            'x': np.random.randn(1000),
            'y': np.random.randn(1000),
            'category': np.random.choice(['A', 'B', 'C'], 1000)
        }),
        'metadata': {
            'experiment': 'demo',
            'date': '2024-01-01',
            'parameters': {'alpha': 0.05, 'beta': 0.1}
        }
    }
    
    print(f"Sample data created:")
    print(f"- Array shape: {sample_data['array'].shape}")
    print(f"- DataFrame shape: {sample_data['dataframe'].shape}")
    print(f"- Metadata keys: {list(sample_data['metadata'].keys())}")


.. parsed-literal::

    Sample data created:
    - Array shape: (100, 50)
    - DataFrame shape: (1000, 3)
    - Metadata keys: ['experiment', 'date', 'parameters']


.. code:: ipython3

    # Save data in multiple formats - automatic format detection
    formats_to_test = ['pkl', 'json', 'npy', 'csv']
    
    for fmt in formats_to_test:
        try:
            if fmt == 'npy':
                # For .npy, save just the array
                scitex.io.save(sample_data['array'], data_dir / f"sample_array.{fmt}")
            elif fmt == 'csv':
                # For .csv, save just the dataframe
                scitex.io.save(sample_data['dataframe'], data_dir / f"sample_dataframe.{fmt}")
            else:
                # For pkl and json, save the full dictionary
                scitex.io.save(sample_data, data_dir / f"sample_data.{fmt}")
            print(f"✓ Saved data in {fmt.upper()} format")
        except Exception as e:
            print(f"✗ Failed to save in {fmt.upper()} format: {e}")


.. parsed-literal::

    ERROR:root:Error occurred while saving: 'PosixPath' object has no attribute 'startswith'Debug: Initial script_path = /tmp/ipykernel_615780/3137666053.pyDebug: Final spath = None
    ERROR:root:Error occurred while saving: 'PosixPath' object has no attribute 'startswith'Debug: Initial script_path = /tmp/ipykernel_615780/3137666053.pyDebug: Final spath = None
    ERROR:root:Error occurred while saving: 'PosixPath' object has no attribute 'startswith'Debug: Initial script_path = /tmp/ipykernel_615780/3137666053.pyDebug: Final spath = None
    ERROR:root:Error occurred while saving: 'PosixPath' object has no attribute 'startswith'Debug: Initial script_path = /tmp/ipykernel_615780/3137666053.pyDebug: Final spath = None


.. parsed-literal::

    ✓ Saved data in PKL format
    ✓ Saved data in JSON format
    ✓ Saved data in NPY format
    ✓ Saved data in CSV format


.. code:: ipython3

    # Load data back - automatic format detection
    loaded_data = {}
    
    # Load pickle data (full dictionary)
    if (data_dir / "sample_data.pkl").exists():
        loaded_data['from_pkl'] = scitex.io.load(data_dir / "sample_data.pkl")
        print("✓ Loaded data from pickle")
    
    # Load numpy array
    if (data_dir / "sample_array.npy").exists():
        loaded_data['from_npy'] = scitex.io.load(data_dir / "sample_array.npy")
        print(f"✓ Loaded array from npy: shape {loaded_data['from_npy'].shape}")
    
    # Load CSV dataframe
    if (data_dir / "sample_dataframe.csv").exists():
        loaded_data['from_csv'] = scitex.io.load(data_dir / "sample_dataframe.csv")
        print(f"✓ Loaded dataframe from csv: shape {loaded_data['from_csv'].shape}")

1.2 Symlink Creation and Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create symlinks for easy access
    symlink_dir = data_dir / "symlinks"
    symlink_dir.mkdir(exist_ok=True)
    
    # Create symlinks to our saved files
    original_file = data_dir / "sample_data.pkl"
    if original_file.exists():
        symlink_path = symlink_dir / "latest_data.pkl"
        
        # Remove existing symlink if it exists
        if symlink_path.is_symlink():
            symlink_path.unlink()
        
        # Create new symlink
        symlink_path.symlink_to(original_file.resolve())
        print(f"✓ Created symlink: {symlink_path} -> {original_file}")
        
        # Verify symlink works
        symlink_data = scitex.io.load(symlink_path)
        print(f"✓ Successfully loaded data through symlink")
        print(f"  Array shape: {symlink_data['array'].shape}")
    else:
        print("Original file not found for symlink creation")

Part 2: Advanced I/O Features
-----------------------------

2.1 Compression Support
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Test compression formats
    compression_formats = ['gzip', 'bz2', 'xz']
    large_data = {
        'large_array': np.random.randn(1000, 1000),
        'text_data': 'This is a test string that will be repeated many times. ' * 1000
    }
    
    file_sizes = {}
    
    # Save uncompressed
    uncompressed_file = data_dir / "large_data.pkl"
    scitex.io.save(large_data, uncompressed_file)
    file_sizes['uncompressed'] = uncompressed_file.stat().st_size
    
    # Save with compression
    for compression in compression_formats:
        try:
            compressed_file = data_dir / f"large_data.pkl.{compression}"
            scitex.io.save(large_data, compressed_file, compression=compression)
            file_sizes[compression] = compressed_file.stat().st_size
            print(f"✓ Saved with {compression} compression")
        except Exception as e:
            print(f"✗ Failed to save with {compression}: {e}")
    
    # Compare file sizes
    print("\nFile size comparison:")
    for format_name, size in file_sizes.items():
        size_mb = size / (1024 * 1024)
        if format_name != 'uncompressed':
            compression_ratio = file_sizes['uncompressed'] / size
            print(f"{format_name:12}: {size_mb:.2f} MB (compression ratio: {compression_ratio:.1f}x)")
        else:
            print(f"{format_name:12}: {size_mb:.2f} MB")

2.2 HDF5 Operations
~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # HDF5 operations for hierarchical data
    try:
        import h5py
        
        # Create hierarchical data structure
        hdf5_data = {
            'experiment_1': {
                'raw_data': np.random.randn(500, 100),
                'processed_data': np.random.randn(500, 50),
                'metadata': {
                    'sampling_rate': 1000,
                    'channels': 100
                }
            },
            'experiment_2': {
                'raw_data': np.random.randn(300, 100),
                'processed_data': np.random.randn(300, 50),
                'metadata': {
                    'sampling_rate': 500,
                    'channels': 100
                }
            }
        }
        
        # Save as HDF5
        hdf5_file = data_dir / "experiments.h5"
        scitex.io.save(hdf5_data, hdf5_file)
        print(f"✓ Saved hierarchical data to HDF5: {hdf5_file}")
        
        # Load HDF5 data
        loaded_hdf5 = scitex.io.load(hdf5_file)
        print(f"✓ Loaded HDF5 data with {len(loaded_hdf5)} experiments")
        
        for exp_name, exp_data in loaded_hdf5.items():
            print(f"  {exp_name}: raw_data shape {exp_data['raw_data'].shape}")
            
    except ImportError:
        print("h5py not available - skipping HDF5 examples")
    except Exception as e:
        print(f"HDF5 operations failed: {e}")

2.3 Performance Comparison Across Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Performance benchmark for different formats
    benchmark_data = {
        'numeric_array': np.random.randn(1000, 100),
        'dataframe': pd.DataFrame({
            'col_' + str(i): np.random.randn(5000) 
            for i in range(20)
        }),
        'mixed_data': {
            'numbers': list(range(10000)),
            'strings': [f'item_{i}' for i in range(1000)],
            'nested': {'a': [1, 2, 3], 'b': {'c': 4, 'd': 5}}
        }
    }
    
    formats_to_benchmark = ['pkl', 'json', 'h5']
    benchmark_results = {}
    
    for fmt in formats_to_benchmark:
        try:
            test_file = data_dir / f"benchmark.{fmt}"
            
            # Time save operation
            start_time = time.time()
            if fmt == 'json':
                # JSON can't handle numpy arrays directly
                json_safe_data = {
                    'numeric_array': benchmark_data['numeric_array'].tolist(),
                    'mixed_data': benchmark_data['mixed_data']
                }
                scitex.io.save(json_safe_data, test_file)
            else:
                scitex.io.save(benchmark_data, test_file)
            save_time = time.time() - start_time
            
            # Time load operation
            start_time = time.time()
            loaded = scitex.io.load(test_file)
            load_time = time.time() - start_time
            
            # Get file size
            file_size = test_file.stat().st_size / (1024 * 1024)  # MB
            
            benchmark_results[fmt] = {
                'save_time': save_time,
                'load_time': load_time,
                'file_size_mb': file_size
            }
            
            print(f"✓ {fmt.upper()}: Save {save_time:.3f}s, Load {load_time:.3f}s, Size {file_size:.2f}MB")
            
        except Exception as e:
            print(f"✗ {fmt.upper()} benchmark failed: {e}")
    
    # Visualize benchmark results
    if benchmark_results:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        formats = list(benchmark_results.keys())
        save_times = [benchmark_results[fmt]['save_time'] for fmt in formats]
        load_times = [benchmark_results[fmt]['load_time'] for fmt in formats]
        file_sizes = [benchmark_results[fmt]['file_size_mb'] for fmt in formats]
        
        axes[0].bar(formats, save_times)
        axes[0].set_title('Save Time (seconds)')
        axes[0].set_ylabel('Time (s)')
        
        axes[1].bar(formats, load_times)
        axes[1].set_title('Load Time (seconds)')
        axes[1].set_ylabel('Time (s)')
        
        axes[2].bar(formats, file_sizes)
        axes[2].set_title('File Size (MB)')
        axes[2].set_ylabel('Size (MB)')
        
        plt.tight_layout()
        plt.show()

Part 3: Complete Workflows and Caching
--------------------------------------

3.1 Caching Mechanisms
~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate caching for expensive operations
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    @scitex.io.cache_result(cache_dir / "expensive_computation.pkl")
    def expensive_computation(n_samples=10000, n_features=100):
        """Simulate an expensive computation that we want to cache."""
        print(f"Performing expensive computation with {n_samples} samples...")
        time.sleep(1)  # Simulate computation time
        
        # Generate some "computed" result
        data = np.random.randn(n_samples, n_features)
        features = np.mean(data, axis=0)
        correlations = np.corrcoef(data.T)
        
        return {
            'raw_data': data,
            'features': features,
            'correlations': correlations,
            'metadata': {
                'n_samples': n_samples,
                'n_features': n_features,
                'computed_at': time.time()
            }
        }
    
    # First call - will compute and cache
    print("First call (will compute):")
    start_time = time.time()
    result1 = expensive_computation(5000, 50)
    first_call_time = time.time() - start_time
    print(f"First call took {first_call_time:.2f} seconds")
    
    # Second call - will load from cache
    print("\nSecond call (will load from cache):")
    start_time = time.time()
    result2 = expensive_computation(5000, 50)
    second_call_time = time.time() - start_time
    print(f"Second call took {second_call_time:.2f} seconds")
    
    print(f"\nSpeedup from caching: {first_call_time/second_call_time:.1f}x")
    print(f"Results identical: {np.array_equal(result1['features'], result2['features'])}")

3.2 Batch Operations
~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Batch file operations
    batch_dir = data_dir / "batch_processing"
    batch_dir.mkdir(exist_ok=True)
    
    # Create multiple data files for batch processing
    batch_files = []
    for i in range(5):
        batch_data = {
            'id': i,
            'data': np.random.randn(100, 10),
            'labels': np.random.choice(['A', 'B', 'C'], 100),
            'timestamp': time.time() + i
        }
        
        filename = batch_dir / f"batch_data_{i:03d}.pkl"
        scitex.io.save(batch_data, filename)
        batch_files.append(filename)
    
    print(f"Created {len(batch_files)} batch files")
    
    # Batch loading with pattern matching
    pattern = batch_dir / "batch_data_*.pkl"
    all_batch_files = list(batch_dir.glob("batch_data_*.pkl"))
    print(f"Found {len(all_batch_files)} files matching pattern")
    
    # Load and combine all batch files
    combined_data = []
    for file_path in sorted(all_batch_files):
        data = scitex.io.load(file_path)
        combined_data.append(data)
    
    print(f"Loaded {len(combined_data)} batch files")
    print(f"Total data points: {sum(len(d['data']) for d in combined_data)}")
    
    # Combine all data into single arrays
    all_data = np.vstack([d['data'] for d in combined_data])
    all_labels = np.hstack([d['labels'] for d in combined_data])
    
    print(f"Combined data shape: {all_data.shape}")
    print(f"Label distribution: {dict(zip(*np.unique(all_labels, return_counts=True)))}")

3.3 Experiment Pipeline Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Complete experiment pipeline with I/O
    class ExperimentPipeline:
        def __init__(self, experiment_name, output_dir):
            self.experiment_name = experiment_name
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (self.output_dir / "raw").mkdir(exist_ok=True)
            (self.output_dir / "processed").mkdir(exist_ok=True)
            (self.output_dir / "results").mkdir(exist_ok=True)
            
        def generate_data(self, n_samples=1000, noise_level=0.1):
            """Generate synthetic experimental data."""
            print(f"Generating data for {self.experiment_name}...")
            
            # Simulate different experimental conditions
            conditions = ['control', 'treatment_A', 'treatment_B']
            raw_data = {}
            
            for condition in conditions:
                # Different signal patterns for each condition
                if condition == 'control':
                    signal = np.sin(np.linspace(0, 4*np.pi, n_samples))
                elif condition == 'treatment_A':
                    signal = np.sin(np.linspace(0, 4*np.pi, n_samples)) * 1.5
                else:  # treatment_B
                    signal = np.sin(np.linspace(0, 6*np.pi, n_samples)) * 0.8
                
                # Add noise
                noisy_signal = signal + np.random.normal(0, noise_level, n_samples)
                
                raw_data[condition] = {
                    'signal': noisy_signal,
                    'time': np.linspace(0, 10, n_samples),
                    'metadata': {
                        'condition': condition,
                        'n_samples': n_samples,
                        'noise_level': noise_level
                    }
                }
            
            # Save raw data
            raw_file = self.output_dir / "raw" / "raw_data.pkl"
            scitex.io.save(raw_data, raw_file)
            print(f"✓ Raw data saved to {raw_file}")
            
            return raw_data
        
        def process_data(self, raw_data=None):
            """Process the raw experimental data."""
            if raw_data is None:
                # Load from file
                raw_file = self.output_dir / "raw" / "raw_data.pkl"
                raw_data = scitex.io.load(raw_file)
            
            print("Processing experimental data...")
            processed_data = {}
            
            for condition, data in raw_data.items():
                signal = data['signal']
                time = data['time']
                
                # Apply processing steps
                # 1. Smoothing
                from scipy import ndimage
                smoothed = ndimage.gaussian_filter1d(signal, sigma=2)
                
                # 2. Feature extraction
                features = {
                    'mean': np.mean(smoothed),
                    'std': np.std(smoothed),
                    'max': np.max(smoothed),
                    'min': np.min(smoothed),
                    'peak_to_peak': np.ptp(smoothed)
                }
                
                # 3. Spectral analysis
                fft = np.fft.fft(smoothed)
                freqs = np.fft.fftfreq(len(smoothed), d=time[1]-time[0])
                power_spectrum = np.abs(fft)**2
                
                processed_data[condition] = {
                    'original_signal': signal,
                    'smoothed_signal': smoothed,
                    'features': features,
                    'power_spectrum': power_spectrum[:len(power_spectrum)//2],
                    'frequencies': freqs[:len(freqs)//2],
                    'time': time,
                    'metadata': data['metadata']
                }
            
            # Save processed data
            processed_file = self.output_dir / "processed" / "processed_data.pkl"
            scitex.io.save(processed_data, processed_file)
            print(f"✓ Processed data saved to {processed_file}")
            
            return processed_data
        
        def analyze_results(self, processed_data=None):
            """Analyze processed data and generate results."""
            if processed_data is None:
                processed_file = self.output_dir / "processed" / "processed_data.pkl"
                processed_data = scitex.io.load(processed_file)
            
            print("Analyzing results...")
            
            # Statistical analysis
            results = {
                'summary_statistics': {},
                'comparisons': {},
                'figures': {}
            }
            
            # Extract features for all conditions
            all_features = {}
            for condition, data in processed_data.items():
                all_features[condition] = data['features']
                results['summary_statistics'][condition] = data['features']
            
            # Generate comparison plots
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Experiment Results: {self.experiment_name}')
            
            # Plot 1: Original signals
            for condition, data in processed_data.items():
                axes[0, 0].plot(data['time'], data['smoothed_signal'], label=condition)
            axes[0, 0].set_title('Processed Signals')
            axes[0, 0].set_xlabel('Time')
            axes[0, 0].set_ylabel('Amplitude')
            axes[0, 0].legend()
            
            # Plot 2: Feature comparison
            feature_names = list(all_features['control'].keys())
            x_pos = np.arange(len(feature_names))
            width = 0.25
            
            for i, condition in enumerate(all_features.keys()):
                values = [all_features[condition][feat] for feat in feature_names]
                axes[0, 1].bar(x_pos + i*width, values, width, label=condition)
            
            axes[0, 1].set_title('Feature Comparison')
            axes[0, 1].set_xlabel('Features')
            axes[0, 1].set_ylabel('Value')
            axes[0, 1].set_xticks(x_pos + width)
            axes[0, 1].set_xticklabels(feature_names, rotation=45)
            axes[0, 1].legend()
            
            # Plot 3: Power spectra
            for condition, data in processed_data.items():
                axes[1, 0].semilogy(data['frequencies'], data['power_spectrum'], label=condition)
            axes[1, 0].set_title('Power Spectra')
            axes[1, 0].set_xlabel('Frequency (Hz)')
            axes[1, 0].set_ylabel('Power')
            axes[1, 0].legend()
            
            # Plot 4: Summary statistics
            conditions = list(all_features.keys())
            means = [all_features[cond]['mean'] for cond in conditions]
            stds = [all_features[cond]['std'] for cond in conditions]
            
            axes[1, 1].bar(conditions, means, yerr=stds, capsize=5)
            axes[1, 1].set_title('Mean ± Std by Condition')
            axes[1, 1].set_ylabel('Signal Mean')
            
            plt.tight_layout()
            
            # Save figure
            figure_file = self.output_dir / "results" / "analysis_summary.png"
            plt.savefig(figure_file, dpi=300, bbox_inches='tight')
            plt.show()
            
            results['figures']['summary_plot'] = str(figure_file)
            
            # Save results
            results_file = self.output_dir / "results" / "analysis_results.pkl"
            scitex.io.save(results, results_file)
            print(f"✓ Analysis results saved to {results_file}")
            
            return results
        
        def run_complete_pipeline(self, n_samples=1000, noise_level=0.1):
            """Run the complete experiment pipeline."""
            print(f"\n=== Running Complete Pipeline: {self.experiment_name} ===")
            
            # Step 1: Generate data
            raw_data = self.generate_data(n_samples, noise_level)
            
            # Step 2: Process data
            processed_data = self.process_data(raw_data)
            
            # Step 3: Analyze results
            results = self.analyze_results(processed_data)
            
            print(f"\n=== Pipeline Complete ===")
            print(f"Output directory: {self.output_dir}")
            print(f"Files created:")
            for file in self.output_dir.rglob("*"):
                if file.is_file():
                    print(f"  {file.relative_to(self.output_dir)}")
            
            return results
    
    # Run the complete pipeline
    pipeline = ExperimentPipeline(
        experiment_name="SciTeX_IO_Demo",
        output_dir=data_dir / "experiment_pipeline"
    )
    
    final_results = pipeline.run_complete_pipeline(n_samples=500, noise_level=0.05)

Part 4: Configuration Management and Advanced Features
------------------------------------------------------

.. code:: ipython3

    # Configuration file management
    config_dir = data_dir / "configs"
    config_dir.mkdir(exist_ok=True)
    
    # Create experiment configurations
    configs = {
        'default': {
            'data_params': {
                'n_samples': 1000,
                'noise_level': 0.1,
                'sampling_rate': 100
            },
            'processing_params': {
                'smoothing_sigma': 2.0,
                'filter_cutoff': 0.5
            },
            'analysis_params': {
                'significance_level': 0.05,
                'bootstrap_iterations': 1000
            }
        },
        'high_resolution': {
            'data_params': {
                'n_samples': 5000,
                'noise_level': 0.05,
                'sampling_rate': 1000
            },
            'processing_params': {
                'smoothing_sigma': 1.0,
                'filter_cutoff': 0.1
            },
            'analysis_params': {
                'significance_level': 0.01,
                'bootstrap_iterations': 5000
            }
        }
    }
    
    # Save configurations in different formats
    for config_name, config_data in configs.items():
        # Save as JSON (human-readable)
        json_file = config_dir / f"{config_name}_config.json"
        scitex.io.save(config_data, json_file)
        
        # Save as YAML (if available)
        try:
            yaml_file = config_dir / f"{config_name}_config.yaml"
            scitex.io.save(config_data, yaml_file)
            print(f"✓ Saved {config_name} config in JSON and YAML formats")
        except Exception:
            print(f"✓ Saved {config_name} config in JSON format (YAML not available)")
    
    # Load and use configuration
    loaded_config = scitex.io.load(config_dir / "high_resolution_config.json")
    print(f"\nLoaded configuration:")
    for section, params in loaded_config.items():
        print(f"  {section}:")
        for key, value in params.items():
            print(f"    {key}: {value}")

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive I/O capabilities of the
SciTeX library:

Key Features Covered:
~~~~~~~~~~~~~~~~~~~~~

1. **Unified Interface**: Automatic format detection for save/load
   operations
2. **Multiple Formats**: Support for pickle, JSON, HDF5, CSV, NumPy, and
   compressed formats
3. **Performance Optimization**: Caching, compression, and
   format-specific optimizations
4. **Batch Operations**: Efficient handling of multiple files
5. **Complete Workflows**: Integration with experimental pipelines
6. **Configuration Management**: Flexible configuration file handling

Best Practices:
~~~~~~~~~~~~~~~

-  Use **pickle** for complex Python objects and mixed data types
-  Use **HDF5** for large, hierarchical datasets
-  Use **JSON/YAML** for human-readable configuration files
-  Apply **compression** for large files when storage space is limited
-  Implement **caching** for expensive computations
-  Organize data with **clear directory structures**
-  Use **symlinks** for easy access to frequently used files

.. code:: ipython3

    # Cleanup - remove example files (optional)
    import shutil
    
    cleanup = input("Clean up example files? (y/n): ").lower().startswith('y')
    if cleanup:
        shutil.rmtree(data_dir)
        print("✓ Example files cleaned up")
    else:
        print(f"Example files preserved in: {data_dir}")
        print(f"Total size: {sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file()) / (1024*1024):.1f} MB")
