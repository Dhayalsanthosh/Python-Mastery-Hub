"""
Asyncio coordination patterns for the async programming module.
"""

import asyncio
import time
import random
from typing import Dict, List, Any, Optional
from .base import AsyncDemo, ProgressTracker


class AsyncioPatterns(AsyncDemo):
    """Demonstrates asyncio coordination and synchronization patterns."""
    
    def __init__(self):
        super().__init__("Asyncio Patterns")
        self._setup_examples()
    
    def _setup_examples(self) -> None:
        """Setup asyncio patterns examples."""
        self.examples = {
            "producer_consumer": {
                "code": '''
import asyncio
import random

async def producer_consumer_example():
    """Demonstrate async producer-consumer pattern."""
    print("=== Async Producer-Consumer Pattern ===")
    
    queue = asyncio.Queue(maxsize=3)
    
    async def producer(name: str, items: list):
        """Async producer that adds items to queue."""
        for item in items:
            await asyncio.sleep(random.uniform(0.1, 0.5))
            await queue.put(f"{name}:{item}")
            print(f"Producer {name} added: {item}")
        
        # Signal completion
        await queue.put(None)
        print(f"Producer {name} finished")
    
    async def consumer(name: str):
        """Async consumer that processes items from queue."""
        processed = 0
        while True:
            item = await queue.get()
            
            if item is None:
                queue.task_done()
                break
            
            # Process item
            await asyncio.sleep(random.uniform(0.2, 0.8))
            print(f"Consumer {name} processed: {item}")
            processed += 1
            queue.task_done()
        
        print(f"Consumer {name} finished, processed {processed} items")
    
    # Create producers and consumers
    producers = [
        producer("P1", ["item1", "item2", "item3"]),
        producer("P2", ["itemA", "itemB"])
    ]
    
    consumers = [
        consumer("C1"),
        consumer("C2")
    ]
    
    # Run producers and consumers concurrently
    await asyncio.gather(*producers, *consumers)

asyncio.run(producer_consumer_example())
''',
                "explanation": "Producer-consumer pattern coordinates data flow between async producers and consumers using queues"
            },
            
            "rate_limiting": {
                "code": '''
import asyncio
import time

class AsyncRateLimiter:
    """Async rate limiter implementation."""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a call."""
        async with self.lock:
            now = time.time()
            
            # Remove old calls outside time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # Check if we can make a call
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    print(f"Rate limit reached, waiting {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()
            
            self.calls.append(now)

async def rate_limiting_example():
    """Demonstrate async rate limiting."""
    print("=== Async Rate Limiting ===")
    
    # Rate limiter: max 3 calls per 2 seconds
    rate_limiter = AsyncRateLimiter(max_calls=3, time_window=2.0)
    
    async def api_call(call_id: int):
        """Simulate API call with rate limiting."""
        await rate_limiter.acquire()
        print(f"Making API call {call_id} at {time.time():.2f}")
        await asyncio.sleep(0.1)  # Simulate API response time
        return f"Response {call_id}"
    
    # Make multiple API calls
    tasks = [api_call(i) for i in range(8)]
    results = await asyncio.gather(*tasks)
    print(f"All API calls completed: {len(results)} results")

asyncio.run(rate_limiting_example())
''',
                "explanation": "Rate limiting prevents overwhelming external services while maintaining high throughput"
            },
            
            "semaphore_coordination": {
                "code": '''
import asyncio
import random

async def semaphore_example():
    """Demonstrate semaphore for controlling concurrent access."""
    print("=== Semaphore Coordination ===")
    
    # Limit to 3 concurrent operations
    semaphore = asyncio.Semaphore(3)
    
    async def limited_resource_operation(operation_id: int):
        """Operation that requires limited resource access."""
        async with semaphore:
            print(f"Operation {operation_id} acquired resource")
            # Simulate work with the limited resource
            work_duration = random.uniform(1, 3)
            await asyncio.sleep(work_duration)
            print(f"Operation {operation_id} released resource after {work_duration:.2f}s")
            return f"Result from operation {operation_id}"
    
    # Start many operations, but only 3 can run concurrently
    tasks = [limited_resource_operation(i) for i in range(8)]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"\\nAll operations completed in {total_time:.2f}s")
    print(f"Results: {len(results)} operations successful")

asyncio.run(semaphore_example())
''',
                "explanation": "Semaphores control the number of concurrent operations accessing shared resources"
            },
            
            "event_coordination": {
                "code": '''
import asyncio

async def event_coordination_example():
    """Demonstrate event-based coordination."""
    print("=== Event Coordination ===")
    
    # Events for coordination
    start_event = asyncio.Event()
    finish_event = asyncio.Event()
    
    async def coordinator():
        """Coordinates the workflow."""
        print("Coordinator: Preparing system...")
        await asyncio.sleep(1)
        
        print("Coordinator: System ready, starting workers")
        start_event.set()  # Signal workers to start
        
        # Wait for all workers to finish
        await finish_event.wait()
        print("Coordinator: All workers finished, shutting down")
    
    async def worker(worker_id: int):
        """Worker that waits for start signal."""
        print(f"Worker {worker_id}: Waiting for start signal...")
        await start_event.wait()
        
        print(f"Worker {worker_id}: Starting work")
        work_duration = random.uniform(2, 4)
        await asyncio.sleep(work_duration)
        
        print(f"Worker {worker_id}: Work completed")
        return f"Worker {worker_id} result"
    
    async def monitor():
        """Monitor that signals when all work is done."""
        # Wait for start signal
        await start_event.wait()
        
        # Create worker tasks
        worker_tasks = [worker(i) for i in range(3)]
        
        # Wait for all workers to complete
        results = await asyncio.gather(*worker_tasks)
        print(f"Monitor: All workers completed: {results}")
        
        # Signal coordinator that work is done
        finish_event.set()
    
    # Run coordinator, workers, and monitor
    await asyncio.gather(
        coordinator(),
        monitor()
    )

asyncio.run(event_coordination_example())
''',
                "explanation": "Events enable coordination between different parts of an async application"
            },
            
            "condition_synchronization": {
                "code": '''
import asyncio
import random

async def condition_example():
    """Demonstrate condition variables for complex synchronization."""
    print("=== Condition Synchronization ===")
    
    condition = asyncio.Condition()
    shared_resource = {"value": 0, "ready": False}
    
    async def producer():
        """Producer that generates values."""
        for i in range(5):
            async with condition:
                # Produce new value
                shared_resource["value"] = random.randint(1, 100)
                shared_resource["ready"] = True
                
                print(f"Producer: Generated value {shared_resource['value']}")
                
                # Notify all waiting consumers
                condition.notify_all()
                
                # Wait for consumers to process
                await condition.wait_for(lambda: not shared_resource["ready"])
            
            await asyncio.sleep(0.5)  # Pause between productions
    
    async def consumer(consumer_id: int):
        """Consumer that processes values."""
        processed_count = 0
        
        while processed_count < 3:  # Each consumer processes 3 values
            async with condition:
                # Wait for a value to be ready
                await condition.wait_for(lambda: shared_resource["ready"])
                
                # Process the value
                value = shared_resource["value"]
                print(f"Consumer {consumer_id}: Processing value {value}")
                
                await asyncio.sleep(random.uniform(0.2, 0.8))  # Simulate processing
                
                print(f"Consumer {consumer_id}: Finished processing {value}")
                processed_count += 1
                
                # Mark as processed (last consumer to finish resets ready flag)
                if processed_count % 2 == 0:  # Arbitrary condition for demo
                    shared_resource["ready"] = False
                    condition.notify_all()
    
    # Run producer and multiple consumers
    await asyncio.gather(
        producer(),
        consumer(1),
        consumer(2)
    )

asyncio.run(condition_example())
''',
                "explanation": "Condition variables provide sophisticated synchronization for complex scenarios"
            }
        }
    
    def get_explanation(self) -> str:
        """Get explanation for asyncio patterns."""
        return (
            "Asyncio provides various synchronization primitives and patterns "
            "for coordinating between coroutines. These patterns help manage "
            "shared resources, control flow, and ensure proper ordering of "
            "operations in concurrent async applications."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for asyncio patterns."""
        return [
            "Use asyncio.Queue for producer-consumer patterns",
            "Implement rate limiting to respect external service limits",
            "Use semaphores to control resource access concurrency",
            "Leverage events for simple coordination between coroutines",
            "Apply condition variables for complex synchronization scenarios",
            "Always handle queue.task_done() when using join()",
            "Set appropriate queue sizes to prevent memory issues",
            "Use locks sparingly and prefer higher-level primitives",
            "Implement proper cleanup in exception scenarios",
            "Monitor and measure the performance impact of synchronization"
        ]


class AsyncRateLimiter:
    """Production-ready async rate limiter."""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a call."""
        async with self.lock:
            now = time.time()
            
            # Remove expired calls
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # Check rate limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()
            
            self.calls.append(now)
    
    def __aenter__(self):
        """Support async context manager."""
        return self.acquire()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass


class AsyncSemaphorePool:
    """Enhanced semaphore with monitoring capabilities."""
    
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_count = 0
        self.total_acquired = 0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire semaphore with monitoring."""
        await self.semaphore.acquire()
        
        async with self.lock:
            self.active_count += 1
            self.total_acquired += 1
    
    def release(self):
        """Release semaphore with monitoring."""
        self.semaphore.release()
        
        # Note: Using asyncio.create_task to avoid blocking
        asyncio.create_task(self._update_count())
    
    async def _update_count(self):
        """Update active count (called from release)."""
        async with self.lock:
            self.active_count -= 1
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.release()
    
    def get_stats(self) -> Dict[str, int]:
        """Get current statistics."""
        return {
            "max_concurrent": self.max_concurrent,
            "active_count": self.active_count,
            "total_acquired": self.total_acquired
        }


class AsyncWorkflowCoordinator:
    """Coordinate complex async workflows."""
    
    def __init__(self):
        self.stages = {}
        self.dependencies = {}
        self.results = {}
        self.events = {}
    
    def add_stage(self, stage_name: str, dependencies: List[str] = None):
        """Add a workflow stage with dependencies."""
        self.stages[stage_name] = dependencies or []
        self.events[stage_name] = asyncio.Event()
    
    async def execute_stage(self, stage_name: str, stage_func: callable, *args, **kwargs):
        """Execute a workflow stage."""
        # Wait for dependencies
        for dependency in self.stages.get(stage_name, []):
            if dependency in self.events:
                await self.events[dependency].wait()
        
        print(f"Executing stage: {stage_name}")
        
        # Execute the stage
        try:
            result = await stage_func(*args, **kwargs)
            self.results[stage_name] = result
            print(f"Stage {stage_name} completed successfully")
        except Exception as e:
            print(f"Stage {stage_name} failed: {e}")
            self.results[stage_name] = e
            raise
        finally:
            # Signal completion
            self.events[stage_name].set()
        
        return result
    
    def get_results(self) -> Dict[str, Any]:
        """Get all stage results."""
        return self.results.copy()