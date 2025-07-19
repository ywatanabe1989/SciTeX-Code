03 SciTeX Utils
===============

.. note::
   This page is generated from the Jupyter notebook `03_scitex_utils.ipynb <https://github.com/scitex/scitex/blob/main/examples/03_scitex_utils.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 03_scitex_utils.ipynb


This comprehensive notebook demonstrates the SciTeX utils module
capabilities, covering general utilities for scientific computing,
system operations, and data management.

Features Covered
----------------

Data Compression
~~~~~~~~~~~~~~~~

-  HDF5 compression utilities
-  Storage optimization
-  File size management

Communication
~~~~~~~~~~~~~

-  Email notifications
-  ANSI escape handling
-  System notifications

Grid Operations
~~~~~~~~~~~~~~~

-  Grid counting and generation
-  Parameter space exploration
-  Combinatorial utilities

System Information
~~~~~~~~~~~~~~~~~~

-  Git branch detection
-  Hostname and user information
-  Environment detection

Search and Analysis
~~~~~~~~~~~~~~~~~~~

-  Advanced search capabilities
-  Content analysis
-  Data exploration

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import matplotlib.pyplot as plt
    import tempfile
    import os
    import time
    
    # Set up example data directory
    data_dir = Path("./utils_examples")
    data_dir.mkdir(exist_ok=True)
    
    print("SciTeX Utils Module Tutorial - Ready to begin!")
    print(f"Available utils functions: {len(scitex.utils.__all__)}")
    print(f"Functions: {scitex.utils.__all__}")

Part 1: System Information and Environment
------------------------------------------

1.1 System Information Gathering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # System information gathering
    print("System Information:")
    print("=" * 22)
    
    try:
        # Get hostname
        hostname = scitex.utils.get_hostname()
        print(f"Hostname: {hostname}")
    except Exception as e:
        print(f"Error getting hostname: {e}")
    
    try:
        # Get username
        username = scitex.utils.get_username()
        print(f"Username: {username}")
    except Exception as e:
        print(f"Error getting username: {e}")
    
    try:
        # Get git branch
        git_branch = scitex.utils.get_git_branch()
        print(f"Git branch: {git_branch}")
    except Exception as e:
        print(f"Error getting git branch: {e}")
    
    # Generate footer with system info
    try:
        footer = scitex.utils.gen_footer()
        print(f"\nGenerated footer:")
        print(footer)
    except Exception as e:
        print(f"Error generating footer: {e}")
    
    # Additional system information
    print("\nAdditional System Info:")
    print("=" * 25)
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Process ID: {os.getpid()}")
    
    # Environment variables (selected)
    env_vars = ['HOME', 'USER', 'PATH', 'SHELL', 'LANG']
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        # Truncate PATH for readability
        if var == 'PATH' and len(value) > 100:
            value = value[:100] + '...'
        print(f"  {var}: {value}")

1.2 Notification System
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Notification system demonstration
    print("Notification System:")
    print("=" * 22)
    
    # Test notification with different messages
    notification_tests = [
        {
            'message': 'Test notification from SciTeX utils',
            'level': 'info'
        },
        {
            'message': 'Computation completed successfully',
            'level': 'success'
        },
        {
            'message': 'Warning: Low memory detected',
            'level': 'warning'
        },
        {
            'message': 'Error: Unable to process data',
            'level': 'error'
        }
    ]
    
    for test in notification_tests:
        try:
            print(f"\nSending {test['level']} notification...")
            result = scitex.utils.notify(
                message=test['message'],
                level=test['level']
            )
            print(f"Notification sent: {result}")
        except Exception as e:
            print(f"Notification failed: {e}")
    
    # ANSI escape sequence handling
    print("\nANSI Escape Handling:")
    print("=" * 25)
    
    ansi_test_strings = [
        "\033[31mRed text\033[0m",
        "\033[1;32mBold green text\033[0m",
        "\033[4;34mUnderlined blue text\033[0m",
        "Normal text without ANSI",
        "\033[91mBright red\033[0m mixed with \033[92mgreen\033[0m"
    ]
    
    for test_string in ansi_test_strings:
        try:
            cleaned = scitex.utils.ansi_escape(test_string)
            print(f"Original: '{test_string}'")
            print(f"Cleaned:  '{cleaned}'")
            print()
        except Exception as e:
            print(f"ANSI escape error: {e}")

Part 2: Grid Operations and Parameter Space
-------------------------------------------

2.1 Grid Generation and Counting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Grid operations for parameter space exploration
    print("Grid Operations:")
    print("=" * 18)
    
    # Define parameter spaces for different scenarios
    parameter_spaces = {
        'machine_learning': {
            'learning_rate': [0.001, 0.01, 0.1],
            'batch_size': [16, 32, 64, 128],
            'dropout': [0.2, 0.3, 0.5],
            'epochs': [50, 100, 200]
        },
        'signal_processing': {
            'window_size': [64, 128, 256, 512],
            'overlap': [0.25, 0.5, 0.75],
            'filter_type': ['lowpass', 'highpass', 'bandpass'],
            'cutoff_freq': [0.1, 0.2, 0.3, 0.4, 0.5]
        },
        'optimization': {
            'algorithm': ['gradient_descent', 'adam', 'rmsprop'],
            'momentum': [0.9, 0.95, 0.99],
            'weight_decay': [0.0, 1e-4, 1e-3, 1e-2]
        }
    }
    
    # Count grids for each parameter space
    for space_name, params in parameter_spaces.items():
        try:
            grid_count = scitex.utils.count_grids(params)
            print(f"\n{space_name.replace('_', ' ').title()} Parameter Space:")
            print(f"  Parameters: {list(params.keys())}")
            print(f"  Parameter counts: {[len(v) for v in params.values()]}")
            print(f"  Total combinations: {grid_count}")
            
            # Show size of each parameter
            for param_name, param_values in params.items():
                print(f"    {param_name}: {len(param_values)} values")
                
        except Exception as e:
            print(f"Error counting grids for {space_name}: {e}")
    
    # Demonstrate memory estimation for large parameter spaces
    print("\nMemory Estimation for Large Spaces:")
    print("=" * 38)
    
    large_spaces = {
        'image_processing': {
            'kernel_size': list(range(3, 16, 2)),  # 3, 5, 7, 9, 11, 13, 15
            'stride': [1, 2, 3, 4],
            'padding': [0, 1, 2],
            'dilation': [1, 2, 3],
            'activation': ['relu', 'tanh', 'sigmoid', 'leaky_relu', 'elu']
        },
        'hyperparameter_search': {
            'num_layers': list(range(1, 11)),  # 1 to 10
            'hidden_units': [32, 64, 128, 256, 512, 1024],
            'learning_rate': [10**(-i) for i in range(1, 7)],  # 0.1 to 0.000001
            'regularization': [0.0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
        }
    }
    
    for space_name, params in large_spaces.items():
        try:
            grid_count = scitex.utils.count_grids(params)
            
            # Estimate memory usage (rough calculation)
            # Assume each parameter combination takes ~100 bytes
            estimated_memory = grid_count * 100
            readable_memory = scitex.str.readable_bytes(estimated_memory)
            
            print(f"\n{space_name.replace('_', ' ').title()}:")
            print(f"  Total combinations: {grid_count:,}")
            print(f"  Estimated memory: {readable_memory}")
            
            if grid_count > 1000000:
                print(f"  ⚠️  Very large parameter space - consider reduction!")
            elif grid_count > 100000:
                print(f"  ⚠️  Large parameter space - may require distributed computing")
            else:
                print(f"  ✓ Manageable parameter space size")
                
        except Exception as e:
            print(f"Error analyzing {space_name}: {e}")

2.2 Grid Generation and Iteration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Grid generation for parameter exploration
    print("Grid Generation and Iteration:")
    print("=" * 33)
    
    # Small parameter space for demonstration
    demo_params = {
        'learning_rate': [0.01, 0.1],
        'batch_size': [32, 64],
        'optimizer': ['adam', 'sgd']
    }
    
    print(f"Demo parameter space: {demo_params}")
    print(f"Expected combinations: {scitex.utils.count_grids(demo_params)}")
    print("\nGenerated parameter combinations:")
    
    try:
        # Generate all combinations
        combination_count = 0
        for combination in scitex.utils.yield_grids(demo_params):
            combination_count += 1
            print(f"  {combination_count}: {combination}")
        
        print(f"\nTotal generated: {combination_count} combinations")
        
    except Exception as e:
        print(f"Error generating grids: {e}")
    
    # Larger example with sampling
    print("\nLarge Grid Sampling:")
    print("=" * 22)
    
    large_params = {
        'alpha': [0.1, 0.2, 0.3, 0.4, 0.5],
        'beta': [0.01, 0.05, 0.1, 0.2],
        'gamma': [0.9, 0.95, 0.99, 0.999],
        'method': ['A', 'B', 'C']
    }
    
    total_combinations = scitex.utils.count_grids(large_params)
    print(f"Large parameter space: {total_combinations} total combinations")
    print("\nSampling first 10 combinations:")
    
    try:
        sample_count = 0
        for combination in scitex.utils.yield_grids(large_params):
            sample_count += 1
            print(f"  {sample_count}: {combination}")
            
            if sample_count >= 10:
                print(f"  ... and {total_combinations - 10} more combinations")
                break
                
    except Exception as e:
        print(f"Error sampling grids: {e}")
    
    # Practical application: Hyperparameter optimization simulation
    print("\nHyperparameter Optimization Simulation:")
    print("=" * 42)
    
    # Simulate evaluating different hyperparameter combinations
    optimization_params = {
        'learning_rate': [0.001, 0.01, 0.1],
        'hidden_units': [64, 128, 256],
        'dropout': [0.2, 0.3, 0.5]
    }
    
    def simulate_model_performance(params):
        """Simulate model performance based on hyperparameters."""
        # Simulate some realistic performance based on parameters
        base_score = 0.7
        
        # Learning rate effect
        if params['learning_rate'] == 0.01:
            base_score += 0.1
        elif params['learning_rate'] == 0.1:
            base_score -= 0.05
        
        # Hidden units effect
        if params['hidden_units'] == 128:
            base_score += 0.05
        elif params['hidden_units'] == 256:
            base_score += 0.02
        
        # Dropout effect
        if params['dropout'] == 0.3:
            base_score += 0.03
        
        # Add some random noise
        import random
        noise = random.uniform(-0.05, 0.05)
        
        return min(1.0, max(0.0, base_score + noise))
    
    # Run optimization simulation
    results = []
    total_combinations = scitex.utils.count_grids(optimization_params)
    
    print(f"Running optimization over {total_combinations} combinations...")
    
    for i, params in enumerate(scitex.utils.yield_grids(optimization_params), 1):
        performance = simulate_model_performance(params)
        results.append({
            'combination': i,
            'params': params.copy(),
            'performance': performance
        })
        print(f"  {i}/{total_combinations}: {params} -> {performance:.4f}")
    
    # Find best combination
    best_result = max(results, key=lambda x: x['performance'])
    print(f"\nBest combination:")
    print(f"  Parameters: {best_result['params']}")
    print(f"  Performance: {best_result['performance']:.4f}")
    
    # Performance statistics
    performances = [r['performance'] for r in results]
    print(f"\nPerformance Statistics:")
    print(f"  Mean: {np.mean(performances):.4f}")
    print(f"  Std:  {np.std(performances):.4f}")
    print(f"  Min:  {np.min(performances):.4f}")
    print(f"  Max:  {np.max(performances):.4f}")

Part 3: Data Compression and Storage
------------------------------------

3.1 HDF5 Compression
~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # HDF5 compression demonstration
    print("HDF5 Compression:")
    print("=" * 20)
    
    # Create test data for compression
    compression_test_dir = data_dir / "compression_tests"
    compression_test_dir.mkdir(exist_ok=True)
    
    # Generate different types of data
    test_datasets = {
        'random_data': np.random.randn(1000, 100),
        'structured_data': np.tile(np.arange(100), (1000, 1)),
        'sparse_data': np.zeros((1000, 100)),
        'time_series': np.sin(np.linspace(0, 100*np.pi, 10000)).reshape(100, 100),
        'image_like': np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    }
    
    # Add some structure to sparse data
    test_datasets['sparse_data'][::10, ::10] = 1.0
    
    print("Test datasets created:")
    for name, data in test_datasets.items():
        print(f"  {name}: shape {data.shape}, dtype {data.dtype}")
    
    # Test HDF5 compression if h5py is available
    try:
        import h5py
        
        # Create uncompressed HDF5 files
        uncompressed_files = {}
        compressed_files = {}
        
        for name, data in test_datasets.items():
            # Uncompressed file
            uncompressed_file = compression_test_dir / f"{name}_uncompressed.h5"
            with h5py.File(uncompressed_file, 'w') as f:
                f.create_dataset('data', data=data)
            uncompressed_files[name] = uncompressed_file
            
            # Compressed file
            compressed_file = compression_test_dir / f"{name}_compressed.h5"
            with h5py.File(compressed_file, 'w') as f:
                f.create_dataset('data', data=data, compression='gzip', compression_opts=9)
            compressed_files[name] = compressed_file
        
        # Test scitex compression utility
        print("\nTesting SciTeX HDF5 compression:")
        for name, uncompressed_file in uncompressed_files.items():
            try:
                scitex_compressed_file = compression_test_dir / f"{name}_scitex_compressed.h5"
                
                # Use scitex compression
                result = scitex.utils.compress_hdf5(
                    str(uncompressed_file), 
                    str(scitex_compressed_file)
                )
                
                print(f"  {name}: SciTeX compression result - {result}")
                
            except Exception as e:
                print(f"  {name}: SciTeX compression error - {e}")
        
        # Compare file sizes
        print("\nFile size comparison:")
        print("=" * 25)
        
        for name in test_datasets.keys():
            print(f"\n{name}:")
            
            # Uncompressed size
            if name in uncompressed_files:
                uncompressed_size = uncompressed_files[name].stat().st_size
                print(f"  Uncompressed: {scitex.str.readable_bytes(uncompressed_size)}")
            
            # Compressed size
            if name in compressed_files:
                compressed_size = compressed_files[name].stat().st_size
                print(f"  Compressed:   {scitex.str.readable_bytes(compressed_size)}")
                
                if name in uncompressed_files:
                    compression_ratio = uncompressed_size / compressed_size
                    space_saved = (1 - compressed_size / uncompressed_size) * 100
                    print(f"  Ratio: {compression_ratio:.2f}x, Space saved: {space_saved:.1f}%")
            
            # SciTeX compressed size
            scitex_file = compression_test_dir / f"{name}_scitex_compressed.h5"
            if scitex_file.exists():
                scitex_size = scitex_file.stat().st_size
                print(f"  SciTeX:       {scitex.str.readable_bytes(scitex_size)}")
        
    except ImportError:
        print("h5py not available - skipping HDF5 compression tests")
    except Exception as e:
        print(f"HDF5 compression test error: {e}")

Part 4: Search and Analysis Utilities
-------------------------------------

4.1 Advanced Search Capabilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Advanced search utilities
    print("Advanced Search Utilities:")
    print("=" * 28)
    
    # Create test data for searching
    search_test_dir = data_dir / "search_tests"
    search_test_dir.mkdir(exist_ok=True)
    
    # Create test files with different content types
    test_files_content = {
        'experiment_log.txt': '''
    Experiment Log - Neural Network Training
    Date: 2024-01-15
    Model: ResNet-50
    Dataset: ImageNet subset
    Hyperparameters:
      learning_rate: 0.001
      batch_size: 32
      epochs: 100
      optimizer: Adam
    Results:
      Training accuracy: 0.945
      Validation accuracy: 0.892
      Test accuracy: 0.885
      Training time: 2.5 hours
    Notes: Model converged successfully
    ''',
        'data_analysis.py': '''
    #!/usr/bin/env python3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    def load_data(filename):
        """Load data from CSV file."""
        return pd.read_csv(filename)
    
    def analyze_performance(data):
        """Analyze model performance metrics."""
        accuracy = data['accuracy'].mean()
        precision = data['precision'].mean()
        recall = data['recall'].mean()
        return accuracy, precision, recall
    
    if __name__ == "__main__":
        data = load_data("results.csv")
        metrics = analyze_performance(data)
        print(f"Performance: {metrics}")
    ''',
        'config.json': '''
    {
      "model": {
        "type": "neural_network",
        "architecture": "resnet50",
        "input_size": [224, 224, 3],
        "num_classes": 1000
      },
      "training": {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 100,
        "optimizer": "adam",
        "loss_function": "categorical_crossentropy"
      },
      "data": {
        "train_path": "/data/train",
        "val_path": "/data/validation",
        "test_path": "/data/test",
        "augmentation": true
      }
    }
    ''',
        'results.csv': '''
    epoch,accuracy,precision,recall,loss,val_accuracy,val_loss
    1,0.234,0.245,0.223,2.345,0.245,2.234
    2,0.345,0.356,0.334,1.876,0.356,1.765
    3,0.456,0.467,0.445,1.543,0.467,1.432
    4,0.567,0.578,0.556,1.234,0.578,1.123
    5,0.678,0.689,0.667,0.987,0.689,0.876
    ''',
        'readme.md': '''
    # Machine Learning Project
    
    This project implements a deep learning model for image classification.
    
    ## Features
    - ResNet-50 architecture
    - Data augmentation
    - Transfer learning
    - Performance monitoring
    
    ## Usage
    ```python
    python train.py --config config.json
    ```
    
    ## Results
    - Accuracy: 88.5%
    - Precision: 87.2%
    - Recall: 86.8%
    '''
    }
    
    # Create test files
    for filename, content in test_files_content.items():
        filepath = search_test_dir / filename
        filepath.write_text(content.strip())
    
    print(f"Created {len(test_files_content)} test files:")
    for filename in test_files_content.keys():
        filepath = search_test_dir / filename
        size = filepath.stat().st_size
        print(f"  {filename}: {scitex.str.readable_bytes(size)}")
    
    # Test search functionality
    print("\nSearch Tests:")
    print("=" * 15)
    
    search_queries = [
        {
            'query': 'accuracy',
            'description': 'Find files containing "accuracy"'
        },
        {
            'query': 'learning_rate',
            'description': 'Find files containing "learning_rate"'
        },
        {
            'query': 'ResNet',
            'description': 'Find files containing "ResNet"'
        },
        {
            'query': 'import.*pandas',
            'description': 'Find files with pandas import (regex)'
        },
        {
            'query': '0\.[0-9]+',
            'description': 'Find files with decimal numbers (regex)'
        }
    ]
    
    for search_test in search_queries:
        try:
            print(f"\n{search_test['description']}:")
            print(f"Query: '{search_test['query']}'")
            
            # Search using scitex.utils.search
            search_results = scitex.utils.search(
                pattern=search_test['query'],
                directory=str(search_test_dir)
            )
            
            if search_results:
                print(f"Found in {len(search_results)} locations:")
                for result in search_results:
                    print(f"  {result}")
            else:
                print("  No matches found")
                
        except Exception as e:
            print(f"  Search error: {e}")
    
    # File content analysis
    print("\nFile Content Analysis:")
    print("=" * 25)
    
    for filename, content in test_files_content.items():
        print(f"\n{filename}:")
        
        # Basic statistics
        lines = content.split('\n')
        words = content.split()
        chars = len(content)
        
        print(f"  Lines: {len(lines)}")
        print(f"  Words: {len(words)}")
        print(f"  Characters: {chars}")
        
        # Find numbers in content
        import re
        numbers = re.findall(r'\b\d+\.\d+\b|\b\d+\b', content)
        if numbers:
            print(f"  Numbers found: {len(numbers)} ({numbers[:5]}{'...' if len(numbers) > 5 else ''})")
        
        # Find common keywords
        keywords = ['accuracy', 'model', 'data', 'training', 'learning', 'neural', 'network']
        found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
        if found_keywords:
            print(f"  Keywords: {found_keywords}")

Part 5: Email and Communication
-------------------------------

5.1 Email Utilities (Demonstration)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Email utilities demonstration (without actually sending emails)
    print("Email Utilities Demonstration:")
    print("=" * 33)
    
    # Note: We won't actually send emails in this demo
    print("Note: This is a demonstration only - no actual emails will be sent.\n")
    
    # Email configuration examples
    email_configs = {
        'experiment_completion': {
            'subject': 'Experiment Completed Successfully',
            'body': '''
    Dear Researcher,
    
    Your machine learning experiment has completed successfully.
    
    Results Summary:
    - Training Accuracy: 94.5%
    - Validation Accuracy: 89.2%
    - Training Time: 2.5 hours
    - Model Size: 45.2 MB
    
    The trained model has been saved to:
    /models/experiment_20240115_142330.pkl
    
    Detailed logs are available in:
    /logs/training_20240115.log
    
    Best regards,
    Automated Training System
    ''',
            'priority': 'normal'
        },
        'error_notification': {
            'subject': 'URGENT: Training Failed - Action Required',
            'body': '''
    ATTENTION: Your machine learning experiment has failed.
    
    Error Details:
    - Error Type: OutOfMemoryError
    - Error Message: CUDA out of memory
    - Batch Size: 128 (consider reducing)
    - Model: ResNet-50
    - Epoch: 15/100
    
    Suggested Actions:
    1. Reduce batch size to 64 or 32
    2. Use gradient accumulation
    3. Enable mixed precision training
    4. Use a smaller model variant
    
    Error log: /logs/error_20240115_143045.log
    
    Please restart the training with adjusted parameters.
    
    Automated Training System
    ''',
            'priority': 'high'
        },
        'weekly_summary': {
            'subject': 'Weekly Training Summary',
            'body': '''
    Weekly Training Summary (Week of Jan 15-21, 2024)
    
    Experiments Completed: 12
    Success Rate: 91.7% (11/12)
    Total Training Time: 18.5 hours
    Best Model Accuracy: 96.2%
    
    Top Performing Models:
    1. ResNet-101: 96.2% accuracy
    2. EfficientNet-B4: 95.8% accuracy
    3. DenseNet-121: 94.9% accuracy
    
    Resource Usage:
    - GPU Hours: 18.5
    - Storage Used: 2.3 GB
    - Models Saved: 11
    
    Upcoming Experiments:
    - Vision Transformer evaluation
    - Hyperparameter optimization
    - Cross-validation study
    
    Have a great week!
    Training Management System
    ''',
            'priority': 'low'
        }
    }
    
    # Demonstrate email preparation
    for email_type, config in email_configs.items():
        print(f"Email Type: {email_type.replace('_', ' ').title()}")
        print(f"Priority: {config['priority'].upper()}")
        print(f"Subject: {config['subject']}")
        print(f"Body length: {len(config['body'])} characters")
        print(f"Body lines: {len(config['body'].split())} words")
        
        # Show email preview (first few lines)
        body_lines = config['body'].strip().split('\n')
        preview_lines = body_lines[:3]
        print(f"Preview: {' '.join(preview_lines)}...")
        print()
    
    # Email sending function demonstration (mock)
    def mock_send_email(subject, body, recipient, priority='normal'):
        """Mock email sending function for demonstration."""
        print(f"[MOCK EMAIL SEND]")
        print(f"  To: {recipient}")
        print(f"  Subject: {subject}")
        print(f"  Priority: {priority}")
        print(f"  Body size: {len(body)} chars")
        print(f"  Status: Would be sent successfully")
        return True
    
    # Demonstrate email sending workflow
    print("Email Sending Workflow Demo:")
    print("=" * 30)
    
    recipients = [
        'researcher@university.edu',
        'admin@lab.org',
        'team@company.com'
    ]
    
    # Simulate sending different types of notifications
    notification_scenarios = [
        {
            'trigger': 'experiment_completed',
            'email_type': 'experiment_completion',
            'recipient': 'researcher@university.edu'
        },
        {
            'trigger': 'training_failed',
            'email_type': 'error_notification',
            'recipient': 'admin@lab.org'
        },
        {
            'trigger': 'weekly_report',
            'email_type': 'weekly_summary',
            'recipient': 'team@company.com'
        }
    ]
    
    for scenario in notification_scenarios:
        email_config = email_configs[scenario['email_type']]
        
        print(f"\nScenario: {scenario['trigger']}")
        print(f"Triggered email type: {scenario['email_type']}")
        
        # Simulate email sending
        try:
            # In a real implementation, you would use scitex.utils.send_gmail here
            result = mock_send_email(
                subject=email_config['subject'],
                body=email_config['body'],
                recipient=scenario['recipient'],
                priority=email_config['priority']
            )
            print(f"Email sent successfully: {result}")
            
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    print("\nNote: To use actual email sending, configure scitex.utils.send_gmail() with:")
    print("- Gmail credentials")
    print("- App password or OAuth")
    print("- Recipient addresses")
    print("- SMTP server settings")

Part 6: Practical Applications
------------------------------

6.1 Experiment Management System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Comprehensive experiment management system
    class ExperimentManager:
        def __init__(self, base_dir):
            self.base_dir = Path(base_dir)
            self.base_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            self.experiments_dir = self.base_dir / "experiments"
            self.logs_dir = self.base_dir / "logs"
            self.results_dir = self.base_dir / "results"
            
            for dir_path in [self.experiments_dir, self.logs_dir, self.results_dir]:
                dir_path.mkdir(exist_ok=True)
            
            self.experiment_history = []
        
        def create_experiment(self, name, parameters):
            """Create a new experiment configuration."""
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            experiment_id = f"{name}_{timestamp}"
            
            experiment = {
                'id': experiment_id,
                'name': name,
                'parameters': parameters,
                'created': timestamp,
                'status': 'created',
                'results': None,
                'log_file': self.logs_dir / f"{experiment_id}.log",
                'results_file': self.results_dir / f"{experiment_id}_results.json"
            }
            
            # Save experiment configuration
            config_file = self.experiments_dir / f"{experiment_id}_config.json"
            import json
            with open(config_file, 'w') as f:
                json.dump(experiment, f, indent=2, default=str)
            
            self.experiment_history.append(experiment)
            
            print(f"Created experiment: {experiment_id}")
            return experiment
        
        def run_parameter_sweep(self, base_name, parameter_space):
            """Run experiments for all parameter combinations."""
            print(f"Starting parameter sweep: {base_name}")
            
            # Count total combinations
            total_combinations = scitex.utils.count_grids(parameter_space)
            print(f"Total parameter combinations: {total_combinations}")
            
            # Generate experiments
            experiments = []
            for i, params in enumerate(scitex.utils.yield_grids(parameter_space), 1):
                experiment_name = f"{base_name}_run_{i:03d}"
                experiment = self.create_experiment(experiment_name, params)
                experiments.append(experiment)
                
                # Simulate running the experiment
                self.simulate_experiment_run(experiment)
            
            print(f"\nParameter sweep completed: {len(experiments)} experiments")
            return experiments
        
        def simulate_experiment_run(self, experiment):
            """Simulate running an experiment."""
            import random
            import time
            
            # Simulate some processing time
            time.sleep(0.1)
            
            # Update status
            experiment['status'] = 'running'
            
            # Write to log file
            with open(experiment['log_file'], 'w') as f:
                f.write(f"Experiment: {experiment['id']}\n")
                f.write(f"Parameters: {experiment['parameters']}\n")
                f.write(f"Status: {experiment['status']}\n")
                f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Simulate results based on parameters
            base_performance = 0.7
            
            # Add parameter-based adjustments
            params = experiment['parameters']
            if 'learning_rate' in params:
                if params['learning_rate'] == 0.01:
                    base_performance += 0.1
                elif params['learning_rate'] == 0.1:
                    base_performance -= 0.05
            
            if 'batch_size' in params:
                if params['batch_size'] == 64:
                    base_performance += 0.05
            
            # Add random variation
            performance = base_performance + random.uniform(-0.1, 0.1)
            performance = max(0.0, min(1.0, performance))
            
            # Create results
            results = {
                'accuracy': performance,
                'precision': performance * random.uniform(0.9, 1.1),
                'recall': performance * random.uniform(0.9, 1.1),
                'training_time': random.uniform(30, 120),  # seconds
                'memory_usage': random.uniform(500, 2000),  # MB
                'converged': performance > 0.6
            }
            
            # Clamp precision and recall
            results['precision'] = max(0.0, min(1.0, results['precision']))
            results['recall'] = max(0.0, min(1.0, results['recall']))
            
            experiment['results'] = results
            experiment['status'] = 'completed' if results['converged'] else 'failed'
            
            # Save results
            import json
            with open(experiment['results_file'], 'w') as f:
                json.dump(results, f, indent=2)
            
            # Update log
            with open(experiment['log_file'], 'a') as f:
                f.write(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Results: {results}\n")
                f.write(f"Final status: {experiment['status']}\n")
        
        def analyze_results(self):
            """Analyze results across all experiments."""
            print("\nExperiment Results Analysis:")
            print("=" * 30)
            
            if not self.experiment_history:
                print("No experiments to analyze")
                return
            
            # Filter completed experiments
            completed = [e for e in self.experiment_history if e['status'] == 'completed']
            failed = [e for e in self.experiment_history if e['status'] == 'failed']
            
            print(f"Total experiments: {len(self.experiment_history)}")
            print(f"Completed: {len(completed)}")
            print(f"Failed: {len(failed)}")
            print(f"Success rate: {len(completed)/len(self.experiment_history)*100:.1f}%")
            
            if completed:
                # Performance statistics
                accuracies = [e['results']['accuracy'] for e in completed]
                training_times = [e['results']['training_time'] for e in completed]
                memory_usage = [e['results']['memory_usage'] for e in completed]
                
                print(f"\nPerformance Statistics:")
                print(f"  Accuracy - Mean: {np.mean(accuracies):.4f}, Std: {np.std(accuracies):.4f}")
                print(f"  Best accuracy: {np.max(accuracies):.4f}")
                print(f"  Worst accuracy: {np.min(accuracies):.4f}")
                print(f"  Training time - Mean: {np.mean(training_times):.1f}s")
                print(f"  Memory usage - Mean: {np.mean(memory_usage):.1f}MB")
                
                # Find best experiment
                best_experiment = max(completed, key=lambda x: x['results']['accuracy'])
                print(f"\nBest Experiment: {best_experiment['id']}")
                print(f"  Parameters: {best_experiment['parameters']}")
                print(f"  Accuracy: {best_experiment['results']['accuracy']:.4f}")
                
            # Storage analysis
            total_log_size = sum(f.stat().st_size for f in self.logs_dir.rglob('*.log'))
            total_results_size = sum(f.stat().st_size for f in self.results_dir.rglob('*.json'))
            total_config_size = sum(f.stat().st_size for f in self.experiments_dir.rglob('*.json'))
            
            print(f"\nStorage Usage:")
            print(f"  Logs: {scitex.str.readable_bytes(total_log_size)}")
            print(f"  Results: {scitex.str.readable_bytes(total_results_size)}")
            print(f"  Configs: {scitex.str.readable_bytes(total_config_size)}")
            print(f"  Total: {scitex.str.readable_bytes(total_log_size + total_results_size + total_config_size)}")
        
        def generate_summary_report(self):
            """Generate a comprehensive summary report."""
            report_file = self.base_dir / "experiment_summary.txt"
            
            with open(report_file, 'w') as f:
                f.write("EXPERIMENT SUMMARY REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # System information
                f.write("System Information:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Hostname: {scitex.utils.get_hostname()}\n")
                f.write(f"Username: {scitex.utils.get_username()}\n")
                f.write(f"Git branch: {scitex.utils.get_git_branch()}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Experiment statistics
                completed = [e for e in self.experiment_history if e['status'] == 'completed']
                
                f.write("Experiment Statistics:\n")
                f.write("-" * 22 + "\n")
                f.write(f"Total experiments: {len(self.experiment_history)}\n")
                f.write(f"Completed: {len(completed)}\n")
                f.write(f"Success rate: {len(completed)/len(self.experiment_history)*100:.1f}%\n\n")
                
                if completed:
                    accuracies = [e['results']['accuracy'] for e in completed]
                    f.write(f"Best accuracy: {np.max(accuracies):.4f}\n")
                    f.write(f"Mean accuracy: {np.mean(accuracies):.4f}\n")
                    f.write(f"Std accuracy: {np.std(accuracies):.4f}\n\n")
                    
                    # Top experiments
                    top_experiments = sorted(completed, key=lambda x: x['results']['accuracy'], reverse=True)[:3]
                    f.write("Top 3 Experiments:\n")
                    f.write("-" * 18 + "\n")
                    for i, exp in enumerate(top_experiments, 1):
                        f.write(f"{i}. {exp['id']} - Accuracy: {exp['results']['accuracy']:.4f}\n")
                        f.write(f"   Parameters: {exp['parameters']}\n")
                
                # Footer
                f.write("\n" + scitex.utils.gen_footer())
            
            print(f"\nSummary report saved to: {report_file}")
            return report_file
    
    # Test the experiment management system
    experiment_manager = ExperimentManager(data_dir / "experiment_management")
    
    # Define parameter space for hyperparameter optimization
    hyperparameter_space = {
        'learning_rate': [0.001, 0.01, 0.1],
        'batch_size': [32, 64, 128],
        'optimizer': ['adam', 'sgd']
    }
    
    # Run parameter sweep
    experiments = experiment_manager.run_parameter_sweep(
        "neural_network_optimization",
        hyperparameter_space
    )
    
    # Analyze results
    experiment_manager.analyze_results()
    
    # Generate summary report
    report_file = experiment_manager.generate_summary_report()
    
    # Show report content
    with open(report_file, 'r') as f:
        report_content = f.read()
        print(f"\nReport content preview:")
        print("=" * 30)
        print(report_content[:500] + "..." if len(report_content) > 500 else report_content)

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive utility capabilities of the
SciTeX utils module:

Key Features Covered:
~~~~~~~~~~~~~~~~~~~~~

1. **System Information**: ``get_hostname()``, ``get_username()``,
   ``get_git_branch()``, ``gen_footer()``
2. **Grid Operations**: ``count_grids()``, ``yield_grids()`` for
   parameter space exploration
3. **Data Compression**: ``compress_hdf5()`` for storage optimization
4. **Communication**: ``send_gmail()``, ``notify()``, ``ansi_escape()``
   for notifications
5. **Search Utilities**: ``search()`` for advanced content analysis
6. **Experiment Management**: Comprehensive parameter sweep and result
   analysis
7. **File Management**: Automated logging and result storage
8. **Report Generation**: Summary reports with system information

Best Practices:
~~~~~~~~~~~~~~~

-  Use **grid operations** for systematic parameter space exploration
-  Apply **HDF5 compression** for large dataset storage
-  Implement **notification systems** for long-running experiments
-  Use **search utilities** for comprehensive data analysis
-  Create **experiment management** systems for reproducible research
-  Generate **automated reports** with system information
-  Use **system information** functions for environment tracking
-  Implement **proper logging** for experiment tracking

Recommended Workflows:
~~~~~~~~~~~~~~~~~~~~~~

1. **Hyperparameter Optimization**: Use grid operations with experiment
   management
2. **Data Storage**: Apply compression utilities for large datasets
3. **Result Analysis**: Use search utilities for pattern detection
4. **Communication**: Set up notification systems for experiment
   completion
5. **Documentation**: Generate automated reports with system context

.. code:: ipython3

    # Cleanup
    import shutil
    
    cleanup = input("Clean up example files? (y/n): ").lower().startswith('y')
    if cleanup:
        shutil.rmtree(data_dir)
        print("✓ Example files cleaned up")
    else:
        print(f"Example files preserved in: {data_dir}")
        print(f"Directories created: {len([d for d in data_dir.rglob('*') if d.is_dir()])}")
        print(f"Files created: {len([f for f in data_dir.rglob('*') if f.is_file()])}")
        total_size = sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file())
        print(f"Total size: {scitex.str.readable_bytes(total_size)}")
        
        # Show structure
        print(f"\nCreated structure:")
        for item in sorted(data_dir.rglob('*')):
            if item.is_dir():
                print(f"  📁 {item.relative_to(data_dir)}/")
            else:
                size = scitex.str.readable_bytes(item.stat().st_size)
                print(f"  📄 {item.relative_to(data_dir)} ({size})")
