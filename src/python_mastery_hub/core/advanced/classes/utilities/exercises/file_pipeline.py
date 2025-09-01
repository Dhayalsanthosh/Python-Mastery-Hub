"""
File Processing Pipeline Exercise Implementation.

This module provides a generator-based file processing pipeline exercise
that demonstrates memory-efficient data processing patterns.
"""

import re
from typing import Iterator, Callable, Any, Dict, List


class FilePipelineExercise:
    """Exercise for building a memory-efficient file processing pipeline."""
    
    def __init__(self):
        self.title = "File Processing Pipeline"
        self.description = "Build a memory-efficient file processing pipeline using generators"
        self.difficulty = "hard"
    
    def get_instructions(self) -> str:
        """Return exercise instructions."""
        return """
        Build a memory-efficient file processing pipeline using generators:
        
        1. Create generators for reading large files line by line
        2. Add filtering generator for specific patterns
        3. Implement transformation generators for data cleaning
        4. Create aggregation generators for statistics
        5. Chain generators together in a processing pipeline
        6. Handle errors gracefully and provide progress feedback
        7. Support batch processing for memory management
        """
    
    def get_tasks(self) -> List[str]:
        """Return list of specific tasks."""
        return [
            "Create generators for reading large files line by line",
            "Add filtering generator for specific patterns",
            "Implement transformation generators for data cleaning",
            "Create aggregation generators for statistics",
            "Chain generators together in a processing pipeline",
            "Add batch processing for memory efficiency",
            "Include error handling and progress reporting"
        ]
    
    def get_starter_code(self) -> str:
        """Return starter code template."""
        return '''
def file_reader(filename):
    """Generator to read file line by line."""
    # TODO: Implement file reading generator
    pass

def filter_lines(lines, pattern):
    """Generator to filter lines matching pattern."""
    # TODO: Implement filtering generator
    pass

def transform_lines(lines, transform_func):
    """Generator to transform each line."""
    # TODO: Implement transformation generator
    pass

def process_file_pipeline(filename, pattern, transform_func):
    """Complete file processing pipeline."""
    # TODO: Chain generators together
    pass
'''
    
    def get_solution(self) -> str:
        """Return complete solution."""
        return '''
import re
from typing import Iterator, Callable, Any, Dict, List

def file_reader(filename: str) -> Iterator[tuple]:
    """Generator to read file line by line."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                yield line_num, line.rstrip('\\n\\r')
    except FileNotFoundError:
        # Generate sample data for demo
        sample_data = [
            "INFO: User login successful",
            "ERROR: Database connection failed", 
            "DEBUG: Processing request ID 123",
            "INFO: User logout",
            "ERROR: Timeout occurred",
            "WARNING: Low disk space",
            "INFO: Backup completed",
            "ERROR: Network unreachable",
            "DEBUG: Cache hit for user 456",
            "INFO: System maintenance started"
        ]
        for line_num, line in enumerate(sample_data, 1):
            yield line_num, line
    except UnicodeDecodeError as e:
        print(f"Encoding error in {filename}: {e}")
        return
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return

def filter_lines(lines: Iterator[tuple], pattern: str) -> Iterator[tuple]:
    """Generator to filter lines matching pattern."""
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        for line_num, line in lines:
            try:
                if regex.search(line):
                    yield line_num, line
            except Exception as e:
                print(f"Error filtering line {line_num}: {e}")
                continue
    except re.error as e:
        print(f"Invalid regex pattern '{pattern}': {e}")
        return

def transform_lines(lines: Iterator[tuple], transform_func: Callable) -> Iterator[tuple]:
    """Generator to transform each line."""
    for line_num, line in lines:
        try:
            transformed = transform_func(line)
            yield line_num, transformed
        except Exception as e:
            print(f"Error transforming line {line_num}: {e}")
            yield line_num, line  # Yield original on error

def parse_log_line(line: str) -> Dict[str, Any]:
    """Parse log line into structured data."""
    parts = line.split(': ', 1)
    if len(parts) == 2:
        level, message = parts
        return {
            'level': level.strip(),
            'message': message.strip(),
            'length': len(message),
            'original': line
        }
    return {
        'level': 'UNKNOWN', 
        'message': line, 
        'length': len(line),
        'original': line
    }

def aggregate_stats(lines: Iterator[tuple]) -> Iterator[tuple]:
    """Generator that yields running statistics."""
    stats = {
        'total': 0,
        'by_level': {},
        'avg_length': 0,
        'total_length': 0,
        'errors': 0
    }
    
    for line_num, data in lines:
        try:
            if isinstance(data, dict):
                level = data.get('level', 'UNKNOWN')
                length = data.get('length', 0)
                
                stats['total'] += 1
                stats['total_length'] += length
                stats['avg_length'] = stats['total_length'] / stats['total']
                stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
                
                yield line_num, data, stats.copy()
            else:
                stats['errors'] += 1
                yield line_num, data, stats.copy()
        except Exception as e:
            stats['errors'] += 1
            print(f"Error in aggregation for line {line_num}: {e}")
            yield line_num, data, stats.copy()

def batch_processor(lines: Iterator[Any], batch_size: int) -> Iterator[List[Any]]:
    """Generator that groups lines into batches."""
    batch = []
    for item in lines:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:  # Yield remaining items
        yield batch

def progress_reporter(lines: Iterator[Any], report_interval: int = 100) -> Iterator[Any]:
    """Generator that reports progress periodically."""
    count = 0
    for item in lines:
        count += 1
        if count % report_interval == 0:
            print(f"Processed {count} lines...")
        yield item

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

def process_file_pipeline(filename: str, pattern: str = None, batch_size: int = None):
    """Complete file processing pipeline."""
    
    print(f"Processing file: {filename}")
    
    # Stage 1: Read file
    lines = file_reader(filename)
    print("Stage 1: Reading file")
    
    # Stage 2: Add progress reporting
    lines = progress_reporter(lines, report_interval=50)
    
    # Stage 3: Filter if pattern provided
    if pattern:
        lines = filter_lines(lines, pattern)
        print(f"Stage 2: Filtering with pattern '{pattern}'")
    
    # Stage 4: Parse lines
    lines = transform_lines(lines, parse_log_line)
    print("Stage 3: Parsing log lines")
    
    # Stage 5: Aggregate statistics
    lines = aggregate_stats(lines)
    print("Stage 4: Computing statistics")
    
    # Stage 6: Process results
    if batch_size:
        print(f"Stage 5: Processing in batches of {batch_size}")
        lines = batch_processor(lines, batch_size)
        
        batch_count = 0
        total_processed = 0
        
        for batch in lines:
            batch_count += 1
            total_processed += len(batch)
            
            # Process batch statistics
            if batch and len(batch[0]) >= 3:  # Has stats
                last_stats = batch[-1][2] if len(batch[-1]) >= 3 else {}
                print(f"Batch {batch_count}: {len(batch)} lines, Current stats: {last_stats}")
        
        print(f"Total processed: {total_processed} lines in {batch_count} batches")
    else:
        print("Stage 5: Processing individual lines")
        final_stats = None
        line_count = 0
        
        for line_num, data, stats in lines:
            line_count += 1
            final_stats = stats
            
            if line_count <= 5:  # Show first few lines
                level = data.get('level', 'UNKNOWN') if isinstance(data, dict) else 'UNKNOWN'
                message = data.get('message', str(data))[:50] if isinstance(data, dict) else str(data)[:50]
                print(f"Line {line_num}: {level} - {message}...")
            elif line_count == 6:
                print("... (showing first 5 lines)")
        
        print(f"\\nFinal statistics: {final_stats}")
        return final_stats

# Advanced pipeline with decorator pattern
@pipeline_processor(
    lambda lines: progress_reporter(lines, 25),
    lambda lines: filter_lines(lines, "ERROR|WARNING"),
    lambda lines: transform_lines(lines, parse_log_line),
    lambda lines: aggregate_stats(lines)
)
def error_analysis_pipeline():
    """Pipeline focused on error and warning analysis."""
    return file_reader("system.log")

def memory_efficient_processor(filename: str, chunk_size: int = 1000):
    """Process large files in memory-efficient chunks."""
    
    def process_chunk(chunk_lines):
        """Process a chunk of lines."""
        chunk_stats = {'lines': 0, 'errors': 0, 'warnings': 0, 'info': 0}
        
        for line_num, line in chunk_lines:
            chunk_stats['lines'] += 1
            
            # Simple classification
            line_upper = line.upper()
            if 'ERROR' in line_upper:
                chunk_stats['errors'] += 1
            elif 'WARNING' in line_upper:
                chunk_stats['warnings'] += 1
            elif 'INFO' in line_upper:
                chunk_stats['info'] += 1
        
        return chunk_stats
    
    total_stats = {'lines': 0, 'errors': 0, 'warnings': 0, 'info': 0, 'chunks': 0}
    
    # Process file in chunks
    lines = file_reader(filename)
    chunks = batch_processor(lines, chunk_size)
    
    for chunk in chunks:
        chunk_stats = process_chunk(chunk)
        total_stats['chunks'] += 1
        
        # Aggregate statistics
        for key in ['lines', 'errors', 'warnings', 'info']:
            total_stats[key] += chunk_stats[key]
        
        print(f"Chunk {total_stats['chunks']}: {chunk_stats}")
        
        # Simulate memory cleanup between chunks
        del chunk
    
    print(f"\\nTotal statistics: {total_stats}")
    return total_stats

def test_file_pipeline():
    """Test the file processing pipeline."""
    print("=== File Processing Pipeline Test ===")
    
    # Test basic pipeline
    print("\\n1. Processing all lines:")
    stats1 = process_file_pipeline("sample.log")
    
    # Test filtered pipeline
    print("\\n2. Processing ERROR lines only:")
    stats2 = process_file_pipeline("sample.log", pattern="ERROR")
    
    # Test batch processing
    print("\\n3. Batch processing:")
    process_file_pipeline("sample.log", batch_size=3)
    
    # Test memory-efficient processing
    print("\\n4. Memory-efficient processing:")
    memory_efficient_processor("sample.log", chunk_size=4)
    
    # Test decorator pattern
    print("\\n5. Error analysis pipeline:")
    try:
        for line_num, data, stats in error_analysis_pipeline():
            if stats['total'] <= 3:  # Show first few
                print(f"Error/Warning {line_num}: {data}")
            if stats['total'] >= 3:
                break
        print(f"Final error analysis stats: {stats}")
    except Exception as e:
        print(f"Error in pipeline: {e}")

if __name__ == "__main__":
    test_file_pipeline()
'''
    
    def get_test_cases(self) -> List[Dict[str, str]]:
        """Return test cases for validation."""
        return [
            {
                "name": "File reading generator",
                "test": "Verify file_reader yields line numbers and content"
            },
            {
                "name": "Pattern filtering", 
                "test": "Verify filter_lines correctly filters by regex pattern"
            },
            {
                "name": "Line transformation",
                "test": "Verify transform_lines applies functions to each line"
            },
            {
                "name": "Statistics aggregation",
                "test": "Verify aggregate_stats maintains running totals"
            },
            {
                "name": "Batch processing",
                "test": "Verify batch_processor groups items correctly"
            },
            {
                "name": "Memory efficiency",
                "test": "Verify pipeline processes large files without loading all into memory"
            },
            {
                "name": "Error handling",
                "test": "Verify pipeline handles file errors gracefully"
            }
        ]