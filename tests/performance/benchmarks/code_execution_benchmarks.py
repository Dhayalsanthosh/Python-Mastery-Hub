# tests/performance/benchmarks/code_execution_benchmarks.py
"""
Benchmarks for code execution performance in the Python learning platform.
Tests various aspects of code execution including parsing, compilation, 
execution time, and resource usage.
"""
import ast
import compile
import exec
import time
import sys
import io
import contextlib
import tempfile
import subprocess
import threading
import queue
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import concurrent.futures

from .benchmark_runner import BenchmarkRunner, BenchmarkConfig, benchmark, async_benchmark


@dataclass
class CodeExecutionMetrics:
    """Metrics for code execution performance."""
    parse_time: float
    compile_time: float
    execution_time: float
    total_time: float
    memory_peak_mb: float
    output_size_bytes: int
    error_occurred: bool
    error_message: Optional[str] = None


class CodeExecutionBenchmarks:
    """Benchmark suite for code execution performance."""
    
    def __init__(self):
        self.runner = BenchmarkRunner("code_execution_benchmarks")
        self.sample_codes = self._generate_sample_codes()
        
    def _generate_sample_codes(self) -> Dict[str, str]:
        """Generate various sample code snippets for testing."""
        return {
            "hello_world": """
print("Hello, World!")
""",
            "simple_function": """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(10)
print(f"Factorial of 10: {result}")
""",
            "list_comprehension": """
numbers = list(range(1000))
squares = [x**2 for x in numbers if x % 2 == 0]
print(f"Generated {len(squares)} squares")
""",
            "class_definition": """
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

calc = Calculator()
calc.add(5, 3)
calc.multiply(4, 6)
print(f"History: {calc.history}")
""",
            "file_operations": """
import tempfile
import os

# Create temporary file
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("Test data\\n" * 100)
    temp_file = f.name

# Read file
with open(temp_file, 'r') as f:
    content = f.read()

# Clean up
os.unlink(temp_file)
print(f"Processed {len(content)} characters")
""",
            "algorithm_sorting": """
import random

# Generate random data
data = [random.randint(1, 1000) for _ in range(500)]

# Bubble sort implementation
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

sorted_data = bubble_sort(data.copy())
print(f"Sorted {len(sorted_data)} items")
""",
            "recursive_function": """
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 2:
        return 1
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]

result = fibonacci(30)
print(f"Fibonacci(30) = {result}")
""",
            "data_processing": """
import json

# Create sample data
students = []
for i in range(100):
    student = {
        "id": i,
        "name": f"Student{i}",
        "grades": [random.randint(60, 100) for _ in range(5)],
        "average": 0
    }
    student["average"] = sum(student["grades"]) / len(student["grades"])
    students.append(student)

# Process data
high_performers = [s for s in students if s["average"] >= 90]
json_data = json.dumps(students, indent=2)

print(f"Found {len(high_performers)} high performers")
print(f"JSON size: {len(json_data)} characters")
""",
            "error_handling": """
def risky_operation(x):
    try:
        if x < 0:
            raise ValueError("Negative numbers not allowed")
        if x == 0:
            return 1 / x  # This will raise ZeroDivisionError
        return x ** 0.5
    except ValueError as e:
        return f"ValueError: {e}"
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except Exception as e:
        return f"Unexpected error: {e}"

results = []
for i in range(-5, 6):
    result = risky_operation(i)
    results.append(f"{i}: {result}")

for result in results:
    print(result)
""",
            "import_heavy": """
import sys
import os
import json
import re
import math
import random
import collections
import itertools
import functools
from datetime import datetime, timedelta
from pathlib import Path

# Use various imported modules
current_time = datetime.now()
random_numbers = [random.random() for _ in range(50)]
math_result = math.sqrt(sum(random_numbers))
json_data = json.dumps({"timestamp": current_time.isoformat(), "result": math_result})

print(f"Computed result: {math_result}")
print(f"JSON length: {len(json_data)}")
"""
        }
    
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all code execution benchmarks."""
        benchmarks = {
            "parse_performance": (
                BenchmarkConfig("code_parsing", "AST parsing performance", iterations=100),
                self.benchmark_code_parsing,
                (),
                {}
            ),
            "compile_performance": (
                BenchmarkConfig("code_compilation", "Code compilation performance", iterations=50),
                self.benchmark_code_compilation,
                (),
                {}
            ),
            "execution_simple": (
                BenchmarkConfig("simple_execution", "Simple code execution", iterations=50),
                self.benchmark_simple_execution,
                (),
                {}
            ),
            "execution_complex": (
                BenchmarkConfig("complex_execution", "Complex code execution", iterations=20),
                self.benchmark_complex_execution,
                (),
                {}
            ),
            "memory_usage": (
                BenchmarkConfig("memory_usage", "Memory usage during execution", iterations=30, measure_memory=True),
                self.benchmark_memory_usage,
                (),
                {}
            ),
            "concurrent_execution": (
                BenchmarkConfig("concurrent_execution", "Concurrent code execution", iterations=10),
                self.benchmark_concurrent_execution,
                (),
                {}
            ),
            "sandbox_overhead": (
                BenchmarkConfig("sandbox_overhead", "Sandboxed execution overhead", iterations=25),
                self.benchmark_sandbox_overhead,
                (),
                {}
            ),
            "error_handling": (
                BenchmarkConfig("error_handling", "Error handling performance", iterations=40),
                self.benchmark_error_handling,
                (),
                {}
            )
        }
        
        return self.runner.run_benchmark_suite(benchmarks)
    
    @benchmark("code_parsing", iterations=100)
    def benchmark_code_parsing(self):
        """Benchmark AST parsing performance."""
        total_nodes = 0
        
        for code in self.sample_codes.values():
            try:
                tree = ast.parse(code)
                total_nodes += len(list(ast.walk(tree)))
            except SyntaxError:
                pass  # Skip invalid syntax
        
        return total_nodes
    
    @benchmark("code_compilation", iterations=50)
    def benchmark_code_compilation(self):
        """Benchmark code compilation performance."""
        compiled_count = 0
        
        for name, code in self.sample_codes.items():
            try:
                compiled_code = compile(code, f"<{name}>", "exec")
                compiled_count += 1
            except Exception:
                pass  # Skip compilation errors
        
        return compiled_count
    
    @benchmark("simple_execution", iterations=50)
    def benchmark_simple_execution(self):
        """Benchmark simple code execution."""
        simple_codes = ["hello_world", "simple_function", "list_comprehension"]
        results = []
        
        for code_name in simple_codes:
            code = self.sample_codes[code_name]
            result = self._execute_code_safely(code)
            results.append(result)
        
        return len(results)
    
    @benchmark("complex_execution", iterations=20)
    def benchmark_complex_execution(self):
        """Benchmark complex code execution."""
        complex_codes = ["algorithm_sorting", "data_processing", "recursive_function", "import_heavy"]
        results = []
        
        for code_name in complex_codes:
            code = self.sample_codes[code_name]
            result = self._execute_code_safely(code)
            results.append(result)
        
        return len(results)
    
    @benchmark("memory_usage", iterations=30, measure_memory=True)
    def benchmark_memory_usage(self):
        """Benchmark memory usage during code execution."""
        memory_intensive_code = """
