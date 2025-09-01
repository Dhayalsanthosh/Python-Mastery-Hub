"""
Generator examples and demonstrations for the Advanced Python module.
"""

import itertools
from typing import Dict, List, Any, Iterator, Callable
from .base import TopicDemo


class GeneratorsDemo(TopicDemo):
    """Demonstration class for Python generators."""
    
    def __init__(self):
        super().__init__("generators")
    
    def _setup_examples(self) -> None:
        """Setup generator examples."""
        self.examples = {
            "basic_generators": {
                "code": '''
def simple_generator():
    """Basic generator function."""
    print("Generator started")
    yield 1
    print("Between yields")
    yield 2
    print("Generator ending")
    yield 3

def fibonacci_generator(limit: int):
    """Generate Fibonacci numbers up to limit."""
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1

def file_reader(filename: str):
    """Generator that reads file line by line (memory efficient)."""
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                yield line_num, line.strip()
    except FileNotFoundError:
        # Simulate file content for demo
        content = ["First line", "Second line", "Third line", "Fourth line"]
        for line_num, line in enumerate(content, 1):
            yield line_num, line

def infinite_sequence():
    """Generator for infinite sequence."""
    num = 0
    while True:
        yield num
        num += 1

# Generator expressions
squares = (x**2 for x in range(10))
even_squares = (x**2 for x in range(20) if x % 2 == 0)

def stateful_generator():
    """Generator that maintains state and accepts sent values."""
    state = 0
    while True:
        received = yield state
        if received is not None:
            state = received
        else:
            state += 1
''',
                "explanation": "Generators provide memory-efficient iteration by yielding values on-demand rather than creating entire sequences in memory"
            },
            
            "advanced_generators": {
                "code": '''
import itertools
from typing import Iterator, Any, Callable

def pipeline_processor(*processors):
    """Create a data processing pipeline using generators."""
    def decorator(source_generator):
        def pipeline():
            data_stream = source_generator()
            for processor in processors:
                data_stream = processor(data_stream)
            yield from data_stream
        return pipeline
    return decorator

def filter_processor(predicate: Callable):
    """Processor that filters data based on predicate."""
    def processor(data_stream):
        for item in data_stream:
            if predicate(item):
                yield item
    return processor

def transform_processor(transform_func: Callable):
    """Processor that transforms each data item."""
    def processor(data_stream):
        for item in data_stream:
            yield transform_func(item)
    return processor

def batch_processor(batch_size: int):
    """Processor that groups items into batches."""
    def processor(data_stream):
        batch = []
        for item in data_stream:
            batch.append(item)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:  # Yield remaining items
            yield batch
    return processor

def data_source():
    """Generate sample data."""
    for i in range(1, 21):
        yield {"id": i, "value": i * 2, "category": "even" if i % 2 == 0 else "odd"}

# Create processing pipeline
@pipeline_processor(
    filter_processor(lambda x: x["value"] > 10),  # Filter values > 10
    transform_processor(lambda x: {**x, "processed": True}),  # Add processed flag
    batch_processor(3)  # Group into batches of 3
)
def processed_data():
    return data_source()

def coroutine_example():
    """Demonstrate coroutine behavior with generators."""
    
    def averaging_coroutine():
        """Coroutine that maintains running average."""
        total = 0
        count = 0
        average = None
        
        while True:
            value = yield average
            if value is not None:
                total += value
                count += 1
                average = total / count
    
    def logger_coroutine():
        """Coroutine that logs received values."""
        while True:
            value = yield
            print(f"  Logged: {value}")
    
    return averaging_coroutine, logger_coroutine

def generator_delegation():
    """Demonstrate yield from for generator delegation."""
    
    def inner_generator(start, end):
        """Inner generator."""
        for i in range(start, end):
            yield f"Inner: {i}"
    
    def outer_generator():
        """Outer generator that delegates to inner generators."""
        yield "Starting outer generator"
        
        # Delegate to first inner generator
        yield from inner_generator(1, 4)
        
        yield "Middle of outer generator"
        
        # Delegate to second inner generator
        yield from inner_generator(10, 13)
        
        yield "Ending outer generator"
    
    return outer_generator()
''',
                "explanation": "Advanced generators enable sophisticated data processing pipelines, coroutines, and efficient memory usage patterns"
            },
            
            "itertools_examples": {
                "code": '''
import itertools

# Infinite iterators
def infinite_examples():
    """Examples of infinite iterators from itertools."""
    
    # count(start, step) - infinite arithmetic sequence
    counter = itertools.count(1, 2)  # 1, 3, 5, 7, ...
    first_five_odds = list(itertools.islice(counter, 5))
    
    # cycle(iterable) - infinite repetition
    colors = itertools.cycle(['red', 'green', 'blue'])
    first_ten_colors = list(itertools.islice(colors, 10))
    
    # repeat(value, times) - repeat value
    repeated_values = list(itertools.repeat('hello', 3))
    
    return first_five_odds, first_ten_colors, repeated_values

# Combinatorial generators
def combinatorial_examples():
    """Examples of combinatorial generators."""
    
    colors = ['red', 'blue']
    sizes = ['S', 'M', 'L']
    
    # Cartesian product
    combinations = list(itertools.product(colors, sizes))
    
    # Permutations
    numbers = [1, 2, 3]
    perms = list(itertools.permutations(numbers, 2))
    
    # Combinations
    combs = list(itertools.combinations(numbers, 2))
    
    # Combinations with replacement
    combs_with_replacement = list(itertools.combinations_with_replacement([1, 2], 2))
    
    return combinations, perms, combs, combs_with_replacement

# Filtering and grouping
def filtering_grouping_examples():
    """Examples of filtering and grouping generators."""
    
    # Grouping consecutive items
    data = [1, 1, 2, 2, 2, 3, 1, 1]
    grouped = [(key, list(group)) for key, group in itertools.groupby(data)]
    
    # Filter with takewhile and dropwhile
    numbers = [1, 3, 5, 8, 9, 11, 13]
    less_than_8 = list(itertools.takewhile(lambda x: x < 8, numbers))
    from_8_onwards = list(itertools.dropwhile(lambda x: x < 8, numbers))
    
    # Chain generators together
    gen1 = (x for x in range(3))
    gen2 = (x for x in range(10, 13))
    chained = list(itertools.chain(gen1, gen2))
    
    return grouped, less_than_8, from_8_onwards, chained
''',
                "explanation": "The itertools module provides powerful tools for creating efficient loops and processing iterables"
            }
        }
    
    def _setup_exercises(self) -> None:
        """Setup generator exercises."""
        from .exercises.file_pipeline import FilePipelineExercise
        
        pipeline_exercise = FilePipelineExercise()
        
        self.exercises = [
            {
                "topic": "generators",
                "title": "File Processing Pipeline",
                "description": "Build a memory-efficient file processing pipeline using generators",
                "difficulty": "hard",
                "exercise": pipeline_exercise
            }
        ]
    
    def get_explanation(self) -> str:
        """Get detailed explanation for generators."""
        return ("Generators create iterators that yield values on-demand, providing memory-efficient "
                "processing of large datasets and enabling lazy evaluation patterns.")
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for generators."""
        return [
            "Use generators for memory-efficient iteration",
            "Prefer generator expressions for simple transformations",
            "Use yield from for generator delegation",
            "Handle exceptions properly in generators",
            "Close generators explicitly when needed"
        ]