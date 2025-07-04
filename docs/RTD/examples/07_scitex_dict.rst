07 SciTeX Dict
==============

.. note::
   This page is generated from the Jupyter notebook `07_scitex_dict.ipynb <https://github.com/scitex/scitex/blob/main/examples/07_scitex_dict.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 07_scitex_dict.ipynb


This comprehensive notebook demonstrates the SciTeX dictionary utilities
module, covering advanced dictionary operations, data structures, and
utilities for scientific computing.

Features Covered
----------------

Core Dictionary Classes
~~~~~~~~~~~~~~~~~~~~~~~

-  DotDict - Attribute-style access to dictionary keys
-  listed_dict - Dictionary with automatic list initialization

Dictionary Operations
~~~~~~~~~~~~~~~~~~~~~

-  safe_merge - Merge dictionaries with conflict detection
-  pop_keys - Remove specified keys from key lists
-  replace - String replacement using dictionaries
-  to_str - Convert dictionaries to string representations

Use Cases
~~~~~~~~~

-  Configuration management
-  Data aggregation and collection
-  Parameter handling for scientific experiments
-  Template processing and string manipulation

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import json
    import random
    from collections import defaultdict
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    print("SciTeX Dictionary Utilities Tutorial - Ready to begin!")

Part 1: DotDict - Attribute-Style Dictionary Access
---------------------------------------------------

1.1 Basic DotDict Usage
~~~~~~~~~~~~~~~~~~~~~~~

The DotDict class allows you to access dictionary keys as attributes,
making code more readable and intuitive:

.. code:: ipython3

    # Create a DotDict from a regular dictionary
    config_data = {
        'experiment_name': 'neural_network_training',
        'model_params': {
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 100,
            'hidden_layers': [128, 64, 32]
        },
        'data_params': {
            'train_split': 0.8,
            'validation_split': 0.1,
            'test_split': 0.1
        },
        'output_dir': '/tmp/experiment_results',
        'random_seed': 42
    }
    
    # Convert to DotDict
    config = scitex.dict.DotDict(config_data)
    
    # Access using dot notation
    print(f"Experiment name: {config.experiment_name}")
    print(f"Learning rate: {config.model_params.learning_rate}")
    print(f"Hidden layers: {config.model_params.hidden_layers}")
    print(f"Train split: {config.data_params.train_split}")
    
    # Also supports traditional dictionary access
    print(f"\nUsing bracket notation:")
    print(f"Output dir: {config['output_dir']}")
    print(f"Batch size: {config['model_params']['batch_size']}")

1.2 DotDict with Complex Data Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create a DotDict with various data types
    complex_data = {
        'metadata': {
            'author': 'Research Team',
            'date': '2024-01-01',
            'version': '1.0.0'
        },
        'arrays': {
            'data_matrix': np.random.randn(100, 50),
            'labels': np.random.randint(0, 3, 100),
            'weights': np.random.uniform(0, 1, 50)
        },
        'dataframes': {
            'results': pd.DataFrame({
                'accuracy': np.random.uniform(0.8, 0.95, 10),
                'loss': np.random.uniform(0.1, 0.5, 10),
                'epoch': range(1, 11)
            })
        },
        'functions': {
            'activation': 'relu',
            'optimizer': 'adam',
            'loss_function': 'categorical_crossentropy'
        },
        123: 'integer_key',  # Non-string key
        'invalid-key': 'hyphenated_key'  # Invalid identifier
    }
    
    dot_dict = scitex.dict.DotDict(complex_data)
    
    # Access different data types
    print(f"Data matrix shape: {dot_dict.arrays.data_matrix.shape}")
    print(f"Results dataframe shape: {dot_dict.dataframes.results.shape}")
    print(f"Activation function: {dot_dict.functions.activation}")
    
    # Access non-string keys with bracket notation
    print(f"Integer key: {dot_dict[123]}")
    print(f"Hyphenated key: {dot_dict['invalid-key']}")
    
    # Modify values
    dot_dict.functions.activation = 'tanh'
    dot_dict.metadata.version = '1.1.0'
    
    print(f"\nAfter modification:")
    print(f"New activation: {dot_dict.functions.activation}")
    print(f"New version: {dot_dict.metadata.version}")

1.3 DotDict Methods and Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Demonstrate DotDict methods
    sample_dict = scitex.dict.DotDict({
        'a': 1,
        'b': 2,
        'c': {'nested': 3, 'more': 4},
        'd': [1, 2, 3]
    })
    
    print(f"Length: {len(sample_dict)}")
    print(f"Keys: {list(sample_dict.keys())}")
    print(f"Values: {list(sample_dict.values())}")
    print(f"Items: {list(sample_dict.items())}")
    
    # Check membership
    print(f"\n'a' in sample_dict: {'a' in sample_dict}")
    print(f"'z' in sample_dict: {'z' in sample_dict}")
    
    # Get method with default
    print(f"Get 'a' with default: {sample_dict.get('a', 'not found')}")
    print(f"Get 'z' with default: {sample_dict.get('z', 'not found')}")
    
    # Update method
    sample_dict.update({'e': 5, 'f': {'new_nested': 6}})
    print(f"\nAfter update: {list(sample_dict.keys())}")
    print(f"New nested value: {sample_dict.f.new_nested}")
    
    # Pop method
    popped_value = sample_dict.pop('b', 'not found')
    print(f"\nPopped value: {popped_value}")
    print(f"Keys after pop: {list(sample_dict.keys())}")
    
    # Copy method
    copied_dict = sample_dict.copy()
    copied_dict.a = 999
    print(f"\nOriginal 'a': {sample_dict.a}")
    print(f"Copy 'a': {copied_dict.a}")
    
    # Convert back to regular dict
    regular_dict = sample_dict.to_dict()
    print(f"\nType of original: {type(sample_dict)}")
    print(f"Type of converted: {type(regular_dict)}")
    print(f"Type of nested in converted: {type(regular_dict['c'])}")

Part 2: listed_dict - Dictionary with Automatic List Initialization
-------------------------------------------------------------------

2.1 Basic listed_dict Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create a listed_dict without predefined keys
    data_collector = scitex.dict.listed_dict()
    
    # Simulate data collection process
    for i in range(10):
        # Automatically creates lists for new keys
        data_collector['experiment_A'].append(random.randint(0, 100))
        data_collector['experiment_B'].append(random.randint(50, 150))
        data_collector['timestamps'].append(f"2024-01-{i+1:02d}")
    
    print("Data collected:")
    for key, values in data_collector.items():
        print(f"{key}: {values}")
    
    print(f"\nType of data_collector: {type(data_collector)}")
    print(f"Length of experiment_A: {len(data_collector['experiment_A'])}")

2.2 listed_dict with Predefined Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create listed_dict with predefined keys
    metrics_keys = ['accuracy', 'precision', 'recall', 'f1_score']
    metrics_collector = scitex.dict.listed_dict(metrics_keys)
    
    print("Initial state:")
    for key in metrics_keys:
        print(f"{key}: {metrics_collector[key]}")
    
    # Simulate multiple training runs
    n_runs = 5
    for run in range(n_runs):
        # Generate realistic metrics for each run
        base_accuracy = 0.85 + random.uniform(-0.1, 0.1)
        metrics_collector['accuracy'].append(base_accuracy)
        metrics_collector['precision'].append(base_accuracy + random.uniform(-0.05, 0.05))
        metrics_collector['recall'].append(base_accuracy + random.uniform(-0.05, 0.05))
        
        # F1 score as harmonic mean of precision and recall
        p = metrics_collector['precision'][-1]
        r = metrics_collector['recall'][-1]
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
        metrics_collector['f1_score'].append(f1)
    
    print(f"\nAfter {n_runs} runs:")
    for key, values in metrics_collector.items():
        avg_value = np.mean(values)
        std_value = np.std(values)
        print(f"{key}: {avg_value:.3f} ± {std_value:.3f} (n={len(values)})")
    
    # Convert to DataFrame for analysis
    metrics_df = pd.DataFrame(dict(metrics_collector))
    print(f"\nMetrics DataFrame:")
    print(metrics_df.round(3))

2.3 Real-world Example: Experiment Log Collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Simulate a machine learning experiment with multiple conditions
    experiment_log = scitex.dict.listed_dict()
    
    # Define experimental conditions
    learning_rates = [0.001, 0.01, 0.1]
    batch_sizes = [16, 32, 64]
    architectures = ['small', 'medium', 'large']
    
    # Run experiments
    for lr in learning_rates:
        for batch_size in batch_sizes:
            for arch in architectures:
                # Simulate training results
                final_accuracy = 0.7 + random.uniform(0, 0.25)
                training_time = random.uniform(10, 300)  # seconds
                
                # Log results
                experiment_log['learning_rate'].append(lr)
                experiment_log['batch_size'].append(batch_size)
                experiment_log['architecture'].append(arch)
                experiment_log['final_accuracy'].append(final_accuracy)
                experiment_log['training_time'].append(training_time)
                experiment_log['experiment_id'].append(f"lr{lr}_bs{batch_size}_{arch}")
    
    print(f"Total experiments: {len(experiment_log['experiment_id'])}")
    print(f"Unique learning rates: {set(experiment_log['learning_rate'])}")
    print(f"Unique batch sizes: {set(experiment_log['batch_size'])}")
    print(f"Unique architectures: {set(experiment_log['architecture'])}")
    
    # Convert to DataFrame for analysis
    experiment_df = pd.DataFrame(dict(experiment_log))
    
    # Find best configurations
    best_accuracy_idx = experiment_df['final_accuracy'].idxmax()
    best_config = experiment_df.loc[best_accuracy_idx]
    
    print(f"\nBest configuration:")
    print(f"Learning rate: {best_config['learning_rate']}")
    print(f"Batch size: {best_config['batch_size']}")
    print(f"Architecture: {best_config['architecture']}")
    print(f"Final accuracy: {best_config['final_accuracy']:.3f}")
    print(f"Training time: {best_config['training_time']:.1f} seconds")
    
    # Group by architecture and show average performance
    arch_performance = experiment_df.groupby('architecture')['final_accuracy'].agg(['mean', 'std', 'count'])
    print(f"\nPerformance by architecture:")
    print(arch_performance.round(3))

Part 3: Dictionary Manipulation Functions
-----------------------------------------

3.1 safe_merge - Merge Dictionaries with Conflict Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create test dictionaries for merging
    config_base = {
        'model': {
            'type': 'neural_network',
            'layers': 3
        },
        'training': {
            'epochs': 100,
            'batch_size': 32
        }
    }
    
    config_experiment = {
        'experiment': {
            'name': 'test_run_1',
            'date': '2024-01-01'
        },
        'optimization': {
            'learning_rate': 0.001,
            'optimizer': 'adam'
        }
    }
    
    config_output = {
        'output': {
            'save_path': '/tmp/results',
            'save_format': 'pickle'
        },
        'logging': {
            'level': 'INFO',
            'file': 'experiment.log'
        }
    }
    
    # Safe merge without conflicts
    try:
        merged_config = scitex.dict.safe_merge(config_base, config_experiment, config_output)
        print("Successfully merged configurations:")
        print(f"Top-level keys: {list(merged_config.keys())}")
        print(f"Model type: {merged_config['model']['type']}")
        print(f"Experiment name: {merged_config['experiment']['name']}")
        print(f"Output path: {merged_config['output']['save_path']}")
    except ValueError as e:
        print(f"Merge failed: {e}")
    
    # Test with conflicting keys
    config_conflict = {
        'model': {  # This will conflict with config_base
            'type': 'decision_tree',
            'max_depth': 10
        },
        'validation': {
            'split': 0.2
        }
    }
    
    try:
        conflicted_merge = scitex.dict.safe_merge(config_base, config_conflict)
        print("\nConflict merge succeeded (this shouldn't happen)")
    except ValueError as e:
        print(f"\nExpected conflict detected: {e}")

3.2 pop_keys - Remove Keys from Key Lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example: Feature selection by removing unwanted features
    all_features = [
        'age', 'gender', 'income', 'education', 'occupation',
        'marital_status', 'health_score', 'exercise_frequency',
        'smoking_status', 'alcohol_consumption', 'bmi', 'blood_pressure'
    ]
    
    # Remove sensitive or irrelevant features
    features_to_remove = ['gender', 'marital_status', 'income']
    
    selected_features = scitex.dict.pop_keys(all_features, features_to_remove)
    
    print(f"Original features ({len(all_features)}): {all_features}")
    print(f"Features to remove: {features_to_remove}")
    print(f"Selected features ({len(selected_features)}): {selected_features}")
    
    # Example: Column selection for data analysis
    dataframe_columns = [
        'timestamp', 'user_id', 'session_id', 'action_type',
        'page_url', 'referrer', 'user_agent', 'ip_address',
        'duration', 'clicks', 'scrolls', 'conversions'
    ]
    
    # Remove PII and technical columns for analysis
    columns_to_exclude = ['user_id', 'session_id', 'ip_address', 'user_agent']
    analysis_columns = scitex.dict.pop_keys(dataframe_columns, columns_to_exclude)
    
    print(f"\nOriginal columns: {dataframe_columns}")
    print(f"Columns to exclude: {columns_to_exclude}")
    print(f"Analysis columns: {analysis_columns}")
    
    # Example: Multi-stage feature filtering
    ml_features = [
        'feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5',
        'feature_6', 'feature_7', 'feature_8', 'feature_9', 'feature_10',
        'target', 'id', 'timestamp'
    ]
    
    # Remove non-feature columns
    non_features = ['target', 'id', 'timestamp']
    features_only = scitex.dict.pop_keys(ml_features, non_features)
    
    # Remove low-importance features (simulated)
    low_importance = ['feature_3', 'feature_7', 'feature_9']
    high_importance_features = scitex.dict.pop_keys(features_only, low_importance)
    
    print(f"\nML pipeline feature selection:")
    print(f"All columns: {ml_features}")
    print(f"Features only: {features_only}")
    print(f"High importance features: {high_importance_features}")

3.3 replace - String Replacement with Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example: Template processing for experiment reports
    report_template = """
    Experiment Report
    =================
    
    Experiment Name: {EXPERIMENT_NAME}
    Date: {DATE}
    Model: {MODEL_TYPE}
    Dataset: {DATASET}
    
    Results:
    - Accuracy: {ACCURACY}
    - Precision: {PRECISION}
    - Recall: {RECALL}
    - F1 Score: {F1_SCORE}
    
    Training Time: {TRAINING_TIME}
    Status: {STATUS}
    """
    
    # Define replacement dictionary
    experiment_values = {
        '{EXPERIMENT_NAME}': 'Image Classification Study',
        '{DATE}': '2024-01-15',
        '{MODEL_TYPE}': 'Convolutional Neural Network',
        '{DATASET}': 'CIFAR-10',
        '{ACCURACY}': '0.923',
        '{PRECISION}': '0.918',
        '{RECALL}': '0.915',
        '{F1_SCORE}': '0.916',
        '{TRAINING_TIME}': '2.5 hours',
        '{STATUS}': 'COMPLETED'
    }
    
    # Generate report
    final_report = scitex.dict.replace(report_template, experiment_values)
    print(final_report)
    
    # Example: Code generation with variable substitution
    code_template = """
    def {FUNCTION_NAME}({PARAMETERS}):
        \"\"\"
        {DOCSTRING}
        \"\"\"
        {BODY}
        return {RETURN_VALUE}
    """
    
    function_specs = {
        '{FUNCTION_NAME}': 'calculate_metrics',
        '{PARAMETERS}': 'y_true, y_pred',
        '{DOCSTRING}': 'Calculate classification metrics from predictions.',
        '{BODY}': '''    accuracy = np.mean(y_true == y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')''',
        '{RETURN_VALUE}': '{'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1}'
    }
    
    generated_code = scitex.dict.replace(code_template, function_specs)
    print("\nGenerated code:")
    print(generated_code)
    
    # Example: Configuration file processing
    config_template = """
    model_config = {
        'architecture': '{ARCHITECTURE}',
        'input_size': {INPUT_SIZE},
        'hidden_layers': {HIDDEN_LAYERS},
        'output_size': {OUTPUT_SIZE},
        'activation': '{ACTIVATION}',
        'dropout_rate': {DROPOUT_RATE}
    }
    
    training_config = {
        'learning_rate': {LEARNING_RATE},
        'batch_size': {BATCH_SIZE},
        'epochs': {EPOCHS},
        'optimizer': '{OPTIMIZER}'
    }
    """
    
    config_values = {
        '{ARCHITECTURE}': 'feedforward',
        '{INPUT_SIZE}': '784',
        '{HIDDEN_LAYERS}': '[128, 64, 32]',
        '{OUTPUT_SIZE}': '10',
        '{ACTIVATION}': 'relu',
        '{DROPOUT_RATE}': '0.2',
        '{LEARNING_RATE}': '0.001',
        '{BATCH_SIZE}': '32',
        '{EPOCHS}': '100',
        '{OPTIMIZER}': 'adam'
    }
    
    config_code = scitex.dict.replace(config_template, config_values)
    print("\nGenerated configuration:")
    print(config_code)

3.4 to_str - Convert Dictionary to String Representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Example: Creating unique experiment identifiers
    experiment_params = {
        'lr': 0.001,
        'bs': 32,
        'arch': 'resnet',
        'dropout': 0.2
    }
    
    experiment_id = scitex.dict.to_str(experiment_params)
    print(f"Experiment ID: {experiment_id}")
    
    # Custom delimiter
    experiment_id_custom = scitex.dict.to_str(experiment_params, delimiter='__')
    print(f"Custom delimiter ID: {experiment_id_custom}")
    
    # Example: Model hyperparameter tracking
    model_configs = [
        {'model': 'cnn', 'layers': 3, 'filters': 64, 'lr': 0.01},
        {'model': 'rnn', 'units': 128, 'dropout': 0.3, 'lr': 0.001},
        {'model': 'transformer', 'heads': 8, 'layers': 6, 'lr': 0.0001}
    ]
    
    print("\nModel configuration strings:")
    for i, config in enumerate(model_configs):
        config_str = scitex.dict.to_str(config, delimiter='|')
        print(f"Config {i+1}: {config_str}")
    
    # Example: Creating file names from parameters
    experiment_settings = {
        'dataset': 'cifar10',
        'model': 'vgg16',
        'epochs': 50,
        'augment': True
    }
    
    filename_base = scitex.dict.to_str(experiment_settings, delimiter='_')
    full_filename = f"results_{filename_base}.pkl"
    print(f"\nGenerated filename: {full_filename}")
    
    # Example: Logging experiment parameters
    training_logs = scitex.dict.listed_dict(['timestamp', 'config_string', 'final_loss'])
    
    # Simulate multiple training runs
    configs = [
        {'lr': 0.1, 'momentum': 0.9, 'weight_decay': 1e-4},
        {'lr': 0.01, 'momentum': 0.95, 'weight_decay': 1e-5},
        {'lr': 0.001, 'momentum': 0.99, 'weight_decay': 1e-3}
    ]
    
    for i, config in enumerate(configs):
        config_str = scitex.dict.to_str(config, delimiter=',')
        final_loss = random.uniform(0.1, 0.5)
        
        training_logs['timestamp'].append(f"2024-01-{i+1:02d}")
        training_logs['config_string'].append(config_str)
        training_logs['final_loss'].append(final_loss)
    
    print("\nTraining logs:")
    for i in range(len(training_logs['timestamp'])):
        print(f"{training_logs['timestamp'][i]}: {training_logs['config_string'][i]} -> Loss: {training_logs['final_loss'][i]:.3f}")

Part 4: Advanced Use Cases and Integration
------------------------------------------

4.1 Scientific Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Complex scientific experiment configuration
    class ExperimentConfig:
        def __init__(self):
            self.base_config = scitex.dict.DotDict({
                'experiment': {
                    'name': 'baseline',
                    'description': 'Baseline experiment setup',
                    'version': '1.0.0'
                },
                'data': {
                    'source': 'synthetic',
                    'size': 10000,
                    'features': 100,
                    'noise_level': 0.1
                },
                'model': {
                    'type': 'neural_network',
                    'architecture': [100, 50, 25, 10],
                    'activation': 'relu',
                    'dropout': 0.2
                },
                'training': {
                    'optimizer': 'adam',
                    'learning_rate': 0.001,
                    'batch_size': 32,
                    'epochs': 100,
                    'validation_split': 0.2
                },
                'output': {
                    'save_model': True,
                    'save_predictions': True,
                    'save_metrics': True,
                    'plot_results': True
                }
            })
            
            self.experiment_variants = []
            self.results_log = scitex.dict.listed_dict()
        
        def create_variant(self, name, modifications):
            """Create a new experiment variant by modifying the base configuration."""
            variant_config = self.base_config.copy()
            variant_config.experiment.name = name
            
            # Apply modifications
            for key_path, value in modifications.items():
                keys = key_path.split('.')
                current = variant_config
                for key in keys[:-1]:
                    current = current[key]
                current[keys[-1]] = value
            
            # Generate unique identifier
            config_id = scitex.dict.to_str(modifications, delimiter='_')
            variant_config.experiment.config_id = config_id
            
            self.experiment_variants.append(variant_config)
            return variant_config
        
        def run_experiment(self, config):
            """Simulate running an experiment with the given configuration."""
            # Simulate training
            print(f"Running experiment: {config.experiment.name}")
            print(f"Config ID: {config.experiment.config_id}")
            
            # Simulate results based on configuration
            base_accuracy = 0.8
            lr_factor = min(1.0, config.training.learning_rate * 1000)  # Penalize very high LR
            dropout_factor = 1.0 - config.model.dropout * 0.5  # Slight penalty for high dropout
            
            final_accuracy = base_accuracy * lr_factor * dropout_factor + random.uniform(-0.1, 0.1)
            final_accuracy = max(0.0, min(1.0, final_accuracy))  # Clamp to [0, 1]
            
            results = {
                'accuracy': final_accuracy,
                'loss': random.uniform(0.1, 0.5),
                'training_time': random.uniform(60, 300)
            }
            
            # Log results
            self.results_log['experiment_name'].append(config.experiment.name)
            self.results_log['config_id'].append(config.experiment.config_id)
            self.results_log['accuracy'].append(results['accuracy'])
            self.results_log['loss'].append(results['loss'])
            self.results_log['training_time'].append(results['training_time'])
            
            return results
        
        def get_best_config(self):
            """Find the best performing configuration."""
            if not self.results_log['accuracy']:
                return None
            
            best_idx = np.argmax(self.results_log['accuracy'])
            return {
                'name': self.results_log['experiment_name'][best_idx],
                'config_id': self.results_log['config_id'][best_idx],
                'accuracy': self.results_log['accuracy'][best_idx],
                'loss': self.results_log['loss'][best_idx],
                'training_time': self.results_log['training_time'][best_idx]
            }
    
    # Create experiment manager
    exp_manager = ExperimentConfig()
    
    # Create different experiment variants
    variants = [
        ('high_lr', {'training.learning_rate': 0.01}),
        ('low_lr', {'training.learning_rate': 0.0001}),
        ('high_dropout', {'model.dropout': 0.5}),
        ('large_batch', {'training.batch_size': 128}),
        ('small_batch', {'training.batch_size': 8}),
        ('deep_model', {'model.architecture': [100, 80, 60, 40, 20, 10]})
    ]
    
    # Create and run experiments
    for variant_name, modifications in variants:
        config = exp_manager.create_variant(variant_name, modifications)
        results = exp_manager.run_experiment(config)
        print(f"Results: Accuracy={results['accuracy']:.3f}, Loss={results['loss']:.3f}")
        print()
    
    # Find best configuration
    best_config = exp_manager.get_best_config()
    print(f"Best configuration:")
    print(f"Name: {best_config['name']}")
    print(f"Config ID: {best_config['config_id']}")
    print(f"Accuracy: {best_config['accuracy']:.3f}")
    print(f"Loss: {best_config['loss']:.3f}")
    print(f"Training time: {best_config['training_time']:.1f} seconds")

4.2 Data Processing Pipeline with Dictionary Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create a data processing pipeline using dictionary utilities
    class DataProcessingPipeline:
        def __init__(self):
            self.pipeline_config = scitex.dict.DotDict({
                'input': {
                    'source': 'database',
                    'format': 'csv',
                    'encoding': 'utf-8'
                },
                'preprocessing': {
                    'remove_duplicates': True,
                    'handle_missing': 'impute',
                    'normalize': True,
                    'feature_selection': True
                },
                'feature_engineering': {
                    'create_interactions': False,
                    'polynomial_features': False,
                    'text_vectorization': 'tfidf'
                },
                'output': {
                    'format': 'parquet',
                    'compression': 'snappy',
                    'save_metadata': True
                }
            })
            
            self.processing_log = scitex.dict.listed_dict()
            self.feature_metadata = scitex.dict.listed_dict()
        
        def process_dataset(self, dataset_info):
            """Process a dataset according to the pipeline configuration."""
            dataset_name = dataset_info['name']
            original_features = dataset_info['features']
            
            print(f"Processing dataset: {dataset_name}")
            print(f"Original features: {len(original_features)}")
            
            # Step 1: Preprocessing
            processed_features = original_features.copy()
            
            if self.pipeline_config.preprocessing.remove_duplicates:
                # Simulate removing duplicate features
                duplicate_features = ['feature_1_copy', 'feature_2_duplicate']
                processed_features = scitex.dict.pop_keys(processed_features, duplicate_features)
                print(f"Removed duplicates: {len(original_features) - len(processed_features)} features")
            
            if self.pipeline_config.preprocessing.feature_selection:
                # Simulate feature selection
                low_variance_features = [f for f in processed_features if 'low_var' in f]
                processed_features = scitex.dict.pop_keys(processed_features, low_variance_features)
                print(f"Feature selection: {len(processed_features)} features remaining")
            
            # Step 2: Feature Engineering
            if self.pipeline_config.feature_engineering.create_interactions:
                # Simulate creating interaction features
                interaction_features = [f"{f1}_x_{f2}" for f1 in processed_features[:3] for f2 in processed_features[3:6]]
                processed_features.extend(interaction_features)
                print(f"Created interactions: {len(interaction_features)} new features")
            
            # Log processing results
            processing_summary = {
                'dataset': dataset_name,
                'original_features': len(original_features),
                'final_features': len(processed_features),
                'reduction_ratio': len(processed_features) / len(original_features),
                'config': scitex.dict.to_str(self.pipeline_config.preprocessing.to_dict(), delimiter='|')
            }
            
            for key, value in processing_summary.items():
                self.processing_log[key].append(value)
            
            # Store feature metadata
            self.feature_metadata['dataset_name'].append(dataset_name)
            self.feature_metadata['final_features'].append(processed_features)
            self.feature_metadata['feature_count'].append(len(processed_features))
            
            return processed_features
        
        def get_processing_summary(self):
            """Get a summary of all processing operations."""
            if not self.processing_log['dataset']:
                return "No datasets processed yet."
            
            summary_df = pd.DataFrame(dict(self.processing_log))
            return summary_df
        
        def merge_feature_sets(self, *feature_sets):
            """Safely merge multiple feature sets."""
            try:
                # Convert lists to dictionaries for merging
                feature_dicts = []
                for i, features in enumerate(feature_sets):
                    feature_dict = {f"set_{i}_{j}": feature for j, feature in enumerate(features)}
                    feature_dicts.append(feature_dict)
                
                merged_dict = scitex.dict.safe_merge(*feature_dicts)
                merged_features = list(merged_dict.values())
                
                print(f"Successfully merged {len(feature_sets)} feature sets")
                print(f"Total features: {len(merged_features)}")
                
                return merged_features
            except ValueError as e:
                print(f"Feature merge failed: {e}")
                return None
    
    # Create processing pipeline
    pipeline = DataProcessingPipeline()
    
    # Define test datasets
    test_datasets = [
        {
            'name': 'customer_data',
            'features': ['age', 'income', 'feature_1_copy', 'education', 'low_var_1', 'spending', 'low_var_2', 'location']
        },
        {
            'name': 'product_data',
            'features': ['price', 'category', 'rating', 'feature_2_duplicate', 'reviews', 'low_var_3', 'availability']
        },
        {
            'name': 'transaction_data',
            'features': ['amount', 'timestamp', 'payment_method', 'low_var_4', 'merchant', 'low_var_5']
        }
    ]
    
    # Process all datasets
    processed_feature_sets = []
    for dataset in test_datasets:
        processed_features = pipeline.process_dataset(dataset)
        processed_feature_sets.append(processed_features)
        print(f"Final features for {dataset['name']}: {processed_features}")
        print()
    
    # Get processing summary
    summary = pipeline.get_processing_summary()
    print("Processing Summary:")
    print(summary)
    print()
    
    # Merge feature sets (this should work as features are from different datasets)
    merged_features = pipeline.merge_feature_sets(*processed_feature_sets)
    if merged_features:
        print(f"\nMerged features: {merged_features}")
        print(f"Total merged features: {len(merged_features)}")

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive dictionary utilities
available in the SciTeX library:

Key Components Covered:
~~~~~~~~~~~~~~~~~~~~~~~

1. **DotDict**: Enables attribute-style access to dictionary keys

   -  Supports nested dictionaries
   -  Handles various data types (arrays, DataFrames, functions)
   -  Provides standard dictionary methods

2. **listed_dict**: Automatically initializes lists for new keys

   -  Perfect for data collection and aggregation
   -  Supports predefined keys
   -  Integrates well with pandas DataFrames

3. **safe_merge**: Merges dictionaries with conflict detection

   -  Prevents accidental overwrites
   -  Useful for configuration management
   -  Supports multiple dictionaries

4. **pop_keys**: Removes specified keys from key lists

   -  Feature selection and filtering
   -  Data privacy and security
   -  Multi-stage processing pipelines

5. **replace**: String replacement using dictionaries

   -  Template processing
   -  Code generation
   -  Report generation

6. **to_str**: Converts dictionaries to string representations

   -  Experiment identification
   -  File naming
   -  Configuration tracking

Best Practices:
~~~~~~~~~~~~~~~

-  Use **DotDict** for configuration objects and nested data structures
-  Use **listed_dict** for collecting experimental data and metrics
-  Use **safe_merge** when combining configurations from multiple
   sources
-  Use **pop_keys** for feature selection and data filtering
-  Use **replace** for template processing and code generation
-  Use **to_str** for creating unique identifiers and file names
-  Combine utilities for complex data processing pipelines
-  Always validate merged configurations in critical applications
-  Use meaningful delimiters in **to_str** for better readability

.. code:: ipython3

    print("SciTeX Dictionary Utilities Tutorial Complete!")
    print("\nKey takeaways:")
    print("1. DotDict provides intuitive attribute-style access to dictionaries")
    print("2. listed_dict simplifies data collection and aggregation")
    print("3. safe_merge prevents configuration conflicts")
    print("4. pop_keys enables flexible feature selection")
    print("5. replace supports powerful template processing")
    print("6. to_str creates unique identifiers from parameters")
    print("7. All utilities work together for complex scientific computing workflows")
