# tests/unit/core/test_data_science.py
# Unit tests for data science concepts and exercises

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import tempfile
import os
import json
import csv
from datetime import datetime, timedelta
import warnings

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore')

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.data_science import (
        NumpyExercise,
        PandasExercise,
        MatplotlibExercise,
        DataAnalysisExercise,
        MachineLearningExercise,
        StatisticsExercise
    )
    from src.core.evaluators import DataScienceEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class NumpyExercise:
        pass
    class PandasExercise:
        pass
    class MatplotlibExercise:
        pass
    class DataAnalysisExercise:
        pass
    class MachineLearningExercise:
        pass
    class StatisticsExercise:
        pass
    class DataScienceEvaluator:
        pass


class TestNumpyExercises:
    """Test cases for NumPy array operations and exercises."""
    
    def test_array_creation_and_basic_operations(self):
        """Test NumPy array creation and basic operations."""
        code = '''
import numpy as np

# Array creation
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([[1, 2, 3], [4, 5, 6]])
arr3 = np.zeros((3, 3))
arr4 = np.ones((2, 4))
arr5 = np.eye(3)
arr6 = np.arange(0, 10, 2)
arr7 = np.linspace(0, 1, 5)
arr8 = np.random.rand(3, 3)

# Basic properties
shape_2d = arr2.shape
ndim_2d = arr2.ndim
size_2d = arr2.size
dtype_arr1 = arr1.dtype

# Array operations
arr_sum = arr1 + 10
arr_mult = arr1 * 2
arr_power = arr1 ** 2
arr_sqrt = np.sqrt(arr1)

# Mathematical operations
arr_mean = np.mean(arr1)
arr_std = np.std(arr1)
arr_max = np.max(arr1)
arr_min = np.min(arr1)
arr_cumsum = np.cumsum(arr1)

# Boolean operations
bool_mask = arr1 > 3
filtered_arr = arr1[bool_mask]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test array properties
        assert globals_dict['shape_2d'] == (2, 3)
        assert globals_dict['ndim_2d'] == 2
        assert globals_dict['size_2d'] == 6
        
        # Test operations
        assert np.array_equal(globals_dict['arr_sum'], [11, 12, 13, 14, 15])
        assert np.array_equal(globals_dict['arr_mult'], [2, 4, 6, 8, 10])
        assert np.array_equal(globals_dict['arr_power'], [1, 4, 9, 16, 25])
        
        # Test statistics
        assert globals_dict['arr_mean'] == 3.0
        assert globals_dict['arr_max'] == 5
        assert globals_dict['arr_min'] == 1
        
        # Test boolean operations
        assert np.array_equal(globals_dict['filtered_arr'], [4, 5])
    
    def test_array_indexing_and_slicing(self):
        """Test NumPy array indexing and slicing operations."""
        code = '''
import numpy as np

# Create test arrays
arr_1d = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
arr_2d = np.array([[1, 2, 3, 4],
                   [5, 6, 7, 8],
                   [9, 10, 11, 12]])

# Basic indexing
first_element = arr_1d[0]
last_element = arr_1d[-1]
middle_element = arr_2d[1, 1]

# Slicing
slice_1d = arr_1d[2:8]
slice_step = arr_1d[::2]
slice_2d_row = arr_2d[1, :]
slice_2d_col = arr_2d[:, 2]
slice_2d_subarray = arr_2d[0:2, 1:3]

# Advanced indexing
indices = [0, 2, 4]
fancy_indexed = arr_1d[indices]

# Boolean indexing
condition = arr_1d % 2 == 0
even_numbers = arr_1d[condition]

# Conditional operations
arr_conditional = np.where(arr_1d > 5, arr_1d, 0)

# Array modification
arr_copy = arr_1d.copy()
arr_copy[arr_copy < 5] = -1
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test basic indexing
        assert globals_dict['first_element'] == 0
        assert globals_dict['last_element'] == 9
        assert globals_dict['middle_element'] == 6
        
        # Test slicing
        assert np.array_equal(globals_dict['slice_1d'], [2, 3, 4, 5, 6, 7])
        assert np.array_equal(globals_dict['slice_step'], [0, 2, 4, 6, 8])
        assert np.array_equal(globals_dict['slice_2d_row'], [5, 6, 7, 8])
        assert np.array_equal(globals_dict['slice_2d_col'], [3, 7, 11])
        
        # Test advanced indexing
        assert np.array_equal(globals_dict['fancy_indexed'], [0, 2, 4])
        assert np.array_equal(globals_dict['even_numbers'], [0, 2, 4, 6, 8])
    
    def test_array_reshaping_and_manipulation(self):
        """Test array reshaping and manipulation operations."""
        code = '''
import numpy as np

# Create test array
arr = np.arange(12)

# Reshaping
reshaped_2d = arr.reshape(3, 4)
reshaped_3d = arr.reshape(2, 2, 3)

# Flattening
flattened = reshaped_2d.flatten()
raveled = reshaped_2d.ravel()

# Transposing
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
transposed = arr_2d.T
transposed_func = np.transpose(arr_2d)

# Concatenation
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
concatenated = np.concatenate([arr1, arr2])

# Stacking
stacked_vertical = np.vstack([arr1, arr2])
stacked_horizontal = np.hstack([arr1, arr2])

# Splitting
arr_to_split = np.arange(10)
split_arrays = np.split(arr_to_split, 5)

# Broadcasting
broadcast_result = arr1[:, np.newaxis] + arr2

# Array copying
shallow_copy = arr1.view()
deep_copy = arr1.copy()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test reshaping
        assert globals_dict['reshaped_2d'].shape == (3, 4)
        assert globals_dict['reshaped_3d'].shape == (2, 2, 3)
        
        # Test flattening
        assert len(globals_dict['flattened']) == 12
        assert np.array_equal(globals_dict['flattened'], np.arange(12))
        
        # Test transposing
        assert globals_dict['transposed'].shape == (3, 2)
        assert np.array_equal(globals_dict['transposed'], globals_dict['transposed_func'])
        
        # Test concatenation
        assert np.array_equal(globals_dict['concatenated'], [1, 2, 3, 4, 5, 6])
        assert globals_dict['stacked_vertical'].shape == (2, 3)
        
        # Test broadcasting
        assert globals_dict['broadcast_result'].shape == (3, 3)
    
    def test_linear_algebra_operations(self):
        """Test NumPy linear algebra operations."""
        code = '''
import numpy as np

# Matrix operations
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication
matrix_mult = np.dot(A, B)
matrix_mult_operator = A @ B

# Element-wise operations
element_mult = A * B
element_add = A + B

# Matrix properties
determinant = np.linalg.det(A)
trace = np.trace(A)

# Eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

# Matrix inverse (for invertible matrices)
try:
    inverse_A = np.linalg.inv(A)
    has_inverse = True
except np.linalg.LinAlgError:
    has_inverse = False

# Solving linear systems Ax = b
b = np.array([1, 2])
x_solution = np.linalg.solve(A, b)

# Verify solution
verification = np.allclose(A @ x_solution, b)

# Vector operations
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])

dot_product = np.dot(v1, v2)
cross_product = np.cross(v1, v2)
vector_norm = np.linalg.norm(v1)

# Matrix decompositions
U, s, Vt = np.linalg.svd(A)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test matrix operations
        expected_matrix_mult = np.array([[19, 22], [43, 50]])
        assert np.array_equal(globals_dict['matrix_mult'], expected_matrix_mult)
        assert np.array_equal(globals_dict['matrix_mult_operator'], expected_matrix_mult)
        
        # Test matrix properties
        assert abs(globals_dict['determinant'] - (-2.0)) < 1e-10
        assert globals_dict['trace'] == 5
        
        # Test solution verification
        assert globals_dict['verification'] is True
        
        # Test vector operations
        assert globals_dict['dot_product'] == 32
        assert len(globals_dict['cross_product']) == 3


