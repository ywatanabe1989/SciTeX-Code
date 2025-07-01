# SciTeX Stats MCP Server

Statistical analysis translations and tools for SciTeX.

## Features

### 1. Statistical Test Translation
- T-tests (independent, paired, one-sample)
- Correlation tests (Pearson, Spearman, Kendall)
- ANOVA and non-parametric alternatives
- Normality tests (Shapiro-Wilk, D'Agostino, Jarque-Bera)
- Chi-square tests

### 2. P-value Formatting
- Automatic star notation (*** p<0.001, ** p<0.01, * p<0.05)
- Multiple comparison corrections (Bonferroni, FDR, Holm)
- Significance interpretation

### 3. Statistical Summaries
- Enhanced descriptive statistics
- Effect size calculations
- Confidence intervals

### 4. Report Generation
- Complete statistical analysis templates
- Automatic test selection based on data
- Publication-ready formatting

## Tools

- `translate_statistical_tests`: Bidirectional translation of test functions
- `add_p_value_formatting`: Add star notation to p-values
- `translate_statistical_summaries`: Convert summary statistics
- `add_multiple_comparison_correction`: Apply correction methods
- `generate_statistical_report`: Create complete analysis scripts
- `validate_statistical_code`: Check for best practices

## Usage Examples

### Basic Translation
```python
# From scipy to SciTeX
code = """
from scipy import stats
t_stat, p_val = stats.ttest_ind(group1, group2)
"""
# Becomes:
import scitex as stx
t_stat, p_val = stx.stats.tests.ttest_ind(group1, group2)
p_val_stars = stx.stats.p2stars(p_val)
```

### Complete Analysis
```python
# Generate full statistical report
generate_statistical_report(
    data_vars=["reaction_time", "accuracy"],
    group_var="condition",
    tests=["normality", "descriptive", "comparison"]
)
```

## Installation

```bash
cd mcp_servers/scitex-stats
pip install -e .
```

## Configuration

Add to your MCP settings:
```json
{
  "mcpServers": {
    "scitex-stats": {
      "command": "python",
      "args": ["-m", "scitex_stats.server"]
    }
  }
}
```