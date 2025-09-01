"""
Transaction Manager Exercise Implementation.

This module provides a context manager exercise for database transaction
management with rollback, commit, and nested transaction support.
"""

import threading
import time
from contextlib import contextmanager
from typing import Optional, Any, Dict, List


class TransactionManagerExercise:
    """Exercise for implementing a database transaction context manager."""
    
    def __init__(self):
        self.title = "Database Transaction Manager"
        self.description = "Implement a context manager for database transactions"
        self.difficulty = "hard"
    
    def get_instructions(self) -> str:
        """Return exercise instructions."""
        return """
        Implement a context manager for database transactions with:
        
        1. Automatic transaction start on context entry
        2. Commit on successful completion
        3. Rollback on exceptions
        4. Nested transaction support using savepoints
        5. Transaction isolation levels
        6. Timeout handling
        7. Retry logic for transient failures
        8. Thread safety
        """
    
    def get_tasks(self) -> List[str]:
        """Return list of specific tasks."""
        return [
            "Create a transaction context manager",
            "Handle commit on successful completion", 
            "Handle rollback on exceptions",
            "Add nested transaction support with savepoints",
            "Include transaction isolation levels",
            "Add timeout and retry functionality",
            "Ensure thread safety",
            "Provide transaction statistics and logging"
        ]
    
    def get_starter_code(self) -> str:
        """Return starter code template."""
        return '''
class DatabaseConnection:
    """Simulated database connection."""
    def __init__(self):
        self.in_transaction = False
        self.operations = []
    
    def begin_transaction(self):
        # TODO: Start transaction
        pass
    
    def commit(self):
        # TODO: Commit transaction
        pass
    
    def rollback(self):
        # TODO: Rollback transaction
        pass

class TransactionManager:
    """Context manager for database transactions."""
    def __init__(self, db_connection):
        self.db = db_connection
    
    def __enter__(self):
        # TODO: Start transaction
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Handle commit/rollback
        pass
'''
    
    def get_solution(self) -> str:
        """Return complete solution."""
        return '''
import threading
import time
from contextlib import contextmanager
from typing import Optional, Any, Dict, List
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Simulated database connection with transaction support."""
    
    def __init__(self, connection_id: str = None):
        self.connection_id = connection_id or f"db_conn_{uuid.uuid4().hex[:8]}"
        self.in_transaction = False
        self.operations = []
        self.transaction_stack = []
        self.isolation_level = "READ_COMMITTED"
        self.lock = threading.RLock()
        self.failure_rate = 0.0  # For testing failure scenarios
    
    def begin_transaction(self, isolation_level: str = None) -> str:
        """Start a new transaction."""
        with self.lock:
            if isolation_level:
                self.isolation_level = isolation_level
            
            transaction_id = f"tx_{len(self.transaction_stack) + 1}_{int(time.time() * 1000) % 10000}"
            self.transaction_stack.append({
                'id': transaction_id,
                'operations': [],
                'savepoint': len(self.operations),
                'start_time': time.time()
            })
            self.in_transaction = True
            
            logger.info(f"[{self.connection_id}] BEGIN TRANSACTION {transaction_id} (isolation: {self.isolation_level})")
            return transaction_id
    
    def execute(self, sql: str):
        """Execute SQL operation."""
        with self.lock:
            # Simulate random failures for testing
            import random
            if self.failure_rate > 0 and random.random() < self.failure_rate:
                raise Exception(f"Simulated database error: {sql}")
            
            operation = {
                'sql': sql,
                'timestamp': time.time(),
                'transaction': self.transaction_stack[-1]['id'] if self.transaction_stack else None
            }
            
            self.operations.append(operation)
            if self.transaction_stack:
                self.transaction_stack[-1]['operations'].append(operation)
            
            logger.info(f"[{self.connection_id}] EXECUTE: {sql}")
            
            # Simulate potential errors based on SQL content
            if "TRIGGER_ERROR" in sql.upper():
                raise Exception(f"SQL Error: {sql}")
            
            # Simulate processing time
            time.sleep(0.001)
    
    def commit(self):
        """Commit current transaction."""
        with self.lock:
            if not self.transaction_stack:
                raise Exception("No active transaction to commit")
            
            transaction = self.transaction_stack.pop()
            duration = time.time() - transaction['start_time']
            
            logger.info(f"[{self.connection_id}] COMMIT TRANSACTION {transaction['id']} "
                       f"({len(transaction['operations'])} operations, {duration:.3f}s)")
            
            if not self.transaction_stack:
                self.in_transaction = False
            
            return transaction['id']
    
    def rollback(self):
        """Rollback current transaction."""
        with self.lock:
            if not self.transaction_stack:
                raise Exception("No active transaction to rollback")
            
            transaction = self.transaction_stack.pop()
            
            # Remove operations from this transaction
            self.operations = self.operations[:transaction['savepoint']]
            
            duration = time.time() - transaction['start_time']
            logger.info(f"[{self.connection_id}] ROLLBACK TRANSACTION {transaction['id']} "
                       f"({len(transaction['operations'])} operations rolled back, {duration:.3f}s)")
            
            if not self.transaction_stack:
                self.in_transaction = False
            
            return transaction['id']
    
    def savepoint(self, name: str) -> Dict[str, Any]:
        """Create a savepoint within current transaction."""
        with self.lock:
            if not self.in_transaction:
                raise Exception("No active transaction for savepoint")
            
            savepoint = {
                'name': name,
                'position': len(self.operations),
                'transaction': self.transaction_stack[-1]['id'],
                'timestamp': time.time()
            }
            
            logger.info(f"[{self.connection_id}] SAVEPOINT {name}")
            return savepoint
    
    def rollback_to_savepoint(self, savepoint: Dict[str, Any]):
        """Rollback to specific savepoint."""
        with self.lock:
            self.operations = self.operations[:savepoint['position']]
            logger.info(f"[{self.connection_id}] ROLLBACK TO SAVEPOINT {savepoint['name']}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        with self.lock:
            return {
                'connection_id': self.connection_id,
                'total_operations': len(self.operations),
                'active_transactions': len(self.transaction_stack),
                'in_transaction': self.in_transaction,
                'isolation_level': self.isolation_level
            }

class TransactionManager:
    """Context manager for database transactions with advanced features."""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 isolation_level: str = None,
                 auto_retry: int = 0,
                 timeout: float = None,
                 name: str = None):
        self.db = db_connection
        self.isolation_level = isolation_level
        self.auto_retry = auto_retry
        self.timeout = timeout
        self.name = name or f"tx_{uuid.uuid4().hex[:8]}"
        self.transaction_id = None
        self.start_time = None
        self.stats = {'attempts': 0, 'timeouts': 0, 'errors': 0}
    
    def __enter__(self):
        """Enter transaction context."""
        self.start_time = time.time()
        
        for attempt in range(self.auto_retry + 1):
            self.stats['attempts'] += 1
            
            try:
                self.transaction_id = self.db.begin_transaction(self.isolation_level)
                logger.info(f"Transaction {self.name} started (attempt {attempt + 1})")
                return self
            except Exception as e:
                self.stats['errors'] += 1
                if attempt == self.auto_retry:
                    logger.error(f"Transaction {self.name} failed after {attempt + 1} attempts: {e}")
                    raise
                
                logger.warning(f"Transaction {self.name} start failed (attempt {attempt + 1}), retrying: {e}")
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        try:
            # Check timeout
            if self.timeout and (time.time() - self.start_time) > self.timeout:
                self.stats['timeouts'] += 1
                logger.warning(f"Transaction {self.name} timeout exceeded ({self.timeout}s)")
                self.db.rollback()
                return False
            
            if exc_type is not None:
                self.stats['errors'] += 1
                logger.error(f"Exception in transaction {self.name}: {exc_type.__name__}: {exc_val}")
                self.db.rollback()
                return False  # Don't suppress the exception
            else:
                self.db.commit()
                logger.info(f"Transaction {self.name} completed successfully")
                return True
        
        except Exception as cleanup_error:
            self.stats['errors'] += 1
            logger.error(f"Error during transaction {self.name} cleanup: {cleanup_error}")
            return False
    
    def execute(self, sql: str):
        """Execute SQL within the transaction."""
        return self.db.execute(sql)
    
    def savepoint(self, name: str):
        """Create a savepoint within the transaction."""
        return self.db.savepoint(name)
    
    def rollback_to_savepoint(self, savepoint: Dict[str, Any]):
        """Rollback to a savepoint."""
        return self.db.rollback_to_savepoint(savepoint)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transaction statistics."""
        return {
            'name': self.name,
            'transaction_id': self.transaction_id,
            'duration': time.time() - self.start_time if self.start_time else 0,
            'stats': self.stats.copy(),
            'db_stats': self.db.get_stats()
        }

@contextmanager
def nested_transaction(db_connection: DatabaseConnection, name: str = "nested"):
    """Context manager for nested transactions using savepoints."""
    savepoint = db_connection.savepoint(name)
    try:
        yield savepoint
    except Exception as e:
        db_connection.rollback_to_savepoint(savepoint)
        logger.warning(f"Nested transaction '{name}' rolled back due to: {e}")
        raise

class TransactionPool:
    """Pool of database connections with transaction management."""
    
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.connections = [DatabaseConnection(f"pooled_conn_{i}") for i in range(pool_size)]
        self.available = list(self.connections)
        self.in_use = set()
        self.lock = threading.Lock()
    
    @contextmanager
    def get_transaction(self, **kwargs):
        """Get a transaction from the pool."""
        connection = self._acquire_connection()
        try:
            with TransactionManager(connection, **kwargs) as tx:
                yield tx
        finally:
            self._release_connection(connection)
    
    def _acquire_connection(self) -> DatabaseConnection:
        """Acquire a connection from the pool."""
        with self.lock:
            if not self.available:
                raise Exception("No available connections in pool")
            
            connection = self.available.pop()
            self.in_use.add(connection)
            return connection
    
    def _release_connection(self, connection: DatabaseConnection):
        """Release a connection back to the pool."""
        with self.lock:
            if connection in self.in_use:
                self.in_use.remove(connection)
                self.available.append(connection)

def test_transaction_manager():
    """Test the transaction manager implementation."""
    print("=== Transaction Manager Tests ===")
    
    db = DatabaseConnection("test_db")
    
    # Test 1: Basic successful transaction
    print("\\n1. Basic successful transaction:")
    try:
        with TransactionManager(db, name="basic_test") as tx:
            tx.execute("INSERT INTO users (name) VALUES ('Alice')")
            tx.execute("UPDATE users SET email='alice@example.com' WHERE name='Alice'")
            print("  Transaction completed successfully")
    except Exception as e:
        print(f"  Transaction failed: {e}")
    
    # Test 2: Failed transaction with rollback
    print("\\n2. Failed transaction with rollback:")
    try:
        with TransactionManager(db, name="failed_test") as tx:
            tx.execute("INSERT INTO users (name) VALUES ('Bob')")
            tx.execute("TRIGGER_ERROR - Invalid SQL")  # This will cause rollback
    except Exception as e:
        print(f"  Expected failure handled: {type(e).__name__}")
    
    # Test 3: Nested transactions with savepoints
    print("\\n3. Nested transactions with savepoints:")
    try:
        with TransactionManager(db, isolation_level="SERIALIZABLE", name="nested_test") as tx:
            tx.execute("INSERT INTO products (name) VALUES ('Product A')")
            
            # Nested transaction for related operations
            try:
                with nested_transaction(db, "product_details") as sp:
                    tx.execute("INSERT INTO product_details (product_id, description) VALUES (1, 'Description A')")
                    tx.execute("INSERT INTO product_prices (product_id, price) VALUES (1, 29.99)")
            except Exception as e:
                print(f"  Nested transaction failed: {e}")
            
            # Another nested transaction that fails
            try:
                with nested_transaction(db, "product_categories") as sp:
                    tx.execute("INSERT INTO product_categories (product_id, category) VALUES (1, 'Electronics')")
                    tx.execute("TRIGGER_ERROR - Category assignment failed")
            except Exception as e:
                print(f"  Second nested transaction failed but main transaction continues")
            
            tx.execute("UPDATE products SET status='active' WHERE name='Product A'")
    except Exception as e:
        print(f"  Main transaction failed: {e}")
    
    # Test 4: Transaction with timeout and retry
    print("\\n4. Transaction with advanced features:")
    try:
        with TransactionManager(db,
                              isolation_level="READ_UNCOMMITTED",
                              auto_retry=2,
                              timeout=5.0,
                              name="advanced_test") as tx:
            tx.execute("INSERT INTO logs (message) VALUES ('Advanced transaction test')")
            time.sleep(0.1)  # Simulate processing time
            tx.execute("UPDATE settings SET last_update = NOW()")
            
            stats = tx.get_stats()
            print(f"  Transaction stats: {stats}")
    except Exception as e:
        print(f"  Advanced transaction failed: {e}")
    
    # Test 5: Connection pool
    print("\\n5. Connection pool test:")
    pool = TransactionPool(pool_size=3)
    
    def worker_task(worker_id: int):
        """Worker task using connection pool."""
        try:
            with pool.get_transaction(name=f"worker_{worker_id}") as tx:
                tx.execute(f"INSERT INTO worker_logs (worker_id) VALUES ({worker_id})")
                time.sleep(0.1)  # Simulate work
                tx.execute(f"UPDATE worker_stats SET count = count + 1 WHERE worker_id = {worker_id}")
            print(f"  Worker {worker_id} completed successfully")
        except Exception as e:
            print(f"  Worker {worker_id} failed: {e}")
    
    # Run multiple workers
    import threading
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker_task, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\\nFinal database stats: {db.get_stats()}")
    print(f"Total operations executed: {len(db.operations)}")

if __name__ == "__main__":
    test_transaction_manager()
'''
    
    def get_test_cases(self) -> List[Dict[str, str]]:
        """Return test cases for validation."""
        return [
            {
                "name": "Basic transaction flow",
                "test": "Verify transaction starts, executes operations, and commits successfully"
            },
            {
                "name": "Exception handling",
                "test": "Verify transaction rolls back on exceptions"
            },
            {
                "name": "Nested transactions",
                "test": "Verify savepoints work for nested transaction scenarios"
            },
            {
                "name": "Isolation levels",
                "test": "Verify different isolation levels can be set"
            },
            {
                "name": "Timeout handling",
                "test": "Verify transactions timeout and rollback appropriately"
            },
            {
                "name": "Retry logic",
                "test": "Verify auto-retry works for transient failures"
            },
            {
                "name": "Thread safety",
                "test": "Verify transaction manager works correctly with multiple threads"
            }
        ]