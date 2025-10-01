#!/usr/bin/env python3
"""Effect size calculations for statistical tests.

This module provides functions to calculate and interpret effect sizes
for various statistical tests, helping researchers understand the 
practical significance of their results beyond p-values.
"""

from typing import Union, Tuple, Dict, Optional
import numpy as np
import scipy.stats
import warnings
from ..errors import SciTeXWarning


class EffectSizeCalculator:
    """Calculate and interpret effect sizes for statistical tests."""
    
    @staticmethod
    def cohens_d(
        group1: Union[np.ndarray, list],
        group2: Union[np.ndarray, list],
        pooled: bool = True
    ) -> Dict[str, Union[float, str]]:
        """Calculate Cohen's d effect size for two groups.
        
        Parameters
        ----------
        group1, group2 : array-like
            Data from two groups to compare
        pooled : bool, default=True
            Whether to use pooled standard deviation
            
        Returns
        -------
        result : dict
            Dictionary containing:
            - d: Cohen's d value
            - interpretation: Qualitative interpretation
            - ci_lower, ci_upper: 95% confidence interval
            - n1, n2: Sample sizes
        """
        g1 = np.asarray(group1)[~np.isnan(group1)]
        g2 = np.asarray(group2)[~np.isnan(group2)]
        
        n1, n2 = len(g1), len(g2)
        mean1, mean2 = np.mean(g1), np.mean(g2)
        
        if pooled:
            # Pooled standard deviation
            var1, var2 = np.var(g1, ddof=1), np.var(g2, ddof=1)
            pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
            pooled_std = np.sqrt(pooled_var)
            d = (mean1 - mean2) / pooled_std
        else:
            # Glass's delta (uses control group SD)
            d = (mean1 - mean2) / np.std(g2, ddof=1)
        
        # Calculate confidence interval
        se_d = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
        ci_lower = d - 1.96 * se_d
        ci_upper = d + 1.96 * se_d
        
        # Interpret effect size
        abs_d = abs(d)
        if abs_d < 0.2:
            interpretation = "negligible"
        elif abs_d < 0.5:
            interpretation = "small"
        elif abs_d < 0.8:
            interpretation = "medium"
        else:
            interpretation = "large"
        
        return {
            'd': d,
            'interpretation': interpretation,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'n1': n1,
            'n2': n2,
            'mean_diff': mean1 - mean2
        }
    
    @staticmethod
    def hedges_g(
        group1: Union[np.ndarray, list],
        group2: Union[np.ndarray, list]
    ) -> Dict[str, Union[float, str]]:
        """Calculate Hedges' g (bias-corrected Cohen's d).
        
        Better for small sample sizes (n < 20).
        
        Parameters
        ----------
        group1, group2 : array-like
            Data from two groups to compare
            
        Returns
        -------
        result : dict
            Dictionary with Hedges' g and related statistics
        """
        # First calculate Cohen's d
        d_result = EffectSizeCalculator.cohens_d(group1, group2)
        d = d_result['d']
        n1, n2 = d_result['n1'], d_result['n2']
        
        # Correction factor
        df = n1 + n2 - 2
        correction = 1 - 3 / (4 * df - 1)
        g = d * correction
        
        # Adjust confidence intervals
        ci_lower = d_result['ci_lower'] * correction
        ci_upper = d_result['ci_upper'] * correction
        
        return {
            'g': g,
            'interpretation': d_result['interpretation'],  # Same thresholds
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'n1': n1,
            'n2': n2,
            'correction_factor': correction
        }
    
    @staticmethod
    def glass_delta(
        treatment: Union[np.ndarray, list],
        control: Union[np.ndarray, list]
    ) -> Dict[str, Union[float, str]]:
        """Calculate Glass's delta using control group SD.
        
        Useful when groups have very different variances.
        
        Parameters
        ----------
        treatment : array-like
            Treatment group data
        control : array-like
            Control group data (SD used for standardization)
            
        Returns
        -------
        result : dict
            Dictionary with Glass's delta and related statistics
        """
        return EffectSizeCalculator.cohens_d(treatment, control, pooled=False)
    
    @staticmethod
    def eta_squared(
        groups: list,
        partial: bool = False
    ) -> Dict[str, Union[float, str]]:
        """Calculate eta-squared for ANOVA.
        
        Parameters
        ----------
        groups : list of array-like
            List of groups to compare
        partial : bool, default=False
            Whether to calculate partial eta-squared
            
        Returns
        -------
        result : dict
            Dictionary with eta-squared and interpretation
        """
        # Clean data
        groups_clean = [np.asarray(g)[~np.isnan(g)] for g in groups]
        
        # Calculate sum of squares
        all_data = np.concatenate(groups_clean)
        grand_mean = np.mean(all_data)
        
        # Between-group sum of squares
        ss_between = sum(
            len(g) * (np.mean(g) - grand_mean)**2 
            for g in groups_clean
        )
        
        # Within-group sum of squares
        ss_within = sum(
            np.sum((g - np.mean(g))**2) 
            for g in groups_clean
        )
        
        # Total sum of squares
        ss_total = ss_between + ss_within
        
        if partial:
            eta2 = ss_between / (ss_between + ss_within)
            eta_type = "partial_eta_squared"
        else:
            eta2 = ss_between / ss_total
            eta_type = "eta_squared"
        
        # Interpret effect size
        if eta2 < 0.01:
            interpretation = "negligible"
        elif eta2 < 0.06:
            interpretation = "small"
        elif eta2 < 0.14:
            interpretation = "medium"
        else:
            interpretation = "large"
        
        return {
            eta_type: eta2,
            'interpretation': interpretation,
            'ss_between': ss_between,
            'ss_within': ss_within,
            'ss_total': ss_total,
            'n_groups': len(groups_clean),
            'total_n': len(all_data)
        }
    
    @staticmethod
    def omega_squared(groups: list) -> Dict[str, Union[float, str]]:
        """Calculate omega-squared (less biased than eta-squared).
        
        Parameters
        ----------
        groups : list of array-like
            List of groups to compare
            
        Returns
        -------
        result : dict
            Dictionary with omega-squared and interpretation
        """
        eta_result = EffectSizeCalculator.eta_squared(groups)
        
        ss_between = eta_result['ss_between']
        ss_within = eta_result['ss_within']
        ss_total = eta_result['ss_total']
        k = eta_result['n_groups']
        N = eta_result['total_n']
        
        # Mean square within
        ms_within = ss_within / (N - k)
        
        # Omega squared formula
        omega2 = (ss_between - (k - 1) * ms_within) / (ss_total + ms_within)
        omega2 = max(0, omega2)  # Can't be negative
        
        # Same interpretation thresholds as eta-squared
        if omega2 < 0.01:
            interpretation = "negligible"
        elif omega2 < 0.06:
            interpretation = "small"
        elif omega2 < 0.14:
            interpretation = "medium"
        else:
            interpretation = "large"
        
        return {
            'omega_squared': omega2,
            'interpretation': interpretation,
            'ms_within': ms_within,
            'df_between': k - 1,
            'df_within': N - k
        }
    
    @staticmethod
    def correlation_to_r2(r: float) -> Dict[str, Union[float, str]]:
        """Convert correlation coefficient to coefficient of determination.
        
        Parameters
        ----------
        r : float
            Correlation coefficient
            
        Returns
        -------
        result : dict
            Dictionary with r-squared and interpretation
        """
        r2 = r ** 2
        
        # Interpret variance explained
        if r2 < 0.02:
            interpretation = "negligible"
        elif r2 < 0.13:
            interpretation = "small"
        elif r2 < 0.26:
            interpretation = "medium"
        else:
            interpretation = "large"
        
        return {
            'r': r,
            'r_squared': r2,
            'variance_explained': f"{r2 * 100:.1f}%",
            'interpretation': interpretation
        }
    
    @staticmethod
    def odds_ratio(
        table: Union[np.ndarray, list],
        alpha: float = 0.05
    ) -> Dict[str, Union[float, str, Tuple[float, float]]]:
        """Calculate odds ratio for 2x2 contingency table.
        
        Parameters
        ----------
        table : array-like
            2x2 contingency table [[a, b], [c, d]]
        alpha : float, default=0.05
            Significance level for confidence interval
            
        Returns
        -------
        result : dict
            Dictionary with odds ratio and confidence interval
        """
        table = np.asarray(table)
        if table.shape != (2, 2):
            raise ValueError("Table must be 2x2")
        
        a, b, c, d = table.flatten()
        
        # Add small constant to avoid division by zero
        if 0 in [a, b, c, d]:
            warnings.warn(
                "Zero cell detected, adding 0.5 to all cells",
                SciTeXWarning
            )
            a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        
        or_value = (a * d) / (b * c)
        log_or = np.log(or_value)
        se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d)
        
        # Confidence interval
        z = scipy.stats.norm.ppf(1 - alpha/2)
        ci_lower = np.exp(log_or - z * se_log_or)
        ci_upper = np.exp(log_or + z * se_log_or)
        
        # Interpret
        if or_value < 0.5:
            interpretation = "strong negative association"
        elif or_value < 0.67:
            interpretation = "moderate negative association"
        elif or_value < 1.5:
            interpretation = "weak or no association"
        elif or_value < 3.0:
            interpretation = "moderate positive association"
        else:
            interpretation = "strong positive association"
        
        return {
            'odds_ratio': or_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'log_or': log_or,
            'interpretation': interpretation,
            'significant': not (ci_lower <= 1 <= ci_upper)
        }
    
    @staticmethod
    def relative_risk(
        table: Union[np.ndarray, list],
        alpha: float = 0.05
    ) -> Dict[str, Union[float, str, Tuple[float, float]]]:
        """Calculate relative risk for 2x2 contingency table.
        
        Parameters
        ----------
        table : array-like
            2x2 contingency table [[exposed_disease, exposed_no_disease],
                                   [unexposed_disease, unexposed_no_disease]]
        alpha : float, default=0.05
            Significance level for confidence interval
            
        Returns
        -------
        result : dict
            Dictionary with relative risk and confidence interval
        """
        table = np.asarray(table)
        if table.shape != (2, 2):
            raise ValueError("Table must be 2x2")
        
        a, b, c, d = table.flatten()
        
        # Risk in exposed and unexposed
        risk_exposed = a / (a + b) if (a + b) > 0 else 0
        risk_unexposed = c / (c + d) if (c + d) > 0 else 0
        
        # Relative risk
        if risk_unexposed == 0:
            rr = np.inf if risk_exposed > 0 else 1.0
            log_rr = np.log(rr) if rr != np.inf else np.nan
        else:
            rr = risk_exposed / risk_unexposed
            log_rr = np.log(rr)
        
        # Standard error of log(RR)
        se_log_rr = np.sqrt(
            1/a - 1/(a+b) + 1/c - 1/(c+d)
        ) if all(x > 0 for x in [a, a+b, c, c+d]) else np.nan
        
        # Confidence interval
        if not np.isnan(se_log_rr):
            z = scipy.stats.norm.ppf(1 - alpha/2)
            ci_lower = np.exp(log_rr - z * se_log_rr)
            ci_upper = np.exp(log_rr + z * se_log_rr)
        else:
            ci_lower, ci_upper = np.nan, np.nan
        
        # Interpret
        if rr < 0.5:
            interpretation = "strong protective effect"
        elif rr < 0.8:
            interpretation = "moderate protective effect"
        elif rr < 1.25:
            interpretation = "no effect"
        elif rr < 2.0:
            interpretation = "moderate risk increase"
        else:
            interpretation = "strong risk increase"
        
        return {
            'relative_risk': rr,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'risk_exposed': risk_exposed,
            'risk_unexposed': risk_unexposed,
            'interpretation': interpretation,
            'significant': not (ci_lower <= 1 <= ci_upper) if not np.isnan(ci_lower) else False
        }
    
    @staticmethod
    def cramers_v(
        chi2_statistic: float,
        n: int,
        df: int
    ) -> Dict[str, Union[float, str]]:
        """Calculate Cramér's V for chi-square test.
        
        Parameters
        ----------
        chi2_statistic : float
            Chi-square test statistic
        n : int
            Total sample size
        df : int
            Degrees of freedom
            
        Returns
        -------
        result : dict
            Dictionary with Cramér's V and interpretation
        """
        # For 2x2 table, this reduces to phi coefficient
        min_dim = min(df + 1, 2)  # Assuming rectangular table
        
        v = np.sqrt(chi2_statistic / (n * (min_dim - 1)))
        
        # Interpret based on degrees of freedom
        if df == 1:  # 2x2 table
            if v < 0.1:
                interpretation = "negligible"
            elif v < 0.3:
                interpretation = "small"
            elif v < 0.5:
                interpretation = "medium"
            else:
                interpretation = "large"
        else:  # Larger tables
            if v < 0.05:
                interpretation = "negligible"
            elif v < 0.15:
                interpretation = "small"
            elif v < 0.25:
                interpretation = "medium"
            else:
                interpretation = "large"
        
        return {
            'cramers_v': v,
            'interpretation': interpretation,
            'chi2': chi2_statistic,
            'n': n,
            'df': df
        }