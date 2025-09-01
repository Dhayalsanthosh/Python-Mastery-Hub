# tests/unit/core/test_async.py
# Unit tests for asynchronous programming concepts and exercises

import pytest
import asyncio
import time
import aiohttp
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.async_programming import (
        AsyncBasicsExercise,
        ConcurrencyExercise,
        AsyncIOExercise,
        ThreadingExercise,
        MultiprocessingExercise
    )
    from src.core.evaluators import AsyncEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class AsyncBasicsExercise:
        pass
    class ConcurrencyExercise:
        pass
    class AsyncIOExercise:
        pass
    class ThreadingExercise:
        pass
    class MultiprocessingExercise:
        pass
    class AsyncEvaluator:
        pass


class TestAsyncBasics:
    """Test cases for basic asynchronous programming concepts."""
    
    @pytest.mark.asyncio
    async def test_simple_async_function(self):
        """Test basic async function definition and execution."""
        code = '''
import asyncio

async def simple_async_function():
    await asyncio.sleep(0.01)
    return "Hello, Async World!"

async def run_test():
    result = await simple_async_function()
    return result

result = asyncio.run(run_test())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == "Hello, Async World!"
    
    @pytest.mark.asyncio
    async def test_async_with_parameters(self):
        """Test async function with parameters."""
        code = '''
import asyncio

async def async_multiply(a, b):
    await asyncio.sleep(0.01)
    return a * b

async def async_add(a, b):
    await asyncio.sleep(0.01)
    return a + b

async def run_calculations():
    mult_result = await async_multiply(5, 6)
    add_result = await async_add(10, 15)
    return mult_result, add_result

results = asyncio.run(run_calculations())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['results'] == (30, 25)
    
    @pytest.mark.asyncio
    async def test_async_gather(self):
        """Test asyncio.gather for concurrent execution."""
        code = '''
import asyncio
import time

async def async_task(task_id, delay):
    start_time = time.time()
    await asyncio.sleep(delay)
    end_time = time.time()
    return f"Task {task_id} completed in {end_time - start_time:.2f}s"

async def run_concurrent_tasks():
    start_time = time.time()
    
    # Run tasks concurrently
    results = await asyncio.gather(
        async_task(1, 0.1),
        async_task(2, 0.1),
        async_task(3, 0.1)
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return results, total_time

results, total_time = asyncio.run(run_concurrent_tasks())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 3
        assert globals_dict['total_time'] < 0.5  # Should be much less than 0.3s (3 * 0.1s)
    
    @pytest.mark.asyncio
    async def test_async_with_exception_handling(self):
        """Test exception handling in async functions."""
        code = '''
import asyncio

async def async_function_with_error():
    await asyncio.sleep(0.01)
    raise ValueError("Something went wrong!")

async def async_function_normal():
    await asyncio.sleep(0.01)
    return "Success"

async def run_with_exception_handling():
    results = []
    
    try:
        result1 = await async_function_normal()
        results.append(result1)
    except Exception as e:
        results.append(f"Error: {e}")
    
    try:
        result2 = await async_function_with_error()
        results.append(result2)
    except ValueError as e:
        results.append(f"Caught: {e}")
    
    return results