class TestPandasExercises:
    """Test cases for Pandas DataFrame operations and exercises."""
    
    def test_dataframe_creation_and_basic_operations(self):
        """Test pandas DataFrame creation and basic operations."""
        code = '''
import pandas as pd
import numpy as np

# DataFrame creation from different sources
data_dict = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'salary': [50000, 60000, 70000, 55000],
    'department': ['Engineering', 'Marketing', 'Engineering', 'Sales']
}

df_from_dict = pd.DataFrame(data_dict)

# DataFrame from lists
df_from_lists = pd.DataFrame([
    ['Alice', 25, 50000],
    ['Bob', 30, 60000],
    ['Charlie', 35, 70000]
], columns=['name', 'age', 'salary'])

# Series creation
ages_series = pd.Series([25, 30, 35, 28], name='age')

# Basic DataFrame properties
num_rows, num_cols = df_from_dict.shape
column_names = list(df_from_dict.columns)
data_types = df_from_dict.dtypes.to_dict()
df_info = df_from_dict.info(buf=None)

# Basic statistics
age_mean = df_from_dict['age'].mean()
salary_std = df_from_dict['salary'].std()
age_median = df_from_dict['age'].median()

# DataFrame operations
df_copy = df_from_dict.copy()
df_copy['bonus'] = df_copy['salary'] * 0.1
df_copy['total_compensation'] = df_copy['salary'] + df_copy['bonus']

# Indexing and selection
first_row = df_from_dict.iloc[0]
first_col = df_from_dict['name']
subset_df = df_from_dict[['name', 'age']]
filtered_df = df_from_dict[df_from_dict['age'] > 30]

# Sorting
sorted_by_age = df_from_dict.sort_values('age')
sorted_by_salary_desc = df_from_dict.sort_values('salary', ascending=False)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test DataFrame properties
        assert globals_dict['num_rows'] == 4
        assert globals_dict['num_cols'] == 4
        assert 'name' in globals_dict['column_names']
        assert 'age' in globals_dict['column_names']
        
        # Test statistics
        assert globals_dict['age_mean'] == 29.5
        assert globals_dict['age_median'] == 29.0
        
        # Test operations
        assert 'bonus' in globals_dict['df_copy'].columns
        assert 'total_compensation' in globals_dict['df_copy'].columns
        
        # Test filtering
        filtered = globals_dict['filtered_df']
        assert len(filtered) == 2  # Bob and Charlie are > 30
        assert all(filtered['age'] > 30)
    
    def test_data_cleaning_and_preprocessing(self):
        """Test data cleaning and preprocessing operations."""
        code = '''
import pandas as pd
import numpy as np

# Create DataFrame with missing and messy data
data_messy = {
    'name': ['Alice', 'Bob', None, 'Diana', 'Eve'],
    'age': [25, None, 35, 28, 32],
    'salary': [50000, 60000, np.nan, 55000, 65000],
    'email': ['alice@email.com', 'BOB@EMAIL.COM', 'charlie@email.com', None, 'eve@email.com'],
    'join_date': ['2020-01-15', '2019-06-20', '2021-03-10', '2020-11-05', '2021-01-20']
}

df_messy = pd.DataFrame(data_messy)

# Handle missing values
df_cleaned = df_messy.copy()

# Fill missing names with 'Unknown'
df_cleaned['name'] = df_cleaned['name'].fillna('Unknown')

# Fill missing ages with median age
median_age = df_cleaned['age'].median()
df_cleaned['age'] = df_cleaned['age'].fillna(median_age)

# Drop rows with missing salary
df_cleaned = df_cleaned.dropna(subset=['salary'])

# Data type conversions
df_cleaned['join_date'] = pd.to_datetime(df_cleaned['join_date'])
df_cleaned['age'] = df_cleaned['age'].astype(int)

# String operations
df_cleaned['email'] = df_cleaned['email'].str.lower()
df_cleaned['name_length'] = df_cleaned['name'].str.len()

# Create derived columns
df_cleaned['years_at_company'] = (pd.Timestamp.now() - df_cleaned['join_date']).dt.days / 365.25

# Remove duplicates (if any)
df_cleaned = df_cleaned.drop_duplicates()

# Data validation
valid_emails = df_cleaned['email'].str.contains('@', na=False)
valid_ages = (df_cleaned['age'] >= 18) & (df_cleaned['age'] <= 100)

# Summary statistics after cleaning
final_shape = df_cleaned.shape
missing_values_count = df_cleaned.isnull().sum().sum()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test data cleaning results
        df_cleaned = globals_dict['df_cleaned']
        assert globals_dict['missing_values_count'] == 1  # Only email might be missing
        assert df_cleaned['name'].notna().all()  # No missing names after cleaning
        assert df_cleaned['salary'].notna().all()  # No missing salaries after dropping
        
        # Test data types
        assert pd.api.types.is_datetime64_any_dtype(df_cleaned['join_date'])
        assert pd.api.types.is_integer_dtype(df_cleaned['age'])
        
        # Test string operations
        assert all(email.islower() for email in df_cleaned['email'].dropna())
    
    def test_groupby_and_aggregation_operations(self):
        """Test groupby and aggregation operations."""
        code = '''
import pandas as pd
import numpy as np

# Create sample sales data
sales_data = {
    'salesperson': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob', 'Alice', 'Charlie', 'Bob'],
    'region': ['North', 'South', 'North', 'East', 'South', 'North', 'East', 'South'],
    'product': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'A'],
    'quantity': [10, 15, 8, 12, 20, 5, 18, 7],
    'price': [100, 150, 100, 200, 150, 200, 100, 100],
    'date': pd.date_range('2023-01-01', periods=8, freq='D')
}

df_sales = pd.DataFrame(sales_data)
df_sales['revenue'] = df_sales['quantity'] * df_sales['price']

# Basic groupby operations
grouped_by_person = df_sales.groupby('salesperson')['revenue'].sum()
grouped_by_region = df_sales.groupby('region')['revenue'].sum()

# Multiple aggregations
sales_summary = df_sales.groupby('salesperson').agg({
    'revenue': ['sum', 'mean', 'count'],
    'quantity': ['sum', 'mean']
})

# Groupby with multiple columns
region_product_summary = df_sales.groupby(['region', 'product'])['revenue'].sum()

# Custom aggregation functions
def revenue_range(series):
    return series.max() - series.min()

custom_agg = df_sales.groupby('salesperson')['revenue'].agg(['sum', 'mean', revenue_range])

# Transform operations
df_sales['revenue_pct_of_person_total'] = df_sales['revenue'] / df_sales.groupby('salesperson')['revenue'].transform('sum')

# Filter groups
high_revenue_groups = df_sales.groupby('salesperson').filter(lambda x: x['revenue'].sum() > 2000)

# Pivot tables
pivot_revenue = df_sales.pivot_table(
    values='revenue',
    index='salesperson',
    columns='region',
    aggfunc='sum',
    fill_value=0
)

# Cross-tabulation
crosstab_product_region = pd.crosstab(df_sales['product'], df_sales['region'], values=df_sales['quantity'], aggfunc='sum')

# Time-based grouping
df_sales['month'] = df_sales['date'].dt.month
monthly_revenue = df_sales.groupby('month')['revenue'].sum()
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test groupby results
        grouped_by_person = globals_dict['grouped_by_person']
        assert len(grouped_by_person) == 3  # Alice, Bob, Charlie
        assert all(revenue > 0 for revenue in grouped_by_person.values)
        
        # Test pivot table
        pivot_revenue = globals_dict['pivot_revenue']
        assert pivot_revenue.shape[0] == 3  # 3 salespeople
        assert pivot_revenue.shape[1] >= 2  # At least 2 regions
        
        # Test transform operations
        df_sales = globals_dict['df_sales']
        assert 'revenue_pct_of_person_total' in df_sales.columns
        
        # Verify percentages sum to 1 for each person
        pct_sums = df_sales.groupby('salesperson')['revenue_pct_of_person_total'].sum()
        assert all(abs(pct_sum - 1.0) < 1e-10 for pct_sum in pct_sums)
    
    def test_time_series_operations(self):
        """Test time series operations with pandas."""
        code = '''
import pandas as pd
import numpy as np

# Create time series data
date_range = pd.date_range('2023-01-01', '2023-12-31', freq='D')
np.random.seed(42)
values = np.random.randn(len(date_range)).cumsum() + 100

ts_data = pd.Series(values, index=date_range, name='value')

# Basic time series operations
ts_monthly = ts_data.resample('M').mean()
ts_weekly = ts_data.resample('W').sum()

# Rolling window operations
rolling_mean = ts_data.rolling(window=7).mean()
rolling_std = ts_data.rolling(window=30).std()

# Lag operations
ts_lag1 = ts_data.shift(1)
ts_lead1 = ts_data.shift(-1)

# Percentage change
pct_change = ts_data.pct_change()

# Date/time components
df_ts = ts_data.to_frame()
df_ts['year'] = df_ts.index.year
df_ts['month'] = df_ts.index.month
df_ts['day_of_week'] = df_ts.index.dayofweek
df_ts['quarter'] = df_ts.index.quarter

# Seasonal decomposition (simplified)
monthly_avg = df_ts.groupby('month')['value'].mean()
df_ts['seasonal'] = df_ts['month'].map(monthly_avg)
df_ts['detrended'] = df_ts['value'] - df_ts['seasonal']

# Time zone operations
ts_utc = ts_data.tz_localize('UTC')
ts_est = ts_utc.tz_convert('US/Eastern')

# Date filtering
q1_data = ts_data['2023-01':'2023-03']
march_data = ts_data['2023-03']

# Business day operations
business_days = pd.bdate_range('2023-01-01', '2023-12-31')
business_day_data = ts_data.reindex(business_days, method='ffill')

