"""
Machine learning examples for the Data Science module.
Covers classification, regression, clustering, and model evaluation.
"""

from typing import Dict, Any


class MLExamples:
    """Machine learning examples and demonstrations."""
    
    @staticmethod
    def get_classification_models() -> Dict[str, Any]:
        """Get classification models examples."""
        return {
            "code": '''
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.datasets import make_classification, load_iris

def classification_demo():
    """Demonstrate classification algorithms."""
    print("=== Classification Algorithms Demo ===")
    
    # Generate synthetic dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=5,
        n_redundant=3,
        n_classes=3,
        n_clusters_per_class=1,
        random_state=42
    )
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define models
    models = {
        'Logistic Regression': LogisticRegression(random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(random_state=42),
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5)
    }
    
    # Train and evaluate models
    results = {}
    
    for name, model in models.items():
        print(f"\\n{name}:")
        
        # Use scaled data for SVM and KNN, original for tree-based models
        if name in ['SVM', 'K-Nearest Neighbors', 'Logistic Regression']:
            X_train_model = X_train_scaled
            X_test_model = X_test_scaled
        else:
            X_train_model = X_train
            X_test_model = X_test
        
        # Train model
        model.fit(X_train_model, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_model)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_model, y_train, cv=5)
        
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"CV Mean: {cv_scores.mean():.4f} (±{cv_scores.std()*2:.4f})")
        
        results[name] = {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'predictions': y_pred
        }
    
    # Best model
    best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
    print(f"\\nBest Model: {best_model[0]} (Accuracy: {best_model[1]['accuracy']:.4f})")
    
    return results, X_test, y_test

def model_evaluation_demo():
    """Demonstrate model evaluation techniques."""
    print("\\n=== Model Evaluation Demo ===")
    
    # Load iris dataset for demonstration
    iris = load_iris()
    X, y = iris.data, iris.target
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # Train a Random Forest model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred = rf_model.predict(X_test)
    
    # Detailed evaluation
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))
    
    print("\\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Feature importance
    print("\\nFeature Importance:")
    feature_importance = pd.DataFrame({
        'feature': iris.feature_names,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_importance)
    
    # Cross-validation with different metrics
    print("\\nCross-validation with different metrics:")
    
    # Accuracy
    cv_accuracy = cross_val_score(rf_model, X, y, cv=5, scoring='accuracy')
    print(f"Accuracy: {cv_accuracy.mean():.4f} (±{cv_accuracy.std()*2:.4f})")
    
    # Precision
    cv_precision = cross_val_score(rf_model, X, y, cv=5, scoring='precision_macro')
    print(f"Precision: {cv_precision.mean():.4f} (±{cv_precision.std()*2:.4f})")
    
    # Recall
    cv_recall = cross_val_score(rf_model, X, y, cv=5, scoring='recall_macro')
    print(f"Recall: {cv_recall.mean():.4f} (±{cv_recall.std()*2:.4f})")
    
    # F1-score
    cv_f1 = cross_val_score(rf_model, X, y, cv=5, scoring='f1_macro')
    print(f"F1-score: {cv_f1.mean():.4f} (±{cv_f1.std()*2:.4f})")

def hyperparameter_tuning_demo():
    """Demonstrate hyperparameter tuning."""
    print("\\n=== Hyperparameter Tuning Demo ===")
    
    # Generate dataset
    X, y = make_classification(
        n_samples=500,
        n_features=8,
        n_informative=4,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Random Forest hyperparameter tuning
    print("Random Forest Hyperparameter Tuning:")
    
    rf = RandomForestClassifier(random_state=42)
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        rf, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=0
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Test set performance
    best_model = grid_search.best_estimator_
    test_accuracy = best_model.score(X_test, y_test)
    print(f"Test set accuracy: {test_accuracy:.4f}")
    
    # Compare with default parameters
    default_rf = RandomForestClassifier(random_state=42)
    default_rf.fit(X_train, y_train)
    default_accuracy = default_rf.score(X_test, y_test)
    
    print(f"\\nComparison:")
    print(f"Default Random Forest: {default_accuracy:.4f}")
    print(f"Tuned Random Forest: {test_accuracy:.4f}")
    print(f"Improvement: {test_accuracy - default_accuracy:.4f}")

# Run all demonstrations
if __name__ == "__main__":
    classification_demo()
    model_evaluation_demo()
    hyperparameter_tuning_demo()
''',
            "explanation": "Machine learning provides algorithms for prediction, classification, and pattern discovery"
        }