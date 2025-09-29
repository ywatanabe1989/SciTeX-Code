#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./tests/scitex/stats/multiple/test__multicompair.py

import pytest
import numpy as np
import scipy.stats as stats
import scitex


class TestImports:
    def test_import_main(self):
        import scitex

    def test_import_submodule(self):
        import scitex.stats

    def test_import_target(self):
        import scitex.stats.multiple._multicompair
    
    def test_import_from_stats(self):
        # Test that multicompair is available from stats module
        assert hasattr(scitex.stats, 'multicompair')


class TestMulticompair:
    """Test multicompair function for multiple comparison tests."""
    
    def test_basic_functionality(self):
        """Test basic multiple comparison with default Tukey HSD."""
        # Create sample data with three groups
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 30)
        group2 = np.random.normal(105, 10, 30)
        group3 = np.random.normal(110, 10, 30)
        
        data = [group1, group2, group3]
        labels = ['Group1', 'Group2', 'Group3']
        
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        
        # Check that result is returned (summary object)
        assert result is not None
    
    def test_with_custom_test_function(self):
        """Test with custom test function (e.g., Welch's t-test)."""
        np.random.seed(42)
        group1 = np.random.normal(0, 1, 20)
        group2 = np.random.normal(0.5, 1, 20)
        
        data = [group1, group2]
        labels = ['Control', 'Treatment']
        
        # Define custom test function (Welch's t-test)
        def welch_ttest(x, y):
            return stats.ttest_ind(x, y, equal_var=False)
        
        result = scitex.stats.multiple._multicompair.multicompair(
            data, labels, testfunc=welch_ttest
        )
        
        assert result is not None
    
    def test_different_group_sizes(self):
        """Test with groups of different sizes."""
        np.random.seed(42)
        group1 = np.random.normal(0, 1, 15)
        group2 = np.random.normal(1, 1, 25)
        group3 = np.random.normal(2, 1, 20)
        
        data = [group1, group2, group3]
        labels = ['Small', 'Large', 'Medium']
        
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result is not None
    
    def test_two_groups_comparison(self):
        """Test with only two groups."""
        np.random.seed(42)
        group1 = np.random.normal(10, 2, 50)
        group2 = np.random.normal(12, 2, 50)
        
        data = [group1, group2]
        labels = ['A', 'B']
        
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result is not None
    
    def test_many_groups_comparison(self):
        """Test with many groups."""
        np.random.seed(42)
        n_groups = 6
        data = []
        labels = []
        
        for i in range(n_groups):
            group_data = np.random.normal(i * 2, 1, 30)
            data.append(group_data)
            labels.append(f'Group_{i}')
        
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result is not None
    
    def test_label_handling(self):
        """Test that labels are properly handled."""
        np.random.seed(42)
        group1 = np.random.normal(0, 1, 10)
        group2 = np.random.normal(1, 1, 10)
        
        data = [group1, group2]
        labels = ['First_Group', 'Second_Group']
        
        # The function should handle label copying and expansion
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result is not None
    
    def test_with_brunner_munzel_test(self):
        """Test with Brunner-Munzel test function."""
        np.random.seed(42)
        group1 = np.random.normal(0, 1, 20)
        group2 = np.random.normal(0.5, 2, 20)  # Different variance
        
        data = [group1, group2]
        labels = ['Group1', 'Group2']
        
        # Brunner-Munzel test for unequal variances
        result = scitex.stats.multiple._multicompair.multicompair(
            data, labels, testfunc=stats.brunnermunzel
        )
        
        assert result is not None


class TestMulticompairWrapper:
    """Test the wrapper function from stats module."""
    
    def test_wrapper_functionality(self):
        """Test wrapper returns expected dictionary format."""
        np.random.seed(42)
        group1 = np.random.normal(0, 1, 25)
        group2 = np.random.normal(0.5, 1, 25)
        group3 = np.random.normal(1, 1, 25)
        
        groups = [group1, group2, group3]
        
        result = scitex.stats.multicompair(groups)
        
        # Wrapper should return dictionary
        assert isinstance(result, dict)
        assert 'summary' in result
        assert 'p_values' in result
        assert 'test_statistic' in result
        
        # Check array shapes
        assert isinstance(result['p_values'], np.ndarray)
        assert isinstance(result['test_statistic'], np.ndarray)


