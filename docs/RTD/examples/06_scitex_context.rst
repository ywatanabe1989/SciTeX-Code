06 SciTeX Context
=================

.. note::
   This page is generated from the Jupyter notebook `06_scitex_context.ipynb <https://github.com/scitex/scitex/blob/main/examples/06_scitex_context.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 06_scitex_context.ipynb


This comprehensive notebook demonstrates the SciTeX context module
capabilities, covering context management, output suppression, and
environment control utilities.

Features Covered
----------------

Output Control
~~~~~~~~~~~~~~

-  Output suppression utilities
-  Quiet operation modes
-  Context managers for clean execution

Environment Management
~~~~~~~~~~~~~~~~~~~~~~

-  Temporary state changes
-  Clean execution contexts
-  Resource management

Integration Examples
~~~~~~~~~~~~~~~~~~~~

-  Scientific computation workflows
-  Data processing pipelines
-  Automated analysis systems

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import matplotlib.pyplot as plt
    import warnings
    import time
    import os
    
    # Set up example data directory
    data_dir = Path("./context_examples")
    data_dir.mkdir(exist_ok=True)
    
    print("SciTeX Context Management Tutorial - Ready to begin!")
    print(f"Available context functions: {len(scitex.context.__all__)}")
    print(f"Functions: {scitex.context.__all__}")

Part 1: Basic Output Suppression
--------------------------------

1.1 Suppress Output Context Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate basic output suppression
    print("Basic Output Suppression:")
    print("=" * 28)
    
    # Normal output (visible)
    print("\n1. Normal output (visible):")
    print("This message will be visible")
    print("So will this one")
    print("And this one too")
    
    # Suppressed output (hidden)
    print("\n2. Suppressed output (hidden):")
    print("About to suppress output...")
    
    with scitex.context.suppress_output():
        print("This message will be hidden")
        print("This one too")
        print("And this one as well")
        
        # Even function calls that produce output
        for i in range(3):
            print(f"Hidden message {i+1}")
    
    print("Output suppression ended - this message is visible again")
    
    # Test with different types of output
    print("\n3. Testing different output types:")
    
    def noisy_function():
        """A function that produces lots of output."""
        print("Starting noisy function...")
        for i in range(5):
            print(f"Processing item {i+1}/5")
            # Simulate some work
            time.sleep(0.01)
        print("Noisy function completed!")
        return "Function result"
    
    # Run function normally (noisy)
    print("\nRunning function normally (noisy):")
    result1 = noisy_function()
    print(f"Result: {result1}")
    
    # Run function with suppressed output (quiet)
    print("\nRunning function with suppressed output (quiet):")
    with scitex.context.suppress_output():
        result2 = noisy_function()
    print(f"Result: {result2}")
    
    print("\nBoth results are identical:", result1 == result2)

1.2 Quiet Operation Mode
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate quiet operation mode
    print("Quiet Operation Mode:")
    print("=" * 22)
    
    # Define functions with verbose output
    def verbose_data_processing():
        """Simulate verbose data processing."""
        print("Loading data...")
        data = np.random.randn(1000, 50)
        print(f"Loaded data shape: {data.shape}")
        
        print("Normalizing data...")
        normalized_data = (data - np.mean(data)) / np.std(data)
        print(f"Data normalized, mean: {np.mean(normalized_data):.6f}, std: {np.std(normalized_data):.6f}")
        
        print("Computing correlations...")
        correlations = np.corrcoef(normalized_data.T)
        print(f"Correlation matrix shape: {correlations.shape}")
        
        print("Finding principal components...")
        eigenvalues, eigenvectors = np.linalg.eig(correlations)
        print(f"Found {len(eigenvalues)} eigenvalues")
        print(f"Top 3 eigenvalues: {sorted(eigenvalues, reverse=True)[:3]}")
        
        print("Data processing completed!")
        return {
            'data': normalized_data,
            'correlations': correlations,
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors
        }
    
    def verbose_model_training():
        """Simulate verbose model training."""
        print("Initializing model...")
        print("Model architecture: 3-layer neural network")
        print("Input size: 50, Hidden: 32, Output: 10")
        
        print("Starting training...")
        for epoch in range(10):
            loss = 1.0 / (epoch + 1) + 0.1 * np.random.random()
            accuracy = 1.0 - loss + 0.05 * np.random.random()
            print(f"Epoch {epoch+1}/10 - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
            time.sleep(0.01)  # Simulate training time
        
        print("Training completed!")
        print("Model saved to: model_weights.pkl")
        return {'final_loss': loss, 'final_accuracy': accuracy}
    
    # Test verbose operations
    print("\n1. Verbose data processing:")
    data_results = verbose_data_processing()
    print(f"Data processing returned {len(data_results)} items")
    
    print("\n2. Verbose model training:")
    training_results = verbose_model_training()
    print(f"Training results: {training_results}")
    
    # Test quiet operations using scitex.context.quiet
    print("\n" + "="*50)
    print("QUIET OPERATIONS (OUTPUT SUPPRESSED)")
    print("="*50)
    
    print("\n3. Quiet data processing:")
    with scitex.context.quiet():
        quiet_data_results = verbose_data_processing()
    print(f"Quiet data processing completed, returned {len(quiet_data_results)} items")
    
    print("\n4. Quiet model training:")
    with scitex.context.quiet():
        quiet_training_results = verbose_model_training()
    print(f"Quiet training completed: {quiet_training_results}")
    
    # Verify results are identical
    print("\n5. Results comparison:")
    print(f"Data results keys match: {set(data_results.keys()) == set(quiet_data_results.keys())}")
    print(f"Training final accuracy: {training_results['final_accuracy']:.4f} vs {quiet_training_results['final_accuracy']:.4f}")

Part 2: Advanced Context Management
-----------------------------------

2.1 Nested Context Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate nested context managers
    print("Nested Context Managers:")
    print("=" * 27)
    
    def multi_level_function():
        """Function with multiple levels of verbosity."""
        print("[LEVEL 1] Starting multi-level function")
        
        def level_2_function():
            print("[LEVEL 2] Inside level 2 function")
            for i in range(3):
                print(f"[LEVEL 2] Processing {i+1}/3")
            
            def level_3_function():
                print("[LEVEL 3] Deep processing")
                for j in range(5):
                    print(f"[LEVEL 3] Deep step {j+1}/5")
                print("[LEVEL 3] Deep processing complete")
                return "deep_result"
            
            result = level_3_function()
            print(f"[LEVEL 2] Level 3 returned: {result}")
            return result
        
        result = level_2_function()
        print(f"[LEVEL 1] Level 2 returned: {result}")
        print("[LEVEL 1] Multi-level function complete")
        return result
    
    # Test normal execution
    print("\n1. Normal execution (all output visible):")
    result1 = multi_level_function()
    print(f"Final result: {result1}")
    
    # Test single-level suppression
    print("\n2. Single-level suppression:")
    with scitex.context.suppress_output():
        result2 = multi_level_function()
    print(f"Final result: {result2}")
    
    # Test nested suppression contexts
    print("\n3. Nested suppression contexts:")
    
    def selective_suppression():
        print("[OUTER] Starting selective suppression")
        
        print("[OUTER] About to enter quiet zone...")
        with scitex.context.quiet():
            print("[QUIET] This should be suppressed")
            
            # Even more nested
            with scitex.context.suppress_output():
                print("[DOUBLE QUIET] This is doubly suppressed")
                for i in range(3):
                    print(f"[DOUBLE QUIET] Iteration {i}")
            
            print("[QUIET] Back to single suppression")
        
        print("[OUTER] Exited quiet zone")
        return "selective_result"
    
    result3 = selective_suppression()
    print(f"Selective suppression result: {result3}")
    
    # Test context manager exception handling
    print("\n4. Exception handling in context managers:")
    
    def function_with_error():
        print("Starting function that will raise an error")
        print("Doing some work...")
        raise ValueError("Intentional error for testing")
    
    # Test that context manager properly handles exceptions
    try:
        print("Testing exception handling with context manager:")
        with scitex.context.suppress_output():
            function_with_error()
    except ValueError as e:
        print(f"Caught expected error: {e}")
        print("Context manager properly restored output after exception")
    
    print("This message confirms output is working normally after exception")

2.2 Warning and Error Suppression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate warning and error suppression
    print("Warning and Error Suppression:")
    print("=" * 32)
    
    # Function that generates warnings
    def function_with_warnings():
        """Function that generates various warnings."""
        print("Function starting...")
        
        # Generate numpy warnings
        print("Creating arrays with potential warnings...")
        
        # Division by zero warning
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            result1 = np.array([1, 2, 3, 0]) / np.array([2, 0, 1, 0])  # Will generate warnings
        
        # Invalid value warning
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            result2 = np.sqrt(np.array([-1, 4, -9, 16]))  # Will generate warnings
        
        # Overflow warning
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            result3 = np.exp(np.array([700, 800, 900]))  # Will generate warnings
        
        print("Arrays created with potential warnings")
        print(f"Results: {len(result1)}, {len(result2)}, {len(result3)} arrays")
        
        return result1, result2, result3
    
    # Test with warnings visible
    print("\n1. Function with warnings visible:")
    with warnings.catch_warnings():
        warnings.simplefilter("always")  # Show all warnings
        results1 = function_with_warnings()
    
    # Test with both output and warnings suppressed
    print("\n2. Function with output and warnings suppressed:")
    with scitex.context.suppress_output():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress warnings
            results2 = function_with_warnings()
    
    print("Suppressed execution completed")
    
    # Verify results are still computed correctly
    print(f"Results computed correctly: {len(results1) == len(results2)}")
    
    # Test stderr suppression
    print("\n3. Testing stderr suppression:")
    
    def function_with_stderr():
        """Function that writes to stderr."""
        print("Writing to stdout")
        sys.stderr.write("Writing to stderr\n")
        sys.stderr.write("Another stderr message\n")
        print("Back to stdout")
        return "stderr_test_result"
    
    # Normal execution (stderr visible)
    print("Normal execution (stderr may be visible):")
    result_normal = function_with_stderr()
    
    # Suppressed execution
    print("\nSuppressed execution:")
    with scitex.context.suppress_output():
        result_suppressed = function_with_stderr()
    
    print(f"Results match: {result_normal == result_suppressed}")

Part 3: Scientific Computing Applications
-----------------------------------------

3.1 Clean Data Processing Pipelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Clean data processing pipelines
    print("Clean Data Processing Pipelines:")
    print("=" * 36)
    
    class DataProcessor:
        """A data processor with verbose and quiet modes."""
        
        def __init__(self, verbose=True):
            self.verbose = verbose
            self.processing_log = []
        
        def log(self, message):
            """Log a message if verbose mode is enabled."""
            self.processing_log.append(message)
            if self.verbose:
                print(f"[DataProcessor] {message}")
        
        def load_data(self, shape=(1000, 50)):
            """Load synthetic data."""
            self.log(f"Loading data with shape {shape}")
            data = np.random.randn(*shape)
            
            # Add some structure
            data[:, :10] += np.sin(np.linspace(0, 2*np.pi, shape[0]))[:, np.newaxis]
            data[:, 10:20] += np.cos(np.linspace(0, 4*np.pi, shape[0]))[:, np.newaxis]
            
            self.log(f"Data loaded successfully")
            self.log(f"Data statistics: mean={np.mean(data):.4f}, std={np.std(data):.4f}")
            
            return data
        
        def preprocess_data(self, data):
            """Preprocess the data."""
            self.log("Starting data preprocessing")
            
            # Step 1: Remove outliers
            self.log("Removing outliers (>3 std)")
            outlier_mask = np.abs(data) > 3 * np.std(data)
            data_cleaned = data.copy()
            data_cleaned[outlier_mask] = np.nan
            outliers_removed = np.sum(outlier_mask)
            self.log(f"Removed {outliers_removed} outliers")
            
            # Step 2: Interpolate missing values
            self.log("Interpolating missing values")
            for col in range(data_cleaned.shape[1]):
                mask = ~np.isnan(data_cleaned[:, col])
                if np.sum(mask) > 0:
                    data_cleaned[~mask, col] = np.mean(data_cleaned[mask, col])
            
            # Step 3: Normalize
            self.log("Normalizing data (z-score)")
            data_normalized = (data_cleaned - np.mean(data_cleaned, axis=0)) / np.std(data_cleaned, axis=0)
            
            self.log("Preprocessing completed")
            self.log(f"Final data: mean={np.mean(data_normalized):.6f}, std={np.std(data_normalized):.6f}")
            
            return data_normalized
        
        def analyze_data(self, data):
            """Analyze the preprocessed data."""
            self.log("Starting data analysis")
            
            # Correlation analysis
            self.log("Computing correlation matrix")
            correlation_matrix = np.corrcoef(data.T)
            
            # Principal component analysis
            self.log("Performing PCA")
            eigenvalues, eigenvectors = np.linalg.eig(correlation_matrix)
            
            # Sort by eigenvalue magnitude
            idx = np.argsort(eigenvalues)[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]
            
            # Compute explained variance
            explained_variance = eigenvalues / np.sum(eigenvalues)
            cumulative_variance = np.cumsum(explained_variance)
            
            self.log(f"First 5 eigenvalues: {eigenvalues[:5]}")
            self.log(f"Variance explained by first 5 PCs: {explained_variance[:5]}")
            self.log(f"Cumulative variance (first 10 PCs): {cumulative_variance[9]:.4f}")
            
            # Cluster analysis
            self.log("Performing simple clustering")
            # Simple k-means-like clustering
            n_clusters = 3
            centroids = data[np.random.choice(data.shape[0], n_clusters, replace=False)]
            
            distances = np.sqrt(((data[:, np.newaxis, :] - centroids[np.newaxis, :, :]) ** 2).sum(axis=2))
            labels = np.argmin(distances, axis=1)
            
            cluster_sizes = [np.sum(labels == i) for i in range(n_clusters)]
            self.log(f"Cluster sizes: {cluster_sizes}")
            
            self.log("Analysis completed")
            
            return {
                'correlation_matrix': correlation_matrix,
                'eigenvalues': eigenvalues,
                'eigenvectors': eigenvectors,
                'explained_variance': explained_variance,
                'cumulative_variance': cumulative_variance,
                'cluster_labels': labels,
                'cluster_sizes': cluster_sizes
            }
        
        def run_pipeline(self, data_shape=(1000, 50)):
            """Run the complete data processing pipeline."""
            self.log("=" * 50)
            self.log("STARTING DATA PROCESSING PIPELINE")
            self.log("=" * 50)
            
            # Load data
            data = self.load_data(data_shape)
            
            # Preprocess
            processed_data = self.preprocess_data(data)
            
            # Analyze
            analysis_results = self.analyze_data(processed_data)
            
            self.log("=" * 50)
            self.log("PIPELINE COMPLETED SUCCESSFULLY")
            self.log("=" * 50)
            
            return {
                'raw_data': data,
                'processed_data': processed_data,
                'analysis': analysis_results,
                'log': self.processing_log
            }
    
    # Test verbose pipeline
    print("\n1. Verbose data processing pipeline:")
    verbose_processor = DataProcessor(verbose=True)
    verbose_results = verbose_processor.run_pipeline((500, 20))
    print(f"\nVerbose pipeline completed. Log entries: {len(verbose_results['log'])}")
    
    # Test quiet pipeline using context manager
    print("\n" + "="*60)
    print("2. Quiet data processing pipeline:")
    
    with scitex.context.quiet():
        quiet_processor = DataProcessor(verbose=True)  # Still verbose, but output suppressed
        quiet_results = quiet_processor.run_pipeline((500, 20))
    
    print(f"Quiet pipeline completed. Log entries: {len(quiet_results['log'])}")
    
    # Compare results
    print("\n3. Results comparison:")
    print(f"Verbose analysis keys: {list(verbose_results['analysis'].keys())}")
    print(f"Quiet analysis keys: {list(quiet_results['analysis'].keys())}")
    print(f"Results structure identical: {set(verbose_results.keys()) == set(quiet_results.keys())}")
    
    # Show log comparison
    print(f"\nLog comparison:")
    print(f"Verbose log entries: {len(verbose_results['log'])}")
    print(f"Quiet log entries: {len(quiet_results['log'])}")
    print(f"First verbose log entry: {verbose_results['log'][0]}")
    print(f"First quiet log entry: {quiet_results['log'][0]}")

3.2 Automated Analysis with Clean Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Automated analysis with clean output
    print("Automated Analysis with Clean Output:")
    print("=" * 38)
    
    class AutomatedAnalyzer:
        """Automated analyzer that can run in quiet or verbose mode."""
        
        def __init__(self):
            self.analysis_history = []
        
        def analyze_dataset(self, dataset_name, data, quiet=False):
            """Analyze a dataset with optional quiet mode."""
            
            def verbose_analysis():
                print(f"\n{'='*50}")
                print(f"ANALYZING DATASET: {dataset_name}")
                print(f"{'='*50}")
                
                print(f"Dataset shape: {data.shape}")
                print(f"Data type: {data.dtype}")
                
                # Basic statistics
                print("\nBasic Statistics:")
                print(f"  Mean: {np.mean(data):.6f}")
                print(f"  Std:  {np.std(data):.6f}")
                print(f"  Min:  {np.min(data):.6f}")
                print(f"  Max:  {np.max(data):.6f}")
                
                # Distribution analysis
                print("\nDistribution Analysis:")
                percentiles = [5, 25, 50, 75, 95]
                perc_values = np.percentile(data, percentiles)
                for p, v in zip(percentiles, perc_values):
                    print(f"  {p}th percentile: {v:.6f}")
                
                # Correlation analysis
                if data.ndim > 1 and data.shape[1] > 1:
                    print("\nCorrelation Analysis:")
                    corr_matrix = np.corrcoef(data.T)
                    
                    # Find highest correlations
                    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
                    correlations = corr_matrix[mask]
                    high_corr = correlations[np.abs(correlations) > 0.5]
                    
                    print(f"  Correlation matrix shape: {corr_matrix.shape}")
                    print(f"  High correlations (|r| > 0.5): {len(high_corr)}")
                    if len(high_corr) > 0:
                        print(f"  Max correlation: {np.max(np.abs(high_corr)):.4f}")
                
                # Outlier detection
                print("\nOutlier Detection:")
                z_scores = np.abs((data - np.mean(data)) / np.std(data))
                outliers = z_scores > 3
                n_outliers = np.sum(outliers)
                outlier_percentage = (n_outliers / data.size) * 100
                
                print(f"  Outliers (|z| > 3): {n_outliers} ({outlier_percentage:.2f}%)")
                
                # Trend analysis
                if data.ndim == 1 or (data.ndim == 2 and data.shape[1] == 1):
                    print("\nTrend Analysis:")
                    flat_data = data.flatten()
                    x = np.arange(len(flat_data))
                    slope, intercept = np.polyfit(x, flat_data, 1)
                    print(f"  Linear trend slope: {slope:.8f}")
                    print(f"  Trend direction: {'Increasing' if slope > 0 else 'Decreasing' if slope < 0 else 'Flat'}")
                
                print(f"\n{'='*50}")
                print(f"ANALYSIS COMPLETED: {dataset_name}")
                print(f"{'='*50}\n")
                
                # Return analysis results
                results = {
                    'dataset_name': dataset_name,
                    'shape': data.shape,
                    'basic_stats': {
                        'mean': np.mean(data),
                        'std': np.std(data),
                        'min': np.min(data),
                        'max': np.max(data)
                    },
                    'percentiles': dict(zip(percentiles, perc_values)),
                    'outliers': {
                        'count': n_outliers,
                        'percentage': outlier_percentage
                    }
                }
                
                if data.ndim > 1 and data.shape[1] > 1:
                    results['correlations'] = {
                        'matrix_shape': corr_matrix.shape,
                        'high_correlations': len(high_corr),
                        'max_correlation': np.max(np.abs(high_corr)) if len(high_corr) > 0 else 0
                    }
                
                if data.ndim == 1 or (data.ndim == 2 and data.shape[1] == 1):
                    results['trend'] = {
                        'slope': slope,
                        'direction': 'Increasing' if slope > 0 else 'Decreasing' if slope < 0 else 'Flat'
                    }
                
                return results
            
            # Run analysis with or without output suppression
            if quiet:
                with scitex.context.suppress_output():
                    results = verbose_analysis()
            else:
                results = verbose_analysis()
            
            # Store in history
            self.analysis_history.append(results)
            
            return results
        
        def batch_analysis(self, datasets, quiet=True):
            """Perform batch analysis on multiple datasets."""
            print(f"Starting batch analysis of {len(datasets)} datasets...")
            
            results = []
            for name, data in datasets.items():
                if not quiet:
                    print(f"\nProcessing dataset: {name}")
                
                result = self.analyze_dataset(name, data, quiet=quiet)
                results.append(result)
                
                if not quiet:
                    print(f"Completed: {name}")
            
            print(f"\nBatch analysis completed. Processed {len(results)} datasets.")
            return results
        
        def generate_summary(self):
            """Generate a summary of all analyses."""
            if not self.analysis_history:
                print("No analyses performed yet.")
                return
            
            print(f"\nANALYSIS SUMMARY")
            print(f"="*20)
            print(f"Total datasets analyzed: {len(self.analysis_history)}")
            
            # Summary statistics
            all_means = [r['basic_stats']['mean'] for r in self.analysis_history]
            all_stds = [r['basic_stats']['std'] for r in self.analysis_history]
            all_outlier_pcts = [r['outliers']['percentage'] for r in self.analysis_history]
            
            print(f"\nAcross all datasets:")
            print(f"  Mean of means: {np.mean(all_means):.6f}")
            print(f"  Mean of stds: {np.mean(all_stds):.6f}")
            print(f"  Average outlier percentage: {np.mean(all_outlier_pcts):.2f}%")
            
            # Dataset with highest/lowest variation
            max_std_idx = np.argmax(all_stds)
            min_std_idx = np.argmin(all_stds)
            
            print(f"\nDataset with highest variation: {self.analysis_history[max_std_idx]['dataset_name']} (std: {all_stds[max_std_idx]:.6f})")
            print(f"Dataset with lowest variation: {self.analysis_history[min_std_idx]['dataset_name']} (std: {all_stds[min_std_idx]:.6f})")
    
    # Create test datasets
    test_datasets = {
        'random_normal': np.random.randn(1000, 10),
        'random_uniform': np.random.uniform(-1, 1, (800, 15)),
        'structured_sine': np.sin(np.linspace(0, 4*np.pi, 500)).reshape(-1, 1),
        'noisy_trend': np.linspace(0, 10, 1000) + 0.5 * np.random.randn(1000),
        'sparse_data': np.zeros((200, 20)),
    }
    
    # Add some structure to sparse data
    test_datasets['sparse_data'][::10, ::5] = np.random.randn(20, 4)
    
    # Create analyzer
    analyzer = AutomatedAnalyzer()
    
    # Test individual analysis (verbose)
    print("\n1. Individual analysis (verbose):")
    individual_result = analyzer.analyze_dataset('test_normal', np.random.randn(100, 5), quiet=False)
    
    # Test batch analysis (quiet)
    print("\n" + "="*60)
    print("2. Batch analysis (quiet):")
    batch_results = analyzer.batch_analysis(test_datasets, quiet=True)
    
    # Generate summary
    analyzer.generate_summary()
    
    # Test mixed mode
    print("\n" + "="*60)
    print("3. Mixed mode analysis:")
    
    print("\nAnalyzing with context manager:")
    with scitex.context.quiet():
        mixed_result = analyzer.analyze_dataset('mixed_mode', np.random.exponential(2, (300, 8)), quiet=False)
    
    print(f"Mixed mode analysis completed for dataset: {mixed_result['dataset_name']}")
    print(f"Dataset shape: {mixed_result['shape']}")
    print(f"Mean: {mixed_result['basic_stats']['mean']:.4f}")

Part 4: Performance and Resource Management
-------------------------------------------

4.1 Performance Comparison with Context Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Performance comparison with context managers
    print("Performance Comparison with Context Managers:")
    print("=" * 47)
    
    import time
    
    def performance_heavy_function(n_iterations=100):
        """A function that does heavy computation with lots of output."""
        results = []
        
        for i in range(n_iterations):
            print(f"Iteration {i+1}/{n_iterations}: Starting computation")
            
            # Heavy computation
            data = np.random.randn(100, 100)
            print(f"  Generated {data.shape[0]}x{data.shape[1]} matrix")
            
            # Matrix operations
            eigenvals = np.linalg.eigvals(data @ data.T)
            print(f"  Computed {len(eigenvals)} eigenvalues")
            
            result = np.sum(eigenvals)
            results.append(result)
            print(f"  Eigenvalue sum: {result:.4f}")
            
            if i % 10 == 9:
                print(f"Completed {i+1} iterations")
        
        print(f"All {n_iterations} iterations completed")
        return results
    
    # Test performance with output
    print("\n1. Performance test with output (10 iterations):")
    start_time = time.time()
    results_with_output = performance_heavy_function(10)
    time_with_output = time.time() - start_time
    print(f"Time with output: {time_with_output:.4f} seconds")
    
    # Test performance without output
    print("\n2. Performance test without output (10 iterations):")
    start_time = time.time()
    with scitex.context.suppress_output():
        results_without_output = performance_heavy_function(10)
    time_without_output = time.time() - start_time
    print(f"Time without output: {time_without_output:.4f} seconds")
    
    # Compare performance
    print(f"\n3. Performance comparison:")
    print(f"With output:    {time_with_output:.4f} seconds")
    print(f"Without output: {time_without_output:.4f} seconds")
    if time_with_output > time_without_output:
        speedup = time_with_output / time_without_output
        print(f"Speedup from suppressing output: {speedup:.2f}x")
        print(f"Time saved: {(time_with_output - time_without_output)*1000:.1f} ms")
    else:
        print("No significant performance difference detected")
    
    # Verify results are identical
    results_match = np.allclose(results_with_output, results_without_output)
    print(f"Results identical: {results_match}")
    
    # Memory usage test
    print("\n4. Memory usage test:")
    
    def memory_intensive_function():
        """Function that creates large objects and prints about them."""
        arrays = []
        
        for i in range(20):
            # Create progressively larger arrays
            size = (i + 1) * 100
            arr = np.random.randn(size, size)
            arrays.append(arr)
            
            memory_usage = sum(a.nbytes for a in arrays) / (1024**2)  # MB
            print(f"Created array {i+1}: {arr.shape}, Memory usage: {memory_usage:.1f} MB")
            
            if i % 5 == 4:
                print(f"Checkpoint: {i+1} arrays created, total memory: {memory_usage:.1f} MB")
        
        total_memory = sum(a.nbytes for a in arrays) / (1024**2)
        print(f"Final memory usage: {total_memory:.1f} MB")
        
        return arrays
    
    # Test memory function with output
    print("\nMemory test with output:")
    start_time = time.time()
    arrays_with_output = memory_intensive_function()
    time_memory_with = time.time() - start_time
    print(f"Memory test with output completed in {time_memory_with:.4f} seconds")
    
    # Clean up
    del arrays_with_output
    
    # Test memory function without output
    print("\nMemory test without output:")
    start_time = time.time()
    with scitex.context.suppress_output():
        arrays_without_output = memory_intensive_function()
    time_memory_without = time.time() - start_time
    print(f"Memory test without output completed in {time_memory_without:.4f} seconds")
    
    # Compare memory test performance
    memory_speedup = time_memory_with / time_memory_without if time_memory_without > 0 else 1
    print(f"Memory test speedup: {memory_speedup:.2f}x")
    
    # Clean up
    del arrays_without_output

4.2 Resource Management and Context Cleanup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Resource management and context cleanup
    print("Resource Management and Context Cleanup:")
    print("=" * 42)
    
    class ResourceManager:
        """Demonstrate resource management with context managers."""
        
        def __init__(self):
            self.resources = []
            self.resource_counter = 0
        
        def create_resource(self, name, size_mb=10):
            """Create a mock resource (large array)."""
            self.resource_counter += 1
            resource_id = f"{name}_{self.resource_counter}"
            
            # Create resource (large array)
            elements = int(size_mb * 1024 * 1024 / 8)  # 8 bytes per float64
            array_size = int(np.sqrt(elements))
            resource_data = np.random.randn(array_size, array_size)
            
            resource = {
                'id': resource_id,
                'name': name,
                'data': resource_data,
                'size_mb': resource_data.nbytes / (1024**2),
                'created_at': time.time()
            }
            
            self.resources.append(resource)
            
            print(f"Created resource: {resource_id} ({resource['size_mb']:.1f} MB)")
            return resource
        
        def cleanup_resources(self):
            """Clean up all resources."""
            total_memory = sum(r['size_mb'] for r in self.resources)
            count = len(self.resources)
            
            print(f"Cleaning up {count} resources ({total_memory:.1f} MB total)")
            
            for resource in self.resources:
                print(f"  Cleaning resource: {resource['id']} ({resource['size_mb']:.1f} MB)")
                del resource['data']  # Free the large array
            
            self.resources.clear()
            print(f"All resources cleaned up")
        
        def get_memory_usage(self):
            """Get current memory usage."""
            total_mb = sum(r['size_mb'] for r in self.resources)
            return total_mb
        
        def resource_intensive_operation(self, n_resources=5):
            """Perform a resource-intensive operation."""
            print(f"Starting resource-intensive operation with {n_resources} resources")
            
            for i in range(n_resources):
                resource = self.create_resource(f"data_array", size_mb=20)
                
                # Simulate processing
                print(f"Processing resource {resource['id']}...")
                
                # Some computation
                mean_value = np.mean(resource['data'])
                std_value = np.std(resource['data'])
                
                print(f"  Mean: {mean_value:.6f}, Std: {std_value:.6f}")
                print(f"  Current memory usage: {self.get_memory_usage():.1f} MB")
                
                if i % 2 == 1:
                    print(f"  Checkpoint: {i+1} resources created")
            
            final_memory = self.get_memory_usage()
            print(f"Operation completed. Final memory usage: {final_memory:.1f} MB")
            
            return final_memory
    
    # Test resource management with output
    print("\n1. Resource management with output:")
    manager1 = ResourceManager()
    memory_used_1 = manager1.resource_intensive_operation(3)
    print(f"Memory used: {memory_used_1:.1f} MB")
    manager1.cleanup_resources()
    
    # Test resource management without output
    print("\n2. Resource management without output:")
    manager2 = ResourceManager()
    
    with scitex.context.suppress_output():
        memory_used_2 = manager2.resource_intensive_operation(3)
    
    print(f"Silent operation completed. Memory used: {memory_used_2:.1f} MB")
    
    # Show current state
    print(f"Resources still in memory: {len(manager2.resources)}")
    print(f"Current memory usage: {manager2.get_memory_usage():.1f} MB")
    
    # Clean up with output
    manager2.cleanup_resources()
    
    # Test context manager exception handling with resources
    print("\n3. Exception handling with resources:")
    
    class SafeResourceManager(ResourceManager):
        """Resource manager with automatic cleanup on exceptions."""
        
        def __enter__(self):
            print("Entering SafeResourceManager context")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                print(f"Exception occurred: {exc_type.__name__}: {exc_val}")
                print("Performing emergency cleanup...")
            else:
                print("Normal exit, performing cleanup...")
            
            self.cleanup_resources()
            print("SafeResourceManager context exited")
            
            # Don't suppress the exception
            return False
    
    # Test normal operation
    print("\nTesting normal operation with SafeResourceManager:")
    with SafeResourceManager() as safe_manager:
        safe_manager.create_resource("test_resource", 5)
        safe_manager.create_resource("another_resource", 5)
        print(f"Created resources, memory usage: {safe_manager.get_memory_usage():.1f} MB")
    
    # Test exception handling
    print("\nTesting exception handling with SafeResourceManager:")
    try:
        with SafeResourceManager() as safe_manager:
            safe_manager.create_resource("test_resource", 5)
            print(f"Memory before exception: {safe_manager.get_memory_usage():.1f} MB")
            
            # Cause an intentional exception
            raise ValueError("Intentional error for testing")
            
    except ValueError as e:
        print(f"Caught exception outside context manager: {e}")
        print("Resources were properly cleaned up despite the exception")
    
    # Test nested context managers
    print("\n4. Nested context managers:")
    
    with SafeResourceManager() as outer_manager:
        outer_manager.create_resource("outer_resource", 10)
        
        print("About to enter quiet zone...")
        with scitex.context.suppress_output():
            outer_manager.create_resource("quiet_resource_1", 10)
            outer_manager.create_resource("quiet_resource_2", 10)
            
            # This output will be suppressed
            print("This message is suppressed")
            print(f"Quiet zone memory: {outer_manager.get_memory_usage():.1f} MB")
        
        print("Exited quiet zone")
        print(f"Final memory before cleanup: {outer_manager.get_memory_usage():.1f} MB")
    
    print("All nested context managers completed successfully")

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive context management
capabilities of the SciTeX context module:

Key Features Covered:
~~~~~~~~~~~~~~~~~~~~~

1. **Output Suppression**: ``suppress_output()`` for clean execution
2. **Quiet Operations**: ``quiet()`` for silent processing
3. **Context Management**: Proper resource handling and cleanup
4. **Exception Safety**: Robust error handling with context managers
5. **Performance Optimization**: Reduced overhead from suppressed output
6. **Nested Contexts**: Complex workflow management
7. **Resource Management**: Memory and resource cleanup
8. **Scientific Applications**: Clean data processing pipelines

Best Practices:
~~~~~~~~~~~~~~~

-  Use **output suppression** for batch processing and automated
   workflows
-  Apply **quiet operations** when running repetitive analyses
-  Implement **proper exception handling** in context managers
-  Use **nested contexts** for complex processing pipelines
-  Apply **resource management** for memory-intensive operations
-  Use **context managers** for temporary state changes
-  Implement **clean interfaces** that can operate in silent mode
-  Consider **performance benefits** of suppressing verbose output

Recommended Workflows:
~~~~~~~~~~~~~~~~~~~~~~

1. **Batch Processing**: Use quiet mode for multiple dataset analysis
2. **Automated Pipelines**: Suppress output during production runs
3. **Interactive Development**: Use normal mode for debugging, quiet for
   final runs
4. **Resource Management**: Implement context managers for cleanup
5. **Performance Optimization**: Profile with and without output
   suppression

Context Manager Patterns:
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   # Basic suppression
   with scitex.context.suppress_output():
       noisy_function()

   # Quiet operations
   with scitex.context.quiet():
       batch_process_data()

   # Resource management
   with ResourceManager() as manager:
       manager.process_data()
       # Automatic cleanup on exit

.. code:: ipython3

    # Cleanup
    import shutil
    
    cleanup = input("Clean up example files? (y/n): ").lower().startswith('y')
    if cleanup:
        shutil.rmtree(data_dir)
        print("✓ Example files cleaned up")
    else:
        print(f"Example files preserved in: {data_dir}")
        if data_dir.exists():
            files = list(data_dir.rglob('*'))
            print(f"Files created: {len([f for f in files if f.is_file()])}")
            print(f"Directories created: {len([d for d in files if d.is_dir()])}")
            
            if files:
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                print(f"Total size: {scitex.str.readable_bytes(total_size)}")
    
    print("\nSciTeX Context Management Tutorial Complete!")
    print("\nKey takeaways:")
    print("- Use suppress_output() for clean automation")
    print("- Apply quiet() for batch processing")
    print("- Implement proper resource management")
    print("- Consider performance benefits of output suppression")
    print("- Use nested contexts for complex workflows")
