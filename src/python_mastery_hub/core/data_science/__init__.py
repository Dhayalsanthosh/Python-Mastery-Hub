"""
Data Science Learning Module.

Comprehensive coverage of data science with Python including NumPy, Pandas,
Matplotlib, Seaborn, Scikit-learn, and statistical analysis.
"""

from typing import Dict, List, Any
from python_mastery_hub.core import LearningModule

# Import example modules
from .examples.numpy_examples import NumpyExamples
from .examples.pandas_examples import PandasExamples
from .examples.visualization_examples import VisualizationExamples
from .examples.statistics_examples import StatisticsExamples
from .examples.ml_examples import MLExamples
from .examples.preprocessing_examples import PreprocessingExamples

# Import exercise modules
from .exercises.data_analysis import DataAnalysisExercise
from .exercises.ml_pipeline import MLPipelineExercise
from .exercises.dashboard import DashboardExercise

# Import utilities
from .utils.explanations import EXPLANATIONS
from .utils.best_practices import BEST_PRACTICES
from .config.topics import TOPICS_CONFIG


class DataScience(LearningModule):
    """Interactive learning module for Data Science with Python."""
    
    def __init__(self):
        super().__init__(
            name="Data Science",
            description="Master data science with NumPy, Pandas, visualization, and machine learning",
            difficulty="intermediate"
        )
        self._setup_module()
    
    def _setup_module(self) -> None:
        """Setup examples and exercises for data science."""
        self.examples = {
            "numpy_fundamentals": {
                "array_operations": NumpyExamples.get_array_operations(),
                "linear_algebra": NumpyExamples.get_linear_algebra(),
            },
            "pandas_basics": {
                "dataframe_operations": PandasExamples.get_dataframe_operations(),
            },
            "data_visualization": {
                "matplotlib_basics": VisualizationExamples.get_matplotlib_basics(),
            },
            "statistical_analysis": {
                "descriptive_statistics": StatisticsExamples.get_descriptive_statistics(),
                "hypothesis_testing": StatisticsExamples.get_hypothesis_testing(),
                "correlation_analysis": StatisticsExamples.get_correlation_analysis(),
                "confidence_intervals": StatisticsExamples.get_confidence_intervals(),
                "normality_testing": StatisticsExamples.get_normality_testing(),
            },
            "machine_learning": {
                "classification_models": MLExamples.get_classification_models(),
            },
            "data_preprocessing": {
                "data_preprocessing": PreprocessingExamples.get_data_preprocessing(),
            },
        }
        
        self.exercises = [
            {
                "topic": "pandas_basics",
                "title": "Data Analysis Pipeline",
                "description": "Build a complete data analysis pipeline with real datasets",
                "difficulty": "hard",
                "function": DataAnalysisExercise.get_exercise
            },
            {
                "topic": "machine_learning",
                "title": "Predictive Model Development",
                "description": "Create and evaluate machine learning models",
                "difficulty": "hard",
                "function": MLPipelineExercise.get_exercise
            },
            {
                "topic": "data_visualization",
                "title": "Interactive Dashboard",
                "description": "Build an interactive data visualization dashboard",
                "difficulty": "hard",
                "function": DashboardExercise.get_exercise
            }
        ]
    
    def get_topics(self) -> List[str]:
        """Return list of topics covered in this module."""
        return list(TOPICS_CONFIG.keys())
    
    def demonstrate(self, topic: str) -> Dict[str, Any]:
        """Demonstrate a specific topic with examples."""
        if topic not in self.examples:
            raise ValueError(f"Topic '{topic}' not found in data science module")
        
        return {
            "topic": topic,
            "examples": self.examples[topic],
            "explanation": EXPLANATIONS.get(topic, "No explanation available"),
            "best_practices": BEST_PRACTICES.get(topic, []),
        }


# Make the module importable
__all__ = ["DataScience"]