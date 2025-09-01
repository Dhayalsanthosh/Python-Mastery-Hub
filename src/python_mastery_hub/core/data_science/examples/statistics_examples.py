"""
Statistical analysis examples for the Data Science module.
Covers descriptive statistics, hypothesis testing, and correlation analysis.
"""

from typing import Dict, Any


class StatisticsExamples:
    """Statistical analysis examples and demonstrations."""
    
"""
Statistical analysis examples for the Data Science module.
Covers descriptive statistics, hypothesis testing, and correlation analysis.
"""

from typing import Dict, Any


class StatisticsExamples:
    """Statistical analysis examples and demonstrations."""
    
    @staticmethod
    def get_descriptive_statistics() -> Dict[str, Any]:
        """Get descriptive statistics examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

def descriptive_statistics_demo():
    """Demonstrate descriptive statistics."""
    print("=== Descriptive Statistics ===")
    
    # Generate sample data
    np.random.seed(42)
    data = np.random.normal(50, 15, 1000)  # Normal distribution
    skewed_data = np.random.exponential(2, 1000)  # Exponential distribution
    
    def analyze_distribution(data, name):
        print(f"\\n{name} Analysis:")
        print(f"Mean: {np.mean(data):.4f}")
        print(f"Median: {np.median(data):.4f}")
        print(f"Mode: {stats.mode(data)[0]:.4f}")
        print(f"Standard Deviation: {np.std(data, ddof=1):.4f}")
        print(f"Variance: {np.var(data, ddof=1):.4f}")
        print(f"Skewness: {stats.skew(data):.4f}")
        print(f"Kurtosis: {stats.kurtosis(data):.4f}")
        
        # Quartiles and IQR
        q1, q2, q3 = np.percentile(data, [25, 50, 75])
        iqr = q3 - q1
        print(f"Q1: {q1:.4f}, Q2: {q2:.4f}, Q3: {q3:.4f}")
        print(f"IQR: {iqr:.4f}")
        
        # Range
        print(f"Range: {np.max(data) - np.min(data):.4f}")
        
        return q1, q3, iqr
    
    # Analyze both distributions
    q1_norm, q3_norm, iqr_norm = analyze_distribution(data, "Normal Distribution")
    q1_exp, q3_exp, iqr_exp = analyze_distribution(skewed_data, "Exponential Distribution")
    
    # Outlier detection using IQR method
    def detect_outliers_iqr(data, q1, q3, iqr):
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        return outliers, lower_bound, upper_bound
    
    outliers_norm, lb_norm, ub_norm = detect_outliers_iqr(data, q1_norm, q3_norm, iqr_norm)
    outliers_exp, lb_exp, ub_exp = detect_outliers_iqr(skewed_data, q1_exp, q3_exp, iqr_exp)
    
    print(f"\\nOutlier Detection (IQR method):")
    print(f"Normal data outliers: {len(outliers_norm)} ({len(outliers_norm)/len(data)*100:.1f}%)")
    print(f"Exponential data outliers: {len(outliers_exp)} ({len(outliers_exp)/len(skewed_data)*100:.1f}%)")

# Run demonstration
if __name__ == "__main__":
    descriptive_statistics_demo()
''',
            "explanation": "Descriptive statistics provide essential summaries of data distributions and characteristics"
        }
    
    @staticmethod
    def get_hypothesis_testing() -> Dict[str, Any]:
        """Get hypothesis testing examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
import scipy.stats as stats

