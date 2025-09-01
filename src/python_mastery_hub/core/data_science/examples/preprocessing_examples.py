"""
Data preprocessing examples for the Data Science module.
Covers data cleaning, feature scaling, encoding, and dimensionality reduction.
"""

from typing import Dict, Any


class PreprocessingExamples:
    """Data preprocessing examples and demonstrations."""
    
    @staticmethod
    def get_data_preprocessing() -> Dict[str, Any]:
        """Get comprehensive data preprocessing examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

def data_cleaning_demo():
    """Demonstrate data cleaning techniques."""
    print("=== Data Cleaning Demo ===")
    
    # Create messy dataset
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'income': np.random.normal(50000, 20000, n_samples),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
        'experience': np.random.randint(0, 40, n_samples),
        'city': np.random.choice(['New York', 'LA', 'Chicago', 'Houston'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Introduce missing values
    missing_indices = np.random.choice(df.index, size=50, replace=False)
    df.loc[missing_indices[:20], 'income'] = np.nan
    df.loc[missing_indices[20:35], 'education'] = np.nan
    df.loc[missing_indices[35:], 'experience'] = np.nan
    
    # Introduce outliers in income
    outlier_indices = np.random.choice(df.index, size=20, replace=False)
    df.loc[outlier_indices, 'income'] = np.random.uniform(200000, 500000, 20)
    
    print("Original dataset info:")
    print(f"Shape: {df.shape}")
    print(f"Missing values:\\n{df.isnull().sum()}")
    print(f"\\nIncome statistics:")
    print(df['income'].describe())
    
    # Handle missing values
    print("\\n=== Handling Missing Values ===")
    
    # Numerical imputation
    income_median = df['income'].median()
    df['income_filled'] = df['income'].fillna(income_median)
    
    experience_mean = df['experience'].mean()
    df['experience_filled'] = df['experience'].fillna(experience_mean)
    
    # Categorical imputation
    education_mode = df['education'].mode()[0]
    df['education_filled'] = df['education'].fillna(education_mode)
    
    print("After imputation:")
    print(f"Missing values: {df[['income_filled', 'experience_filled', 'education_filled']].isnull().sum().sum()}")
    
    # Outlier detection and handling
    print("\\n=== Outlier Detection ===")
    
    Q1 = df['income_filled'].quantile(0.25)
    Q3 = df['income_filled'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df['income_filled'] < lower_bound) | (df['income_filled'] > upper_bound)]
    print(f"Outliers detected: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")
    
    # Cap outliers
    df['income_capped'] = df['income_filled'].clip(lower=lower_bound, upper=upper_bound)
    
    print(f"Income range after capping: {df['income_capped'].min():.0f} - {df['income_capped'].max():.0f}")

def feature_scaling_demo():
    """Demonstrate feature scaling techniques."""
    print("\\n=== Feature Scaling Demo ===")
    
    # Create sample data with different scales
    np.random.seed(42)
    data = pd.DataFrame({
        'age': np.random.randint(20, 70, 100),
        'income': np.random.normal(50000, 15000, 100),
        'score': np.random.uniform(0, 100, 100),
        'years_exp': np.random.randint(0, 30, 100)
    })
    
    print("Original data statistics:")
    print(data.describe())
    
    # Standard Scaling (Z-score normalization)
    scaler_standard = StandardScaler()
    data_standard = pd.DataFrame(
        scaler_standard.fit_transform(data),
        columns=data.columns
    )
    
    print("\\nAfter Standard Scaling:")
    print(data_standard.describe())
    
    # Min-Max Scaling
    scaler_minmax = MinMaxScaler()
    data_minmax = pd.DataFrame(
        scaler_minmax.fit_transform(data),
        columns=data.columns
    )
    
    print("\\nAfter Min-Max Scaling:")
    print(data_minmax.describe())
    
    # Robust Scaling
    scaler_robust = RobustScaler()
    data_robust = pd.DataFrame(
        scaler_robust.fit_transform(data),
        columns=data.columns
    )
    
    print("\\nAfter Robust Scaling:")
    print(data_robust.describe())

def encoding_demo():
    """Demonstrate categorical encoding techniques."""
    print("\\n=== Categorical Encoding Demo ===")
    
    # Create sample categorical data
    data = pd.DataFrame({
        'education': ['High School', 'Bachelor', 'Master', 'PhD', 'Bachelor', 'High School'],
        'city': ['New York', 'LA', 'Chicago', 'New York', 'LA', 'Chicago'],
        'size': ['Small', 'Medium', 'Large', 'Medium', 'Small', 'Large'],
        'satisfaction': ['Low', 'Medium', 'High', 'Very High', 'Medium', 'Low']
    })
    
    print("Original categorical data:")
    print(data)
    
    # Label Encoding
    print("\\n=== Label Encoding ===")
    le = LabelEncoder()
    data_label = data.copy()
    
    for col in data.columns:
        data_label[f'{col}_label'] = le.fit_transform(data[col])
    
    print(data_label[['education', 'education_label', 'city', 'city_label']])
    
    # One-Hot Encoding
    print("\\n=== One-Hot Encoding ===")
    data_onehot = pd.get_dummies(data, prefix_sep='_')
    print(f"Original columns: {len(data.columns)}")
    print(f"After one-hot encoding: {len(data_onehot.columns)}")
    print("\\nFirst few columns:")
    print(data_onehot.head())
    
    # Ordinal Encoding (for ordered categories)
    print("\\n=== Ordinal Encoding ===")
    education_order = ['High School', 'Bachelor', 'Master', 'PhD']
    satisfaction_order = ['Low', 'Medium', 'High', 'Very High']
    
    ordinal_encoder = OrdinalEncoder(categories=[education_order, satisfaction_order])
    data_ordinal = data[['education', 'satisfaction']].copy()
    data_ordinal[['education_ordinal', 'satisfaction_ordinal']] = ordinal_encoder.fit_transform(
        data[['education', 'satisfaction']]
    )
    
    print(data_ordinal)

def feature_selection_demo():
    """Demonstrate feature selection techniques."""
    print("\\n=== Feature Selection Demo ===")
    
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    
    # Generate dataset with many features
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=5,
        n_redundant=10,
        n_clusters_per_class=1,
        random_state=42
    )
    
    feature_names = [f'feature_{i}' for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    
    print(f"Original dataset shape: {X.shape}")
    
    # Univariate Feature Selection
    print("\\n=== Univariate Feature Selection ===")
    selector = SelectKBest(score_func=f_classif, k=10)
    X_selected = selector.fit_transform(X, y)
    
    selected_features = [feature_names[i] for i in selector.get_support(indices=True)]
    feature_scores = selector.scores_
    
    print(f"Selected {len(selected_features)} features:")
    for feature, score in zip(selected_features, feature_scores[selector.get_support()]):
        print(f"{feature}: {score:.4f}")
    
    # Recursive Feature Elimination
    print("\\n=== Recursive Feature Elimination ===")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rfe = RFE(estimator=rf, n_features_to_select=8)
    X_rfe = rfe.fit_transform(X, y)
    
    rfe_features = [feature_names[i] for i in range(len(feature_names)) if rfe.support_[i]]
    print(f"RFE selected features: {rfe_features}")
    
    # Feature Importance from Random Forest
    print("\\n=== Feature Importance ===")
    rf.fit(X, y)
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("Top 10 most important features:")
    print(importance_df.head(10))

def dimensionality_reduction_demo():
    """Demonstrate dimensionality reduction techniques."""
    print("\\n=== Dimensionality Reduction Demo ===")
    
    from sklearn.datasets import load_digits
    
    # Load digits dataset (64 features)
    digits = load_digits()
    X, y = digits.data, digits.target
    
    print(f"Original dataset shape: {X.shape}")
    print(f"Number of classes: {len(np.unique(y))}")
    
    # PCA
    print("\\n=== Principal Component Analysis ===")
    
    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    
    # Explained variance ratio
    cumsum_var = np.cumsum(pca.explained_variance_ratio_)
    
    # Find number of components for 95% variance
    n_components_95 = np.argmax(cumsum_var >= 0.95) + 1
    print(f"Components needed for 95% variance: {n_components_95}")
    
    # Apply PCA with optimal number of components
    pca_optimal = PCA(n_components=n_components_95)
    X_pca_optimal = pca_optimal.fit_transform(X_scaled)
    
    print(f"Reduced dataset shape: {X_pca_optimal.shape}")
    print(f"Variance explained: {pca_optimal.explained_variance_ratio_.sum():.4f}")
    
    # Show first few principal components
    print("\\nFirst 5 principal components explained variance:")
    for i, var_ratio in enumerate(pca_optimal.explained_variance_ratio_[:5]):
        print(f"PC{i+1}: {var_ratio:.4f}")

# Run all demonstrations
if __name__ == "__main__":
    data_cleaning_demo()
    feature_scaling_demo()
    encoding_demo()
    feature_selection_demo()
    dimensionality_reduction_demo()
''',
            "explanation": "Data preprocessing is crucial for preparing raw data for machine learning algorithms"
        }