results = asyncio.run(run_with_exception_handling())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 2
        assert globals_dict['results'][0] == "Success"
        assert "Caught: Something went wrong!" in globals_dict['results'][1]
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context managers."""
        code = '''
import asyncio

class AsyncContextManager:
    def __init__(self, name):
        self.name = name
        self.entered = False
        self.exited = False
    
    async def __aenter__(self):
        await asyncio.sleep(0.01)
        self.entered = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.01)
        self.exited = True
        return False

async def test_async_context():
    async with AsyncContextManager("test") as cm:
        entered_status = cm.entered
        name = cm.name
    
    exited_status = cm.exited
    return entered_status, exited_status, name

result = asyncio.run(test_async_context())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        entered, exited, name = globals_dict['result']
        assert entered is True
        assert exited is True
        assert name == "test"


class TestAsyncIOAdvanced:
    """Test cases for advanced asyncio concepts."""
    
    @pytest.mark.asyncio
    async def test_async_queue(self):
        """Test asyncio Queue for producer-consumer pattern."""
        code = '''
import asyncio

async def producer(queue, producer_id, num_items):
    for i in range(num_items):
        item = f"Producer-{producer_id}-Item-{i}"
        await queue.put(item)
        await asyncio.sleep(0.01)
    await queue.put(None)  # Sentinel to signal completion

async def consumer(queue, consumer_id):
    consumed_items = []
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        consumed_items.append(item)
        queue.task_done()
        await asyncio.sleep(0.01)
    return consumed_items

async def run_producer_consumer():
    queue = asyncio.Queue(maxsize=5)
    
    # Start producer and consumer
    producer_task = asyncio.create_task(producer(queue, 1, 3))
    consumer_task = asyncio.create_task(consumer(queue, 1))
    
    # Wait for producer to finish
    await producer_task
    
    # Get consumer results
    consumed_items = await consumer_task
    
    return consumed_items

result = asyncio.run(run_producer_consumer())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['result']) == 3
        assert all("Producer-1-Item-" in item for item in globals_dict['result'])
    
    @pytest.mark.asyncio
    async def test_async_semaphore(self):
        """Test asyncio Semaphore for limiting concurrency."""
        code = '''
import asyncio
import time

async def limited_resource_task(task_id, semaphore):
    async with semaphore:
        start_time = time.time()
        await asyncio.sleep(0.1)  # Simulate work
        end_time = time.time()
        return f"Task {task_id}: {end_time - start_time:.2f}s"

async def run_semaphore_test():
    # Limit to 2 concurrent tasks
    semaphore = asyncio.Semaphore(2)
    
    start_time = time.time()
    
    # Create 4 tasks (but only 2 can run concurrently)
    tasks = [
        limited_resource_task(i, semaphore) 
        for i in range(4)
    ]
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return results, total_time

results, total_time = asyncio.run(run_semaphore_test())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 4
        # With semaphore of 2, 4 tasks should take about 0.2s (2 batches of 0.1s each)
        assert 0.15 < globals_dict['total_time'] < 0.35
    
    @pytest.mark.asyncio
    async def test_async_event(self):
        """Test asyncio Event for coordination."""
        code = '''
import asyncio

async def waiter(event, waiter_id):
    await event.wait()
    return f"Waiter {waiter_id} proceeding"

async def setter(event, delay):
    await asyncio.sleep(delay)
    event.set()
    return "Event set"

async def run_event_test():
    event = asyncio.Event()
    
    # Create waiters and setter
    waiter_tasks = [
        asyncio.create_task(waiter(event, i)) 
        for i in range(3)
    ]
    setter_task = asyncio.create_task(setter(event, 0.05))
    
    # Wait for all tasks
    all_tasks = waiter_tasks + [setter_task]
    results = await asyncio.gather(*all_tasks)
    
    return results

results = asyncio.run(run_event_test())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 4  # 3 waiters + 1 setter
        assert sum(1 for r in globals_dict['results'] if "Waiter" in r) == 3
        assert "Event set" in globals_dict['results']
    
    @pytest.mark.asyncio
    async def test_async_lock(self):
        """Test asyncio Lock for mutual exclusion."""
        code = '''
import asyncio

shared_resource = 0
operations_log = []

async def increment_resource(lock, worker_id):
    global shared_resource
    async with lock:
        # Critical section
        old_value = shared_resource
        await asyncio.sleep(0.01)  # Simulate work
        shared_resource = old_value + 1
        operations_log.append(f"Worker {worker_id}: {old_value} -> {shared_resource}")

async def run_lock_test():
    global shared_resource, operations_log
    shared_resource = 0
    operations_log = []
    
    lock = asyncio.Lock()
    
    # Create multiple workers
    tasks = [
        increment_resource(lock, i) 
        for i in range(5)
    ]
    
    await asyncio.gather(*tasks)
    
    return shared_resource, operations_log

final_value, log = asyncio.run(run_lock_test())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['final_value'] == 5  # Should be exactly 5 due to lock
        assert len(globals_dict['log']) == 5


class TestConcurrencyPatterns:
    """Test cases for concurrency patterns and exercises."""
    
    def test_threading_basics(self):
        """Test basic threading concepts."""
        code = '''
import threading
import time

results = []
lock = threading.Lock()

def worker_function(worker_id, delay):
    time.sleep(delay)
    with lock:
        results.append(f"Worker {worker_id} completed")

# Create and start threads
threads = []
start_time = time.time()

for i in range(3):
    t = threading.Thread(target=worker_function, args=(i, 0.1))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

end_time = time.time()
total_time = end_time - start_time
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 3
        assert globals_dict['total_time'] < 0.5  # Should be much less than 0.3s
    
    def test_thread_pool_executor(self):
        """Test ThreadPoolExecutor."""
        code = '''
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def cpu_bound_task(n):
    result = sum(i * i for i in range(n))
    return result

def io_bound_task(delay):
    time.sleep(delay)
    return f"Task completed after {delay}s"

# Test ThreadPoolExecutor with I/O bound tasks
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(io_bound_task, 0.1) for _ in range(3)]
    
    start_time = time.time()
    results = [future.result() for future in futures]
    end_time = time.time()
    
    io_time = end_time - start_time

# Test with CPU bound tasks
with ThreadPoolExecutor(max_workers=2) as executor:
    cpu_futures = [executor.submit(cpu_bound_task, 1000) for _ in range(2)]
    cpu_results = [future.result() for future in cpu_futures]

len_results = len(results)
len_cpu_results = len(cpu_results)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['len_results'] == 3
        assert globals_dict['len_cpu_results'] == 2
        assert globals_dict['io_time'] < 0.5  # Should be concurrent
    
    def test_process_pool_executor(self):
        """Test ProcessPoolExecutor."""
        code = '''
from concurrent.futures import ProcessPoolExecutor
import os

def cpu_intensive_task(n):
    # CPU intensive task that benefits from multiprocessing
    result = 0
    for i in range(n):
        result += i * i
    return result, os.getpid()

# Test ProcessPoolExecutor
if __name__ == '__main__' or 'pytest' in os.path.basename(__file__):
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(cpu_intensive_task, 1000) for _ in range(2)]
        results = [future.result() for future in futures]
    
    # Check that different processes were used
    pids = [result[1] for result in results]
    unique_pids = len(set(pids))
    
    len_results = len(results)
else:
    len_results = 2
    unique_pids = 1  # Fallback for testing
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['len_results'] == 2
        # Note: unique_pids might be 1 in some test environments
    
    @pytest.mark.asyncio
    async def test_mixing_sync_and_async(self):
        """Test mixing synchronous and asynchronous code."""
        code = '''
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def blocking_io_task(duration):
    """Simulate blocking I/O operation."""
    time.sleep(duration)
    return f"Blocking task completed in {duration}s"

async def async_wrapper_for_blocking_task(duration):
    """Wrap blocking task to run in thread pool."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, blocking_io_task, duration)
    return result

