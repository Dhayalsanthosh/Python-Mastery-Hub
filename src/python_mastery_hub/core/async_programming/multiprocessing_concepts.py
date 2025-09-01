"""
Multiprocessing concepts for the async programming module.
"""

import multiprocessing as mp
import time
import os
from typing import Dict, List, Any, Optional
from concurrent.futures import ProcessPoolExecutor
from .base import AsyncDemo, simulate_cpu_work


class MultiprocessingConcepts(AsyncDemo):
    """Demonstrates multiprocessing concepts and parallelism."""
    
    def __init__(self):
        super().__init__("Multiprocessing Concepts")
        self._setup_examples()
    
    def _setup_examples(self) -> None:
        """Setup multiprocessing examples."""
        self.examples = {
            "cpu_intensive_parallel": {
                "code": '''
import multiprocessing as mp
import time
import os
from concurrent.futures import ProcessPoolExecutor

def cpu_intensive_task(n):
    """CPU-intensive task that benefits from multiprocessing."""
    start = time.time()
    result = sum(i * i for i in range(n))
    duration = time.time() - start
    process_id = os.getpid()
    return f"Process {process_id}: n={n}, result={result}, time={duration:.3f}s"

def multiprocessing_vs_sequential():
    """Compare multiprocessing vs sequential execution."""
    print("=== Multiprocessing vs Sequential Comparison ===")
    
    # Test data
    test_values = [500000, 600000, 700000, 800000]
    
    # Sequential execution
    print("Sequential execution:")
    start_time = time.time()
    sequential_results = []
    for n in test_values:
        result = cpu_intensive_task(n)
        sequential_results.append(result)
        print(f"  {result}")
    sequential_time = time.time() - start_time
    
    print(f"Sequential total time: {sequential_time:.3f}s")
    
    # Multiprocessing execution
    print(f"\\nMultiprocessing execution (using {mp.cpu_count()} cores):")
    start_time = time.time()
    
    with ProcessPoolExecutor() as executor:
        multiprocessing_results = list(executor.map(cpu_intensive_task, test_values))
    
    multiprocessing_time = time.time() - start_time
    
    for result in multiprocessing_results:
        print(f"  {result}")
    
    print(f"Multiprocessing total time: {multiprocessing_time:.3f}s")
    print(f"Speedup: {sequential_time / multiprocessing_time:.2f}x")

if __name__ == "__main__":
    multiprocessing_vs_sequential()
''',
                "explanation": "Multiprocessing enables true parallelism for CPU-bound tasks by utilizing multiple CPU cores"
            },
            
            "process_communication": {
                "code": '''
import multiprocessing as mp
import time
import os

def process_communication_example():
    """Demonstrate inter-process communication with Queue."""
    print("=== Process Communication with Queue ===")
    
    def producer(queue, producer_id, num_items):
        """Producer process that adds items to queue."""
        for i in range(num_items):
            item = f"Item-{producer_id}-{i}"
            queue.put(item)
            print(f"Producer {producer_id} (PID {os.getpid()}) produced: {item}")
            time.sleep(0.1)
        
        queue.put(None)  # Sentinel value
        print(f"Producer {producer_id} finished")
    
    def consumer(queue, consumer_id):
        """Consumer process that processes items from queue."""
        processed = 0
        while True:
            item = queue.get()
            if item is None:
                break
            
            print(f"Consumer {consumer_id} (PID {os.getpid()}) processing: {item}")
            time.sleep(0.2)
            processed += 1
        
        print(f"Consumer {consumer_id} processed {processed} items")
    
    # Create queue for inter-process communication
    queue = mp.Queue()
    
    # Create and start processes
    processes = []
    
    # Start producer process
    producer_process = mp.Process(target=producer, args=(queue, 1, 5))
    processes.append(producer_process)
    producer_process.start()
    
    # Start consumer process
    consumer_process = mp.Process(target=consumer, args=(queue, 1))
    processes.append(consumer_process)
    consumer_process.start()
    
    # Wait for all processes to complete
    for process in processes:
        process.join()

if __name__ == "__main__":
    process_communication_example()
''',
                "explanation": "Inter-process communication allows processes to share data safely and efficiently"
            },
            
            "shared_memory": {
                "code": '''
import multiprocessing as mp
import time
import random

def shared_memory_example():
    """Demonstrate shared memory between processes."""
    print("=== Shared Memory Example ===")
    
    def worker(shared_array, shared_value, worker_id, lock):
        """Worker process that modifies shared data."""
        for i in range(5):
            # Acquire lock before modifying shared data
            with lock:
                # Modify shared array
                index = worker_id * 5 + i
                if index < len(shared_array):
                    old_value = shared_array[index]
                    shared_array[index] = random.randint(1, 100)
                    print(f"Worker {worker_id}: array[{index}] = {old_value} -> {shared_array[index]}")
                
                # Modify shared value
                old_shared = shared_value.value
                shared_value.value += 1
                print(f"Worker {worker_id}: shared_value = {old_shared} -> {shared_value.value}")
            
            time.sleep(0.1)
    
    # Create shared memory objects
    shared_array = mp.Array('i', [0] * 20)  # Array of integers
    shared_value = mp.Value('i', 0)  # Single integer value
    lock = mp.Lock()
    
    print(f"Initial shared array: {list(shared_array[:])}")
    print(f"Initial shared value: {shared_value.value}")
    
    # Create and start worker processes
    processes = []
    for i in range(4):
        process = mp.Process(target=worker, args=(shared_array, shared_value, i, lock))
        processes.append(process)
        process.start()
    
    # Wait for all processes to complete
    for process in processes:
        process.join()
    
    print(f"\\nFinal shared array: {list(shared_array[:])}")
    print(f"Final shared value: {shared_value.value}")

if __name__ == "__main__":
    shared_memory_example()
''',
                "explanation": "Shared memory enables efficient data sharing between processes"
            },
            
            "process_pool": {
                "code": '''
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import random

def heavy_computation(n):
    """Simulate heavy computational work."""
    start_time = time.time()
    
    # Perform actual computation
    result = 0
    for i in range(n):
        result += i ** 2
        if i % 100000 == 0:
            # Simulate some complexity
            result = result % 1000000
    
    duration = time.time() - start_time
    return {
        'input': n,
        'result': result,
        'duration': duration,
        'process_id': mp.current_process().pid
    }

def process_pool_example():
    """Demonstrate process pool execution."""
    print("=== Process Pool Example ===")
    
    # Generate test data
    test_inputs = [random.randint(500000, 1000000) for _ in range(8)]
    
    print(f"Processing {len(test_inputs)} tasks...")
    print(f"Available CPU cores: {mp.cpu_count()}")
    
    start_time = time.time()
    
    # Method 1: Using ProcessPoolExecutor with map
    print("\\n--- Using ProcessPoolExecutor.map() ---")
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        results = list(executor.map(heavy_computation, test_inputs))
    
    for result in results:
        print(f"Process {result['process_id']}: input={result['input']}, "
              f"result={result['result']}, time={result['duration']:.3f}s")
    
    pool_time = time.time() - start_time
    print(f"Total time with process pool: {pool_time:.3f}s")
    
    # Method 2: Processing results as they complete
    print("\\n--- Processing as completed ---")
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # Submit all tasks
        future_to_input = {executor.submit(heavy_computation, n): n for n in test_inputs}
        
        # Process results as they complete
        completed_count = 0
        for future in as_completed(future_to_input):
            input_value = future_to_input[future]
            try:
                result = future.result()
                completed_count += 1
                print(f"Completed {completed_count}/{len(test_inputs)}: "
                      f"input={input_value}, process={result['process_id']}")
            except Exception as e:
                print(f"Task with input {input_value} failed: {e}")
    
    as_completed_time = time.time() - start_time
    print(f"Total time with as_completed: {as_completed_time:.3f}s")
    
    # Sequential comparison
    print("\\n--- Sequential execution (for comparison) ---")
    start_time = time.time()
    
    sequential_results = [heavy_computation(n) for n in test_inputs[:4]]  # Only do 4 for time
    
    sequential_time = time.time() - start_time
    print(f"Sequential time (4 tasks): {sequential_time:.3f}s")
    
    # Calculate theoretical speedup
    estimated_sequential_full = sequential_time * (len(test_inputs) / 4)
    speedup = estimated_sequential_full / pool_time
    print(f"\\nEstimated speedup: {speedup:.2f}x")

if __name__ == "__main__":
    process_pool_example()
''',
                "explanation": "Process pools provide efficient management of worker processes for parallel execution"
            },
            
            "data_parallelism": {
                "code": '''
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time
import random

def process_data_chunk(chunk_data):
    """Process a chunk of data in parallel."""
    chunk_id, data = chunk_data
    
    print(f"Process {mp.current_process().pid} processing chunk {chunk_id} "
          f"({len(data)} items)")
    
    # Simulate data processing
    processed_results = []
    for item in data:
        # Simulate some computation
        result = item ** 2 + random.randint(1, 10)
        processed_results.append(result)
        
        # Add some processing delay
        time.sleep(0.001)
    
    print(f"Process {mp.current_process().pid} completed chunk {chunk_id}")
    
    return {
        'chunk_id': chunk_id,
        'original_size': len(data),
        'processed_size': len(processed_results),
        'results': processed_results,
        'process_id': mp.current_process().pid
    }

def data_parallelism_example():
    """Demonstrate data parallelism with large datasets."""
    print("=== Data Parallelism Example ===")
    
    # Generate large dataset
    dataset_size = 10000
    dataset = [random.randint(1, 1000) for _ in range(dataset_size)]
    
    # Split data into chunks for parallel processing
    num_processes = mp.cpu_count()
    chunk_size = len(dataset) // num_processes
    
    chunks = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        if i == num_processes - 1:  # Last chunk gets remaining items
            end_idx = len(dataset)
        else:
            end_idx = start_idx + chunk_size
        
        chunk_data = dataset[start_idx:end_idx]
        chunks.append((i, chunk_data))
    
    print(f"Dataset size: {dataset_size}")
    print(f"Number of processes: {num_processes}")
    print(f"Chunk sizes: {[len(chunk[1]) for chunk in chunks]}")
    
    # Parallel processing
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        chunk_results = list(executor.map(process_data_chunk, chunks))
    
    parallel_time = time.time() - start_time
    
    # Combine results
    all_results = []
    for chunk_result in sorted(chunk_results, key=lambda x: x['chunk_id']):
        all_results.extend(chunk_result['results'])
    
    print(f"\\nParallel processing completed in {parallel_time:.3f}s")
    print(f"Processed {len(all_results)} items")
    
    # Sequential processing comparison (with smaller dataset for time)
    small_dataset = dataset[:1000]  # Use smaller dataset for comparison
    
    start_time = time.time()
    sequential_results = []
    for item in small_dataset:
        result = item ** 2 + random.randint(1, 10)
        sequential_results.append(result)
        time.sleep(0.001)
    
    sequential_time = time.time() - start_time
    
    # Estimate full sequential time
    estimated_full_sequential = sequential_time * (dataset_size / len(small_dataset))
    
    print(f"\\nSequential processing (1000 items): {sequential_time:.3f}s")
    print(f"Estimated full sequential time: {estimated_full_sequential:.3f}s")
    print(f"Speedup: {estimated_full_sequential / parallel_time:.2f}x")
    
    # Show process distribution
    print(f"\\nProcess distribution:")
    for result in chunk_results:
        print(f"  Chunk {result['chunk_id']}: Process {result['process_id']} "
              f"({result['processed_size']} items)")

if __name__ == "__main__":
    data_parallelism_example()
''',
                "explanation": "Data parallelism divides large datasets across multiple processes for efficient parallel processing"
            }
        }
    
    def get_explanation(self) -> str:
        """Get explanation for multiprocessing concepts."""
        return (
            "Multiprocessing in Python creates separate processes that run "
            "independently with their own memory space. This enables true "
            "parallelism for CPU-bound tasks by utilizing multiple CPU cores, "
            "bypassing the Global Interpreter Lock (GIL) limitation."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for multiprocessing."""
        return [
            "Use multiprocessing for CPU-bound tasks that can be parallelized",
            "Minimize data transfer between processes to reduce overhead",
            "Use ProcessPoolExecutor for simple parallel task execution",
            "Be aware of pickling limitations for inter-process communication",
            "Use shared memory objects for large data that needs to be shared",
            "Always handle process exceptions and implement proper cleanup",
            "Consider memory usage - each process has its own memory space",
            "Use locks when accessing shared resources between processes",
            "Profile your code to ensure multiprocessing provides real benefits",
            "Be mindful of process startup overhead for short-running tasks"
        ]


def cpu_intensive_benchmark():
    """Benchmark CPU-intensive tasks across different approaches."""
    
    def fibonacci(n):
        """CPU-intensive Fibonacci calculation."""
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    def matrix_multiply(size):
        """CPU-intensive matrix multiplication."""
        import random
        
        # Create two random matrices
        matrix_a = [[random.random() for _ in range(size)] for _ in range(size)]
        matrix_b = [[random.random() for _ in range(size)] for _ in range(size)]
        
        # Multiply matrices
        result = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]
        
        return result
    
    # Test different approaches
    test_sizes = [50, 60, 70, 80]
    
    print("=== CPU-Intensive Benchmark ===")
    print(f"Available CPU cores: {mp.cpu_count()}")
    
    # Sequential execution
    print("\n--- Sequential Execution ---")
    start_time = time.time()
    sequential_results = [matrix_multiply(size) for size in test_sizes]
    sequential_time = time.time() - start_time
    print(f"Sequential time: {sequential_time:.3f}s")
    
    # Multiprocessing execution
    print("\n--- Multiprocessing Execution ---")
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        parallel_results = list(executor.map(matrix_multiply, test_sizes))
    
    parallel_time = time.time() - start_time
    print(f"Parallel time: {parallel_time:.3f}s")
    
    # Results
    speedup = sequential_time / parallel_time
    efficiency = speedup / mp.cpu_count()
    
    print(f"\n--- Performance Results ---")
    print(f"Speedup: {speedup:.2f}x")
    print(f"Efficiency: {efficiency:.2%}")
    print(f"Overhead: {(mp.cpu_count() * parallel_time - sequential_time):.3f}s")


class ProcessManager:
    """Manages multiple processes with monitoring capabilities."""
    
    def __init__(self):
        self.processes = {}
        self.results = mp.Queue()
        self.shutdown_event = mp.Event()
    
    def start_process(self, name: str, target_func, *args, **kwargs):
        """Start a named process."""
        process = mp.Process(target=target_func, args=args, kwargs=kwargs, name=name)
        process.start()
        self.processes[name] = {
            'process': process,
            'start_time': time.time(),
            'status': 'running'
        }
        print(f"Started process '{name}' (PID: {process.pid})")
    
    def monitor_processes(self):
        """Monitor all running processes."""
        print("\n=== Process Monitor ===")
        for name, info in self.processes.items():
            process = info['process']
            runtime = time.time() - info['start_time']
            
            if process.is_alive():
                status = "RUNNING"
            else:
                status = f"FINISHED (exit code: {process.exitcode})"
                info['status'] = 'finished'
            
            print(f"Process '{name}': {status}, Runtime: {runtime:.2f}s")
    
    def wait_for_all(self):
        """Wait for all processes to complete."""
        for name, info in self.processes.items():
            process = info['process']
            process.join()
            info['end_time'] = time.time()
            info['total_runtime'] = info['end_time'] - info['start_time']
        
        print("\nAll processes completed")
        self._print_summary()
    
    def _print_summary(self):
        """Print execution summary."""
        print("\n=== Execution Summary ===")
        total_runtime = 0
        
        for name, info in self.processes.items():
            runtime = info.get('total_runtime', 0)
            total_runtime += runtime
            print(f"Process '{name}': {runtime:.3f}s")
        
        print(f"Total process time: {total_runtime:.3f}s")