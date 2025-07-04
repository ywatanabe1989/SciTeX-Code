09 SciTeX Os
============

.. note::
   This page is generated from the Jupyter notebook `09_scitex_os.ipynb <https://github.com/scitex/scitex/blob/main/examples/09_scitex_os.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 09_scitex_os.ipynb


This notebook demonstrates the complete functionality of the
``scitex.os`` module, which provides operating system utilities for
scientific computing workflows.

Module Overview
---------------

The ``scitex.os`` module includes: - File and directory manipulation
utilities - Safe file movement operations - Cross-platform file system
operations

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import os
    import tempfile
    import shutil
    from pathlib import Path
    
    # Import scitex os module
    import scitex.os as sos
    
    print("Available functions in scitex.os:")
    os_attrs = [attr for attr in dir(sos) if not attr.startswith('_')]
    for i, attr in enumerate(os_attrs):
        print(f"{i+1:2d}. {attr}")
    
    print(f"\nTotal functions available: {len(os_attrs)}")

1. File Movement Operations
---------------------------

Basic File Movement
~~~~~~~~~~~~~~~~~~~

The ``mv`` function provides safe file and directory movement
operations.

.. code:: ipython3

    # Example 1: Basic file movement
    print("Basic File Movement Operations:")
    print("=" * 35)
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix='scitex_os_test_')
    print(f"Created temporary directory: {temp_dir}")
    
    # Create test files
    test_files = {
        'data.txt': "Sample scientific data\n1,2,3\n4,5,6\n7,8,9",
        'results.csv': "experiment,value,error\nA,10.5,0.1\nB,12.3,0.2\nC,9.8,0.15",
        'analysis.py': "import numpy as np\ndata = np.array([1,2,3])\nprint(data.mean())",
        'readme.md': "# Scientific Analysis\nThis directory contains analysis files."
    }
    
    source_dir = os.path.join(temp_dir, 'source')
    target_dir = os.path.join(temp_dir, 'target')
    
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)
    
    # Create test files in source directory
    created_files = []
    for filename, content in test_files.items():
        file_path = os.path.join(source_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        created_files.append(file_path)
        print(f"Created: {filename}")
    
    print(f"\nSource directory contents:")
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        size = os.path.getsize(item_path)
        print(f"  {item} ({size} bytes)")
    
    print(f"\nTarget directory contents (before move):")
    target_contents = os.listdir(target_dir)
    if target_contents:
        for item in target_contents:
            print(f"  {item}")
    else:
        print("  (empty)")

Moving Individual Files
~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate moving individual files using the ``mv`` function.

.. code:: ipython3

    # Example 2: Moving individual files
    print("Moving Individual Files:")
    print("=" * 25)
    
    # Test moving individual files
    files_to_move = ['data.txt', 'results.csv']
    
    for filename in files_to_move:
        source_path = os.path.join(source_dir, filename)
        
        if os.path.exists(source_path):
            print(f"\nMoving {filename}:")
            print(f"  From: {source_path}")
            print(f"  To: {target_dir}")
            
            try:
                # Use scitex.os.mv function
                result = sos.mv(source_path, target_dir)
                
                # Check if file was moved successfully
                target_path = os.path.join(target_dir, filename)
                if os.path.exists(target_path):
                    print(f"  ✓ Successfully moved to {target_path}")
                else:
                    print(f"  ✗ File not found at expected location")
                    
                # Check if source file was removed
                if not os.path.exists(source_path):
                    print(f"  ✓ Source file properly removed")
                else:
                    print(f"  ⚠ Source file still exists")
                    
            except Exception as e:
                print(f"  ✗ Error moving file: {e}")
        else:
            print(f"\n✗ Source file {filename} not found")
    
    # Show updated directory contents
    print(f"\nUpdated directory contents:")
    print(f"Source directory:")
    source_contents = os.listdir(source_dir)
    for item in source_contents:
        print(f"  {item}")
    
    print(f"\nTarget directory:")
    target_contents = os.listdir(target_dir)
    for item in target_contents:
        item_path = os.path.join(target_dir, item)
        size = os.path.getsize(item_path)
        print(f"  {item} ({size} bytes)")

Moving Remaining Files
~~~~~~~~~~~~~~~~~~~~~~

Let’s move the remaining files and test error handling.

.. code:: ipython3

    # Example 3: Moving remaining files and error handling
    print("Moving Remaining Files and Error Handling:")
    print("=" * 45)
    
    # Move remaining files
    remaining_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    
    print(f"Remaining files to move: {remaining_files}")
    
    for filename in remaining_files:
        source_path = os.path.join(source_dir, filename)
        
        print(f"\nMoving {filename}:")
        try:
            result = sos.mv(source_path, target_dir)
            print(f"  ✓ Move operation completed")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test error handling with non-existent file
    print(f"\nTesting error handling:")
    print(f"Attempting to move non-existent file...")
    
    non_existent_file = os.path.join(source_dir, 'does_not_exist.txt')
    try:
        result = sos.mv(non_existent_file, target_dir)
        print(f"  Unexpected success")
    except Exception as e:
        print(f"  ✓ Properly handled error: {e}")
    
    # Final directory status
    print(f"\nFinal directory status:")
    print(f"Source directory ({len(os.listdir(source_dir))} items):")
    for item in os.listdir(source_dir):
        print(f"  {item}")
    
    print(f"\nTarget directory ({len(os.listdir(target_dir))} items):")
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"  {item} ({size} bytes)")
        else:
            print(f"  {item} (directory)")

2. Advanced File Operations
---------------------------

Working with Different File Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s test the mv function with various scientific file types.

.. code:: ipython3

    # Example 4: Working with different scientific file types
    print("Working with Different Scientific File Types:")
    print("=" * 45)
    
    # Create a new test directory structure
    scientific_dir = os.path.join(temp_dir, 'scientific_files')
    organized_dir = os.path.join(temp_dir, 'organized')
    
    os.makedirs(scientific_dir, exist_ok=True)
    os.makedirs(organized_dir, exist_ok=True)
    
    # Create different types of scientific files
    scientific_files = {
        # Data files
        'experiment_001.csv': "time,temperature,pressure\n0,25.1,1013\n1,25.3,1012\n2,25.5,1011",
        'sensor_data.json': '{"sensors": [{"id": 1, "value": 23.4}, {"id": 2, "value": 24.1}]}',
        'measurements.xlsx': "# Simulated Excel file content (binary data would go here)",
        
        # Analysis files
        'statistical_analysis.py': "import pandas as pd\nimport numpy as np\ndata = pd.read_csv('data.csv')\nprint(data.describe())",
        'visualization.R': "library(ggplot2)\ndata <- read.csv('data.csv')\nggplot(data, aes(x=time, y=value)) + geom_line()",
        'analysis.ipynb': '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}',
        
        # Configuration files
        'config.yaml': "experiment:\n  name: test_001\n  duration: 3600\n  sampling_rate: 100",
        'parameters.ini': "[DEFAULT]\ntemperature = 25\npressure = 1013\n[EXPERIMENT]\nruns = 10",
        
        # Documentation
        'protocol.md': "# Experimental Protocol\n\n## Procedure\n1. Setup equipment\n2. Calibrate sensors\n3. Run experiment",
        'results_summary.txt': "Experimental Results Summary\n\nMean temperature: 25.3°C\nStandard deviation: 0.2°C"
    }
    
    # Create all files
    print("Creating scientific files:")
    for filename, content in scientific_files.items():
        file_path = os.path.join(scientific_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Get file info
        size = os.path.getsize(file_path)
        ext = os.path.splitext(filename)[1]
        print(f"  {filename:20s} ({size:4d} bytes) [{ext or 'no ext'}]")
    
    print(f"\nCreated {len(scientific_files)} scientific files")

Organizing Files by Type
~~~~~~~~~~~~~~~~~~~~~~~~

Let’s organize the scientific files by type using the mv function.

.. code:: ipython3

    # Example 5: Organizing files by type
    print("Organizing Files by Type:")
    print("=" * 25)
    
    # Define file type categories
    file_categories = {
        'data': ['.csv', '.json', '.xlsx', '.txt'],
        'analysis': ['.py', '.R', '.ipynb'],
        'config': ['.yaml', '.ini'],
        'docs': ['.md', '.txt']
    }
    
    # Create category directories
    category_dirs = {}
    for category in file_categories.keys():
        category_dir = os.path.join(organized_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        category_dirs[category] = category_dir
        print(f"Created directory: {category}/")
    
    # Function to determine file category
    def get_file_category(filename):
        ext = os.path.splitext(filename)[1].lower()
        
        for category, extensions in file_categories.items():
            if ext in extensions:
                # Special handling for .txt files
                if ext == '.txt':
                    if 'result' in filename.lower() or 'summary' in filename.lower():
                        return 'data'
                    else:
                        return 'docs'
                return category
        
        return 'misc'  # Default category
    
    # Organize files
    print(f"\nOrganizing files:")
    files_moved = {category: [] for category in file_categories.keys()}
    files_moved['misc'] = []
    
    for filename in os.listdir(scientific_dir):
        source_path = os.path.join(scientific_dir, filename)
        
        if os.path.isfile(source_path):
            category = get_file_category(filename)
            
            # Create misc directory if needed
            if category == 'misc' and category not in category_dirs:
                misc_dir = os.path.join(organized_dir, 'misc')
                os.makedirs(misc_dir, exist_ok=True)
                category_dirs['misc'] = misc_dir
            
            target_dir = category_dirs[category]
            
            print(f"  {filename:25s} → {category}/")
            
            try:
                result = sos.mv(source_path, target_dir)
                files_moved[category].append(filename)
            except Exception as e:
                print(f"    ✗ Error moving {filename}: {e}")
    
    # Show organization results
    print(f"\nOrganization Results:")
    total_moved = 0
    for category, files in files_moved.items():
        if files:
            print(f"  {category:10s}: {len(files)} files")
            for filename in files:
                print(f"    - {filename}")
            total_moved += len(files)
    
    print(f"\nTotal files moved: {total_moved}")
    
    # Verify organization
    print(f"\nVerifying organization:")
    for category, directory in category_dirs.items():
        if os.path.exists(directory):
            contents = os.listdir(directory)
            print(f"  {category:10s}: {len(contents)} files - {contents}")
        else:
            print(f"  {category:10s}: directory not found")

3. Practical Scientific Workflows
---------------------------------

Experimental Data Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate a practical workflow for organizing experimental data.

.. code:: ipython3

    # Example 6: Experimental data organization workflow
    print("Experimental Data Organization Workflow:")
    print("=" * 40)
    
    # Create a realistic experimental data structure
    experiment_root = os.path.join(temp_dir, 'experiment_2024')
    raw_data_dir = os.path.join(experiment_root, 'raw_data')
    processed_dir = os.path.join(experiment_root, 'processed')
    
    os.makedirs(raw_data_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    # Simulate experimental data files from different days
    import datetime
    
    experimental_data = {
        # Day 1 data
        '2024-01-15_experiment_001_raw.csv': "timestamp,sensor1,sensor2,sensor3\n2024-01-15T09:00:00,23.1,45.2,67.3\n2024-01-15T09:01:00,23.2,45.1,67.4",
        '2024-01-15_experiment_001_metadata.json': '{"date": "2024-01-15", "duration": 3600, "samples": 60, "conditions": "standard"}',
        '2024-01-15_calibration.csv': "device,reference,measured,error\nsensor1,25.0,25.1,0.1\nsensor2,50.0,49.9,-0.1",
        
        # Day 2 data
        '2024-01-16_experiment_002_raw.csv': "timestamp,sensor1,sensor2,sensor3\n2024-01-16T10:00:00,24.1,46.2,68.3\n2024-01-16T10:01:00,24.2,46.1,68.4",
        '2024-01-16_experiment_002_metadata.json': '{"date": "2024-01-16", "duration": 3600, "samples": 60, "conditions": "elevated_temp"}',
        
        # Day 3 data
        '2024-01-17_experiment_003_raw.csv': "timestamp,sensor1,sensor2,sensor3\n2024-01-17T11:00:00,25.1,47.2,69.3\n2024-01-17T11:01:00,25.2,47.1,69.4",
        '2024-01-17_experiment_003_metadata.json': '{"date": "2024-01-17", "duration": 3600, "samples": 60, "conditions": "high_humidity"}',
        '2024-01-17_notes.txt': "Observed unusual fluctuations in sensor2 around 11:30. Need to investigate calibration.",
    }
    
    # Create experimental data files
    print("Creating experimental data files:")
    for filename, content in experimental_data.items():
        file_path = os.path.join(raw_data_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        
        size = os.path.getsize(file_path)
        print(f"  {filename:35s} ({size:3d} bytes)")
    
    print(f"\nCreated {len(experimental_data)} experimental files")
    
    # Organize by experiment date
    print(f"\nOrganizing by experiment date:")
    date_dirs = {}
    
    for filename in os.listdir(raw_data_dir):
        if filename.startswith('2024-'):
            # Extract date from filename
            date_part = filename.split('_')[0]  # e.g., '2024-01-15'
            
            # Create date-based directory
            if date_part not in date_dirs:
                date_dir = os.path.join(processed_dir, date_part)
                os.makedirs(date_dir, exist_ok=True)
                date_dirs[date_part] = date_dir
                print(f"  Created directory: {date_part}/")
            
            # Move file to date directory
            source_path = os.path.join(raw_data_dir, filename)
            target_dir = date_dirs[date_part]
            
            print(f"  Moving {filename} → {date_part}/")
            
            try:
                result = sos.mv(source_path, target_dir)
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    # Show final organization
    print(f"\nFinal experimental data organization:")
    print(f"Raw data directory: {len(os.listdir(raw_data_dir))} remaining files")
    
    print(f"\nProcessed data structure:")
    for date_dir in sorted(date_dirs.keys()):
        full_path = date_dirs[date_dir]
        files = os.listdir(full_path)
        print(f"  {date_dir}/ ({len(files)} files):")
        for file in sorted(files):
            file_path = os.path.join(full_path, file)
            size = os.path.getsize(file_path)
            print(f"    - {file} ({size} bytes)")

File Backup and Archive Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate a backup workflow using the mv function.

.. code:: ipython3

    # Example 7: File backup and archive workflow
    print("File Backup and Archive Workflow:")
    print("=" * 35)
    
    # Create a working directory with important files
    working_dir = os.path.join(temp_dir, 'active_project')
    archive_dir = os.path.join(temp_dir, 'archive')
    backup_dir = os.path.join(temp_dir, 'backup')
    
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create files representing different stages of work
    project_files = {
        # Current work
        'current_analysis.py': "# Current analysis script\nimport numpy as np\ndata = np.random.randn(1000)\nprint(f'Mean: {data.mean():.3f}')",
        'latest_results.csv': "date,value,status\n2024-01-20,95.2,active\n2024-01-21,96.1,active",
        'active_notebook.ipynb': '{"cells": [{"cell_type": "code", "source": ["print(\\"Active work\\")"]}]}',
        
        # Old versions (to be archived)
        'analysis_v1.py': "# Old version 1\nimport numpy as np\ndata = np.random.randn(100)\nprint(data.mean())",
        'analysis_v2.py': "# Old version 2\nimport numpy as np\ndata = np.random.randn(500)\nprint(f'Mean: {data.mean()}')",
        'old_results_2024-01-10.csv': "date,value,status\n2024-01-10,90.1,archived\n2024-01-11,91.2,archived",
        'deprecated_notebook.ipynb': '{"cells": [{"cell_type": "code", "source": ["print(\\"Deprecated\\")"]}]}',
        
        # Temporary files (to be cleaned up)
        'temp_data.tmp': "temporary data for processing",
        'cache_file.cache': "cached computation results",
        'debug_output.log': "DEBUG: Starting analysis\nINFO: Processing complete\nDEBUG: Cleanup finished"
    }
    
    # Create project files
    print("Creating project files:")
    for filename, content in project_files.items():
        file_path = os.path.join(working_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        
        size = os.path.getsize(file_path)
        print(f"  {filename:30s} ({size:3d} bytes)")
    
    print(f"\nWorking directory contains {len(project_files)} files")
    
    # Define file categories for workflow
    def categorize_file(filename):
        """Categorize files for workflow processing."""
        filename_lower = filename.lower()
        
        # Temporary files to delete
        if any(ext in filename_lower for ext in ['.tmp', '.cache', '.log']):
            return 'temporary'
        
        # Old versions to archive
        if any(keyword in filename_lower for keyword in ['_v1', '_v2', 'old_', 'deprecated']):
            return 'archive'
        
        # Current files to keep
        if any(keyword in filename_lower for keyword in ['current', 'latest', 'active']):
            return 'current'
        
        return 'unknown'
    
    # Process files according to workflow
    print(f"\nProcessing files according to workflow:")
    
    files_by_category = {'current': [], 'archive': [], 'temporary': [], 'unknown': []}
    
    for filename in os.listdir(working_dir):
        source_path = os.path.join(working_dir, filename)
        
        if os.path.isfile(source_path):
            category = categorize_file(filename)
            files_by_category[category].append(filename)
            
            if category == 'archive':
                print(f"  Archiving: {filename}")
                try:
                    result = sos.mv(source_path, archive_dir)
                except Exception as e:
                    print(f"    ✗ Error archiving: {e}")
                    
            elif category == 'temporary':
                print(f"  Removing temporary: {filename}")
                try:
                    os.remove(source_path)
                    print(f"    ✓ Deleted temporary file")
                except Exception as e:
                    print(f"    ✗ Error deleting: {e}")
                    
            elif category == 'current':
                print(f"  Keeping current: {filename}")
                
            else:
                print(f"  Unknown category: {filename} (keeping in place)")
    
    # Show workflow results
    print(f"\nWorkflow Results:")
    for category, files in files_by_category.items():
        if files:
            print(f"  {category.capitalize():10s}: {len(files)} files")
            for filename in files:
                print(f"    - {filename}")
    
    # Show final directory states
    print(f"\nFinal Directory States:")
    directories = {
        'Working': working_dir,
        'Archive': archive_dir,
        'Backup': backup_dir
    }
    
    for dir_name, dir_path in directories.items():
        contents = os.listdir(dir_path)
        print(f"  {dir_name:8s}: {len(contents)} files - {contents}")

4. Error Handling and Edge Cases
--------------------------------

Testing Edge Cases
~~~~~~~~~~~~~~~~~~

Let’s test the mv function with various edge cases and error conditions.

.. code:: ipython3

    # Example 8: Testing edge cases and error handling
    print("Testing Edge Cases and Error Handling:")
    print("=" * 40)
    
    # Create test directory for edge cases
    edge_test_dir = os.path.join(temp_dir, 'edge_cases')
    os.makedirs(edge_test_dir, exist_ok=True)
    
    # Test Case 1: Non-existent source file
    print("\n1. Testing non-existent source file:")
    non_existent = os.path.join(edge_test_dir, 'does_not_exist.txt')
    target = os.path.join(edge_test_dir, 'target')
    os.makedirs(target, exist_ok=True)
    
    try:
        result = sos.mv(non_existent, target)
        print(f"  Unexpected success: {result}")
    except Exception as e:
        print(f"  ✓ Expected error: {type(e).__name__}: {e}")
    
    # Test Case 2: Moving to non-existent directory (should create it)
    print("\n2. Testing move to non-existent directory:")
    test_file = os.path.join(edge_test_dir, 'test_file.txt')
    with open(test_file, 'w') as f:
        f.write('Test content')
    
    non_existent_dir = os.path.join(edge_test_dir, 'new_directory')
    print(f"  Source exists: {os.path.exists(test_file)}")
    print(f"  Target exists: {os.path.exists(non_existent_dir)}")
    
    try:
        result = sos.mv(test_file, non_existent_dir)
        print(f"  ✓ Move successful")
        print(f"  Target created: {os.path.exists(non_existent_dir)}")
        print(f"  File moved: {os.path.exists(os.path.join(non_existent_dir, 'test_file.txt'))}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    # Test Case 3: Moving file with same name (overwrite behavior)
    print("\n3. Testing overwrite behavior:")
    source_file = os.path.join(edge_test_dir, 'duplicate.txt')
    target_dir = os.path.join(edge_test_dir, 'target_with_duplicate')
    target_file = os.path.join(target_dir, 'duplicate.txt')
    
    os.makedirs(target_dir, exist_ok=True)
    
    # Create source file
    with open(source_file, 'w') as f:
        f.write('Source content')
    
    # Create existing target file
    with open(target_file, 'w') as f:
        f.write('Target content')
    
    print(f"  Source content: '{open(source_file).read()}'")
    print(f"  Target content: '{open(target_file).read()}'")
    
    try:
        result = sos.mv(source_file, target_dir)
        print(f"  ✓ Move successful")
        if os.path.exists(target_file):
            final_content = open(target_file).read()
            print(f"  Final content: '{final_content}'")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    # Test Case 4: Empty file
    print("\n4. Testing empty file:")
    empty_file = os.path.join(edge_test_dir, 'empty.txt')
    empty_target = os.path.join(edge_test_dir, 'empty_target')
    os.makedirs(empty_target, exist_ok=True)
    
    # Create empty file
    with open(empty_file, 'w') as f:
        pass  # Create empty file
    
    size_before = os.path.getsize(empty_file)
    print(f"  Empty file size: {size_before} bytes")
    
    try:
        result = sos.mv(empty_file, empty_target)
        print(f"  ✓ Empty file moved successfully")
        
        moved_file = os.path.join(empty_target, 'empty.txt')
        if os.path.exists(moved_file):
            size_after = os.path.getsize(moved_file)
            print(f"  Moved file size: {size_after} bytes")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    # Test Case 5: File with special characters in name
    print("\n5. Testing file with special characters:")
    special_file = os.path.join(edge_test_dir, 'file with spaces & symbols!@#.txt')
    special_target = os.path.join(edge_test_dir, 'special_target')
    os.makedirs(special_target, exist_ok=True)
    
    with open(special_file, 'w') as f:
        f.write('Content with special filename')
    
    print(f"  Special filename: '{os.path.basename(special_file)}'")
    
    try:
        result = sos.mv(special_file, special_target)
        print(f"  ✓ Special filename moved successfully")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    print(f"\nEdge case testing complete.")

5. Cleanup
----------

Let’s clean up all the temporary files and directories created during
this demonstration.

.. code:: ipython3

    # Example 9: Cleanup temporary files and directories
    print("Cleaning up temporary files and directories:")
    print("=" * 45)
    
    # Calculate total size before cleanup
    def get_directory_size(directory):
        """Calculate total size of directory and its contents."""
        total_size = 0
        if os.path.exists(directory):
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        return total_size
    
    # Get size before cleanup
    total_size_before = get_directory_size(temp_dir)
    print(f"Total size before cleanup: {total_size_before} bytes ({total_size_before/1024:.2f} KB)")
    
    # Count files and directories
    file_count = 0
    dir_count = 0
    
    if os.path.exists(temp_dir):
        for root, dirs, files in os.walk(temp_dir):
            file_count += len(files)
            dir_count += len(dirs)
    
    print(f"Files to clean: {file_count}")
    print(f"Directories to clean: {dir_count}")
    
    # Show directory structure before cleanup
    print(f"\nDirectory structure before cleanup:")
    def show_tree(directory, prefix="", max_depth=2, current_depth=0):
        """Show directory tree structure."""
        if current_depth >= max_depth or not os.path.exists(directory):
            return
        
        try:
            items = sorted(os.listdir(directory))
            for i, item in enumerate(items):
                item_path = os.path.join(directory, item)
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if os.path.isdir(item_path):
                    print(f"{prefix}{current_prefix}{item}/")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    show_tree(item_path, next_prefix, max_depth, current_depth + 1)
                else:
                    size = os.path.getsize(item_path)
                    print(f"{prefix}{current_prefix}{item} ({size} bytes)")
        except (OSError, PermissionError):
            print(f"{prefix}└── [Permission denied]")
    
    show_tree(temp_dir)
    
    # Perform cleanup
    print(f"\nPerforming cleanup...")
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"✓ Successfully removed temporary directory: {temp_dir}")
            print(f"✓ Cleaned up {file_count} files and {dir_count} directories")
            print(f"✓ Freed {total_size_before} bytes ({total_size_before/1024:.2f} KB) of space")
        else:
            print(f"✓ Temporary directory already cleaned up")
            
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
    
    # Verify cleanup
    print(f"\nVerifying cleanup:")
    if not os.path.exists(temp_dir):
        print(f"✓ Temporary directory successfully removed")
    else:
        remaining_files = sum([len(files) for r, d, files in os.walk(temp_dir)])
        print(f"⚠ Temporary directory still exists with {remaining_files} files")
    
    print(f"\nCleanup complete!")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.os`` module:

Core Functionality
~~~~~~~~~~~~~~~~~~

-  **``mv``**: Safe file and directory movement operations

   -  Automatic target directory creation
   -  Cross-platform compatibility
   -  Error handling and reporting
   -  Support for various file types

Key Features
~~~~~~~~~~~~

1. **Safety**: Proper error handling prevents data loss
2. **Convenience**: Automatic directory creation when needed
3. **Reliability**: Consistent behavior across different operating
   systems
4. **Scientific Focus**: Designed for research data management workflows

Practical Applications Demonstrated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Basic File Operations**: Moving individual files and handling
   errors
-  **File Organization**: Categorizing and organizing files by type
-  **Scientific Workflows**: Managing experimental data and analysis
   files
-  **Data Management**: Archiving, backup, and cleanup procedures
-  **Edge Case Handling**: Robust behavior with various file conditions

Common Use Cases
~~~~~~~~~~~~~~~~

-  **Experimental Data Organization**: Organizing data files by date,
   experiment, or type
-  **File Cleanup**: Moving processed files to appropriate directories
-  **Archive Management**: Moving old files to archive directories
-  **Workflow Automation**: Integrating file operations into analysis
   pipelines
-  **Project Organization**: Structuring research project directories

Best Practices Illustrated
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Test Operations**: Always verify file movements completed
   successfully
-  **Error Handling**: Graceful handling of permission and path issues
-  **Directory Structure**: Maintaining organized, logical file
   hierarchies
-  **Cleanup Procedures**: Proper cleanup of temporary files and
   directories
-  **Safety Checks**: Verifying source and target locations before
   operations

Integration with Scientific Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Data Pipeline Management**: Moving files between processing stages
-  **Result Organization**: Structuring output files for analysis
-  **Backup Strategies**: Implementing systematic backup procedures
-  **Collaboration**: Organizing files for team access and sharing
-  **Reproducibility**: Maintaining consistent file organization for
   reproducible research

The ``scitex.os`` module provides essential file system operations
tailored for scientific computing environments, with emphasis on safety,
reliability, and integration with research workflows.