def hypothesis_testing_demo():
    """Demonstrate hypothesis testing."""
    print("=== Hypothesis Testing ===")
    
    np.random.seed(42)
    
    # One-sample t-test
    print("\\n1. One-sample t-test:")
    sample = np.random.normal(105, 15, 30)  # Sample with mean 105
    null_hypothesis_mean = 100
    
    t_stat, p_value = stats.ttest_1samp(sample, null_hypothesis_mean)
    print(f"Sample mean: {np.mean(sample):.4f}")
    print(f"Null hypothesis mean: {null_hypothesis_mean}")
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Reject null hypothesis (α=0.05): {p_value < 0.05}")
    
    # Two-sample t-test
    print("\\n2. Two-sample t-test:")
    group1 = np.random.normal(100, 15, 50)
    group2 = np.random.normal(105, 15, 50)
    
    t_stat, p_value = stats.ttest_ind(group1, group2)
    print(f"Group 1 mean: {np.mean(group1):.4f}")
    print(f"Group 2 mean: {np.mean(group2):.4f}")
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Significant difference (α=0.05): {p_value < 0.05}")
    
    # Chi-square test
    print("\\n3. Chi-square test:")
    # Create contingency table
    observed = np.array([[20, 15, 10],
                        [15, 25, 20],
                        [10, 20, 25]])
    
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed)
    print(f"Chi-square statistic: {chi2_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Degrees of freedom: {dof}")
    print(f"Reject independence hypothesis (α=0.05): {p_value < 0.05}")
    
    # ANOVA test
    print("\\n4. One-way ANOVA:")
    group_a = np.random.normal(100, 10, 30)
    group_b = np.random.normal(105, 10, 30)
    group_c = np.random.normal(110, 10, 30)
    
    f_stat, p_value = stats.f_oneway(group_a, group_b, group_c)
    print(f"Group A mean: {np.mean(group_a):.4f}")
    print(f"Group B mean: {np.mean(group_b):.4f}")
    print(f"Group C mean: {np.mean(group_c):.4f}")
    print(f"F-statistic: {f_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Significant group differences (α=0.05): {p_value < 0.05}")

# Run demonstration
if __name__ == "__main__":
    hypothesis_testing_demo()
''',
            "explanation": "Hypothesis testing provides methods for making statistical inferences about populations"
        }
    
    @staticmethod
    def get_correlation_analysis() -> Dict[str, Any]:
        """Get correlation analysis examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
import scipy.stats as stats

def correlation_analysis_demo():
    """Demonstrate correlation analysis."""
    print("=== Correlation Analysis ===")
    
    np.random.seed(42)
    n = 100
    
    # Generate correlated data
    x = np.random.randn(n)
    y_strong = 2 * x + np.random.randn(n) * 0.5  # Strong positive correlation
    y_weak = 0.3 * x + np.random.randn(n)        # Weak positive correlation
    y_negative = -1.5 * x + np.random.randn(n) * 0.5  # Strong negative correlation
    y_nonlinear = x**2 + np.random.randn(n) * 0.5     # Nonlinear relationship
    
    def analyze_correlation(x, y, name):
        # Pearson correlation
        pearson_r, pearson_p = stats.pearsonr(x, y)
        
        # Spearman correlation
        spearman_r, spearman_p = stats.spearmanr(x, y)
        
        # Kendall's tau
        kendall_tau, kendall_p = stats.kendalltau(x, y)
        
        print(f"\\n{name}:")
        print(f"Pearson correlation: r = {pearson_r:.4f}, p = {pearson_p:.4f}")
        print(f"Spearman correlation: ρ = {spearman_r:.4f}, p = {spearman_p:.4f}")
        print(f"Kendall's tau: τ = {kendall_tau:.4f}, p = {kendall_p:.4f}")
        
        # Effect size interpretation for Pearson
        if abs(pearson_r) < 0.1:
            effect_size = "negligible"
        elif abs(pearson_r) < 0.3:
            effect_size = "small"
        elif abs(pearson_r) < 0.5:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        print(f"Effect size: {effect_size}")
    
    analyze_correlation(x, y_strong, "Strong Positive Correlation")
    analyze_correlation(x, y_weak, "Weak Positive Correlation")
    analyze_correlation(x, y_negative, "Strong Negative Correlation")
    analyze_correlation(x, y_nonlinear, "Nonlinear Relationship")

# Run demonstration
if __name__ == "__main__":
    correlation_analysis_demo()
''',
            "explanation": "Correlation analysis measures the strength and direction of relationships between variables"
        }
    
    @staticmethod
    def get_confidence_intervals() -> Dict[str, Any]:
        """Get confidence intervals examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
import scipy.stats as stats

def confidence_intervals_demo():
    """Demonstrate confidence intervals."""
    print("=== Confidence Intervals ===")
    
    np.random.seed(42)
    
    # Sample data
    sample = np.random.normal(50, 10, 100)
    sample_mean = np.mean(sample)
    sample_std = np.std(sample, ddof=1)
    n = len(sample)
    
    # Confidence intervals for mean
    confidence_levels = [0.90, 0.95, 0.99]
    
    print(f"Sample statistics:")
    print(f"Mean: {sample_mean:.4f}")
    print(f"Standard deviation: {sample_std:.4f}")
    print(f"Sample size: {n}")
    
    for conf_level in confidence_levels:
        alpha = 1 - conf_level
        
        # T-distribution (unknown population variance)
        t_critical = stats.t.ppf(1 - alpha/2, df=n-1)
        margin_error = t_critical * (sample_std / np.sqrt(n))
        
        lower_bound = sample_mean - margin_error
        upper_bound = sample_mean + margin_error
        
        print(f"\\n{conf_level*100:.0f}% Confidence Interval:")
        print(f"[{lower_bound:.4f}, {upper_bound:.4f}]")
        print(f"Margin of error: ±{margin_error:.4f}")
    
    # Bootstrap confidence interval
    print(f"\\nBootstrap 95% Confidence Interval:")
    n_bootstrap = 10000
    bootstrap_means = []
    
    for _ in range(n_bootstrap):
        bootstrap_sample = np.random.choice(sample, size=n, replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))
    
    bootstrap_means = np.array(bootstrap_means)
    bootstrap_lower = np.percentile(bootstrap_means, 2.5)
    bootstrap_upper = np.percentile(bootstrap_means, 97.5)
    
    print(f"[{bootstrap_lower:.4f}, {bootstrap_upper:.4f}]")

# Run demonstration
if __name__ == "__main__":
    confidence_intervals_demo()
''',
            "explanation": "Confidence intervals provide ranges of plausible values for population parameters"
        }
    
    @staticmethod
    def get_normality_testing() -> Dict[str, Any]:
        """Get normality testing examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
