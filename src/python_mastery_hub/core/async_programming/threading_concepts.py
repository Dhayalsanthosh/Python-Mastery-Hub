"""
Threading concepts for the async programming module.
"""

import threading
import time
import queue
import random
from typing import Dict, List, Any, Optional
from .base import AsyncDemo, ThreadSafeCounter, simulate_io_operation


class ThreadingConcepts(AsyncDemo):
    """Demonstrates threading concepts and synchronization."""
    
    def __init__(self):
        super().__init__("Threading Concepts")
        self._setup_examples()
    
    def _setup_examples(self) -> None:
        """Setup threading examples."""
        self.examples = {
            "basic_threading": {
                "code": '''
import threading
import time
import random

def worker_function(worker_id, duration):
    """Simple worker function for threading demo."""
    print(f"Worker {worker_id} starting (will work for {duration}s)")
    time.sleep(duration)
    print(f"Worker {worker_id} finished")
    return f"Result from worker {worker_id}"

def basic_threading_example():
    """Demonstrate basic threading concepts."""
    print("=== Basic Threading Example ===")
    
    # Create and start threads
    threads = []
    for i in range(3):
        duration = random.uniform(1, 3)
        thread = threading.Thread(
            target=worker_function, 
            args=(i, duration),
            name=f"Worker-{i}"
        )
        threads.append(thread)
        thread.start()
        print(f"Started thread: {thread.name}")
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
        print(f"Thread {thread.name} joined")
    
    print("All threads completed")

basic_threading_example()
''',
                "explanation": "Threading enables concurrent execution of I/O-bound tasks with shared memory space"
            },
            
            "thread_synchronization": {
                "code": '''
import threading
import time
import random

class BankAccount:
    """Thread-safe bank account with locking."""
    
    def __init__(self, initial_balance=0):
        self.balance = initial_balance
        self.lock = threading.Lock()
        self.transaction_count = 0
    
    def deposit(self, amount):
        """Thread-safe deposit operation."""
        with self.lock:
            old_balance = self.balance
            time.sleep(0.01)  # Simulate processing delay
            self.balance += amount
            self.transaction_count += 1
            print(f"Deposited ${amount}: ${old_balance} -> ${self.balance}")
    
    def withdraw(self, amount):
        """Thread-safe withdrawal operation."""
        with self.lock:
            if self.balance >= amount:
                old_balance = self.balance
                time.sleep(0.01)  # Simulate processing delay
                self.balance -= amount
                self.transaction_count += 1
                print(f"Withdrew ${amount}: ${old_balance} -> ${self.balance}")
                return True
            else:
                print(f"Insufficient funds for withdrawal of ${amount}")
                return False
    
    def get_balance(self):
        """Thread-safe balance check."""
        with self.lock:
            return self.balance

def thread_synchronization_example():
    """Demonstrate thread synchronization with locks."""
    print("=== Thread Synchronization Example ===")
    
    account = BankAccount(1000)
    
    def perform_transactions(thread_id):
        """Perform random transactions."""
        for i in range(5):
            if random.choice([True, False]):
                amount = random.randint(10, 100)
                account.deposit(amount)
            else:
                amount = random.randint(10, 200)
                account.withdraw(amount)
    
    # Create multiple threads performing transactions
    threads = []
    for i in range(3):
        thread = threading.Thread(target=perform_transactions, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all transactions to complete
    for thread in threads:
        thread.join()
    
    print(f"Final balance: ${account.get_balance()}")
    print(f"Total transactions: {account.transaction_count}")

thread_synchronization_example()
''',
                "explanation": "Thread synchronization ensures data integrity when multiple threads access shared resources"
            },
            
            "producer_consumer_threading": {
                "code": '''
import threading
import queue
import time
import random

def producer_consumer_threading():
    """Demonstrate producer-consumer pattern with threading."""
    print("=== Producer-Consumer with Threading ===")
    
    # Shared queue with maximum size
    shared_queue = queue.Queue(maxsize=5)
    stop_event = threading.Event()
    
    def producer(producer_id, num_items):
        """Producer function."""
        for i in range(num_items):
            if stop_event.is_set():
                break
            
            item = f"Item-{producer_id}-{i}"
            shared_queue.put(item)
            print(f"Producer {producer_id} produced: {item}")
            time.sleep(random.uniform(0.1, 0.5))
        
        print(f"Producer {producer_id} finished")
    
    def consumer(consumer_id):
        """Consumer function."""
        consumed_count = 0
        
        while not stop_event.is_set() or not shared_queue.empty():
            try:
                item = shared_queue.get(timeout=1)
                print(f"Consumer {consumer_id} consuming: {item}")
                time.sleep(random.uniform(0.2, 0.8))  # Processing time
                shared_queue.task_done()
                consumed_count += 1
            except queue.Empty:
                continue
        
        print(f"Consumer {consumer_id} finished, consumed {consumed_count} items")
    
    # Create and start producer threads
    producer_threads = []
    for i in range(2):
        thread = threading.Thread(target=producer, args=(i, 5))
        producer_threads.append(thread)
        thread.start()
    
    # Create and start consumer threads
    consumer_threads = []
    for i in range(3):
        thread = threading.Thread(target=consumer, args=(i,))
        consumer_threads.append(thread)
        thread.start()
    
    # Let it run for a while
    time.sleep(5)
    
    # Signal stop and wait for completion
    stop_event.set()
    
    for thread in producer_threads:
        thread.join()
    
    # Wait for queue to be empty
    shared_queue.join()
    
    for thread in consumer_threads:
        thread.join()
    
    print("All threads finished")

producer_consumer_threading()
''',
                "explanation": "Producer-consumer pattern with threading uses queues for thread-safe communication"
            },
            
            "thread_pool": {
                "code": '''
import concurrent.futures
import time
import random

def io_bound_task(task_id):
    """Simulate I/O-bound task."""
    duration = random.uniform(0.5, 2.0)
    print(f"Task {task_id} starting (duration: {duration:.2f}s)")
    time.sleep(duration)
    print(f"Task {task_id} completed")
    return f"Result from task {task_id}"

def thread_pool_example():
    """Demonstrate ThreadPoolExecutor."""
    print("=== ThreadPoolExecutor Example ===")
    
    start_time = time.time()
    
    # Using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit multiple tasks
        futures = [executor.submit(io_bound_task, i) for i in range(8)]
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"Received: {result}")
            except Exception as e:
                print(f"Task failed: {e}")
    
    total_time = time.time() - start_time
    print(f"All tasks completed in {total_time:.2f}s")
    
    # Compare with sequential execution
    print("\\n=== Sequential Execution (for comparison) ===")
    start_time = time.time()
    
    for i in range(8):
        result = io_bound_task(i)
        print(f"Received: {result}")
    
    sequential_time = time.time() - start_time
    print(f"Sequential execution took {sequential_time:.2f}s")
    print(f"Speedup with threading: {sequential_time / total_time:.2f}x")

thread_pool_example()
''',
                "explanation": "ThreadPoolExecutor provides a high-level interface for managing thread pools"
            },
            
            "condition_variables": {
                "code": '''
import threading
import time
import random

def condition_variable_example():
    """Demonstrate condition variables for complex synchronization."""
    print("=== Condition Variables Example ===")
    
    condition = threading.Condition()
    shared_data = {"items": [], "max_size": 5}
    
    def producer():
        """Producer that adds items when space is available."""
        for i in range(10):
            with condition:
                # Wait for space in the buffer
                while len(shared_data["items"]) >= shared_data["max_size"]:
                    print("Producer: Buffer full, waiting...")
                    condition.wait()
                
                # Produce item
                item = f"item_{i}"
                shared_data["items"].append(item)
                print(f"Producer: Added {item} (buffer: {len(shared_data['items'])})")
                
                # Notify consumers
                condition.notify_all()
            
            time.sleep(random.uniform(0.1, 0.5))
    
    def consumer(consumer_id):
        """Consumer that processes items when available."""
        processed = 0
        
        while processed < 5:  # Each consumer processes 5 items
            with condition:
                # Wait for items to be available
                while not shared_data["items"]:
                    print(f"Consumer {consumer_id}: Buffer empty, waiting...")
                    condition.wait()
                
                # Consume item
                item = shared_data["items"].pop(0)
                print(f"Consumer {consumer_id}: Processing {item} (buffer: {len(shared_data['items'])})")
                processed += 1
                
                # Notify producer
                condition.notify_all()
            
            # Simulate processing time
            time.sleep(random.uniform(0.2, 0.8))
        
        print(f"Consumer {consumer_id} finished")
    
    # Create and start threads
    producer_thread = threading.Thread(target=producer)
    consumer_threads = [
        threading.Thread(target=consumer, args=(i,)) 
        for i in range(2)
    ]
    
    producer_thread.start()
    for thread in consumer_threads:
        thread.start()
    
    # Wait for all threads to complete
    producer_thread.join()
    for thread in consumer_threads:
        thread.join()
    
    print("All threads completed")

condition_variable_example()
''',
                "explanation": "Condition variables enable complex synchronization patterns between threads"
            }
        }
    
    def get_explanation(self) -> str:
        """Get explanation for threading concepts."""
        return (
            "Threading in Python allows concurrent execution of I/O-bound tasks "
            "within a single process. Threads share memory space, making "
            "communication efficient but requiring careful synchronization to "
            "prevent race conditions and ensure data consistency."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for threading."""
        return [
            "Use threading for I/O-bound tasks, not CPU-bound tasks",
            "Always use locks when accessing shared mutable data",
            "Prefer ThreadPoolExecutor over manual thread management",
            "Use thread-safe collections (queue.Queue) when possible",
            "Handle thread exceptions properly to prevent silent failures",
            "Avoid deadlocks by acquiring locks in consistent order",
            "Use condition variables for complex synchronization scenarios",
            "Keep critical sections as small as possible",
            "Use threading.Event for simple signaling between threads",
            "Be aware of the Global Interpreter Lock (GIL) limitations"
        ]


class ThreadSafeBankAccount:
    """Enhanced thread-safe bank account for demonstrations."""
    
    def __init__(self, initial_balance: float = 0):
        self.balance = initial_balance
        self.lock = threading.RLock()  # Reentrant lock
        self.transaction_history = []
        self.total_deposits = 0
        self.total_withdrawals = 0
    
    def deposit(self, amount: float, description: str = "Deposit") -> bool:
        """Thread-safe deposit with transaction history."""
        if amount <= 0:
            return False
        
        with self.lock:
            old_balance = self.balance
            self.balance += amount
            self.total_deposits += amount
            
            transaction = {
                'type': 'deposit',
                'amount': amount,
                'balance_before': old_balance,
                'balance_after': self.balance,
                'description': description,
                'timestamp': time.time(),
                'thread': threading.current_thread().name
            }
            self.transaction_history.append(transaction)
            
            print(f"[{transaction['thread']}] {description}: +${amount:.2f} "
                  f"(${old_balance:.2f} -> ${self.balance:.2f})")
            
            return True
    
    def withdraw(self, amount: float, description: str = "Withdrawal") -> bool:
        """Thread-safe withdrawal with overdraft protection."""
        if amount <= 0:
            return False
        
        with self.lock:
            if self.balance >= amount:
                old_balance = self.balance
                self.balance -= amount
                self.total_withdrawals += amount
                
                transaction = {
                    'type': 'withdrawal',
                    'amount': amount,
                    'balance_before': old_balance,
                    'balance_after': self.balance,
                    'description': description,
                    'timestamp': time.time(),
                    'thread': threading.current_thread().name
                }
                self.transaction_history.append(transaction)
                
                print(f"[{transaction['thread']}] {description}: -${amount:.2f} "
                      f"(${old_balance:.2f} -> ${self.balance:.2f})")
                
                return True
            else:
                print(f"[{threading.current_thread().name}] "
                      f"Insufficient funds for ${amount:.2f} withdrawal")
                return False
    
    def transfer(self, other_account: 'ThreadSafeBankAccount', amount: float) -> bool:
        """Thread-safe transfer between accounts."""
        # Acquire locks in consistent order to prevent deadlock
        first_lock = self.lock if id(self) < id(other_account) else other_account.lock
        second_lock = other_account.lock if id(self) < id(other_account) else self.lock
        
        with first_lock:
            with second_lock:
                if self.withdraw(amount, f"Transfer to {id(other_account)}"):
                    other_account.deposit(amount, f"Transfer from {id(self)}")
                    return True
                return False
    
    def get_balance(self) -> float:
        """Get current balance thread-safely."""
        with self.lock:
            return self.balance
    
    def get_summary(self) -> Dict[str, Any]:
        """Get account summary with statistics."""
        with self.lock:
            return {
                'current_balance': self.balance,
                'total_deposits': self.total_deposits,
                'total_withdrawals': self.total_withdrawals,
                'transaction_count': len(self.transaction_history),
                'net_change': self.total_deposits - self.total_withdrawals
            }


class WorkerPool:
    """Thread pool implementation for educational purposes."""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.shutdown_event = threading.Event()
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0
        }
        self.stats_lock = threading.Lock()
    
    def start(self):
        """Start the worker threads."""
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        print(f"Started {self.num_workers} worker threads")
    
    def _worker(self, worker_id: int):
        """Worker thread function."""
        print(f"Worker {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                task_func, args, kwargs, task_id = self.task_queue.get(timeout=1)
                
                print(f"Worker {worker_id} processing task {task_id}")
                
                try:
                    result = task_func(*args, **kwargs)
                    self.result_queue.put(('success', task_id, result))
                    
                    with self.stats_lock:
                        self.stats['tasks_completed'] += 1
                        
                except Exception as e:
                    self.result_queue.put(('error', task_id, str(e)))
                    
                    with self.stats_lock:
                        self.stats['tasks_failed'] += 1
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
        
        print(f"Worker {worker_id} shutting down")
    
    def submit_task(self, func, *args, **kwargs) -> int:
        """Submit a task for execution."""
        with self.stats_lock:
            task_id = self.stats['tasks_submitted']
            self.stats['tasks_submitted'] += 1
        
        self.task_queue.put((func, args, kwargs, task_id))
        return task_id
    
    def get_result(self, timeout: Optional[float] = None):
        """Get a completed task result."""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def shutdown(self, wait: bool = True):
        """Shutdown the worker pool."""
        print("Shutting down worker pool...")
        self.shutdown_event.set()
        
        if wait:
            # Wait for current tasks to complete
            self.task_queue.join()
            
            # Wait for workers to finish
            for worker in self.workers:
                worker.join()
        
        print("Worker pool shutdown complete")
    
    def get_stats(self) -> Dict[str, int]:
        """Get worker pool statistics."""
        with self.stats_lock:
            return self.stats.copy()