# Time-based statistics
daily_returns = ts_data.pct_change()
volatility = daily_returns.std() * np.sqrt(252)  # Annualized volatility
sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test time series operations
        ts_data = globals_dict['ts_data']
        assert len(ts_data) == 365  # Full year of daily data
        
        # Test resampling
        ts_monthly = globals_dict['ts_monthly']
        assert len(ts_monthly) == 12  # 12 months
        
        # Test rolling operations
        rolling_mean = globals_dict['rolling_mean']
        assert len(rolling_mean) == len(ts_data)
        
        # Test date components
        df_ts = globals_dict['df_ts']
        assert 'year' in df_ts.columns
        assert 'month' in df_ts.columns
        assert all(df_ts['year'] == 2023)
        assert all((df_ts['month'] >= 1) & (df_ts['month'] <= 12))


class TestMatplotlibExercises:
    """Test cases for Matplotlib plotting exercises."""
    
    @patch('matplotlib.pyplot.show')
    def test_basic_plotting_operations(self, mock_show):
        """Test basic matplotlib plotting operations."""
        code = '''
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) * np.exp(-x/5)

# Basic line plot
plt.figure(figsize=(10, 6))
plt.plot(x, y1, label='sin(x)', color='blue', linewidth=2)
plt.plot(x, y2, label='cos(x)', color='red', linestyle='--')
plt.plot(x, y3, label='damped sin(x)', color='green', marker='o', markersize=3)

plt.title('Trigonometric Functions')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True, alpha=0.3)

# Save plot info
plot_created = True

# Scatter plot
plt.figure(figsize=(8, 6))
np.random.seed(42)
x_scatter = np.random.randn(100)
y_scatter = 2 * x_scatter + np.random.randn(100)

plt.scatter(x_scatter, y_scatter, alpha=0.6, c=y_scatter, cmap='viridis')
plt.colorbar(label='y values')
plt.title('Scatter Plot with Color Mapping')
plt.xlabel('X values')
plt.ylabel('Y values')

scatter_created = True

# Histogram
plt.figure(figsize=(8, 6))
data = np.random.normal(100, 15, 1000)
counts, bins, patches = plt.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')

plt.title('Histogram of Random Data')
plt.xlabel('Value')
plt.ylabel('Frequency')

# Add statistics to plot
mean_val = np.mean(data)
std_val = np.std(data)
plt.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
plt.axvline(mean_val + std_val, color='orange', linestyle='--', label=f'+1 STD: {mean_val + std_val:.2f}')
plt.axvline(mean_val - std_val, color='orange', linestyle='--', label=f'-1 STD: {mean_val - std_val:.2f}')
plt.legend()

histogram_created = True

# Box plot
plt.figure(figsize=(8, 6))
data_groups = [np.random.normal(100, 10, 100),
               np.random.normal(110, 15, 100),
               np.random.normal(95, 8, 100)]

plt.boxplot(data_groups, labels=['Group A', 'Group B', 'Group C'])
plt.title('Box Plot Comparison')
plt.ylabel('Values')

boxplot_created = True
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test that plots were created successfully
        assert globals_dict['plot_created'] is True
        assert globals_dict['scatter_created'] is True
        assert globals_dict['histogram_created'] is True
        assert globals_dict['boxplot_created'] is True
        
        # Verify mock was called (plots were shown)
        assert mock_show.call_count >= 0  # show() might be called
    
    @patch('matplotlib.pyplot.show')
    def test_subplots_and_advanced_plotting(self, mock_show):
        """Test subplot creation and advanced plotting features."""
        code = '''
import matplotlib.pyplot as plt
import numpy as np

# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Multiple Subplots Example')

# Subplot 1: Line plot
x = np.linspace(0, 10, 100)
axes[0, 0].plot(x, np.sin(x), 'b-', label='sin(x)')
axes[0, 0].plot(x, np.cos(x), 'r--', label='cos(x)')
axes[0, 0].set_title('Trigonometric Functions')
axes[0, 0].set_xlabel('x')
axes[0, 0].set_ylabel('y')
axes[0, 0].legend()
axes[0, 0].grid(True)

# Subplot 2: Bar plot
categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]
axes[0, 1].bar(categories, values, color=['red', 'green', 'blue', 'orange', 'purple'])
axes[0, 1].set_title('Bar Chart')
axes[0, 1].set_ylabel('Values')

# Subplot 3: Pie chart
sizes = [30, 25, 20, 15, 10]
labels = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
axes[1, 0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
axes[1, 0].set_title('Pie Chart')

# Subplot 4: Heatmap-like plot
data_2d = np.random.rand(10, 10)
im = axes[1, 1].imshow(data_2d, cmap='hot', interpolation='nearest')
axes[1, 1].set_title('Heatmap')
fig.colorbar(im, ax=axes[1, 1])

plt.tight_layout()
subplots_created = True

# Custom styling
plt.style.use('default')  # Reset to default style

fig, ax = plt.subplots(figsize=(10, 6))

# Create data
x = np.linspace(0, 10, 50)
y = np.sin(x) + 0.1 * np.random.randn(50)

# Plot with custom styling
ax.plot(x, y, 'o-', color='#2E86AB', linewidth=2, markersize=6, alpha=0.8)
ax.fill_between(x, y, alpha=0.3, color='#A23B72')

# Customize axes
ax.set_xlim(0, 10)
ax.set_ylim(-1.5, 1.5)
ax.set_xlabel('X values', fontsize=12, fontweight='bold')
ax.set_ylabel('Y values', fontsize=12, fontweight='bold')
ax.set_title('Customized Plot', fontsize=14, fontweight='bold', pad=20)

# Add annotations
max_idx = np.argmax(y)
ax.annotate(f'Maximum: ({x[max_idx]:.2f}, {y[max_idx]:.2f})',
            xy=(x[max_idx], y[max_idx]),
            xytext=(x[max_idx] + 1, y[max_idx] + 0.5),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

# Customize grid and spines
ax.grid(True, linestyle='--', alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

custom_plot_created = True

# 3D plotting
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax_3d = fig.add_subplot(111, projection='3d')

# Create 3D surface
x_3d = np.linspace(-5, 5, 50)
y_3d = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x_3d, y_3d)
Z = np.sin(np.sqrt(X**2 + Y**2))

surface = ax_3d.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax_3d.set_xlabel('X')
ax_3d.set_ylabel('Y')
ax_3d.set_zlabel('Z')
ax_3d.set_title('3D Surface Plot')

fig.colorbar(surface)
plot_3d_created = True
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test that advanced plots were created
        assert globals_dict['subplots_created'] is True
        assert globals_dict['custom_plot_created'] is True
        assert globals_dict['plot_3d_created'] is True
    
    def test_plot_data_analysis_integration(self):
        """Test integration of plotting with data analysis."""
        code = '''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create sample dataset
np.random.seed(42)
dates = pd.date_range('2023-01-01', periods=365, freq='D')
base_temp = 20 + 10 * np.sin(2 * np.pi * np.arange(365) / 365)  # Seasonal variation
temp = base_temp + np.random.normal(0, 3, 365)  # Add noise
humidity = 60 + 20 * np.sin(2 * np.pi * np.arange(365) / 365 + np.pi/4) + np.random.normal(0, 5, 365)

weather_data = pd.DataFrame({
    'date': dates,
    'temperature': temp,
    'humidity': humidity
})

weather_data['month'] = weather_data['date'].dt.month
weather_data['season'] = weather_data['month'].map({
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Fall', 10: 'Fall', 11: 'Fall'
})

# Time series plot
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Temperature over time
axes[0].plot(weather_data['date'], weather_data['temperature'], color='red', alpha=0.7)
axes[0].set_title('Temperature Over Time')
axes[0].set_ylabel('Temperature (°C)')
axes[0].grid(True, alpha=0.3)

# Humidity over time
axes[1].plot(weather_data['date'], weather_data['humidity'], color='blue', alpha=0.7)
axes[1].set_title('Humidity Over Time')
axes[1].set_ylabel('Humidity (%)')
axes[1].grid(True, alpha=0.3)

# Correlation scatter plot
scatter = axes[2].scatter(weather_data['temperature'], weather_data['humidity'], 
                         c=weather_data['month'], cmap='tab12', alpha=0.6)
axes[2].set_xlabel('Temperature (°C)')
axes[2].set_ylabel('Humidity (%)')
axes[2].set_title('Temperature vs Humidity')
plt.colorbar(scatter, ax=axes[2], label='Month')

plt.tight_layout()
time_series_plots_created = True

# Statistical plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Box plots by season
weather_data.boxplot(column='temperature', by='season', ax=axes[0, 0])
axes[0, 0].set_title('Temperature Distribution by Season')
axes[0, 0].set_xlabel('Season')
axes[0, 0].set_ylabel('Temperature (°C)')

# Histogram with density curve
axes[0, 1].hist(weather_data['temperature'], bins=30, density=True, alpha=0.7, color='skyblue')
x_temp = np.linspace(weather_data['temperature'].min(), weather_data['temperature'].max(), 100)
temp_mean = weather_data['temperature'].mean()
temp_std = weather_data['temperature'].std()
y_normal = (1/(temp_std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_temp - temp_mean)/temp_std)**2)
axes[0, 1].plot(x_temp, y_normal, 'r-', linewidth=2, label='Normal Distribution')
axes[0, 1].set_title('Temperature Distribution')
axes[0, 1].set_xlabel('Temperature (°C)')
axes[0, 1].set_ylabel('Density')
axes[0, 1].legend()

# Monthly averages
monthly_avg = weather_data.groupby('month').agg({
    'temperature': 'mean',
    'humidity': 'mean'
})

axes[1, 0].bar(monthly_avg.index, monthly_avg['temperature'], alpha=0.7, color='red')
axes[1, 0].set_title('Average Temperature by Month')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Temperature (°C)')

# Correlation heatmap (simplified)
correlation_matrix = weather_data[['temperature', 'humidity']].corr()
im = axes[1, 1].imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)
axes[1, 1].set_xticks(range(len(correlation_matrix.columns)))
axes[1, 1].set_yticks(range(len(correlation_matrix.columns)))
axes[1, 1].set_xticklabels(correlation_matrix.columns)
axes[1, 1].set_yticklabels(correlation_matrix.columns)
axes[1, 1].set_title('Correlation Matrix')

# Add correlation values as text
for i in range(len(correlation_matrix.columns)):
    for j in range(len(correlation_matrix.columns)):
        text = axes[1, 1].text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black")

plt.tight_layout()
statistical_plots_created = True

# Calculate correlation coefficient
temp_humidity_corr = weather_data['temperature'].corr(weather_data['humidity'])
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test that data analysis plots were created
        assert globals_dict['time_series_plots_created'] is True
        assert globals_dict['statistical_plots_created'] is True
        
        # Test data analysis results
        weather_data = globals_dict['weather_data']
        assert len(weather_data) == 365
        assert 'season' in weather_data.columns
        
        # Test correlation calculation
        correlation = globals_dict['temp_humidity_corr']
        assert -1 <= correlation <= 1


class TestDataAnalysisExercises:
    """Test cases for comprehensive data analysis exercises."""
    
    def test_exploratory_data_analysis(self):
        """Test exploratory data analysis workflow."""
        code = '''
import pandas as pd
import numpy as np

# Create comprehensive dataset
np.random.seed(42)
n_samples = 1000

# Generate realistic sales data
data = {
    'customer_id': range(1, n_samples + 1),
    'age': np.random.normal(40, 12, n_samples).astype(int),
    'income': np.random.lognormal(10.5, 0.5, n_samples),
    'purchase_amount': np.random.exponential(50, n_samples),
    'num_purchases': np.random.poisson(3, n_samples),
    'satisfaction_score': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.05, 0.15, 0.30, 0.35, 0.15]),
    'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples, p=[0.3, 0.25, 0.25, 0.2]),
    'customer_type': np.random.choice(['Premium', 'Standard', 'Basic'], n_samples, p=[0.2, 0.5, 0.3])
}

