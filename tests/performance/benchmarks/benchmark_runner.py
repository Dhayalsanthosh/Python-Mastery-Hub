# tests/performance/benchmarks/benchmark_runner.py
"""
Core benchmark runner for the Python learning platform.
Provides infrastructure for running, measuring, and comparing performance benchmarks.
"""
import time
import statistics
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import psutil
import gc


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution."""
    name: str
    description: str
    iterations: int = 10
    warmup_iterations: int = 3
    timeout_seconds: int = 60
    measure_memory: bool = True
    measure_cpu: bool = True
    baseline_file: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Results from a benchmark execution."""
    name: str
    timestamp: datetime
    iterations: int
    execution_times: List[float]
    mean_time: float
    median_time: float
    std_dev: float
    min_time: float
    max_time: float
    percentile_95: float
    percentile_99: float
    memory_usage_mb: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    operations_per_second: Optional[float] = None
    baseline_comparison: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkResult":
        """Create from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class BenchmarkRunner:
    """Core benchmark runner with timing, resource monitoring, and comparison features."""
    
    def __init__(self, results_dir: str = "benchmark_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.current_results = {}
        self.baseline_results = {}
        
    async def run_benchmark(self, config: BenchmarkConfig, benchmark_func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Run a benchmark with the given configuration."""
        print(f"Running benchmark: {config.name}")
        
        # Load baseline if specified
        baseline_result = None
        if config.baseline_file:
            baseline_result = self._load_baseline(config.baseline_file)
        
        # Warmup iterations
        if config.warmup_iterations > 0:
            print(f"  Warming up ({config.warmup_iterations} iterations)...")
            for _ in range(config.warmup_iterations):
                try:
                    if asyncio.iscoroutinefunction(benchmark_func):
                        await asyncio.wait_for(benchmark_func(*args, **kwargs), timeout=config.timeout_seconds)
                    else:
                        benchmark_func(*args, **kwargs)
                except Exception as e:
                    print(f"  Warmup iteration failed: {e}")
        
        # Actual benchmark iterations
        print(f"  Running {config.iterations} benchmark iterations...")
        execution_times = []
        memory_usage = []
        cpu_usage = []
        
        for i in range(config.iterations):
            # Garbage collection before each iteration
            gc.collect()
            
            # Memory monitoring setup
            initial_memory = psutil.virtual_memory().used / (1024 * 1024) if config.measure_memory else None
            cpu_before = psutil.cpu_percent() if config.measure_cpu else None
            
            # Execute benchmark
            start_time = time.perf_counter()
            try:
                if asyncio.iscoroutinefunction(benchmark_func):
                    await asyncio.wait_for(benchmark_func(*args, **kwargs), timeout=config.timeout_seconds)
                else:
                    benchmark_func(*args, **kwargs)
            except asyncio.TimeoutError:
                print(f"  Iteration {i+1} timed out after {config.timeout_seconds}s")
                continue
            except Exception as e:
                print(f"  Iteration {i+1} failed: {e}")
                continue
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Memory monitoring
            if config.measure_memory and initial_memory is not None:
                final_memory = psutil.virtual_memory().used / (1024 * 1024)
                memory_used = final_memory - initial_memory
                memory_usage.append(memory_used)
            
            # CPU monitoring
            if config.measure_cpu and cpu_before is not None:
                cpu_after = psutil.cpu_percent()
                cpu_usage.append(cpu_after)
            
            # Progress indicator
            if (i + 1) % max(1, config.iterations // 10) == 0:
                print(f"    Completed {i+1}/{config.iterations} iterations")
        
        if not execution_times:
            raise RuntimeError(f"No successful iterations for benchmark {config.name}")
        
        # Calculate statistics
        mean_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        # Calculate percentiles
        sorted_times = sorted(execution_times)
        percentile_95 = self._percentile(sorted_times, 95)
        percentile_99 = self._percentile(sorted_times, 99)
        
        # Memory statistics
        avg_memory = statistics.mean(memory_usage) if memory_usage else None
        peak_memory = max(memory_usage) if memory_usage else None
        
        # CPU statistics
        avg_cpu = statistics.mean(cpu_usage) if cpu_usage else None
        
        # Operations per second
        ops_per_second = 1.0 / mean_time if mean_time > 0 else None
        
        # Baseline comparison
        baseline_comparison = None
        if baseline_result:
            baseline_comparison = self._compare_with_baseline(mean_time, baseline_result)
        
        # Create result
        result = BenchmarkResult(
            name=config.name,
            timestamp=datetime.now(),
            iterations=len(execution_times),
            execution_times=execution_times,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            min_time=min_time,
            max_time=max_time,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            memory_usage_mb=avg_memory,
            peak_memory_mb=peak_memory,
            cpu_usage_percent=avg_cpu,
            operations_per_second=ops_per_second,
            baseline_comparison=baseline_comparison,
            metadata={
                "config": asdict(config),
                "system_info": self._get_system_info(),
                "successful_iterations": len(execution_times),
                "failed_iterations": config.iterations - len(execution_times)
            }
        )
        
        # Save result
        self._save_result(result)
        
        # Print summary
        self._print_result_summary(result)
        
        return result
    
    def run_benchmark_suite(self, benchmarks: Dict[str, tuple]) -> Dict[str, BenchmarkResult]:
        """Run a suite of benchmarks."""
        results = {}
        
        print(f"Running benchmark suite with {len(benchmarks)} benchmarks")
        print("=" * 60)
        
        for name, (config, func, args, kwargs) in benchmarks.items():
            try:
                if asyncio.iscoroutinefunction(func):
                    result = asyncio.run(self.run_benchmark(config, func, *args, **kwargs))
                else:
                    result = asyncio.run(self.run_benchmark(config, func, *args, **kwargs))
                results[name] = result
            except Exception as e:
                print(f"Benchmark {name} failed: {e}")
                results[name] = None
            
            print("-" * 60)
        
        # Generate suite summary
        self._print_suite_summary(results)
        
        return results
    
    def compare_results(self, result1: BenchmarkResult, result2: BenchmarkResult) -> Dict[str, Any]:
        """Compare two benchmark results."""
        if result1.name != result2.name:
            raise ValueError("Can only compare results from the same benchmark")
        
        time_ratio = result2.mean_time / result1.mean_time
        time_diff_percent = (time_ratio - 1.0) * 100
        
        memory_ratio = None
        memory_diff_percent = None
        if result1.memory_usage_mb and result2.memory_usage_mb:
            memory_ratio = result2.memory_usage_mb / result1.memory_usage_mb
            memory_diff_percent = (memory_ratio - 1.0) * 100
        
        return {
            "benchmark_name": result1.name,
            "result1_timestamp": result1.timestamp,
            "result2_timestamp": result2.timestamp,
            "time_comparison": {
                "result1_mean_ms": result1.mean_time * 1000,
                "result2_mean_ms": result2.mean_time * 1000,
                "ratio": time_ratio,
                "percent_change": time_diff_percent,
                "interpretation": self._interpret_performance_change(time_diff_percent)
            },
            "memory_comparison": {
                "result1_memory_mb": result1.memory_usage_mb,
                "result2_memory_mb": result2.memory_usage_mb,
                "ratio": memory_ratio,
                "percent_change": memory_diff_percent
            } if memory_ratio else None,
            "operations_per_second": {
                "result1_ops": result1.operations_per_second,
                "result2_ops": result2.operations_per_second,
                "ratio": result2.operations_per_second / result1.operations_per_second if result1.operations_per_second and result2.operations_per_second else None
            }
        }
    
    def generate_performance_report(self, results: Dict[str, BenchmarkResult], 
                                  output_file: Optional[str] = None) -> str:
        """Generate a comprehensive performance report."""
        report_lines = []
        report_lines.append("# Performance Benchmark Report")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary table
        report_lines.append("## Benchmark Summary")
        report_lines.append("")
        report_lines.append("| Benchmark | Mean Time (ms) | Ops/sec | Memory (MB) | Status |")
        report_lines.append("|-----------|----------------|---------|-------------|--------|")
        
        for name, result in results.items():
            if result:
                status = "✓ PASS"
                if result.baseline_comparison:
                    regression = result.baseline_comparison.get("performance_regression", False)
                    if regression:
                        status = "⚠ REGRESSION"
                
                ops_per_sec = f"{result.operations_per_second:.2f}" if result.operations_per_second else "N/A"
                memory = f"{result.memory_usage_mb:.2f}" if result.memory_usage_mb else "N/A"
                
                report_lines.append(
                    f"| {name} | {result.mean_time * 1000:.2f} | {ops_per_sec} | {memory} | {status} |"
                )
            else:
                report_lines.append(f"| {name} | FAILED | - | - | ✗ FAIL |")
        
        report_lines.append("")
        
        # Detailed results
        report_lines.append("## Detailed Results")
        report_lines.append("")
        
        for name, result in results.items():
            if result:
                report_lines.append(f"### {name}")
                report_lines.append("")
                report_lines.append(f"- **Mean execution time**: {result.mean_time * 1000:.3f} ms")
                report_lines.append(f"- **Median execution time**: {result.median_time * 1000:.3f} ms")
                report_lines.append(f"- **Standard deviation**: {result.std_dev * 1000:.3f} ms")
                report_lines.append(f"- **Min/Max time**: {result.min_time * 1000:.3f} / {result.max_time * 1000:.3f} ms")
                report_lines.append(f"- **95th percentile**: {result.percentile_95 * 1000:.3f} ms")
                report_lines.append(f"- **99th percentile**: {result.percentile_99 * 1000:.3f} ms")
                
                if result.operations_per_second:
                    report_lines.append(f"- **Operations per second**: {result.operations_per_second:.2f}")
                
                if result.memory_usage_mb:
                    report_lines.append(f"- **Average memory usage**: {result.memory_usage_mb:.2f} MB")
                    report_lines.append(f"- **Peak memory usage**: {result.peak_memory_mb:.2f} MB")
                
                if result.baseline_comparison:
                    comp = result.baseline_comparison
                    report_lines.append(f"- **Baseline comparison**: {comp['percent_change']:+.1f}% change")
                    if comp.get('performance_regression'):
                        report_lines.append("  - ⚠️ **Performance regression detected**")
                
                report_lines.append(f"- **Iterations completed**: {result.iterations}")
                report_lines.append("")
        
        # System information
        system_info = self._get_system_info()
        report_lines.append("## System Information")
        report_lines.append("")
        report_lines.append(f"- **Python version**: {system_info['python_version']}")
        report_lines.append(f"- **Platform**: {system_info['platform']}")
        report_lines.append(f"- **CPU**: {system_info['cpu_model']} ({system_info['cpu_cores']} cores)")
        report_lines.append(f"- **Memory**: {system_info['total_memory_gb']:.1f} GB")
        report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_content)
            print(f"Performance report saved to: {output_file}")
        
        return report_content
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not data:
            return 0.0
        
        index = (percentile / 100) * (len(data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(data) - 1)
        
        if lower_index == upper_index:
            return data[lower_index]
        
        weight = index - lower_index
        return data[lower_index] * (1 - weight) + data[upper_index] * weight
    
    def _compare_with_baseline(self, current_time: float, baseline_result: BenchmarkResult) -> Dict[str, Any]:
        """Compare current result with baseline."""
        baseline_time = baseline_result.mean_time
        ratio = current_time / baseline_time
        percent_change = (ratio - 1.0) * 100
        
        # Define regression threshold (e.g., 10% slower)
        regression_threshold = 10.0
        performance_regression = percent_change > regression_threshold
        
        return {
            "baseline_time_ms": baseline_time * 1000,
            "current_time_ms": current_time * 1000,
            "ratio": ratio,
            "percent_change": percent_change,
            "performance_regression": performance_regression,
            "baseline_timestamp": baseline_result.timestamp.isoformat()
        }
    
    def _interpret_performance_change(self, percent_change: float) -> str:
        """Interpret performance change percentage."""
        if percent_change < -20:
            return "Significant improvement"
        elif percent_change < -5:
            return "Improvement"
        elif percent_change < 5:
            return "No significant change"
        elif percent_change < 20:
            return "Performance degradation"
        else:
            return "Significant performance degradation"
    
    def _save_result(self, result: BenchmarkResult):
        """Save benchmark result to file."""
        filename = f"{result.name}_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        print(f"  Result saved to: {filepath}")
    
    def _load_baseline(self, baseline_file: str) -> Optional[BenchmarkResult]:
        """Load baseline result from file."""
        try:
            baseline_path = Path(baseline_file)
            if not baseline_path.exists():
                print(f"  Baseline file not found: {baseline_file}")
                return None
            
            with open(baseline_path, 'r') as f:
                data = json.load(f)
            
            return BenchmarkResult.from_dict(data)
        except Exception as e:
            print(f"  Error loading baseline: {e}")
            return None
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context."""
        import platform
        import sys
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "cpu_model": platform.processor() or "Unknown",
            "cpu_cores": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "timestamp": datetime.now().isoformat()
        }
    
    def _print_result_summary(self, result: BenchmarkResult):
        """Print a summary of benchmark results."""
        print(f"  Results for {result.name}:")
        print(f"    Mean time: {result.mean_time * 1000:.3f} ms")
        print(f"    Std dev: {result.std_dev * 1000:.3f} ms")
        print(f"    95th percentile: {result.percentile_95 * 1000:.3f} ms")
        
        if result.operations_per_second:
            print(f"    Operations/sec: {result.operations_per_second:.2f}")
        
        if result.memory_usage_mb:
            print(f"    Memory usage: {result.memory_usage_mb:.2f} MB")
        
        if result.baseline_comparison:
            comp = result.baseline_comparison
            change_str = f"{comp['percent_change']:+.1f}%"
            if comp.get('performance_regression'):
                change_str += " (REGRESSION)"
            print(f"    vs Baseline: {change_str}")
    
    def _print_suite_summary(self, results: Dict[str, BenchmarkResult]):
        """Print summary of benchmark suite results."""
        print("\nBenchmark Suite Summary:")
        print("=" * 60)
        
        successful = sum(1 for r in results.values() if r is not None)
        failed = len(results) - successful
        
        print(f"Total benchmarks: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if successful > 0:
            all_times = []
            for result in results.values():
                if result:
                    all_times.append(result.mean_time)
            
            if all_times:
                print(f"Average execution time: {statistics.mean(all_times) * 1000:.3f} ms")
                print(f"Total execution time: {sum(all_times):.3f} s")
        
        # Check for regressions
        regressions = []
        for name, result in results.items():
            if result and result.baseline_comparison:
                if result.baseline_comparison.get('performance_regression'):
                    regressions.append(name)
        
        if regressions:
            print(f"\n⚠️  Performance regressions detected in: {', '.join(regressions)}")
        else:
            print("\n✓ No performance regressions detected")


# Utility decorators for easy benchmarking
def benchmark(name: str, iterations: int = 10, **config_kwargs):
    """Decorator to mark functions for benchmarking."""
    def decorator(func):
        func._benchmark_config = BenchmarkConfig(
            name=name,
            description=func.__doc__ or "",
            iterations=iterations,
            **config_kwargs
        )
        return func
    return decorator


def async_benchmark(name: str, iterations: int = 10, **config_kwargs):
    """Decorator to mark async functions for benchmarking."""
    def decorator(func):
        func._benchmark_config = BenchmarkConfig(
            name=name,
            description=func.__doc__ or "",
            iterations=iterations,
            **config_kwargs
        )
        return func
    return decorator


# Example usage functions
def create_simple_benchmark_suite() -> Dict[str, tuple]:
    """Create a simple benchmark suite for demonstration."""
    runner = BenchmarkRunner()
    
    def cpu_intensive_task():
        """CPU intensive calculation."""
        result = 0
        for i in range(100000):
            result += i * i
        return result
    
    async def async_task():
        """Async task simulation."""
        await asyncio.sleep(0.01)
        return "completed"
    
    def memory_allocation_task():
        """Memory allocation test."""
        data = [i for i in range(10000)]
        return len(data)
    
    return {
        "cpu_intensive": (
            BenchmarkConfig("cpu_intensive", "CPU intensive calculation", iterations=5),
            cpu_intensive_task,
            (),
            {}
        ),
        "async_task": (
            BenchmarkConfig("async_task", "Async task performance", iterations=10),
            async_task,
            (),
            {}
        ),
        "memory_allocation": (
            BenchmarkConfig("memory_allocation", "Memory allocation performance", iterations=8),
            memory_allocation_task,
            (),
            {}
        )
    }


if __name__ == "__main__":
    # Example benchmark execution
    runner = BenchmarkRunner()
    suite = create_simple_benchmark_suite()
    results = runner.run_benchmark_suite(suite)
    
    # Generate report
    report = runner.generate_performance_report(results, "benchmark_report.md")
    print(f"\nBenchmark suite completed. Report generated.")