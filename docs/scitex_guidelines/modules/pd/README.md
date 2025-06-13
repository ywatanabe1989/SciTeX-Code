# SciTeX PD Module Documentation

## Overview

The `scitex.pd` module provides enhanced pandas DataFrame manipulation utilities that extend the standard pandas functionality. It focuses on common data wrangling tasks with improved ease of use, intelligent handling of edge cases, and additional features not found in vanilla pandas.

## Key Features

- **Smart Data Conversion**: Force dictionary to DataFrame conversion with automatic padding
- **Advanced Sorting**: Multi-column sorting with custom ordering and column reordering
- **Column Operations**: Merge, move, and manipulate columns with intuitive syntax
- **Conditional Filtering**: Enhanced row filtering with multiple conditions
- **Type Conversion**: Automatic numeric conversion with error handling
- **Missing Data**: Intelligent NaN handling throughout all operations

## Core Functions

### Data Creation and Conversion

#### `force_df()`
Convert a dictionary to DataFrame, automatically padding shorter values to match the longest.

```python
import scitex.pd

# Dictionary with unequal lengths
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30],  # Shorter list
    'city': ['NYC']   # Even shorter
}

# Convert to DataFrame with automatic padding
df = scitex.pd.force_df(data)
print(df)
#       name   age city
# 0    Alice  25.0  NYC
# 1      Bob  30.0  NaN
# 2  Charlie   NaN  NaN

# Custom filler value
df_filled = scitex.pd.force_df(data, filler="MISSING")
#       name   age     city
# 0    Alice    25      NYC
# 1      Bob    30  MISSING
# 2  Charlie  MISSING  MISSING
```

#### `to_numeric()`
Attempt to convert all possible columns to numeric types.

```python
# DataFrame with mixed types
df = pd.DataFrame({
    'id': ['1', '2', '3'],
    'value': ['10.5', '20.3', '30.1'],
    'name': ['A', 'B', 'C'],
    'flag': ['True', 'False', 'True']
})

# Convert to numeric where possible
df_numeric = scitex.pd.to_numeric(df)
print(df_numeric.dtypes)
# id        int64
# value   float64
# name     object  # Kept as string
# flag     object  # Kept as string
```

### Column Operations

#### `merge_columns()`
Create a new column by joining multiple columns with their labels.

```python
# Create composite identifier
df = pd.DataFrame({
    'subject': ['S001', 'S002', 'S003'],
    'session': [1, 2, 1],
    'condition': ['A', 'B', 'A']
})

# Merge columns into identifier
df = scitex.pd.merge_columns(
    df, 
    columns=['subject', 'session', 'condition'],
    new_col='experiment_id'
)
print(df['experiment_id'])
# 0    subject-S001_session-1_condition-A
# 1    subject-S002_session-2_condition-B
# 2    subject-S003_session-1_condition-A
```

#### `mv()`
Move a DataFrame row or column to a specified position.

```python
# Move column to specific position
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9],
    'D': [10, 11, 12]
})

# Move column 'C' to first position
df_moved = scitex.pd.mv(df, 'C', 0, axis=1)
print(df_moved.columns.tolist())
# ['C', 'A', 'B', 'D']

# Move to last position using negative index
df_last = scitex.pd.mv(df, 'A', -1, axis=1)
print(df_last.columns.tolist())
# ['B', 'C', 'D', 'A']

# Move row by index
df_row_moved = scitex.pd.mv(df, 2, 0, axis=0)  # Move row 2 to top
```

### Filtering and Selection

#### `find_indi()`
Get boolean indicators for rows matching specified conditions.