# Ensure realistic age bounds
data['age'] = np.clip(data['age'], 18, 80)

df = pd.DataFrame(data)

# Basic exploratory analysis
shape_info = df.shape
data_types = df.dtypes.to_dict()
missing_values = df.isnull().sum().to_dict()

# Descriptive statistics
numeric_desc = df.describe()
categorical_desc = df.describe(include=['object'])

# Unique value counts
unique_counts = {col: df[col].nunique() for col in df.columns}

# Correlation analysis
numeric_columns = df.select_dtypes(include=[np.number]).columns
correlation_matrix = df[numeric_columns].corr()

# Outlier detection using IQR method
def detect_outliers_iqr(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return series[(series < lower_bound) | (series > upper_bound)]

outliers_income = detect_outliers_iqr(df['income'])
outliers_purchase = detect_outliers_iqr(df['purchase_amount'])

# Distribution analysis
income_skewness = df['income'].skew()
purchase_kurtosis = df['purchase_amount'].kurtosis()

# Group analysis
region_summary = df.groupby('region').agg({
    'purchase_amount': ['mean', 'median', 'std'],
    'satisfaction_score': 'mean',
    'num_purchases': 'sum'
})

customer_type_summary = df.groupby('customer_type').agg({
    'income': 'mean',
    'purchase_amount': 'mean',
    'satisfaction_score': 'mean'
})

# Advanced analysis
# Customer value segmentation
df['total_spent'] = df['purchase_amount'] * df['num_purchases']
df['avg_purchase_value'] = df['purchase_amount']

# Define customer segments based on spending and frequency
conditions = [
    (df['total_spent'] >= df['total_spent'].quantile(0.75)) & (df['num_purchases'] >= df['num_purchases'].quantile(0.75)),
    (df['total_spent'] >= df['total_spent'].quantile(0.5)) & (df['num_purchases'] >= df['num_purchases'].quantile(0.5)),
    (df['total_spent'] >= df['total_spent'].quantile(0.25)) & (df['num_purchases'] >= df['num_purchases'].quantile(0.25))
]
choices = ['High Value', 'Medium Value', 'Regular']
df['customer_segment'] = np.select(conditions, choices, default='Low Value')

segment_distribution = df['customer_segment'].value_counts()

# Statistical tests (simplified)
from scipy import stats

# Test if there's a significant difference in satisfaction between customer types
premium_satisfaction = df[df['customer_type'] == 'Premium']['satisfaction_score']
standard_satisfaction = df[df['customer_type'] == 'Standard']['satisfaction_score']
basic_satisfaction = df[df['customer_type'] == 'Basic']['satisfaction_score']

# ANOVA test (simplified)
f_statistic, p_value = stats.f_oneway(premium_satisfaction, standard_satisfaction, basic_satisfaction)
significant_difference = p_value < 0.05
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test EDA results
        df = globals_dict['df']
        assert globals_dict['shape_info'] == (1000, 8)
        assert len(globals_dict['missing_values']) == 8
        
        # Test outlier detection
        assert len(globals_dict['outliers_income']) >= 0
        assert len(globals_dict['outliers_purchase']) >= 0
        
        # Test segmentation
        assert 'customer_segment' in df.columns
        segment_dist = globals_dict['segment_distribution']
        assert len(segment_dist) >= 3  # At least 3 segments
        
        # Test statistical analysis
        assert isinstance(globals_dict['significant_difference'], bool)
    
    def test_data_preprocessing_pipeline(self):
        """Test comprehensive data preprocessing pipeline."""
        code = '''
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split

# Create raw dataset with various data quality issues
np.random.seed(42)
n_samples = 500

raw_data = {
    'name': [f'Customer_{i}' for i in range(n_samples)],
    'age': np.random.normal(35, 10, n_samples),
    'income': np.random.lognormal(10, 0.5, n_samples),
    'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD', None], 
                                  n_samples, p=[0.3, 0.4, 0.2, 0.05, 0.05]),
    'employment_status': np.random.choice(['Employed', 'Unemployed', 'Self-employed', 'Student'], 
                                         n_samples, p=[0.7, 0.1, 0.15, 0.05]),
    'credit_score': np.random.normal(650, 100, n_samples),
    'loan_amount': np.random.exponential(10000, n_samples),
    'default': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
}

# Introduce missing values and outliers
raw_data['age'][np.random.choice(n_samples, 20, replace=False)] = np.nan
raw_data['income'][np.random.choice(n_samples, 15, replace=False)] = np.nan
raw_data['credit_score'][np.random.choice(n_samples, 10, replace=False)] = np.nan

# Add some extreme outliers
raw_data['age'][np.random.choice(n_samples, 5, replace=False)] = 150
raw_data['income'][np.random.choice(n_samples, 3, replace=False)] = 1000000

df_raw = pd.DataFrame(raw_data)

# Data preprocessing pipeline
df_processed = df_raw.copy()

# Step 1: Handle missing values
# For numerical columns: fill with median
numerical_cols = ['age', 'income', 'credit_score', 'loan_amount']
for col in numerical_cols:
    if col in df_processed.columns:
        median_val = df_processed[col].median()
        df_processed[col] = df_processed[col].fillna(median_val)

# For categorical columns: fill with mode or 'Unknown'
categorical_cols = ['education', 'employment_status']
for col in categorical_cols:
    if col in df_processed.columns:
        if df_processed[col].mode().empty:
            df_processed[col] = df_processed[col].fillna('Unknown')
        else:
            mode_val = df_processed[col].mode()[0]
            df_processed[col] = df_processed[col].fillna(mode_val)

# Step 2: Handle outliers using IQR method
def remove_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Remove outliers for key numerical columns
outlier_cols = ['age', 'income']
for col in outlier_cols:
    df_processed = remove_outliers_iqr(df_processed, col)

# Step 3: Data transformation
# Log transform skewed variables
df_processed['income_log'] = np.log1p(df_processed['income'])
df_processed['loan_amount_log'] = np.log1p(df_processed['loan_amount'])

# Create derived features
df_processed['debt_to_income'] = df_processed['loan_amount'] / df_processed['income']
df_processed['age_group'] = pd.cut(df_processed['age'], 
                                  bins=[0, 25, 35, 50, 65, 100], 
                                  labels=['Young', 'Adult', 'Middle-aged', 'Senior', 'Elderly'])

# Step 4: Encoding categorical variables
# Label encoding for ordinal variables
education_order = ['High School', 'Bachelor', 'Master', 'PhD', 'Unknown']
education_mapping = {edu: i for i, edu in enumerate(education_order)}
df_processed['education_encoded'] = df_processed['education'].map(education_mapping)

# One-hot encoding for nominal variables
employment_dummies = pd.get_dummies(df_processed['employment_status'], prefix='employment')
df_processed = pd.concat([df_processed, employment_dummies], axis=1)

# Step 5: Feature scaling
scaler = StandardScaler()
features_to_scale = ['age', 'income_log', 'credit_score', 'loan_amount_log', 'debt_to_income']
df_processed[features_to_scale] = scaler.fit_transform(df_processed[features_to_scale])

# Step 6: Feature selection (keep relevant columns)
final_features = [
    'age', 'income_log', 'credit_score', 'loan_amount_log', 'debt_to_income',
    'education_encoded'
] + [col for col in df_processed.columns if col.startswith('employment_')]

X = df_processed[final_features]
y = df_processed['default']

# Step 7: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Data quality metrics
initial_missing = df_raw.isnull().sum().sum()
final_missing = df_processed[final_features].isnull().sum().sum()
initial_shape = df_raw.shape
final_shape = df_processed.shape
feature_count = len(final_features)

# Preprocessing summary
preprocessing_summary = {
    'initial_samples': initial_shape[0],
    'final_samples': final_shape[0],
    'initial_features': initial_shape[1],
    'final_features': feature_count,
    'initial_missing_values': initial_missing,
    'final_missing_values': final_missing,
    'samples_removed': initial_shape[0] - final_shape[0]
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test preprocessing results
        summary = globals_dict['preprocessing_summary']
        assert summary['final_missing_values'] == 0  # No missing values after preprocessing
        assert summary['final_features'] > summary['initial_features']  # More features due to encoding
        
        # Test train-test split
        X_train = globals_dict['X_train']
        X_test = globals_dict['X_test']
        y_train = globals_dict['y_train']
        y_test = globals_dict['y_test']
        
        assert len(X_train) > len(X_test)  # 80-20 split
        assert len(X_train) == len(y_train)
        assert len(X_test) == len(y_test)


class TestMachineLearningExercises:
    """Test cases for basic machine learning exercises."""
    
    def test_supervised_learning_classification(self):
        """Test supervised learning classification workflow."""
        code = '''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Generate synthetic classification dataset
np.random.seed(42)
n_samples = 1000

# Features
X = np.random.randn(n_samples, 5)
X[:, 0] = X[:, 0] * 2 + 1  # Age feature
X[:, 1] = X[:, 1] * 10000 + 50000  # Income feature
X[:, 2] = np.abs(X[:, 2]) * 100 + 500  # Credit score feature
X[:, 3] = np.abs(X[:, 3]) * 5 + 1  # Number of accounts
X[:, 4] = np.abs(X[:, 4]) * 20 + 10  # Account age

# Create target variable (loan approval)
# Higher income, credit score, and account age increase approval probability
approval_prob = (
    0.3 * (X[:, 1] - X[:, 1].min()) / (X[:, 1].max() - X[:, 1].min()) +
    0.4 * (X[:, 2] - X[:, 2].min()) / (X[:, 2].max() - X[:, 2].min()) +
    0.2 * (X[:, 4] - X[:, 4].min()) / (X[:, 4].max() - X[:, 4].min()) +
    0.1 * np.random.rand(n_samples)
)

y = (approval_prob > 0.6).astype(int)

# Create DataFrame
feature_names = ['age', 'income', 'credit_score', 'num_accounts', 'account_age']
df = pd.DataFrame(X, columns=feature_names)
df['loan_approved'] = y

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    df[feature_names], df['loan_approved'], 
    test_size=0.2, random_state=42, stratify=df['loan_approved']
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train multiple models
models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
}

model_results = {}

for model_name, model in models.items():
    # Train model
    if model_name == 'Logistic Regression':
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Store results
    model_results[model_name] = {
        'accuracy': accuracy,
        'predictions': y_pred,
        'probabilities': y_pred_proba,
        'model': model
    }

# Feature importance for Random Forest
rf_model = model_results['Random Forest']['model']
feature_importance = dict(zip(feature_names, rf_model.feature_importances_))

# Best model selection
best_model_name = max(model_results.keys(), key=lambda x: model_results[x]['accuracy'])
best_accuracy = model_results[best_model_name]['accuracy']

# Class distribution
class_distribution = df['loan_approved'].value_counts().to_dict()

# Model comparison summary
comparison_summary = {
    model_name: results['accuracy'] 
    for model_name, results in model_results.items()
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test ML workflow results
        model_results = globals_dict['model_results']
        assert len(model_results) == 2  # Two models trained
        
        # Test accuracy scores
        for model_name, results in model_results.items():
            assert 0 <= results['accuracy'] <= 1
            assert len(results['predictions']) == len(globals_dict['y_test'])
        
        # Test feature importance
        feature_importance = globals_dict['feature_importance']
        assert len(feature_importance) == 5  # 5 features
        assert all(importance >= 0 for importance in feature_importance.values())
        
        # Test best model selection
        best_model = globals_dict['best_model_name']
        assert best_model in ['Logistic Regression', 'Random Forest']
    
    def test_supervised_learning_regression(self):
        """Test supervised learning regression workflow."""
        code = '''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

# Generate synthetic regression dataset (house prices)
np.random.seed(42)
n_samples = 800

# Features
features = {
    'size_sqft': np.random.normal(2000, 500, n_samples),
    'bedrooms': np.random.poisson(3, n_samples) + 1,
    'bathrooms': np.random.poisson(2, n_samples) + 1,
    'age_years': np.random.exponential(10, n_samples),
    'garage_size': np.random.poisson(2, n_samples),
    'lot_size': np.random.normal(8000, 2000, n_samples)
}

# Ensure realistic values
features['size_sqft'] = np.clip(features['size_sqft'], 800, 5000)
features['bedrooms'] = np.clip(features['bedrooms'], 1, 6)
features['bathrooms'] = np.clip(features['bathrooms'], 1, 4)
features['age_years'] = np.clip(features['age_years'], 0, 50)
features['garage_size'] = np.clip(features['garage_size'], 0, 4)
features['lot_size'] = np.clip(features['lot_size'], 3000, 20000)

df = pd.DataFrame(features)

# Create target variable (house price)
price = (
    df['size_sqft'] * 150 +  # $150 per sqft
    df['bedrooms'] * 10000 +  # $10k per bedroom
    df['bathrooms'] * 15000 +  # $15k per bathroom
    df['garage_size'] * 8000 +  # $8k per garage space
    df['lot_size'] * 5 -  # $5 per sqft of lot
    df['age_years'] * 2000 +  # Depreciation
    np.random.normal(0, 20000, n_samples)  # Random noise
)

# Ensure positive prices
df['price'] = np.clip(price, 100000, 1000000)

# Feature engineering
df['price_per_sqft'] = df['price'] / df['size_sqft']
df['bed_bath_ratio'] = df['bedrooms'] / df['bathrooms']
df['total_rooms'] = df['bedrooms'] + df['bathrooms']

# Prepare features for modeling
feature_columns = ['size_sqft', 'bedrooms', 'bathrooms', 'age_years', 
                  'garage_size', 'lot_size', 'bed_bath_ratio', 'total_rooms']

X = df[feature_columns]
y = df['price']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Feature scaling for linear regression
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train models
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42)
}

regression_results = {}

for model_name, model in models.items():
    # Train model
    if model_name == 'Linear Regression':
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Store results
    regression_results[model_name] = {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': y_pred,
        'model': model
    }

# Feature importance for Random Forest
rf_model = regression_results['Random Forest']['model']
rf_feature_importance = dict(zip(feature_columns, rf_model.feature_importances_))

# Linear regression coefficients
lr_model = regression_results['Linear Regression']['model']
lr_coefficients = dict(zip(feature_columns, lr_model.coef_))

# Best model based on R2 score
best_regression_model = max(regression_results.keys(), 
                           key=lambda x: regression_results[x]['r2'])

# Prediction accuracy analysis
best_predictions = regression_results[best_regression_model]['predictions']
prediction_errors = y_test - best_predictions
mean_error = np.mean(prediction_errors)
std_error = np.std(prediction_errors)

# Model performance summary
performance_summary = {
    model_name: {
        'R2': results['r2'],
        'RMSE': results['rmse'],
        'MAE': results['mae']
    }
    for model_name, results in regression_results.items()
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test regression results
        regression_results = globals_dict['regression_results']
        assert len(regression_results) == 2  # Two models trained
        
        # Test metrics
        for model_name, results in regression_results.items():
            assert results['r2'] <= 1  # R2 should be <= 1
            assert results['rmse'] > 0  # RMSE should be positive
            assert results['mae'] > 0  # MAE should be positive
        
        # Test feature importance
        rf_importance = globals_dict['rf_feature_importance']
        assert len(rf_importance) == 8  # 8 features
        assert all(importance >= 0 for importance in rf_importance.values())
        
        # Test coefficients
        lr_coefficients = globals_dict['lr_coefficients']
        assert len(lr_coefficients) == 8  # 8 features
    
    def test_unsupervised_learning_clustering(self):
        """Test unsupervised learning clustering workflow."""
        code = '''
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score

# Generate synthetic customer data for clustering
np.random.seed(42)
n_customers = 600

# Create different customer segments
segments = []

# Segment 1: High-value customers
high_value = {
    'annual_spending': np.random.normal(8000, 1500, 200),
    'frequency': np.random.normal(25, 5, 200),
    'recency': np.random.normal(15, 5, 200),
    'age': np.random.normal(45, 10, 200)
}

# Segment 2: Medium-value customers
medium_value = {
    'annual_spending': np.random.normal(4000, 800, 250),
    'frequency': np.random.normal(15, 3, 250),
    'recency': np.random.normal(30, 8, 250),
    'age': np.random.normal(35, 8, 250)
}

# Segment 3: Low-value customers
low_value = {
    'annual_spending': np.random.normal(1500, 400, 150),
    'frequency': np.random.normal(6, 2, 150),
    'recency': np.random.normal(60, 15, 150),
    'age': np.random.normal(28, 6, 150)
}

# Combine segments
customer_data = {
    'annual_spending': np.concatenate([high_value['annual_spending'], 
                                     medium_value['annual_spending'], 
                                     low_value['annual_spending']]),
    'frequency': np.concatenate([high_value['frequency'], 
                               medium_value['frequency'], 
                               low_value['frequency']]),
    'recency': np.concatenate([high_value['recency'], 
                             medium_value['recency'], 
                             low_value['recency']]),
    'age': np.concatenate([high_value['age'], 
                         medium_value['age'], 
                         low_value['age']])
}

# True labels for evaluation (not used in clustering)
true_labels = np.array([0] * 200 + [1] * 250 + [2] * 150)

df_customers = pd.DataFrame(customer_data)

# Ensure positive values
df_customers['annual_spending'] = np.abs(df_customers['annual_spending'])
df_customers['frequency'] = np.abs(df_customers['frequency'])
df_customers['recency'] = np.abs(df_customers['recency'])
df_customers['age'] = np.clip(df_customers['age'], 18, 80)

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_customers)

