# Location: src/python_mastery_hub/web/config/database.py

"""
Database Configuration

Manages database connections, connection pooling, migrations,
and database-related settings across different environments.
"""

import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from python_mastery_hub.core.config import get_settings
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

# SQLAlchemy base
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.pool: Optional[Pool] = None
        self._connection_cache = {}
        
    async def initialize(self) -> None:
        """Initialize database connections."""
        try:
            # Create SQLAlchemy async engine
            database_url = self._get_database_url()
            
            self.engine = create_async_engine(
                database_url,
                echo=settings.environment == "development",
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_timeout=settings.database_pool_timeout,
                pool_recycle=settings.database_pool_recycle
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create asyncpg connection pool for raw queries
            await self._create_connection_pool()
            
            # Test connection
            await self._test_connection()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _get_database_url(self) -> str:
        """Get database URL based on configuration."""
        if hasattr(settings, 'database_url') and settings.database_url:
            return settings.database_url
        
        # Build URL from components
        host = getattr(settings, 'database_host', 'localhost')
        port = getattr(settings, 'database_port', 5432)
        name = getattr(settings, 'database_name', 'python_mastery_hub')
        user = getattr(settings, 'database_user', 'postgres')
        password = getattr(settings, 'database_password', '')
        
        # Use asyncpg for async support
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
    
    async def _create_connection_pool(self) -> None:
        """Create asyncpg connection pool for raw queries."""
        try:
            # Extract connection parameters
            host = getattr(settings, 'database_host', 'localhost')
            port = getattr(settings, 'database_port', 5432)
            database = getattr(settings, 'database_name', 'python_mastery_hub')
            user = getattr(settings, 'database_user', 'postgres')
            password = getattr(settings, 'database_password', '')
            
            self.pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                min_size=settings.database_pool_min_size,
                max_size=settings.database_pool_size,
                command_timeout=settings.database_command_timeout
            )
            
            logger.info("AsyncPG connection pool created")
            
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """Test database connection."""
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                await session.commit()
                
            logger.info("Database connection test successful")
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session context manager."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get raw database connection from pool."""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a raw SQL query."""
        async with self.get_connection() as conn:
            if params:
                return await conn.fetch(query, *params.values())
            else:
                return await conn.fetch(query)
    
    async def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Execute a SQL command (INSERT, UPDATE, DELETE)."""
        async with self.get_connection() as conn:
            if params:
                return await conn.execute(command, *params.values())
            else:
                return await conn.execute(command)
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a database table."""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
        """
        
        async with self.get_connection() as conn:
            columns = await conn.fetch(query, table_name)
            
            return {
                'table_name': table_name,
                'columns': [dict(row) for row in columns],
                'column_count': len(columns)
            }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats_query = """
        SELECT 
            schemaname,
            tablename,
            attname as column_name,
            n_distinct,
            null_frac
        FROM pg_stats 
        WHERE schemaname = 'public'
        LIMIT 100
        """
        
        async with self.get_connection() as conn:
            stats = await conn.fetch(stats_query)
            
            # Get connection pool stats
            pool_stats = {
                'pool_size': self.pool.get_size(),
                'pool_min_size': self.pool.get_min_size(),
                'pool_max_size': self.pool.get_max_size(),
                'pool_idle_size': self.pool.get_idle_size()
            }
            
            return {
                'table_stats': [dict(row) for row in stats],
                'pool_stats': pool_stats
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Test basic query
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Check pool status
            pool_healthy = (
                self.pool is not None and 
                self.pool.get_size() > 0 and
                self.pool.get_idle_size() >= 0
            )
            
            return {
                'status': 'healthy' if pool_healthy else 'unhealthy',
                'response_time_ms': round(response_time, 2),
                'pool_status': {
                    'size': self.pool.get_size() if self.pool else 0,
                    'idle': self.pool.get_idle_size() if self.pool else 0,
                    'max_size': self.pool.get_max_size() if self.pool else 0
                },
                'timestamp': asyncio.get_event_loop().time()
            }
        
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }
    
    async def run_migrations(self) -> bool:
        """Run database migrations."""
        try:
            # This would typically use Alembic for migrations
            # For now, just create basic tables if they don't exist
            
            migration_queries = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(20) DEFAULT 'student',
                    is_active BOOLEAN DEFAULT true,
                    is_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_login TIMESTAMP WITH TIME ZONE,
                    login_count INTEGER DEFAULT 0
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    session_token TEXT UNIQUE NOT NULL,
                    refresh_token TEXT,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    device_info JSONB,
                    data JSONB DEFAULT '{}'::jsonb
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS user_progress (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    overall_progress DECIMAL(5,4) DEFAULT 0.0,
                    total_time_spent INTEGER DEFAULT 0,
                    modules_completed INTEGER DEFAULT 0,
                    total_modules INTEGER DEFAULT 0,
                    exercises_completed INTEGER DEFAULT 0,
                    total_exercises_attempted INTEGER DEFAULT 0,
                    average_score DECIMAL(5,4) DEFAULT 0.0,
                    current_level INTEGER DEFAULT 1,
                    experience_points INTEGER DEFAULT 0,
                    next_level_points INTEGER DEFAULT 100,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(user_id)
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS exercise_submissions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    exercise_id VARCHAR(100) NOT NULL,
                    code TEXT NOT NULL,
                    language VARCHAR(20) DEFAULT 'python',
                    score DECIMAL(5,2) DEFAULT 0.0,
                    max_score DECIMAL(5,2) DEFAULT 0.0,
                    passed BOOLEAN DEFAULT false,
                    execution_time DECIMAL(10,6) DEFAULT 0.0,
                    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    test_results JSONB DEFAULT '[]'::jsonb
                )
                """,
                
                """
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
                CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
                CREATE INDEX IF NOT EXISTS idx_exercise_submissions_user_id ON exercise_submissions(user_id);
                CREATE INDEX IF NOT EXISTS idx_exercise_submissions_exercise_id ON exercise_submissions(exercise_id);
                """
            ]
            
            async with self.get_connection() as conn:
                for query in migration_queries:
                    await conn.execute(query)
            
            logger.info("Database migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database migrations failed: {e}")
            return False
    
    async def backup_database(self, backup_path: str) -> bool:
        """Create database backup."""
        try:
            # This would typically use pg_dump
            # For now, just log the backup request
            logger.info(f"Database backup requested to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close database connections."""
        try:
            if self.pool:
                await self.pool.close()
                logger.info("Connection pool closed")
            
            if self.engine:
                await self.engine.dispose()
                logger.info("SQLAlchemy engine disposed")
                
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


