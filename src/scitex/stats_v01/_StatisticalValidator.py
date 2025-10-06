#!/usr/bin/env python3
"""Statistical validation framework for ensuring scientific validity.

This module provides validation tools to check statistical assumptions
before running tests, helping ensure the validity of scientific results.
"""

import warnings
from typing import Union, Tuple, Dict, Optional, List
import numpy as np
import scipy.stats
from ..errors import SciTeXWarning


class StatisticalValidator:
    """Validate assumptions before running statistical tests.
    
    This class provides methods to check common statistical assumptions
    such as normality, homoscedasticity, and sample size requirements.
    """
    
    @staticmethod
    def check_normality(
        data: Union[np.ndarray, list], 
        alpha: float = 0.05,
        test: str = 'shapiro'
    ) -> Tuple[bool, float, Dict[str, float]]:
        """Check if data follows normal distribution.
        
        Parameters
        ----------
        data : array-like
            Data to test for normality
        alpha : float, default=0.05
            Significance level for the test
        test : str, default='shapiro'
            Test to use ('shapiro', 'anderson', 'normaltest')
            
        Returns
        -------
        is_normal : bool
            True if data appears normally distributed
        p_value : float
            P-value from the normality test
        stats : dict
            Additional statistics (skew, kurtosis, etc.)
        """
        data = np.asarray(data)
        data = data[~np.isnan(data)]  # Remove NaN values
        
        if len(data) < 3:
            warnings.warn(
                "Sample size too small for normality test (n < 3)",
                SciTeXWarning
            )
            return False, 0.0, {}
        
        stats_dict = {
            'n': len(data),
            'skew': scipy.stats.skew(data),
            'kurtosis': scipy.stats.kurtosis(data)
        }
        
        if test == 'shapiro':
            if len(data) > 5000:
                warnings.warn(
                    "Shapiro-Wilk test may be inaccurate for n > 5000",
                    SciTeXWarning
                )
            stat, p_value = scipy.stats.shapiro(data)
            stats_dict['shapiro_stat'] = stat
            
        elif test == 'anderson':
            result = scipy.stats.anderson(data)
            # Use 5% significance level
            critical_value = result.critical_values[2]
            p_value = 1.0 if result.statistic < critical_value else 0.0
            stats_dict['anderson_stat'] = result.statistic
            stats_dict['critical_values'] = dict(zip(
                result.significance_level, 
                result.critical_values
            ))
            
        elif test == 'normaltest':
            stat, p_value = scipy.stats.normaltest(data)
            stats_dict['normaltest_stat'] = stat
            
        else:
            raise ValueError(f"Unknown normality test: {test}")
        
        is_normal = p_value > alpha
        
        if not is_normal:
            warnings.warn(
                f"Data may not be normally distributed (p={p_value:.4f}). "
                f"Consider using non-parametric tests.",
                SciTeXWarning
            )
        
        return is_normal, p_value, stats_dict
    
    @staticmethod
    def check_homoscedasticity(
        *groups: Union[np.ndarray, list],
        alpha: float = 0.05,
        test: str = 'levene'
    ) -> Tuple[bool, float, Dict[str, float]]:
        """Check for equal variances across groups.
        
        Parameters
        ----------
        *groups : array-like
            Groups to test for equal variances
        alpha : float, default=0.05
            Significance level for the test
        test : str, default='levene'
            Test to use ('levene', 'bartlett', 'fligner')
            
        Returns
        -------
        is_homoscedastic : bool
            True if variances appear equal
        p_value : float
            P-value from the test
        stats : dict
            Additional statistics (variances, ratio, etc.)
        """
        groups = [np.asarray(g)[~np.isnan(g)] for g in groups]
        
        if len(groups) < 2:
            raise ValueError("Need at least 2 groups for homoscedasticity test")
        
        variances = [np.var(g, ddof=1) for g in groups]
        max_var = max(variances)
        min_var = min(variances) if min(variances) > 0 else 1e-10
        
        stats_dict = {
            'variances': variances,
            'variance_ratio': max_var / min_var,
            'n_groups': len(groups),
            'group_sizes': [len(g) for g in groups]
        }
        
        if test == 'levene':
            stat, p_value = scipy.stats.levene(*groups, center='median')
            stats_dict['levene_stat'] = stat
            
        elif test == 'bartlett':
            # Bartlett's test is sensitive to non-normality
            stat, p_value = scipy.stats.bartlett(*groups)
            stats_dict['bartlett_stat'] = stat
            
        elif test == 'fligner':
            # Fligner-Killeen test is robust to non-normality
            stat, p_value = scipy.stats.fligner(*groups)
            stats_dict['fligner_stat'] = stat
            
        else:
            raise ValueError(f"Unknown homoscedasticity test: {test}")
        
        is_homoscedastic = p_value > alpha
        
        if not is_homoscedastic:
            warnings.warn(
                f"Variances may not be equal (p={p_value:.4f}). "
                f"Consider using Welch's t-test or non-parametric tests.",
                SciTeXWarning
            )
        
        return is_homoscedastic, p_value, stats_dict
    
    @staticmethod
    def validate_sample_size(
        data: Union[np.ndarray, list, List[np.ndarray]],
        test_type: str,
        min_size: Optional[int] = None,
        warn_only: bool = True
    ) -> Tuple[bool, Dict[str, Union[int, str]]]:
        """Validate sample size for statistical tests.
        
        Parameters
        ----------
        data : array-like or list of array-like
            Data to check sample size
        test_type : str
            Type of test ('t_test', 'anova', 'correlation', etc.)
        min_size : int, optional
            Minimum required size (uses defaults if None)
        warn_only : bool, default=True
            If True, only warn; if False, return False for inadequate size
            
        Returns
        -------
        is_adequate : bool
            True if sample size is adequate
        info : dict
            Information about sample size and recommendations
        """
        MIN_SIZES = {
            't_test': 30,
            't_test_paired': 20,
            'mann_whitney': 20,
            'wilcoxon': 15,
            'anova': 20,  # per group
            'kruskal': 15,  # per group
            'correlation': 30,
            'chi_square': 5,  # per cell
            'regression': 50,  # 10-20 per variable
            'brunner_munzel': 10  # per group
        }
        
        POWER_RECOMMENDATIONS = {
            't_test': "For 80% power with medium effect (d=0.5), need ~64 per group",
            'anova': "For 80% power with medium effect (f=0.25), need ~52 per group",
            'correlation': "For 80% power with medium effect (r=0.3), need ~85 pairs",
            'regression': "Need 10-20 observations per predictor variable"
        }
        
        min_required = min_size or MIN_SIZES.get(test_type, 30)
        
        if isinstance(data, list) and all(hasattr(d, '__len__') for d in data):
            # Multiple groups
            sizes = [len(np.asarray(d)[~np.isnan(d)]) for d in data]
            actual_size = min(sizes)
            info = {
                'group_sizes': sizes,
                'min_group_size': actual_size,
                'recommended_min': min_required,
                'test_type': test_type
            }
        else:
            # Single group
            data_clean = np.asarray(data)[~np.isnan(data)]
            actual_size = len(data_clean)
            info = {
                'sample_size': actual_size,
                'recommended_min': min_required,
                'test_type': test_type
            }
        
        is_adequate = actual_size >= min_required
        
        if not is_adequate:
            message = (
                f"Sample size ({actual_size}) may be too small for {test_type} "
                f"(recommended minimum: {min_required}). "
            )
            
            if test_type in POWER_RECOMMENDATIONS:
                message += POWER_RECOMMENDATIONS[test_type]
                info['power_recommendation'] = POWER_RECOMMENDATIONS[test_type]
            
            if warn_only:
                warnings.warn(message, SciTeXWarning)
            else:
                info['warning'] = message
        
        info['is_adequate'] = is_adequate
        
        return is_adequate, info
    
    @staticmethod
    def check_paired_data(
        x: Union[np.ndarray, list],
        y: Union[np.ndarray, list]
    ) -> Tuple[bool, Dict[str, Union[int, float]]]:
        """Check if paired data is valid for paired tests.
        
        Parameters
        ----------
        x, y : array-like
            Paired data arrays
            
        Returns
        -------
        is_valid : bool
            True if data is valid for paired tests
        info : dict
            Information about the paired data
        """
        x = np.asarray(x)
        y = np.asarray(y)
        
        # Check lengths
        if len(x) != len(y):
            warnings.warn(
                f"Paired data must have equal lengths (x: {len(x)}, y: {len(y)})",
                SciTeXWarning
            )
            return False, {'x_length': len(x), 'y_length': len(y)}
        
        # Check for paired NaN values
        paired_nan = np.isnan(x) | np.isnan(y)
        n_valid = np.sum(~paired_nan)
        
        info = {
            'total_pairs': len(x),
            'valid_pairs': n_valid,
            'missing_pairs': np.sum(paired_nan),
            'correlation': np.corrcoef(x[~paired_nan], y[~paired_nan])[0, 1]
        }
        
        if n_valid < 3:
            warnings.warn(
                f"Too few valid pairs for analysis (n={n_valid})",
                SciTeXWarning
            )
            return False, info
        
        return True, info
    
    @staticmethod
    def suggest_test(
        data_characteristics: Dict[str, Union[bool, int, float]],
        hypothesis: str = 'two_sample'
    ) -> Dict[str, Union[str, List[str]]]:
        """Suggest appropriate statistical test based on data characteristics.
        
        Parameters
        ----------
        data_characteristics : dict
            Dictionary with keys like 'is_normal', 'is_homoscedastic', 
            'n_groups', 'is_paired', 'sample_size'
        hypothesis : str
            Type of hypothesis ('two_sample', 'multi_sample', 'correlation', 
            'association', 'regression')
            
        Returns
        -------
        suggestions : dict
            Recommended tests with rationale
        """
        suggestions = {
            'primary': None,
            'alternatives': [],
            'rationale': []
        }
        
        is_normal = data_characteristics.get('is_normal', False)
        is_homoscedastic = data_characteristics.get('is_homoscedastic', False)
        n_groups = data_characteristics.get('n_groups', 2)
        is_paired = data_characteristics.get('is_paired', False)
        sample_size = data_characteristics.get('sample_size', 30)
        
        if hypothesis == 'two_sample':
            if is_paired:
                if is_normal:
                    suggestions['primary'] = 'paired_t_test'
                    suggestions['alternatives'] = ['wilcoxon_signed_rank']
                else:
                    suggestions['primary'] = 'wilcoxon_signed_rank'
                    suggestions['alternatives'] = ['sign_test']
                suggestions['rationale'].append(
                    "Paired data detected - using paired tests"
                )
            else:
                if is_normal and is_homoscedastic:
                    suggestions['primary'] = 'independent_t_test'
                    suggestions['alternatives'] = ['mann_whitney_u']
                elif is_normal and not is_homoscedastic:
                    suggestions['primary'] = 'welch_t_test'
                    suggestions['alternatives'] = ['brunner_munzel']
                    suggestions['rationale'].append(
                        "Unequal variances - using Welch's correction"
                    )
                else:
                    suggestions['primary'] = 'brunner_munzel'
                    suggestions['alternatives'] = ['mann_whitney_u']
                    suggestions['rationale'].append(
                        "Non-normal data - using robust non-parametric test"
                    )
                    
        elif hypothesis == 'multi_sample':
            if n_groups > 2:
                if is_normal and is_homoscedastic:
                    suggestions['primary'] = 'one_way_anova'
                    suggestions['alternatives'] = ['kruskal_wallis']
                else:
                    suggestions['primary'] = 'kruskal_wallis'
                    suggestions['alternatives'] = ['friedman_test' if is_paired else None]
                    suggestions['rationale'].append(
                        f"{'Non-normal' if not is_normal else 'Heteroscedastic'} "
                        f"data - using non-parametric test"
                    )
                    
        elif hypothesis == 'correlation':
            if is_normal:
                suggestions['primary'] = 'pearson_correlation'
                suggestions['alternatives'] = ['spearman_correlation']
            else:
                suggestions['primary'] = 'spearman_correlation'
                suggestions['alternatives'] = ['kendall_tau']
                suggestions['rationale'].append(
                    "Non-normal data - using rank correlation"
                )
                
        # Add sample size considerations
        if sample_size < 20:
            suggestions['rationale'].append(
                f"Small sample size (n={sample_size}) - "
                f"consider exact/permutation tests"
            )
            if 'exact_test' not in suggestions['alternatives']:
                suggestions['alternatives'].append('permutation_test')
        
        # Remove None values from alternatives
        suggestions['alternatives'] = [
            alt for alt in suggestions['alternatives'] if alt is not None
        ]
        
        return suggestions