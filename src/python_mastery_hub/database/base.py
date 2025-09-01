# File: src/python_mastery_hub/database/base.py

"""Database base configuration for Python Mastery Hub."""

import os
import logging
from typing import Optional
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import QueuePool, NullPool
from pydantic import BaseSettings, validator

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # Database connection settings
    database_url: str = "postgresql://user:password@localhost:5432/python_mastery_hub"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "python_mastery_hub"
    database_user: str = "user"
    database_password: str = "password"
    database_driver: str = "postgresql+psycopg2"
    
    # Connection pool settings
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    
    # SSL settings
    database_ssl_mode: str = "prefer"
    database_ssl_cert: Optional[str] = None
    database_ssl_key: Optional[str] = None
    database_ssl_ca: Optional[str] = None
    
    # Engine settings
    echo: bool = False
    echo_pool: bool = False
    future: bool = True
    
    # Test database settings
    test_database_url: Optional[str] = None
    test_database_name: str = "python_mastery_hub_test"
    
    class Config:
        env_file = ".env"
        env_prefix = "PMH_"
        case_sensitive = False
    
    @validator('database_url', pre=True, always=True)
    def assemble_database_url(cls, v, values):
        """Assemble database URL from individual components if not provided."""
        if v and v.startswith(('postgresql://', 'postgresql+psycopg2://', 'sqlite://')):
            return v
        
        # Build URL from components
        driver = values.get('database_driver', 'postgresql+psycopg2')
        user = values.get('database_user', 'user')
        password = values.get('database_password', 'password')
        host = values.get('database_host', 'localhost')
        port = values.get('database_port', 5432)
        database = values.get('database_name', 'python_mastery_hub')
        
        return f"{driver}://{user}:{password}@{host}:{port}/{database}"
    
    @validator('test_database_url', pre=True, always=True)
    def assemble_test_database_url(cls, v, values):
        """Assemble test database URL."""
        if v:
            return v
        
        # Use main database URL but change database name
        main_url = values.get('database_url')
        if main_url:
            parsed = urlparse(main_url)
            test_db_name = values.get('test_database_name', 'python_mastery_hub_test')
            return urlunparse(parsed._replace(path=f'/{test_db_name}'))
        
        return None


# Global settings instance
settings = DatabaseSettings()


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    def __repr__(self):
        """String representation of the model."""
        class_name = self.__class__.__name__
        attrs = []
        
        # Include id if it exists
        if hasattr(self, 'id'):
            attrs.append(f"id={self.id}")
        
        # Include other important fields
        for key in ['name', 'title', 'email', 'username']:
            if hasattr(self, key):
                value = getattr(self, key)
                if value:
                    attrs.append(f"{key}='{value}'")
                break
        
        attrs_str = ', '.join(attrs)
        return f"<{class_name}({attrs_str})>"
    
    def to_dict(self, exclude_fields: Optional[list] = None) -> dict:
        """Convert model instance to dictionary."""
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Handle datetime serialization
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                result[column.name] = value
        
        return result


def get_database_url(test: bool = False) -> str:
    """Get the database URL for the current environment.
    
    Args:
        test: Whether to return the test database URL
        
    Returns:
        Database URL string
    """
    if test and settings.test_database_url:
        return settings.test_database_url
    return settings.database_url


def create_engine_instance(
    database_url: Optional[str] = None,
    test: bool = False,
    **kwargs
) -> Engine:
    """Create a SQLAlchemy engine instance.
    
    Args:
        database_url: Database URL to use. If None, uses settings
        test: Whether to create engine for testing
        **kwargs: Additional engine configuration options
        
    Returns:
        SQLAlchemy Engine instance
    """
    if not database_url:
        database_url = get_database_url(test=test)
    
    # Default engine configuration
    engine_config = {
        'echo': settings.echo,
        'echo_pool': settings.echo_pool,
        'future': settings.future,
        'pool_pre_ping': settings.pool_pre_ping,
    }
    
    # Add pool configuration for non-SQLite databases
    if not database_url.startswith('sqlite'):
        engine_config.update({
            'poolclass': QueuePool,
            'pool_size': settings.pool_size,
            'max_overflow': settings.max_overflow,
            'pool_timeout': settings.pool_timeout,
            'pool_recycle': settings.pool_recycle,
        })
    else:
        # SQLite doesn't support connection pooling
        engine_config['poolclass'] = NullPool
    
    # Add SSL configuration if provided
    connect_args = {}
    if not database_url.startswith('sqlite'):
        ssl_config = {}
        if settings.database_ssl_mode:
            ssl_config['sslmode'] = settings.database_ssl_mode
        if settings.database_ssl_cert:
            ssl_config['sslcert'] = settings.database_ssl_cert
        if settings.database_ssl_key:
            ssl_config['sslkey'] = settings.database_ssl_key
        if settings.database_ssl_ca:
            ssl_config['sslrootcert'] = settings.database_ssl_ca
        
        if ssl_config:
            connect_args.update(ssl_config)
    
    if connect_args:
        engine_config['connect_args'] = connect_args
    
    # Override with any provided kwargs
    engine_config.update(kwargs)
    
    try:
        engine = create_engine(database_url, **engine_config)
        logger.info(f"Database engine created successfully for {'test' if test else 'main'} database")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def get_engine_info(engine: Engine) -> dict:
    """Get information about the database engine.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Returns:
        Dictionary with engine information
    """
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


# Create default engine instance
try:
    engine = create_engine_instance()
except Exception as e:
    logger.warning(f"Could not create default engine at import time: {e}")
    engine = None