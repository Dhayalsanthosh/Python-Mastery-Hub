"""
Best practices for each Data Science topic.
"""

from typing import Dict, List

BEST_PRACTICES: Dict[str, List[str]] = {
    "numpy_fundamentals": [
        "Use vectorized operations instead of loops for better performance",
        "Understand broadcasting rules for efficient array operations",
        "Choose appropriate data types to optimize memory usage",
        "Use views vs copies appropriately to avoid unexpected behavior",
        "Leverage NumPy's mathematical functions for complex calculations",
        "Prefer np.allclose() for floating-point comparisons",
        "Use axis parameter in reduction operations for clarity",
        "Understand memory layout (C vs Fortran order) for performance"
    ],
    
    "pandas_basics": [
        "Use vectorized operations over apply() when possible",
        "Set appropriate index for better performance and semantics",
        "Use categorical data types for string columns with limited values",
        "Handle missing data thoughtfully based on context",
        "Use method chaining for readable data transformations",
        "Avoid loops; prefer pandas operations or numpy when needed",
        "Use .loc and .iloc for explicit indexing",
        "Consider memory usage with large datasets (chunking, dtypes)",
        "Use groupby efficiently with appropriate aggregation functions"
    ],
    
    "data_visualization": [
        "Choose appropriate chart types for your data and message",
        "Use clear, descriptive titles, labels, and legends",
        "Consider color accessibility and colorblind-friendly palettes",
        "Avoid chartjunk and unnecessary visual elements",
        "Tell a story with your visualizations",
        "Start y-axis at zero for bar charts to avoid misleading",
        "Use consistent color schemes across related visualizations",
        "Consider your audience when choosing complexity level",
        "Test visualizations on different devices and screen sizes"
    ],
    
    "statistical_analysis": [
        "Check assumptions before applying statistical tests",
        "Use appropriate sample sizes for reliable results",
        "Consider multiple testing corrections when needed",
        "Report effect sizes along with significance tests",
        "Visualize data before and after statistical analysis",
        "Understand the difference between statistical and practical significance",
        "Document your analysis process for reproducibility",
        "Use robust statistics when data doesn't meet assumptions",
        "Consider confidence intervals over just p-values"
    ],
    
    "machine_learning": [
        "Always split data into train/validation/test sets",
        "Cross-validate models to assess generalization",
        "Scale features appropriately for different algorithms",
        "Handle class imbalance in classification problems",
        "Interpret model results and validate assumptions",
        "Start with simple models before trying complex ones",
        "Monitor for data leakage in preprocessing",
        "Use appropriate evaluation metrics for your problem",
        "Document model performance and limitations",
        "Consider ethical implications of your models"
    ],
    
    "data_preprocessing": [
        "Understand your data before applying transformations",
        "Handle missing values based on the mechanism of missingness",
        "Scale features appropriately for your algorithm",
        "Encode categorical variables properly",
        "Select features based on domain knowledge and statistical methods",
        "Avoid data leakage by fitting preprocessors only on training data",
        "Document all preprocessing steps for reproducibility",
        "Consider the impact of outliers on your analysis",
        "Validate preprocessing steps with domain experts",
        "Keep original data unchanged; create processed versions"
    ]
}

def get_best_practices(topic: str) -> List[str]:
    """Get best practices for a specific topic."""
    return BEST_PRACTICES.get(topic, [])

def get_all_best_practices() -> Dict[str, List[str]]:
    """Get all available best practices."""
    return BEST_PRACTICES.copy()

def search_best_practices(keyword: str) -> Dict[str, List[str]]:
    """Search for best practices containing a keyword."""
    results = {}
    keyword_lower = keyword.lower()
    
    for topic, practices in BEST_PRACTICES.items():
        matching_practices = [
            practice for practice in practices 
            if keyword_lower in practice.lower()
        ]
        if matching_practices:
            results[topic] = matching_practices
    
    return results