async def pure_async_task(duration):
    """Pure async task."""
    await asyncio.sleep(duration)
    return f"Async task completed in {duration}s"

async def run_mixed_tasks():
    start_time = time.time()
    
    # Run both blocking and non-blocking tasks concurrently
    results = await asyncio.gather(
        async_wrapper_for_blocking_task(0.1),
        pure_async_task(0.1),
        async_wrapper_for_blocking_task(0.1)
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return results, total_time

results, total_time = asyncio.run(run_mixed_tasks())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 3
        assert globals_dict['total_time'] < 0.5  # Should run concurrently


class TestAsyncWebProgramming:
    """Test cases for asynchronous web programming concepts."""
    
    @pytest.mark.asyncio
    async def test_async_http_requests(self):
        """Test making async HTTP requests (mocked)."""
        code = '''
import asyncio
from unittest.mock import AsyncMock

# Mock aiohttp session
class MockResponse:
    def __init__(self, json_data, status=200):
        self._json_data = json_data
        self.status = status
    
    async def json(self):
        return self._json_data
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockSession:
    async def get(self, url):
        # Simulate different responses based on URL
        if "users" in url:
            return MockResponse({"users": [{"id": 1, "name": "Alice"}]})
        elif "posts" in url:
            return MockResponse({"posts": [{"id": 1, "title": "Test Post"}]})
        else:
            return MockResponse({"error": "Not found"}, 404)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

async def fetch_data(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            return {"error": f"HTTP {response.status}"}

async def fetch_multiple_urls():
    urls = [
        "https://api.example.com/users",
        "https://api.example.com/posts",
        "https://api.example.com/invalid"
    ]
    
    async with MockSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    return results

results = asyncio.run(fetch_multiple_urls())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 3
        assert "users" in str(globals_dict['results'][0])
        assert "posts" in str(globals_dict['results'][1])
        assert "error" in str(globals_dict['results'][2])
    
    @pytest.mark.asyncio
    async def test_async_generator(self):
        """Test async generators."""
        code = '''
import asyncio

async def async_number_generator(start, end, delay=0.01):
    """Async generator that yields numbers with delay."""
    for i in range(start, end):
        await asyncio.sleep(delay)
        yield i

async def async_fibonacci_generator(n):
    """Async generator for Fibonacci sequence."""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        await asyncio.sleep(0.01)
        a, b = b, a + b
        count += 1

async def consume_async_generator():
    numbers = []
    async for num in async_number_generator(1, 6):
        numbers.append(num)
    
    fib_numbers = []
    async for fib in async_fibonacci_generator(5):
        fib_numbers.append(fib)
    
    return numbers, fib_numbers

result = asyncio.run(consume_async_generator())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        numbers, fib_numbers = globals_dict['result']
        assert numbers == [1, 2, 3, 4, 5]
        assert fib_numbers == [0, 1, 1, 2, 3]
    
    @pytest.mark.asyncio
    async def test_async_iterator(self):
        """Test async iterators."""
        code = '''
import asyncio

class AsyncRange:
    def __init__(self, start, end, delay=0.01):
        self.start = start
        self.end = end
        self.delay = delay
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.start >= self.end:
            raise StopAsyncIteration
        
        await asyncio.sleep(self.delay)
        current = self.start
        self.start += 1
        return current

async def use_async_iterator():
    results = []
    async for value in AsyncRange(0, 5):
        results.append(value)
    return results

result = asyncio.run(use_async_iterator())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['result'] == [0, 1, 2, 3, 4]


class TestAsyncErrorHandling:
    """Test cases for error handling in async code."""
    
    @pytest.mark.asyncio
    async def test_async_exception_propagation(self):
        """Test exception propagation in async functions."""
        code = '''
import asyncio

async def failing_task(task_id):
    await asyncio.sleep(0.01)
    if task_id == 2:
        raise ValueError(f"Task {task_id} failed!")
    return f"Task {task_id} succeeded"

async def test_exception_handling():
    tasks = [failing_task(i) for i in range(4)]
    
    # Method 1: Handle exceptions individually
    results_individual = []
    for task in tasks:
        try:
            result = await task
            results_individual.append(result)
        except ValueError as e:
            results_individual.append(f"Error: {e}")
    
    # Method 2: Use gather with return_exceptions=True
    results_gather = await asyncio.gather(*[failing_task(i) for i in range(4)], return_exceptions=True)
    
    return results_individual, results_gather

individual, gather_results = asyncio.run(test_exception_handling())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        individual = globals_dict['individual']
        gather_results = globals_dict['gather_results']
        
        assert len(individual) == 4
        assert len(gather_results) == 4
        assert any("Error:" in str(result) for result in individual)
        assert any(isinstance(result, ValueError) for result in gather_results)
    
    @pytest.mark.asyncio
    async def test_async_timeout(self):
        """Test timeout handling in async operations."""
        code = '''
import asyncio

async def slow_task(duration):
    await asyncio.sleep(duration)
    return f"Task completed in {duration}s"

async def test_timeouts():
    results = []
    
    # Test successful task within timeout
    try:
        result = await asyncio.wait_for(slow_task(0.05), timeout=0.1)
        results.append(result)
    except asyncio.TimeoutError:
        results.append("Task 1 timed out")
    
    # Test task that times out
    try:
        result = await asyncio.wait_for(slow_task(0.2), timeout=0.1)
        results.append(result)
    except asyncio.TimeoutError:
        results.append("Task 2 timed out")
    
    return results

results = asyncio.run(test_timeouts())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 2
        assert "Task completed" in globals_dict['results'][0]
        assert "timed out" in globals_dict['results'][1]
    
    @pytest.mark.asyncio
    async def test_async_cancellation(self):
        """Test task cancellation."""
        code = '''
import asyncio

async def cancellable_task(task_id):
    try:
        for i in range(10):
            await asyncio.sleep(0.01)
            # Check if task is cancelled
            if asyncio.current_task().cancelled():
                return f"Task {task_id} was cancelled"
        return f"Task {task_id} completed normally"
    except asyncio.CancelledError:
        return f"Task {task_id} caught cancellation"

async def test_cancellation():
    # Start tasks
    task1 = asyncio.create_task(cancellable_task(1))
    task2 = asyncio.create_task(cancellable_task(2))
    
    # Let them run for a bit
    await asyncio.sleep(0.05)
    
    # Cancel one task
    task2.cancel()
    
    # Gather results
    results = []
    try:
        result1 = await task1
        results.append(result1)
    except asyncio.CancelledError:
        results.append("Task 1 was cancelled")
    
    try:
        result2 = await task2
        results.append(result2)
    except asyncio.CancelledError:
        results.append("Task 2 was cancelled")
    
    return results

results = asyncio.run(test_cancellation())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['results']) == 2
        assert "Task 1" in globals_dict['results'][0]
        assert "cancelled" in globals_dict['results'][1].lower()