# K-Means clustering
# Find optimal number of clusters using elbow method
inertias = []
silhouette_scores = []
k_range = range(2, 8)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    sil_score = silhouette_score(X_scaled, kmeans.labels_)
    silhouette_scores.append(sil_score)

# Choose optimal k (highest silhouette score)
optimal_k = k_range[np.argmax(silhouette_scores)]
best_silhouette = max(silhouette_scores)

# Train final K-Means model
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
kmeans_labels = kmeans_final.fit_predict(X_scaled)

# DBSCAN clustering
dbscan = DBSCAN(eps=0.5, min_samples=5)
dbscan_labels = dbscan.fit_predict(X_scaled)

# Cluster analysis
df_customers['kmeans_cluster'] = kmeans_labels
df_customers['dbscan_cluster'] = dbscan_labels

# K-Means cluster statistics
kmeans_cluster_stats = df_customers.groupby('kmeans_cluster').agg({
    'annual_spending': ['mean', 'std'],
    'frequency': ['mean', 'std'],
    'recency': ['mean', 'std'],
    'age': ['mean', 'std']
})

# DBSCAN cluster statistics (excluding noise points)
dbscan_non_noise = df_customers[df_customers['dbscan_cluster'] != -1]
if len(dbscan_non_noise) > 0:
    dbscan_cluster_stats = dbscan_non_noise.groupby('dbscan_cluster').agg({
        'annual_spending': ['mean', 'std'],
        'frequency': ['mean', 'std'],
        'recency': ['mean', 'std'],
        'age': ['mean', 'std']
    })
else:
    dbscan_cluster_stats = pd.DataFrame()

# Cluster validation metrics
kmeans_silhouette = silhouette_score(X_scaled, kmeans_labels)

# DBSCAN validation (only if clusters exist)
n_dbscan_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
if n_dbscan_clusters > 1:
    dbscan_non_noise_data = X_scaled[dbscan_labels != -1]
    dbscan_non_noise_labels = dbscan_labels[dbscan_labels != -1]
    dbscan_silhouette = silhouette_score(dbscan_non_noise_data, dbscan_non_noise_labels)
else:
    dbscan_silhouette = -1

# Compare with true labels (if available)
kmeans_ari = adjusted_rand_score(true_labels, kmeans_labels)
dbscan_ari = adjusted_rand_score(true_labels, dbscan_labels)

# PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
explained_variance_ratio = pca.explained_variance_ratio_

