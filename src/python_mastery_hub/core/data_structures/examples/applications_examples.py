"""
Practical applications examples for the Data Structures module.

This module demonstrates real-world use cases and problem-solving scenarios
where different data structures provide optimal solutions. Each example
shows practical implementation patterns and performance considerations.
"""

from collections import defaultdict, Counter, deque, OrderedDict
import heapq
import time
from typing import Dict, List, Any, Tuple, Optional


class ApplicationsExamples:
    """Practical applications examples and demonstrations."""
    
    @staticmethod
    def get_real_world_applications() -> Dict[str, Any]:
        """Get comprehensive real-world applications examples."""
        return {
            "title": "Real-World Data Structure Applications",
            "description": "Comprehensive examples showing how data structures solve practical problems",
            "applications": {
                "text_analysis": ApplicationsExamples._get_text_analysis_example(),
                "graph_algorithms": ApplicationsExamples._get_graph_algorithms_example(),
                "caching_system": ApplicationsExamples._get_caching_system_example(),
                "task_scheduling": ApplicationsExamples._get_task_scheduling_example(),
                "data_aggregation": ApplicationsExamples._get_data_aggregation_example(),
                "log_processing": ApplicationsExamples._get_log_processing_example(),
                "recommendation_engine": ApplicationsExamples._get_recommendation_engine_example(),
                "inventory_management": ApplicationsExamples._get_inventory_management_example()
            },
            "code": ApplicationsExamples._get_complete_demo_code(),
            "learning_points": [
                "Choose appropriate data structures based on access patterns",
                "Combine multiple structures for complex problems",
                "Consider performance implications of different operations",
                "Use built-in collections for efficiency and readability",
                "Design for scalability and maintainability"
            ]
        }
    
    @staticmethod
    def _get_text_analysis_example() -> Dict[str, Any]:
        """Text analysis application using Counter and defaultdict."""
        return {
            "title": "Text Analysis and Natural Language Processing",
            "use_case": "Analyze documents for word frequency, readability, and patterns",
            "data_structures": ["Counter", "defaultdict", "set"],
            "complexity": "O(n) for most operations where n is text length",
            "code": '''
def analyze_text(text):
    """Comprehensive text analysis using multiple data structures."""
    words = text.lower().split()
    
    # Word frequency analysis using Counter
    word_count = Counter(words)
    
    # Words by length using defaultdict
    by_length = defaultdict(list)
    for word in set(words):
        by_length[len(word)].append(word)
    
    # Character frequency analysis
    char_count = Counter(char for char in text.lower() if char.isalpha())
    
    # Find unique words (using set)
    unique_words = set(words)
    
    # Sentence analysis
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    return {
        'total_words': len(words),
        'unique_words': len(unique_words),
        'vocabulary_richness': len(unique_words) / len(words) if words else 0,
        'most_common': word_count.most_common(5),
        'by_length': dict(by_length),
        'char_freq': char_count.most_common(5),
        'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
        'sentence_count': len(sentences),
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0
    }

# Example usage
sample_text = """
The quick brown fox jumps over the lazy dog. The dog was very lazy and the fox was quick.
This sentence contains every letter of the alphabet at least once.
Data structures make text analysis efficient and elegant.
"""

analysis = analyze_text(sample_text)
print(f"Vocabulary richness: {analysis['vocabulary_richness']:.2f}")
print(f"Most common words: {analysis['most_common']}")
''',
            "benefits": [
                "Counter provides O(1) frequency counting",
                "defaultdict eliminates need for key checking",
                "set provides O(1) membership testing for unique words",
                "Efficient memory usage for large documents"
            ]
        }
    
    @staticmethod
    def _get_graph_algorithms_example() -> Dict[str, Any]:
        """Graph algorithms using defaultdict and deque."""
        return {
            "title": "Social Network and Graph Analysis",
            "use_case": "Analyze relationships, find shortest paths, detect communities",
            "data_structures": ["defaultdict", "deque", "heapq", "set"],
            "complexity": "BFS/DFS: O(V+E), Dijkstra: O((V+E)logV)",
            "code": '''
class SocialNetwork:
    """Social network analysis using graph data structures."""
    
    def __init__(self):
        self.graph = defaultdict(set)  # Use set to avoid duplicate connections
        self.user_data = {}
    
    def add_user(self, user_id, name, interests=None):
        """Add user to network."""
        self.user_data[user_id] = {
            'name': name,
            'interests': set(interests or []),
            'connections': set()
        }
    
    def add_connection(self, user1, user2):
        """Add bidirectional connection between users."""
        self.graph[user1].add(user2)
        self.graph[user2].add(user1)
        self.user_data[user1]['connections'].add(user2)
        self.user_data[user2]['connections'].add(user1)
    
    def find_shortest_path(self, start, end):
        """Find shortest path between two users using BFS."""
        if start == end:
            return [start]
        
        visited = set()
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in self.graph[current]:
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found
    
    def find_mutual_friends(self, user1, user2):
        """Find mutual connections between two users."""
        return self.graph[user1] & self.graph[user2]
    
    def suggest_friends(self, user_id, max_suggestions=5):
        """Suggest friends based on mutual connections and interests."""
        user_connections = self.graph[user_id]
        user_interests = self.user_data[user_id]['interests']
        
        # Count mutual friends and common interests
        suggestions = defaultdict(int)
        
        # Points for mutual friends
        for friend in user_connections:
            for friend_of_friend in self.graph[friend]:
                if friend_of_friend != user_id and friend_of_friend not in user_connections:
                    suggestions[friend_of_friend] += 1
        
        # Points for common interests
        for other_user, data in self.user_data.items():
            if other_user != user_id and other_user not in user_connections:
                common_interests = len(user_interests & data['interests'])
                suggestions[other_user] += common_interests * 2
        
        # Sort by score and return top suggestions
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return sorted_suggestions[:max_suggestions]

# Example usage
network = SocialNetwork()
network.add_user('alice', 'Alice', ['python', 'data science', 'hiking'])
network.add_user('bob', 'Bob', ['python', 'gaming', 'music'])
network.add_user('charlie', 'Charlie', ['data science', 'hiking', 'photography'])

network.add_connection('alice', 'bob')
network.add_connection('bob', 'charlie')

path = network.find_shortest_path('alice', 'charlie')
suggestions = network.suggest_friends('alice')
''',
            "benefits": [
                "defaultdict simplifies adjacency list management",
                "deque provides efficient queue operations for BFS",
                "set operations enable fast intersection for mutual friends",
                "Scalable to large social networks"
            ]
        }
    
    @staticmethod
    def _get_caching_system_example() -> Dict[str, Any]:
        """Caching system using OrderedDict."""
        return {
            "title": "Web Application Caching System",
            "use_case": "Cache frequently accessed data with LRU eviction",
            "data_structures": ["OrderedDict", "time tracking"],
            "complexity": "O(1) for get/put operations",
            "code": '''
class WebCache:
    """Production-ready caching system for web applications."""
    
    def __init__(self, capacity=1000, ttl=3600):
        self.capacity = capacity
        self.ttl = ttl  # Time to live in seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.stats = {
            'hits': 0, 'misses': 0, 'evictions': 0, 'expired': 0
        }
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if current_time - timestamp > self.ttl
        ]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                self.stats['expired'] += 1
    
    def get(self, key):
        """Get value from cache."""
        self._cleanup_expired()
        
        if key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        # Move to end (mark as recently used)
        value = self.cache[key]
        self.cache.move_to_end(key)
        self.stats['hits'] += 1
        return value
    
    def put(self, key, value):
        """Store value in cache."""
        self._cleanup_expired()
        
        if key in self.cache:
            self.cache[key] = value
            self.timestamps[key] = time.time()
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                # Remove least recently used
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
                self.stats['evictions'] += 1
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def invalidate(self, pattern=None):
        """Invalidate cache entries matching pattern."""
        if pattern is None:
            self.cache.clear()
            self.timestamps.clear()
        else:
            keys_to_remove = [key for key in self.cache if pattern in str(key)]
            for key in keys_to_remove:
                del self.cache[key]
                del self.timestamps[key]
    
    def get_stats(self):
        """Get cache performance statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': f"{hit_rate:.2f}%",
            'size': len(self.cache),
            'capacity_used': f"{len(self.cache)/self.capacity*100:.1f}%"
        }

# Decorator for automatic caching
def cached(cache_instance, key_func=None):
    """Decorator to automatically cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            result = cache_instance.get(cache_key)
            if result is not None:
                return result
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            cache_instance.put(cache_key, result)
            return result
        return wrapper
    return decorator

# Example usage
app_cache = WebCache(capacity=100, ttl=300)

@cached(app_cache)
def expensive_database_query(user_id, query_type):
    """Simulate expensive database operation."""
    time.sleep(0.1)  # Simulate database delay
    return f"Result for user {user_id}, query {query_type}"

# The second call will be cached
result1 = expensive_database_query(123, "profile")
result2 = expensive_database_query(123, "profile")  # Cache hit
''',
            "benefits": [
                "OrderedDict maintains insertion order for LRU",
                "O(1) cache operations scale to high traffic",
                "TTL prevents stale data issues",
                "Statistics enable performance monitoring"
            ]
        }
    
    @staticmethod
    def _get_task_scheduling_example() -> Dict[str, Any]:
        """Task scheduling using heapq."""
        return {
            "title": "Priority-Based Task Scheduling",
            "use_case": "Schedule tasks based on priority, deadlines, and dependencies",
            "data_structures": ["heapq", "defaultdict", "set"],
            "complexity": "O(log n) for add/remove, O(1) for peek",
            "code": '''
class TaskScheduler:
    """Advanced task scheduler with priorities and dependencies."""
    
    def __init__(self):
        self.tasks = []  # Min heap for priority queue
        self.task_counter = 0
        self.task_registry = {}  # Track all tasks by ID
        self.dependencies = defaultdict(set)  # Task dependencies
        self.completed_tasks = set()
    
    def add_task(self, priority, description, dependencies=None, deadline=None):
        """Add task with optional dependencies."""
        self.task_counter += 1
        task_id = self.task_counter
        
        task = {
            'id': task_id,
            'priority': priority,
            'description': description,
            'deadline': deadline,
            'added_time': time.time(),
            'dependencies': set(dependencies or []),
            'status': 'pending'
        }
        
        self.task_registry[task_id] = task
        
        # Only add to heap if no dependencies or all dependencies completed
        if self._can_execute(task):
            heapq.heappush(self.tasks, (priority, task_id))
        
        return task_id
    
    def _can_execute(self, task):
        """Check if task can be executed (all dependencies completed)."""
        return task['dependencies'].issubset(self.completed_tasks)
    
    def get_next_task(self):
        """Get highest priority executable task."""
        while self.tasks:
            priority, task_id = heapq.heappop(self.tasks)
            
            if task_id in self.task_registry:
                task = self.task_registry[task_id]
                if self._can_execute(task) and task['status'] == 'pending':
                    task['status'] = 'executing'
                    return task
        
        return None
    
    def complete_task(self, task_id):
        """Mark task as completed and check for newly available tasks."""
        if task_id in self.task_registry:
            self.task_registry[task_id]['status'] = 'completed'
            self.completed_tasks.add(task_id)
            
            # Check if any pending tasks can now be executed
            for tid, task in self.task_registry.items():
                if (task['status'] == 'pending' and 
                    self._can_execute(task) and 
                    not any(t[1] == tid for t in self.tasks)):
                    heapq.heappush(self.tasks, (task['priority'], tid))
    
    def get_task_stats(self):
        """Get scheduling statistics."""
        status_counts = defaultdict(int)
        for task in self.task_registry.values():
            status_counts[task['status']] += 1
        
        return {
            'total_tasks': len(self.task_registry),
            'by_status': dict(status_counts),
            'pending_in_queue': len(self.tasks),
            'completed': len(self.completed_tasks)
        }
    
    def get_blocked_tasks(self):
        """Get tasks blocked by dependencies."""
        blocked = []
        for task in self.task_registry.values():
            if (task['status'] == 'pending' and 
                not self._can_execute(task)):
                missing_deps = task['dependencies'] - self.completed_tasks
                blocked.append({
                    'task': task,
                    'waiting_for': missing_deps
                })
        return blocked

# Example: Build system task scheduling
scheduler = TaskScheduler()

# Add tasks with dependencies (like a build pipeline)
scheduler.add_task(1, "Download dependencies", [])
scheduler.add_task(2, "Compile source code", [1])  # Depends on download
scheduler.add_task(2, "Run unit tests", [2])       # Depends on compile
scheduler.add_task(3, "Generate documentation", [2])
scheduler.add_task(1, "Deploy to staging", [3])   # Depends on tests
scheduler.add_task(1, "Deploy to production", [5]) # Depends on staging

# Process tasks in order
while True:
    task = scheduler.get_next_task()
    if not task:
        break
    
    print(f"Executing: {task['description']}")
    # Simulate task execution
    time.sleep(0.1)
    scheduler.complete_task(task['id'])

print(f"Final stats: {scheduler.get_task_stats()}")
''',
            "benefits": [
                "heapq provides efficient priority queue operations",
                "Handles complex dependency relationships",
                "Scales to thousands of tasks",
                "Supports dynamic task addition during execution"
            ]
        }
    
    @staticmethod
    def _get_data_aggregation_example() -> Dict[str, Any]:
        """Data aggregation using multiple structures."""
        return {
            "title": "Business Intelligence and Data Aggregation",
            "use_case": "Analyze sales data with multiple dimensions and metrics",
            "data_structures": ["defaultdict", "Counter", "OrderedDict"],
            "complexity": "O(n) for most aggregations where n is record count",
            "code": '''
class SalesAnalyzer:
    """Comprehensive sales data analysis system."""
    
    def __init__(self):
        self.raw_data = []
        self.processed_metrics = {}
    
    def add_sales_data(self, sales_records):
        """Add sales records for analysis."""
        self.raw_data.extend(sales_records)
        self._process_data()
    
    def _process_data(self):
        """Process raw data into aggregated metrics."""
        # Sales by multiple dimensions
        self.by_category = defaultdict(float)
        self.by_region = defaultdict(float)
        self.by_salesperson = defaultdict(list)
        self.by_date = defaultdict(float)
        self.by_customer = defaultdict(float)
        
        # Product analytics
        self.product_performance = defaultdict(lambda: {
            'revenue': 0, 'quantity': 0, 'transactions': 0
        })
        
        # Time-based analysis
        self.monthly_trends = defaultdict(float)
        self.quarterly_performance = defaultdict(float)
        
        for record in self.raw_data:
            # Basic aggregations
            self.by_category[record['category']] += record['amount']
            self.by_region[record['region']] += record['amount']
            self.by_date[record['date']] += record['amount']
            self.by_customer[record.get('customer_id', 'Unknown')] += record['amount']
            
            # Salesperson tracking
            salesperson = record.get('salesperson', 'Unknown')
            self.by_salesperson[salesperson].append(record['amount'])
            
            # Product performance
            product = record['product']
            self.product_performance[product]['revenue'] += record['amount']
            self.product_performance[product]['quantity'] += record.get('quantity', 1)
            self.product_performance[product]['transactions'] += 1
            
            # Time-based analysis
            date_parts = record['date'].split('-')
            if len(date_parts) >= 2:
                month_key = f"{date_parts[0]}-{date_parts[1]}"
                self.monthly_trends[month_key] += record['amount']
                
                quarter = (int(date_parts[1]) - 1) // 3 + 1
                quarter_key = f"{date_parts[0]}-Q{quarter}"
                self.quarterly_performance[quarter_key] += record['amount']
    
    def get_top_performers(self, dimension, limit=5):
        """Get top performers in any dimension."""
        if dimension == 'salesperson':
            # Calculate totals for salespeople
            salesperson_totals = {
                person: sum(sales) 
                for person, sales in self.by_salesperson.items()
            }
            return sorted(salesperson_totals.items(), 
                         key=lambda x: x[1], reverse=True)[:limit]
        
        elif dimension == 'product':
            return sorted(self.product_performance.items(),
                         key=lambda x: x[1]['revenue'], reverse=True)[:limit]
        
        else:
            data_map = getattr(self, f'by_{dimension}', {})
            return sorted(data_map.items(), 
                         key=lambda x: x[1], reverse=True)[:limit]
    
    def get_customer_segmentation(self):
        """Segment customers by purchase behavior."""
        customer_stats = {}
        
        for customer_id, total_spent in self.by_customer.items():
            # Get customer's transactions
            transactions = [
                record for record in self.raw_data 
                if record.get('customer_id') == customer_id
            ]
            
            customer_stats[customer_id] = {
                'total_spent': total_spent,
                'transaction_count': len(transactions),
                'avg_transaction': total_spent / len(transactions),
                'first_purchase': min(t['date'] for t in transactions),
                'last_purchase': max(t['date'] for t in transactions)
            }
        
        # Segment customers
        segments = defaultdict(list)
        for customer_id, stats in customer_stats.items():
            if stats['total_spent'] > 10000:
                segments['VIP'].append(customer_id)
            elif stats['total_spent'] > 5000:
                segments['Premium'].append(customer_id)
            elif stats['transaction_count'] > 10:
                segments['Frequent'].append(customer_id)
            else:
                segments['Regular'].append(customer_id)
        
        return dict(segments)
    
    def get_comprehensive_report(self):
        """Generate comprehensive business intelligence report."""
        total_revenue = sum(record['amount'] for record in self.raw_data)
        total_transactions = len(self.raw_data)
        
        return {
            'overview': {
                'total_revenue': total_revenue,
                'total_transactions': total_transactions,
                'avg_transaction_value': total_revenue / total_transactions,
                'unique_customers': len(self.by_customer),
                'unique_products': len(self.product_performance)
            },
            'top_categories': self.get_top_performers('category'),
            'top_regions': self.get_top_performers('region'),
            'top_products': self.get_top_performers('product'),
            'top_salespeople': self.get_top_performers('salesperson'),
            'customer_segments': self.get_customer_segmentation(),
            'monthly_trends': dict(self.monthly_trends),
            'quarterly_performance': dict(self.quarterly_performance)
        }

# Example usage with sample data
sales_data = [
    {'date': '2024-01-15', 'product': 'Laptop', 'category': 'Electronics', 
     'amount': 1200, 'region': 'North', 'salesperson': 'Alice', 'customer_id': 'C001'},
    {'date': '2024-01-16', 'product': 'Mouse', 'category': 'Electronics', 
     'amount': 25, 'region': 'South', 'salesperson': 'Bob', 'customer_id': 'C002'},
    {'date': '2024-02-01', 'product': 'Laptop', 'category': 'Electronics', 
     'amount': 1200, 'region': 'East', 'salesperson': 'Alice', 'customer_id': 'C001'},
    # ... more data
]

analyzer = SalesAnalyzer()
analyzer.add_sales_data(sales_data)
report = analyzer.get_comprehensive_report()
''',
            "benefits": [
                "defaultdict simplifies multi-dimensional aggregation",
                "Flexible analysis across any business dimension",
                "Real-time metrics as data is added",
                "Scalable to millions of transactions"
            ]
        }
    
    @staticmethod
    def _get_log_processing_example() -> Dict[str, Any]:
        """Log processing and monitoring."""
        return {
            "title": "Log Processing and System Monitoring",
            "use_case": "Process server logs for error detection and performance monitoring",
            "data_structures": ["deque", "Counter", "defaultdict"],
            "complexity": "O(1) for adding logs, O(k) for analysis where k is window size",
            "code": '''
class LogMonitor:
    """Real-time log processing and monitoring system."""
    
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.recent_logs = deque(maxlen=window_size)  # Fixed-size sliding window
        self.error_counts = Counter()
        self.request_patterns = defaultdict(int)
        self.response_times = deque(maxlen=window_size)
        self.alerts_triggered = []
    
    def process_log_entry(self, log_entry):
        """Process a single log entry."""
        self.recent_logs.append(log_entry)
        
        # Track error patterns
        if log_entry.get('level') == 'ERROR':
            error_type = log_entry.get('error_type', 'Unknown')
            self.error_counts[error_type] += 1
        
        # Track request patterns
        if 'endpoint' in log_entry:
            endpoint = log_entry['endpoint']
            self.request_patterns[endpoint] += 1
        
        # Track response times
        if 'response_time' in log_entry:
            self.response_times.append(log_entry['response_time'])
        
        # Check for alert conditions
        self._check_alerts(log_entry)
    
    def _check_alerts(self, log_entry):
        """Check if any alert conditions are met."""
        current_time = time.time()
        
        # High error rate alert
        recent_errors = sum(1 for log in list(self.recent_logs)[-100:] 
                          if log.get('level') == 'ERROR')
        if recent_errors > 10:  # More than 10 errors in last 100 logs
            self.alerts_triggered.append({
                'type': 'high_error_rate',
                'timestamp': current_time,
                'details': f'{recent_errors} errors in last 100 requests'
            })
        
        # Slow response time alert
        if (self.response_times and 
            len(self.response_times) >= 10 and
            sum(list(self.response_times)[-10:]) / 10 > 2000):  # Avg > 2 seconds
            self.alerts_triggered.append({
                'type': 'slow_response',
                'timestamp': current_time,
                'details': 'Average response time > 2 seconds'
            })
    
    def get_error_summary(self):
        """Get summary of errors in the current window."""
        total_errors = sum(self.error_counts.values())
        total_logs = len(self.recent_logs)
        error_rate = (total_errors / total_logs * 100) if total_logs > 0 else 0
        
        return {
            'total_errors': total_errors,
            'error_rate': f'{error_rate:.2f}%',
            'most_common_errors': self.error_counts.most_common(5),
            'total_logs_processed': total_logs
        }
    
    def get_performance_metrics(self):
        """Get performance metrics from recent logs."""
        if not self.response_times:
            return {'message': 'No response time data available'}
        
        response_list = list(self.response_times)
        avg_response = sum(response_list) / len(response_list)
        
        # Calculate percentiles
        sorted_responses = sorted(response_list)
        p50 = sorted_responses[len(sorted_responses) // 2]
        p95 = sorted_responses[int(len(sorted_responses) * 0.95)]
        p99 = sorted_responses[int(len(sorted_responses) * 0.99)]
        
        return {
            'avg_response_time': f'{avg_response:.2f}ms',
            'p50_response_time': f'{p50:.2f}ms',
            'p95_response_time': f'{p95:.2f}ms',
            'p99_response_time': f'{p99:.2f}ms',
            'sample_size': len(response_list)
        }
    
    def get_request_analytics(self):
        """Analyze request patterns."""
        total_requests = sum(self.request_patterns.values())
        
        # Most popular endpoints
        popular_endpoints = Counter(self.request_patterns).most_common(10)
        
        # Calculate request distribution
        endpoint_stats = {}
        for endpoint, count in self.request_patterns.items():
            percentage = (count / total_requests * 100) if total_requests > 0 else 0
            endpoint_stats[endpoint] = {
                'requests': count,
                'percentage': f'{percentage:.2f}%'
            }
        
        return {
            'total_requests': total_requests,
            'unique_endpoints': len(self.request_patterns),
            'most_popular': popular_endpoints,
            'endpoint_distribution': endpoint_stats
        }
    
    def get_recent_alerts(self, limit=10):
        """Get recent alerts."""
        return sorted(self.alerts_triggered, 
                     key=lambda x: x['timestamp'], reverse=True)[:limit]

# Example usage
monitor = LogMonitor(window_size=5000)

# Simulate log entries
sample_logs = [
    {'timestamp': '2024-01-15T10:30:00', 'level': 'INFO', 'endpoint': '/api/users', 'response_time': 150},
    {'timestamp': '2024-01-15T10:30:01', 'level': 'ERROR', 'error_type': 'database_timeout', 'endpoint': '/api/orders'},
    {'timestamp': '2024-01-15T10:30:02', 'level': 'INFO', 'endpoint': '/api/products', 'response_time': 89},
]

for log in sample_logs:
    monitor.process_log_entry(log)

print("Error Summary:", monitor.get_error_summary())
print("Performance Metrics:", monitor.get_performance_metrics())
''',
            "benefits": [
                "deque provides efficient sliding window for recent logs",
                "Counter automatically tracks error frequencies",
                "Real-time alerting based on configurable thresholds",
                "Memory-efficient for high-volume log streams"
            ]
        }
    
    @staticmethod
    def _get_recommendation_engine_example() -> Dict[str, Any]:
        """Recommendation engine using collaborative filtering."""
        return {
            "title": "Recommendation Engine",
            "use_case": "Generate personalized recommendations based on user behavior",
            "data_structures": ["defaultdict", "Counter", "set"],
            "complexity": "O(n*m) where n is users and m is items for similarity calculation",
            "code": '''
class RecommendationEngine:
    """Collaborative filtering recommendation system."""
    
    def __init__(self):
        self.user_items = defaultdict(set)      # User -> set of items
        self.item_users = defaultdict(set)      # Item -> set of users
        self.user_ratings = defaultdict(dict)   # User -> {item: rating}
        self.item_popularity = Counter()        # Global item popularity
    
    def add_interaction(self, user_id, item_id, rating=1):
        """Record user-item interaction."""
        self.user_items[user_id].add(item_id)
        self.item_users[item_id].add(user_id)
        self.user_ratings[user_id][item_id] = rating
        self.item_popularity[item_id] += 1
    
    def find_similar_users(self, user_id, min_common_items=2):
        """Find users with similar preferences using Jaccard similarity."""
        target_items = self.user_items[user_id]
        similar_users = {}
        
        for other_user, other_items in self.user_items.items():
            if other_user == user_id:
                continue
            
            # Calculate Jaccard similarity
            intersection = len(target_items & other_items)
            union = len(target_items | other_items)
            
            if intersection >= min_common_items and union > 0:
                similarity = intersection / union
                similar_users[other_user] = {
                    'similarity': similarity,
                    'common_items': intersection,
                    'total_items': len(other_items)
                }
        
        return sorted(similar_users.items(), 
                     key=lambda x: x[1]['similarity'], reverse=True)
    
    def recommend_items(self, user_id, num_recommendations=10):
        """Generate item recommendations for a user."""
        if user_id not in self.user_items:
            # New user - recommend popular items
            return self._recommend_popular_items(num_recommendations)
        
        user_items = self.user_items[user_id]
        similar_users = self.find_similar_users(user_id)
        
        # Collaborative filtering recommendations
        item_scores = defaultdict(float)
        
        for similar_user, similarity_data in similar_users[:20]:  # Top 20 similar users
            similarity_score = similarity_data['similarity']
            
            for item in self.user_items[similar_user]:
                if item not in user_items:  # Don't recommend items user already has
                    # Weight by similarity and item rating
                    rating = self.user_ratings[similar_user].get(item, 1)
                    item_scores[item] += similarity_score * rating
        
        # Combine with popularity-based recommendations
        popular_items = self._recommend_popular_items(num_recommendations * 2)
        
        for item, popularity in popular_items:
            if item not in user_items and item not in item_scores:
                item_scores[item] = popularity * 0.1  # Lower weight for popularity
        
        # Sort by score and return top recommendations
        recommendations = sorted(item_scores.items(), 
                               key=lambda x: x[1], reverse=True)
        
        return recommendations[:num_recommendations]
    
    def _recommend_popular_items(self, num_items):
        """Recommend globally popular items."""
        return self.item_popularity.most_common(num_items)
    
    def get_user_stats(self, user_id):
        """Get statistics for a specific user."""
        if user_id not in self.user_items:
            return {'error': 'User not found'}
        
        user_items = self.user_items[user_id]
        similar_users = self.find_similar_users(user_id)
        
        # Calculate user's item category preferences
        item_categories = defaultdict(int)
        for item in user_items:
            # In real system, you'd look up item categories
            # Here we simulate with item ID patterns
            category = f"category_{hash(item) % 5}"
            item_categories[category] += 1
        
        return {
            'total_items': len(user_items),
            'similar_users_found': len(similar_users),
            'top_similar_user': similar_users[0] if similar_users else None,
            'category_preferences': dict(item_categories),
            'avg_rating': sum(self.user_ratings[user_id].values()) / len(self.user_ratings[user_id]) if self.user_ratings[user_id] else 0
        }
    
    def get_system_stats(self):
        """Get overall system statistics."""
        total_interactions = sum(len(items) for items in self.user_items.values())
        
        return {
            'total_users': len(self.user_items),
            'total_items': len(self.item_users),
            'total_interactions': total_interactions,
            'avg_items_per_user': total_interactions / len(self.user_items) if self.user_items else 0,
            'most_popular_items': self.item_popularity.most_common(5),
            'avg_users_per_item': len(self.user_items) / len(self.item_users) if self.item_users else 0
        }

# Example usage
recommender = RecommendationEngine()

# Add sample user interactions
interactions = [
    ('user1', 'movie_a', 5), ('user1', 'movie_b', 4), ('user1', 'movie_c', 3),
    ('user2', 'movie_a', 4), ('user2', 'movie_d', 5), ('user2', 'movie_e', 4),
    ('user3', 'movie_b', 5), ('user3', 'movie_c', 4), ('user3', 'movie_f', 3),
]

for user, item, rating in interactions:
    recommender.add_interaction(user, item, rating)

# Generate recommendations
recommendations = recommender.recommend_items('user1', 3)
print(f"Recommendations for user1: {recommendations}")

system_stats = recommender.get_system_stats()
print(f"System statistics: {system_stats}")
''',
            "benefits": [
                "defaultdict simplifies user-item matrix management",
                "set operations enable efficient similarity calculations",
                "Counter tracks global popularity automatically",
                "Scalable to millions of users and items"
            ]
        }
    
    @staticmethod
    def _get_inventory_management_example() -> Dict[str, Any]:
        """Inventory management system."""
        return {
            "title": "Inventory Management and Supply Chain",
            "use_case": "Track inventory levels, predict demand, manage supply chain",
            "data_structures": ["defaultdict", "deque", "heapq"],
            "complexity": "O(log n) for priority operations, O(1) for most tracking",
            "code": '''
class InventoryManager:
    """Comprehensive inventory management system."""
    
    def __init__(self):
        self.inventory = defaultdict(lambda: {
            'current_stock': 0,
            'reserved_stock': 0,
            'reorder_point': 0,
            'max_stock': 0,
            'cost_per_unit': 0,
            'supplier': None
        })
        
        self.sales_history = defaultdict(deque)  # Recent sales per item
        self.pending_orders = []  # Priority queue for supply orders
        self.low_stock_alerts = set()
        self.transaction_log = deque(maxlen=10000)
    
    def add_item(self, item_id, initial_stock=0, reorder_point=10, 
                 max_stock=100, cost_per_unit=0, supplier=None):
        """Add new item to inventory."""
        self.inventory[item_id].update({
            'current_stock': initial_stock,
            'reorder_point': reorder_point,
            'max_stock': max_stock,
            'cost_per_unit': cost_per_unit,
            'supplier': supplier
        })
        
        self._log_transaction('ADD_ITEM', item_id, initial_stock)
    
    def receive_stock(self, item_id, quantity, cost_per_unit=None):
        """Receive new stock from supplier."""
        if cost_per_unit:
            self.inventory[item_id]['cost_per_unit'] = cost_per_unit
        
        self.inventory[item_id]['current_stock'] += quantity
        self.low_stock_alerts.discard(item_id)  # Remove low stock alert
        
        self._log_transaction('RECEIVE', item_id, quantity)
    
    def reserve_stock(self, item_id, quantity):
        """Reserve stock for pending orders."""
        item = self.inventory[item_id]
        available = item['current_stock'] - item['reserved_stock']
        
        if available >= quantity:
            item['reserved_stock'] += quantity
            self._log_transaction('RESERVE', item_id, quantity)
            return True
        return False
    
    def fulfill_order(self, item_id, quantity):
        """Fulfill customer order and update inventory."""
        item = self.inventory[item_id]
        
        if item['reserved_stock'] >= quantity:
            item['current_stock'] -= quantity
            item['reserved_stock'] -= quantity
            
            # Track sales for demand forecasting
            self.sales_history[item_id].append({
                'quantity': quantity,
                'timestamp': time.time()
            })
            
            # Check if reorder needed
            if item['current_stock'] <= item['reorder_point']:
                self._trigger_reorder(item_id)
            
            self._log_transaction('FULFILL', item_id, quantity)
            return True
        return False
    
    def _trigger_reorder(self, item_id):
        """Trigger automatic reorder when stock is low."""
        item = self.inventory[item_id]
        
        if item_id not in self.low_stock_alerts:
            self.low_stock_alerts.add(item_id)
            
            # Calculate reorder quantity
            reorder_qty = item['max_stock'] - item['current_stock']
            
            # Add to priority queue (priority = days since last order)
            priority = 1  # High priority for low stock
            order = {
                'item_id': item_id,
                'quantity': reorder_qty,
                'supplier': item['supplier'],
                'estimated_cost': reorder_qty * item['cost_per_unit'],
                'order_date': time.time()
            }
            
            heapq.heappush(self.pending_orders, (priority, time.time(), order))
    
    def get_next_purchase_order(self):
        """Get next purchase order to process."""
        if self.pending_orders:
            _, _, order = heapq.heappop(self.pending_orders)
            return order
        return None
    
    def forecast_demand(self, item_id, days_ahead=30):
        """Forecast demand based on sales history."""
        if item_id not in self.sales_history or not self.sales_history[item_id]:
            return {'forecast': 0, 'confidence': 'low'}
        
        # Simple moving average forecast
        recent_sales = list(self.sales_history[item_id])[-30:]  # Last 30 sales
        if not recent_sales:
            return {'forecast': 0, 'confidence': 'low'}
        
        # Calculate daily average
        time_span = (time.time() - recent_sales[0]['timestamp']) / 86400  # days
        total_quantity = sum(sale['quantity'] for sale in recent_sales)
        daily_average = total_quantity / max(time_span, 1)
        
        forecast = daily_average * days_ahead
        confidence = 'high' if len(recent_sales) >= 10 else 'medium'
        
        return {
            'forecast': forecast,
            'confidence': confidence,
            'daily_average': daily_average,
            'based_on_sales': len(recent_sales)
        }
    
    def get_inventory_report(self):
        """Generate comprehensive inventory report."""
        total_value = 0
        low_stock_items = []
        overstocked_items = []
        
        for item_id, item in self.inventory.items():
            item_value = item['current_stock'] * item['cost_per_unit']
            total_value += item_value
            
            # Check stock levels
            if item['current_stock'] <= item['reorder_point']:
                low_stock_items.append(item_id)
            elif item['current_stock'] >= item['max_stock'] * 0.9:
                overstocked_items.append(item_id)
        
        return {
            'total_items': len(self.inventory),
            'total_inventory_value': total_value,
            'low_stock_items': low_stock_items,
            'overstocked_items': overstocked_items,
            'pending_purchase_orders': len(self.pending_orders),
            'items_with_sales_data': len(self.sales_history)
        }
    
    def _log_transaction(self, transaction_type, item_id, quantity):
        """Log inventory transaction."""
        self.transaction_log.append({
            'timestamp': time.time(),
            'type': transaction_type,
            'item_id': item_id,
            'quantity': quantity
        })

# Example usage
inventory = InventoryManager()

# Set up some items
inventory.add_item('laptop_001', initial_stock=50, reorder_point=10, 
                  max_stock=100, cost_per_unit=800, supplier='TechCorp')
inventory.add_item('mouse_001', initial_stock=200, reorder_point=50, 
                  max_stock=500, cost_per_unit=25, supplier='PeripheralsCo')

# Simulate business operations
inventory.reserve_stock('laptop_001', 5)
inventory.fulfill_order('laptop_001', 5)

# Generate demand forecast
forecast = inventory.forecast_demand('laptop_001', 30)
print(f"30-day forecast for laptop_001: {forecast}")

# Get inventory report
report = inventory.get_inventory_report()
print(f"Inventory report: {report}")
''',
            "benefits": [
                "defaultdict handles dynamic inventory additions",
                "deque provides efficient sales history tracking",
                "heapq manages purchase order priorities",
                "Real-time demand forecasting and automated reordering"
            ]
        }
    
    @staticmethod
    def _get_complete_demo_code() -> str:
        """Get complete demonstration code for all applications."""
        return '''
from collections import defaultdict, Counter, deque, OrderedDict
import heapq
import time

def run_all_applications():
    """Demonstrate all real-world applications."""
    
    print("=== Real-World Data Structure Applications ===\\n")
    
    # 1. Text Analysis Application
    print("1. TEXT ANALYSIS APPLICATION")
    print("-" * 40)
    
    def analyze_text(text):
        words = text.lower().split()
        word_count = Counter(words)
        by_length = defaultdict(list)
        for word in set(words):
            by_length[len(word)].append(word)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'most_common': word_count.most_common(3),
            'by_length': dict(by_length)
        }
    
    sample_text = "The quick brown fox jumps over the lazy dog. The fox is very quick."
    analysis = analyze_text(sample_text)
    print(f"Analysis: {analysis}")
    
    # 2. Social Network Analysis
    print("\\n2. SOCIAL NETWORK ANALYSIS")
    print("-" * 40)
    
    class SimpleGraph:
        def __init__(self):
            self.graph = defaultdict(set)
        
        def add_connection(self, user1, user2):
            self.graph[user1].add(user2)
            self.graph[user2].add(user1)
        
        def find_path(self, start, end):
            visited = set()
            queue = deque([(start, [start])])
            
            while queue:
                current, path = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)
                
                if current == end:
                    return path
                
                for neighbor in self.graph[current]:
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
            return None
    
    network = SimpleGraph()
    network.add_connection('Alice', 'Bob')
    network.add_connection('Bob', 'Charlie')
    network.add_connection('Alice', 'David')
    
    path = network.find_path('Alice', 'Charlie')
    print(f"Path from Alice to Charlie: {path}")
    
    # 3. LRU Cache System
    print("\\n3. LRU CACHE SYSTEM")
    print("-" * 40)
    
    class SimpleLRUCache:
        def __init__(self, capacity):
            self.capacity = capacity
            self.cache = OrderedDict()
        
        def get(self, key):
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
        
        def put(self, key, value):
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    cache = SimpleLRUCache(3)
    cache.put('a', 1)
    cache.put('b', 2)
    cache.put('c', 3)
    print(f"Cache contents: {list(cache.cache.items())}")
    
    cache.get('a')  # Make 'a' most recent
    cache.put('d', 4)  # Should evict 'b'
    print(f"After adding 'd': {list(cache.cache.items())}")
    
    # 4. Task Scheduling
    print("\\n4. TASK SCHEDULING")
    print("-" * 40)
    
    class SimpleScheduler:
        def __init__(self):
            self.tasks = []
            self.task_id = 0
        
        def add_task(self, priority, description):
            self.task_id += 1
            heapq.heappush(self.tasks, (priority, self.task_id, description))
        
        def get_next_task(self):
            if self.tasks:
                return heapq.heappop(self.tasks)[2]
            return None
    
    scheduler = SimpleScheduler()
    scheduler.add_task(2, "Medium priority task")
    scheduler.add_task(1, "High priority task")
    scheduler.add_task(3, "Low priority task")
    
    print("Processing tasks in priority order:")
    while scheduler.tasks:
        task = scheduler.get_next_task()
        print(f"  - {task}")
    
    # 5. Data Aggregation
    print("\\n5. DATA AGGREGATION")
    print("-" * 40)
    
    sales_data = [
        {'product': 'Laptop', 'category': 'Electronics', 'amount': 1200, 'region': 'North'},
        {'product': 'Mouse', 'category': 'Electronics', 'amount': 25, 'region': 'South'},
        {'product': 'Book', 'category': 'Education', 'amount': 15, 'region': 'North'},
        {'product': 'Phone', 'category': 'Electronics', 'amount': 800, 'region': 'West'},
    ]
    
    # Aggregate by category
    category_sales = defaultdict(float)
    for sale in sales_data:
        category_sales[sale['category']] += sale['amount']
    
    print("Sales by category:")
    for category, total in category_sales.items():
        print(f"  {category}: ${total}")
    
    # Product frequency
    product_counts = Counter(sale['product'] for sale in sales_data)
    print(f"\\nProduct sales frequency: {product_counts}")
    
    print("\\n=== Applications Summary ===")
    print("These examples show how data structures solve real problems:")
    print("• Text analysis: Counter and defaultdict for frequency analysis")
    print("• Social networks: defaultdict and deque for graph algorithms")
    print("• Caching: OrderedDict for LRU cache implementation")
    print("• Task scheduling: heapq for priority-based management")
    print("• Data aggregation: Multiple structures for business intelligence")


if __name__ == "__main__":
    run_all_applications()
'''


def get_real_world_applications():
    """Get the real-world applications examples."""
    return ApplicationsExamples.get_real_world_applications()