```python
# Sample data
df = pd.DataFrame({
    'group': ['A', 'B', 'A', 'C', 'B', 'A'],
    'value': [10, 20, 15, 30, 25, 12],
    'status': ['active', 'inactive', 'active', 'active', 'inactive', 'active']
})

# Find indices matching conditions
mask = scitex.pd.find_indi(df, {'group': 'A', 'status': 'active'})
print(mask)
# 0     True
# 1    False
# 2     True
# 3    False
# 4    False
# 5     True

# Use with multiple values
mask_multi = scitex.pd.find_indi(df, {'group': ['A', 'B']})
filtered = df[mask_multi]

# Handles NaN intelligently
df_with_nan = df.copy()
df_with_nan.loc[1, 'value'] = np.nan
mask_nan = scitex.pd.find_indi(df_with_nan, {'value': 20})  # Won't match NaN
```

#### `slice()`
Filter DataFrame based on multiple conditions (returns rows, not just mask).

```python
# Filter with multiple conditions
conditions = {
    'group': 'A',
    'value': lambda x: x > 10,
    'status': 'active'
}

filtered_df = scitex.pd.slice(df, conditions)
print(filtered_df)
#   group  value  status
# 2     A     15  active
# 5     A     12  active

# Using lists for 'OR' conditions within a column
conditions_or = {
    'group': ['A', 'B'],  # group is A OR B
    'status': 'active'    # AND status is active
}
filtered_or = scitex.pd.slice(df, conditions_or)
```

### Sorting

#### `sort()`
Enhanced sorting with custom ordering and column reordering.

```python
# Basic sorting
df = pd.DataFrame({
    'name': ['Charlie', 'Alice', 'Bob'],
    'score': [85, 92, 78],
    'grade': ['B', 'A', 'C']
})

# Sort by single column
sorted_df = scitex.pd.sort(df, 'name')

# Sort by multiple columns
sorted_multi = scitex.pd.sort(df, ['grade', 'score'], ascending=[True, False])

# Custom ordering for categorical data
custom_order = {'grade': ['A', 'B', 'C', 'D', 'F']}
sorted_custom = scitex.pd.sort(df, 'grade', orders=custom_order)

# Automatically move sorted columns to front
sorted_reorder = scitex.pd.sort(df, 'score', reorder_cols=True)
print(sorted_reorder.columns.tolist())
# ['score', 'name', 'grade']  # 'score' moved to first
```

## Common Workflows

### 1. Data Preprocessing Pipeline
```python
import scitex.pd
import pandas as pd

# Load messy data
raw_data = {
    'id': ['001', '002', '003', '004'],
    'measurement': ['12.5', '13.2', 'ERROR', '14.1'],
    'group': ['control', 'treatment', 'control'],  # Missing one value
    'notes': ['good', 'bad', 'good', 'excellent']
}

# Convert to DataFrame with padding
df = scitex.pd.force_df(raw_data, filler='MISSING')

# Try to convert to numeric
df = scitex.pd.to_numeric(df)

# Create composite ID
df = scitex.pd.merge_columns(
    df, 
    columns=['id', 'group'],
    new_col='subject_id'
)

# Filter valid measurements
valid_df = scitex.pd.slice(df, {
    'measurement': lambda x: pd.notna(x) and x != 'ERROR'
})

# Sort by group and measurement
final_df = scitex.pd.sort(
    valid_df, 
    ['group', 'measurement'],
    ascending=[True, False]
)
```

### 2. Experimental Data Organization
```python
# Organize experimental results
results = pd.DataFrame({
    'subject': ['S01', 'S02', 'S03', 'S01', 'S02', 'S03'],
    'session': [1, 1, 1, 2, 2, 2],
    'accuracy': [0.95, 0.87, 0.92, 0.97, 0.89, 0.94],
    'rt_ms': [450, 520, 480, 440, 510, 470],
    'condition': ['A', 'B', 'A', 'B', 'A', 'B']
})

# Create unique trial identifier
results = scitex.pd.merge_columns(
    results,
    columns=['subject', 'session', 'condition'],
    new_col='trial_id'
)

# Find specific conditions
condition_a_mask = scitex.pd.find_indi(results, {
    'condition': 'A',
    'accuracy': lambda x: x > 0.9
})

high_performers = results[condition_a_mask]

# Reorder columns for better readability
results = scitex.pd.mv(results, 'trial_id', 0, axis=1)
results = scitex.pd.mv(results, 'condition', 1, axis=1)

# Sort by performance metrics
results_sorted = scitex.pd.sort(
    results,
    ['accuracy', 'rt_ms'],
    ascending=[False, True],  # High accuracy, low RT
    reorder_cols=True
)
```

