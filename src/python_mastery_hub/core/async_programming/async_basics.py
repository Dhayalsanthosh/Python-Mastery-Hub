"""
Basic async/await concepts for the async programming module.
"""

import asyncio
import time
from typing import Dict, List, Any
from .base import AsyncDemo, TimingContextManager, AsyncTimingContextManager


class AsyncBasics(AsyncDemo):
    """Demonstrates fundamental async/await concepts."""
    
    def __init__(self):
        super().__init__("Async Basics")
        self._setup_examples()
    
    def _setup_examples(self) -> None:
        """Setup basic async examples."""
        self.examples = {
            "basic_async_await": {
                "code": '''
import asyncio
import time

# Basic async function
async def say_hello(name, delay):
    """Simple async function with delay."""
    print(f"Hello {name}, starting...")
    await asyncio.sleep(delay)  # Non-blocking sleep
    print(f"Hello {name}, finished after {delay}s!")
    return f"Greeted {name}"

# Synchronous version for comparison
def say_hello_sync(name, delay):
    """Synchronous version of the same function."""
    print(f"Hello {name}, starting...")
    time.sleep(delay)  # Blocking sleep
    print(f"Hello {name}, finished after {delay}s!")
    return f"Greeted {name}"

async def async_example():
    """Demonstrate async execution."""
    print("=== Async Execution ===")
    start_time = time.time()
    
    # Run multiple async functions concurrently
    tasks = [
        say_hello("Alice", 1),
        say_hello("Bob", 2),
        say_hello("Charlie", 1.5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"Async total time: {end_time - start_time:.2f}s")
    print(f"Results: {results}")

def sync_example():
    """Demonstrate synchronous execution."""
    print("\\n=== Synchronous Execution ===")
    start_time = time.time()
    
    results = [
        say_hello_sync("Alice", 1),
        say_hello_sync("Bob", 2),
        say_hello_sync("Charlie", 1.5)
    ]
    
    end_time = time.time()
    print(f"Sync total time: {end_time - start_time:.2f}s")
    print(f"Results: {results}")

# Running the examples
if __name__ == "__main__":
    sync_example()
    asyncio.run(async_example())
''',
                "explanation": "Async/await enables concurrent execution of I/O-bound operations, dramatically improving performance",
                "key_concepts": [
                    "async def creates an async function",
                    "await suspends execution until the awaited operation completes",
                    "asyncio.gather() runs multiple async operations concurrently",
                    "asyncio.sleep() is non-blocking unlike time.sleep()"
                ]
            },
            
            "async_context_managers": {
                "code": '''
import asyncio

class AsyncDatabaseConnection:
    """Example async context manager for database connections."""
    
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        print(f"Connecting to database: {self.db_url}")
        await asyncio.sleep(0.1)  # Simulate connection delay
        self.connection = f"Connected to {self.db_url}"
        print("Database connection established")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        print("Closing database connection")
        await asyncio.sleep(0.05)  # Simulate cleanup delay
        self.connection = None
        print("Database connection closed")
        return False  # Don't suppress exceptions
    
    async def execute_query(self, query):
        """Execute a database query."""
        if not self.connection:
            raise RuntimeError("No database connection")
        
        print(f"Executing query: {query}")
        await asyncio.sleep(0.2)  # Simulate query execution
        return f"Query result for: {query}"

async def async_context_example():
    """Demonstrate async context managers."""
    async with AsyncDatabaseConnection("postgresql://localhost/testdb") as db:
        result1 = await db.execute_query("SELECT * FROM users")
        print(f"Result 1: {result1}")
        
        result2 = await db.execute_query("SELECT COUNT(*) FROM orders")
        print(f"Result 2: {result2}")

# Run the example
asyncio.run(async_context_example())
''',
                "explanation": "Async context managers provide powerful patterns for managing resources asynchronously",
                "key_concepts": [
                    "__aenter__ and __aexit__ define async context manager protocol",
                    "async with statement ensures proper resource cleanup",
                    "Useful for database connections, file operations, network resources"
                ]
            },
            
            "error_handling": {
                "code": '''
import asyncio
import random

async def unreliable_operation(operation_id, failure_rate=0.3):
    """Simulate an unreliable async operation."""
    await asyncio.sleep(0.1)  # Simulate work
    
    if random.random() < failure_rate:
        raise ValueError(f"Operation {operation_id} failed!")
    
    return f"Operation {operation_id} succeeded"

async def error_handling_example():
    """Demonstrate error handling in async code."""
    print("=== Error Handling in Async Code ===")
    
    # Method 1: Try/except for individual operations
    try:
        result = await unreliable_operation(1)
        print(f"Success: {result}")
    except ValueError as e:
        print(f"Caught error: {e}")
    
    # Method 2: Handling errors in gather()
    tasks = [unreliable_operation(i) for i in range(2, 6)]
    
    # Option A: return_exceptions=True to collect both results and exceptions
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\\nResults from gather (with exceptions):")
    for i, result in enumerate(results, 2):
        if isinstance(result, Exception):
            print(f"  Operation {i}: ERROR - {result}")
        else:
            print(f"  Operation {i}: SUCCESS - {result}")
    
    # Option B: Handle exceptions individually
    print("\\nHandling tasks individually:")
    tasks = [unreliable_operation(i) for i in range(6, 10)]
    
    for i, task in enumerate(asyncio.as_completed(tasks), 6):
        try:
            result = await task
            print(f"  Operation {i}: SUCCESS - {result}")
        except ValueError as e:
            print(f"  Operation {i}: ERROR - {e}")

# Run the example
asyncio.run(error_handling_example())
''',
                "explanation": "Proper error handling is crucial in async code to prevent task failures from affecting other operations",
                "key_concepts": [
                    "Use try/except blocks around await statements",
                    "gather() with return_exceptions=True collects both results and exceptions",
                    "as_completed() allows handling results as they finish",
                    "Async exceptions can bubble up through the call stack"
                ]
            },
            
            "task_management": {
                "code": '''
import asyncio

async def long_running_task(task_id, duration):
    """Simulate a long-running task."""
    print(f"Task {task_id} starting (duration: {duration}s)")
    
    for i in range(int(duration * 10)):
        await asyncio.sleep(0.1)
        if i % 10 == 0:  # Progress update every second
            print(f"  Task {task_id}: {i/10:.1f}s elapsed")
    
    print(f"Task {task_id} completed!")
    return f"Result from task {task_id}"

async def task_management_example():
    """Demonstrate task creation, cancellation, and management."""
    print("=== Task Management ===")
    
    # Create tasks
    task1 = asyncio.create_task(long_running_task(1, 3))
    task2 = asyncio.create_task(long_running_task(2, 5))
    task3 = asyncio.create_task(long_running_task(3, 2))
    
    # Wait for a short time, then cancel one task
    await asyncio.sleep(1.5)
    print("\\nCancelling task 2...")
    task2.cancel()
    
    # Wait for remaining tasks
    results = await asyncio.gather(task1, task2, task3, return_exceptions=True)
    
    print("\\nTask results:")
    for i, result in enumerate(results, 1):
        if isinstance(result, asyncio.CancelledError):
            print(f"  Task {i}: CANCELLED")
        elif isinstance(result, Exception):
            print(f"  Task {i}: ERROR - {result}")
        else:
            print(f"  Task {i}: SUCCESS - {result}")

async def timeout_example():
    """Demonstrate timeout handling."""
    print("\\n=== Timeout Example ===")
    
    async def slow_operation():
        await asyncio.sleep(3)
        return "Slow operation completed"
    
    try:
        # Wait for operation with 2-second timeout
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
        print(f"Result: {result}")
    except asyncio.TimeoutError:
        print("Operation timed out!")

# Run examples
async def main():
    await task_management_example()
    await timeout_example()

asyncio.run(main())
''',
                "explanation": "Task management allows fine-grained control over async operations including cancellation and timeouts",
                "key_concepts": [
                    "asyncio.create_task() converts coroutines to tasks",
                    "Tasks can be cancelled with .cancel()",
                    "asyncio.wait_for() provides timeout functionality",
                    "CancelledError is raised when tasks are cancelled"
                ]
            }
        }
    
    def get_explanation(self) -> str:
        """Get explanation for async basics."""
        return (
            "Async/await is Python's approach to asynchronous programming, enabling "
            "concurrent execution of I/O-bound operations. Unlike traditional "
            "synchronous code that blocks on I/O operations, async code can "
            "suspend execution and resume when the operation completes, allowing "
            "other code to run in the meantime."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for async programming."""
        return [
            "Use async/await for I/O-bound operations, not CPU-bound tasks",
            "Never use blocking operations (like time.sleep()) in async functions",
            "Always handle exceptions properly in async code",
            "Use asyncio.gather() to run multiple operations concurrently",
            "Prefer async context managers for resource management",
            "Use asyncio.create_task() to convert coroutines to tasks",
            "Implement proper cancellation and timeout handling",
            "Don't mix sync and async code without proper integration",
            "Use asyncio.run() as the main entry point for async programs",
            "Understand the difference between concurrency and parallelism"
        ]
    
    def demonstrate_sync_vs_async(self):
        """Interactive demonstration of sync vs async performance."""
        print("=== Synchronous vs Asynchronous Demonstration ===")
        
        def sync_demo():
            """Synchronous version."""
            start_time = time.time()
            
            # Simulate three I/O operations
            for i in range(3):
                print(f"Sync operation {i+1} starting...")
                time.sleep(1)  # Blocking I/O
                print(f"Sync operation {i+1} completed")
            
            return time.time() - start_time
        
        async def async_demo():
            """Asynchronous version."""
            start_time = time.time()
            
            async def async_operation(op_id):
                print(f"Async operation {op_id} starting...")
                await asyncio.sleep(1)  # Non-blocking I/O
                print(f"Async operation {op_id} completed")
                return f"Result {op_id}"
            
            # Run operations concurrently
            tasks = [async_operation(i+1) for i in range(3)]
            await asyncio.gather(*tasks)
            
            return time.time() - start_time
        
        # Run demonstrations
        sync_time = sync_demo()
        async_time = asyncio.run(async_demo())
        
        print(f"\nResults:")
        print(f"Synchronous time: {sync_time:.2f}s")
        print(f"Asynchronous time: {async_time:.2f}s")
        print(f"Speedup: {sync_time / async_time:.2f}x")
    
    def demonstrate_async_patterns(self):
        """Demonstrate common async patterns."""
        async def pattern_demo():
            print("=== Common Async Patterns ===")
            
            # Pattern 1: Fire and forget
            async def background_task():
                await asyncio.sleep(2)
                print("Background task completed")
            
            print("1. Fire and forget pattern:")
            asyncio.create_task(background_task())  # Don't await
            print("Background task started, continuing...")
            
            # Pattern 2: Timeout with fallback
            print("\n2. Timeout with fallback:")
            
            async def slow_operation():
                await asyncio.sleep(3)
                return "Slow result"
            
            try:
                result = await asyncio.wait_for(slow_operation(), timeout=1.0)
                print(f"Got result: {result}")
            except asyncio.TimeoutError:
                print("Operation timed out, using fallback")
                result = "Fallback result"
            
            # Pattern 3: Processing results as they complete
            print("\n3. Processing as completed:")
            
            async def variable_duration_task(task_id, duration):
                await asyncio.sleep(duration)
                return f"Task {task_id} result"
            
            tasks = [
                variable_duration_task(1, 0.5),
                variable_duration_task(2, 1.0),
                variable_duration_task(3, 0.3),
            ]
            
            for completed_task in asyncio.as_completed(tasks):
                result = await completed_task
                print(f"Completed: {result}")
            
            # Small delay to see background task
            await asyncio.sleep(3)
        
        asyncio.run(pattern_demo())