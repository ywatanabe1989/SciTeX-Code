# Classification Results Export

## Files

- `summary_table.csv`: Results table in CSV format
- `summary_table.tex`: LaTeX table for direct inclusion
- `raw_results.json`: Complete raw data in JSON format

## Usage

### LaTeX
```latex
\input{summary_table.tex}
```

### Python
```python
import pandas as pd
df = pd.read_csv('summary_table.csv')
```