# Memory intensive operations
large_list = list(range(100000))
large_dict = {i: str(i) * 10 for i in range(10000)}
matrix = [[j * i for j in range(100)] for i in range(100)]

# Clean up
del large_list
del large_dict
del matrix
"""
        
        result = self._execute_code_safely(memory_intensive_code)
        return result.execution_time if result else 0
    
    @benchmark("concurrent_execution", iterations=10)
    def benchmark_concurrent_execution(self):
        """Benchmark concurrent code execution."""
        concurrent_code = self.sample_codes["list_comprehension"]
        
        def execute_single():
            return self._execute_code_safely(concurrent_code)
        
        # Execute 5 codes concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_single) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return len([r for r in results if r and not r.error_occurred])
    
    @benchmark("sandbox_overhead", iterations=25)
    def benchmark_sandbox_overhead(self):
        """Benchmark overhead of sandboxed execution."""
        test_code = self.sample_codes["simple_function"]
        
        # Direct execution
        start_time = time.perf_counter()
        self._execute_code_directly(test_code)
        direct_time = time.perf_counter() - start_time
        
        # Sandboxed execution
        start_time = time.perf_counter()
        self._execute_code_safely(test_code)
        sandbox_time = time.perf_counter() - start_time
        
        # Return overhead ratio
        return sandbox_time / direct_time if direct_time > 0 else 1.0
    
    @benchmark("error_handling", iterations=40)
    def benchmark_error_handling(self):
        """Benchmark error handling performance."""
        error_codes = [
            "1 / 0",  # ZeroDivisionError
            "undefined_variable",  # NameError
            "int('not_a_number')",  # ValueError
            "import nonexistent_module",  # ImportError
            "[][5]",  # IndexError
        ]
        
        handled_errors = 0
        for code in error_codes:
            result = self._execute_code_safely(code)
            if result and result.error_occurred:
                handled_errors += 1
        
        return handled_errors
    
    def _execute_code_safely(self, code: str) -> Optional[CodeExecutionMetrics]:
        """Execute code safely with metrics collection."""
        start_total = time.perf_counter()
        
        try:
            # Parse phase
            start_parse = time.perf_counter()
            tree = ast.parse(code)
            parse_time = time.perf_counter() - start_parse
            
            # Compile phase
            start_compile = time.perf_counter()
            compiled_code = compile(tree, "<benchmark>", "exec")
            compile_time = time.perf_counter() - start_compile
            
            # Execution phase
            start_exec = time.perf_counter()
            
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Execute with restricted globals
            restricted_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "enumerate": enumerate,
                    "zip": zip,
                }
            }
            
            exec(compiled_code, restricted_globals)
            execution_time = time.perf_counter() - start_exec
            
            # Restore stdout
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            total_time = time.perf_counter() - start_total
            
            return CodeExecutionMetrics(
                parse_time=parse_time,
                compile_time=compile_time,
                execution_time=execution_time,
                total_time=total_time,
                memory_peak_mb=0,  # Would need memory monitoring
                output_size_bytes=len(output.encode('utf-8')),
                error_occurred=False
            )
            
        except Exception as e:
            # Restore stdout if needed
            if 'old_stdout' in locals():
                sys.stdout = old_stdout
            
            total_time = time.perf_counter() - start_total
            
            return CodeExecutionMetrics(
                parse_time=0,
                compile_time=0,
                execution_time=0,
                total_time=total_time,
                memory_peak_mb=0,
                output_size_bytes=0,
                error_occurred=True,
                error_message=str(e)
            )
    
    def _execute_code_directly(self, code: str) -> float:
        """Execute code directly without safety measures."""
        start_time = time.perf_counter()
        
        try:
            # Capture output to prevent printing
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            exec(code)
            
        except Exception:
            pass  # Ignore errors for timing comparison
        finally:
            if 'old_stdout' in locals():
                sys.stdout = old_stdout
        
        return time.perf_counter() - start_time
    
    def benchmark_code_execution_by_complexity(self) -> Dict[str, Any]:
        """Benchmark code execution grouped by complexity."""
        complexity_groups = {
            "trivial": ["hello_world"],
            "simple": ["simple_function", "list_comprehension"],
            "moderate": ["class_definition", "file_operations"],
            "complex": ["algorithm_sorting", "data_processing"],
            "advanced": ["recursive_function", "import_heavy"]
        }
        
        results = {}
        
        for complexity, code_names in complexity_groups.items():
            print(f"Benchmarking {complexity} complexity codes...")
            
            def execute_complexity_group():
                total_time = 0
                success_count = 0
                
                for code_name in code_names:
                    code = self.sample_codes[code_name]
                    result = self._execute_code_safely(code)
                    
                    if result and not result.error_occurred:
                        total_time += result.execution_time
                        success_count += 1
                
                return total_time, success_count
            
            config = BenchmarkConfig(
                name=f"complexity_{complexity}",
                description=f"Execution performance for {complexity} complexity code",
                iterations=20
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_complexity_group)
            )
            
            results[complexity] = benchmark_result
        
        return results
    
    def benchmark_language_features(self) -> Dict[str, Any]:
        """Benchmark specific Python language features."""
        feature_codes = {
            "list_comprehension": "[x**2 for x in range(1000)]",
            "generator_expression": "sum(x**2 for x in range(1000))",
            "lambda_functions": "list(map(lambda x: x**2, range(1000)))",
            "class_instantiation": """
