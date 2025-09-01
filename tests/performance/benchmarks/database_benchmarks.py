# tests/performance/benchmarks/database_benchmarks.py
"""
Database performance benchmarks for the Python learning platform.
Tests database operations including queries, inserts, updates, and
connection management under various load conditions.
"""
import sqlite3
import asyncio
import time
import random
import string
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import tempfile
import concurrent.futures
from contextlib import contextmanager

from .benchmark_runner import BenchmarkRunner, BenchmarkConfig, benchmark, async_benchmark


@dataclass
class DatabaseMetrics:
    """Metrics for database operations."""
    query_time: float
    rows_affected: int
    connection_time: float
    transaction_time: Optional[float] = None
    lock_wait_time: Optional[float] = None


class MockDatabase:
    """Mock database for benchmarking purposes."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
        self.active_connections = []
        self.connection_pool_size = 10
        self.lock = threading.Lock()
        
    def connect(self) -> sqlite3.Connection:
        """Create database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        self.active_connections.append(conn)
        return conn
    
    def setup_schema(self):
        """Set up database schema for benchmarking."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                difficulty_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Enrollments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                progress_percentage INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (course_id) REFERENCES courses (id),
                UNIQUE(user_id, course_id)
            )
        """)
        
        # Submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_id TEXT NOT NULL,
                code TEXT NOT NULL,
                score INTEGER,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time REAL,
                memory_usage INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Progress tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                score INTEGER,
                time_spent INTEGER,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, lesson_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_user ON enrollments(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_exercise ON submissions(exercise_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_progress_user ON user_progress(user_id)")
        
        conn.commit()
        conn.close()
    
    def generate_sample_data(self, num_users: int = 1000, num_courses: int = 50):
        """Generate sample data for benchmarking."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Generate users
        users_data = []
        for i in range(num_users):
            username = f"user_{i:06d}"
            email = f"user{i}@example.com"
            password_hash = self._generate_random_string(64)
            users_data.append((username, email, password_hash))
        
        cursor.executemany(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            users_data
        )
        
        # Generate courses
        courses_data = []
        difficulties = ["beginner", "intermediate", "advanced"]
        for i in range(num_courses):
            title = f"Python Course {i+1}"
            description = f"Description for course {i+1}"
            difficulty = random.choice(difficulties)
            courses_data.append((title, description, difficulty))
        
        cursor.executemany(
            "INSERT INTO courses (title, description, difficulty_level) VALUES (?, ?, ?)",
            courses_data
        )
        
        # Generate enrollments (random subset)
        enrollments_data = []
        for user_id in range(1, min(num_users + 1, 501)):  # First 500 users
            num_enrollments = random.randint(1, min(5, num_courses))
            enrolled_courses = random.sample(range(1, num_courses + 1), num_enrollments)
            
            for course_id in enrolled_courses:
                progress = random.randint(0, 100)
                enrollments_data.append((user_id, course_id, progress))
        
        cursor.executemany(
            "INSERT INTO enrollments (user_id, course_id, progress_percentage) VALUES (?, ?, ?)",
            enrollments_data
        )
        
        # Generate submissions
        submissions_data = []
        for i in range(min(num_users * 5, 5000)):  # Up to 5000 submissions
            user_id = random.randint(1, min(num_users, 500))
            exercise_id = f"exercise_{random.randint(1, 100)}"
            code = f"def solution():\n    return {random.randint(1, 100)}"
            score = random.randint(60, 100)
            execution_time = random.uniform(0.1, 2.0)
            memory_usage = random.randint(1024, 10240)
            
            submissions_data.append((user_id, exercise_id, code, score, execution_time, memory_usage))
        
        cursor.executemany(
            "INSERT INTO submissions (user_id, exercise_id, code, score, execution_time, memory_usage) VALUES (?, ?, ?, ?, ?, ?)",
            submissions_data
        )
        
        conn.commit()
        conn.close()
        
        print(f"Generated sample data: {num_users} users, {num_courses} courses, {len(enrollments_data)} enrollments, {len(submissions_data)} submissions")
    
    def _generate_random_string(self, length: int) -> str:
        """Generate random string for testing."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    def cleanup(self):
        """Clean up database connections."""
        for conn in self.active_connections:
            try:
                conn.close()
            except:
                pass
        self.active_connections.clear()


class DatabaseBenchmarks:
    """Database performance benchmark suite."""
    
    def __init__(self, use_file_db: bool = False):
        self.runner = BenchmarkRunner("database_benchmarks")
        self.use_file_db = use_file_db
        self.db = None
        self.temp_db_file = None
        
    def setup(self):
        """Set up database for benchmarking."""
        if self.use_file_db:
            self.temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            self.temp_db_file.close()
            self.db = MockDatabase(self.temp_db_file.name)
        else:
            self.db = MockDatabase(":memory:")
        
        self.db.setup_schema()
        self.db.generate_sample_data(1000, 50)
        
    def teardown(self):
        """Clean up database resources."""
        if self.db:
            self.db.cleanup()
        
        if self.temp_db_file:
            try:
                Path(self.temp_db_file.name).unlink()
            except:
                pass
    
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all database benchmarks."""
        self.setup()
        
        try:
            benchmarks = {
                "simple_select": (
                    BenchmarkConfig("simple_select", "Simple SELECT queries", iterations=100),
                    self.benchmark_simple_select,
                    (),
                    {}
                ),
                "complex_joins": (
                    BenchmarkConfig("complex_joins", "Complex JOIN queries", iterations=50),
                    self.benchmark_complex_joins,
                    (),
                    {}
                ),
                "insert_operations": (
                    BenchmarkConfig("insert_operations", "INSERT operations", iterations=50),
                    self.benchmark_insert_operations,
                    (),
                    {}
                ),
                "update_operations": (
                    BenchmarkConfig("update_operations", "UPDATE operations", iterations=50),
                    self.benchmark_update_operations,
                    (),
                    {}
                ),
                "delete_operations": (
                    BenchmarkConfig("delete_operations", "DELETE operations", iterations=30),
                    self.benchmark_delete_operations,
                    (),
                    {}
                ),
                "transaction_performance": (
                    BenchmarkConfig("transaction_performance", "Transaction performance", iterations=30),
                    self.benchmark_transaction_performance,
                    (),
                    {}
                ),
                "concurrent_reads": (
                    BenchmarkConfig("concurrent_reads", "Concurrent read operations", iterations=20),
                    self.benchmark_concurrent_reads,
                    (),
                    {}
                ),
                "concurrent_writes": (
                    BenchmarkConfig("concurrent_writes", "Concurrent write operations", iterations=10),
                    self.benchmark_concurrent_writes,
                    (),
                    {}
                ),
                "connection_overhead": (
                    BenchmarkConfig("connection_overhead", "Connection establishment overhead", iterations=50),
                    self.benchmark_connection_overhead,
                    (),
                    {}
                ),
                "index_performance": (
                    BenchmarkConfig("index_performance", "Index usage performance", iterations=40),
                    self.benchmark_index_performance,
                    (),
                    {}
                )
            }
            
            return self.runner.run_benchmark_suite(benchmarks)
        
        finally:
            self.teardown()
    
    @benchmark("simple_select", iterations=100)
    def benchmark_simple_select(self):
        """Benchmark simple SELECT queries."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Various simple queries
            queries = [
                "SELECT COUNT(*) FROM users",
                "SELECT * FROM users WHERE id = ?",
                "SELECT username, email FROM users LIMIT 10",
                "SELECT * FROM courses WHERE difficulty_level = 'beginner'",
                "SELECT COUNT(*) FROM submissions WHERE score > 80"
            ]
            
            total_rows = 0
            for query in queries:
                if "?" in query:
                    cursor.execute(query, (random.randint(1, 100),))
                else:
                    cursor.execute(query)
                
                results = cursor.fetchall()
                total_rows += len(results)
            
            return total_rows
    
    @benchmark("complex_joins", iterations=50)
    def benchmark_complex_joins(self):
        """Benchmark complex JOIN queries."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Complex query with multiple joins
            query = """
                SELECT 
                    u.username,
                    c.title,
                    e.progress_percentage,
                    COUNT(s.id) as submission_count,
                    AVG(s.score) as avg_score
                FROM users u
                JOIN enrollments e ON u.id = e.user_id
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN submissions s ON u.id = s.user_id
                WHERE e.progress_percentage > 50
                GROUP BY u.id, c.id
                HAVING submission_count > 2
                ORDER BY avg_score DESC
                LIMIT 20
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return len(results)
    
    @benchmark("insert_operations", iterations=50)
    def benchmark_insert_operations(self):
        """Benchmark INSERT operations."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Single inserts
            for i in range(10):
                cursor.execute(
                    "INSERT INTO submissions (user_id, exercise_id, code, score) VALUES (?, ?, ?, ?)",
                    (random.randint(1, 100), f"benchmark_ex_{i}", f"def test_{i}(): pass", random.randint(60, 100))
                )
            
            # Batch insert
            batch_data = [
                (random.randint(1, 100), f"batch_ex_{i}", f"def batch_{i}(): pass", random.randint(60, 100))
                for i in range(20)
            ]
            
            cursor.executemany(
                "INSERT INTO submissions (user_id, exercise_id, code, score) VALUES (?, ?, ?, ?)",
                batch_data
            )
            
            conn.commit()
            return 30  # Total inserts
    
    @benchmark("update_operations", iterations=50)
    def benchmark_update_operations(self):
        """Benchmark UPDATE operations."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Single row update
            cursor.execute(
                "UPDATE enrollments SET progress_percentage = ? WHERE user_id = ? AND course_id = ?",
                (random.randint(80, 100), random.randint(1, 100), random.randint(1, 10))
            )
            
            # Batch update
            cursor.execute(
                "UPDATE submissions SET score = score + 5 WHERE score < 70 AND user_id IN (SELECT id FROM users LIMIT 10)"
            )
            
            # Update with subquery
            cursor.execute("""
                UPDATE user_progress 
                SET last_accessed = CURRENT_TIMESTAMP 
                WHERE user_id IN (
                    SELECT user_id FROM enrollments WHERE progress_percentage > 75
                )
            """)
            
            conn.commit()
            return cursor.rowcount
    
    @benchmark("delete_operations", iterations=30)
    def benchmark_delete_operations(self):
        """Benchmark DELETE operations."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete old submissions (safe for benchmark)
            cursor.execute(
                "DELETE FROM submissions WHERE user_id > 900 AND score < 60"
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
    
    @benchmark("transaction_performance", iterations=30)
    def benchmark_transaction_performance(self):
        """Benchmark transaction performance."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Large transaction
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # Multiple operations in single transaction
                for i in range(20):
                    cursor.execute(
                        "INSERT INTO submissions (user_id, exercise_id, code, score) VALUES (?, ?, ?, ?)",
                        (random.randint(1, 100), f"tx_ex_{i}", f"def tx_test_{i}(): pass", random.randint(60, 100))
                    )
                
                # Update related records
                cursor.execute(
                    "UPDATE enrollments SET progress_percentage = progress_percentage + 1 WHERE user_id IN (SELECT DISTINCT user_id FROM submissions WHERE exercise_id LIKE 'tx_ex_%')"
                )
                
                conn.commit()
                return 20  # Number of operations in transaction
                
            except Exception:
                conn.rollback()
                return 0
    
    @benchmark("concurrent_reads", iterations=20)
    def benchmark_concurrent_reads(self):
        """Benchmark concurrent read operations."""
        def execute_read_query():
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT u.username, c.title FROM users u JOIN enrollments e ON u.id = e.user_id JOIN courses c ON e.course_id = c.id WHERE u.id = ?",
                    (random.randint(1, 100),)
                )
                return len(cursor.fetchall())
        
        # Execute 10 concurrent reads
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(execute_read_query) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return sum(results)
    
    @benchmark("concurrent_writes", iterations=10)
    def benchmark_concurrent_writes(self):
        """Benchmark concurrent write operations."""
        def execute_write_operation(thread_id):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO submissions (user_id, exercise_id, code, score) VALUES (?, ?, ?, ?)",
                    (random.randint(1, 100), f"concurrent_ex_{thread_id}", f"def concurrent_test_{thread_id}(): pass", random.randint(60, 100))
                )
                conn.commit()
                return 1
        
        # Execute 5 concurrent writes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_write_operation, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return sum(results)
    
    @benchmark("connection_overhead", iterations=50)
    def benchmark_connection_overhead(self):
        """Benchmark connection establishment overhead."""
        connections_created = 0
        
        # Test connection creation and immediate closure
        for _ in range(10):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                connections_created += 1
        
        return connections_created
    
    @benchmark("index_performance", iterations=40)
    def benchmark_index_performance(self):
        """Benchmark index usage performance."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Queries that should use indexes
            indexed_queries = [
                ("SELECT * FROM users WHERE username = ?", (f"user_{random.randint(0, 999):06d}",)),
                ("SELECT * FROM users WHERE email = ?", (f"user{random.randint(0, 999)}@example.com",)),
                ("SELECT * FROM enrollments WHERE user_id = ?", (random.randint(1, 100),)),
                ("SELECT * FROM submissions WHERE user_id = ?", (random.randint(1, 100),)),
            ]
            
            total_rows = 0
            for query, params in indexed_queries:
                cursor.execute(query, params)
                results = cursor.fetchall()
                total_rows += len(results)
            
            return total_rows
    
    def benchmark_query_optimization(self) -> Dict[str, Any]:
        """Benchmark query optimization scenarios."""
        optimization_tests = {
            "with_index": "SELECT * FROM users WHERE username = 'user_000001'",
            "without_index": "SELECT * FROM users WHERE password_hash LIKE '%abc%'",
            "optimized_join": """
                SELECT u.username, COUNT(s.id) 
                FROM users u 
                LEFT JOIN submissions s ON u.id = s.user_id 
                WHERE u.id BETWEEN 1 AND 100
                GROUP BY u.id
            """,
            "suboptimal_join": """
                SELECT u.username, 
                       (SELECT COUNT(*) FROM submissions s WHERE s.user_id = u.id) as submission_count
                FROM users u 
                WHERE u.id BETWEEN 1 AND 100
            """
        }
        
        results = {}
        
        for test_name, query in optimization_tests.items():
            print(f"Benchmarking query optimization: {test_name}")
            
            def execute_optimization_query():
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    return len(cursor.fetchall())
            
            config = BenchmarkConfig(
                name=f"query_opt_{test_name}",
                description=f"Query optimization test: {test_name}",
                iterations=30
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_optimization_query)
            )
            
            results[test_name] = benchmark_result
        
        return results
    
    def benchmark_bulk_operations(self) -> Dict[str, Any]:
        """Benchmark bulk database operations."""
        bulk_tests = {
            "bulk_insert_small": (100, "Small bulk insert"),
            "bulk_insert_medium": (1000, "Medium bulk insert"),
            "bulk_insert_large": (5000, "Large bulk insert"),
        }
        
        results = {}
        
        for test_name, (record_count, description) in bulk_tests.items():
            print(f"Benchmarking bulk operations: {test_name}")
            
            def execute_bulk_insert():
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Generate bulk data
                    bulk_data = [
                        (
                            random.randint(1, 100),
                            f"bulk_ex_{i}",
                            f"def bulk_test_{i}(): return {i}",
                            random.randint(60, 100)
                        )
                        for i in range(record_count)
                    ]
                    
                    # Execute bulk insert
                    cursor.executemany(
                        "INSERT INTO submissions (user_id, exercise_id, code, score) VALUES (?, ?, ?, ?)",
                        bulk_data
                    )
                    
                    conn.commit()
                    return record_count
            
            config = BenchmarkConfig(
                name=f"bulk_{test_name}",
                description=description,
                iterations=5 if record_count > 1000 else 10
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_bulk_insert)
            )
            
            results[test_name] = benchmark_result
        
        return results
    
    def benchmark_database_scaling(self) -> Dict[str, Any]:
        """Benchmark database performance under different data scales."""
        scaling_tests = [
            (100, "Small dataset"),
            (1000, "Medium dataset"),
            (5000, "Large dataset"),
        ]
        
        results = {}
        
        for user_count, description in scaling_tests:
            print(f"Benchmarking database scaling: {description} ({user_count} users)")
            
            # Create fresh database with specific scale
            temp_db = MockDatabase(":memory:")
            temp_db.setup_schema()
            temp_db.generate_sample_data(user_count, max(10, user_count // 20))
            
            def execute_scaling_query():
                with temp_db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Complex query that scales with data size
                    cursor.execute("""
                        SELECT 
                            u.username,
                            COUNT(DISTINCT e.course_id) as courses_enrolled,
                            COUNT(s.id) as total_submissions,
                            AVG(s.score) as avg_score,
                            MAX(s.submitted_at) as last_submission
                        FROM users u
                        LEFT JOIN enrollments e ON u.id = e.user_id
                        LEFT JOIN submissions s ON u.id = s.user_id
                        GROUP BY u.id
                        HAVING total_submissions > 0
                        ORDER BY avg_score DESC
                        LIMIT 50
                    """)
                    
                    return len(cursor.fetchall())
            
            config = BenchmarkConfig(
                name=f"scaling_{user_count}_users",
                description=f"Performance with {user_count} users",
                iterations=15
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, execute_scaling_query)
            )
            
            results[f"scale_{user_count}"] = benchmark_result
            
            # Cleanup
            temp_db.cleanup()
        
        return results
    
    def benchmark_connection_pooling(self) -> Dict[str, Any]:
        """Benchmark connection pooling vs single connections."""
        pooling_tests = {
            "single_connection": "Single connection reuse",
            "multiple_connections": "Multiple connection creation",
            "connection_pool_simulation": "Simulated connection pool"
        }
        
        results = {}
        
        for test_name, description in pooling_tests.items():
            print(f"Benchmarking connection strategy: {test_name}")
            
            if test_name == "single_connection":
                def execute_single_connection():
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        operations = 0
                        
                        for _ in range(20):
                            cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (random.randint(1, 100),))
                            cursor.fetchone()
                            operations += 1
                        
                        return operations
                
                benchmark_func = execute_single_connection
                
            elif test_name == "multiple_connections":
                def execute_multiple_connections():
                    operations = 0
                    
                    for _ in range(20):
                        with self.db.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (random.randint(1, 100),))
                            cursor.fetchone()
                            operations += 1
                    
                    return operations
                
                benchmark_func = execute_multiple_connections
                
            else:  # connection_pool_simulation
                def execute_pool_simulation():
                    # Simulate connection pool with limited connections
                    pool_connections = [self.db.connect() for _ in range(5)]
                    operations = 0
                    
                    try:
                        for i in range(20):
                            conn = pool_connections[i % len(pool_connections)]
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (random.randint(1, 100),))
                            cursor.fetchone()
                            operations += 1
                    
                    finally:
                        for conn in pool_connections:
                            conn.close()
                    
                    return operations
                
                benchmark_func = execute_pool_simulation
            
            config = BenchmarkConfig(
                name=f"connection_{test_name}",
                description=description,
                iterations=25
            )
            
            benchmark_result = asyncio.run(
                self.runner.run_benchmark(config, benchmark_func)
            )
            
            results[test_name] = benchmark_result
        
        return results
    
    @async_benchmark("async_database_operations", iterations=20)
    async def benchmark_async_database_operations(self):
        """Benchmark simulated async database operations."""
        # Simulate async database operations
        async def async_query_simulation():
            # Simulate network latency and async processing
            await asyncio.sleep(0.001)
            
            # Simulate actual database work
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                result = cursor.fetchone()
                return result[0] if result else 0
        
        # Execute multiple async operations
        tasks = [async_query_simulation() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        return sum(results)


# Standalone benchmark execution
def run_database_benchmarks():
    """Run all database benchmarks."""
    print("Running Database Performance Benchmarks")
    print("=" * 50)
    
    # Test both in-memory and file-based databases
    for use_file_db in [False, True]:
        db_type = "File-based" if use_file_db else "In-memory"
        print(f"\n{db_type} Database Benchmarks:")
        print("-" * 40)
        
        benchmarks = DatabaseBenchmarks(use_file_db=use_file_db)
        
        # Run main benchmark suite
        main_results = asyncio.run(benchmarks.run_all_benchmarks())
        
        # Run additional specialized benchmarks
        print(f"\nRunning query optimization benchmarks ({db_type})...")
        optimization_results = benchmarks.benchmark_query_optimization()
        
        print(f"\nRunning bulk operations benchmarks ({db_type})...")
        bulk_results = benchmarks.benchmark_bulk_operations()
        
        print(f"\nRunning scaling benchmarks ({db_type})...")
        scaling_results = benchmarks.benchmark_database_scaling()
        
        print(f"\nRunning connection pooling benchmarks ({db_type})...")
        pooling_results = benchmarks.benchmark_connection_pooling()
        
        # Combine all results
        all_results = {
            **main_results,
            **optimization_results,
            **bulk_results,
            **scaling_results,
            **pooling_results
        }
        
        # Generate report
        report_filename = f"database_benchmark_report_{'file' if use_file_db else 'memory'}.md"
        report = benchmarks.runner.generate_performance_report(all_results, report_filename)
        
        print(f"\n{db_type} database benchmarks completed!")
        print(f"Total benchmarks run: {len(all_results)}")
        print(f"Report saved to: {report_filename}")
        
        # Performance comparison summary
        if main_results:
            avg_query_time = sum(r.mean_time for r in main_results.values() if r) / len([r for r in main_results.values() if r])
            print(f"Average query time: {avg_query_time * 1000:.3f} ms")
        
        print("-" * 60)
    
    return True


def run_database_stress_test():
    """Run database stress test with high concurrency."""
    print("Running Database Stress Test")
    print("=" * 40)
    
    benchmarks = DatabaseBenchmarks(use_file_db=False)
    benchmarks.setup()
    
    try:
        def stress_test_operation():
            operations_completed = 0
            
            for _ in range(50):  # 50 operations per thread
                try:
                    with benchmarks.db.get_connection() as conn:
                        cursor = conn.cursor()
                        
                        # Random operation
                        operation = random.choice(["read", "write", "update"])
                        
                        if operation == "read":
                            cursor.execute("SELECT * FROM users WHERE id = ?", (random.randint(1, 100),))
                            cursor.fetchall()
                        elif operation == "write":
                            cursor.execute(
                                "INSERT INTO submissions (user_id, exercise_id, code, score) VALUES (?, ?, ?, ?)",
                                (random.randint(1, 100), f"stress_ex_{random.randint(1, 1000)}", 
                                 "def stress_test(): pass", random.randint(60, 100))
                            )
                            conn.commit()
                        else:  # update
                            cursor.execute(
                                "UPDATE enrollments SET progress_percentage = ? WHERE user_id = ?",
                                (random.randint(0, 100), random.randint(1, 100))
                            )
                            conn.commit()
                        
                        operations_completed += 1
                
                except Exception as e:
                    print(f"Stress test operation failed: {e}")
                    continue
            
            return operations_completed
        
        # Run stress test with high concurrency
        print("Starting stress test with 20 concurrent threads...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stress_test_operation) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        total_operations = sum(results)
        duration = end_time - start_time
        operations_per_second = total_operations / duration
        
        print(f"Stress test completed:")
        print(f"  Total operations: {total_operations}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Operations per second: {operations_per_second:.2f}")
        print(f"  Active connections: {len(benchmarks.db.active_connections)}")
        
    finally:
        benchmarks.teardown()


if __name__ == "__main__":
    # Run comprehensive database benchmarks
    run_database_benchmarks()
    
    # Run stress test
    print("\n" + "=" * 60)
    run_database_stress_test()