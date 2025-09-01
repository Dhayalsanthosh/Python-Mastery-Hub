# File: scripts/migrate_db.py
# Database migration management script

import os
import sys
import argparse
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask
    from flask_migrate import Migrate, upgrade, downgrade, current, stamp, init, migrate as flask_migrate
    from sqlalchemy import create_engine, text
    from app import create_app, db
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure you're in the virtual environment and dependencies are installed")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Database migration management class"""
    
    def __init__(self, environment='development'):
        """Initialize the migrator with environment configuration"""
        self.environment = environment
        self.app = None
        self.migrate = None
        self.setup_app()
    
    def setup_app(self):
        """Setup Flask application and migration instance"""
        try:
            # Create app with specific environment
            os.environ['FLASK_ENV'] = self.environment
            self.app = create_app()
            self.migrate = Migrate(self.app, db)
            logger.info(f"Application setup completed for environment: {self.environment}")
        except Exception as e:
            logger.error(f"Failed to setup application: {e}")
            raise
    
    def check_database_connection(self):
        """Test database connectivity"""
        try:
            with self.app.app_context():
                engine = db.engine
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT 1"))
                    result.fetchone()
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def init_migrations(self):
        """Initialize migration repository"""
        try:
            with self.app.app_context():
                if Path('migrations').exists():
                    logger.warning("Migration repository already exists")
                    return False
                
                init()
                logger.info("Migration repository initialized")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize migrations: {e}")
            return False
    
    def create_migration(self, message=None, auto=True):
        """Create a new migration"""
        try:
            with self.app.app_context():
                if not message:
                    message = f"Auto migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                if auto:
                    flask_migrate(message=message)
                else:
                    # Create empty migration
                    flask_migrate(message=message, empty=True)
                
                logger.info(f"Migration created: {message}")
                return True
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return False
    
    def upgrade_database(self, revision='head'):
        """Upgrade database to specified revision"""
        try:
            with self.app.app_context():
                logger.info(f"Upgrading database to revision: {revision}")
                
                # Get current revision before upgrade
                current_rev = current()
                logger.info(f"Current revision: {current_rev}")
                
                # Perform upgrade
                upgrade(revision=revision)
                
                # Get new revision after upgrade
                new_rev = current()
                logger.info(f"Upgraded to revision: {new_rev}")
                
                return True
        except Exception as e:
            logger.error(f"Failed to upgrade database: {e}")
            return False
    
    def downgrade_database(self, revision):
        """Downgrade database to specified revision"""
        try:
            with self.app.app_context():
                logger.info(f"Downgrading database to revision: {revision}")
                
                # Get current revision before downgrade
                current_rev = current()
                logger.info(f"Current revision: {current_rev}")
                
                # Confirm downgrade
                if self.environment == 'production':
                    confirm = input(f"Are you sure you want to downgrade production database to {revision}? (yes/no): ")
                    if confirm.lower() != 'yes':
                        logger.info("Downgrade cancelled")
                        return False
                
                # Perform downgrade
                downgrade(revision=revision)
                
                # Get new revision after downgrade
                new_rev = current()
                logger.info(f"Downgraded to revision: {new_rev}")
                
                return True
        except Exception as e:
            logger.error(f"Failed to downgrade database: {e}")
            return False
    
    def get_current_revision(self):
        """Get current database revision"""
        try:
            with self.app.app_context():
                rev = current()
                logger.info(f"Current database revision: {rev}")
                return rev
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    def stamp_database(self, revision='head'):
        """Mark database as being at a particular revision without running migrations"""
        try:
            with self.app.app_context():
                logger.info(f"Stamping database with revision: {revision}")
                stamp(revision=revision)
                logger.info("Database stamping completed")
                return True
        except Exception as e:
            logger.error(f"Failed to stamp database: {e}")
            return False
    
    def get_migration_history(self):
        """Get migration history"""
        try:
            with self.app.app_context():
                # Run alembic history command
                result = subprocess.run(
                    ['flask', 'db', 'history'],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(self.app.instance_path)
                )
                
                if result.returncode == 0:
                    logger.info("Migration history:")
                    print(result.stdout)
                    return result.stdout
                else:
                    logger.error(f"Failed to get migration history: {result.stderr}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return None
    
    def validate_migrations(self):
        """Validate migration scripts"""
        try:
            migrations_dir = Path('migrations/versions')
            if not migrations_dir.exists():
                logger.warning("No migrations directory found")
                return True
            
            migration_files = list(migrations_dir.glob('*.py'))
            logger.info(f"Found {len(migration_files)} migration files")
            
            # Basic validation
            for migration_file in migration_files:
                try:
                    with open(migration_file, 'r') as f:
                        content = f.read()
                        
                    # Check for required functions
                    if 'def upgrade():' not in content:
                        logger.error(f"Missing upgrade() function in {migration_file}")
                        return False
                    
                    if 'def downgrade():' not in content:
                        logger.error(f"Missing downgrade() function in {migration_file}")
                        return False
                    
                    logger.debug(f"Migration file validated: {migration_file}")
                
                except Exception as e:
                    logger.error(f"Error validating migration file {migration_file}: {e}")
                    return False
            
            logger.info("All migration files validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate migrations: {e}")
            return False
    
    def backup_before_migration(self):
        """Create database backup before running migrations"""
        try:
            backup_script = Path(__file__).parent / 'backup_db.sh'
            if not backup_script.exists():
                logger.warning("Backup script not found, skipping backup")
                return True
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"backups/pre_migration_{self.environment}_{timestamp}.sql"
            
            cmd = [
                'bash', str(backup_script),
                '--env', self.environment,
                '--output', backup_file,
                '--compress'
            ]
            
            logger.info("Creating pre-migration backup...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Pre-migration backup created: {backup_file}")
                return backup_file
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def run_data_migrations(self):
        """Run custom data migration scripts"""
        try:
            data_migrations_dir = Path('migrations/data')
            if not data_migrations_dir.exists():
                logger.info("No data migrations directory found")
                return True
            
            # Get list of data migration scripts
            scripts = sorted(data_migrations_dir.glob('*.py'))
            if not scripts:
                logger.info("No data migration scripts found")
                return True
            
            logger.info(f"Found {len(scripts)} data migration scripts")
            
            with self.app.app_context():
                for script in scripts:
                    logger.info(f"Running data migration: {script.name}")
                    
                    # Import and run the migration script
                    try:
                        spec = importlib.util.spec_from_file_location("data_migration", script)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'migrate'):
                            module.migrate(db)
                            logger.info(f"Data migration completed: {script.name}")
                        else:
                            logger.warning(f"No migrate() function found in {script.name}")
                    
                    except Exception as e:
                        logger.error(f"Data migration failed {script.name}: {e}")
                        return False
            
            logger.info("All data migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run data migrations: {e}")
            return False

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Database migration management')
    parser.add_argument('--env', default='development', 
                       choices=['development', 'staging', 'production'],
                       help='Environment to use')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize migration repository')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new migration')
    create_parser.add_argument('-m', '--message', help='Migration message')
    create_parser.add_argument('--empty', action='store_true', help='Create empty migration')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('-r', '--revision', default='head', help='Target revision')
    upgrade_parser.add_argument('--backup', action='store_true', help='Create backup before upgrade')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', help='Target revision')
    downgrade_parser.add_argument('--backup', action='store_true', help='Create backup before downgrade')
    
    # Current command
    subparsers.add_parser('current', help='Show current revision')
    
    # History command
    subparsers.add_parser('history', help='Show migration history')
    
    # Stamp command
    stamp_parser = subparsers.add_parser('stamp', help='Stamp database with revision')
    stamp_parser.add_argument('revision', help='Revision to stamp')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate migration scripts')
    
    # Data migrations command
    subparsers.add_parser('data', help='Run data migration scripts')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize migrator
    migrator = DatabaseMigrator(args.env)
    
    # Check database connection
    if not migrator.check_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    success = True
    
    try:
        if args.command == 'init':
            success = migrator.init_migrations()
        
        elif args.command == 'create':
            success = migrator.create_migration(
                message=args.message,
                auto=not args.empty
            )
        
        elif args.command == 'upgrade':
            if args.backup:
                backup_file = migrator.backup_before_migration()
                if backup_file:
                    logger.info(f"Backup created: {backup_file}")
            
            success = migrator.upgrade_database(args.revision)
        
        elif args.command == 'downgrade':
            if args.backup:
                backup_file = migrator.backup_before_migration()
                if backup_file:
                    logger.info(f"Backup created: {backup_file}")
            
            success = migrator.downgrade_database(args.revision)
        
        elif args.command == 'current':
            migrator.get_current_revision()
        
        elif args.command == 'history':
            migrator.get_migration_history()
        
        elif args.command == 'stamp':
            success = migrator.stamp_database(args.revision)
        
        elif args.command == 'validate':
            success = migrator.validate_migrations()
        
        elif args.command == 'data':
            success = migrator.run_data_migrations()
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    if success:
        logger.info("Operation completed successfully")
        sys.exit(0)
    else:
        logger.error("Operation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()