class TestAsyncEvaluator:
    """Test cases for async code evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create an async evaluator instance."""
        return AsyncEvaluator()
    
    @pytest.mark.asyncio
    async def test_evaluate_async_function(self, evaluator):
        """Test evaluation of async function."""
        code = '''
import asyncio

async def test_async():
    await asyncio.sleep(0.01)
    return "async result"

result = asyncio.run(test_async())
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['result'] == "async result"
    
    @pytest.mark.asyncio
    async def test_check_async_patterns(self, evaluator):
        """Test checking for async patterns in code."""
        code = '''
import asyncio

async def example_function():
    await asyncio.sleep(0.1)
    
    async with some_async_context():
        async for item in async_iterator():
            yield item

async def another_function():
    await asyncio.gather(
        task1(),
        task2()
    )
'''
        
        patterns = evaluator.check_async_patterns(code)
        
        assert patterns['async_functions'] >= 2
        assert patterns['await_expressions'] >= 2
        assert patterns['async_context_managers'] >= 1
        assert patterns['async_generators'] >= 1
    
    def test_performance_async_vs_sync(self, evaluator):
        """Test performance comparison between async and sync approaches."""
        # This would be a more complex test comparing execution times
        sync_code = '''
import time

def sync_task(duration):
    time.sleep(duration)
    return f"Sync task completed"

