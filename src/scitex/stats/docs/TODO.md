<!-- ---
!-- Timestamp: 2025-10-01 12:55:00
!-- Author: ywatanabe + Claude Code
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/stats/TODO.md
!-- --- -->

# SciTeX Stats - TODO

## ✅ Completed (Version 2.0.0)

### Architecture
- ✅ Organized module structure
  - ✅ `scitex.stats.tests` - 23 statistical tests
  - ✅ `scitex.stats.correct` - 4 multiple comparison corrections
  - ✅ `scitex.stats.posthoc` - 3 post-hoc tests
  - ✅ `scitex.stats.effect_sizes` - Effect size computations
  - ✅ `scitex.stats.power` - Power analysis
  - ✅ `scitex.stats.utils` - Formatters and normalizers
- ✅ Normalized naming (all tests use `test_*` prefix, posthoc use `posthoc_*`)
- ✅ No backward compatibility (clean slate)
- ✅ Consistent API across all tests

### Tests Implemented (23)
- ✅ **Parametric (6)**: t-tests (ind, rel, 1samp), ANOVA (one-way, repeated measures, two-way)
- ✅ **Non-parametric (5)**: Brunner-Munzel, Wilcoxon, Kruskal, Mann-Whitney, Friedman
- ✅ **Normality (4)**: Shapiro-Wilk, test_normality, KS (1samp, 2samp)
- ✅ **Correlation (3)**: Pearson, Spearman, Kendall's tau
- ✅ **Categorical (4)**: Chi-square, Fisher's exact, McNemar, Cochran's Q

### Corrections (4)
- ✅ **Bonferroni**: Conservative FWER control
- ✅ **Holm**: Sequential Bonferroni
- ✅ **FDR (Benjamini-Hochberg)**: False discovery rate
- ✅ **Šidák**: More powerful than Bonferroni under independence

### Post-hoc Tests (3)
- ✅ **Tukey HSD**: All pairwise comparisons (equal variances)
- ✅ **Games-Howell**: Unequal variances (Welch-Satterthwaite)
- ✅ **Dunnett**: Multiple treatments vs control

### Features
- ✅ Standardized output format (dict and DataFrame)
- ✅ 9 export formats (CSV, LaTeX, Excel, JSON, etc.)
- ✅ Publication-ready visualizations
- ✅ Automatic assumption checking
- ✅ Comprehensive effect sizes with interpretations
- ✅ Power analysis for t-tests
- ✅ `decimals=3` default rounding

### Documentation
- ✅ README.md - Professional overview
- ✅ QUICKSTART.md - Quick start guide with examples
- ✅ docs/API.md - Complete API reference
- ✅ docs/PROGRESS.md - Detailed implementation with examples
- ✅ docs/SUMMARY.md - Comprehensive summary and comparisons

---

## 🔄 In Progress

None - Version 2.0.0 is complete and production-ready!

---

## 📋 Future Enhancements (Version 2.1+)

### High Priority (Version 2.1+)
- ✅ **Šidák correction** (COMPLETED)
  - Alternative to Bonferroni assuming independence
  - Formula: 1 - (1-α)^(1/m)
  - More powerful than Bonferroni under independence

- ✅ **McNemar's test** (COMPLETED)
  - Paired categorical data
  - 2×2 contingency tables for matched pairs
  - Odds ratio effect size

- ✅ **Repeated measures ANOVA** (COMPLETED)
  - Within-subjects factor
  - Sphericity testing (Mauchly's test)
  - Greenhouse-Geisser correction
  - Partial eta-squared effect size

- ✅ **Two-way ANOVA** (COMPLETED)
  - Factorial design (2 factors)
  - Main effects and interaction effects
  - Partial eta-squared for each effect
  - Interaction plots

### Medium Priority (Version 2.1+)
- ✅ **Kendall's tau correlation** (COMPLETED)
  - Alternative to Spearman
  - Better for small samples with ties
  - tau-b and tau-c variants

- ✅ **Friedman test** (COMPLETED)
  - Non-parametric repeated measures ANOVA
  - 3+ related samples
  - Kendall's W effect size

- ✅ **Cochran's Q test** (COMPLETED)
  - Binary repeated measures
  - Extension of McNemar's test to 3+ conditions
  - Kendall's W for binary data

- [ ] **Bootstrap confidence intervals**
  - For effect sizes
  - Non-parametric CI estimation

- ✅ **Post-hoc framework enhancement** (COMPLETED)
  - ✅ Tukey HSD - All pairwise comparisons
  - ✅ Games-Howell - Unequal variances
  - ✅ Dunnett - Multiple treatments vs control

### Low Priority
- [ ] **Permutation tests**
  - General non-parametric alternative
  - Exact p-values

- [ ] **Mixed-effects models interface**
  - Basic linear mixed models
  - Random effects

- [ ] **Bayesian alternatives**
  - Bayes factors
  - Credible intervals

- [ ] **Time series tests**
  - Autocorrelation tests
  - Stationarity tests

- [ ] **Survival analysis basics**
  - Log-rank test
  - Kaplan-Meier curves

### Infrastructure Improvements
- [ ] **Performance optimization**
  - Lazy imports to speed up module loading
  - Caching for repeated operations

- [ ] **Extended export formats**
  - APA-style tables
  - R-compatible output

- [ ] **Enhanced visualizations**
  - Interactive plots (plotly)
  - Customizable themes

- [ ] **Batch processing**
  - Apply same test to multiple datasets
  - Parallel computation support

---

## 💡 Ideas for Discussion

- [ ] Auto-test selection based on data properties
- [ ] Integration with pandas DataFrames (native support)
- [ ] Effect size visualization (forest plots, etc.)
- [ ] Sample size calculator web interface
- [ ] Automatic report generation (full analysis pipeline)

---

## 🐛 Known Issues

None currently - all tests working as expected!

---

## 📝 Notes

- Version 2.0.0 represents a complete rewrite with clean architecture
- All legacy code moved to `.old/` directory
- No backward compatibility with version 1.x (by design)
- Focus on quality over quantity - 16 well-implemented tests
- All tests have 7-10 comprehensive examples in `__main__` blocks

---

<!-- EOF -->
