#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 11:10:00 (ywatanabe)"
# File: ./mcp_servers/scitex-pd/server.py
# ----------------------------------------

"""MCP server for SciTeX pandas (pd) module translations and DataFrame enhancements."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from scitex_base.base_server import ScitexBaseMCPServer
from scitex_base.translator_mixin import ScitexTranslatorMixin


class ScitexPdMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX pandas module translations."""
    
    def __init__(self):
        super().__init__("pd", "0.1.0")
        
    def _register_module_tools(self):
        """Register pandas-specific tools."""
        
        @self.app.tool()
        async def translate_dataframe_operations(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate DataFrame operations between standard pandas and SciTeX.
            
            Args:
                code: Python code containing pandas operations
                direction: "to_scitex" or "from_scitex"
                
            Returns:
                Dictionary with translated_code and conversions made
            """
            
            if direction == "to_scitex":
                patterns = [
                    # Data loading - handled by IO module but included for completeness
                    (r"pd\.read_csv\(([^)]+)\)", r"stx.io.load(\1)"),
                    (r"pd\.read_excel\(([^)]+)\)", r"stx.io.load(\1)"),
                    (r"pd\.read_json\(([^)]+)\)", r"stx.io.load(\1)"),
                    
                    # Data saving - handled by IO module
                    (r"\.to_csv\(([^)]+)\)", r"stx.io.save(self, \1)"),
                    (r"\.to_excel\(([^)]+)\)", r"stx.io.save(self, \1)"),
                    (r"\.to_json\(([^)]+)\)", r"stx.io.save(self, \1)"),
                    
                    # Enhanced describe
                    (r"\.describe\(\)", r".stx_describe()"),
                    (r"\.describe\(include='all'\)", r".stx_describe(include='all')"),
                    
                    # Missing data handling
                    (r"\.dropna\(\)", r".stx_dropna()"),
                    (r"\.fillna\(([^)]+)\)", r".stx_fillna(\1)"),
                    (r"\.isna\(\)", r".stx_isna()"),
                    (r"\.notna\(\)", r".stx_notna()"),
                    
                    # Data transformation
                    (r"\.pivot_table\(([^)]+)\)", r".stx_pivot_table(\1)"),
                    (r"\.melt\(([^)]+)\)", r".stx_melt(\1)"),
                    (r"\.stack\(\)", r".stx_stack()"),
                    (r"\.unstack\(\)", r".stx_unstack()"),
                    
                    # Groupby operations
                    (r"\.groupby\(([^)]+)\)\.agg\(([^)]+)\)", r".stx_groupby(\1).agg(\2)"),
                    (r"\.groupby\(([^)]+)\)\.transform\(([^)]+)\)", r".stx_groupby(\1).transform(\2)"),
                    
                    # Window functions
                    (r"\.rolling\(([^)]+)\)", r".stx_rolling(\1)"),
                    (r"\.expanding\(\)", r".stx_expanding()"),
                    (r"\.ewm\(([^)]+)\)", r".stx_ewm(\1)"),
                    
                    # String operations
                    (r"\.str\.contains\(([^)]+)\)", r".stx_str_contains(\1)"),
                    (r"\.str\.replace\(([^)]+)\)", r".stx_str_replace(\1)"),
                    (r"\.str\.extract\(([^)]+)\)", r".stx_str_extract(\1)"),
                    
                    # DateTime operations
                    (r"pd\.to_datetime\(([^)]+)\)", r"stx.pd.to_datetime(\1)"),
                    (r"\.dt\.date", r".stx_dt_date"),
                    (r"\.dt\.year", r".stx_dt_year"),
                    (r"\.dt\.month", r".stx_dt_month"),
                    
                    # Merge operations
                    (r"pd\.merge\(([^)]+)\)", r"stx.pd.merge(\1)"),
                    (r"pd\.concat\(([^)]+)\)", r"stx.pd.concat(\1)"),
                    (r"\.merge\(([^)]+)\)", r".stx_merge(\1)"),
                ]
                
                # Add imports if needed
                if "pandas as pd" in code and "import scitex as stx" not in code:
                    code = "import scitex as stx\n" + code
                    
            else:  # from_scitex
                patterns = [
                    # Reverse patterns
                    (r"stx\.io\.load\(([^)]+)\)", self._infer_pandas_reader),
                    (r"\.stx_describe\(\)", r".describe()"),
                    (r"\.stx_dropna\(\)", r".dropna()"),
                    (r"\.stx_fillna\(([^)]+)\)", r".fillna(\1)"),
                    (r"\.stx_pivot_table\(([^)]+)\)", r".pivot_table(\1)"),
                    (r"\.stx_groupby\(([^)]+)\)", r".groupby(\1)"),
                    (r"stx\.pd\.merge\(([^)]+)\)", r"pd.merge(\1)"),
                    (r"stx\.pd\.concat\(([^)]+)\)", r"pd.concat(\1)"),
                ]
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                if callable(replacement):
                    # Handle dynamic replacements
                    for match in re.finditer(pattern, translated):
                        new_text = replacement(match)
                        translated = translated.replace(match.group(0), new_text)
                        conversions.append(f"{match.group(0)} → {new_text}")
                else:
                    matches = re.findall(pattern, translated)
                    if matches:
                        translated = re.sub(pattern, replacement, translated)
                        conversions.append(f"{pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions,
                "imports_added": "scitex as stx" in translated
            }
        
        @self.app.tool()
        async def add_dataframe_validation(
            code: str,
            df_names: List[str]
        ) -> Dict[str, str]:
            """
            Add DataFrame validation and quality checks.
            
            Args:
                code: Code containing DataFrame operations
                df_names: Names of DataFrame variables to validate
                
            Returns:
                Enhanced code with validation
            """
            
            validation_code = "\n# DataFrame validation\n"
            
            for df_name in df_names:
                validation_code += f"""
# Validate {df_name}
{df_name}_info = {{
    'shape': {df_name}.shape,
    'dtypes': {df_name}.dtypes.to_dict(),
    'missing': {df_name}.isnull().sum().to_dict(),
    'duplicates': {df_name}.duplicated().sum()
}}

if {df_name}_info['duplicates'] > 0:
    stx.str.printc(f"Warning: {{df_name}} has {{{df_name}_info['duplicates']}} duplicate rows", c='yellow')

missing_pct = {df_name}.isnull().sum() / len({df_name}) * 100
high_missing = missing_pct[missing_pct > 20]
if not high_missing.empty:
    stx.str.printc(f"Warning: High missing data in {{high_missing.to_dict()}}", c='yellow')
"""
            
            # Insert validation after DataFrame creation/loading
            insert_points = []
            
            # Find DataFrame assignments
            for match in re.finditer(rf"({('|'.join(df_names))})\s*=\s*[^=]", code):
                # Find the end of the statement
                line_end = code.find('\n', match.end())
                if line_end == -1:
                    line_end = len(code)
                insert_points.append(line_end)
            
            # Insert validation code (in reverse order to maintain positions)
            enhanced = code
            for point in sorted(insert_points, reverse=True):
                enhanced = enhanced[:point] + validation_code + enhanced[point:]
            
            return {
                "enhanced_code": enhanced,
                "dataframes_validated": df_names,
                "validations_added": len(insert_points)
            }
        
        @self.app.tool()
        async def generate_data_cleaning_pipeline(
            df_name: str,
            operations: List[str] = ["missing", "duplicates", "outliers", "dtypes"]
        ) -> Dict[str, str]:
            """
            Generate a complete data cleaning pipeline.
            
            Args:
                df_name: Name of the DataFrame variable
                operations: List of cleaning operations to include
                
            Returns:
                Data cleaning pipeline code
            """
            
            pipeline = f'''#!/usr/bin/env python3
"""Data cleaning pipeline for {df_name}."""

import scitex as stx
import pandas as pd
import numpy as np

# Load data
{df_name} = stx.io.load(CONFIG.PATH.RAW_DATA)
print(f"Original shape: {{{df_name}.shape}}")

# Create cleaning report
cleaning_report = {{
    'original_shape': {df_name}.shape,
    'steps': []
}}

'''
            
            if "missing" in operations:
                pipeline += f'''# Handle missing data
missing_before = {df_name}.isnull().sum()
print("\\nMissing values per column:")
print(missing_before[missing_before > 0])

# Strategy: Drop columns with >50% missing, impute others
high_missing_cols = missing_before[missing_before > len({df_name}) * 0.5].index
{df_name} = {df_name}.drop(columns=high_missing_cols)
cleaning_report['steps'].append({{
    'action': 'dropped_high_missing_columns',
    'columns': list(high_missing_cols)
}})

# Impute numeric columns with median
numeric_cols = {df_name}.select_dtypes(include=[np.number]).columns
{df_name}[numeric_cols] = {df_name}[numeric_cols].fillna({df_name}[numeric_cols].median())

# Impute categorical columns with mode
categorical_cols = {df_name}.select_dtypes(include=['object']).columns
for col in categorical_cols:
    if {df_name}[col].isnull().any():
        {df_name}[col] = {df_name}[col].fillna({df_name}[col].mode()[0])

cleaning_report['steps'].append({{
    'action': 'imputed_missing_values',
    'numeric_strategy': 'median',
    'categorical_strategy': 'mode'
}})

'''
            
            if "duplicates" in operations:
                pipeline += f'''# Remove duplicates
duplicates_before = {df_name}.duplicated().sum()
print(f"\\nDuplicate rows: {{duplicates_before}}")

if duplicates_before > 0:
    {df_name} = {df_name}.drop_duplicates()
    cleaning_report['steps'].append({{
        'action': 'removed_duplicates',
        'count': duplicates_before
    }})

'''
            
            if "outliers" in operations:
                pipeline += f'''# Handle outliers (IQR method for numeric columns)
numeric_cols = {df_name}.select_dtypes(include=[np.number]).columns
outliers_removed = 0

for col in numeric_cols:
    Q1 = {df_name}[col].quantile(0.25)
    Q3 = {df_name}[col].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = ((df_name}[col] < lower_bound) | ({df_name}[col] > upper_bound)).sum()
    if outliers > 0:
        # Cap outliers instead of removing
        {df_name}[col] = {df_name}[col].clip(lower_bound, upper_bound)
        outliers_removed += outliers
        print(f"Capped {{outliers}} outliers in {{col}}")

cleaning_report['steps'].append({{
    'action': 'capped_outliers',
    'method': 'IQR',
    'total_outliers': outliers_removed
}})

'''
            
            if "dtypes" in operations:
                pipeline += f'''# Optimize data types
print("\\nOptimizing data types...")
initial_memory = {df_name}.memory_usage(deep=True).sum() / 1024**2

# Convert object columns that should be categorical
for col in {df_name}.select_dtypes(include=['object']).columns:
    num_unique = {df_name}[col].nunique()
    if num_unique < len({df_name}) * 0.5:  # Less than 50% unique values
        {df_name}[col] = {df_name}[col].astype('category')

# Downcast numeric types
for col in {df_name}.select_dtypes(include=['int']).columns:
    {df_name}[col] = pd.to_numeric({df_name}[col], downcast='integer')

for col in {df_name}.select_dtypes(include=['float']).columns:
    {df_name}[col] = pd.to_numeric({df_name}[col], downcast='float')

final_memory = {df_name}.memory_usage(deep=True).sum() / 1024**2
memory_reduction = (1 - final_memory/initial_memory) * 100

cleaning_report['steps'].append({{
    'action': 'optimized_dtypes',
    'memory_reduction_pct': round(memory_reduction, 2)
}})
print(f"Memory usage reduced by {{memory_reduction:.1f}}%")

'''
            
            pipeline += f'''# Final validation
print(f"\\nFinal shape: {{{df_name}.shape}}")
print(f"Rows removed: {{cleaning_report['original_shape'][0] - {df_name}.shape[0]}}")
print(f"Columns removed: {{cleaning_report['original_shape'][1] - {df_name}.shape[1]}}")

# Save cleaned data
stx.io.save({df_name}, './cleaned_data.csv', symlink_from_cwd=True)
stx.io.save(cleaning_report, './cleaning_report.json', symlink_from_cwd=True)

# Generate summary statistics
summary = {df_name}.stx_describe()
stx.io.save(summary, './data_summary.csv', symlink_from_cwd=True)

print("\\nCleaning complete! Files saved:")
print("  - cleaned_data.csv")
print("  - cleaning_report.json")
print("  - data_summary.csv")
'''
            
            return {
                "pipeline_code": pipeline,
                "operations_included": operations,
                "dataframe_name": df_name
            }
        
        @self.app.tool()
        async def translate_advanced_pandas(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate advanced pandas operations and method chaining.
            
            Args:
                code: Code with advanced pandas operations
                direction: Translation direction
                
            Returns:
                Translated code
            """
            
            if direction == "to_scitex":
                # Handle method chaining
                chain_pattern = r"(\w+)" + r"(\.[a-zA-Z_]+\([^)]*\))+" 
                
                # Common advanced patterns
                patterns = [
                    # Query operations
                    (r"\.query\(([^)]+)\)", r".stx_query(\1)"),
                    
                    # Advanced indexing
                    (r"\.loc\[([^\]]+)\]", r".stx_loc[\1]"),
                    (r"\.iloc\[([^\]]+)\]", r".stx_iloc[\1]"),
                    (r"\.at\[([^\]]+)\]", r".stx_at[\1]"),
                    (r"\.iat\[([^\]]+)\]", r".stx_iat[\1]"),
                    
                    # Multi-index operations
                    (r"\.set_index\(([^)]+)\)", r".stx_set_index(\1)"),
                    (r"\.reset_index\(([^)]+)\)", r".stx_reset_index(\1)"),
                    (r"\.xs\(([^)]+)\)", r".stx_xs(\1)"),
                    
                    # Advanced aggregations
                    (r"\.agg\(\{([^}]+)\}\)", r".stx_agg({\1})"),
                    (r"\.transform\(([^)]+)\)", r".stx_transform(\1)"),
                    
                    # Time series specific
                    (r"\.resample\(([^)]+)\)", r".stx_resample(\1)"),
                    (r"\.shift\(([^)]+)\)", r".stx_shift(\1)"),
                    (r"\.diff\(([^)]*)\)", r".stx_diff(\1)"),
                    (r"\.pct_change\(([^)]*)\)", r".stx_pct_change(\1)"),
                    
                    # Categorical operations
                    (r"\.astype\('category'\)", r".stx_to_categorical()"),
                    (r"\.cat\.categories", r".stx_cat_categories"),
                    (r"\.cat\.codes", r".stx_cat_codes"),
                ]
            else:
                patterns = [
                    # Reverse patterns
                    (r"\.stx_query\(([^)]+)\)", r".query(\1)"),
                    (r"\.stx_loc\[([^\]]+)\]", r".loc[\1]"),
                    (r"\.stx_set_index\(([^)]+)\)", r".set_index(\1)"),
                    (r"\.stx_agg\(([^)]+)\)", r".agg(\1)"),
                    (r"\.stx_resample\(([^)]+)\)", r".resample(\1)"),
                    (r"\.stx_to_categorical\(\)", r".astype('category')"),
                ]
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    conversions.append(f"Advanced: {pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions,
                "advanced_operations": len(conversions)
            }
        
        @self.app.tool()
        async def generate_exploratory_analysis(
            df_name: str,
            target_column: Optional[str] = None,
            analysis_types: List[str] = ["basic", "correlations", "distributions"]
        ) -> Dict[str, str]:
            """
            Generate exploratory data analysis (EDA) code.
            
            Args:
                df_name: DataFrame variable name
                target_column: Target variable for analysis
                analysis_types: Types of analysis to include
                
            Returns:
                EDA script code
            """
            
            script = f'''#!/usr/bin/env python3
"""Exploratory Data Analysis for {df_name}."""

import scitex as stx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load and prepare data
{df_name} = stx.io.load(CONFIG.PATH.DATA_FILE)
print(f"Dataset shape: {{{df_name}.shape}}")
print(f"\\nColumns: {{list({df_name}.columns)}}")

# Set up visualization style
plt.style.use('seaborn-v0_8-darkgrid')
fig_num = 0

'''
            
            if "basic" in analysis_types:
                script += f'''# Basic information
print("\\n" + "="*50)
print("BASIC INFORMATION")
print("="*50)

# Data types
print("\\nData types:")
print({df_name}.dtypes)

# Summary statistics
summary = {df_name}.stx_describe()
print("\\nSummary statistics:")
print(summary)

# Missing data analysis
missing = {df_name}.isnull().sum()
missing_pct = missing / len({df_name}) * 100
missing_df = pd.DataFrame({{
    'Missing_Count': missing,
    'Missing_Percentage': missing_pct
}})
missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)

if not missing_df.empty:
    print("\\nMissing data:")
    print(missing_df)
    
    # Visualize missing data
    fig, ax = stx.plt.subplots(figsize=(10, 6))
    missing_df['Missing_Percentage'].plot(kind='bar', ax=ax)
    ax.set_xyt('Columns', 'Missing %', 'Missing Data by Column')
    stx.io.save(fig, f'./eda_missing_data_{{fig_num}}.jpg', symlink_from_cwd=True)
    fig_num += 1

'''
            
            if "distributions" in analysis_types:
                script += f'''# Distribution analysis
print("\\n" + "="*50)
print("DISTRIBUTION ANALYSIS")
print("="*50)

# Numeric columns
numeric_cols = {df_name}.select_dtypes(include=[np.number]).columns
n_numeric = len(numeric_cols)

if n_numeric > 0:
    # Create distribution plots
    n_cols = min(3, n_numeric)
    n_rows = (n_numeric + n_cols - 1) // n_cols
    
    fig, axes = stx.plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    axes = axes.flatten() if n_numeric > 1 else [axes]
    
    for i, col in enumerate(numeric_cols):
        if i < len(axes):
            {df_name}[col].hist(bins=30, ax=axes[i], edgecolor='black')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')
            axes[i].set_title(f'Distribution of {{col}}')
            
            # Add statistics
            mean_val = {df_name}[col].mean()
            median_val = {df_name}[col].median()
            axes[i].axvline(mean_val, color='red', linestyle='--', label=f'Mean={{mean_val:.2f}}')
            axes[i].axvline(median_val, color='green', linestyle='--', label=f'Median={{median_val:.2f}}')
            axes[i].legend()
    
    # Hide unused subplots
    for i in range(n_numeric, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    stx.io.save(fig, f'./eda_distributions_{{fig_num}}.jpg', symlink_from_cwd=True)
    fig_num += 1
    
    # Check for skewness
    skewness = {df_name}[numeric_cols].skew()
    print("\\nSkewness:")
    print(skewness.sort_values(ascending=False))

# Categorical columns
categorical_cols = {df_name}.select_dtypes(include=['object', 'category']).columns
for col in categorical_cols[:5]:  # Limit to first 5
    print(f"\\nValue counts for {{col}}:")
    print({df_name}[col].value_counts().head(10))
    
    if {df_name}[col].nunique() <= 20:
        fig, ax = stx.plt.subplots(figsize=(10, 6))
        {df_name}[col].value_counts().plot(kind='bar', ax=ax)
        ax.set_xyt(col, 'Count', f'Distribution of {{col}}')
        plt.xticks(rotation=45, ha='right')
        stx.io.save(fig, f'./eda_categorical_{{col}}_{{fig_num}}.jpg', symlink_from_cwd=True)
        fig_num += 1

'''
            
            if "correlations" in analysis_types:
                script += f'''# Correlation analysis
print("\\n" + "="*50)
print("CORRELATION ANALYSIS")
print("="*50)

numeric_df = {df_name}[numeric_cols]
if len(numeric_cols) > 1:
    # Correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Heatmap
    fig, ax = stx.plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, linewidths=0.5, cbar_kws={{"shrink": 0.8}}, ax=ax)
    ax.set_title('Correlation Matrix Heatmap')
    stx.io.save(fig, f'./eda_correlation_heatmap_{{fig_num}}.jpg', symlink_from_cwd=True)
    fig_num += 1
    
    # Find strong correlations
    threshold = 0.7
    strong_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                strong_corr.append({{
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j],
                    'corr': corr_matrix.iloc[i, j]
                }})
    
    if strong_corr:
        print("\\nStrong correlations (|r| > {{threshold}}):")
        for item in strong_corr:
            print(f"  {{item['var1']}} <-> {{item['var2']}}: {{item['corr']:.3f}}")

'''
            
            if target_column:
                script += f'''# Target variable analysis
print("\\n" + "="*50)
print("TARGET VARIABLE ANALYSIS: {target_column}")
print("="*50)

if {target_column} in {df_name}.columns:
    # Target distribution
    fig, ax = stx.plt.subplots(figsize=(10, 6))
    {df_name}['{target_column}'].hist(bins=30, ax=ax, edgecolor='black')
    ax.set_xyt('{target_column}', 'Frequency', 'Target Variable Distribution')
    stx.io.save(fig, f'./eda_target_distribution_{{fig_num}}.jpg', symlink_from_cwd=True)
    fig_num += 1
    
    # Relationship with numeric features
    for col in numeric_cols:
        if col != '{target_column}':
            fig, ax = stx.plt.subplots(figsize=(10, 6))
            ax.scatter({df_name}[col], {df_name}['{target_column}'], alpha=0.5)
            ax.set_xlabel(col)
            ax.set_ylabel('{target_column}')
            ax.set_title(f'{{col}} vs {target_column}')
            
            # Add correlation
            corr = {df_name}[[col, '{target_column}']].corr().iloc[0, 1]
            ax.text(0.05, 0.95, f'Correlation: {{corr:.3f}}', transform=ax.transAxes, 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            stx.io.save(fig, f'./eda_target_vs_{{col}}_{{fig_num}}.jpg', symlink_from_cwd=True)
            fig_num += 1

'''
            
            script += f'''# Save EDA report
eda_report = {{
    'shape': {df_name}.shape,
    'numeric_columns': list(numeric_cols),
    'categorical_columns': list(categorical_cols),
    'missing_data': missing_df.to_dict() if not missing_df.empty else {{}},
    'skewness': skewness.to_dict() if 'skewness' in locals() else {{}},
    'figures_generated': fig_num
}}

stx.io.save(eda_report, './eda_report.json', symlink_from_cwd=True)
print(f"\\nEDA complete! Generated {{fig_num}} figures.")
print("Check the output directory for all visualizations and eda_report.json")
'''
            
            return {
                "eda_script": script,
                "dataframe": df_name,
                "target": target_column,
                "analysis_types": analysis_types
            }
        
        @self.app.tool()
        async def validate_pandas_code(
            code: str
        ) -> Dict[str, Any]:
            """
            Validate pandas code for best practices.
            
            Args:
                code: Pandas code to validate
                
            Returns:
                Validation results with suggestions
            """
            
            issues = []
            suggestions = []
            
            # Check for chained assignments
            if ".loc[" in code and "] =" in code:
                # This is good
                pass
            elif re.search(r"\]\[[^\]]+\]\s*=", code):
                issues.append("Chained assignment detected - use .loc[] instead")
                suggestions.append("Replace df[cond][col] = value with df.loc[cond, col] = value")
            
            # Check for proper copy usage
            if "=" in code and "copy()" not in code:
                if re.search(r"(\w+)\s*=\s*(\w+)\[", code):
                    suggestions.append("Consider using .copy() to avoid SettingWithCopyWarning")
            
            # Check for inefficient operations
            if "iterrows()" in code:
                issues.append("iterrows() is slow - consider vectorized operations")
                suggestions.append("Use apply(), vectorized operations, or numpy functions instead")
            
            if "append(" in code and "concat(" not in code:
                issues.append("append() is deprecated - use pd.concat() instead")
            
            # Check for proper handling of datetime
            if "datetime" in code and "pd.to_datetime" not in code:
                suggestions.append("Use pd.to_datetime() for datetime conversions")
            
            # Check for memory efficiency
            if "read_csv(" in code and "dtype=" not in code and "chunksize=" not in code:
                suggestions.append("Consider specifying dtypes or using chunksize for large files")
            
            # Check for proper NA handling
            if "== None" in code or "!= None" in code:
                issues.append("Use .isna() or .notna() instead of == None")
            
            # Check for SQL-like operations
            if ".merge(" in code and "how=" not in code:
                suggestions.append("Explicitly specify 'how' parameter in merge operations")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "suggestions": suggestions,
                "best_practices_score": max(0, 100 - len(issues) * 15 - len(suggestions) * 5)
            }
    
    def _infer_pandas_reader(self, match) -> str:
        """Infer the appropriate pandas reader based on file extension."""
        file_path = match.group(1)
        if '.csv' in file_path:
            return f"pd.read_csv({file_path})"
        elif '.xlsx' in file_path or '.xls' in file_path:
            return f"pd.read_excel({file_path})"
        elif '.json' in file_path:
            return f"pd.read_json({file_path})"
        else:
            return f"pd.read_csv({file_path})  # Inferred"
    
    def get_module_description(self) -> str:
        """Get description of pandas functionality."""
        return (
            "SciTeX pandas server provides DataFrame operation translations, data cleaning pipelines, "
            "exploratory data analysis generation, and pandas best practices validation "
            "for enhanced data manipulation in scientific computing."
        )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "translate_dataframe_operations",
            "add_dataframe_validation",
            "generate_data_cleaning_pipeline",
            "translate_advanced_pandas",
            "generate_exploratory_analysis",
            "validate_pandas_code",
            "get_module_info",
            "validate_code"
        ]
    
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate pandas module usage."""
        issues = []
        
        # Check for common anti-patterns
        if "pd." in code and "stx.pd" not in code and "scitex" in code:
            issues.append("Using pandas directly instead of stx.pd enhancements")
        
        if ".describe()" in code and ".stx_describe()" not in code and "scitex" in code:
            issues.append("Use .stx_describe() for enhanced statistics")
        
        # Check for proper imports
        if "pandas" in code and "import pandas as pd" not in code:
            issues.append("Missing proper pandas import")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "module": "pd"
        }


# Main entry point
if __name__ == "__main__":
    server = ScitexPdMCPServer()
    asyncio.run(server.run())

# EOF