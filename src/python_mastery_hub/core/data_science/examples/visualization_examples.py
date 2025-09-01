"""
Data visualization examples for the Data Science module.
Covers Matplotlib and Seaborn plotting capabilities.
"""

from typing import Dict, Any


class VisualizationExamples:
    """Data visualization examples and demonstrations."""
    
    @staticmethod
    def get_matplotlib_basics() -> Dict[str, Any]:
        """Get basic Matplotlib plotting examples."""
        return {
            "code": '''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def basic_plots_demo():
    """Demonstrate basic plotting with Matplotlib."""
    print("=== Basic Matplotlib Plots ===")
    
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.exp(-x/5)
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Basic Matplotlib Plots', fontsize=16)
    
    # Line plot
    axes[0, 0].plot(x, y1, label='sin(x)', color='blue', linewidth=2)
    axes[0, 0].plot(x, y2, label='cos(x)', color='red', linestyle='--', linewidth=2)
    axes[0, 0].set_title('Line Plot')
    axes[0, 0].set_xlabel('X values')
    axes[0, 0].set_ylabel('Y values')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Scatter plot
    np.random.seed(42)
    x_scatter = np.random.randn(100)
    y_scatter = 2 * x_scatter + np.random.randn(100)
    axes[0, 1].scatter(x_scatter, y_scatter, alpha=0.6, color='green')
    axes[0, 1].set_title('Scatter Plot')
    axes[0, 1].set_xlabel('X values')
    axes[0, 1].set_ylabel('Y values')
    
    # Bar plot
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    axes[1, 0].bar(categories, values, color=['red', 'blue', 'green', 'orange', 'purple'])
    axes[1, 0].set_title('Bar Plot')
    axes[1, 0].set_xlabel('Categories')
    axes[1, 0].set_ylabel('Values')
    
    # Histogram
    data = np.random.normal(0, 1, 1000)
    axes[1, 1].hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[1, 1].set_title('Histogram')
    axes[1, 1].set_xlabel('Values')
    axes[1, 1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.show()
    
    print("Basic plots created successfully!")

def advanced_visualization_demo():
    """Demonstrate advanced visualization techniques."""
    print("\\n=== Advanced Visualizations ===")
    
    # Create sample dataset
    np.random.seed(42)
    n_samples = 500
    df = pd.DataFrame({
        'x': np.random.randn(n_samples),
        'y': np.random.randn(n_samples),
        'category': np.random.choice(['A', 'B', 'C'], n_samples),
        'size': np.random.randint(20, 200, n_samples),
        'color_val': np.random.randn(n_samples)
    })
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Advanced Visualization Techniques', fontsize=16)
    
    # Bubble plot
    scatter = axes[0, 0].scatter(df['x'], df['y'], s=df['size'], c=df['color_val'], 
                                alpha=0.6, cmap='viridis')
    axes[0, 0].set_title('Bubble Plot')
    axes[0, 0].set_xlabel('X values')
    axes[0, 0].set_ylabel('Y values')
    plt.colorbar(scatter, ax=axes[0, 0])
    
    # Box plot by category
    categories = ['A', 'B', 'C']
    data_by_cat = [df[df['category'] == cat]['y'].values for cat in categories]
    axes[0, 1].boxplot(data_by_cat, labels=categories)
    axes[0, 1].set_title('Box Plot by Category')
    axes[0, 1].set_xlabel('Category')
    axes[0, 1].set_ylabel('Y values')
    
    # Heatmap correlation matrix
    correlation_data = np.random.randn(10, 10)
    correlation_matrix = np.corrcoef(correlation_data)
    im = axes[1, 0].imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
    axes[1, 0].set_title('Correlation Heatmap')
    plt.colorbar(im, ax=axes[1, 0])
    
    # Multiple line plot with error bars
    x_line = np.arange(10)
    y_mean = np.random.randn(10).cumsum()
    y_std = np.random.rand(10)
    
    axes[1, 1].plot(x_line, y_mean, 'b-', label='Mean')
    axes[1, 1].fill_between(x_line, y_mean - y_std, y_mean + y_std, 
                           alpha=0.3, label='±1 std')
    axes[1, 1].set_title('Line Plot with Error Bands')
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('Value')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.show()
    
    print("Advanced visualizations created successfully!")

def seaborn_examples():
    """Demonstrate Seaborn plotting capabilities."""
    print("\\n=== Seaborn Examples ===")
    
    # Load sample dataset
    tips = sns.load_dataset('tips')
    flights = sns.load_dataset('flights')
    
    # Set style
    sns.set_style("whitegrid")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Seaborn Visualization Examples', fontsize=16)
    
    # Distribution plot
    sns.histplot(data=tips, x='total_bill', hue='time', kde=True, ax=axes[0, 0])
    axes[0, 0].set_title('Distribution Plot')
    
    # Violin plot
    sns.violinplot(data=tips, x='day', y='total_bill', ax=axes[0, 1])
    axes[0, 1].set_title('Violin Plot')
    
    # Swarm plot
    sns.swarmplot(data=tips, x='day', y='total_bill', hue='sex', ax=axes[0, 2])
    axes[0, 2].set_title('Swarm Plot')
    axes[0, 2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Regression plot
    sns.regplot(data=tips, x='total_bill', y='tip', ax=axes[1, 0])
    axes[1, 0].set_title('Regression Plot')
    
    # Heatmap
    flights_pivot = flights.pivot(index='month', columns='year', values='passengers')
    sns.heatmap(flights_pivot, annot=True, fmt='d', ax=axes[1, 1])
    axes[1, 1].set_title('Heatmap')
    
    # Pair plot reference
    axes[1, 2].text(0.5, 0.5, 'Pair Plot\\n(see separate figure)', 
                   ha='center', va='center', fontsize=12)
    axes[1, 2].set_xlim(0, 1)
    axes[1, 2].set_ylim(0, 1)
    axes[1, 2].set_title('Pair Plot Reference')
    
    plt.tight_layout()
    plt.show()
    
    # Create pair plot separately
    plt.figure(figsize=(10, 8))
    sns.pairplot(tips, hue='time', diag_kind='kde')
    plt.suptitle('Pair Plot Matrix', y=1.02)
    plt.show()
    
    print("Seaborn examples created successfully!")

# Run all demonstrations
if __name__ == "__main__":
    basic_plots_demo()
    advanced_visualization_demo()
    seaborn_examples()
''',
            "explanation": "Matplotlib and Seaborn provide comprehensive visualization capabilities for data analysis"
        }