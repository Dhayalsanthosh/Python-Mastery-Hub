# src/python_mastery_hub/utils/metrics_collector.py
"""
Metrics Collection Utilities - Application Performance and Usage Metrics

Provides comprehensive metrics collection for monitoring application performance,
user engagement, learning analytics, and system health indicators.
"""

import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
import json
import statistics
import logging
from contextlib import contextmanager
import psutil
import sys

logger = logging.getLogger(__name__)


@dataclass
class MetricEvent:
    """Represents a single metric event."""
    name: str
    value: Union[int, float, str]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    event_type: str = 'gauge'  # gauge, counter, histogram, timer
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp,
            'labels': self.labels,
            'event_type': self.event_type,
            'unit': self.unit
        }


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    count: int
    min_value: float
    max_value: float
    avg_value: float
    sum_value: float
    percentiles: Dict[str, float]
    last_updated: float


class MetricStore:
    """Stores and manages metric data."""
    
    def __init__(self, max_events_per_metric: int = 10000):
        self.max_events_per_metric = max_events_per_metric
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events_per_metric))
        self._counters: Dict[str, float] = defaultdict(float)
        self._lock = threading.RLock()
    
    def add_event(self, event: MetricEvent) -> None:
        """Add metric event to store."""
        with self._lock:
            metric_key = f"{event.name}:{json.dumps(event.labels, sort_keys=True)}"
            
            if event.event_type == 'counter':
                self._counters[metric_key] += event.value
            else:
                self._metrics[metric_key].append(event)
    
    def get_events(
        self, 
        metric_name: str, 
        labels: Optional[Dict[str, str]] = None,
        since: Optional[float] = None
    ) -> List[MetricEvent]:
        """Get events for a metric."""
        with self._lock:
            labels = labels or {}
            metric_key = f"{metric_name}:{json.dumps(labels, sort_keys=True)}"
            
            events = list(self._metrics.get(metric_key, []))
            
            if since:
                events = [e for e in events if e.timestamp >= since]
            
            return events
    
    def get_counter_value(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        with self._lock:
            labels = labels or {}
            metric_key = f"{metric_name}:{json.dumps(labels, sort_keys=True)}"
            return self._counters.get(metric_key, 0.0)
    
    def get_summary(
        self, 
        metric_name: str, 
        labels: Optional[Dict[str, str]] = None,
        since: Optional[float] = None
    ) -> Optional[MetricSummary]:
        """Get summary statistics for a metric."""
        events = self.get_events(metric_name, labels, since)
        
        if not events:
            return None
        
        values = [float(e.value) for e in events if isinstance(e.value, (int, float))]
        
        if not values:
            return None
        
        # Calculate percentiles
        percentiles = {}
        for p in [50, 90, 95, 99]:
            try:
                percentiles[f'p{p}'] = statistics.quantiles(values, n=100)[p-1]
            except statistics.StatisticsError:
                percentiles[f'p{p}'] = values[0] if values else 0
        
        return MetricSummary(
            name=metric_name,
            count=len(values),
            min_value=min(values),
            max_value=max(values),
            avg_value=statistics.mean(values),
            sum_value=sum(values),
            percentiles=percentiles,
            last_updated=events[-1].timestamp if events else 0
        )
    
    def get_all_metrics(self) -> List[str]:
        """Get list of all tracked metrics."""
        with self._lock:
            metric_names = set()
            
            # From stored events
            for key in self._metrics.keys():
                metric_name = key.split(':', 1)[0]
                metric_names.add(metric_name)
            
            # From counters
            for key in self._counters.keys():
                metric_name = key.split(':', 1)[0]
                metric_names.add(metric_name)
            
            return sorted(metric_names)
    
    def clear_old_events(self, older_than_hours: int = 24) -> int:
        """Clear events older than specified hours."""
        cutoff_time = time.time() - (older_than_hours * 3600)
        removed_count = 0
        
        with self._lock:
            for metric_key in list(self._metrics.keys()):
                original_len = len(self._metrics[metric_key])
                
                # Filter out old events
                self._metrics[metric_key] = deque(
                    (e for e in self._metrics[metric_key] if e.timestamp >= cutoff_time),
                    maxlen=self.max_events_per_metric
                )
                
                removed_count += original_len - len(self._metrics[metric_key])
                
                # Remove empty metric keys
                if not self._metrics[metric_key]:
                    del self._metrics[metric_key]
        
        return removed_count


class MetricsCollector:
    """Main metrics collection system."""
    
    def __init__(
        self, 
        store: Optional[MetricStore] = None,
        auto_system_metrics: bool = True,
        collection_interval: float = 60.0
    ):
        self.store = store or MetricStore()
        self.auto_system_metrics = auto_system_metrics
        self.collection_interval = collection_interval
        
        # Background collection
        self._collection_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Async event queue for high-throughput scenarios
        self._event_queue: queue.Queue = queue.Queue()
        self._queue_processor: Optional[threading.Thread] = None
        
        # Start background threads
        self.start_collection()
    
    def start_collection(self) -> None:
        """Start background metric collection."""
        if self._collection_thread and self._collection_thread.is_alive():
            return
        
        self._shutdown_event.clear()
        
        # Start system metrics collection thread
        if self.auto_system_metrics:
            self._collection_thread = threading.Thread(
                target=self._collect_system_metrics_loop,
                daemon=True
            )
            self._collection_thread.start()
        
        # Start event queue processor
        self._queue_processor = threading.Thread(
            target=self._process_event_queue,
            daemon=True
        )
        self._queue_processor.start()
    
    def stop_collection(self) -> None:
        """Stop background metric collection."""
        self._shutdown_event.set()
        
        if self._collection_thread and self._collection_thread.is_alive():
            self._collection_thread.join(timeout=5)
        
        if self._queue_processor and self._queue_processor.is_alive():
            self._queue_processor.join(timeout=5)
    
    def record_gauge(
        self, 
        name: str, 
        value: Union[int, float], 
        labels: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None
    ) -> None:
        """Record a gauge metric (point-in-time value)."""
        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            event_type='gauge',
            unit=unit
        )
        self._event_queue.put(event)
    
    def record_counter(
        self, 
        name: str, 
        value: Union[int, float] = 1, 
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a counter metric (cumulative value)."""
        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            event_type='counter'
        )
        self._event_queue.put(event)
    
    def record_timer(
        self, 
        name: str, 
        duration_seconds: float, 
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a timer metric (duration measurement)."""
        event = MetricEvent(
            name=name,
            value=duration_seconds,
            timestamp=time.time(),
            labels=labels or {},
            event_type='timer',
            unit='seconds'
        )
        self._event_queue.put(event)
    
    def record_histogram(
        self, 
        name: str, 
        value: Union[int, float], 
        labels: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None
    ) -> None:
        """Record a histogram metric (distribution of values)."""
        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            event_type='histogram',
            unit=unit
        )
        self._event_queue.put(event)
    
    @contextmanager
    def time_operation(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager to time an operation."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_timer(name, duration, labels)
    
    def get_metric_summary(
        self, 
        name: str, 
        labels: Optional[Dict[str, str]] = None,
        since_hours: Optional[int] = None
    ) -> Optional[MetricSummary]:
        """Get summary for a metric."""
        since = time.time() - (since_hours * 3600) if since_hours else None
        return self.store.get_summary(name, labels, since)
    
    def get_counter_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        return self.store.get_counter_value(name, labels)
    
    def get_all_metrics(self) -> List[str]:
        """Get list of all metrics."""
        return self.store.get_all_metrics()
    
    def _process_event_queue(self) -> None:
        """Process events from the queue."""
        while not self._shutdown_event.is_set():
            try:
                event = self._event_queue.get(timeout=1.0)
                self.store.add_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing metric event: {e}")
    
    def _collect_system_metrics_loop(self) -> None:
        """Background loop to collect system metrics."""
        while not self._shutdown_event.wait(self.collection_interval):
            try:
                self._collect_system_metrics()
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_system_metrics(self) -> None:
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_gauge('system.cpu.usage_percent', cpu_percent, unit='percent')
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_gauge('system.memory.usage_percent', memory.percent, unit='percent')
            self.record_gauge('system.memory.available_bytes', memory.available, unit='bytes')
            self.record_gauge('system.memory.used_bytes', memory.used, unit='bytes')
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.record_gauge('system.disk.usage_percent', (disk.used / disk.total) * 100, unit='percent')
            self.record_gauge('system.disk.free_bytes', disk.free, unit='bytes')
            
            # Process metrics
            process = psutil.Process()
            self.record_gauge('process.memory.rss_bytes', process.memory_info().rss, unit='bytes')
            self.record_gauge('process.cpu.usage_percent', process.cpu_percent(), unit='percent')
            self.record_gauge('process.threads.count', process.num_threads())
            
            # Python-specific metrics
            import gc
            self.record_gauge('python.gc.objects', len(gc.get_objects()))
            
        except Exception as e:
            logger.warning(f"Failed to collect some system metrics: {e}")


class LearningMetricsCollector:
    """Specialized metrics collector for learning analytics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_topic_start(self, user_id: str, module_id: str, topic_name: str) -> None:
        """Record when a user starts a topic."""
        labels = {
            'user_id': user_id,
            'module_id': module_id,
            'topic_name': topic_name
        }
        self.metrics.record_counter('learning.topic.started', 1, labels)
    
    def record_topic_completion(
        self, 
        user_id: str, 
        module_id: str, 
        topic_name: str, 
        duration_minutes: float,
        score: Optional[float] = None
    ) -> None:
        """Record topic completion."""
        labels = {
            'user_id': user_id,
            'module_id': module_id,
            'topic_name': topic_name
        }
        
        self.metrics.record_counter('learning.topic.completed', 1, labels)
        self.metrics.record_histogram('learning.topic.duration_minutes', duration_minutes, labels, 'minutes')
        
        if score is not None:
            self.metrics.record_histogram('learning.topic.score', score, labels, 'percentage')
    
    def record_module_completion(self, user_id: str, module_id: str, total_time_minutes: float) -> None:
        """Record module completion."""
        labels = {
            'user_id': user_id,
            'module_id': module_id
        }
        
        self.metrics.record_counter('learning.module.completed', 1, labels)
        self.metrics.record_histogram('learning.module.duration_minutes', total_time_minutes, labels, 'minutes')
    
    def record_achievement_earned(self, user_id: str, achievement_id: str, points: int) -> None:
        """Record achievement earned."""
        labels = {
            'user_id': user_id,
            'achievement_id': achievement_id
        }
        
        self.metrics.record_counter('learning.achievement.earned', 1, labels)
        self.metrics.record_histogram('learning.achievement.points', points, labels, 'points')
    
    def record_streak_update(self, user_id: str, streak_days: int) -> None:
        """Record learning streak update."""
        labels = {'user_id': user_id}
        self.metrics.record_gauge('learning.streak.current_days', streak_days, labels, 'days')
    
    def record_code_execution(
        self, 
        user_id: str, 
        success: bool, 
        execution_time_ms: float,
        module_id: Optional[str] = None
    ) -> None:
        """Record code execution metrics."""
        labels = {
            'user_id': user_id,
            'success': str(success).lower()
        }
        
        if module_id:
            labels['module_id'] = module_id
        
        self.metrics.record_counter('learning.code.execution', 1, labels)
        self.metrics.record_histogram('learning.code.execution_time_ms', execution_time_ms, labels, 'milliseconds')
    
    def record_session_duration(self, user_id: str, duration_minutes: float) -> None:
        """Record learning session duration."""
        labels = {'user_id': user_id}
        self.metrics.record_histogram('learning.session.duration_minutes', duration_minutes, labels, 'minutes')


class ApplicationMetricsCollector:
    """Specialized metrics collector for application performance."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_request(
        self, 
        endpoint: str, 
        method: str, 
        status_code: int, 
        duration_ms: float,
        user_id: Optional[str] = None
    ) -> None:
        """Record HTTP request metrics."""
        labels = {
            'endpoint': endpoint,
            'method': method,
            'status_code': str(status_code)
        }
        
        if user_id:
            labels['user_id'] = user_id
        
        self.metrics.record_counter('app.request.count', 1, labels)
        self.metrics.record_histogram('app.request.duration_ms', duration_ms, labels, 'milliseconds')
    
    def record_database_query(
        self, 
        operation: str, 
        table: str, 
        duration_ms: float,
        success: bool = True
    ) -> None:
        """Record database query metrics."""
        labels = {
            'operation': operation,
            'table': table,
            'success': str(success).lower()
        }
        
        self.metrics.record_counter('app.database.query_count', 1, labels)
        self.metrics.record_histogram('app.database.query_duration_ms', duration_ms, labels, 'milliseconds')
    
    def record_cache_operation(
        self, 
        operation: str, 
        hit: bool, 
        duration_ms: Optional[float] = None
    ) -> None:
        """Record cache operation metrics."""
        labels = {
            'operation': operation,
            'result': 'hit' if hit else 'miss'
        }
        
        self.metrics.record_counter('app.cache.operation_count', 1, labels)
        
        if duration_ms is not None:
            self.metrics.record_histogram('app.cache.operation_duration_ms', duration_ms, labels, 'milliseconds')
    
    def record_error(
        self, 
        error_type: str, 
        component: str, 
        severity: str = 'error'
    ) -> None:
        """Record application error."""
        labels = {
            'error_type': error_type,
            'component': component,
            'severity': severity
        }
        
        self.metrics.record_counter('app.error.count', 1, labels)
    
    def record_user_login(self, user_id: str, success: bool, login_method: str = 'password') -> None:
        """Record user login attempt."""
        labels = {
            'user_id': user_id,
            'success': str(success).lower(),
            'method': login_method
        }
        
        self.metrics.record_counter('app.auth.login_attempt', 1, labels)
    
    def record_file_operation(
        self, 
        operation: str, 
        file_type: str, 
        size_bytes: Optional[int] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """Record file operation metrics."""
        labels = {
            'operation': operation,
            'file_type': file_type
        }
        
        self.metrics.record_counter('app.file.operation_count', 1, labels)
        
        if size_bytes is not None:
            self.metrics.record_histogram('app.file.size_bytes', size_bytes, labels, 'bytes')
        
        if duration_ms is not None:
            self.metrics.record_histogram('app.file.operation_duration_ms', duration_ms, labels, 'milliseconds')


class MetricsExporter:
    """Export metrics data in various formats."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for metric_name in self.metrics.get_all_metrics():
            summary = self.metrics.get_metric_summary(metric_name)
            if summary:
                # Convert metric name to Prometheus format
                prom_name = metric_name.replace('.', '_').replace('-', '_')
                
                lines.append(f"# HELP {prom_name} {metric_name}")
                lines.append(f"# TYPE {prom_name} gauge")
                lines.append(f"{prom_name}_count {summary.count}")
                lines.append(f"{prom_name}_sum {summary.sum_value}")
                lines.append(f"{prom_name}_min {summary.min_value}")
                lines.append(f"{prom_name}_max {summary.max_value}")
                lines.append(f"{prom_name}_avg {summary.avg_value}")
                
                for percentile, value in summary.percentiles.items():
                    lines.append(f"{prom_name}_{percentile} {value}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def export_json(self, since_hours: Optional[int] = None) -> str:
        """Export metrics as JSON."""
        data = {
            'timestamp': time.time(),
            'since_hours': since_hours,
            'metrics': {}
        }
        
        for metric_name in self.metrics.get_all_metrics():
            summary = self.metrics.get_metric_summary(metric_name, since_hours=since_hours)
            if summary:
                data['metrics'][metric_name] = asdict(summary)
        
        return json.dumps(data, indent=2)
    
    def export_csv(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Export specific metric events as CSV."""
        events = self.metrics.store.get_events(metric_name, labels)
        
        if not events:
            return "timestamp,value,labels\n"
        
        lines = ["timestamp,value,labels"]
        
        for event in events:
            timestamp = datetime.fromtimestamp(event.timestamp).isoformat()
            labels_str = json.dumps(event.labels) if event.labels else "{}"
            lines.append(f"{timestamp},{event.value},\"{labels_str}\"")
        
        return "\n".join(lines)


# Decorator for automatic metrics collection
def collect_metrics(
    metric_name: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    record_duration: bool = True,
    record_calls: bool = True
):
    """Decorator to automatically collect metrics for function calls."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_type = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time
                
                # Determine metric name
                name = metric_name or f"function.{func.__module__}.{func.__name__}"
                
                # Prepare labels
                func_labels = (labels or {}).copy()
                func_labels.update({
                    'function': func.__name__,
                    'success': str(success).lower()
                })
                
                if error_type:
                    func_labels['error_type'] = error_type
                
                # Record metrics
                if record_calls:
                    _default_collector.record_counter(f"{name}.calls", 1, func_labels)
                
                if record_duration:
                    _default_collector.record_timer(f"{name}.duration", duration, func_labels)
        
        return wrapper
    return decorator


# Global metrics collector instance
_default_collector = MetricsCollector()
learning_metrics = LearningMetricsCollector(_default_collector)
app_metrics = ApplicationMetricsCollector(_default_collector)


# Convenience functions
def record_gauge(name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None) -> None:
    """Record gauge metric using default collector."""
    _default_collector.record_gauge(name, value, labels)


def record_counter(name: str, value: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None) -> None:
    """Record counter metric using default collector."""
    _default_collector.record_counter(name, value, labels)


def record_timer(name: str, duration_seconds: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Record timer metric using default collector."""
    _default_collector.record_timer(name, duration_seconds, labels)


def record_histogram(name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None) -> None:
    """Record histogram metric using default collector."""
    _default_collector.record_histogram(name, value, labels)


def time_operation(name: str, labels: Optional[Dict[str, str]] = None):
    """Context manager to time operation using default collector."""
    return _default_collector.time_operation(name, labels)


def get_metric_summary(name: str, labels: Optional[Dict[str, str]] = None, since_hours: Optional[int] = None) -> Optional[MetricSummary]:
    """Get metric summary using default collector."""
    return _default_collector.get_metric_summary(name, labels, since_hours)


def get_counter_value(name: str, labels: Optional[Dict[str, str]] = None) -> float:
    """Get counter value using default collector."""
    return _default_collector.get_counter_value(name, labels)


def export_metrics_json(since_hours: Optional[int] = None) -> str:
    """Export all metrics as JSON."""
    exporter = MetricsExporter(_default_collector)
    return exporter.export_json(since_hours)


def export_metrics_prometheus() -> str:
    """Export all metrics in Prometheus format."""
    exporter = MetricsExporter(_default_collector)
    return exporter.export_prometheus()


def cleanup_old_metrics(older_than_hours: int = 24) -> int:
    """Clean up old metric events."""
    return _default_collector.store.clear_old_events(older_than_hours)


# Shutdown cleanup
import atexit
atexit.register(lambda: _default_collector.stop_collection())