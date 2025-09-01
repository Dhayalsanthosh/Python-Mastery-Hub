"""
Longest Common Subsequence (LCS) Exercise - Comprehensive implementation with multiple approaches.
"""

import time
from typing import List, Tuple, Dict, Optional
from ..base import AlgorithmDemo


class LCSExercise(AlgorithmDemo):
    """Comprehensive LCS exercise with multiple implementations and analysis."""
    
    def __init__(self):
        super().__init__("lcs_exercise")
    
    def _setup_examples(self) -> None:
        """Setup LCS exercise examples."""
        self.examples = {
            "recursive_lcs": {
                "code": self._get_recursive_lcs_code(),
                "explanation": "Naive recursive LCS solution with exponential time complexity",
                "time_complexity": "O(2^(m+n)) - exponential",
                "space_complexity": "O(m+n) for recursion stack"
            },
            "memoized_lcs": {
                "code": self._get_memoized_lcs_code(),
                "explanation": "Top-down DP approach using memoization",
                "time_complexity": "O(m*n)",
                "space_complexity": "O(m*n) for memoization table + O(m+n) for recursion"
            },
            "tabulation_lcs": {
                "code": self._get_tabulation_lcs_code(),
                "explanation": "Bottom-up DP approach with full table construction",
                "time_complexity": "O(m*n)",
                "space_complexity": "O(m*n) for DP table"
            },
            "space_optimized_lcs": {
                "code": self._get_space_optimized_lcs_code(),
                "explanation": "Space-optimized DP using only two rows",
                "time_complexity": "O(m*n)",
                "space_complexity": "O(min(m,n))"
            }
        }
    
    def _get_recursive_lcs_code(self) -> str:
        return '''
def lcs_recursive(X, Y, m=None, n=None, depth=0):
    """Naive recursive LCS solution with call tracing."""
    if m is None:
        m = len(X)
    if n is None:
        n = len(Y)
    
    indent = "  " * depth
    print(f"{indent}lcs_recursive('{X[:m]}', '{Y[:n]}', {m}, {n})")
    
    # Base case: if either string is empty
    if m == 0 or n == 0:
        print(f"{indent}  Base case: returning 0")
        return 0
    
    # If last characters match
    if X[m-1] == Y[n-1]:
        print(f"{indent}  Match: '{X[m-1]}' == '{Y[n-1]}'")
        result = 1 + lcs_recursive(X, Y, m-1, n-1, depth + 1)
        print(f"{indent}  Returning {result}")
        return result
    else:
        print(f"{indent}  No match: '{X[m-1]}' != '{Y[n-1]}'")
        # Take maximum of two possibilities
        left = lcs_recursive(X, Y, m, n-1, depth + 1)
        right = lcs_recursive(X, Y, m-1, n, depth + 1)
        result = max(left, right)
        print(f"{indent}  Returning max({left}, {right}) = {result}")
        return result

def count_recursive_calls(X, Y):
    """Count total recursive calls made by naive approach."""
    call_count = [0]
    
    def lcs_with_counter(X, Y, m, n):
        call_count[0] += 1
        
        if m == 0 or n == 0:
            return 0
        
        if X[m-1] == Y[n-1]:
            return 1 + lcs_with_counter(X, Y, m-1, n-1)
        else:
            return max(lcs_with_counter(X, Y, m, n-1),
                      lcs_with_counter(X, Y, m-1, n))
    
    result = lcs_with_counter(X, Y, len(X), len(Y))
    return result, call_count[0]

# Example usage
X, Y = "ABCD", "ACBD"
print(f"Finding LCS of '{X}' and '{Y}':")
result = lcs_recursive(X, Y)
print(f"\\nLCS length: {result}")

length, calls = count_recursive_calls(X, Y)
print(f"Total recursive calls: {calls}")
'''
    
    def _get_memoized_lcs_code(self) -> str:
        return '''
def lcs_memoized(X, Y):
    """LCS using memoization (top-down DP)."""
    m, n = len(X), len(Y)
    memo = {}
    
    def lcs_helper(i, j, depth=0):
        indent = "  " * depth
        print(f"{indent}lcs_helper({i}, {j}) -> '{X[:i]}', '{Y[:j]}'")
        
        # Check if already computed
        if (i, j) in memo:
            print(f"{indent}  Found in memo: {memo[(i, j)]}")
            return memo[(i, j)]
        
        # Base case
        if i == 0 or j == 0:
            result = 0
            print(f"{indent}  Base case: {result}")
        # If characters match
        elif X[i-1] == Y[j-1]:
            print(f"{indent}  Match: '{X[i-1]}' == '{Y[j-1]}'")
            result = 1 + lcs_helper(i-1, j-1, depth + 1)
        else:
            print(f"{indent}  No match: '{X[i-1]}' != '{Y[j-1]}'")
            left = lcs_helper(i, j-1, depth + 1)
            right = lcs_helper(i-1, j, depth + 1)
            result = max(left, right)
            print(f"{indent}  max({left}, {right}) = {result}")
        
        memo[(i, j)] = result
        print(f"{indent}  Stored in memo: ({i}, {j}) = {result}")
        return result
    
    result = lcs_helper(m, n)
    print(f"\\nMemo table size: {len(memo)}")
    print(f"Memo table: {dict(sorted(memo.items()))}")
    return result

def lcs_memoized_with_path(X, Y):
    """LCS with memoization and path reconstruction."""
    m, n = len(X), len(Y)
    memo = {}
    
    def lcs_helper(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        
        if i == 0 or j == 0:
            result = 0
        elif X[i-1] == Y[j-1]:
            result = 1 + lcs_helper(i-1, j-1)
        else:
            result = max(lcs_helper(i, j-1), lcs_helper(i-1, j))
        
        memo[(i, j)] = result
        return result
    
    length = lcs_helper(m, n)
    
    # Reconstruct LCS string
    lcs_str = []
    i, j = m, n
    
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs_str.append(X[i-1])
            i -= 1
            j -= 1
        elif memo.get((i-1, j), 0) > memo.get((i, j-1), 0):
            i -= 1
        else:
            j -= 1
    
    lcs_str.reverse()
    return length, ''.join(lcs_str)

# Example usage
X, Y = "AGGTAB", "GXTXAYB"
print(f"\\nFinding LCS of '{X}' and '{Y}' using memoization:")
length = lcs_memoized(X, Y)
print(f"LCS length: {length}")

length_with_path, lcs_string = lcs_memoized_with_path(X, Y)
print(f"\\nLCS string: '{lcs_string}'")
'''
    
    def _get_tabulation_lcs_code(self) -> str:
        return '''
def lcs_tabulation(X, Y):
    """LCS using bottom-up DP (tabulation)."""
    m, n = len(X), len(Y)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    print(f"Building DP table for '{X}' and '{Y}':")
    print(f"Table dimensions: {m+1} x {n+1}")
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                print(f"dp[{i}][{j}] = dp[{i-1}][{j-1}] + 1 = {dp[i][j]} (match: '{X[i-1]}')")
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                print(f"dp[{i}][{j}] = max(dp[{i-1}][{j}], dp[{i}][{j-1}]) = max({dp[i-1][j]}, {dp[i][j-1]}) = {dp[i][j]}")
    
    # Print DP table
    print(f"\\nFinal DP table:")
    print("    ", end="")
    for char in " " + Y:
        print(f"{char:3}", end="")
    print()
    
    for i in range(m + 1):
        char = " " if i == 0 else X[i-1]
        print(f"{char:3} ", end="")
        for j in range(n + 1):
            print(f"{dp[i][j]:3}", end="")
        print()
    
    return dp[m][n], dp

def lcs_with_path_reconstruction(X, Y):
    """LCS with complete path reconstruction showing all steps."""
    m, n = len(X), len(Y)
    length, dp = lcs_tabulation(X, Y)
    
    print(f"\\nReconstructing LCS from DP table:")
    
    # Reconstruct LCS
    lcs = []
    i, j = m, n
    
    print(f"Starting from dp[{i}][{j}] = {dp[i][j]}")
    
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            print(f"  Match '{X[i-1]}': add to LCS, move to dp[{i-1}][{j-1}]")
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            print(f"  dp[{i-1}][{j}] = {dp[i-1][j]} > dp[{i}][{j-1}] = {dp[i][j-1]}, move up")
            i -= 1
        else:
            print(f"  dp[{i}][{j-1}] = {dp[i][j-1]} >= dp[{i-1}][{j}] = {dp[i-1][j]}, move left")
            j -= 1
    
    lcs.reverse()
    lcs_string = ''.join(lcs)
    
    print(f"\\nLCS: '{lcs_string}' (length: {length})")
    return length, lcs_string

def print_all_lcs(X, Y):
    """Find and print all possible LCS strings."""
    m, n = len(X), len(Y)
    _, dp = lcs_tabulation(X, Y)
    
    def backtrack_all(i, j, current_lcs):
        if i == 0 or j == 0:
            all_lcs.add(current_lcs[::-1])  # Reverse the string
            return
        
        if X[i-1] == Y[j-1]:
            backtrack_all(i-1, j-1, current_lcs + X[i-1])
        else:
            if dp[i-1][j] == dp[i][j]:
                backtrack_all(i-1, j, current_lcs)
            if dp[i][j-1] == dp[i][j]:
                backtrack_all(i, j-1, current_lcs)
    
    all_lcs = set()
    backtrack_all(m, n, "")
    
    print(f"\\nAll possible LCS strings:")
    for lcs_str in sorted(all_lcs):
        print(f"  '{lcs_str}'")
    
    return list(all_lcs)

# Example usage
X, Y = "ABCDGH", "AEDFHR"
print(f"Finding LCS of '{X}' and '{Y}' using tabulation:")
length, dp_table = lcs_tabulation(X, Y)

length_with_path, lcs_string = lcs_with_path_reconstruction(X, Y)

all_lcs = print_all_lcs("ABC", "AC")  # Simpler example for multiple LCS
'''
    
    def _get_space_optimized_lcs_code(self) -> str:
        return '''
def lcs_space_optimized(X, Y):
    """Space-optimized LCS using only two rows."""
    m, n = len(X), len(Y)
    
    # Ensure Y is the shorter string for better space optimization
    if m < n:
        X, Y = Y, X
        m, n = n, m
    
    print(f"Space-optimized LCS for '{X}' and '{Y}':")
    print(f"Using only 2 rows of size {n + 1} instead of {m + 1} x {n + 1}")
    
    # Use only two rows instead of full table
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    
    for i in range(1, m + 1):
        print(f"\\nProcessing X[{i-1}] = '{X[i-1]}':")
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                curr[j] = prev[j-1] + 1
                print(f"  Match with Y[{j-1}] = '{Y[j-1]}': curr[{j}] = {curr[j]}")
            else:
                curr[j] = max(prev[j], curr[j-1])
                print(f"  No match: curr[{j}] = max({prev[j]}, {curr[j-1]}) = {curr[j]}")
        
        print(f"  Row {i}: {curr}")
        
        # Swap rows
        prev, curr = curr, prev
        curr = [0] * (n + 1)  # Reset current row
    
    result = prev[n]
    print(f"\\nLCS length: {result}")
    return result

def lcs_space_optimized_with_path(X, Y):
    """Space-optimized LCS with path reconstruction using divide and conquer."""
    def lcs_length_forward(X, Y):
        """Compute LCS length table from top-left to bottom-right."""
        m, n = len(X), len(Y)
        prev = [0] * (n + 1)
        curr = [0] * (n + 1)
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i-1] == Y[j-1]:
                    curr[j] = prev[j-1] + 1
                else:
                    curr[j] = max(prev[j], curr[j-1])
            prev, curr = curr, [0] * (n + 1)
        
        return prev
    
    def lcs_length_backward(X, Y):
        """Compute LCS length table from bottom-right to top-left."""
        m, n = len(X), len(Y)
        prev = [0] * (n + 1)
        curr = [0] * (n + 1)
        
        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if X[i] == Y[j]:
                    curr[j] = prev[j+1] + 1
                else:
                    curr[j] = max(prev[j], curr[j+1])
            prev, curr = curr, [0] * (n + 1)
        
        return prev
    
    def lcs_divide_conquer(X, Y):
        """Find LCS using divide and conquer with space optimization."""
        m, n = len(X), len(Y)
        
        if m == 0 or n == 0:
            return ""
        
        if m == 1:
            for char in Y:
                if char == X[0]:
                    return X[0]
            return ""
        
        # Divide X in half
        mid = m // 2
        
        # Compute LCS lengths for first and second halves
        left_lengths = lcs_length_forward(X[:mid], Y)
        right_lengths = lcs_length_backward(X[mid:], Y)
        
        # Find optimal split point
        max_length = -1
        split_point = 0
        
        for j in range(n + 1):
            total_length = left_lengths[j] + right_lengths[j]
            if total_length > max_length:
                max_length = total_length
                split_point = j
        
        # Recursively solve subproblems
        left_lcs = lcs_divide_conquer(X[:mid], Y[:split_point])
        right_lcs = lcs_divide_conquer(X[mid:], Y[split_point:])
        
        return left_lcs + right_lcs
    
    result = lcs_divide_conquer(X, Y)
    print(f"Space-optimized LCS with path: '{result}'")
    return result

def compare_space_complexity():
    """Compare space complexity of different approaches."""
    X = "PROGRAMMING"
    Y = "GRAMMARING"
    m, n = len(X), len(Y)
    
    print(f"\\nSpace Complexity Comparison for strings of length {m} and {n}:")
    print(f"1. Full DP table: {(m+1) * (n+1)} integers = {(m+1) * (n+1) * 4} bytes")
    print(f"2. Two rows only: {2 * (n+1)} integers = {2 * (n+1) * 4} bytes")
    print(f"3. Space saving: {((m+1) * (n+1) - 2 * (n+1)) * 4} bytes")
    print(f"4. Percentage saved: {(1 - (2 * (n+1)) / ((m+1) * (n+1))) * 100:.1f}%")

# Example usage
X, Y = "PROGRAMMING", "GRAMMARING"
print(f"Testing space optimization with '{X}' and '{Y}':")

length = lcs_space_optimized(X, Y)
lcs_string = lcs_space_optimized_with_path(X, Y)

compare_space_complexity()
'''
    
    def demonstrate_lcs_performance_analysis(self):
        """Comprehensive performance analysis of different LCS approaches."""
        print("=== LCS Performance Analysis ===")
        
        def time_lcs_function(func, X, Y, *args):
            """Time a specific LCS function."""
            start_time = time.time()
            try:
                result = func(X, Y, *args)
                end_time = time.time()
                return result, (end_time - start_time) * 1000, None
            except Exception as e:
                end_time = time.time()
                return None, (end_time - start_time) * 1000, str(e)
        
        # Test cases with increasing complexity
        test_cases = [
            ("Small", "ABCD", "ACBD"),
            ("Medium", "AGGTAB", "GXTXAYB"),
            ("Longer", "PROGRAMMING", "GRAMMARING"),
            ("Similar", "ABCDEFGHIJ", "ACEGI"),
            ("Very Different", "ABCDEFGHIJ", "KLMNOPQRST")
        ]
        
        approaches = [
            ("Recursive", self._lcs_recursive_simple),
            ("Memoized", self._lcs_memoized_simple),
            ("Tabulation", self._lcs_tabulation_simple),
            ("Space Optimized", self._lcs_space_optimized_simple)
        ]
        
        for case_name, X, Y in test_cases:
            print(f"\n{case_name} case: '{X}' vs '{Y}' (lengths: {len(X)}, {len(Y)})")
            print("-" * 60)
            
            for approach_name, func in approaches:
                # Skip recursive for long strings
                if approach_name == "Recursive" and (len(X) > 8 or len(Y) > 8):
                    print(f"  {approach_name:15s}: Skipped (too slow for long strings)")
                    continue
                
                result, time_ms, error = time_lcs_function(func, X, Y)
                
                if error:
                    print(f"  {approach_name:15s}: Error - {error}")
                else:
                    print(f"  {approach_name:15s}: LCS length = {result:2d}, Time = {time_ms:8.3f}ms")
    
    def _lcs_recursive_simple(self, X, Y):
        """Simple recursive LCS for timing."""
        def lcs_rec(m, n):
            if m == 0 or n == 0:
                return 0
            if X[m-1] == Y[n-1]:
                return 1 + lcs_rec(m-1, n-1)
            return max(lcs_rec(m, n-1), lcs_rec(m-1, n))
        return lcs_rec(len(X), len(Y))
    
    def _lcs_memoized_simple(self, X, Y):
        """Simple memoized LCS for timing."""
        memo = {}
        def lcs_memo(m, n):
            if (m, n) in memo:
                return memo[(m, n)]
            if m == 0 or n == 0:
                result = 0
            elif X[m-1] == Y[n-1]:
                result = 1 + lcs_memo(m-1, n-1)
            else:
                result = max(lcs_memo(m, n-1), lcs_memo(m-1, n))
            memo[(m, n)] = result
            return result
        return lcs_memo(len(X), len(Y))
    
    def _lcs_tabulation_simple(self, X, Y):
        """Simple tabulation LCS for timing."""
        m, n = len(X), len(Y)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i-1] == Y[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _lcs_space_optimized_simple(self, X, Y):
        """Simple space-optimized LCS for timing."""
        m, n = len(X), len(Y)
        prev = [0] * (n + 1)
        curr = [0] * (n + 1)
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i-1] == Y[j-1]:
                    curr[j] = prev[j-1] + 1
                else:
                    curr[j] = max(prev[j], curr[j-1])
            prev, curr = curr, [0] * (n + 1)
        
        return prev[n]
    
    def get_exercise_tasks(self) -> List[str]:
        """Get list of exercise tasks for students."""
        return [
            "Implement naive recursive LCS solution",
            "Add memoization to optimize recursive solution",
            "Implement bottom-up tabulation approach",
            "Add path reconstruction to return actual LCS string",
            "Implement space-optimized version using only two rows",
            "Find and return all possible LCS strings",
            "Compare performance of different approaches",
            "Handle edge cases (empty strings, identical strings)",
            "Implement LCS for multiple strings (3 or more)",
            "Apply LCS to solve related problems (edit distance, diff tools)"
        ]
    
    def get_starter_code(self) -> str:
        """Get starter code template for students."""
        return '''
def lcs_recursive(X, Y, m=None, n=None):
    """
    Find LCS length using naive recursion.
    
    Args:
        X, Y: Input strings
        m, n: Current lengths being considered
    
    Returns:
        Length of LCS
    """
    # TODO: Implement recursive LCS
    pass

def lcs_memoized(X, Y):
    """
    Find LCS length using memoization.
    
    Args:
        X, Y: Input strings
    
    Returns:
        Length of LCS
    """
    # TODO: Implement memoized LCS
    pass

def lcs_tabulation(X, Y):
    """
    Find LCS length using bottom-up DP.
    
    Args:
        X, Y: Input strings
    
    Returns:
        Tuple of (length, dp_table)
    """
    # TODO: Implement tabulation LCS
    pass

def lcs_with_string(X, Y):
    """
    Find LCS and return both length and actual string.
    
    Args:
        X, Y: Input strings
    
    Returns:
        Tuple of (length, lcs_string)
    """
    # TODO: Implement LCS with path reconstruction
    pass

def lcs_space_optimized(X, Y):
    """
    Find LCS length with optimized space complexity.
    
    Args:
        X, Y: Input strings
    
    Returns:
        Length of LCS
    """
    # TODO: Implement space-optimized LCS
    pass

# Test your implementations
if __name__ == "__main__":
    test_cases = [
        ("", ""),
        ("A", ""),
        ("", "B"),
        ("A", "A"),
        ("ABCD", "ACBD"),
        ("AGGTAB", "GXTXAYB"),
        ("PROGRAMMING", "GRAMMARING")
    ]
    
    for X, Y in test_cases:
        print(f"\\nTesting LCS of '{X}' and '{Y}':")
        
        # Test all implementations
        try:
            rec_result = lcs_recursive(X, Y)
            memo_result = lcs_memoized(X, Y)
            tab_result, _ = lcs_tabulation(X, Y)
            space_result = lcs_space_optimized(X, Y)
            
            print(f"  Recursive: {rec_result}")
            print(f"  Memoized: {memo_result}")
            print(f"  Tabulation: {tab_result}")
            print(f"  Space optimized: {space_result}")
            
            # Verify all give same result
            if rec_result == memo_result == tab_result == space_result:
                print("  ✓ All implementations agree")
            else:
                print("  ✗ Implementations disagree!")
                
        except Exception as e:
            print(f"  Error: {e}")
'''
    
    def validate_solution(self, student_lcs_func) -> Tuple[bool, List[str]]:
        """Validate student's LCS implementation."""
        test_cases = [
            ("", "", 0),
            ("A", "", 0),
            ("", "B", 0),
            ("A", "A", 1),
            ("AB", "BA", 1),
            ("ABCD", "ACBD", 3),
            ("AGGTAB", "GXTXAYB", 4),
            ("PROGRAMMING", "GRAMMARING", 7),
            ("ABCDEFG", "HIJKLMN", 0),
            ("AAAA", "AA", 2)
        ]
        
        feedback = []
        all_passed = True
        
        for i, (X, Y, expected) in enumerate(test_cases):
            try:
                result = student_lcs_func(X, Y)
                
                if result == expected:
                    feedback.append(f"✓ Test case {i+1} passed: LCS('{X}', '{Y}') = {result}")
                else:
                    feedback.append(f"✗ Test case {i+1} failed: expected {expected}, got {result}")
                    all_passed = False
                    
            except Exception as e:
                feedback.append(f"✗ Test case {i+1} raised exception: {str(e)}")
                all_passed = False
        
        return all_passed, feedback