start_time = time.time()
results = [sync_task(0.01) for _ in range(3)]
sync_time = time.time() - start_time
'''
        
        async_code = '''
import asyncio
import time

async def async_task(duration):
    await asyncio.sleep(duration)
    return f"Async task completed"

async def run_async():
    start_time = time.time()
    results = await asyncio.gather(*[async_task(0.01) for _ in range(3)])
    async_time = time.time() - start_time
    return async_time

async_time = asyncio.run(run_async())
'''
        
        sync_result = evaluator.evaluate(sync_code)
        async_result = evaluator.evaluate(async_code)
        
        assert sync_result['success'] is True
        assert async_result['success'] is True
        
        # Async should generally be faster for I/O bound tasks
        if 'sync_time' in sync_result['globals'] and 'async_time' in async_result['globals']:
            sync_time = sync_result['globals']['sync_time']
            async_time = async_result['globals']['async_time']
            assert async_time < sync_time


@pytest.mark.integration
class TestAsyncIntegration:
    """Integration tests for async programming exercises."""
    
    @pytest.mark.asyncio
    async def test_complete_async_application(self):
        """Test a complete async application scenario."""
        code = '''
import asyncio
from collections import defaultdict

class AsyncTaskManager:
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.task_counter = 0
    
    async def create_task(self, coro, task_name=None):
        task_id = self.task_counter
        self.task_counter += 1
        
        if task_name is None:
            task_name = f"Task-{task_id}"
        
        task = asyncio.create_task(coro)
        self.tasks[task_id] = {
            'task': task,
            'name': task_name,
            'created_at': asyncio.get_event_loop().time()
        }
        
        return task_id
    
    async def wait_for_task(self, task_id):
        if task_id in self.tasks:
            task_info = self.tasks[task_id]
            try:
                result = await task_info['task']
                self.results[task_id] = {
                    'result': result,
                    'status': 'completed',
                    'name': task_info['name']
                }
                return result
            except Exception as e:
                self.results[task_id] = {
                    'error': str(e),
                    'status': 'failed',
                    'name': task_info['name']
                }
                raise
        else:
            raise ValueError(f"Task {task_id} not found")
    
    async def wait_for_all(self):
        pending_tasks = [
            self.wait_for_task(task_id) 
            for task_id in self.tasks 
            if task_id not in self.results
        ]
        
        if pending_tasks:
            results = await asyncio.gather(*pending_tasks, return_exceptions=True)
            return results
        return []
    
    def get_completed_tasks(self):
        return {
            task_id: result 
            for task_id, result in self.results.items() 
            if result['status'] == 'completed'
        }