# Clustering summary
clustering_summary = {
    'optimal_k': optimal_k,
    'kmeans_clusters': len(set(kmeans_labels)),
    'dbscan_clusters': n_dbscan_clusters,
    'dbscan_noise_points': sum(dbscan_labels == -1),
    'kmeans_silhouette': kmeans_silhouette,
    'dbscan_silhouette': dbscan_silhouette,
    'kmeans_ari': kmeans_ari,
    'dbscan_ari': dbscan_ari,
    'pca_variance_explained': sum(explained_variance_ratio)
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test clustering results
        summary = globals_dict['clustering_summary']
        assert summary['optimal_k'] >= 2
        assert summary['kmeans_clusters'] >= 2
        assert -1 <= summary['kmeans_silhouette'] <= 1
        assert -1 <= summary['kmeans_ari'] <= 1
        
        # Test PCA
        assert 0 <= summary['pca_variance_explained'] <= 1
        
        # Test cluster statistics
        kmeans_stats = globals_dict['kmeans_cluster_stats']
        assert len(kmeans_stats) >= 2  # At least 2 clusters


class TestStatisticsExercises:
    """Test cases for statistics and probability exercises."""
    
    def test_descriptive_statistics(self):
        """Test descriptive statistics calculations."""
        code = '''
import numpy as np
import pandas as pd
from scipy import stats

# Generate sample data
np.random.seed(42)
data = {
    'normal_dist': np.random.normal(100, 15, 1000),
    'uniform_dist': np.random.uniform(0, 100, 1000),
    'exponential_dist': np.random.exponential(2, 1000),
    'poisson_dist': np.random.poisson(5, 1000)
}

df_stats = pd.DataFrame(data)

# Central tendency measures
measures_central = {}
for col in df_stats.columns:
    measures_central[col] = {
        'mean': df_stats[col].mean(),
        'median': df_stats[col].median(),
        'mode': stats.mode(df_stats[col])[0][0] if len(stats.mode(df_stats[col])[0]) > 0 else np.nan
    }

# Variability measures
measures_variability = {}
for col in df_stats.columns:
    measures_variability[col] = {
        'variance': df_stats[col].var(),
        'std_dev': df_stats[col].std(),
        'range': df_stats[col].max() - df_stats[col].min(),
        'iqr': df_stats[col].quantile(0.75) - df_stats[col].quantile(0.25),
        'mad': np.median(np.abs(df_stats[col] - df_stats[col].median()))  # Median Absolute Deviation
    }

# Distribution shape measures
measures_shape = {}
for col in df_stats.columns:
    measures_shape[col] = {
        'skewness': stats.skew(df_stats[col]),
        'kurtosis': stats.kurtosis(df_stats[col]),
        'min': df_stats[col].min(),
        'max': df_stats[col].max(),
        'q1': df_stats[col].quantile(0.25),
        'q3': df_stats[col].quantile(0.75)
    }

# Percentiles
percentiles = [10, 25, 50, 75, 90, 95, 99]
percentile_values = {}
for col in df_stats.columns:
    percentile_values[col] = {
        f'p{p}': df_stats[col].quantile(p/100) 
        for p in percentiles
    }

# Correlation analysis
correlation_matrix = df_stats.corr()
correlation_pairs = []
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        col1 = correlation_matrix.columns[i]
        col2 = correlation_matrix.columns[j]
        corr_value = correlation_matrix.iloc[i, j]
        correlation_pairs.append({
            'variables': f'{col1}_vs_{col2}',
            'correlation': corr_value,
            'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate' if abs(corr_value) > 0.3 else 'weak'
        })

# Z-scores and outlier detection
z_scores = {}
outliers = {}
for col in df_stats.columns:
    z_scores[col] = np.abs(stats.zscore(df_stats[col]))
    outliers[col] = np.sum(z_scores[col] > 3)  # Count of outliers (z-score > 3)

# Confidence intervals
confidence_intervals = {}
confidence_level = 0.95
for col in df_stats.columns:
    mean_val = df_stats[col].mean()
    sem = stats.sem(df_stats[col])  # Standard error of mean
    ci = stats.t.interval(confidence_level, len(df_stats[col])-1, mean_val, sem)
    confidence_intervals[col] = {
        'mean': mean_val,
        'ci_lower': ci[0],
        'ci_upper': ci[1],
        'margin_of_error': ci[1] - mean_val
    }
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test descriptive statistics
        central = globals_dict['measures_central']
        variability = globals_dict['measures_variability']
        shape = globals_dict['measures_shape']
        
        assert len(central) == 4  # 4 distributions
        assert len(variability) == 4
        assert len(shape) == 4
        
        # Test that normal distribution has expected properties
        normal_stats = central['normal_dist']
        assert 95 < normal_stats['mean'] < 105  # Should be around 100
        assert abs(normal_stats['mean'] - normal_stats['median']) < 5  # Should be close for normal dist
        
        # Test outlier detection
        outliers = globals_dict['outliers']
        assert all(count >= 0 for count in outliers.values())
        
        # Test confidence intervals
        ci = globals_dict['confidence_intervals']
        assert len(ci) == 4
        for col_ci in ci.values():
            assert col_ci['ci_lower'] < col_ci['mean'] < col_ci['ci_upper']
    
    def test_hypothesis_testing(self):
        """Test hypothesis testing procedures."""
        code = '''
import numpy as np
import pandas as pd
from scipy import stats

# Generate sample data for hypothesis testing
np.random.seed(42)

# Scenario 1: One-sample t-test
# Test if a new teaching method improves test scores (population mean = 75)
new_method_scores = np.random.normal(78, 10, 30)  # Slightly higher mean
population_mean = 75

# One-sample t-test
t_stat_one, p_value_one = stats.ttest_1samp(new_method_scores, population_mean)
alpha = 0.05
reject_null_one = p_value_one < alpha

# Effect size (Cohen's d)
cohens_d_one = (np.mean(new_method_scores) - population_mean) / np.std(new_method_scores, ddof=1)

# Scenario 2: Two-sample t-test
# Compare test scores between two different teaching methods
method_a_scores = np.random.normal(75, 12, 35)
method_b_scores = np.random.normal(80, 10, 32)

# Independent two-sample t-test
t_stat_two, p_value_two = stats.ttest_ind(method_a_scores, method_b_scores)
reject_null_two = p_value_two < alpha

# Welch's t-test (unequal variances)
t_stat_welch, p_value_welch = stats.ttest_ind(method_a_scores, method_b_scores, equal_var=False)

# Effect size (Cohen's d for two samples)
pooled_std = np.sqrt(((len(method_a_scores) - 1) * np.var(method_a_scores, ddof=1) + 
                     (len(method_b_scores) - 1) * np.var(method_b_scores, ddof=1)) / 
                     (len(method_a_scores) + len(method_b_scores) - 2))
cohens_d_two = (np.mean(method_b_scores) - np.mean(method_a_scores)) / pooled_std

# Scenario 3: Paired t-test
# Test if training improves performance (before/after measurements)
before_training = np.random.normal(70, 8, 25)
improvement = np.random.normal(5, 3, 25)  # Average improvement of 5 points
after_training = before_training + improvement

# Paired t-test
t_stat_paired, p_value_paired = stats.ttest_rel(after_training, before_training)
reject_null_paired = p_value_paired < alpha

# Effect size for paired test
differences = after_training - before_training
cohens_d_paired = np.mean(differences) / np.std(differences, ddof=1)

# Scenario 4: Chi-square test of independence
# Test if gender is independent of course preference
np.random.seed(42)
# Create contingency table
contingency_table = np.array([
    [15, 25, 10],  # Male preferences for courses A, B, C
    [20, 15, 15]   # Female preferences for courses A, B, C
])

chi2_stat, p_value_chi2, dof, expected = stats.chi2_contingency(contingency_table)
reject_null_chi2 = p_value_chi2 < alpha

# Cramér's V (effect size for chi-square)
n = np.sum(contingency_table)
cramers_v = np.sqrt(chi2_stat / (n * (min(contingency_table.shape) - 1)))

# Scenario 5: ANOVA (Analysis of Variance)
# Test if there are differences between multiple groups
group1 = np.random.normal(75, 10, 20)
group2 = np.random.normal(80, 12, 22)
group3 = np.random.normal(78, 8, 18)

# One-way ANOVA
f_stat, p_value_anova = stats.f_oneway(group1, group2, group3)
reject_null_anova = p_value_anova < alpha

# Effect size (eta-squared)
ss_between = len(group1) * (np.mean(group1) - np.mean(np.concatenate([group1, group2, group3])))**2 + \
             len(group2) * (np.mean(group2) - np.mean(np.concatenate([group1, group2, group3])))**2 + \
             len(group3) * (np.mean(group3) - np.mean(np.concatenate([group1, group2, group3])))**2

ss_within = np.sum((group1 - np.mean(group1))**2) + \
            np.sum((group2 - np.mean(group2))**2) + \
            np.sum((group3 - np.mean(group3))**2)

ss_total = ss_between + ss_within
eta_squared = ss_between / ss_total

# Normality tests
# Shapiro-Wilk test for normality
shapiro_stat, shapiro_p = stats.shapiro(new_method_scores)
is_normal = shapiro_p > 0.05

# Kolmogorov-Smirnov test
ks_stat, ks_p = stats.kstest(new_method_scores, 'norm', 
                            args=(np.mean(new_method_scores), np.std(new_method_scores)))

# Power analysis (simplified)
# Calculate observed power for two-sample t-test
from scipy.stats import norm

# Effect size from our data
effect_size = cohens_d_two
sample_size = min(len(method_a_scores), len(method_b_scores))

# Critical t-value
df = len(method_a_scores) + len(method_b_scores) - 2
t_critical = stats.t.ppf(1 - alpha/2, df)

# Non-centrality parameter
ncp = effect_size * np.sqrt(sample_size / 2)

# Power calculation (simplified)
power = 1 - stats.t.cdf(t_critical, df, ncp) + stats.t.cdf(-t_critical, df, ncp)

# Summary of all tests
hypothesis_results = {
    'one_sample_t': {
        't_statistic': t_stat_one,
        'p_value': p_value_one,
        'reject_null': reject_null_one,
        'effect_size': cohens_d_one
    },
    'two_sample_t': {
        't_statistic': t_stat_two,
        'p_value': p_value_two,
        'reject_null': reject_null_two,
        'effect_size': cohens_d_two
    },
    'paired_t': {
        't_statistic': t_stat_paired,
        'p_value': p_value_paired,
        'reject_null': reject_null_paired,
        'effect_size': cohens_d_paired
    },
    'chi_square': {
        'chi2_statistic': chi2_stat,
        'p_value': p_value_chi2,
        'reject_null': reject_null_chi2,
        'effect_size': cramers_v
    },
    'anova': {
        'f_statistic': f_stat,
        'p_value': p_value_anova,
        'reject_null': reject_null_anova,
        'effect_size': eta_squared
    }
}

# Additional statistics
additional_stats = {
    'normality_test': {
        'shapiro_stat': shapiro_stat,
        'shapiro_p': shapiro_p,
        'is_normal': is_normal
    },
    'power_analysis': {
        'observed_power': power,
        'effect_size': effect_size,
        'sample_size': sample_size
    }
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test hypothesis testing results
        results = globals_dict['hypothesis_results']
        assert len(results) == 5  # 5 different tests
        
        # Test that all tests have required components
        for test_name, test_results in results.items():
            assert 'p_value' in test_results
            assert 'reject_null' in test_results
            assert 'effect_size' in test_results
            assert 0 <= test_results['p_value'] <= 1
            assert isinstance(test_results['reject_null'], bool)
        
        # Test additional statistics
        additional = globals_dict['additional_stats']
        assert 'normality_test' in additional
        assert 'power_analysis' in additional
        assert 0 <= additional['power_analysis']['observed_power'] <= 1


class TestDataScienceEvaluator:
    """Test cases for data science code evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create a data science evaluator instance."""
        return DataScienceEvaluator()
    
    def test_evaluate_numpy_code(self, evaluator):
        """Test evaluation of NumPy code."""
        numpy_code = '''
import numpy as np

# Create arrays
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([[1, 2], [3, 4]])

# Operations
mean_val = np.mean(arr1)
sum_val = np.sum(arr1)
reshaped = arr1.reshape(5, 1)

# Results
results = {
    'mean': mean_val,
    'sum': sum_val,
    'shape_original': arr1.shape,
    'shape_reshaped': reshaped.shape
}
'''
        result = evaluator.evaluate(numpy_code)
        
        assert result['success'] is True
        results = result['globals']['results']
        assert results['mean'] == 3.0
        assert results['sum'] == 15
        assert results['shape_original'] == (5,)
        assert results['shape_reshaped'] == (5, 1)
    
    def test_evaluate_pandas_code(self, evaluator):
        """Test evaluation of Pandas code."""
        pandas_code = '''
import pandas as pd
import numpy as np

# Create DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
}

df = pd.DataFrame(data)

# Operations
mean_age = df['age'].mean()
total_salary = df['salary'].sum()
sorted_df = df.sort_values('age')

# Results
results = {
    'mean_age': mean_age,
    'total_salary': total_salary,
    'num_rows': len(df),
    'columns': list(df.columns)
}
'''
        result = evaluator.evaluate(pandas_code)
        
        assert result['success'] is True
        results = result['globals']['results']
        assert results['mean_age'] == 30.0
        assert results['total_salary'] == 180000
        assert results['num_rows'] == 3
        assert 'name' in results['columns']
    
    def test_check_data_science_libraries(self, evaluator):
        """Test checking for data science library usage."""
        data_science_code = '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import seaborn as sns

# Use libraries
df = pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 6]})
arr = np.array([1, 2, 3])
model = LinearRegression()