### 3. Data Quality Control
```python
# Check data quality and handle issues
df = pd.DataFrame({
    'sample_id': ['A1', 'A2', 'B1', 'B2', 'C1'],
    'value1': ['10.5', '11.2', 'NA', '12.1', '11.8'],
    'value2': ['20.1', 'ERROR', '19.8', '20.5', '19.9'],
    'batch': ['1', '1', '2', '2', '3'],
    'qc_pass': ['True', 'True', 'False', 'True', 'True']
})

# Convert to numeric, identifying conversion failures
df_numeric = scitex.pd.to_numeric(df)

# Find rows with any non-numeric values in value columns
value_cols = ['value1', 'value2']
for col in value_cols:
    # Check which values couldn't be converted
    if df[col].dtype == 'object':
        non_numeric = df[df[col].apply(lambda x: not str(x).replace('.','').isdigit())]
        print(f"Non-numeric values in {col}:")
        print(non_numeric[['sample_id', col]])

# Filter only QC-passed samples
qc_passed = scitex.pd.slice(df, {'qc_pass': 'True'})

# Group by batch and sort
batch_sorted = scitex.pd.sort(qc_passed, ['batch', 'sample_id'])
```

## Integration with Other SciTeX Modules

### With scitex.io for Data Loading
```python
# Load and preprocess data
data = scitex.io.load("raw_data.pkl")

# Convert to DataFrame if needed
if isinstance(data, dict):
    df = scitex.pd.force_df(data)
else:
    df = data

# Process and save
df_processed = scitex.pd.to_numeric(df)
scitex.io.save(df_processed, "processed_data.csv")
```

### With scitex.stats for Analysis
```python
# Prepare data for statistical analysis
df = scitex.pd.slice(full_data, {
    'quality': lambda x: x > threshold,
    'group': ['control', 'treatment']
})

# Get groups for comparison
control = df[scitex.pd.find_indi(df, {'group': 'control'})]['value']
treatment = df[scitex.pd.find_indi(df, {'group': 'treatment'})]['value']

# Statistical test
result = scitex.stats.tests.brunner_munzel_test(control, treatment)
```

## Best Practices

1. **Use force_df() for robust DataFrame creation**: Handles unequal lengths gracefully
2. **Chain operations for data pipelines**: Most functions return DataFrames for chaining
3. **Leverage find_indi() for complex selections**: More readable than multiple boolean operations
4. **Use custom ordering in sort()**: Essential for categorical data with meaningful order
5. **Move important columns to front**: Use mv() or sort() with reorder_cols for better visibility

## Troubleshooting

### Common Issues

**Issue**: `merge_columns()` creates very long column names
```python
# Solution: Use subset of columns or create shorter labels
df = scitex.pd.merge_columns(
    df,
    columns=['subject', 'session'],  # Skip less important columns
    new_col='id'
)
```

**Issue**: `to_numeric()` silently keeps object columns
```python
# Solution: Check which columns weren't converted
before_types = df.dtypes
df_numeric = scitex.pd.to_numeric(df)
after_types = df_numeric.dtypes

not_converted = before_types[before_types == after_types].index
print(f"Columns not converted: {list(not_converted)}")
```

**Issue**: `slice()` returns empty DataFrame
```python
# Solution: Check conditions individually
for col, condition in conditions.items():
    matching = scitex.pd.find_indi(df, {col: condition})
    print(f"{col}: {matching.sum()} matches")
```

## API Reference

For detailed API documentation, see the individual function docstrings or the Sphinx-generated documentation.

## See Also

- `pandas` - The underlying DataFrame library
- `scitex.io` - For loading and saving DataFrames
- `scitex.stats` - For statistical analysis of DataFrame data