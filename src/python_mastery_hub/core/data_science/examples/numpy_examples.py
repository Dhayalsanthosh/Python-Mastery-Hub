"""
NumPy examples for the Data Science module.
Covers array operations, mathematical computing, and linear algebra.
"""

from typing import Dict, Any


class NumpyExamples:
    """NumPy examples and demonstrations."""
    
    @staticmethod
    def get_array_operations() -> Dict[str, Any]:
        """Get NumPy array operations examples."""
        return {
            "code": '''
import numpy as np
import time

# Array creation and basic operations
def numpy_basics_demo():
    """Demonstrate NumPy array basics."""
    print("=== NumPy Array Basics ===")
    
    # Creating arrays
    arr1 = np.array([1, 2, 3, 4, 5])
    arr2 = np.array([[1, 2, 3], [4, 5, 6]])
    arr3 = np.zeros((3, 4))
    arr4 = np.ones((2, 3))
    arr5 = np.arange(0, 20, 2)
    arr6 = np.linspace(0, 1, 5)
    
    print(f"1D array: {arr1}")
    print(f"2D array:\\n{arr2}")
    print(f"Zeros array:\\n{arr3}")
    print(f"Ones array:\\n{arr4}")
    print(f"Arange array: {arr5}")
    print(f"Linspace array: {arr6}")
    
    # Array properties
    print(f"\\nArray properties:")
    print(f"Shape: {arr2.shape}")
    print(f"Size: {arr2.size}")
    print(f"Dtype: {arr2.dtype}")
    print(f"Dimensions: {arr2.ndim}")

def array_indexing_demo():
    """Demonstrate array indexing and slicing."""
    print("\\n=== Array Indexing and Slicing ===")
    
    # Create sample array
    arr = np.array([[1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9, 10, 11, 12]])
    
    print(f"Original array:\\n{arr}")
    
    # Basic indexing
    print(f"\\nElement at [1, 2]: {arr[1, 2]}")
    print(f"First row: {arr[0, :]}")
    print(f"Second column: {arr[:, 1]}")
    print(f"Subarray:\\n{arr[1:3, 1:3]}")
    
    # Boolean indexing
    mask = arr > 6
    print(f"\\nBoolean mask (> 6):\\n{mask}")
    print(f"Elements > 6: {arr[mask]}")
    
    # Fancy indexing
    rows = [0, 2]
    cols = [1, 3]
    print(f"Fancy indexing [0,2], [1,3]: {arr[rows, cols]}")

def mathematical_operations_demo():
    """Demonstrate mathematical operations."""
    print("\\n=== Mathematical Operations ===")
    
    # Create sample arrays
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    
    print(f"Array a:\\n{a}")
    print(f"Array b:\\n{b}")
    
    # Element-wise operations
    print(f"\\nElement-wise addition:\\n{a + b}")
    print(f"Element-wise multiplication:\\n{a * b}")
    print(f"Element-wise division:\\n{a / b}")
    print(f"Power operation:\\n{a ** 2}")
    
    # Matrix operations
    print(f"\\nMatrix multiplication:\\n{np.dot(a, b)}")
    print(f"Matrix multiplication (@ operator):\\n{a @ b}")
    
    # Statistical operations
    data = np.random.randn(1000)
    print(f"\\nStatistical operations on random data:")
    print(f"Mean: {np.mean(data):.4f}")
    print(f"Std: {np.std(data):.4f}")
    print(f"Min: {np.min(data):.4f}")
    print(f"Max: {np.max(data):.4f}")
    print(f"Median: {np.median(data):.4f}")

def broadcasting_demo():
    """Demonstrate NumPy broadcasting."""
    print("\\n=== Broadcasting ===")
    
    # Broadcasting examples
    a = np.array([[1, 2, 3],
                  [4, 5, 6]])
    b = np.array([10, 20, 30])
    
    print(f"Array a (2x3):\\n{a}")
    print(f"Array b (3,): {b}")
    print(f"Broadcasting a + b:\\n{a + b}")
    
    # More complex broadcasting
    c = np.array([[1], [2]])
    print(f"\\nArray c (2x1):\\n{c}")
    print(f"Broadcasting a * c:\\n{a * c}")
    
    # Broadcasting with scalar
    print(f"\\nBroadcasting with scalar:")
    print(f"a * 2:\\n{a * 2}")

def performance_comparison_demo():
    """Compare NumPy vs Python list performance."""
    print("\\n=== Performance Comparison ===")
    
    # Create large datasets
    size = 1000000
    python_list = list(range(size))
    numpy_array = np.arange(size)
    
    # Time Python list operations
    start_time = time.time()
    python_result = [x * 2 for x in python_list]
    python_time = time.time() - start_time
    
    # Time NumPy operations
    start_time = time.time()
    numpy_result = numpy_array * 2
    numpy_time = time.time() - start_time
    
    print(f"Dataset size: {size:,}")
    print(f"Python list time: {python_time:.4f} seconds")
    print(f"NumPy array time: {numpy_time:.4f} seconds")
    print(f"NumPy speedup: {python_time / numpy_time:.1f}x faster")

def advanced_operations_demo():
    """Demonstrate advanced NumPy operations."""
    print("\\n=== Advanced Operations ===")
    
    # Array reshaping
    arr = np.arange(12)
    print(f"Original array: {arr}")
    print(f"Reshaped (3x4):\\n{arr.reshape(3, 4)}")
    print(f"Reshaped (2x6):\\n{arr.reshape(2, 6)}")
    
    # Stacking arrays
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    
    print(f"\\nArray a: {a}")
    print(f"Array b: {b}")
    print(f"Vertical stack:\\n{np.vstack([a, b])}")
    print(f"Horizontal stack: {np.hstack([a, b])}")
    
    # Conditional operations
    data = np.random.randn(5, 5)
    print(f"\\nRandom data:\\n{data}")
    print(f"Where data > 0, set to 1, else 0:\\n{np.where(data > 0, 1, 0)}")
    
    # Unique values and sorting
    arr = np.array([3, 1, 4, 1, 5, 9, 2, 6, 5])
    print(f"\\nOriginal: {arr}")
    print(f"Sorted: {np.sort(arr)}")
    print(f"Unique: {np.unique(arr)}")
    print(f"Unique with counts: {np.unique(arr, return_counts=True)}")

# Run all demonstrations
if __name__ == "__main__":
    numpy_basics_demo()
    array_indexing_demo()
    mathematical_operations_demo()
    broadcasting_demo()
    performance_comparison_demo()
    advanced_operations_demo()
''',
            "explanation": "NumPy provides efficient array operations and mathematical functions for numerical computing"
        }
    
    @staticmethod
    def get_linear_algebra() -> Dict[str, Any]:
        """Get NumPy linear algebra examples."""
        return {
            "code": '''
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt

def linear_algebra_demo():
    """Demonstrate linear algebra operations with NumPy."""
    print("=== Linear Algebra with NumPy ===")
    
    # Matrix creation
    A = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 10]])  # Note: made determinant non-zero
    
    b = np.array([1, 2, 3])
    
    print(f"Matrix A:\\n{A}")
    print(f"Vector b: {b}")
    
    # Basic matrix operations
    print(f"\\nMatrix transpose:\\n{A.T}")
    print(f"Matrix determinant: {np.linalg.det(A):.4f}")
    print(f"Matrix trace: {np.trace(A)}")
    
    # Matrix inverse
    try:
        A_inv = np.linalg.inv(A)
        print(f"\\nMatrix inverse:\\n{A_inv}")
        print(f"A @ A_inv (should be identity):\\n{A @ A_inv}")
    except np.linalg.LinAlgError:
        print("\\nMatrix is singular and cannot be inverted")
    
    # Solving linear systems
    x = np.linalg.solve(A, b)
    print(f"\\nSolution to Ax = b: {x}")
    print(f"Verification A @ x = {A @ x}")
    
    # Eigenvalues and eigenvectors
    eigenvals, eigenvecs = np.linalg.eig(A)
    print(f"\\nEigenvalues: {eigenvals}")
    print(f"Eigenvectors:\\n{eigenvecs}")
    
    # Singular Value Decomposition
    U, s, Vt = np.linalg.svd(A)
    print(f"\\nSVD - Singular values: {s}")
    
    # Matrix norms
    print(f"\\nMatrix norms:")
    print(f"Frobenius norm: {np.linalg.norm(A, 'fro'):.4f}")
    print(f"2-norm: {np.linalg.norm(A, 2):.4f}")
    print(f"Infinity norm: {np.linalg.norm(A, np.inf):.4f}")

def least_squares_demo():
    """Demonstrate least squares fitting."""
    print("\\n=== Least Squares Fitting ===")
    
    # Generate sample data with noise
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y_true = 2 * x + 3
    noise = np.random.normal(0, 2, size=x.shape)
    y = y_true + noise
    
    # Set up design matrix for linear regression
    A = np.vstack([x, np.ones(len(x))]).T
    
    # Solve least squares problem
    coeffs, residuals, rank, s = np.linalg.lstsq(A, y, rcond=None)
    
    print(f"True coefficients: slope=2, intercept=3")
    print(f"Fitted coefficients: slope={coeffs[0]:.4f}, intercept={coeffs[1]:.4f}")
    print(f"Residual sum of squares: {residuals[0]:.4f}")
    
    # Calculate R-squared
    y_pred = A @ coeffs
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    print(f"R-squared: {r_squared:.4f}")

def matrix_decomposition_demo():
    """Demonstrate matrix decompositions."""
    print("\\n=== Matrix Decompositions ===")
    
    # Create a symmetric positive definite matrix
    A = np.random.randn(5, 5)
    A = A @ A.T  # This ensures positive definiteness
    
    # Cholesky decomposition
    L = np.linalg.cholesky(A)
    print(f"Cholesky decomposition:")
    print(f"Original matrix A (5x5): shape {A.shape}")
    print(f"Lower triangular L: shape {L.shape}")
    print(f"L @ L.T equals A: {np.allclose(L @ L.T, A)}")
    
    # QR decomposition
    B = np.random.randn(6, 4)
    Q, R = np.linalg.qr(B)
    print(f"\\nQR decomposition:")
    print(f"Original matrix B: shape {B.shape}")
    print(f"Q (orthogonal): shape {Q.shape}")
    print(f"R (upper triangular): shape {R.shape}")
    print(f"Q @ R equals B: {np.allclose(Q @ R, B)}")
    print(f"Q is orthogonal (Q.T @ Q = I): {np.allclose(Q.T @ Q, np.eye(Q.shape[0]))}")
    
    # LU decomposition (using scipy)
    try:
        from scipy.linalg import lu
        P, L, U = lu(A)
        print(f"\\nLU decomposition:")
        print(f"P @ L @ U equals A: {np.allclose(P @ L @ U, A)}")
    except ImportError:
        print("\\nSciPy not available for LU decomposition")

# Run demonstrations
if __name__ == "__main__":
    linear_algebra_demo()
    least_squares_demo()
    matrix_decomposition_demo()
''',
            "explanation": "NumPy provides comprehensive linear algebra operations for scientific computing"
        }