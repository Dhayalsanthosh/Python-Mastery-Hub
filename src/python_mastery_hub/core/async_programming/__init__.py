"""
Asynchronous Programming Learning Module.

Comprehensive coverage of async/await, asyncio, concurrent programming,
threading, multiprocessing, and performance optimization techniques.
"""

from .async_basics import AsyncBasics
from .asyncio_patterns import AsyncioPatterns  
from .threading_concepts import ThreadingConcepts
from .multiprocessing_concepts import MultiprocessingConcepts
from .concurrent_futures_concepts import ConcurrentFuturesConcepts
from .exercises import (
    AsyncScraperExercise,
    ProducerConsumerExercise, 
    ParallelProcessorExercise
)

# Main module class that coordinates all components
class AsyncProgramming:
    """Interactive learning module for Asynchronous Programming."""
    
    def __init__(self):
        self.name = "Asynchronous Programming"
        self.description = "Master async/await, concurrency, threading, and parallel processing"
        self.difficulty = "advanced"
        
        # Initialize sub-modules
        self.async_basics = AsyncBasics()
        self.asyncio_patterns = AsyncioPatterns()
        self.threading_concepts = ThreadingConcepts()
        self.multiprocessing_concepts = MultiprocessingConcepts()
        self.concurrent_futures_concepts = ConcurrentFuturesConcepts()
        
        # Initialize exercises
        self.exercises = {
            "async_scraper": AsyncScraperExercise(),
            "producer_consumer": ProducerConsumerExercise(),
            "parallel_processor": ParallelProcessorExercise()
        }
    
    def get_topics(self):
        """Return list of available topics."""
        return [
            "async_basics",
            "asyncio_patterns", 
            "threading_concepts",
            "multiprocessing_concepts",
            "concurrent_futures_concepts"
        ]
    
    def demonstrate(self, topic: str):
        """Demonstrate a specific topic."""
        topic_modules = {
            "async_basics": self.async_basics,
            "asyncio_patterns": self.asyncio_patterns,
            "threading_concepts": self.threading_concepts,
            "multiprocessing_concepts": self.multiprocessing_concepts,
            "concurrent_futures_concepts": self.concurrent_futures_concepts
        }
        
        if topic not in topic_modules:
            raise ValueError(f"Topic '{topic}' not found")
        
        return topic_modules[topic].demonstrate()

__all__ = [
    'AsyncProgramming',
    'AsyncBasics',
    'AsyncioPatterns',
    'ThreadingConcepts', 
    'MultiprocessingConcepts',
    'ConcurrentFuturesConcepts',
    'AsyncScraperExercise',
    'ProducerConsumerExercise',
    'ParallelProcessorExercise'
]