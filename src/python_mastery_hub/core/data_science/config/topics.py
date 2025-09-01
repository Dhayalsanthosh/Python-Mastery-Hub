"""
Topic configuration and metadata for the Data Science module.
"""

from typing import Dict, List, Any

TOPICS_CONFIG: Dict[str, Dict[str, Any]] = {
    "numpy_fundamentals": {
        "name": "NumPy Fundamentals",
        "description": "Essential NumPy operations and mathematical computing",
        "prerequisites": ["python_basics"],
        "difficulty": "intermediate",
        "estimated_time": "2-3 hours",
        "subtopics": [
            "array_creation",
            "indexing_slicing",
            "mathematical_operations",
            "broadcasting",
            "linear_algebra"
        ]
    },
    
    "pandas_basics": {
        "name": "Pandas Data Manipulation",
        "description": "Data manipulation and analysis with Pandas",
        "prerequisites": ["numpy_fundamentals"],
        "difficulty": "intermediate",
        "estimated_time": "3-4 hours",
        "subtopics": [
            "dataframe_creation",
            "indexing_selection",
            "groupby_operations",
            "data_cleaning",
            "time_series"
        ]
    },
    
    "data_visualization": {
        "name": "Data Visualization",
        "description": "Creating effective visualizations with Matplotlib and Seaborn",
        "prerequisites": ["pandas_basics"],
        "difficulty": "intermediate",
        "estimated_time": "2-3 hours",
        "subtopics": [
            "matplotlib_basics",
            "advanced_plots",
            "seaborn_statistical",
            "interactive_concepts"
        ]
    },
    
    "statistical_analysis": {
        "name": "Statistical Analysis",
        "description": "Statistical methods for data analysis and inference",
        "prerequisites": ["pandas_basics"],
        "difficulty": "advanced",
        "estimated_time": "4-5 hours",
        "subtopics": [
            "descriptive_statistics",
            "hypothesis_testing",
            "correlation_analysis",
            "confidence_intervals",
            "normality_testing"
        ]
    },
    
    "machine_learning": {
        "name": "Machine Learning",
        "description": "ML algorithms for prediction and pattern discovery",
        "prerequisites": ["statistical_analysis", "data_preprocessing"],
        "difficulty": "advanced",
        "estimated_time": "5-6 hours",
        "subtopics": [
            "classification",
            "regression",
            "clustering",
            "model_evaluation",
            "hyperparameter_tuning"
        ]
    },
    
    "data_preprocessing": {
        "name": "Data Preprocessing",
        "description": "Preparing data for machine learning algorithms",
        "prerequisites": ["pandas_basics"],
        "difficulty": "intermediate",
        "estimated_time": "3-4 hours",
        "subtopics": [
            "data_cleaning",
            "feature_scaling",
            "encoding",
            "feature_selection",
            "dimensionality_reduction"
        ]
    }
}

def get_topic_order() -> List[str]:
    """Return recommended learning order for topics."""
    return [
        "numpy_fundamentals",
        "pandas_basics",
        "data_visualization",
        "data_preprocessing",
        "statistical_analysis",
        "machine_learning"
    ]

def get_topic_dependencies() -> Dict[str, List[str]]:
    """Return dependency mapping for topics."""
    dependencies = {}
    for topic, config in TOPICS_CONFIG.items():
        dependencies[topic] = config.get("prerequisites", [])
    return dependencies