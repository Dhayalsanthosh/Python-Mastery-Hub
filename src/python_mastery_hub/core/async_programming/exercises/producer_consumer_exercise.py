"""
Producer-Consumer Threading Exercise - Implement thread-safe producer-consumer system.
"""

import threading
import queue
import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..base import AsyncDemo, ThreadSafeCounter


@dataclass
class SystemStats:
    """Statistics for the producer-consumer system."""
    items_produced: int = 0
    items_consumed: int = 0
    total_production_time: float = 0.0
    total_consumption_time: float = 0.0
    queue_full_events: int = 0
    queue_empty_events: int = 0


class ProducerConsumerExercise(AsyncDemo):
    """Exercise for implementing a thread-safe producer-consumer system."""
    
    def __init__(self):
        super().__init__("Producer-Consumer Threading Exercise")
        self.instructions = self._get_instructions()
        self.starter_code = self._get_starter_code()
        self.solution = self._get_solution()
    
    def _get_instructions(self) -> Dict[str, Any]:
        """Get exercise instructions."""
        return {
            "title": "Thread-Safe Producer-Consumer System",
            "description": "Build a robust producer-consumer system using threading with proper synchronization",
            "objectives": [
                "Create thread-safe queue with size limits",
                "Implement producer threads that generate work items",
                "Implement consumer threads that process work items",
                "Add proper synchronization using locks and conditions",
                "Include comprehensive monitoring and statistics",
                "Handle graceful shutdown and cleanup",
                "Implement load balancing across consumers"
            ],
            "requirements": [
                "Use threading.Queue for thread-safe communication",
                "Implement multiple producer and consumer threads",
                "Add proper exception handling and cleanup",
                "Track detailed performance statistics",
                "Support dynamic scaling of workers",
                "Implement priority-based work items",
                "Add monitoring and health checks"
            ],
            "difficulty": "Advanced",
            "estimated_time": "2-3 hours"
        }
    
    def _get_starter_code(self) -> str:
        """Get starter code template."""
        return '''
import threading
import queue
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class SystemStats:
    items_produced: int = 0
    items_consumed: int = 0
    total_production_time: float = 0.0
    total_consumption_time: float = 0.0
    queue_full_events: int = 0
    queue_empty_events: int = 0

class ProducerConsumerSystem:
    def __init__(self, queue_size=10, num_producers=2, num_consumers=3):
        self.queue_size = queue_size
        self.num_producers = num_producers
        self.num_consumers = num_consumers
        # TODO: Initialize queue, locks, events, and statistics
        pass
    
    def producer(self, producer_id: int):
        """Producer thread that generates work items."""
        # TODO: Implement producer logic
        # - Generate work items
        # - Handle queue full scenarios
        # - Update statistics
        # - Respect shutdown signals
        pass
    
    def consumer(self, consumer_id: int):
        """Consumer thread that processes work items."""
        # TODO: Implement consumer logic
        # - Get items from queue
        # - Process items
        # - Handle queue empty scenarios
        # - Update statistics
        pass
    
    def monitor(self):
        """Monitor thread that tracks system status."""
        # TODO: Implement monitoring
        # - Track queue size
        # - Print periodic status updates
        # - Monitor thread health
        pass
    
    def run(self, duration: float = 10.0):
        """Run the producer-consumer system."""
        # TODO: Implement main execution logic
        # - Start all threads
        # - Run for specified duration
        # - Handle graceful shutdown
        # - Print final statistics
        pass

# Example usage
if __name__ == "__main__":
    system = ProducerConsumerSystem(
        queue_size=5,
        num_producers=2,
        num_consumers=3
    )
    system.run(duration=8.0)
'''
    
    def _get_solution(self) -> str:
        """Get complete solution."""
        return '''
import threading
import queue
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class SystemStats:
    """Statistics for the producer-consumer system."""
    items_produced: int = 0
    items_consumed: int = 0
    total_production_time: float = 0.0
    total_consumption_time: float = 0.0
    queue_full_events: int = 0
    queue_empty_events: int = 0

@dataclass
class WorkItem:
    """Work item with metadata."""
    id: str
    data: Any
    priority: int = 0
    created_at: float = 0.0
    producer_id: int = 0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()

class ProducerConsumerSystem:
    """Advanced producer-consumer system with comprehensive features."""
    
    def __init__(self, queue_size=10, num_producers=2, num_consumers=3):
        self.queue_size = queue_size
        self.num_producers = num_producers
        self.num_consumers = num_consumers
        
        # Thread-safe queue with priority support
        self.work_queue = queue.PriorityQueue(maxsize=queue_size)
        
        # Synchronization primitives
        self.running = threading.Event()
        self.stats_lock = threading.Lock()
        self.shutdown_complete = threading.Event()
        
        # Statistics tracking
        self.stats = SystemStats()
        self.producer_stats: Dict[int, Dict[str, Any]] = {}
        self.consumer_stats: Dict[int, Dict[str, Any]] = {}
        
        # Thread management
        self.producer_threads: List[threading.Thread] = []
        self.consumer_threads: List[threading.Thread] = []
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Health monitoring
        self.last_activity = {}
        self.thread_health = {}
    
    def producer(self, producer_id: int):
        """Enhanced producer with priority work items and health tracking."""
        thread_name = f"Producer-{producer_id}"
        self.producer_stats[producer_id] = {
            'items_produced': 0,
            'queue_full_events': 0,
            'production_time': 0.0,
            'start_time': time.time()
        }
        
        print(f"{thread_name} started")
        self.thread_health[thread_name] = 'healthy'
        
        item_counter = 0
        
        while self.running.is_set():
            try:
                # Update health status
                self.last_activity[thread_name] = time.time()
                
                # Generate work item with random priority
                priority = random.randint(1, 5)  # 1 = highest priority
                work_item = WorkItem(
                    id=f"P{producer_id}-{item_counter}",
                    data=random.randint(1, 100),
                    priority=priority,
                    producer_id=producer_id
                )
                
                # Try to add to queue with timeout
                start_time = time.time()
                try:
                    # Use negative priority for PriorityQueue (min-heap)
                    self.work_queue.put((-priority, work_item), timeout=1.0)
                    production_time = time.time() - start_time
                    
                    # Update statistics
                    with self.stats_lock:
                        self.stats.items_produced += 1
                        self.stats.total_production_time += production_time
                        self.producer_stats[producer_id]['items_produced'] += 1
                        self.producer_stats[producer_id]['production_time'] += production_time
                    
                    print(f"{thread_name} created: {work_item.id} (priority: {priority})")
                    item_counter += 1
                    
                    # Variable production rate
                    time.sleep(random.uniform(0.1, 0.8))
                    
                except queue.Full:
                    with self.stats_lock:
                        self.stats.queue_full_events += 1
                        self.producer_stats[producer_id]['queue_full_events'] += 1
                    
                    print(f"{thread_name}: Queue full, waiting...")
                    time.sleep(0.2)
                
            except Exception as e:
                print(f"{thread_name} error: {e}")
                self.thread_health[thread_name] = f'error: {e}'
                break
        
        self.thread_health[thread_name] = 'stopped'
        print(f"{thread_name} finished ({item_counter} items produced)")
    
    def consumer(self, consumer_id: int):
        """Enhanced consumer with detailed processing and health tracking."""
        thread_name = f"Consumer-{consumer_id}"
        self.consumer_stats[consumer_id] = {
            'items_consumed': 0,
            'queue_empty_events': 0,
            'consumption_time': 0.0,
            'processing_time': 0.0,
            'start_time': time.time()
        }
        
        print(f"{thread_name} started")
        self.thread_health[thread_name] = 'healthy'
        
        while self.running.is_set() or not self.work_queue.empty():
            try:
                # Update health status
                self.last_activity[thread_name] = time.time()
                
                # Get work item from queue
                start_time = time.time()
                try:
                    priority, work_item = self.work_queue.get(timeout=1.0)
                    priority = -priority  # Convert back to positive
                    
                    # Process the item
                    processing_start = time.time()
                    processing_time = random.uniform(0.2, 1.2)
                    time.sleep(processing_time)
                    
                    # Simulate processing result
                    result = work_item.data * 2
                    age = time.time() - work_item.created_at
                    
                    consumption_time = time.time() - start_time
                    
                    # Update statistics
                    with self.stats_lock:
                        self.stats.items_consumed += 1
                        self.stats.total_consumption_time += consumption_time
                        stats = self.consumer_stats[consumer_id]
                        stats['items_consumed'] += 1
                        stats['consumption_time'] += consumption_time
                        stats['processing_time'] += processing_time
                    
                    print(f"{thread_name} processed: {work_item.id} "
                          f"(priority: {priority}, age: {age:.2f}s) -> {result}")
                    
                    # Mark task as done
                    self.work_queue.task_done()
                    
                except queue.Empty:
                    if self.running.is_set():
                        with self.stats_lock:
                            self.stats.queue_empty_events += 1
                            self.consumer_stats[consumer_id]['queue_empty_events'] += 1
                        
                        print(f"{thread_name}: Queue empty, waiting...")
                    time.sleep(0.1)
                
            except Exception as e:
                print(f"{thread_name} error: {e}")
                self.thread_health[thread_name] = f'error: {e}'
                break
        
        self.thread_health[thread_name] = 'stopped'
        print(f"{thread_name} finished")
    
    def monitor(self):
        """Enhanced monitoring with health checks and performance metrics."""
        print("Monitor started")
        
        monitor_interval = 2.0
        last_stats = SystemStats()
        
        while self.running.is_set():
            time.sleep(monitor_interval)
            
            current_time = time.time()
            
            with self.stats_lock:
                queue_size = self.work_queue.qsize()
                
                # Calculate rates since last update
                items_produced_delta = self.stats.items_produced - last_stats.items_produced
                items_consumed_delta = self.stats.items_consumed - last_stats.items_consumed
                
                production_rate = items_produced_delta / monitor_interval
                consumption_rate = items_consumed_delta / monitor_interval
                
                print(f"\\n{'='*60}")
                print("SYSTEM STATUS")
                print(f"{'='*60}")
                print(f"Queue: {queue_size}/{self.queue_size} items")
                print(f"Production rate: {production_rate:.1f} items/sec")
                print(f"Consumption rate: {consumption_rate:.1f} items/sec")
                
                print(f"\\nCumulative Stats:")
                print(f"  Produced: {self.stats.items_produced}")
                print(f"  Consumed: {self.stats.items_consumed}")
                print(f"  Pending: {self.stats.items_produced - self.stats.items_consumed}")
                
                if self.stats.items_produced > 0:
                    avg_production = self.stats.total_production_time / self.stats.items_produced
                    print(f"  Avg production time: {avg_production:.3f}s")
                
                if self.stats.items_consumed > 0:
                    avg_consumption = self.stats.total_consumption_time / self.stats.items_consumed
                    print(f"  Avg consumption time: {avg_consumption:.3f}s")
                
                print(f"\\nQueue Events:")
                print(f"  Queue full events: {self.stats.queue_full_events}")
                print(f"  Queue empty events: {self.stats.queue_empty_events}")
                
                # Health check
                print(f"\\nThread Health:")
                for thread_name, status in self.thread_health.items():
                    last_seen = self.last_activity.get(thread_name, 0)
                    if last_seen > 0:
                        idle_time = current_time - last_seen
                        health_indicator = "⚠️" if idle_time > 5.0 else "✅"
                        print(f"  {health_indicator} {thread_name}: {status} "
                              f"(idle: {idle_time:.1f}s)")
                    else:
                        print(f"  ❓ {thread_name}: {status}")
                
                # Update last stats for rate calculation
                last_stats = SystemStats(
                    items_produced=self.stats.items_produced,
                    items_consumed=self.stats.items_consumed,
                    total_production_time=self.stats.total_production_time,
                    total_consumption_time=self.stats.total_consumption_time,
                    queue_full_events=self.stats.queue_full_events,
                    queue_empty_events=self.stats.queue_empty_events
                )
        
        print("Monitor stopped")
    
    def run(self, duration: float = 10.0):
        """Run the enhanced producer-consumer system."""
        print(f"Starting Enhanced Producer-Consumer System")
        print(f"Configuration:")
        print(f"  Queue size: {self.queue_size}")
        print(f"  Producers: {self.num_producers}")
        print(f"  Consumers: {self.num_consumers}")
        print(f"  Duration: {duration}s")
        print("="*60)
        
        # Set running flag
        self.running.set()
        
        # Start producer threads
        for i in range(self.num_producers):
            thread = threading.Thread(
                target=self.producer, 
                args=(i,), 
                name=f"Producer-{i}",
                daemon=False
            )
            self.producer_threads.append(thread)
            thread.start()
        
        # Start consumer threads
        for i in range(self.num_consumers):
            thread = threading.Thread(
                target=self.consumer, 
                args=(i,), 
                name=f"Consumer-{i}",
                daemon=False
            )
            self.consumer_threads.append(thread)
            thread.start()
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(
            target=self.monitor, 
            name="Monitor",
            daemon=False
        )
        self.monitor_thread.start()
        
        # Run for specified duration
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\\nReceived interrupt signal...")
        
        # Initiate graceful shutdown
        print("\\nInitiating graceful shutdown...")
        self.running.clear()
        
        # Wait for producers to finish
        print("Waiting for producers to finish...")
        for thread in self.producer_threads:
            thread.join(timeout=5.0)
        
        # Wait for remaining items to be processed
        print("Waiting for queue to empty...")
        self.work_queue.join()
        
        # Wait for consumers to finish
        print("Waiting for consumers to finish...")
        for thread in self.consumer_threads:
            thread.join(timeout=5.0)
        
        # Stop monitor
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        self._print_final_statistics()
    
    def _print_final_statistics(self):
        """Print comprehensive final statistics."""
        print("\\n" + "="*80)
        print("FINAL EXECUTION REPORT")
        print("="*80)
        
        with self.stats_lock:
            total_runtime = time.time() - min(
                stats['start_time'] for stats in self.producer_stats.values()
            )
            
            print(f"System Overview:")
            print(f"  Total runtime: {total_runtime:.2f}s")
            print(f"  Items produced: {self.stats.items_produced}")
            print(f"  Items consumed: {self.stats.items_consumed}")
            print(f"  Items remaining: {self.work_queue.qsize()}")
            
            if self.stats.items_produced > 0:
                processing_rate = (self.stats.items_consumed / self.stats.items_produced) * 100
                print(f"  Processing completion: {processing_rate:.1f}%")
            
            print(f"\\nPerformance Metrics:")
            if total_runtime > 0:
                throughput = self.stats.items_consumed / total_runtime
                print(f"  Overall throughput: {throughput:.2f} items/sec")
            
            if self.stats.items_produced > 0:
                avg_production = self.stats.total_production_time / self.stats.items_produced
                print(f"  Avg production time: {avg_production:.3f}s")
            
            if self.stats.items_consumed > 0:
                avg_consumption = self.stats.total_consumption_time / self.stats.items_consumed
                print(f"  Avg consumption time: {avg_consumption:.3f}s")
            
            print(f"\\nProducer Statistics:")
            for producer_id, stats in self.producer_stats.items():
                runtime = time.time() - stats['start_time']
                rate = stats['items_produced'] / runtime if runtime > 0 else 0
                print(f"  Producer {producer_id}: {stats['items_produced']} items "
                      f"({rate:.2f} items/sec, {stats['queue_full_events']} queue full events)")
            
            print(f"\\nConsumer Statistics:")
            for consumer_id, stats in self.consumer_stats.items():
                runtime = time.time() - stats['start_time']
                rate = stats['items_consumed'] / runtime if runtime > 0 else 0
                avg_processing = (stats['processing_time'] / stats['items_consumed'] 
                                if stats['items_consumed'] > 0 else 0)
                print(f"  Consumer {consumer_id}: {stats['items_consumed']} items "
                      f"({rate:.2f} items/sec, avg processing: {avg_processing:.3f}s)")
            
            print(f"\\nSystem Events:")
            print(f"  Queue full events: {self.stats.queue_full_events}")
            print(f"  Queue empty events: {self.stats.queue_empty_events}")
            
            # Efficiency analysis
            total_production_time = sum(
                stats['production_time'] for stats in self.producer_stats.values()
            )
            total_consumption_time = sum(
                stats['consumption_time'] for stats in self.consumer_stats.values()
            )
            
            if total_runtime > 0:
                producer_efficiency = (total_production_time / (self.num_producers * total_runtime)) * 100
                consumer_efficiency = (total_consumption_time / (self.num_consumers * total_runtime)) * 100
                
                print(f"\\nEfficiency Analysis:")
                print(f"  Producer utilization: {producer_efficiency:.1f}%")
                print(f"  Consumer utilization: {consumer_efficiency:.1f}%")

# Example usage and testing
def run_basic_test():
    """Run basic functionality test."""
    print("Running basic producer-consumer test...")
    
    system = ProducerConsumerSystem(
        queue_size=5,
        num_producers=2,
        num_consumers=3
    )
    
    system.run(duration=8.0)

def run_stress_test():
    """Run stress test with high load."""
    print("\\n" + "="*80)
    print("Running stress test...")
    
    system = ProducerConsumerSystem(
        queue_size=3,  # Small queue to test backpressure
        num_producers=4,  # More producers than consumers
        num_consumers=2
    )
    
    system.run(duration=6.0)

def run_performance_comparison():
    """Compare different configurations."""
    print("\\n" + "="*80)
    print("Performance comparison test...")
    
    configurations = [
        {"producers": 1, "consumers": 1, "queue_size": 5},
        {"producers": 2, "consumers": 2, "queue_size": 5},
        {"producers": 3, "consumers": 1, "queue_size": 10},
        {"producers": 1, "consumers": 3, "queue_size": 10},
    ]
    
    for i, config in enumerate(configurations, 1):
        print(f"\\nConfiguration {i}: {config}")
        
        system = ProducerConsumerSystem(
            queue_size=config["queue_size"],
            num_producers=config["producers"],
            num_consumers=config["consumers"]
        )
        
        system.run(duration=4.0)

if __name__ == "__main__":
    # Run all tests
    run_basic_test()
    run_stress_test()
    run_performance_comparison()
'''
    
    def get_explanation(self) -> str:
        """Get explanation for the exercise."""
        return (
            "This exercise teaches essential concepts in concurrent programming "
            "using Python's threading module. You'll learn to coordinate multiple "
            "threads safely, handle shared resources, implement proper synchronization, "
            "and build production-ready concurrent systems with monitoring and health checks."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for producer-consumer systems.""" 
        return [
            "Always use thread-safe data structures like queue.Queue",
            "Implement proper exception handling in all threads",
            "Use locks to protect shared mutable state",
            "Handle graceful shutdown with threading.Event",
            "Monitor thread health and detect deadlocks",
            "Implement backpressure mechanisms for queue management",
            "Use timeouts to prevent indefinite blocking",
            "Track performance statistics for optimization",
            "Consider using priority queues for work prioritization",
            "Test with various load patterns and edge cases"
        ]
    
    def validate_solution(self, solution_code: str) -> List[str]:
        """Validate student solution."""
        feedback = []
        
        required_components = [
            ("queue.Queue", "Must use thread-safe queue"),
            ("threading.Thread", "Must use threading for workers"),
            ("threading.Lock", "Must implement proper locking"),
            ("threading.Event", "Must use events for coordination"),
            ("producer", "Must implement producer function"),
            ("consumer", "Must implement consumer function"),
            ("statistics", "Must track performance statistics"),
            ("exception", "Must handle exceptions properly")
        ]
        
        for component, message in required_components:
            if component.lower() in solution_code.lower():
                feedback.append(f"✓ {message}")
            else:
                feedback.append(f"✗ {message}")
        
        return feedback