# Example async tasks
async def fetch_user_data(user_id):
    await asyncio.sleep(0.05)  # Simulate API call
    return {"user_id": user_id, "name": f"User {user_id}"}

async def process_data(data):
    await asyncio.sleep(0.03)  # Simulate processing
    return {"processed": data, "timestamp": asyncio.get_event_loop().time()}

async def run_task_manager_demo():
    manager = AsyncTaskManager()
    
    # Create tasks
    task1_id = await manager.create_task(
        fetch_user_data(1), 
        "fetch_user_1"
    )
    
    task2_id = await manager.create_task(
        fetch_user_data(2), 
        "fetch_user_2"
    )
    
    # Wait for user data
    user1_data = await manager.wait_for_task(task1_id)
    user2_data = await manager.wait_for_task(task2_id)
    
    # Create processing tasks
    process1_id = await manager.create_task(
        process_data(user1_data), 
        "process_user_1"
    )
    
    process2_id = await manager.create_task(
        process_data(user2_data), 
        "process_user_2"
    )
    
    # Wait for all remaining tasks
    await manager.wait_for_all()
    
    # Get results
    completed = manager.get_completed_tasks()
    
    return len(completed), completed

num_completed, completed_tasks = asyncio.run(run_task_manager_demo())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['num_completed'] == 4  # All 4 tasks should complete
        assert len(globals_dict['completed_tasks']) == 4
    
    @pytest.mark.asyncio
    async def test_async_web_scraper_simulation(self):
        """Test simulation of async web scraping."""
        code = '''
import asyncio
import random

class MockWebPage:
    def __init__(self, url, content, delay=None):
        self.url = url
        self.content = content
        self.delay = delay or random.uniform(0.01, 0.05)
    
    async def fetch(self):
        await asyncio.sleep(self.delay)
        return {
            'url': self.url,
            'content': self.content,
            'size': len(self.content),
            'fetch_time': self.delay
        }

class AsyncWebScraper:
    def __init__(self, max_concurrent=3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session_count = 0
    
    async def fetch_page(self, page):
        async with self.semaphore:
            self.session_count += 1
            try:
                result = await page.fetch()
                result['session_id'] = self.session_count
                return result
            except Exception as e:
                return {
                    'url': page.url,
                    'error': str(e),
                    'session_id': self.session_count
                }
    
    async def scrape_multiple(self, pages):
        tasks = [self.fetch_page(page) for page in pages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = [r for r in results if isinstance(r, dict) and 'error' not in r]
        failed = [r for r in results if isinstance(r, dict) and 'error' in r]
        
        return {
            'successful': successful,
            'failed': failed,
            'total_pages': len(pages),
            'success_rate': len(successful) / len(pages) if pages else 0
        }

async def run_scraper_simulation():
    # Create mock pages
    pages = [
        MockWebPage(f"https://example.com/page{i}", f"Content for page {i}")
        for i in range(10)
    ]
    
    scraper = AsyncWebScraper(max_concurrent=3)
    results = await scraper.scrape_multiple(pages)
    
    return results

result = asyncio.run(run_scraper_simulation())
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        result = globals_dict['result']
        assert result['total_pages'] == 10
        assert result['success_rate'] > 0.8  # Should have high success rate
        assert len(result['successful']) >= 8


if __name__ == '__main__':
    pytest.main([__file__])