import scipy.stats as stats

def normality_testing_demo():
    """Demonstrate normality testing."""
    print("=== Normality Testing ===")
    
    np.random.seed(42)
    
    # Generate different distributions
    normal_data = np.random.normal(0, 1, 1000)
    uniform_data = np.random.uniform(-2, 2, 1000)
    exponential_data = np.random.exponential(1, 1000)
    
    datasets = [
        (normal_data, "Normal Distribution"),
        (uniform_data, "Uniform Distribution"),
        (exponential_data, "Exponential Distribution")
    ]
    
    def test_normality(data, name):
        print(f"\\n{name}:")
        
        # Shapiro-Wilk test (best for small samples)
        if len(data) <= 5000:
            shapiro_stat, shapiro_p = stats.shapiro(data)
            print(f"Shapiro-Wilk: W = {shapiro_stat:.4f}, p = {shapiro_p:.4f}")
        
        # D'Agostino and Pearson's test
        dagostino_stat, dagostino_p = stats.normaltest(data)
        print(f"D'Agostino: χ² = {dagostino_stat:.4f}, p = {dagostino_p:.4f}")
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data)))
        print(f"Kolmogorov-Smirnov: D = {ks_stat:.4f}, p = {ks_p:.4f}")
        
        # Anderson-Darling test
        ad_stat, ad_critical, ad_significance = stats.anderson(data, dist='norm')
        print(f"Anderson-Darling: A² = {ad_stat:.4f}")
        
        # Interpretation
        alpha = 0.05
        tests_passed = 0
        total_tests = 0
        
        if len(data) <= 5000:
            tests_passed += int(shapiro_p > alpha)
            total_tests += 1
        
        tests_passed += int(dagostino_p > alpha)
        tests_passed += int(ks_p > alpha)
        total_tests += 2
        
        # Anderson-Darling interpretation
        ad_critical_05 = ad_critical[2]  # 5% significance level
        tests_passed += int(ad_stat < ad_critical_05)
        total_tests += 1
        
        print(f"Tests supporting normality: {tests_passed}/{total_tests}")
        
        if tests_passed >= total_tests * 0.5:
            print("Conclusion: Data appears to be normally distributed")
        else:
            print("Conclusion: Data does not appear to be normally distributed")
    
    for data, name in datasets:
        test_normality(data, name)

# Run demonstration
if __name__ == "__main__":
    normality_testing_demo()
''',
            "explanation": "Normality testing determines whether data follows a normal distribution"
        }