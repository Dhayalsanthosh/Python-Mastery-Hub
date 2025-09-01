"""
Pandas examples for the Data Science module.
Covers DataFrame operations, data manipulation, and time series analysis.
"""

from typing import Dict, Any


class PandasExamples:
    """Pandas examples and demonstrations."""
    
    @staticmethod
    def get_dataframe_operations() -> Dict[str, Any]:
        """Get Pandas DataFrame operations examples."""
        return {
            "code": '''
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def pandas_basics_demo():
    """Demonstrate basic Pandas operations."""
    print("=== Pandas Basics ===")
    
    # Creating DataFrames
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'City': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney'],
        'Salary': [50000, 60000, 70000, 55000, 65000],
        'Department': ['IT', 'Finance', 'IT', 'HR', 'Finance']
    }
    
    df = pd.DataFrame(data)
    print("Original DataFrame:")
    print(df)
    
    # Basic information
    print(f"\\nDataFrame info:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:\\n{df.dtypes}")
    
    # Basic statistics
    print(f"\\nDescriptive statistics:")
    print(df.describe())
    
    # Indexing and selection
    print(f"\\nIndexing examples:")
    print(f"Names column: {df['Name'].tolist()}")
    print(f"First 3 rows:\\n{df.head(3)}")
    print(f"Age > 30:\\n{df[df['Age'] > 30]}")

def data_manipulation_demo():
    """Demonstrate data manipulation operations."""
    print("\\n=== Data Manipulation ===")
    
    # Create sample dataset
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Product': np.random.choice(['A', 'B', 'C'], 100),
        'Sales': np.random.randint(100, 1000, 100),
        'Profit': np.random.randint(10, 100, 100),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100)
    })
    
    print("Sample data:")
    print(df.head())
    
    # Filtering
    high_sales = df[df['Sales'] > 500]
    print(f"\\nHigh sales (>500): {len(high_sales)} records")
    
    # Sorting
    sorted_df = df.sort_values(['Product', 'Sales'], ascending=[True, False])
    print(f"\\nTop sales by product:")
    print(sorted_df.groupby('Product').first()[['Sales', 'Profit']])
    
    # Adding new columns
    df['Profit_Margin'] = df['Profit'] / df['Sales'] * 100
    df['Month'] = df['Date'].dt.month
    
    print(f"\\nAdded columns:")
    print(df[['Sales', 'Profit', 'Profit_Margin']].head())

def groupby_operations_demo():
    """Demonstrate groupby operations."""
    print("\\n=== GroupBy Operations ===")
    
    # Create employee dataset
    employees = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace'],
        'Department': ['IT', 'Finance', 'IT', 'HR', 'Finance', 'IT', 'HR'],
        'Salary': [70000, 80000, 75000, 65000, 85000, 72000, 68000],
        'Experience': [3, 5, 4, 2, 6, 3, 4],
        'Performance': [8.5, 9.0, 7.8, 8.2, 9.2, 8.0, 8.7]
    })
    
    print("Employee data:")
    print(employees)
    
    # Basic groupby
    dept_stats = employees.groupby('Department').agg({
        'Salary': ['mean', 'min', 'max'],
        'Experience': 'mean',
        'Performance': 'mean'
    })
    
    print(f"\\nDepartment statistics:")
    print(dept_stats)
    
    # Multiple groupby
    exp_performance = employees.groupby(['Department', pd.cut(employees['Experience'], bins=3)])['Salary'].mean()
    print(f"\\nSalary by department and experience level:")
    print(exp_performance)
    
    # Custom aggregation functions
    def salary_range(x):
        return x.max() - x.min()
    
    custom_agg = employees.groupby('Department')['Salary'].agg([
        'count', 'mean', salary_range
    ])
    
    print(f"\\nCustom aggregation:")
    print(custom_agg)

def data_cleaning_demo():
    """Demonstrate data cleaning operations."""
    print("\\n=== Data Cleaning ===")
    
    # Create messy dataset
    messy_data = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5, 6],
        'Name': ['Alice', 'Bob', None, 'Diana', 'Eve', 'Frank'],
        'Age': [25, None, 35, 28, 32, 45],
        'Email': ['alice@email.com', 'bob@email.com', 'charlie@email', 
                 'diana@email.com', None, 'frank@email.com'],
        'Salary': [50000, 60000, 70000, None, 65000, 80000],
        'Join_Date': ['2023-01-01', '2023-02-15', '2023-03-10', 
                     '2023-04-20', '2023-05-05', None]
    })
    
    print("Messy data:")
    print(messy_data)
    
    # Check for missing values
    print(f"\\nMissing values:")
    print(messy_data.isnull().sum())
    
    # Handle missing values
    cleaned_data = messy_data.copy()
    
    # Fill missing names with 'Unknown'
    cleaned_data['Name'].fillna('Unknown', inplace=True)
    
    # Fill missing age with median
    cleaned_data['Age'].fillna(cleaned_data['Age'].median(), inplace=True)
    
    # Drop rows with invalid email
    cleaned_data = cleaned_data[cleaned_data['Email'].str.contains('@.*\\.', na=False)]
    
    # Fill missing salary with department average (simplified)
    cleaned_data['Salary'].fillna(cleaned_data['Salary'].mean(), inplace=True)
    
    # Convert date column
    cleaned_data['Join_Date'] = pd.to_datetime(cleaned_data['Join_Date'])
    
    print(f"\\nCleaned data:")
    print(cleaned_data)
    print(f"\\nRemaining missing values:")
    print(cleaned_data.isnull().sum())

def time_series_demo():
    """Demonstrate time series operations."""
    print("\\n=== Time Series Operations ===")
    
    # Create time series data
    dates = pd.date_range('2023-01-01', periods=365, freq='D')
    np.random.seed(42)
    
    # Simulate stock price with trend and noise
    trend = np.linspace(100, 150, 365)
    noise = np.random.normal(0, 5, 365)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(365) / 365 * 4)  # Quarterly pattern
    
    stock_price = trend + seasonal + noise
    
    ts_df = pd.DataFrame({
        'Date': dates,
        'Price': stock_price,
        'Volume': np.random.randint(1000, 10000, 365)
    })
    
    ts_df.set_index('Date', inplace=True)
    
    print("Time series data (first 10 days):")
    print(ts_df.head(10))
    
    # Resampling
    monthly_avg = ts_df.resample('M').mean()
    print(f"\\nMonthly averages:")
    print(monthly_avg.head())
    
    # Rolling statistics
    ts_df['Price_MA_7'] = ts_df['Price'].rolling(window=7).mean()
    ts_df['Price_MA_30'] = ts_df['Price'].rolling(window=30).mean()
    
    print(f"\\nWith moving averages:")
    print(ts_df[['Price', 'Price_MA_7', 'Price_MA_30']].head(10))
    
    # Time-based filtering
    q1_data = ts_df['2023-01':'2023-03']
    print(f"\\nQ1 2023 data points: {len(q1_data)}")
    
    # Calculate returns
    ts_df['Daily_Return'] = ts_df['Price'].pct_change()
    print(f"\\nDaily returns statistics:")
    print(ts_df['Daily_Return'].describe())

# Run all demonstrations
if __name__ == "__main__":
    pandas_basics_demo()
    data_manipulation_demo()
    groupby_operations_demo()
    data_cleaning_demo()
    time_series_demo()
''',
            "explanation": "Pandas provides powerful data manipulation and analysis tools for structured data"
        }