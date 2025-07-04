19 SciTeX Db
============

.. note::
   This page is generated from the Jupyter notebook `19_scitex_db.ipynb <https://github.com/scitex/scitex/blob/main/examples/19_scitex_db.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 19_scitex_db.ipynb


This notebook demonstrates the complete functionality of the
``scitex.db`` module, which provides database operations and utilities
for scientific data management.

Module Overview
---------------

The ``scitex.db`` module includes: - SQLite3 database management with
comprehensive mixins - PostgreSQL database operations - Database
inspection and analysis tools - Duplicate data detection and removal

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import sqlite3
    import pandas as pd
    import numpy as np
    import tempfile
    import os
    from pathlib import Path
    
    # Import scitex db module
    import scitex.db as sdb
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("Available classes/functions in scitex.db:")
    db_attrs = [attr for attr in dir(sdb) if not attr.startswith('_')]
    for i, attr in enumerate(db_attrs):
        print(f"{i+1:2d}. {attr}")

1. Database Inspection Tools
----------------------------

Creating Sample Database
~~~~~~~~~~~~~~~~~~~~~~~~

Let’s start by creating a sample database for demonstration purposes.

.. code:: ipython3

    # Example 1: Create sample database for demonstration
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = temp_db.name
    temp_db.close()
    
    print(f"Creating sample database at: {db_path}")
    
    # Create sample data
    np.random.seed(42)
    
    # Experimental data table
    experiments_data = {
        'experiment_id': range(1, 21),
        'subject_id': [f'S{i:03d}' for i in np.random.randint(1, 11, 20)],
        'condition': np.random.choice(['control', 'treatment_A', 'treatment_B'], 20),
        'measurement': np.random.normal(100, 15, 20),
        'timestamp': pd.date_range('2024-01-01', periods=20, freq='D')
    }
    
    # Subjects metadata table
    subjects_data = {
        'subject_id': [f'S{i:03d}' for i in range(1, 11)],
        'age': np.random.randint(18, 65, 10),
        'gender': np.random.choice(['M', 'F'], 10),
        'group': np.random.choice(['A', 'B'], 10)
    }
    
    # Time series data table
    time_series_data = []
    for exp_id in range(1, 6):  # First 5 experiments have time series
        n_points = 100
        time_points = np.linspace(0, 10, n_points)
        signal = np.sin(2 * np.pi * time_points) + 0.1 * np.random.randn(n_points)
        for i, (t, s) in enumerate(zip(time_points, signal)):
            time_series_data.append({
                'experiment_id': exp_id,
                'time_point': i,
                'time_value': t,
                'signal_value': s
            })
    
    # Create database and tables
    conn = sqlite3.connect(db_path)
    
    # Experiments table
    experiments_df = pd.DataFrame(experiments_data)
    experiments_df.to_sql('experiments', conn, if_exists='replace', index=False)
    
    # Subjects table
    subjects_df = pd.DataFrame(subjects_data)
    subjects_df.to_sql('subjects', conn, if_exists='replace', index=False)
    
    # Time series table
    time_series_df = pd.DataFrame(time_series_data)
    time_series_df.to_sql('time_series', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print(f"Sample database created with {len(experiments_df)} experiments")
    print(f"Number of subjects: {len(subjects_df)}")
    print(f"Number of time series points: {len(time_series_df)}")

Database Inspection
~~~~~~~~~~~~~~~~~~~

Now let’s use the ``inspect`` function to examine our database.

.. code:: ipython3

    # Example 2: Database inspection
    print("Database Inspection:")
    print("=" * 20)
    
    try:
        # Inspect all tables
        inspection_results = sdb.inspect(db_path, verbose=True)
        
        print(f"\nNumber of tables inspected: {len(inspection_results)}")
        
        # Show structure of each inspection result
        for i, result in enumerate(inspection_results):
            print(f"\nTable {i+1} structure:")
            print(f"Index: {result.index.names}")
            print(f"Columns: {list(result.columns)}")
            print(f"Shape: {result.shape}")
            
    except Exception as e:
        print(f"Error during inspection: {e}")
        print("This might require additional dependencies or configuration.")

.. code:: ipython3

    # Example 3: Inspect specific tables
    print("Inspecting specific tables:")
    print("=" * 30)
    
    try:
        # Inspect only experiments table
        experiments_inspection = sdb.inspect(db_path, table_names=['experiments'], verbose=True)
        
        # Inspect only subjects table
        subjects_inspection = sdb.inspect(db_path, table_names=['subjects'], verbose=True)
        
        print("\nSpecific table inspection completed.")
        
    except Exception as e:
        print(f"Error during specific table inspection: {e}")

2. SQLite3 Database Management
------------------------------

Basic SQLite3 Operations
~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate the comprehensive SQLite3 class functionality.

.. code:: ipython3

    # Example 4: SQLite3 database management
    print("SQLite3 Database Management:")
    print("=" * 30)
    
    try:
        # Initialize SQLite3 database manager
        db_manager = sdb.SQLite3(db_path)
        
        print(f"Database manager initialized for: {db_path}")
        print(f"SQLite3 class available methods:")
        
        # Show available methods
        methods = [method for method in dir(db_manager) if not method.startswith('_')]
        for i, method in enumerate(methods[:10]):  # Show first 10 methods
            print(f"  {i+1:2d}. {method}")
        if len(methods) > 10:
            print(f"  ... and {len(methods) - 10} more methods")
        
        # Call the database summary
        print("\nDatabase Summary:")
        summary = db_manager(print_summary=True, verbose=True)
        
    except Exception as e:
        print(f"Error with SQLite3 manager: {e}")
        print("This might require additional dependencies or configuration.")

Database Querying
~~~~~~~~~~~~~~~~~

Let’s demonstrate database querying capabilities.

.. code:: ipython3

    # Example 5: Database querying
    print("Database Querying Examples:")
    print("=" * 30)
    
    # Direct SQL queries for demonstration
    conn = sqlite3.connect(db_path)
    
    try:
        # Query 1: Basic select
        print("1. Basic SELECT query:")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiments LIMIT 5")
        results = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(experiments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Columns: {columns}")
        print("First 5 experiments:")
        for row in results:
            print(f"  {dict(zip(columns, row))}")
        
        # Query 2: Aggregation
        print("\n2. Aggregation query:")
        cursor.execute("""
            SELECT condition, 
                   COUNT(*) as count, 
                   AVG(measurement) as avg_measurement,
                   ROUND(AVG(measurement), 2) as avg_rounded
            FROM experiments 
            GROUP BY condition
        """)
        agg_results = cursor.fetchall()
        
        print("Results by condition:")
        for row in agg_results:
            print(f"  Condition: {row[0]}, Count: {row[1]}, Avg: {row[2]:.2f}")
        
        # Query 3: Join query
        print("\n3. JOIN query:")
        cursor.execute("""
            SELECT e.experiment_id, e.condition, e.measurement, s.age, s.gender
            FROM experiments e
            JOIN subjects s ON e.subject_id = s.subject_id
            LIMIT 5
        """)
        join_results = cursor.fetchall()
        
        print("Experiment data with subject info:")
        for row in join_results:
            print(f"  Exp {row[0]}: {row[1]}, measurement={row[2]:.1f}, subject: age={row[3]}, gender={row[4]}")
        
        # Query 4: Statistical analysis
        print("\n4. Statistical analysis:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_experiments,
                MIN(measurement) as min_measurement,
                MAX(measurement) as max_measurement,
                AVG(measurement) as mean_measurement,
                COUNT(DISTINCT subject_id) as unique_subjects
            FROM experiments
        """)
        stats = cursor.fetchone()
        
        print(f"Total experiments: {stats[0]}")
        print(f"Measurement range: [{stats[1]:.2f}, {stats[2]:.2f}]")
        print(f"Mean measurement: {stats[3]:.2f}")
        print(f"Unique subjects: {stats[4]}")
        
    except Exception as e:
        print(f"Error during querying: {e}")
        
    finally:
        conn.close()

3. Duplicate Detection and Removal
----------------------------------

Creating Data with Duplicates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s create a database with duplicate entries to demonstrate the
duplicate removal functionality.

.. code:: ipython3

    # Example 6: Create database with duplicates
    print("Creating database with duplicate entries:")
    print("=" * 45)
    
    # Create temporary database with duplicates
    temp_dup_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    dup_db_path = temp_dup_db.name
    temp_dup_db.close()
    
    # Create sample data with intentional duplicates
    np.random.seed(42)
    
    # Original data
    original_data = {
        'id': range(1, 21),
        'name': [f'Item_{i}' for i in range(1, 21)],
        'category': np.random.choice(['A', 'B', 'C'], 20),
        'value': np.random.randint(1, 100, 20),
        'date': pd.date_range('2024-01-01', periods=20, freq='D')
    }
    
    original_df = pd.DataFrame(original_data)
    
    # Create duplicates by repeating some rows
    duplicate_indices = [2, 5, 8, 12, 15]  # Duplicate these rows
    duplicated_rows = original_df.iloc[duplicate_indices].copy()
    duplicated_rows['id'] = range(21, 26)  # Give new IDs to duplicates
    
    # Combine original and duplicated data
    combined_df = pd.concat([original_df, duplicated_rows], ignore_index=True)
    
    # Create database with duplicates
    conn = sqlite3.connect(dup_db_path)
    combined_df.to_sql('test_data', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"Created database with duplicates at: {dup_db_path}")
    print(f"Original entries: {len(original_df)}")
    print(f"Duplicate entries added: {len(duplicated_rows)}")
    print(f"Total entries: {len(combined_df)}")
    
    # Show the data structure
    print("\nFirst few entries:")
    print(combined_df.head())
    
    print("\nDuplicated entries (different IDs, same other data):")
    for idx in duplicate_indices:
        original_row = original_df.iloc[idx]
        duplicate_row = duplicated_rows[duplicated_rows.index == duplicate_indices.index(idx)].iloc[0]
        print(f"Original: ID={original_row['id']}, Name={original_row['name']}, Category={original_row['category']}")
        print(f"Duplicate: ID={duplicate_row['id']}, Name={duplicate_row['name']}, Category={duplicate_row['category']}")
        print()

Duplicate Detection and Removal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let’s use the ``delete_duplicates`` function to identify and remove
duplicates.

.. code:: ipython3

    # Example 7: Duplicate detection and removal (dry run)
    print("Duplicate Detection and Removal:")
    print("=" * 35)
    
    try:
        # First, do a dry run to see what would be removed
        print("1. DRY RUN - Detecting duplicates:")
        print("-" * 35)
        
        # Exclude 'id' column from duplicate detection (since IDs are unique)
        columns_to_check = ['name', 'category', 'value', 'date']
        
        dry_run_result = sdb.delete_duplicates(
            dup_db_path,
            'test_data',
            columns=columns_to_check,
            dry_run=True
        )
        
        if dry_run_result:
            total_processed, total_duplicates = dry_run_result
            print(f"\nDry run results:")
            print(f"Total rows that would be processed: {total_processed}")
            print(f"Total duplicates that would be removed: {total_duplicates}")
        
        # Now do the actual removal
        print("\n2. ACTUAL REMOVAL - Removing duplicates:")
        print("-" * 40)
        
        actual_result = sdb.delete_duplicates(
            dup_db_path,
            'test_data',
            columns=columns_to_check,
            dry_run=False
        )
        
        if actual_result:
            total_processed, total_duplicates = actual_result
            print(f"\nActual removal results:")
            print(f"Total rows processed: {total_processed}")
            print(f"Total duplicates removed: {total_duplicates}")
        
        # Verify the results
        print("\n3. VERIFICATION - Checking results:")
        print("-" * 35)
        
        conn = sqlite3.connect(dup_db_path)
        remaining_df = pd.read_sql_query("SELECT * FROM test_data", conn)
        conn.close()
        
        print(f"Remaining entries after duplicate removal: {len(remaining_df)}")
        print(f"Expected unique entries: {len(original_df)}")
        
        # Check if there are still duplicates
        duplicate_check = remaining_df[columns_to_check].duplicated().sum()
        print(f"Remaining duplicates: {duplicate_check}")
        
        if duplicate_check == 0:
            print("✓ All duplicates successfully removed!")
        else:
            print("⚠ Some duplicates may still remain.")
        
        # Show final data
        print("\nFinal data sample:")
        print(remaining_df.head())
        
    except Exception as e:
        print(f"Error during duplicate removal: {e}")
        print("This might require additional dependencies or configuration.")

4. PostgreSQL Database Operations
---------------------------------

PostgreSQL Class Demonstration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: PostgreSQL operations require a running PostgreSQL server and
proper credentials.

.. code:: ipython3

    # Example 8: PostgreSQL operations (conceptual demonstration)
    print("PostgreSQL Database Operations:")
    print("=" * 35)
    
    try:
        # Note: This will likely fail without a running PostgreSQL server
        # This is just to show the interface
        
        print("Attempting to create PostgreSQL connection...")
        print("(This will likely fail without a running PostgreSQL server)")
        
        # Show available PostgreSQL class
        print(f"\nPostgreSQL class available: {hasattr(sdb, 'PostgreSQL')}")
        
        if hasattr(sdb, 'PostgreSQL'):
            print("PostgreSQL class methods:")
            postgres_methods = [method for method in dir(sdb.PostgreSQL) if not method.startswith('_')]
            for i, method in enumerate(postgres_methods[:10]):
                print(f"  {i+1:2d}. {method}")
            if len(postgres_methods) > 10:
                print(f"  ... and {len(postgres_methods) - 10} more methods")
        
        # Conceptual usage (would require actual PostgreSQL server)
        print("\nConceptual usage:")
        print("# pg_db = sdb.PostgreSQL(")
        print("#     dbname='scientific_data',")
        print("#     user='researcher',")
        print("#     password='password',")
        print("#     host='localhost',")
        print("#     port=5432")
        print("# )")
        print("# pg_db.connect()")
        print("# results = pg_db.query('SELECT * FROM experiments')")
        
    except Exception as e:
        print(f"PostgreSQL operations not available: {e}")
        print("This requires psycopg2 and a running PostgreSQL server.")

5. Practical Applications
-------------------------

Scientific Data Management Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate a complete scientific data management workflow.

.. code:: ipython3

    # Example 9: Complete scientific data management workflow
    print("Scientific Data Management Workflow:")
    print("=" * 40)
    
    # Create a more complex scientific database
    workflow_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    workflow_db_path = workflow_db.name
    workflow_db.close()
    
    print(f"Creating scientific database at: {workflow_db_path}")
    
    # Simulate experimental setup
    np.random.seed(42)
    
    # 1. Experimental conditions
    conditions = {
        'condition_id': range(1, 5),
        'condition_name': ['baseline', 'low_dose', 'medium_dose', 'high_dose'],
        'dose_mg': [0, 10, 50, 100],
        'description': [
            'Control condition',
            'Low dose treatment',
            'Medium dose treatment', 
            'High dose treatment'
        ]
    }
    
    # 2. Subject information
    n_subjects = 50
    subjects = {
        'subject_id': [f'SUBJ_{i:03d}' for i in range(1, n_subjects + 1)],
        'age': np.random.randint(18, 80, n_subjects),
        'gender': np.random.choice(['M', 'F'], n_subjects),
        'weight_kg': np.random.normal(70, 15, n_subjects),
        'group': np.random.choice(['experimental', 'control'], n_subjects),
        'enrollment_date': pd.date_range('2024-01-01', periods=n_subjects, freq='D')
    }
    
    # 3. Measurements (multiple per subject)
    measurements = []
    measurement_id = 1
    
    for subject_id in subjects['subject_id']:
        for condition_id in conditions['condition_id']:
            # Each subject gets 3 measurements per condition
            for rep in range(3):
                # Simulate dose-response relationship
                dose = conditions['dose_mg'][condition_id - 1]
                baseline_response = 100
                dose_effect = dose * 0.5 + np.random.normal(0, 10)
                response = baseline_response + dose_effect + np.random.normal(0, 5)
                
                measurements.append({
                    'measurement_id': measurement_id,
                    'subject_id': subject_id,
                    'condition_id': condition_id,
                    'replicate': rep + 1,
                    'response_value': response,
                    'measurement_date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=measurement_id),
                    'quality_score': np.random.uniform(0.7, 1.0)
                })
                measurement_id += 1
    
    # 4. Create database
    conn = sqlite3.connect(workflow_db_path)
    
    # Create tables
    conditions_df = pd.DataFrame(conditions)
    subjects_df = pd.DataFrame(subjects)
    measurements_df = pd.DataFrame(measurements)
    
    conditions_df.to_sql('conditions', conn, if_exists='replace', index=False)
    subjects_df.to_sql('subjects', conn, if_exists='replace', index=False)
    measurements_df.to_sql('measurements', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print(f"Database created with:")
    print(f"  - {len(conditions_df)} experimental conditions")
    print(f"  - {len(subjects_df)} subjects")
    print(f"  - {len(measurements_df)} measurements")
    
    # 5. Inspect the database
    print("\nInspecting the scientific database:")
    try:
        inspection_results = sdb.inspect(workflow_db_path, verbose=False)
        print(f"Successfully inspected {len(inspection_results)} tables")
    except Exception as e:
        print(f"Inspection error: {e}")
    
    # 6. Perform scientific analysis queries
    print("\nScientific Analysis Queries:")
    conn = sqlite3.connect(workflow_db_path)
    
    try:
        # Analysis 1: Dose-response relationship
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.condition_name, c.dose_mg, 
                   COUNT(m.measurement_id) as n_measurements,
                   AVG(m.response_value) as mean_response,
                   ROUND(AVG(m.response_value), 2) as mean_rounded,
                   MIN(m.response_value) as min_response,
                   MAX(m.response_value) as max_response
            FROM measurements m
            JOIN conditions c ON m.condition_id = c.condition_id
            GROUP BY c.condition_id, c.condition_name, c.dose_mg
            ORDER BY c.dose_mg
        """)
        
        dose_response = cursor.fetchall()
        print("\n1. Dose-Response Analysis:")
        print("Condition\t\tDose (mg)\tN\tMean Response\tRange")
        print("-" * 65)
        for row in dose_response:
            print(f"{row[0]:15s}\t{row[1]:8.0f}\t{row[2]:3d}\t{row[4]:11.2f}\t[{row[5]:.1f}, {row[6]:.1f}]")
        
        # Analysis 2: Subject demographics
        cursor.execute("""
            SELECT gender, 
                   COUNT(*) as count,
                   AVG(age) as avg_age,
                   AVG(weight_kg) as avg_weight
            FROM subjects
            GROUP BY gender
        """)
        
        demographics = cursor.fetchall()
        print("\n2. Subject Demographics:")
        print("Gender\tCount\tAvg Age\tAvg Weight (kg)")
        print("-" * 40)
        for row in demographics:
            print(f"{row[0]}\t{row[1]}\t{row[2]:.1f}\t{row[3]:.1f}")
        
        # Analysis 3: Data quality assessment
        cursor.execute("""
            SELECT 
                COUNT(*) as total_measurements,
                AVG(quality_score) as avg_quality,
                COUNT(CASE WHEN quality_score < 0.8 THEN 1 END) as low_quality_count,
                ROUND(COUNT(CASE WHEN quality_score < 0.8 THEN 1 END) * 100.0 / COUNT(*), 2) as low_quality_percent
            FROM measurements
        """)
        
        quality = cursor.fetchone()
        print("\n3. Data Quality Assessment:")
        print(f"Total measurements: {quality[0]}")
        print(f"Average quality score: {quality[1]:.3f}")
        print(f"Low quality measurements (<0.8): {quality[2]} ({quality[3]}%)")
        
    except Exception as e:
        print(f"Analysis error: {e}")
        
    finally:
        conn.close()

Database Maintenance and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate database maintenance operations.

.. code:: ipython3

    # Example 10: Database maintenance and optimization
    print("Database Maintenance and Optimization:")
    print("=" * 40)
    
    # Check database file size before maintenance
    db_size_before = os.path.getsize(workflow_db_path)
    print(f"Database size before maintenance: {db_size_before / 1024:.2f} KB")
    
    # Perform maintenance operations
    conn = sqlite3.connect(workflow_db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Analyze database structure
        print("\n1. Database Structure Analysis:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Number of tables: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"  {table_name}: {row_count} rows")
        
        # 2. Check for indexes
        print("\n2. Index Analysis:")
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        print(f"Number of indexes: {len(indexes)}")
        
        # 3. Create useful indexes for scientific queries
        print("\n3. Creating Indexes for Performance:")
        
        # Index on measurements for faster joins
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_measurements_subject ON measurements(subject_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_measurements_condition ON measurements(condition_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_measurements_date ON measurements(measurement_date)")
            print("  ✓ Created indexes on measurements table")
        except Exception as e:
            print(f"  ✗ Error creating indexes: {e}")
        
        # 4. Database statistics
        print("\n4. Database Statistics:")
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchall()
        print(f"Database info: {db_info[0]}")
        
        # Check page count and size
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        print(f"Pages: {page_count}, Page size: {page_size} bytes")
        print(f"Calculated DB size: {page_count * page_size / 1024:.2f} KB")
        
        # 5. Vacuum database to reclaim space
        print("\n5. Database Vacuum Operation:")
        cursor.execute("VACUUM")
        conn.commit()
        print("  ✓ Database vacuumed successfully")
        
        # 6. Update statistics
        cursor.execute("ANALYZE")
        conn.commit()
        print("  ✓ Database statistics updated")
        
    except Exception as e:
        print(f"Maintenance error: {e}")
        
    finally:
        conn.close()
    
    # Check database size after maintenance
    db_size_after = os.path.getsize(workflow_db_path)
    print(f"\nDatabase size after maintenance: {db_size_after / 1024:.2f} KB")
    size_change = db_size_after - db_size_before
    print(f"Size change: {size_change / 1024:+.2f} KB")
    
    if size_change < 0:
        print(f"Space saved: {abs(size_change) / 1024:.2f} KB")
    elif size_change > 0:
        print(f"Space used (indexes): {size_change / 1024:.2f} KB")
    else:
        print("No size change")

6. Cleanup
----------

Let’s clean up the temporary databases created during this
demonstration.

.. code:: ipython3

    # Example 11: Cleanup temporary databases
    print("Cleaning up temporary databases:")
    print("=" * 35)
    
    temp_databases = [
        (db_path, "Sample database"),
        (dup_db_path, "Duplicate test database"),
        (workflow_db_path, "Scientific workflow database")
    ]
    
    for db_file, description in temp_databases:
        try:
            if os.path.exists(db_file):
                size = os.path.getsize(db_file)
                os.unlink(db_file)
                print(f"✓ Removed {description} ({size / 1024:.2f} KB)")
            else:
                print(f"✗ {description} not found")
        except Exception as e:
            print(f"✗ Error removing {description}: {e}")
    
    print("\nCleanup complete!")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.db`` module:

Database Management Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``SQLite3``**: Comprehensive SQLite database management with
   multiple mixins

   -  Connection management
   -  Query operations
   -  Transaction handling
   -  Table operations
   -  Index management
   -  Batch operations
   -  BLOB handling
   -  Import/Export capabilities
   -  Maintenance operations

-  **``PostgreSQL``**: Enterprise-grade PostgreSQL database operations

   -  Advanced connection management
   -  Schema operations
   -  Backup and restore
   -  Performance optimization

Utility Functions
~~~~~~~~~~~~~~~~~

-  **``inspect``**: Database structure analysis and exploration

   -  Table enumeration
   -  Schema inspection
   -  Sample data viewing
   -  Metadata extraction

-  **``delete_duplicates``**: Intelligent duplicate detection and
   removal

   -  Flexible column selection
   -  Batch processing for large datasets
   -  Dry-run capability for safety
   -  Performance optimization

Key Features
~~~~~~~~~~~~

1. **Scientific Focus**: Designed for research data management
2. **Robustness**: Comprehensive error handling and validation
3. **Performance**: Optimized for large scientific datasets
4. **Flexibility**: Support for various database operations
5. **Safety**: Dry-run modes and transaction management

Practical Applications
~~~~~~~~~~~~~~~~~~~~~~

-  **Experimental Data Storage**: Structured storage of research data
-  **Data Quality Control**: Duplicate detection and removal
-  **Database Inspection**: Quick exploration of database contents
-  **Performance Optimization**: Index creation and maintenance
-  **Multi-database Support**: SQLite for local work, PostgreSQL for
   enterprise

Use Cases
~~~~~~~~~

-  Laboratory data management
-  Clinical trial databases
-  Sensor data collection
-  Experimental result archiving
-  Scientific collaboration platforms
-  Research data repositories

The ``scitex.db`` module provides a complete toolkit for scientific
database management, from simple data storage to complex multi-table
research databases with advanced querying and maintenance capabilities.
