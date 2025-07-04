05 SciTeX Path
==============

.. note::
   This page is generated from the Jupyter notebook `05_scitex_path.ipynb <https://github.com/scitex/scitex/blob/main/examples/05_scitex_path.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 05_scitex_path.ipynb


This comprehensive notebook demonstrates the SciTeX path module
capabilities, covering path manipulation, file system operations, and
directory management.

Features Covered
----------------

Path Operations
~~~~~~~~~~~~~~~

-  Path cleaning and normalization
-  Directory and file finding
-  Path splitting and parsing
-  Current directory utilities

File System Navigation
~~~~~~~~~~~~~~~~~~~~~~

-  Git repository detection
-  Module path resolution
-  Size calculations
-  Version management

Advanced Features
~~~~~~~~~~~~~~~~~

-  Smart path creation
-  Version incrementing
-  Latest file detection
-  Package data access

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import os
    import tempfile
    import shutil
    
    # Set up example data directory
    data_dir = Path("./path_examples")
    data_dir.mkdir(exist_ok=True)
    
    print("SciTeX Path Management Tutorial - Ready to begin!")
    print(f"Available path functions: {len(scitex.path.__all__)}")
    print(f"Functions: {scitex.path.__all__}")

Part 1: Basic Path Operations
-----------------------------

1.1 Current Path Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Get current path information
    print("Current Path Information:")
    print("=" * 30)
    
    try:
        # Get this path (current file/notebook location)
        this_path = scitex.path.this_path()
        print(f"This path: {this_path}")
        
        # Alternative method
        this_path_alt = scitex.path.get_this_path()
        print(f"This path (alt): {this_path_alt}")
        
        # Current working directory
        current_dir = Path.cwd()
        print(f"Current working directory: {current_dir}")
        
        # Path relationships
        if this_path:
            print(f"Parent directory: {Path(this_path).parent}")
            print(f"File name: {Path(this_path).name}")
            print(f"File stem: {Path(this_path).stem}")
            print(f"File suffix: {Path(this_path).suffix}")
        
    except Exception as e:
        print(f"Error getting path information: {e}")
    
    # Demonstrate path existence
    print("\nPath Existence Checks:")
    print("=" * 25)
    
    test_paths = [
        "../src",
        "../src/scitex",
        "../src/scitex/path",
        "./path_examples",
        "./nonexistent_directory",
        "../requirements.txt",
        "../nonexistent_file.txt"
    ]
    
    for path_str in test_paths:
        path = Path(path_str)
        print(f"'{path_str}':")
        print(f"  Exists: {path.exists()}")
        print(f"  Is file: {path.is_file()}")
        print(f"  Is directory: {path.is_dir()}")
        print(f"  Absolute: {path.absolute()}")
        print()

1.2 Path Cleaning and Normalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Path cleaning examples
    messy_paths = [
        "./data/../data/./file.txt",
        "/home/user//double//slashes///file.txt",
        "~/data/./current/./directory/file.txt",
        "..\\windows\\style\\path\\file.txt",
        "relative/path/with/../redundant/../elements/file.txt",
        "/absolute/path/with/./current/./references/file.txt"
    ]
    
    print("Path Cleaning:")
    print("=" * 18)
    
    for messy_path in messy_paths:
        try:
            cleaned = scitex.path.clean(messy_path)
            print(f"Original: '{messy_path}'")
            print(f"Cleaned:  '{cleaned}'")
            print(f"Resolved: '{Path(messy_path).resolve()}'")
            print()
        except Exception as e:
            print(f"Error cleaning '{messy_path}': {e}")
            print()

1.3 Path Splitting and Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Path splitting examples
    example_paths = [
        "/home/user/documents/project/data/file.csv",
        "C:\\Users\\Name\\Documents\\project\\results.xlsx",
        "../data/experiments/2024/experiment_001.json",
        "./models/trained_model_v2.pkl",
        "https://example.com/data/dataset.zip"
    ]
    
    print("Path Splitting:")
    print("=" * 18)
    
    for path_str in example_paths:
        try:
            split_result = scitex.path.split(path_str)
            print(f"Path: '{path_str}'")
            print(f"Split result: {split_result}")
            
            # Also show pathlib parsing
            path_obj = Path(path_str)
            print(f"Parts: {path_obj.parts if hasattr(path_obj, 'parts') else 'N/A'}")
            print(f"Parent: {path_obj.parent}")
            print(f"Name: {path_obj.name}")
            print(f"Stem: {path_obj.stem}")
            print(f"Suffix: {path_obj.suffix}")
            print()
        except Exception as e:
            print(f"Error splitting '{path_str}': {e}")
            print()

Part 2: File and Directory Finding
----------------------------------

2.1 Directory and File Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create test directory structure
    test_structure = {
        "project_root": {
            "src": {
                "module1": ["__init__.py", "main.py", "utils.py"],
                "module2": ["__init__.py", "core.py", "helpers.py"]
            },
            "data": {
                "raw": ["dataset1.csv", "dataset2.json"],
                "processed": ["clean_data.pkl", "features.npy"]
            },
            "tests": ["test_module1.py", "test_module2.py"],
            "docs": ["README.md", "tutorial.md"]
        }
    }
    
    def create_test_structure(base_path, structure):
        """Create a test directory structure."""
        for name, content in structure.items():
            current_path = base_path / name
            current_path.mkdir(exist_ok=True)
            
            if isinstance(content, dict):
                create_test_structure(current_path, content)
            elif isinstance(content, list):
                for filename in content:
                    file_path = current_path / filename
                    file_path.write_text(f"# Content of {filename}\nprint('Hello from {filename}')")
    
    # Create the test structure
    test_root = data_dir / "test_project"
    create_test_structure(test_root, test_structure)
    
    print("Test Directory Structure Created:")
    print("=" * 35)
    
    # Function to print directory tree
    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth > max_depth:
            return
        
        items = sorted(path.iterdir()) if path.is_dir() else []
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, max_depth, current_depth + 1)
    
    print_tree(test_root)

.. code:: ipython3

    # Directory finding
    print("\nDirectory Finding:")
    print("=" * 20)
    
    directories_to_find = ['src', 'data', 'tests', 'docs', 'nonexistent']
    
    for dir_name in directories_to_find:
        try:
            found_dir = scitex.path.find_dir(dir_name, str(test_root))
            print(f"Looking for '{dir_name}': {found_dir}")
        except Exception as e:
            print(f"Error finding directory '{dir_name}': {e}")
    
    # File finding
    print("\nFile Finding:")
    print("=" * 15)
    
    files_to_find = ['main.py', 'utils.py', 'dataset1.csv', 'README.md', 'nonexistent.txt']
    
    for file_name in files_to_find:
        try:
            found_file = scitex.path.find_file(file_name, str(test_root))
            print(f"Looking for '{file_name}': {found_file}")
        except Exception as e:
            print(f"Error finding file '{file_name}': {e}")
    
    # Git root finding
    print("\nGit Root Finding:")
    print("=" * 20)
    
    try:
        # Try to find git root from current directory
        git_root = scitex.path.find_git_root()
        print(f"Git root found: {git_root}")
        
        if git_root:
            git_path = Path(git_root)
            print(f"Git directory exists: {(git_path / '.git').exists()}")
            print(f"Git root name: {git_path.name}")
    except Exception as e:
        print(f"Error finding git root: {e}")
    
    # Try from test directory (should not find git)
    try:
        git_root_from_test = scitex.path.find_git_root(str(test_root))
        print(f"Git root from test dir: {git_root_from_test}")
    except Exception as e:
        print(f"No git root from test directory (expected): {e}")

Part 3: Size Calculations and File Information
----------------------------------------------

3.1 File and Directory Sizes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create files of different sizes for testing
    size_test_dir = data_dir / "size_tests"
    size_test_dir.mkdir(exist_ok=True)
    
    # Create files with different content sizes
    file_contents = {
        "small.txt": "Small file content",
        "medium.txt": "Medium file content\n" * 100,
        "large.txt": "Large file content with lots of text\n" * 1000,
        "binary.dat": bytes(range(256)) * 100,  # Binary content
        "empty.txt": ""
    }
    
    for filename, content in file_contents.items():
        filepath = size_test_dir / filename
        if isinstance(content, str):
            filepath.write_text(content)
        else:
            filepath.write_bytes(content)
    
    print("File Size Analysis:")
    print("=" * 22)
    
    for filename in file_contents.keys():
        filepath = size_test_dir / filename
        
        try:
            # Using scitex.path.getsize
            scitex_size = scitex.path.getsize(str(filepath))
            
            # Using pathlib for comparison
            pathlib_size = filepath.stat().st_size
            
            # Readable format
            readable_size = scitex.str.readable_bytes(scitex_size)
            
            print(f"{filename}:")
            print(f"  SciTeX size: {scitex_size} bytes")
            print(f"  Pathlib size: {pathlib_size} bytes")
            print(f"  Readable: {readable_size}")
            print(f"  Match: {scitex_size == pathlib_size}")
            print()
            
        except Exception as e:
            print(f"Error getting size for {filename}: {e}")
            print()
    
    # Directory size calculation
    print("Directory Size Analysis:")
    print("=" * 26)
    
    directories_to_analyze = [size_test_dir, test_root, data_dir]
    
    for directory in directories_to_analyze:
        try:
            # Calculate total directory size
            total_size = 0
            file_count = 0
            
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    size = scitex.path.getsize(str(file_path))
                    total_size += size
                    file_count += 1
            
            readable_total = scitex.str.readable_bytes(total_size)
            
            print(f"Directory: {directory.name}")
            print(f"  Total size: {total_size} bytes ({readable_total})")
            print(f"  File count: {file_count}")
            print(f"  Average file size: {total_size/file_count if file_count > 0 else 0:.1f} bytes")
            print()
            
        except Exception as e:
            print(f"Error analyzing directory {directory}: {e}")
            print()

Part 4: Version Management
--------------------------

4.1 Version Incrementing and Latest File Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create versioned files for testing
    version_test_dir = data_dir / "version_tests"
    version_test_dir.mkdir(exist_ok=True)
    
    # Create files with version numbers
    versioned_files = [
        "experiment_v1.txt",
        "experiment_v2.txt",
        "experiment_v3.txt",
        "model_v001.pkl",
        "model_v002.pkl",
        "model_v010.pkl",
        "data_1.csv",
        "data_2.csv",
        "data_11.csv",
        "results_2024_01.json",
        "results_2024_02.json",
        "results_2024_10.json"
    ]
    
    # Create the files with timestamps to test ordering
    import time
    
    for i, filename in enumerate(versioned_files):
        filepath = version_test_dir / filename
        filepath.write_text(f"Content of {filename}\nVersion: {i+1}\nCreated: {time.time()}")
        time.sleep(0.01)  # Small delay to ensure different timestamps
    
    print("Version Management:")
    print("=" * 20)
    
    # List all files with their timestamps
    print("Created versioned files:")
    for filename in versioned_files:
        filepath = version_test_dir / filename
        if filepath.exists():
            stat = filepath.stat()
            mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
            print(f"  {filename} (modified: {mod_time})")
    
    # Test version incrementing
    print("\nVersion Incrementing:")
    print("=" * 23)
    
    base_names = [
        "experiment_v3.txt",
        "model_v010.pkl",
        "data_11.csv",
        "results_2024_10.json",
        "new_file.txt"  # File that doesn't exist yet
    ]
    
    for base_name in base_names:
        try:
            base_path = version_test_dir / base_name
            incremented = scitex.path.increment_version(str(base_path))
            print(f"'{base_name}' -> '{Path(incremented).name}'")
        except Exception as e:
            print(f"Error incrementing version for '{base_name}': {e}")
    
    # Test finding latest files
    print("\nFinding Latest Files:")
    print("=" * 23)
    
    patterns = [
        "experiment_v*.txt",
        "model_v*.pkl",
        "data_*.csv",
        "results_*.json"
    ]
    
    for pattern in patterns:
        try:
            latest = scitex.path.find_latest(pattern, str(version_test_dir))
            print(f"Pattern '{pattern}': {Path(latest).name if latest else 'None found'}")
        except Exception as e:
            print(f"Error finding latest for pattern '{pattern}': {e}")

Part 5: Smart Path Creation and Management
------------------------------------------

5.1 Smart Path (spath) Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Smart path creation and management
    spath_test_dir = data_dir / "spath_tests"
    spath_test_dir.mkdir(exist_ok=True)
    
    print("Smart Path (spath) Operations:")
    print("=" * 33)
    
    # Test smart path creation
    test_scenarios = [
        {
            'description': 'Simple file creation',
            'base': 'simple_file.txt',
            'content': 'Simple content'
        },
        {
            'description': 'File with timestamp',
            'base': 'timestamped_file.log',
            'content': 'Log entry with timestamp'
        },
        {
            'description': 'Data file with metadata',
            'base': 'data_export.csv',
            'content': 'col1,col2,col3\n1,2,3\n4,5,6'
        },
        {
            'description': 'Configuration file',
            'base': 'config.json',
            'content': '{"setting1": "value1", "setting2": 42}'
        }
    ]
    
    for scenario in test_scenarios:
        try:
            print(f"\n{scenario['description']}:")
            
            # Create smart path
            base_path = spath_test_dir / scenario['base']
            spath = scitex.path.mk_spath(str(base_path))
            
            print(f"  Base path: {scenario['base']}")
            print(f"  Smart path: {Path(spath).name}")
            
            # Write content to the smart path
            with open(spath, 'w') as f:
                f.write(scenario['content'])
            
            print(f"  File created: {Path(spath).exists()}")
            print(f"  File size: {Path(spath).stat().st_size} bytes")
            
            # Test getting the spath
            retrieved_spath = scitex.path.get_spath(str(base_path))
            print(f"  Retrieved spath: {Path(retrieved_spath).name if retrieved_spath else 'None'}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Demonstrate spath behavior with existing files
    print("\nSmart Path with Existing Files:")
    print("=" * 34)
    
    # Create the same file multiple times to see versioning
    base_name = "repeated_file.txt"
    base_path = spath_test_dir / base_name
    
    for i in range(3):
        try:
            spath = scitex.path.mk_spath(str(base_path))
            content = f"Content version {i+1}\nCreated at iteration {i+1}"
            
            with open(spath, 'w') as f:
                f.write(content)
            
            print(f"Iteration {i+1}: Created {Path(spath).name}")
            
        except Exception as e:
            print(f"Iteration {i+1}: Error - {e}")
    
    # List all files created
    print("\nFiles created in spath_tests:")
    for file_path in sorted(spath_test_dir.iterdir()):
        if file_path.is_file():
            size = file_path.stat().st_size
            readable_size = scitex.str.readable_bytes(size)
            print(f"  {file_path.name} ({readable_size})")

Part 6: Package Data and Module Paths
-------------------------------------

6.1 Module Path Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Module path resolution
    print("Module Path Resolution:")
    print("=" * 25)
    
    # Test with various packages and modules
    modules_to_test = [
        'scitex',
        'scitex.path',
        'scitex.str',
        'scitex.gen',
        'numpy',
        'pandas',
        'pathlib',
        'os',
        'sys'
    ]
    
    for module_name in modules_to_test:
        try:
            # Try to get module path using scitex
            module_path = scitex.path.get_data_path_from_a_package(module_name)
            print(f"'{module_name}': {module_path}")
            
            if module_path and Path(module_path).exists():
                path_obj = Path(module_path)
                print(f"  Exists: {path_obj.exists()}")
                print(f"  Is directory: {path_obj.is_dir()}")
                print(f"  Parent: {path_obj.parent.name}")
            
        except Exception as e:
            print(f"'{module_name}': Error - {e}")
        print()
    
    # Alternative method using importlib for comparison
    print("Comparison with importlib:")
    print("=" * 28)
    
    import importlib
    import importlib.util
    
    for module_name in ['scitex', 'numpy', 'pandas']:
        try:
            # Using importlib
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                importlib_path = Path(spec.origin).parent
                print(f"'{module_name}' (importlib): {importlib_path}")
            else:
                print(f"'{module_name}' (importlib): Not found")
                
            # Using scitex for comparison
            scitex_path = scitex.path.get_data_path_from_a_package(module_name)
            print(f"'{module_name}' (scitex): {scitex_path}")
            
            # Check if paths match
            if spec and spec.origin and scitex_path:
                match = str(importlib_path) == str(scitex_path)
                print(f"  Paths match: {match}")
            
        except Exception as e:
            print(f"'{module_name}': Comparison error - {e}")
        print()

Part 7: Practical Applications
------------------------------

7.1 Project Organization Tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create a comprehensive project organization tool
    class ProjectOrganizer:
        def __init__(self, project_root):
            self.project_root = Path(project_root)
            self.analysis_results = {}
        
        def analyze_project_structure(self):
            """Analyze the project directory structure."""
            print(f"Analyzing project: {self.project_root.name}")
            print("=" * 40)
            
            if not self.project_root.exists():
                print(f"Project root does not exist: {self.project_root}")
                return
            
            # Basic statistics
            total_files = 0
            total_dirs = 0
            total_size = 0
            file_types = {}
            
            for item in self.project_root.rglob('*'):
                if item.is_file():
                    total_files += 1
                    try:
                        size = scitex.path.getsize(str(item))
                        total_size += size
                        
                        # Track file types
                        suffix = item.suffix.lower() or 'no_extension'
                        if suffix not in file_types:
                            file_types[suffix] = {'count': 0, 'size': 0}
                        file_types[suffix]['count'] += 1
                        file_types[suffix]['size'] += size
                    except:
                        pass
                elif item.is_dir():
                    total_dirs += 1
            
            self.analysis_results = {
                'total_files': total_files,
                'total_dirs': total_dirs,
                'total_size': total_size,
                'file_types': file_types
            }
            
            # Print results
            print(f"Total files: {total_files}")
            print(f"Total directories: {total_dirs}")
            print(f"Total size: {scitex.str.readable_bytes(total_size)}")
            
            # File type breakdown
            print("\nFile types:")
            for suffix, info in sorted(file_types.items(), key=lambda x: x[1]['size'], reverse=True):
                readable_size = scitex.str.readable_bytes(info['size'])
                print(f"  {suffix}: {info['count']} files ({readable_size})")
        
        def find_large_files(self, threshold_mb=1):
            """Find files larger than threshold."""
            threshold_bytes = threshold_mb * 1024 * 1024
            large_files = []
            
            print(f"\nFiles larger than {threshold_mb} MB:")
            print("-" * 30)
            
            for item in self.project_root.rglob('*'):
                if item.is_file():
                    try:
                        size = scitex.path.getsize(str(item))
                        if size > threshold_bytes:
                            relative_path = item.relative_to(self.project_root)
                            readable_size = scitex.str.readable_bytes(size)
                            large_files.append((str(relative_path), size, readable_size))
                    except:
                        pass
            
            # Sort by size (largest first)
            large_files.sort(key=lambda x: x[1], reverse=True)
            
            if large_files:
                for filepath, size, readable_size in large_files:
                    print(f"  {filepath}: {readable_size}")
            else:
                print(f"  No files larger than {threshold_mb} MB found")
            
            return large_files
        
        def find_duplicate_names(self):
            """Find files with duplicate names (potentially confusing)."""
            name_map = {}
            
            for item in self.project_root.rglob('*'):
                if item.is_file():
                    name = item.name
                    if name not in name_map:
                        name_map[name] = []
                    name_map[name].append(item.relative_to(self.project_root))
            
            duplicates = {name: paths for name, paths in name_map.items() if len(paths) > 1}
            
            print("\nFiles with duplicate names:")
            print("-" * 30)
            
            if duplicates:
                for name, paths in duplicates.items():
                    print(f"  {name}:")
                    for path in paths:
                        print(f"    {path}")
                    print()
            else:
                print("  No duplicate file names found")
            
            return duplicates
        
        def suggest_cleanup(self):
            """Suggest cleanup actions."""
            print("\nCleanup Suggestions:")
            print("=" * 22)
            
            suggestions = []
            
            # Check for common temporary files
            temp_patterns = ['*.tmp', '*.temp', '*~', '*.bak', '*.log']
            temp_files = []
            
            for pattern in temp_patterns:
                temp_files.extend(self.project_root.rglob(pattern))
            
            if temp_files:
                total_temp_size = sum(scitex.path.getsize(str(f)) for f in temp_files if f.is_file())
                suggestions.append(f"Remove {len(temp_files)} temporary files (saves {scitex.str.readable_bytes(total_temp_size)})")
            
            # Check for large files
            large_files = self.find_large_files(5)  # Files > 5MB
            if large_files:
                suggestions.append(f"Review {len(large_files)} large files (consider compression or archiving)")
            
            # Check file type distribution
            if self.analysis_results:
                file_types = self.analysis_results['file_types']
                if '.log' in file_types and file_types['.log']['count'] > 10:
                    suggestions.append(f"Archive or clean {file_types['.log']['count']} log files")
            
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
            else:
                print("  No obvious cleanup opportunities found")
    
    # Test the project organizer
    organizer = ProjectOrganizer(test_root)
    organizer.analyze_project_structure()
    organizer.find_large_files(0.001)  # Very small threshold for demo
    organizer.find_duplicate_names()
    organizer.suggest_cleanup()

7.2 Backup and Version Management System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create a backup and version management system
    class BackupManager:
        def __init__(self, source_dir, backup_dir):
            self.source_dir = Path(source_dir)
            self.backup_dir = Path(backup_dir)
            self.backup_dir.mkdir(exist_ok=True)
        
        def create_backup(self, description=""):
            """Create a timestamped backup."""
            import datetime
            
            # Create timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create backup name
            backup_name = f"backup_{timestamp}"
            if description:
                safe_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_desc = safe_desc.replace(' ', '_')
                backup_name += f"_{safe_desc}"
            
            backup_path = self.backup_dir / backup_name
            
            print(f"Creating backup: {backup_name}")
            
            try:
                # Copy directory structure
                shutil.copytree(self.source_dir, backup_path)
                
                # Calculate backup size
                backup_size = sum(
                    scitex.path.getsize(str(f)) 
                    for f in backup_path.rglob('*') 
                    if f.is_file()
                )
                
                print(f"✓ Backup created successfully")
                print(f"  Location: {backup_path}")
                print(f"  Size: {scitex.str.readable_bytes(backup_size)}")
                
                return backup_path
                
            except Exception as e:
                print(f"✗ Backup failed: {e}")
                return None
        
        def list_backups(self):
            """List all available backups."""
            backups = []
            
            for item in self.backup_dir.iterdir():
                if item.is_dir() and item.name.startswith('backup_'):
                    # Get backup info
                    stat = item.stat()
                    created = datetime.datetime.fromtimestamp(stat.st_ctime)
                    
                    # Calculate size
                    size = sum(
                        scitex.path.getsize(str(f)) 
                        for f in item.rglob('*') 
                        if f.is_file()
                    )
                    
                    backups.append({
                        'name': item.name,
                        'path': item,
                        'created': created,
                        'size': size
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            print(f"Available backups ({len(backups)} total):")
            print("=" * 35)
            
            if backups:
                for backup in backups:
                    created_str = backup['created'].strftime("%Y-%m-%d %H:%M:%S")
                    size_str = scitex.str.readable_bytes(backup['size'])
                    print(f"  {backup['name']}")
                    print(f"    Created: {created_str}")
                    print(f"    Size: {size_str}")
                    print()
            else:
                print("  No backups found")
            
            return backups
        
        def cleanup_old_backups(self, keep_count=5):
            """Remove old backups, keeping only the most recent ones."""
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                print(f"Only {len(backups)} backups found, no cleanup needed")
                return
            
            backups_to_remove = backups[keep_count:]
            total_freed = 0
            
            print(f"\nRemoving {len(backups_to_remove)} old backups:")
            
            for backup in backups_to_remove:
                try:
                    shutil.rmtree(backup['path'])
                    total_freed += backup['size']
                    print(f"  ✓ Removed {backup['name']}")
                except Exception as e:
                    print(f"  ✗ Failed to remove {backup['name']}: {e}")
            
            print(f"\nFreed space: {scitex.str.readable_bytes(total_freed)}")
    
    # Test the backup manager
    backup_dir = data_dir / "backups"
    backup_manager = BackupManager(test_root, backup_dir)
    
    # Create a few backups
    backup_manager.create_backup("initial_state")
    time.sleep(1)  # Ensure different timestamps
    backup_manager.create_backup("after_modifications")
    time.sleep(1)
    backup_manager.create_backup("final_version")
    
    # List all backups
    print("\n" + "="*50)
    backup_manager.list_backups()
    
    # Test cleanup (keep only 2 most recent)
    print("\n" + "="*50)
    backup_manager.cleanup_old_backups(keep_count=2)

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive path management
capabilities of the SciTeX path module:

Key Features Covered:
~~~~~~~~~~~~~~~~~~~~~

1. **Path Operations**: ``this_path()``, ``clean()``, ``split()`` for
   basic path handling
2. **File Finding**: ``find_file()``, ``find_dir()``,
   ``find_git_root()`` for navigation
3. **Size Calculations**: ``getsize()`` for file and directory size
   analysis
4. **Version Management**: ``increment_version()``, ``find_latest()``
   for file versioning
5. **Smart Paths**: ``mk_spath()``, ``get_spath()`` for intelligent path
   creation
6. **Module Resolution**: ``get_data_path_from_a_package()`` for package
   paths
7. **Project Organization**: Comprehensive directory analysis and
   cleanup
8. **Backup Management**: Automated backup creation and maintenance

Best Practices:
~~~~~~~~~~~~~~~

-  Use **path cleaning** functions to normalize paths across platforms
-  Apply **smart path creation** to avoid overwriting important files
-  Implement **version management** for iterative development
-  Use **file finding** utilities for robust project navigation
-  Apply **size analysis** for storage optimization
-  Create **backup systems** for important project data
-  Use **git root detection** for repository-aware operations
-  Implement **project organization** tools for maintenance

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