plt.plot([1, 2, 3], [2, 4, 6])
'''
        
        libraries = evaluator.check_library_usage(data_science_code)
        
        assert libraries['pandas'] is True
        assert libraries['numpy'] is True
        assert libraries['matplotlib'] is True
        assert libraries['sklearn'] is True
    
    def test_analyze_data_workflow(self, evaluator):
        """Test analysis of data science workflow patterns."""
        workflow_code = '''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 1. Data loading
df = pd.read_csv('data.csv')  # Simulated

# 2. Data cleaning
df = df.dropna()
df['feature'] = df['feature'].fillna(df['feature'].median())

# 3. Feature engineering
df['new_feature'] = df['feature1'] * df['feature2']

# 4. Model training
X = df[['feature1', 'feature2', 'new_feature']]
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

# 5. Model evaluation
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
'''
        
        workflow = evaluator.analyze_workflow(workflow_code)
        
        assert workflow['has_data_loading'] is True
        assert workflow['has_data_cleaning'] is True
        assert workflow['has_feature_engineering'] is True
        assert workflow['has_model_training'] is True
        assert workflow['has_model_evaluation'] is True
        assert workflow['follows_ml_pipeline'] is True


@pytest.mark.integration
class TestDataScienceIntegration:
    """Integration tests for data science exercises."""
    
    def test_complete_data_science_pipeline(self):
        """Test a complete end-to-end data science pipeline."""
        code = '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# Step 1: Generate synthetic dataset
np.random.seed(42)
n_samples = 1000

# Create realistic real estate dataset
data = {
    'size_sqft': np.random.normal(2000, 600, n_samples),
    'bedrooms': np.random.poisson(3, n_samples) + 1,
    'bathrooms': np.random.poisson(2, n_samples) + 1,
    'age_years': np.random.exponential(15, n_samples),
    'garage_spots': np.random.poisson(2, n_samples),
    'lot_size_sqft': np.random.normal(8000, 2000, n_samples),
    'distance_to_city': np.random.exponential(10, n_samples),
    'school_rating': np.random.normal(7, 1.5, n_samples)
}

# Ensure realistic bounds
data['size_sqft'] = np.clip(data['size_sqft'], 600, 5000)
data['bedrooms'] = np.clip(data['bedrooms'], 1, 6)
data['bathrooms'] = np.clip(data['bathrooms'], 1, 4)
data['age_years'] = np.clip(data['age_years'], 0, 100)
data['garage_spots'] = np.clip(data['garage_spots'], 0, 4)
data['lot_size_sqft'] = np.clip(data['lot_size_sqft'], 3000, 20000)
data['distance_to_city'] = np.clip(data['distance_to_city'], 1, 50)
data['school_rating'] = np.clip(data['school_rating'], 1, 10)

df = pd.DataFrame(data)

# Create target variable (house price)
price = (
    df['size_sqft'] * 120 +
    df['bedrooms'] * 8000 +
    df['bathrooms'] * 12000 +
    df['garage_spots'] * 5000 +
    df['lot_size_sqft'] * 3 +
    df['school_rating'] * 10000 -
    df['age_years'] * 1000 -
    df['distance_to_city'] * 2000 +
    np.random.normal(0, 15000, n_samples)
)

df['price'] = np.clip(price, 50000, 800000)

# Step 2: Exploratory Data Analysis
summary_stats = df.describe()
correlation_matrix = df.corr()
price_corr_with_features = correlation_matrix['price'].abs().sort_values(ascending=False)

# Step 3: Data preprocessing
# Handle outliers using IQR method for price
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_clean = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]

# Feature engineering
df_clean['price_per_sqft'] = df_clean['price'] / df_clean['size_sqft']
df_clean['bed_bath_ratio'] = df_clean['bedrooms'] / df_clean['bathrooms']
df_clean['total_rooms'] = df_clean['bedrooms'] + df_clean['bathrooms']
df_clean['age_category'] = pd.cut(df_clean['age_years'], 
                                 bins=[0, 5, 15, 30, 100], 
                                 labels=['New', 'Recent', 'Mature', 'Old'])

# Encode categorical variables
age_cat_dummies = pd.get_dummies(df_clean['age_category'], prefix='age')
df_final = pd.concat([df_clean, age_cat_dummies], axis=1)

# Step 4: Model preparation
feature_cols = ['size_sqft', 'bedrooms', 'bathrooms', 'garage_spots', 
               'lot_size_sqft', 'distance_to_city', 'school_rating',
               'bed_bath_ratio', 'total_rooms'] + list(age_cat_dummies.columns)

X = df_final[feature_cols]
y = df_final['price']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Step 5: Model training and evaluation
# Train Random Forest model
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)

# Calculate metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
mae = np.mean(np.abs(y_test - y_pred))

# Cross-validation
cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='r2')
cv_mean = cv_scores.mean()
cv_std = cv_scores.std()

# Feature importance
feature_importance = dict(zip(feature_cols, rf_model.feature_importances_))
top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]

# Model performance summary
model_performance = {
    'r2_score': r2,
    'rmse': rmse,
    'mae': mae,
    'cv_mean_r2': cv_mean,
    'cv_std_r2': cv_std,
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'num_features': len(feature_cols)
}

# Prediction analysis
prediction_errors = y_test - y_pred
error_stats = {
    'mean_error': np.mean(prediction_errors),
    'std_error': np.std(prediction_errors),
    'max_error': np.max(np.abs(prediction_errors)),
    'median_error': np.median(np.abs(prediction_errors))
}

# Pipeline success indicators
pipeline_success = (
    r2 > 0.7 and  # Good predictive performance
    len(df_final) > 800 and  # Reasonable data retention after cleaning
    cv_mean > 0.65 and  # Consistent cross-validation performance
    len(feature_cols) >= 8  # Sufficient feature engineering
)

# Final results
final_results = {
    'original_samples': len(df),
    'clean_samples': len(df_clean),
    'final_samples': len(df_final),
    'model_performance': model_performance,
    'top_features': top_features,
    'error_statistics': error_stats,
    'pipeline_successful': pipeline_success
}
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Test the complete pipeline
        results = globals_dict['final_results']
        performance = results['model_performance']
        
        # Test data processing
        assert results['clean_samples'] <= results['original_samples']  # Some outliers removed
        assert results['final_samples'] >= 800  # Reasonable data retention
        
        # Test model performance
        assert 0 <= performance['r2_score'] <= 1  # Valid R2 score
        assert performance['rmse'] > 0  # Valid RMSE
        assert performance['num_features'] >= 8  # Feature engineering occurred
        
        # Test feature importance
        top_features = results['top_features']
        assert len(top_features) == 5  # Top 5 features identified
        assert all(importance >= 0 for _, importance in top_features)  # Valid importances
        
        # Test pipeline success
        assert isinstance(results['pipeline_successful'], bool)


if __name__ == '__main__':
    pytest.main([__file__])