async def get_database() -> DatabaseManager:
    """Get the global database manager instance."""
    global _database_manager
    
    if _database_manager is None:
        _database_manager = DatabaseManager()
        await _database_manager.initialize()
    
    return _database_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    db = await get_database()
    async with db.get_session() as session:
        yield session


class DatabaseConfig:
    """Database configuration settings."""
    
    def __init__(self):
        self.settings = get_settings()
    
    @property
    def connection_settings(self) -> Dict[str, Any]:
        """Get connection settings."""
        return {
            'host': getattr(self.settings, 'database_host', 'localhost'),
            'port': getattr(self.settings, 'database_port', 5432),
            'database': getattr(self.settings, 'database_name', 'python_mastery_hub'),
            'user': getattr(self.settings, 'database_user', 'postgres'),
            'password': getattr(self.settings, 'database_password', ''),
            'pool_size': getattr(self.settings, 'database_pool_size', 10),
            'max_overflow': getattr(self.settings, 'database_max_overflow', 20),
            'pool_timeout': getattr(self.settings, 'database_pool_timeout', 30),
            'pool_recycle': getattr(self.settings, 'database_pool_recycle', 3600)
        }
    
    @property
    def is_configured(self) -> bool:
        """Check if database is properly configured."""
        required_settings = ['database_host', 'database_name', 'database_user']
        return all(hasattr(self.settings, setting) for setting in required_settings)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate database configuration."""
        issues = []
        warnings = []
        
        # Check required settings
        if not hasattr(self.settings, 'database_host'):
            issues.append("Database host not configured")
        
        if not hasattr(self.settings, 'database_name'):
            issues.append("Database name not configured")
        
        if not hasattr(self.settings, 'database_user'):
            issues.append("Database user not configured")
        
        # Check optional but recommended settings
        if not hasattr(self.settings, 'database_password'):
            warnings.append("Database password not set")
        
        pool_size = getattr(self.settings, 'database_pool_size', 10)
        if pool_size < 5:
            warnings.append("Database pool size may be too small for production")
        elif pool_size > 50:
            warnings.append("Database pool size may be too large")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }