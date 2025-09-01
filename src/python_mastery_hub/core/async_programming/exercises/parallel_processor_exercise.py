"""
Parallel Data Processing Exercise - Build multiprocessing data processing pipeline.
"""

import multiprocessing as mp
import time
import math
import random
import psutil
import os
from typing import List, Any, Callable, Optional, Tuple, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field


@dataclass
class ProcessingStats:
    """Comprehensive statistics for processing operations."""
    total_items: int
    processing_time: float
    items_per_second: float
    num_processes: int
    memory_usage_mb: float = 0.0
    cpu_utilization: float = 0.0
    overhead_time: float = 0.0
    efficiency: float = 0.0


@dataclass
class ChunkResult:
    """Result from processing a data chunk."""
    chunk_id: int
    original_size: int
    processed_size: int
    results: List[Any]
    process_id: int
    processing_time: float
    memory_used_mb: float = 0.0


class ProgressTracker:
    """Advanced progress tracking with ETA calculation."""
    
    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.processed_items = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = 1.0  # Update every second
    
    def update(self, increment: int = 1):
        """Update progress with intelligent update frequency."""
        self.processed_items += increment
        current_time = time.time()
        
        if (current_time - self.last_update >= self.update_interval or 
            self.processed_items == self.total_items):
            self._print_progress()
            self.last_update = current_time
    
    def _print_progress(self):
        """Print detailed progress information."""
        if self.processed_items == 0:
            return
            
        elapsed = time.time() - self.start_time
        percentage = (self.processed_items / self.total_items) * 100
        rate = self.processed_items / elapsed if elapsed > 0 else 0
        
        if self.processed_items < self.total_items:
            eta = (self.total_items - self.processed_items) / rate if rate > 0 else 0
            print(f"{self.description}: {self.processed_items:,}/{self.total_items:,} "
                  f"({percentage:.1f}%) - {rate:.1f} items/sec - ETA: {eta:.1f}s")
        else:
            print(f"{self.description}: Completed {self.total_items:,} items "
                  f"in {elapsed:.2f}s ({rate:.1f} items/sec)")


class ParallelDataProcessor:
    """Advanced parallel data processor with comprehensive features."""
    
    def __init__(self, num_processes: Optional[int] = None, chunk_size: Optional[int] = None,
                 enable_monitoring: bool = True):
        self.num_processes = num_processes or mp.cpu_count()
        self.chunk_size = chunk_size
        self.enable_monitoring = enable_monitoring
        
        print(f"Parallel processor initialized:")
        print(f"  Available CPU cores: {mp.cpu_count()}")
        print(f"  Using processes: {self.num_processes}")
        print(f"  Monitoring enabled: {self.enable_monitoring}")
    
    def _calculate_optimal_chunk_size(self, data_size: int) -> int:
        """Calculate optimal chunk size based on data size and CPU count."""
        if self.chunk_size:
            return self.chunk_size
        
        # Heuristic: aim for 4x more chunks than processes for load balancing
        target_chunks = self.num_processes * 4
        calculated_size = max(1, data_size // target_chunks)
        
        # Ensure minimum chunk size for efficiency
        min_chunk_size = 10
        optimal_size = max(min_chunk_size, calculated_size)
        
        print(f"Calculated optimal chunk size: {optimal_size} "
              f"(will create ~{data_size // optimal_size} chunks)")
        
        return optimal_size
    
    def _chunk_data(self, data: List[Any], chunk_size: Optional[int] = None) -> List[Tuple[int, List[Any]]]:
        """Split data into intelligently sized chunks."""
        effective_chunk_size = chunk_size or self._calculate_optimal_chunk_size(len(data))
        
        chunks = []
        for i in range(0, len(data), effective_chunk_size):
            chunk_data = data[i:i + effective_chunk_size]
            chunks.append((len(chunks), chunk_data))  # (chunk_id, data)
        
        return chunks
    
    def process_data_sequential(self, data: List[Any], processor_func: Callable) -> Tuple[List[Any], ProcessingStats]:
        """Process data sequentially with comprehensive monitoring."""
        print(f"Sequential processing of {len(data):,} items...")
        
        # Memory monitoring
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        results = []
        
        # Progress tracking
        progress = ProgressTracker(len(data), "Sequential processing")
        
        for i, item in enumerate(data):
            result = processor_func(item)
            results.append(result)
            
            if (i + 1) % max(1, len(data) // 20) == 0:  # Update every 5%
                progress.update(max(1, len(data) // 20))
        
        if len(data) % max(1, len(data) // 20) != 0:
            progress.update(len(data) % max(1, len(data) // 20))
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Final memory measurement
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_used = final_memory - initial_memory
        
        stats = ProcessingStats(
            total_items=len(data),
            processing_time=processing_time,
            items_per_second=len(data) / processing_time,
            num_processes=1,
            memory_usage_mb=memory_used,
            cpu_utilization=100.0,  # Single process uses one core fully
            efficiency=100.0
        )
        
        return results, stats
    
    @staticmethod
    def _process_chunk_with_monitoring(chunk_data: Tuple[int, List[Any]], processor_func: Callable) -> ChunkResult:
        """Process a single chunk with detailed monitoring."""
        chunk_id, data = chunk_data
        
        # Monitor process info
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        start_time = time.time()
        
        # Process the chunk
        results = []
        for item in data:
            result = processor_func(item)
            results.append(result)
        
        processing_time = time.time() - start_time
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_used = final_memory - initial_memory
        
        return ChunkResult(
            chunk_id=chunk_id,
            original_size=len(data),
            processed_size=len(results),
            results=results,
            process_id=os.getpid(),
            processing_time=processing_time,
            memory_used_mb=memory_used
        )
    
    def process_data_parallel(self, data: List[Any], processor_func: Callable) -> Tuple[List[Any], ProcessingStats]:
        """Process data in parallel with comprehensive monitoring."""
        print(f"Parallel processing of {len(data):,} items using {self.num_processes} processes...")
        
        start_time = time.time()
        
        # Chunk the data
        chunks = self._chunk_data(data)
        chunk_setup_time = time.time() - start_time
        
        print(f"Data split into {len(chunks)} chunks (setup time: {chunk_setup_time:.3f}s)")
        
        # Process chunks in parallel
        parallel_start = time.time()
        
        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(self._process_chunk_with_monitoring, chunk, processor_func): i 
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results with progress tracking
            chunk_results = [None] * len(chunks)
            progress = ProgressTracker(len(chunks), "Processing chunks")
            
            for future in as_completed(future_to_chunk):
                chunk_index = future_to_chunk[future]
                try:
                    chunk_result = future.result()
                    chunk_results[chunk_index] = chunk_result
                    progress.update(1)
                    
                except Exception as e:
                    print(f"Chunk {chunk_index} failed: {e}")
                    # Create empty result for failed chunk
                    chunk_results[chunk_index] = ChunkResult(
                        chunk_id=chunk_index,
                        original_size=len(chunks[chunk_index][1]),
                        processed_size=0,
                        results=[],
                        process_id=-1,
                        processing_time=0.0
                    )
        
        parallel_end = time.time()
        
        # Flatten results maintaining original order
        all_results = []
        total_chunk_time = 0.0
        total_memory_used = 0.0
        
        for chunk_result in chunk_results:
            if chunk_result and chunk_result.results:
                all_results.extend(chunk_result.results)
                total_chunk_time += chunk_result.processing_time
                total_memory_used += chunk_result.memory_used_mb
        
        total_time = time.time() - start_time
        parallel_processing_time = parallel_end - parallel_start
        overhead_time = total_time - parallel_processing_time
        
        # Calculate efficiency metrics
        theoretical_sequential_time = total_chunk_time
        speedup = theoretical_sequential_time / parallel_processing_time if parallel_processing_time > 0 else 0
        efficiency = (speedup / self.num_processes) * 100
        
        stats = ProcessingStats(
            total_items=len(data),
            processing_time=total_time,
            items_per_second=len(data) / total_time,
            num_processes=self.num_processes,
            memory_usage_mb=total_memory_used,
            overhead_time=overhead_time,
            efficiency=efficiency
        )
        
        # Print chunk distribution analysis
        self._analyze_chunk_distribution(chunk_results)
        
        return all_results, stats
    
    def _analyze_chunk_distribution(self, chunk_results: List[ChunkResult]):
        """Analyze how work was distributed across processes."""
        if not chunk_results:
            return
        
        print(f"\nChunk Distribution Analysis:")
        
        # Group by process
        process_work = {}
        for result in chunk_results:
            if result:
                pid = result.process_id
                if pid not in process_work:
                    process_work[pid] = []
                process_work[pid].append(result)
        
        print(f"Work distributed across {len(process_work)} processes:")
        
        total_items = sum(r.processed_size for r in chunk_results if r)
        total_time = sum(r.processing_time for r in chunk_results if r)
        
        for pid, results in process_work.items():
            items_processed = sum(r.processed_size for r in results)
            time_spent = sum(r.processing_time for r in results)
            memory_used = sum(r.memory_used_mb for r in results)
            
            percentage = (items_processed / total_items) * 100 if total_items > 0 else 0
            
            print(f"  PID {pid}: {len(results)} chunks, {items_processed} items ({percentage:.1f}%), "
                  f"{time_spent:.2f}s, {memory_used:.1f}MB")
    
    def benchmark_performance(self, data: List[Any], processor_func: Callable, 
                            runs: int = 1, compare_chunk_sizes: bool = False):
        """Compare sequential vs parallel performance comprehensively."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE PERFORMANCE BENCHMARK")
        print("=" * 80)
        
        all_results = {}
        
        for run in range(runs):
            if runs > 1:
                print(f"\n--- RUN {run + 1}/{runs} ---")
            
            # Sequential processing
            seq_results, seq_stats = self.process_data_sequential(data, processor_func)
            
            print("\n" + "-" * 60)
            
            # Parallel processing
            par_results, par_stats = self.process_data_parallel(data, processor_func)
            
            # Verify results are the same
            if seq_results == par_results:
                print("\n✓ Results verification: PASSED")
            else:
                print("\n✗ Results verification: FAILED")
                print(f"  Sequential items: {len(seq_results)}")
                print(f"  Parallel items: {len(par_results)}")
            
            # Store results
            all_results[f"run_{run}"] = {
                "sequential": seq_stats,
                "parallel": par_stats
            }
        
        # Calculate averages if multiple runs
        if runs > 1:
            self._print_multi_run_analysis(all_results)
        else:
            self._print_performance_analysis(seq_stats, par_stats)
        
        # Optional chunk size comparison
        if compare_chunk_sizes:
            self._compare_chunk_sizes(data, processor_func)
    
    def _print_performance_analysis(self, seq_stats: ProcessingStats, par_stats: ProcessingStats):
        """Print detailed performance analysis."""
        speedup = seq_stats.processing_time / par_stats.processing_time
        efficiency = speedup / self.num_processes
        throughput_improvement = par_stats.items_per_second / seq_stats.items_per_second
        
        print(f"\n" + "=" * 80)
        print("PERFORMANCE ANALYSIS")
        print("=" * 80)
        
        print(f"Sequential Processing:")
        print(f"  Time: {seq_stats.processing_time:.3f}s")
        print(f"  Throughput: {seq_stats.items_per_second:.1f} items/sec")
        print(f"  Memory usage: {seq_stats.memory_usage_mb:.1f} MB")
        
        print(f"\nParallel Processing ({par_stats.num_processes} processes):")
        print(f"  Time: {par_stats.processing_time:.3f}s")
        print(f"  Throughput: {par_stats.items_per_second:.1f} items/sec")
        print(f"  Memory usage: {par_stats.memory_usage_mb:.1f} MB")
        print(f"  Overhead time: {par_stats.overhead_time:.3f}s")
        print(f"  Efficiency: {par_stats.efficiency:.1f}%")
        
        print(f"\nPerformance Metrics:")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Parallel efficiency: {efficiency:.1%}")
        print(f"  Throughput improvement: {throughput_improvement:.2f}x")
        
        # Performance recommendations
        print(f"\nRecommendations:")
        if efficiency < 0.5:
            print("  • Low efficiency suggests overhead dominates - consider larger chunks or fewer processes")
        elif efficiency > 0.9:
            print("  • Excellent efficiency - well-suited for parallelization")
        
        if par_stats.overhead_time > par_stats.processing_time * 0.2:
            print("  • High overhead detected - consider optimizing data serialization")
        
        if speedup < 2 and self.num_processes >= 4:
            print("  • Limited speedup suggests CPU-bound bottlenecks or insufficient work per item")
    
    def _print_multi_run_analysis(self, all_results: Dict[str, Any]):
        """Print analysis for multiple runs."""
        seq_times = [all_results[f"run_{i}"]["sequential"].processing_time for i in range(len(all_results))]
        par_times = [all_results[f"run_{i}"]["parallel"].processing_time for i in range(len(all_results))]
        
        seq_avg = sum(seq_times) / len(seq_times)
        par_avg = sum(par_times) / len(par_times)
        
        print(f"\n" + "=" * 80)
        print(f"MULTI-RUN ANALYSIS ({len(all_results)} runs)")
        print("=" * 80)
        
        print(f"Sequential Processing (average):")
        print(f"  Time: {seq_avg:.3f}s (±{max(seq_times) - min(seq_times):.3f}s)")
        
        print(f"\nParallel Processing (average):")
        print(f"  Time: {par_avg:.3f}s (±{max(par_times) - min(par_times):.3f}s)")
        
        avg_speedup = seq_avg / par_avg
        print(f"\nAverage speedup: {avg_speedup:.2f}x")
    
    def _compare_chunk_sizes(self, data: List[Any], processor_func: Callable):
        """Compare performance with different chunk sizes."""
        print(f"\n" + "=" * 80)
        print("CHUNK SIZE COMPARISON")
        print("=" * 80)
        
        original_chunk_size = self.chunk_size
        chunk_sizes = [10, 50, 100, 200, None]  # None = auto-calculated
        
        results = {}
        
        for chunk_size in chunk_sizes:
            self.chunk_size = chunk_size
            print(f"\nTesting chunk size: {chunk_size or 'auto'}")
            
            _, stats = self.process_data_parallel(data, processor_func)
            results[chunk_size or 'auto'] = stats.processing_time
        
        # Restore original chunk size
        self.chunk_size = original_chunk_size
        
        # Print comparison
        print(f"\nChunk Size Performance:")
        for chunk_size, processing_time in results.items():
            print(f"  {chunk_size}: {processing_time:.3f}s")
        
        best_chunk_size = min(results.keys(), key=lambda k: results[k])
        print(f"\nBest chunk size: {best_chunk_size}")


# Example processing functions for testing
def cpu_intensive_function(n: int) -> int:
    """CPU-intensive function for testing parallelization."""
    return sum(i * i for i in range(n))


def complex_math_function(x: float) -> float:
    """Complex mathematical function for testing."""
    result = 0
    for i in range(1000):
        result += math.sin(x * i) * math.cos(x * i) / (i + 1)
    return result


def simulate_data_processing(item: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate realistic data processing task."""
    # Simulate CPU-intensive data transformation
    data = item.get('data', 0)
    processed = 0
    
    # Some mathematical operations
    for i in range(100):
        processed += math.sqrt(data * i + 1) * math.log(i + 1)
    
    # Simulate some I/O delay
    time.sleep(0.001)
    
    return {
        'original': item,
        'processed_value': processed,
        'timestamp': time.time(),
        'process_id': os.getpid()
    }


def demo_parallel_processing():
    """Comprehensive demonstration of parallel processing capabilities."""
    print("=" * 100)
    print("PARALLEL DATA PROCESSING DEMONSTRATION")
    print("=" * 100)
    
    processor = ParallelDataProcessor(num_processes=4)
    
    # Demo 1: CPU-intensive function
    print("\nDEMO 1: CPU-Intensive Processing")
    print("-" * 50)
    test_data_1 = list(range(1000, 3000, 50))  # 40 items
    processor.benchmark_performance(test_data_1, cpu_intensive_function)
    
    # Demo 2: Complex math function
    print("\nDEMO 2: Complex Mathematical Processing")
    print("-" * 50)
    test_data_2 = [x * 0.1 for x in range(100)]  # 100 items
    processor.benchmark_performance(test_data_2, complex_math_function)
    
    # Demo 3: Realistic data processing
    print("\nDEMO 3: Realistic Data Processing Simulation")
    print("-" * 50)
    test_data_3 = [{'id': i, 'data': random.randint(1, 1000)} for i in range(200)]
    processor.benchmark_performance(test_data_3, simulate_data_processing)
    
    # Demo 4: Chunk size comparison
    print("\nDEMO 4: Chunk Size Optimization")
    print("-" * 50)
    small_processor = ParallelDataProcessor(num_processes=2)
    small_processor.benchmark_performance(
        test_data_1[:20], 
        cpu_intensive_function, 
        compare_chunk_sizes=True
    )


if __name__ == "__main__":
    demo_parallel_processing()