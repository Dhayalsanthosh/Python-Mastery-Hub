# File: src/python_mastery_hub/database/connection.py

"""Database connection management for Python Mastery Hub."""

import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy import Engine, text, event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy.pool import Pool

from .base import Base, create_engine_instance, get_database_url, settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and engines."""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._async_engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._async_session_factory: Optional[async_sessionmaker] = None
        self._test_engine: Optional[Engine] = None
        self._is_connected: bool = False
        
        # Connection retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Setup connection event listeners
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for connection monitoring."""
        
        @event.listens_for(Pool, "connect")
        def on_connect(dbapi_conn, connection_record):
            """Called when a connection is created."""
            logger.debug("Database connection established")
        
        @event.listens_for(Pool, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            """Called when a connection is retrieved from the pool."""
            logger.debug("Database connection checked out from pool")
        
        @event.listens_for(Pool, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            """Called when a connection is returned to the pool."""
            logger.debug("Database connection checked back into pool")
        
        @event.listens_for(Pool, "close")
        def on_close(dbapi_conn, connection_record):
            """Called when a connection is closed."""
            logger.debug("Database connection closed")
        
        @event.listens_for(Pool, "invalidate")
        def on_invalidate(dbapi_conn, connection_record, exception):
            """Called when a connection is invalidated."""
            logger.warning(f"Database connection invalidated: {exception}")
    
    @property
    def engine(self) -> Engine:
        """Get the main database engine."""
        if self._engine is None:
            self._engine = create_engine_instance()
            logger.info("Main database engine initialized")
        return self._engine
    
    @property
    def async_engine(self) -> AsyncEngine:
        """Get the async database engine."""
        if self._async_engine is None:
            database_url = get_database_url()
            # Convert to async URL
            if database_url.startswith('postgresql://'):
                async_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
            elif database_url.startswith('postgresql+psycopg2://'):
                async_url = database_url.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
            else:
                async_url = database_url
            
            self._async_engine = create_async_engine(
                async_url,
                echo=settings.echo,
                future=True,
                pool_size=settings.pool_size,
                max_overflow=settings.max_overflow,
                pool_timeout=settings.pool_timeout,
                pool_recycle=settings.pool_recycle,
                pool_pre_ping=settings.pool_pre_ping,
            )
            logger.info("Async database engine initialized")
        return self._async_engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get the session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False
            )
        return self._session_factory
    
    @property
    def async_session_factory(self) -> async_sessionmaker:
        """Get the async session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False
            )
        return self._async_session_factory
    
    def get_test_engine(self) -> Engine:
        """Get the test database engine."""
        if self._test_engine is None:
            self._test_engine = create_engine_instance(test=True)
            logger.info("Test database engine initialized")
        return self._test_engine
    
    def check_connection(self, engine: Optional[Engine] = None) -> bool:
        """Check if database connection is working.
        
        Args:
            engine: Engine to test. If None, uses main engine.
            
        Returns:
            True if connection is working, False otherwise
        """
        if engine is None:
            engine = self.engine
        
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.debug("Database connection check successful")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    async def check_async_connection(self, engine: Optional[AsyncEngine] = None) -> bool:
        """Check if async database connection is working.
        
        Args:
            engine: Async engine to test. If None, uses main async engine.
            
        Returns:
            True if connection is working, False otherwise
        """
        if engine is None:
            engine = self.async_engine
        
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.debug("Async database connection check successful")
            return True
        except Exception as e:
            logger.error(f"Async database connection check failed: {e}")
            return False
    
    @contextmanager
    def get_connection(self, engine: Optional[Engine] = None):
        """Get a database connection context manager.
        
        Args:
            engine: Engine to use. If None, uses main engine.
            
        Yields:
            Database connection
        """
        if engine is None:
            engine = self.engine
        
        connection = None
        try:
            connection = engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    @asynccontextmanager
    async def get_async_connection(self, engine: Optional[AsyncEngine] = None):
        """Get an async database connection context manager.
        
        Args:
            engine: Async engine to use. If None, uses main async engine.
            
        Yields:
            Async database connection
        """
        if engine is None:
            engine = self.async_engine
        
        connection = None
        try:
            connection = await engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Async database connection error: {e}")
            if connection:
                await connection.rollback()
            raise
        finally:
            if connection:
                await connection.close()
    
    def create_all_tables(self, engine: Optional[Engine] = None):
        """Create all database tables.
        
        Args:
            engine: Engine to use. If None, uses main engine.
        """
        if engine is None:
            engine = self.engine
        
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("All database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    async def create_all_tables_async(self, engine: Optional[AsyncEngine] = None):
        """Create all database tables asynchronously.
        
        Args:
            engine: Async engine to use. If None, uses main async engine.
        """
        if engine is None:
            engine = self.async_engine
        
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("All database tables created successfully (async)")
        except Exception as e:
            logger.error(f"Failed to create database tables (async): {e}")
            raise
    
    def drop_all_tables(self, engine: Optional[Engine] = None):
        """Drop all database tables.
        
        Args:
            engine: Engine to use. If None, uses main engine.
        """
        if engine is None:
            engine = self.engine
        
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    async def drop_all_tables_async(self, engine: Optional[AsyncEngine] = None):
        """Drop all database tables asynchronously.
        
        Args:
            engine: Async engine to use. If None, uses main async engine.
        """
        if engine is None:
            engine = self.async_engine
        
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("All database tables dropped successfully (async)")
        except Exception as e:
            logger.error(f"Failed to drop database tables (async): {e}")
            raise
    
    def get_engine_info(self, engine: Optional[Engine] = None) -> Dict[str, Any]:
        """Get information about the database engine.
        
        Args:
            engine: Engine to inspect. If None, uses main engine.
            
        Returns:
            Dictionary with engine information
        """
        if engine is None:
            engine = self.engine
        
        pool = engine.pool
        
        return {
            'url': str(engine.url).replace(f":{engine.url.password}@", ":***@"),
            'driver': engine.dialect.name,
            'pool_class': pool.__class__.__name__,
            'pool_size': getattr(pool, 'size', lambda: 'N/A')(),
            'checked_in': getattr(pool, 'checkedin', lambda: 'N/A')(),
            'checked_out': getattr(pool, 'checkedout', lambda: 'N/A')(),
            'overflow': getattr(pool, 'overflow', lambda: 'N/A')(),
            'echo': engine.echo,
            'echo_pool': engine.echo_pool,
        }
    
    def close_all_connections(self):
        """Close all database connections and dispose engines."""
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("Main database engine disposed")
            
            if self._async_engine:
                asyncio.create_task(self._async_engine.dispose())
                logger.info("Async database engine disposed")
            
            if self._test_engine:
                self._test_engine.dispose()
                logger.info("Test database engine disposed")
            
            # Reset all instances
            self._engine = None
            self._async_engine = None
            self._test_engine = None
            self._session_factory = None
            self._async_session_factory = None
            self._is_connected = False
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
            raise


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def reset_database_manager():
    """Reset the global database manager instance."""
    global _db_manager
    if _db_manager:
        _db_manager.close_all_connections()
    _db_manager = None