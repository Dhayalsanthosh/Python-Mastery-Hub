# File: src/python_mastery_hub/database/session.py

"""Database session management for Python Mastery Hub."""

import logging
from typing import Optional, Generator, AsyncGenerator, Any, Dict
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy import event

from .connection import get_database_manager

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages database session lifecycle and operations."""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self._setup_session_events()
    
    def _setup_session_events(self):
        """Setup session event listeners."""
        
        @event.listens_for(Session, "after_transaction_end")
        def receive_after_transaction_end(session, transaction):
            """Called after a transaction ends."""
            if transaction._parent is None:  # Only log for top-level transactions
                if hasattr(transaction, '_sa_rollback'):
                    logger.debug("Database transaction rolled back")
                else:
                    logger.debug("Database transaction committed")
        
        @event.listens_for(Session, "after_soft_rollback")
        def receive_after_soft_rollback(session, previous_transaction):
            """Called after a soft rollback."""
            logger.debug("Database session soft rollback")
    
    @contextmanager
    def get_session(self, 
                   autoflush: bool = True,
                   autocommit: bool = False,
                   expire_on_commit: bool = True) -> Generator[Session, None, None]:
        """Get a database session context manager.
        
        Args:
            autoflush: Whether to automatically flush before queries
            autocommit: Whether to automatically commit after each statement
            expire_on_commit: Whether to expire all instances after commit
            
        Yields:
            Database session
        """
        session = None
        try:
            session_factory = self.db_manager.session_factory
            session = session_factory()
            
            # Configure session behavior
            session.autoflush = autoflush
            session.autocommit = autocommit
            session.expire_on_commit = expire_on_commit
            
            logger.debug("Database session created")
            yield session
            
            # Commit if no autocommit and no exception occurred
            if not autocommit and session.dirty:
                session.commit()
                logger.debug("Database session committed")
                
        except Exception as e:
            logger.error(f"Database session error: {e}")
            if session:
                session.rollback()
                logger.debug("Database session rolled back due to error")
            raise
        finally:
            if session:
                session.close()
                logger.debug("Database session closed")
    
    @asynccontextmanager
    async def get_async_session(self,
                               autoflush: bool = True,
                               autocommit: bool = False,
                               expire_on_commit: bool = True) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session context manager.
        
        Args:
            autoflush: Whether to automatically flush before queries
            autocommit: Whether to automatically commit after each statement
            expire_on_commit: Whether to expire all instances after commit
            
        Yields:
            Async database session
        """
        session = None
        try:
            session_factory = self.db_manager.async_session_factory
            session = session_factory()
            
            # Configure session behavior
            session.autoflush = autoflush
            session.autocommit = autocommit
            session.expire_on_commit = expire_on_commit
            
            logger.debug("Async database session created")
            yield session
            
            # Commit if no autocommit and no exception occurred
            if not autocommit and session.dirty:
                await session.commit()
                logger.debug("Async database session committed")
                
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            if session:
                await session.rollback()
                logger.debug("Async database session rolled back due to error")
            raise
        finally:
            if session:
                await session.close()
                logger.debug("Async database session closed")
    
    def create_session(self, **kwargs) -> Session:
        """Create a new database session.
        
        Args:
            **kwargs: Additional session configuration options
            
        Returns:
            Database session
        """
        session_factory = self.db_manager.session_factory
        return session_factory(**kwargs)
    
    def create_async_session(self, **kwargs) -> AsyncSession:
        """Create a new async database session.
        
        Args:
            **kwargs: Additional session configuration options
            
        Returns:
            Async database session
        """
        session_factory = self.db_manager.async_session_factory
        return session_factory(**kwargs)
    
    @contextmanager
    def transaction(self, session: Session):
        """Transaction context manager for manual transaction control.
        
        Args:
            session: Database session to use
            
        Yields:
            Transaction object
        """
        transaction = session.begin()
        try:
            logger.debug("Database transaction started")
            yield transaction
            transaction.commit()
            logger.debug("Database transaction committed")
        except Exception as e:
            logger.error(f"Database transaction error: {e}")
            transaction.rollback()
            logger.debug("Database transaction rolled back")
            raise
    
    @asynccontextmanager
    async def async_transaction(self, session: AsyncSession):
        """Async transaction context manager for manual transaction control.
        
        Args:
            session: Async database session to use
            
        Yields:
            Async transaction object
        """
        transaction = await session.begin()
        try:
            logger.debug("Async database transaction started")
            yield transaction
            await transaction.commit()
            logger.debug("Async database transaction committed")
        except Exception as e:
            logger.error(f"Async database transaction error: {e}")
            await transaction.rollback()
            logger.debug("Async database transaction rolled back")
            raise
    
    def execute_with_retry(self, 
                          session: Session,
                          func,
                          *args,
                          max_retries: int = 3,
                          **kwargs) -> Any:
        """Execute a function with automatic retry on connection errors.
        
        Args:
            session: Database session to use
            func: Function to execute
            *args: Function arguments
            max_retries: Maximum number of retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(session, *args, **kwargs)
            except (DisconnectionError, SQLAlchemyError) as e:
                last_exception = e
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt < max_retries:
                    # Rollback and try to reconnect
                    try:
                        session.rollback()
                    except:
                        pass
                    
                    # Close and recreate session for next attempt
                    session.close()
                    session = self.create_session()
                else:
                    logger.error(f"Database operation failed after {max_retries + 1} attempts")
                    raise last_exception
        
        raise last_exception
    
    async def execute_async_with_retry(self,
                                     session: AsyncSession,
                                     func,
                                     *args,
                                     max_retries: int = 3,
                                     **kwargs) -> Any:
        """Execute an async function with automatic retry on connection errors.
        
        Args:
            session: Async database session to use
            func: Async function to execute
            *args: Function arguments
            max_retries: Maximum number of retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await func(session, *args, **kwargs)
            except (DisconnectionError, SQLAlchemyError) as e:
                last_exception = e
                logger.warning(f"Async database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt < max_retries:
                    # Rollback and try to reconnect
                    try:
                        await session.rollback()
                    except:
                        pass
                    
                    # Close and recreate session for next attempt
                    await session.close()
                    session = self.create_async_session()
                else:
                    logger.error(f"Async database operation failed after {max_retries + 1} attempts")
                    raise last_exception
        
        raise last_exception


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Convenience functions for direct session access
@contextmanager
def get_session(**kwargs) -> Generator[Session, None, None]:
    """Get a database session context manager.
    
    Args:
        **kwargs: Session configuration options
        
    Yields:
        Database session
    """
    session_manager = get_session_manager()
    with session_manager.get_session(**kwargs) as session:
        yield session


@asynccontextmanager
async def get_async_session(**kwargs) -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session context manager.
    
    Args:
        **kwargs: Session configuration options
        
    Yields:
        Async database session
    """
    session_manager = get_session_manager()
    async with session_manager.get_async_session(**kwargs) as session:
        yield session


def create_session(**kwargs) -> Session:
    """Create a new database session.
    
    Args:
        **kwargs: Session configuration options
        
    Returns:
        Database session
    """
    session_manager = get_session_manager()
    return session_manager.create_session(**kwargs)


def create_async_session(**kwargs) -> AsyncSession:
    """Create a new async database session.
    
    Args:
        **kwargs: Session configuration options
        
    Returns:
        Async database session
    """
    session_manager = get_session_manager()
    return session_manager.create_async_session(**kwargs)