"""
Topic explanations for the Data Science module.
"""

from typing import Dict

EXPLANATIONS: Dict[str, str] = {
    "numpy_fundamentals": """
NumPy (Numerical Python) is the fundamental package for scientific computing in Python. 
It provides a powerful N-dimensional array object and tools for working with these arrays.
NumPy arrays are more efficient than Python lists for numerical operations due to:
- Homogeneous data types (all elements same type)
- Contiguous memory layout
- Vectorized operations implemented in C
- Broadcasting capabilities for operations on arrays of different shapes
Key concepts include array creation, indexing, mathematical operations, and linear algebra.
""",

    "pandas_basics": """
Pandas is a powerful data manipulation and analysis library built on top of NumPy.
It provides two main data structures: Series (1D) and DataFrame (2D).
Key features include:
- Handling missing data gracefully
- Automatic data alignment
- Powerful group-by functionality
- Time series analysis capabilities
- Flexible data import/export (CSV, Excel, SQL, JSON, etc.)
- Data cleaning and transformation tools
Essential operations include filtering, grouping, merging, and time-based analysis.
""",

    "data_visualization": """
Data visualization is crucial for understanding patterns, trends, and insights in data.
Python offers several powerful libraries:
- Matplotlib: Low-level, flexible plotting library (foundation for others)
- Seaborn: Statistical visualization built on matplotlib with better defaults
- Plotly: Interactive visualizations for web deployment
Key principles include choosing appropriate chart types, using color effectively,
avoiding chart junk, and telling a clear story with your visualizations.
Understanding when to use different plot types is essential for effective communication.
""",

    "statistical_analysis": """
Statistical analysis provides methods for understanding data patterns and making inferences.
Key areas include:
- Descriptive statistics: Summarizing and describing data characteristics
- Inferential statistics: Making conclusions about populations from samples
- Hypothesis testing: Testing claims or theories about data
- Correlation analysis: Understanding relationships between variables
- Confidence intervals: Estimating population parameters with uncertainty
Proper statistical analysis requires understanding assumptions, choosing appropriate tests,
and interpreting results in context.
""",

    "machine_learning": """
Machine learning enables computers to learn patterns from data without explicit programming.
Main categories include:
- Supervised learning: Learning from labeled examples (classification, regression)
- Unsupervised learning: Finding patterns in unlabeled data (clustering, dimensionality reduction)
- Reinforcement learning: Learning through interaction and feedback
Key concepts include model selection, overfitting/underfitting, cross-validation,
hyperparameter tuning, and evaluation metrics. Success requires understanding
both the algorithms and the problem domain.
""",

    "data_preprocessing": """
Data preprocessing is the crucial step of preparing raw data for analysis and modeling.
Real-world data is often messy and requires cleaning:
- Handling missing values (imputation strategies)
- Detecting and treating outliers
- Feature scaling and normalization
- Encoding categorical variables
- Feature selection and dimensionality reduction
Quality preprocessing often determines model success more than algorithm choice.
Understanding your data and choosing appropriate preprocessing steps is essential
for building robust machine learning pipelines.
"""
}

def get_explanation(topic: str) -> str:
    """Get explanation for a specific topic."""
    return EXPLANATIONS.get(topic, "No explanation available for this topic.")

def get_all_explanations() -> Dict[str, str]:
    """Get all available explanations."""
    return EXPLANATIONS.copy()