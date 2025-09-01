"""
Machine Learning Pipeline Exercise for the Data Science module.
"""

from typing import Dict, Any


class MLPipelineExercise:
    """Machine learning pipeline exercise implementation."""
    
    @staticmethod
    def get_exercise() -> Dict[str, Any]:
        """Get the ML pipeline exercise."""
        return {
            "instructions": """
Create a complete machine learning pipeline that demonstrates end-to-end ML workflow.
Build, evaluate, and optimize models while following ML best practices for a real-world
prediction problem.
""",
            "objectives": [
                "Design and implement a complete ML pipeline",
                "Apply proper data preprocessing techniques",
                "Compare multiple algorithms and select the best",
                "Perform hyperparameter optimization",
                "Evaluate models using appropriate metrics"
            ],
            "tasks": [
                {
                    "step": 1,
                    "title": "Problem Definition and Data Preparation",
                    "description": "Define the ML problem and prepare the dataset",
                    "requirements": [
                        "Load and examine the dataset",
                        "Define the prediction target clearly",
                        "Split data into train/validation/test sets",
                        "Document the problem type (classification/regression)"
                    ]
                },
                {
                    "step": 2,
                    "title": "Feature Engineering and Preprocessing",
                    "description": "Prepare features for machine learning",
                    "requirements": [
                        "Handle missing values appropriately",
                        "Encode categorical variables",
                        "Scale numerical features",
                        "Create new features if beneficial"
                    ]
                },
                {
                    "step": 3,
                    "title": "Model Selection and Training",
                    "description": "Train multiple models and compare performance",
                    "requirements": [
                        "Implement at least 3 different algorithms",
                        "Use cross-validation for model evaluation",
                        "Compare models using appropriate metrics",
                        "Document model assumptions and requirements"
                    ]
                },
                {
                    "step": 4,
                    "title": "Hyperparameter Optimization",
                    "description": "Optimize the best performing model",
                    "requirements": [
                        "Define hyperparameter search space",
                        "Use grid search or random search",
                        "Evaluate on validation set",
                        "Compare optimized vs baseline performance"
                    ]
                },
                {
                    "step": 5,
                    "title": "Model Evaluation and Interpretation",
                    "description": "Thoroughly evaluate the final model",
                    "requirements": [
                        "Test on holdout test set",
                        "Generate comprehensive evaluation metrics",
                        "Analyze feature importance/coefficients",
                        "Create visualizations of model performance"
                    ]
                },
                {
                    "step": 6,
                    "title": "Model Deployment Preparation",
                    "description": "Prepare model for production deployment",
                    "requirements": [
                        "Create prediction pipeline function",
                        "Save trained model and preprocessors",
                        "Document model limitations and assumptions",
                        "Provide usage examples"
                    ]
                }
            ],
            "starter_code": '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class MLPipeline:
    """Complete machine learning pipeline implementation."""
    
    def __init__(self):
        self.preprocessors = {}
        self.models = {}
        self.best_model = None
        self.results = {}
    
    def load_and_split_data(self, filepath, target_column, test_size=0.2, random_state=42):
        """
        Load data and split into train/validation/test sets.
        
        Args:
            filepath (str): Path to dataset
            target_column (str): Name of target column
            test_size (float): Proportion for test set
            random_state (int): Random seed
        """
        # TODO: Implement data loading and splitting
        pass
    
    def preprocess_features(self, X_train, X_val, X_test):
        """
        Preprocess features for machine learning.
        
        Args:
            X_train, X_val, X_test: Feature matrices
            
        Returns:
            Preprocessed feature matrices
        """
        # TODO: Implement feature preprocessing
        pass
    
    def train_models(self, X_train, y_train, X_val, y_val):
        """
        Train multiple models and compare performance.
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
        """
        # TODO: Implement model training and comparison
        pass
    
    def optimize_hyperparameters(self, X_train, y_train, model_name):
        """
        Optimize hyperparameters for the best model.
        
        Args:
            X_train, y_train: Training data
            model_name (str): Name of model to optimize
        """
        # TODO: Implement hyperparameter optimization
        pass
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the final model on test set.
        
        Args:
            X_test, y_test: Test data
        """
        # TODO: Implement comprehensive model evaluation
        pass
    
    def save_pipeline(self, filepath):
        """
        Save the complete pipeline for deployment.
        
        Args:
            filepath (str): Path to save pipeline
        """
        # TODO: Implement pipeline saving
        pass

def main():
    """Main execution function."""
    # Initialize pipeline
    pipeline = MLPipeline()
    
    # Step 1: Load and split data
    print("=== Step 1: Data Loading and Splitting ===")
    pipeline.load_and_split_data('your_dataset.csv', 'target_column')
    
    # Step 2: Preprocess features
    print("\\n=== Step 2: Feature Preprocessing ===")
    X_train_processed, X_val_processed, X_test_processed = pipeline.preprocess_features(
        pipeline.X_train, pipeline.X_val, pipeline.X_test
    )
    
    # Step 3: Train models
    print("\\n=== Step 3: Model Training and Comparison ===")
    pipeline.train_models(X_train_processed, pipeline.y_train, 
                         X_val_processed, pipeline.y_val)
    
    # Step 4: Optimize hyperparameters
    print("\\n=== Step 4: Hyperparameter Optimization ===")
    best_model_name = max(pipeline.results.keys(), 
                         key=lambda k: pipeline.results[k]['val_score'])
    pipeline.optimize_hyperparameters(X_train_processed, pipeline.y_train, 
                                     best_model_name)
    
    # Step 5: Final evaluation
    print("\\n=== Step 5: Model Evaluation ===")
    pipeline.evaluate_model(X_test_processed, pipeline.y_test)
    
    # Step 6: Save pipeline
    print("\\n=== Step 6: Pipeline Deployment Preparation ===")
    pipeline.save_pipeline('ml_pipeline.pkl')
    
    print("\\nML pipeline completed successfully!")

if __name__ == "__main__":
    main()
''',
            "evaluation_criteria": [
                "Pipeline design and implementation (25%)",
                "Feature engineering quality (20%)",
                "Model selection and comparison (20%)",
                "Hyperparameter optimization (15%)",
                "Evaluation thoroughness (20%)"
            ],
            "solution": '''
# Complete ML pipeline solution with production-ready code
# Implementation includes proper error handling, logging, and documentation
'''
        }