class TestClass:
    def __init__(self, value):
        self.value = value
    def method(self):
        return self.value * 2

objects = [TestClass(i) for i in range(100)]
results = [obj.method() for obj in objects]
""",
            "exception_handling": """
results = []
for i in range(100):
    try:
        if i % 10 == 0:
            raise ValueError("Test error")
        results.append(i * 2)
    except ValueError:
        results.append(-1)
""",
            "string_operations": """
text = "Hello, World! " * 100
words = text.split()
upper_words = [word.upper() for word in words]
joined = " ".join(upper_words)
""",
            "dictionary_operations": """
data = {f"key_{i}": i**2 for i in range(500)}
filtered = {k: v for k, v in data.items() if v % 2 == 0}
values_sum = sum(filtered.values())
"""
        }
        
        results = {}
        
        for feature_name, code in feature_codes.items():
            print(f"Benchmarking {feature_name}...")
            
            def execute_feature():
                result = self._execute_code_safely(code)
                return result.execution_time if result and not result.error_occurred else 0
            
            config = BenchmarkConfig(
                name=f"feature_{feature_name}",
                description=f"Performance of {feature_name}",
                iterations=50
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_feature)
            )
            
            results[feature_name] = benchmark_result
        
        return results
    
    @async_benchmark("async_code_execution", iterations=20)
    async def benchmark_async_code_execution(self):
        """Benchmark asynchronous code execution simulation."""
        async_code = """