class TestIntegration:
    """Integration tests for multicompair functionality."""
    
    def test_anova_like_scenario(self):
        """Test in ANOVA-like scenario with multiple groups."""
        np.random.seed(42)
        
        # Simulate data from different treatments
        control = np.random.normal(100, 15, 40)
        treatment1 = np.random.normal(110, 15, 40)
        treatment2 = np.random.normal(120, 15, 40)
        treatment3 = np.random.normal(105, 15, 40)
        
        data = [control, treatment1, treatment2, treatment3]
        labels = ['Control', 'Treat1', 'Treat2', 'Treat3']
        
        # Perform multiple comparisons
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        
        # Should detect significant differences
        assert result is not None
    
    def test_no_difference_scenario(self):
        """Test when all groups come from same distribution."""
        np.random.seed(42)
        
        # All groups from same distribution
        data = []
        labels = []
        for i in range(4):
            group = np.random.normal(50, 10, 30)
            data.append(group)
            labels.append(f'Group{i}')
        
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        
        # Should find no significant differences
        assert result is not None
    
    def test_with_outliers(self):
        """Test robustness with outliers."""
        np.random.seed(42)
        
        # Create data with outliers
        group1 = np.random.normal(0, 1, 30)
        group1[0] = 10  # Add outlier
        group1[1] = -10  # Add outlier
        
        group2 = np.random.normal(1, 1, 30)
        group2[0] = 15  # Add outlier
        
        data = [group1, group2]
        labels = ['WithOutliers1', 'WithOutliers2']
        
        # Should still work with outliers
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result is not None
    
    def test_real_world_example(self):
        """Test with realistic experimental design."""
        np.random.seed(42)
        
        # Simulate drug trial with placebo and doses
        placebo = np.random.normal(100, 20, 35)
        low_dose = np.random.normal(95, 20, 32)
        medium_dose = np.random.normal(85, 18, 38)
        high_dose = np.random.normal(75, 15, 30)
        
        data = [placebo, low_dose, medium_dose, high_dose]
        labels = ['Placebo', 'Low', 'Medium', 'High']
        
        # Test with default method
        result_tukey = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result_tukey is not None
        
        # Test with custom test function
        def custom_test(x, y):
            # Use Mann-Whitney U test for non-parametric comparison
            return stats.mannwhitneyu(x, y, alternative='two-sided')
        
        result_custom = scitex.stats.multiple._multicompair.multicompair(
            data, labels, testfunc=custom_test
        )
        assert result_custom is not None
    
    def test_edge_cases(self):
        """Test edge cases."""
        np.random.seed(42)
        
        # Very small samples
        group1 = np.array([1.0, 2.0, 3.0])
        group2 = np.array([4.0, 5.0, 6.0])
        
        data = [group1, group2]
        labels = ['Tiny1', 'Tiny2']
        
        result = scitex.stats.multiple._multicompair.multicompair(data, labels)
        assert result is not None
        
        # Identical groups
        identical1 = np.ones(20) * 5
        identical2 = np.ones(20) * 5
        
        data_identical = [identical1, identical2]
        labels_identical = ['Same1', 'Same2']
        
        result_identical = scitex.stats.multiple._multicompair.multicompair(
            data_identical, labels_identical
        )
        assert result_identical is not None


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/multiple/_multicompair.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# 
# import numpy as np
# import scipy.stats as stats
# from statsmodels.stats.multicomp import MultiComparison
# 
# 
# def multicompair(data, labels, testfunc=None):
#     # https://pythonhealthcare.org/2018/04/13/55-statistics-multi-comparison-with-tukeys-test-and-the-holm-bonferroni-method/
#     _labels = labels.copy()
#     # Set up the data for comparison (creates a specialised object)
#     for i_labels in range(len(_labels)):
#         _labels[i_labels] = [_labels[i_labels] for i_data in range(len(data[i_labels]))]
# 
#     data, _labels = np.hstack(data), np.hstack(_labels)
#     MultiComp = MultiComparison(data, _labels)
# 
#     if testfunc is not None:
#         # print(MultiComp.allpairtest(testfunc, mehotd='bonf', pvalidx=1))
#         return MultiComp.allpairtest(testfunc, method="bonf", pvalidx=1)
#     else:
#         # print(MultiComp.tukeyhsd().summary())
#         return MultiComp.tukeyhsd().summary()
# 
# 
# # t_statistic, p_value = scipy.stats.ttest_ind(data1, data2, equal_var=False) # Welch's t test
# # W_statistic, p_value = scipy.stats.brunnermunzel(data1, data2)
# # H_statistic, p_value = scipy.stats.kruskal(*data) # one-way ANOVA on RANKs

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/multiple/_multicompair.py
# --------------------------------------------------------------------------------
