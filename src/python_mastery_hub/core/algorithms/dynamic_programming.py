"""
Dynamic programming algorithms demonstrations for the Algorithms module.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from .base import AlgorithmDemo


class DynamicProgramming(AlgorithmDemo):
    """Demonstration class for dynamic programming algorithms."""
    
    def __init__(self):
        super().__init__("dynamic_programming")
    
    def _setup_examples(self) -> None:
        """Setup dynamic programming examples."""
        self.examples = {
            "fibonacci_dp": {
                "code": '''
def fibonacci_recursive(n):
    """Naive recursive Fibonacci - exponential time complexity."""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

def fibonacci_memoized(n, memo=None):
    """Memoized Fibonacci - linear time complexity."""
    if memo is None:
        memo = {}
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        result = n
    else:
        result = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    
    memo[n] = result
    return result

def fibonacci_tabulation(n):
    """Bottom-up dynamic programming Fibonacci."""
    if n <= 1:
        return n
    
    # Create table to store results
    dp = [0] * (n + 1)
    dp[1] = 1
    
    print(f"Computing Fibonacci({n}) using tabulation:")
    print(f"dp[0] = {dp[0]}, dp[1] = {dp[1]}")
    
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
        print(f"dp[{i}] = dp[{i-1}] + dp[{i-2}] = {dp[i-1]} + {dp[i-2]} = {dp[i]}")
    
    return dp[n]

def fibonacci_optimized(n):
    """Space-optimized dynamic programming Fibonacci."""
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    
    return prev1
''',
                "explanation": "Dynamic programming optimizes recursive problems by storing and reusing previously computed results",
                "time_complexity": "O(n) for DP versions vs O(2^n) for naive recursion",
                "space_complexity": "O(n) for memoization/tabulation, O(1) for optimized"
            },
            
            "longest_common_subsequence": {
                "code": '''
def lcs_recursive(X, Y, m=None, n=None):
    """Naive recursive LCS solution."""
    if m is None:
        m = len(X)
    if n is None:
        n = len(Y)
    
    # Base case
    if m == 0 or n == 0:
        return 0
    
    # If last characters match
    if X[m-1] == Y[n-1]:
        return 1 + lcs_recursive(X, Y, m-1, n-1)
    else:
        # Take maximum of two possibilities
        return max(lcs_recursive(X, Y, m, n-1),
                  lcs_recursive(X, Y, m-1, n))

def lcs_tabulation(X, Y):
    """Bottom-up tabulation LCS solution."""
    m, n = len(X), len(Y)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n], dp

def lcs_with_path(X, Y):
    """LCS with actual subsequence reconstruction."""
    m, n = len(X), len(Y)
    length, dp = lcs_tabulation(X, Y)
    
    # Reconstruct LCS
    lcs = []
    i, j = m, n
    
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    lcs.reverse()
    return length, ''.join(lcs)

# Example usage
X, Y = "AGGTAB", "GXTXAYB"
length, lcs_str = lcs_with_path(X, Y)
print(f"LCS of '{X}' and '{Y}': '{lcs_str}' (length: {length})")
''',
                "explanation": "LCS finds the longest sequence that appears in both strings, useful for diff algorithms and bioinformatics",
                "time_complexity": "O(m*n) for DP vs O(2^max(m,n)) for naive recursion",
                "space_complexity": "O(m*n) for full table, can be optimized to O(min(m,n))"
            },
            
            "coin_change": {
                "code": '''
def coin_change_dp(coins, amount):
    """Dynamic programming solution for coin change problem."""
    # dp[i] represents minimum coins needed for amount i
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # 0 coins needed for amount 0
    
    print(f"Coin change for amount {amount} using coins {coins}")
    print(f"Initial: dp = {dp[:min(10, len(dp))]}...")
    
    for current_amount in range(1, amount + 1):
        for coin in coins:
            if coin <= current_amount:
                dp[current_amount] = min(dp[current_amount], 
                                       dp[current_amount - coin] + 1)
        
        if current_amount <= 10 or current_amount % 10 == 0:
            print(f"dp[{current_amount}] = {dp[current_amount]}")
    
    return dp[amount] if dp[amount] != float('inf') else -1

def coin_change_with_path(coins, amount):
    """Coin change that also returns which coins to use."""
    dp = [float('inf')] * (amount + 1)
    parent = [-1] * (amount + 1)
    dp[0] = 0
    
    for current_amount in range(1, amount + 1):
        for coin in coins:
            if coin <= current_amount and dp[current_amount - coin] + 1 < dp[current_amount]:
                dp[current_amount] = dp[current_amount - coin] + 1
                parent[current_amount] = coin
    
    if dp[amount] == float('inf'):
        return -1, []
    
    # Reconstruct path
    path = []
    current = amount
    while current > 0:
        coin_used = parent[current]
        path.append(coin_used)
        current -= coin_used
    
    return dp[amount], path

# Example usage
coins, amount = [1, 3, 4], 6
min_coins = coin_change_dp(coins, amount)
num_coins, path = coin_change_with_path(coins, amount)
print(f"Minimum coins needed: {min_coins}")
print(f"Coins to use: {path}")
''',
                "explanation": "Coin change finds minimum coins needed to make a target amount, classic DP optimization problem",
                "time_complexity": "O(amount * len(coins))",
                "space_complexity": "O(amount)"
            },
            
            "knapsack_problem": {
                "code": '''
def knapsack_01(weights, values, capacity):
    """0/1 Knapsack problem using dynamic programming."""
    n = len(weights)
    
    # Create DP table
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    print(f"0/1 Knapsack: capacity={capacity}")
    print(f"Items: weights={weights}, values={values}")
    
    # Fill DP table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't include current item
            dp[i][w] = dp[i-1][w]
            
            # Include current item if it fits
            if weights[i-1] <= w:
                include_value = dp[i-1][w - weights[i-1]] + values[i-1]
                dp[i][w] = max(dp[i][w], include_value)
    
    # Reconstruct solution
    max_value = dp[n][capacity]
    items_used = []
    w = capacity
    
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            items_used.append(i-1)
            w -= weights[i-1]
    
    items_used.reverse()
    
    print(f"Maximum value: {max_value}")
    print(f"Items selected: {items_used}")
    print(f"Total weight: {sum(weights[i] for i in items_used)}")
    
    return max_value, items_used

def knapsack_unbounded(weights, values, capacity):
    """Unbounded knapsack problem - unlimited items of each type."""
    dp = [0] * (capacity + 1)
    
    print(f"Unbounded Knapsack: capacity={capacity}")
    
    for w in range(1, capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
        
        if w <= 10 or w % 10 == 0:
            print(f"dp[{w}] = {dp[w]}")
    
    return dp[capacity]

# Example usage
weights = [2, 1, 3, 2]
values = [12, 10, 20, 15]
capacity = 5

max_value, items = knapsack_01(weights, values, capacity)
print(f"\\n0/1 Knapsack result: {max_value}")

unbounded_value = knapsack_unbounded(weights, values, capacity)
print(f"Unbounded Knapsack result: {unbounded_value}")
''',
                "explanation": "Knapsack problems optimize value selection under weight constraints, fundamental in resource allocation",
                "time_complexity": "O(n * capacity) for 0/1, O(len(items) * capacity) for unbounded",
                "space_complexity": "O(n * capacity) for 0/1, O(capacity) for unbounded"
            },
            
            "edit_distance": {
                "code": '''
def edit_distance(str1, str2):
    """Compute minimum edit distance between two strings."""
    m, n = len(str1), len(str2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i  # Delete all characters from str1
    for j in range(n + 1):
        dp[0][j] = j  # Insert all characters to get str2
    
    print(f"Edit distance between '{str1}' and '{str2}'")
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Delete
                    dp[i][j-1],    # Insert
                    dp[i-1][j-1]   # Replace
                )
    
    return dp[m][n]

def edit_distance_with_operations(str1, str2):
    """Compute edit distance and return the sequence of operations."""
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    # Reconstruct operations
    operations = []
    i, j = m, n
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and str1[i-1] == str2[j-1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            operations.append(f"Replace '{str1[i-1]}' with '{str2[j-1]}' at position {i-1}")
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(f"Delete '{str1[i-1]}' at position {i-1}")
            i -= 1
        else:
            operations.append(f"Insert '{str2[j-1]}' at position {i}")
            j -= 1
    
    operations.reverse()
    return dp[m][n], operations

# Example usage
str1, str2 = "kitten", "sitting"
distance = edit_distance(str1, str2)
dist_with_ops, operations = edit_distance_with_operations(str1, str2)

print(f"Edit distance: {distance}")
print("Operations:")
for op in operations:
    print(f"  {op}")
''',
                "explanation": "Edit distance measures similarity between strings, used in spell checkers and DNA analysis",
                "time_complexity": "O(m*n) where m, n are string lengths",
                "space_complexity": "O(m*n) for full table, can be optimized to O(min(m,n))"
            },
            
            "matrix_chain_multiplication": {
                "code": '''
def matrix_chain_order(dimensions):
    """Find optimal parenthesization for matrix chain multiplication."""
    n = len(dimensions) - 1  # Number of matrices
    
    # dp[i][j] = minimum scalar multiplications for matrices i to j
    dp = [[0] * n for _ in range(n)]
    # split[i][j] = optimal split point for matrices i to j
    split = [[0] * n for _ in range(n)]
    
    print(f"Matrix chain with dimensions: {dimensions}")
    print(f"Number of matrices: {n}")
    
    # l is chain length
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            
            # Try all possible split points
            for k in range(i, j):
                cost = (dp[i][k] + dp[k+1][j] + 
                       dimensions[i] * dimensions[k+1] * dimensions[j+1])
                
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    split[i][j] = k
            
            print(f"dp[{i}][{j}] = {dp[i][j]} (split at {split[i][j]})")
    
    return dp[0][n-1], split

def print_optimal_parentheses(split, i, j):
    """Print the optimal parenthesization."""
    if i == j:
        return f"M{i}"
    else:
        return (f"({print_optimal_parentheses(split, i, split[i][j])} × "
                f"{print_optimal_parentheses(split, split[i][j] + 1, j)})")

# Example usage
dims = [40, 20, 30, 10, 30]  # 4 matrices: 40×20, 20×30, 30×10, 10×30
min_cost, split_points = matrix_chain_order(dims)
print(f"\\nMinimum scalar multiplications: {min_cost}")
print(f"Optimal parenthesization: {print_optimal_parentheses(split_points, 0, len(dims)-2)}")
''',
                "explanation": "Matrix chain multiplication finds optimal order to multiply matrices, minimizing scalar operations",
                "time_complexity": "O(n³) where n is number of matrices",
                "space_complexity": "O(n²)"
            },
            
            "longest_increasing_subsequence": {
                "code": '''
def lis_dp(arr):
    """Longest Increasing Subsequence using dynamic programming."""
    n = len(arr)
    if n == 0:
        return 0, []
    
    # dp[i] = length of LIS ending at index i
    dp = [1] * n
    parent = [-1] * n
    
    print(f"Finding LIS in {arr}")
    
    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                parent[i] = j
        print(f"dp[{i}] = {dp[i]} (element: {arr[i]})")
    
    # Find maximum length and its index
    max_length = max(dp)
    max_index = dp.index(max_length)
    
    # Reconstruct LIS
    lis = []
    current = max_index
    while current != -1:
        lis.append(arr[current])
        current = parent[current]
    
    lis.reverse()
    return max_length, lis

def lis_binary_search(arr):
    """Optimized LIS using binary search - O(n log n)."""
    if not arr:
        return 0
    
    # tails[i] = smallest ending element of all increasing subsequences of length i+1
    tails = []
    
    print(f"Finding LIS using binary search in {arr}")
    
    for num in arr:
        # Binary search for the position to replace or append
        left, right = 0, len(tails)
        
        while left < right:
            mid = (left + right) // 2
            if tails[mid] < num:
                left = mid + 1
            else:
                right = mid
        
        # If left == len(tails), append; otherwise replace
        if left == len(tails):
            tails.append(num)
            print(f"Appended {num}: tails = {tails}")
        else:
            tails[left] = num
            print(f"Replaced at position {left} with {num}: tails = {tails}")
    
    return len(tails)

# Example usage
test_array = [10, 9, 2, 5, 3, 7, 101, 18]
length_dp, lis_sequence = lis_dp(test_array)
print(f"\\nLIS length: {length_dp}")
print(f"LIS sequence: {lis_sequence}")

length_bs = lis_binary_search(test_array)
print(f"\\nLIS length (binary search): {length_bs}")
''',
                "explanation": "LIS finds the longest subsequence where elements are in increasing order",
                "time_complexity": "O(n²) for DP, O(n log n) for binary search optimization",
                "space_complexity": "O(n)"
            }
        }
    
    def demonstrate_fibonacci_comparison(self):
        """Compare different Fibonacci implementations."""
        def fibonacci_recursive(n):
            if n <= 1:
                return n
            return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)
        
        def fibonacci_memoized(n, memo=None):
            if memo is None:
                memo = {}
            if n in memo:
                return memo[n]
            if n <= 1:
                result = n
            else:
                result = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
            memo[n] = result
            return result
        
        def fibonacci_tabulation(n):
            if n <= 1:
                return n
            dp = [0] * (n + 1)
            dp[1] = 1
            for i in range(2, n + 1):
                dp[i] = dp[i - 1] + dp[i - 2]
            return dp[n]
        
        def fibonacci_optimized(n):
            if n <= 1:
                return n
            prev2, prev1 = 0, 1
            for i in range(2, n + 1):
                current = prev1 + prev2
                prev2, prev1 = prev1, current
            return prev1
        
        print("=== Fibonacci Performance Comparison ===")
        test_values = [10, 20, 30]
        
        for n in test_values:
            print(f"\nFibonacci({n}):")
            
            # Recursive (only for small n)
            if n <= 30:
                start = time.time()
                result_rec = fibonacci_recursive(n)
                time_rec = (time.time() - start) * 1000
                print(f"  Recursive:   {result_rec:>10} ({time_rec:>6.2f}ms)")
            
            # Memoized
            start = time.time()
            result_memo = fibonacci_memoized(n)
            time_memo = (time.time() - start) * 1000
            print(f"  Memoized:    {result_memo:>10} ({time_memo:>6.2f}ms)")
            
            # Tabulation
            start = time.time()
            result_tab = fibonacci_tabulation(n)
            time_tab = (time.time() - start) * 1000
            print(f"  Tabulation:  {result_tab:>10} ({time_tab:>6.2f}ms)")
            
            # Optimized
            start = time.time()
            result_opt = fibonacci_optimized(n)
            time_opt = (time.time() - start) * 1000
            print(f"  Optimized:   {result_opt:>10} ({time_opt:>6.2f}ms)")
    
    def demonstrate_coin_change_variants(self):
        """Demonstrate different coin change problem variants."""
        def coin_change_ways(coins, amount):
            """Count number of ways to make change."""
            dp = [0] * (amount + 1)
            dp[0] = 1
            
            for coin in coins:
                for i in range(coin, amount + 1):
                    dp[i] += dp[i - coin]
            
            return dp[amount]
        
        print("=== Coin Change Variants ===")
        coins = [1, 2, 5]
        amount = 5
        
        print(f"Coins: {coins}, Amount: {amount}")
        
        # Minimum coins
        dp = [float('inf')] * (amount + 1)
        dp[0] = 0
        for i in range(1, amount + 1):
            for coin in coins:
                if coin <= i:
                    dp[i] = min(dp[i], dp[i - coin] + 1)
        min_coins = dp[amount] if dp[amount] != float('inf') else -1
        
        # Number of ways
        ways = coin_change_ways(coins, amount)
        
        print(f"Minimum coins needed: {min_coins}")
        print(f"Number of ways to make change: {ways}")
    
    def get_complexity_analysis(self) -> Dict[str, Any]:
        """Get complexity analysis for DP problems."""
        return {
            "fibonacci": {
                "recursive": {"time": "O(2^n)", "space": "O(n)"},
                "memoized": {"time": "O(n)", "space": "O(n)"},
                "tabulation": {"time": "O(n)", "space": "O(n)"},
                "optimized": {"time": "O(n)", "space": "O(1)"}
            },
            "lcs": {
                "recursive": {"time": "O(2^(m+n))", "space": "O(m+n)"},
                "dp": {"time": "O(m*n)", "space": "O(m*n)"},
                "space_optimized": {"time": "O(m*n)", "space": "O(min(m,n))"}
            },
            "coin_change": {
                "time": "O(amount * coins)",
                "space": "O(amount)"
            },
            "knapsack_01": {
                "time": "O(n * capacity)",
                "space": "O(n * capacity)"
            },
            "edit_distance": {
                "time": "O(m * n)",
                "space": "O(m * n)"
            }
        }