import asyncio

async def async_task(n):
    await asyncio.sleep(0.001)  # Simulate async work
    return n * n

async def main():
    tasks = [async_task(i) for i in range(50)]
    results = await asyncio.gather(*tasks)
    return sum(results)

# Note: This would need to be executed in an async context
# For benchmark purposes, we'll simulate the execution time
"""
        
        # Simulate async execution overhead
        await asyncio.sleep(0.001)
        
        result = self._execute_code_safely("result = sum(i*i for i in range(50))")
        return result.execution_time if result else 0


# Standalone benchmark execution
def run_code_execution_benchmarks():
    """Run all code execution benchmarks."""
    benchmarks = CodeExecutionBenchmarks()
    
    print("Running Code Execution Benchmarks")
    print("=" * 50)
    
    # Run main benchmark suite
    results = asyncio.run(benchmarks.run_all_benchmarks())
    
    # Run complexity analysis
    print("\nRunning complexity analysis...")
    complexity_results = benchmarks.benchmark_code_execution_by_complexity()
    
    # Run language features analysis
    print("\nRunning language features analysis...")
    feature_results = benchmarks.benchmark_language_features()
    
    # Generate comprehensive report
    all_results = {**results, **complexity_results, **feature_results}
    
    report = benchmarks.runner.generate_performance_report(
        all_results, 
        "code_execution_benchmark_report.md"
    )
    
    print(f"\nCode execution benchmarks completed!")
    print(f"Total benchmarks run: {len(all_results)}")
    
    return all_results


if __name__ == "__main__":
    run_code_execution_benchmarks()