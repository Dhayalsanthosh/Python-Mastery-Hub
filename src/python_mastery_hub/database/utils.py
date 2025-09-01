# File: src/python_mastery_hub/database/utils.py

"""Database utilities for Python Mastery Hub."""

import os
import sys
import logging
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from sqlalchemy import Engine, MetaData, Table, text, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

from .base import Base, get_database_url, settings
from .connection import get_database_manager
from .session import get_session, get_async_session

logger = logging.getLogger(__name__)


def create_tables(engine: Optional[Engine] = None) -> bool:
    """Create all database tables.
    
    Args:
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        Base.metadata.create_all(bind=engine)
        logger.info("All database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False


def drop_tables(engine: Optional[Engine] = None) -> bool:
    """Drop all database tables.
    
    Args:
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        Base.metadata.drop_all(bind=engine)
        logger.info("All database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        return False


def reset_database(engine: Optional[Engine] = None) -> bool:
    """Reset the database by dropping and recreating all tables.
    
    Args:
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if drop_tables(engine) and create_tables(engine):
            logger.info("Database reset successfully")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False


def check_database_connection(engine: Optional[Engine] = None) -> bool:
    """Check if database connection is working.
    
    Args:
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if connection is working, False otherwise
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_table_info(engine: Optional[Engine] = None) -> Dict[str, Any]:
    """Get information about database tables.
    
    Args:
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        Dictionary with table information
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        tables_info = {}
        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            tables_info[table_name] = {
                'columns': [
                    {
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': col.get('default'),
                        'primary_key': col.get('primary_key', False)
                    }
                    for col in columns
                ],
                'indexes': [
                    {
                        'name': idx['name'],
                        'columns': idx['column_names'],
                        'unique': idx['unique']
                    }
                    for idx in indexes
                ],
                'foreign_keys': [
                    {
                        'name': fk['name'],
                        'constrained_columns': fk['constrained_columns'],
                        'referred_table': fk['referred_table'],
                        'referred_columns': fk['referred_columns']
                    }
                    for fk in foreign_keys
                ]
            }
        
        return {
            'table_count': len(table_names),
            'tables': tables_info
        }
    except Exception as e:
        logger.error(f"Failed to get table info: {e}")
        return {}


def get_database_size(engine: Optional[Engine] = None) -> Dict[str, Any]:
    """Get database size information.
    
    Args:
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        Dictionary with size information
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        with engine.connect() as conn:
            # For PostgreSQL
            if engine.dialect.name == 'postgresql':
                db_name = engine.url.database
                result = conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_database_size('{db_name}')) as size,
                           pg_database_size('{db_name}') as size_bytes
                """))
                row = result.first()
                if row:
                    return {
                        'size': row[0],
                        'size_bytes': row[1]
                    }
            
            # For SQLite
            elif engine.dialect.name == 'sqlite':
                db_path = engine.url.database
                if os.path.exists(db_path):
                    size_bytes = os.path.getsize(db_path)
                    return {
                        'size': f"{size_bytes / 1024 / 1024:.2f} MB",
                        'size_bytes': size_bytes
                    }
        
        return {'size': 'Unknown', 'size_bytes': 0}
    except Exception as e:
        logger.error(f"Failed to get database size: {e}")
        return {'size': 'Error', 'size_bytes': 0}


def backup_database(backup_path: Union[str, Path], 
                   engine: Optional[Engine] = None) -> bool:
    """Create a database backup.
    
    Args:
        backup_path: Path where to save the backup
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # For PostgreSQL
        if engine.dialect.name == 'postgresql':
            url = engine.url
            cmd = [
                'pg_dump',
                '-h', str(url.host),
                '-p', str(url.port),
                '-U', str(url.username),
                '-d', str(url.database),
                '-f', str(backup_path),
                '--verbose'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = str(url.password)
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Database backup created successfully: {backup_path}")
                return True
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return False
        
        # For SQLite
        elif engine.dialect.name == 'sqlite':
            db_path = engine.url.database
            if os.path.exists(db_path):
                import shutil
                shutil.copy2(db_path, backup_path)
                logger.info(f"SQLite database backup created: {backup_path}")
                return True
            else:
                logger.error(f"SQLite database file not found: {db_path}")
                return False
        
        else:
            logger.error(f"Backup not supported for database type: {engine.dialect.name}")
            return False
    
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        return False


def restore_database(backup_path: Union[str, Path],
                    engine: Optional[Engine] = None) -> bool:
    """Restore database from backup.
    
    Args:
        backup_path: Path to the backup file
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        backup_path = Path(backup_path)
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # For PostgreSQL
        if engine.dialect.name == 'postgresql':
            url = engine.url
            cmd = [
                'psql',
                '-h', str(url.host),
                '-p', str(url.port),
                '-U', str(url.username),
                '-d', str(url.database),
                '-f', str(backup_path),
                '--verbose'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = str(url.password)
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Database restored successfully from: {backup_path}")
                return True
            else:
                logger.error(f"Database restore failed: {result.stderr}")
                return False
        
        # For SQLite
        elif engine.dialect.name == 'sqlite':
            db_path = engine.url.database
            import shutil
            shutil.copy2(backup_path, db_path)
            logger.info(f"SQLite database restored from: {backup_path}")
            return True
        
        else:
            logger.error(f"Restore not supported for database type: {engine.dialect.name}")
            return False
    
    except Exception as e:
        logger.error(f"Failed to restore database: {e}")
        return False


def run_migration(revision: str = "head", 
                 config_path: Optional[str] = None) -> bool:
    """Run database migrations using Alembic.
    
    Args:
        revision: Target revision (default: "head")
        config_path: Path to alembic.ini file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if config_path is None:
            # Look for alembic.ini in common locations
            possible_paths = [
                "alembic.ini",
                "migrations/alembic.ini",
                "src/migrations/alembic.ini"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if config_path is None:
                logger.error("Could not find alembic.ini file")
                return False
        
        # Create Alembic config
        alembic_cfg = Config(config_path)
        
        # Set the database URL
        database_url = get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migration
        command.upgrade(alembic_cfg, revision)
        logger.info(f"Database migration completed to revision: {revision}")
        return True
    
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False


def get_migration_status(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get the current migration status.
    
    Args:
        config_path: Path to alembic.ini file
        
    Returns:
        Dictionary with migration status information
    """
    try:
        if config_path is None:
            # Look for alembic.ini in common locations
            possible_paths = [
                "alembic.ini",
                "migrations/alembic.ini",
                "src/migrations/alembic.ini"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if config_path is None:
                return {'error': 'Could not find alembic.ini file'}
        
        # Create Alembic config
        alembic_cfg = Config(config_path)
        
        # Set the database URL
        database_url = get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        db_manager = get_database_manager()
        engine = db_manager.engine
        
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_revision = context.get_current_revision()
        
        return {
            'current_revision': current_revision,
            'database_url': str(engine.url).replace(f":{engine.url.password}@", ":***@")
        }
    
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        return {'error': str(e)}


def execute_sql_file(file_path: Union[str, Path],
                    engine: Optional[Engine] = None) -> bool:
    """Execute SQL commands from a file.
    
    Args:
        file_path: Path to the SQL file
        engine: Database engine to use. If None, uses default engine.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = get_database_manager()
        if engine is None:
            engine = db_manager.engine
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"SQL file not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        with engine.connect() as conn:
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                conn.execute(text(statement))
                conn.commit()
        
        logger.info(f"SQL file executed successfully: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to execute SQL file: {e}")
        return False