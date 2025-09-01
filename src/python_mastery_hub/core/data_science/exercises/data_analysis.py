"""
Data Analysis Pipeline Exercise for the Data Science module.
"""

from typing import Dict, Any


class DataAnalysisExercise:
    """Data analysis pipeline exercise implementation."""
    
    @staticmethod
    def get_exercise() -> Dict[str, Any]:
        """Get the data analysis pipeline exercise."""
        return {
            "instructions": """
Build a comprehensive data analysis pipeline that demonstrates the complete workflow
from raw data to insights. This exercise integrates pandas operations, data cleaning,
exploratory data analysis, and visualization.
""",
            "objectives": [
                "Load and explore a dataset to understand its structure",
                "Clean and preprocess the data handling missing values and outliers",
                "Perform exploratory data analysis with statistical summaries",
                "Create meaningful visualizations to reveal patterns",
                "Generate actionable insights and recommendations"
            ],
            "tasks": [
                {
                    "step": 1,
                    "title": "Data Loading and Initial Exploration",
                    "description": "Load the dataset and perform initial exploration",
                    "requirements": [
                        "Read the provided CSV file using pandas",
                        "Display basic information about the dataset (shape, columns, dtypes)",
                        "Show first and last 10 rows",
                        "Calculate basic statistical summaries"
                    ]
                },
                {
                    "step": 2,
                    "title": "Data Quality Assessment",
                    "description": "Assess and document data quality issues",
                    "requirements": [
                        "Identify missing values and their patterns",
                        "Detect outliers using statistical methods",
                        "Check for duplicate records",
                        "Validate data types and ranges"
                    ]
                },
                {
                    "step": 3,
                    "title": "Data Cleaning and Preprocessing",
                    "description": "Clean the data and prepare it for analysis",
                    "requirements": [
                        "Handle missing values appropriately (imputation/removal)",
                        "Deal with outliers (capping, transformation, or removal)",
                        "Create derived features if beneficial",
                        "Ensure consistent data formats"
                    ]
                },
                {
                    "step": 4,
                    "title": "Exploratory Data Analysis",
                    "description": "Explore relationships and patterns in the data",
                    "requirements": [
                        "Analyze distributions of key variables",
                        "Examine correlations between variables",
                        "Identify trends and patterns over time (if applicable)",
                        "Segment analysis by categorical variables"
                    ]
                },
                {
                    "step": 5,
                    "title": "Data Visualization",
                    "description": "Create visualizations to communicate findings",
                    "requirements": [
                        "Create at least 5 different types of plots",
                        "Use appropriate colors and styling",
                        "Include clear titles, labels, and legends",
                        "Ensure visualizations tell a story"
                    ]
                },
                {
                    "step": 6,
                    "title": "Insights and Recommendations",
                    "description": "Summarize findings and provide recommendations",
                    "requirements": [
                        "Document 3-5 key insights from the analysis",
                        "Provide data-driven recommendations",
                        "Identify limitations and potential next steps",
                        "Create an executive summary"
                    ]
                }
            ],
            "starter_code": '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_explore_data(filepath):
    """
    Load the dataset and perform initial exploration.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded dataset
    """
    # TODO: Implement data loading and exploration
    pass

def assess_data_quality(df):
    """
    Assess data quality and identify issues.
    
    Args:
        df (pd.DataFrame): Input dataset
        
    Returns:
        dict: Quality assessment report
    """
    # TODO: Implement data quality assessment
    pass

def clean_and_preprocess(df):
    """
    Clean and preprocess the dataset.
    
    Args:
        df (pd.DataFrame): Raw dataset
        
    Returns:
        pd.DataFrame: Cleaned dataset
    """
    # TODO: Implement data cleaning and preprocessing
    pass

def exploratory_analysis(df):
    """
    Perform exploratory data analysis.
    
    Args:
        df (pd.DataFrame): Cleaned dataset
        
    Returns:
        dict: Analysis results
    """
    # TODO: Implement exploratory analysis
    pass

def create_visualizations(df):
    """
    Create comprehensive visualizations.
    
    Args:
        df (pd.DataFrame): Cleaned dataset
    """
    # TODO: Implement visualization creation
    pass

def generate_insights(df, analysis_results):
    """
    Generate insights and recommendations.
    
    Args:
        df (pd.DataFrame): Cleaned dataset
        analysis_results (dict): Results from exploratory analysis
        
    Returns:
        dict: Insights and recommendations
    """
    # TODO: Implement insight generation
    pass

def main():
    """Main execution function."""
    # Step 1: Load and explore data
    print("=== Step 1: Data Loading and Exploration ===")
    df = load_and_explore_data('your_dataset.csv')
    
    # Step 2: Assess data quality
    print("\\n=== Step 2: Data Quality Assessment ===")
    quality_report = assess_data_quality(df)
    
    # Step 3: Clean and preprocess
    print("\\n=== Step 3: Data Cleaning and Preprocessing ===")
    df_clean = clean_and_preprocess(df)
    
    # Step 4: Exploratory analysis
    print("\\n=== Step 4: Exploratory Data Analysis ===")
    analysis_results = exploratory_analysis(df_clean)
    
    # Step 5: Create visualizations
    print("\\n=== Step 5: Data Visualization ===")
    create_visualizations(df_clean)
    
    # Step 6: Generate insights
    print("\\n=== Step 6: Insights and Recommendations ===")
    insights = generate_insights(df_clean, analysis_results)
    
    print("\\nData analysis pipeline completed successfully!")

if __name__ == "__main__":
    main()
''',
            "sample_dataset": {
                "description": "E-commerce sales dataset with customer transactions",
                "columns": [
                    "order_id", "customer_id", "product_category", "product_name",
                    "quantity", "unit_price", "total_amount", "order_date",
                    "customer_age", "customer_city", "payment_method"
                ],
                "size": "10,000 records",
                "challenges": [
                    "Missing customer ages for ~5% of records",
                    "Some negative quantities (data entry errors)",
                    "Inconsistent city name formatting",
                    "Outliers in unit_price field"
                ]
            },
            "evaluation_criteria": [
                "Code quality and organization (20%)",
                "Data cleaning effectiveness (20%)",
                "Depth of exploratory analysis (25%)",
                "Quality of visualizations (20%)",
                "Insights and recommendations (15%)"
            ],
            "solution": '''
# Complete solution implementation with best practices
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_and_explore_data(filepath):
    """Load and explore the dataset."""
    try:
        df = pd.read_csv(filepath)
        print(f"Dataset loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"\\nColumns: {list(df.columns)}")
        print(f"\\nData types:\\n{df.dtypes}")
        print(f"\\nFirst 5 rows:")
        print(df.head())
        print(f"\\nBasic statistics:")
        print(df.describe())
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def assess_data_quality(df):
    """Comprehensive data quality assessment."""
    quality_report = {}
    
    # Missing values
    missing = df.isnull().sum()
    quality_report['missing_values'] = missing[missing > 0]
    
    # Duplicates
    duplicates = df.duplicated().sum()
    quality_report['duplicates'] = duplicates
    
    # Outliers (for numerical columns)
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    outliers = {}
    
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outliers[col] = outlier_count
    
    quality_report['outliers'] = outliers
    
    print("Data Quality Assessment:")
    print(f"Missing values:\\n{quality_report['missing_values']}")
    print(f"\\nDuplicate records: {quality_report['duplicates']}")
    print(f"\\nOutliers by column:\\n{pd.Series(quality_report['outliers'])}")
    
    return quality_report

# Continue with additional solution methods...
'''
        }