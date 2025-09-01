# File: security/compliance/audit_logger.py
"""
Audit Logger Implementation
Provides comprehensive audit logging for security, compliance, and operational monitoring.
Supports multiple output formats, encryption, and compliance frameworks.
"""

import json
import logging
import hashlib
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import gzip
import sqlite3
from cryptography.fernet import Fernet
import socket
import os
import uuid


class AuditLevel(Enum):
    """Audit event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class AuditCategory(Enum):
    """Categories of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIGURATION = "system_configuration"
    USER_MANAGEMENT = "user_management"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_EVENT = "compliance_event"
    BUSINESS_PROCESS = "business_process"
    NETWORK_ACTIVITY = "network_activity"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    API_CALL = "api_call"
    PERFORMANCE = "performance"
    ERROR_EVENT = "error_event"


class AuditAction(Enum):
    """Types of actions being audited"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    CONFIGURATION_CHANGED = "configuration_changed"
    PASSWORD_CHANGED = "password_changed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"


class ComplianceFramework(Enum):
    """Compliance frameworks requiring audit trails"""
    SOX = "sox"                    # Sarbanes-Oxley Act
    GDPR = "gdpr"                  # General Data Protection Regulation
    HIPAA = "hipaa"                # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"            # Payment Card Industry Data Security Standard
    ISO27001 = "iso27001"          # ISO/IEC 27001
    SOC2 = "soc2"                  # Service Organization Control 2
    FISMA = "fisma"                # Federal Information Security Management Act
    NIST = "nist"                  # NIST Cybersecurity Framework
    COBIT = "cobit"                # Control Objectives for Information and Related Technology


@dataclass
class AuditEvent:
    """Represents an audit event"""
    event_id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    action: AuditAction
    actor: str                     # User/system performing the action
    target: str                    # Resource being acted upon
    result: str                    # Success/failure/pending
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    compliance_frameworks: Set[ComplianceFramework] = field(default_factory=set)
    risk_score: int = 0            # 0-100 risk assessment
    sensitive_data: bool = False
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        
        # Auto-assign compliance frameworks based on category and action
        self._assign_compliance_frameworks()
    
    def _assign_compliance_frameworks(self):
        """Automatically assign relevant compliance frameworks"""
        # GDPR - any data access or modification
        if self.category in [AuditCategory.DATA_ACCESS, AuditCategory.DATA_MODIFICATION]:
            self.compliance_frameworks.add(ComplianceFramework.GDPR)
        
        # SOX - financial data and system configurations
        if "financial" in self.target.lower() or self.category == AuditCategory.SYSTEM_CONFIGURATION:
            self.compliance_frameworks.add(ComplianceFramework.SOX)
        
        # Security events apply to multiple frameworks
        if self.category == AuditCategory.SECURITY_EVENT:
            self.compliance_frameworks.update([
                ComplianceFramework.ISO27001,
                ComplianceFramework.SOC2,
                ComplianceFramework.NIST
            ])
        
        # Authentication events
        if self.category == AuditCategory.AUTHENTICATION:
            self.compliance_frameworks.update([
                ComplianceFramework.SOC2,
                ComplianceFramework.ISO27001,
                ComplianceFramework.PCI_DSS
            ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        data['category'] = self.category.value
        data['action'] = self.action.value
        data['compliance_frameworks'] = [f.value for f in self.compliance_frameworks]
        return data
    
    def to_json(self) -> str:
        """Convert audit event to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for integrity verification"""
        data = self.to_json()
        return hashlib.sha256(data.encode()).hexdigest()


class AuditFilter:
    """Filters audit events based on criteria"""
    
    def __init__(self, 
                 min_level: AuditLevel = AuditLevel.INFO,
                 categories: Set[AuditCategory] = None,
                 actors: Set[str] = None,
                 exclude_actors: Set[str] = None,
                 compliance_frameworks: Set[ComplianceFramework] = None,
                 time_range: tuple = None):
        self.min_level = min_level
        self.categories = categories
        self.actors = actors
        self.exclude_actors = exclude_actors or set()
        self.compliance_frameworks = compliance_frameworks
        self.time_range = time_range
    
    def should_log(self, event: AuditEvent) -> bool:
        """Determine if event should be logged based on filter criteria"""
        # Check minimum level
        level_priority = {
            AuditLevel.DEBUG: 0,
            AuditLevel.INFO: 1,
            AuditLevel.WARNING: 2,
            AuditLevel.ERROR: 3,
            AuditLevel.CRITICAL: 4,
            AuditLevel.SECURITY: 5,
            AuditLevel.COMPLIANCE: 5
        }
        
        if level_priority.get(event.level, 0) < level_priority.get(self.min_level, 0):
            return False
        
        # Check categories
        if self.categories and event.category not in self.categories:
            return False
        
        # Check actors
        if self.actors and event.actor not in self.actors:
            return False
        
        if event.actor in self.exclude_actors:
            return False
        
        # Check compliance frameworks
        if self.compliance_frameworks and not event.compliance_frameworks.intersection(self.compliance_frameworks):
            return False
        
        # Check time range
        if self.time_range:
            start_time, end_time = self.time_range
            if not (start_time <= event.timestamp <= end_time):
                return False
        
        return True


class AuditStorage(ABC):
    """Abstract base class for audit storage backends"""
    
    @abstractmethod
    def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event"""
        pass
    
    @abstractmethod
    def retrieve_events(self, filter: AuditFilter = None, limit: int = 1000) -> List[AuditEvent]:
        """Retrieve audit events with optional filtering"""
        pass
    
    @abstractmethod
    def get_event_count(self, filter: AuditFilter = None) -> int:
        """Get count of events matching filter"""
        pass
    
    @abstractmethod
    def cleanup_old_events(self, older_than: datetime) -> int:
        """Clean up events older than specified date"""
        pass


class FileAuditStorage(AuditStorage):
    """File-based audit storage with rotation and compression"""
    
    def __init__(self, 
                 log_directory: str = "logs/audit",
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 max_files: int = 10,
                 compress_old_files: bool = True,
                 encrypt_files: bool = False,
                 encryption_key: bytes = None):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.compress_old_files = compress_old_files
        self.encrypt_files = encrypt_files
        
        if encrypt_files:
            self.cipher_suite = Fernet(encryption_key or Fernet.generate_key())
        
        self.current_file = None
        self.file_lock = threading.Lock()
        
        self._initialize_current_file()
    
    def _initialize_current_file(self):
        """Initialize the current log file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_{timestamp}.log"
        self.current_file = self.log_directory / filename
    
    def _rotate_file_if_needed(self):
        """Rotate log file if it exceeds maximum size"""
        if (self.current_file.exists() and 
            self.current_file.stat().st_size >= self.max_file_size):
            
            # Compress old file if enabled
            if self.compress_old_files:
                self._compress_file(self.current_file)
            
            # Create new file
            self._initialize_current_file()
            
            # Clean up old files
            self._cleanup_old_files()
    
    def _compress_file(self, file_path: Path):
        """Compress a log file"""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        file_path.unlink()  # Remove original file
    
    def _cleanup_old_files(self):
        """Remove old log files exceeding max_files limit"""
        log_files = list(self.log_directory.glob("audit_*.log*"))
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        for old_file in log_files[self.max_files:]:
            old_file.unlink()
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event to file"""
        try:
            with self.file_lock:
                self._rotate_file_if_needed()
                
                log_entry = event.to_json() + '\n'
                
                if self.encrypt_files:
                    log_entry = self.cipher_suite.encrypt(log_entry.encode()).decode()
                    log_entry += '\n'
                
                with open(self.current_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                return True
                
        except Exception as e:
            logging.error(f"Failed to store audit event: {e}")
            return False
    
    def retrieve_events(self, filter: AuditFilter = None, limit: int = 1000) -> List[AuditEvent]:
        """Retrieve audit events from files"""
        events = []
        log_files = list(self.log_directory.glob("audit_*.log*"))
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        for log_file in log_files:
            if len(events) >= limit:
                break
            
            try:
                if log_file.suffix == '.gz':
                    opener = gzip.open
                else:
                    opener = open
                
                with opener(log_file, 'rt', encoding='utf-8') as f:
                    for line in f:
                        if len(events) >= limit:
                            break
                        
                        try:
                            if self.encrypt_files:
                                line = self.cipher_suite.decrypt(line.strip().encode()).decode()
                            
                            event_data = json.loads(line.strip())
                            event = self._dict_to_event(event_data)
                            
                            if not filter or filter.should_log(event):
                                events.append(event)
                                
                        except Exception:
                            continue  # Skip malformed lines
                            
            except Exception as e:
                logging.error(f"Error reading audit file {log_file}: {e}")
                continue
        
        return events
    
    def get_event_count(self, filter: AuditFilter = None) -> int:
        """Get count of events matching filter"""
        count = 0
        log_files = list(self.log_directory.glob("audit_*.log*"))
        
        for log_file in log_files:
            try:
                if log_file.suffix == '.gz':
                    opener = gzip.open
                else:
                    opener = open
                
                with opener(log_file, 'rt', encoding='utf-8') as f:
                    for line in f:
                        try:
                            if self.encrypt_files:
                                line = self.cipher_suite.decrypt(line.strip().encode()).decode()
                            
                            event_data = json.loads(line.strip())
                            event = self._dict_to_event(event_data)
                            
                            if not filter or filter.should_log(event):
                                count += 1
                                
                        except Exception:
                            continue
                            
            except Exception as e:
                logging.error(f"Error reading audit file {log_file}: {e}")
                continue
        
        return count
    
    def cleanup_old_events(self, older_than: datetime) -> int:
        """Clean up events older than specified date"""
        # For file storage, we clean up entire files based on modification time
        cleaned_count = 0
        log_files = list(self.log_directory.glob("audit_*.log*"))
        
        for log_file in log_files:
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < older_than:
                log_file.unlink()
                cleaned_count += 1
        
        return cleaned_count
    
    def _dict_to_event(self, data: Dict[str, Any]) -> AuditEvent:
        """Convert dictionary to AuditEvent"""
        # Convert string enums back to enum objects
        data['level'] = AuditLevel(data['level'])
        data['category'] = AuditCategory(data['category'])
        data['action'] = AuditAction(data['action'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['compliance_frameworks'] = {ComplianceFramework(f) for f in data.get('compliance_frameworks', [])}
        
        return AuditEvent(**data)


class DatabaseAuditStorage(AuditStorage):
    """Database-based audit storage using SQLite"""
    
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the audit database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    target TEXT NOT NULL,
                    result TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    source_ip TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    correlation_id TEXT,
                    compliance_frameworks TEXT,
                    risk_score INTEGER DEFAULT 0,
                    sensitive_data BOOLEAN DEFAULT FALSE,
                    checksum TEXT
                )
            ''')
            
            # Create indexes for better query performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_actor ON audit_events(actor)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON audit_events(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_level ON audit_events(level)')
            conn.commit()
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event to database"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    checksum = event.calculate_checksum()
                    compliance_frameworks = json.dumps([f.value for f in event.compliance_frameworks])
                    
                    conn.execute('''
                        INSERT INTO audit_events (
                            event_id, timestamp, level, category, action, actor, target,
                            result, message, details, source_ip, user_agent, session_id,
                            correlation_id, compliance_frameworks, risk_score, sensitive_data, checksum
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event.event_id,
                        event.timestamp.isoformat(),
                        event.level.value,
                        event.category.value,
                        event.action.value,
                        event.actor,
                        event.target,
                        event.result,
                        event.message,
                        json.dumps(event.details),
                        event.source_ip,
                        event.user_agent,
                        event.session_id,
                        event.correlation_id,
                        compliance_frameworks,
                        event.risk_score,
                        event.sensitive_data,
                        checksum
                    ))
                    conn.commit()
                    
            return True
            
        except Exception as e:
            logging.error(f"Failed to store audit event: {e}")
            return False
    
    def retrieve_events(self, filter: AuditFilter = None, limit: int = 1000) -> List[AuditEvent]:
        """Retrieve audit events from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM audit_events"
                params = []
                where_conditions = []
                
                if filter:
                    if filter.min_level:
                        # This is a simplified level comparison
                        where_conditions.append("level IN (?, ?, ?, ?, ?)")
                        level_hierarchy = {
                            AuditLevel.DEBUG: ['COMPLIANCE', 'SECURITY', 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                            AuditLevel.INFO: ['COMPLIANCE', 'SECURITY', 'CRITICAL', 'ERROR', 'WARNING', 'INFO'],
                            AuditLevel.WARNING: ['COMPLIANCE', 'SECURITY', 'CRITICAL', 'ERROR', 'WARNING'],
                            AuditLevel.ERROR: ['COMPLIANCE', 'SECURITY', 'CRITICAL', 'ERROR'],
                            AuditLevel.CRITICAL: ['COMPLIANCE', 'SECURITY', 'CRITICAL'],
                            AuditLevel.SECURITY: ['COMPLIANCE', 'SECURITY'],
                            AuditLevel.COMPLIANCE: ['COMPLIANCE']
                        }
                        allowed_levels = level_hierarchy.get(filter.min_level, [])
                        params.extend(allowed_levels[:5])  # SQLite limitation
                    
                    if filter.categories:
                        placeholders = ','.join(['?' for _ in filter.categories])
                        where_conditions.append(f"category IN ({placeholders})")
                        params.extend([cat.value for cat in filter.categories])
                    
                    if filter.actors:
                        placeholders = ','.join(['?' for _ in filter.actors])
                        where_conditions.append(f"actor IN ({placeholders})")
                        params.extend(filter.actors)
                    
                    if filter.time_range:
                        start_time, end_time = filter.time_range
                        where_conditions.append("timestamp BETWEEN ? AND ?")
                        params.extend([start_time.isoformat(), end_time.isoformat()])
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event_data = dict(row)
                    event = self._row_to_event(event_data)
                    events.append(event)
                
                return events
                
        except Exception as e:
            logging.error(f"Failed to retrieve audit events: {e}")
            return []
    
    def get_event_count(self, filter: AuditFilter = None) -> int:
        """Get count of events matching filter"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT COUNT(*) FROM audit_events"
                params = []
                where_conditions = []
                
                if filter:
                    # Similar filtering logic as retrieve_events
                    if filter.categories:
                        placeholders = ','.join(['?' for _ in filter.categories])
                        where_conditions.append(f"category IN ({placeholders})")
                        params.extend([cat.value for cat in filter.categories])
                    
                    if filter.actors:
                        placeholders = ','.join(['?' for _ in filter.actors])
                        where_conditions.append(f"actor IN ({placeholders})")
                        params.extend(filter.actors)
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                cursor = conn.execute(query, params)
                return cursor.fetchone()[0]
                
        except Exception as e:
            logging.error(f"Failed to get event count: {e}")
            return 0
    
    def cleanup_old_events(self, older_than: datetime) -> int:
        """Clean up events older than specified date"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM audit_events WHERE timestamp < ?",
                        (older_than.isoformat(),)
                    )
                    conn.commit()
                    return cursor.rowcount
                    
        except Exception as e:
            logging.error(f"Failed to cleanup old events: {e}")
            return 0
    
    def _row_to_event(self, row_data: Dict[str, Any]) -> AuditEvent:
        """Convert database row to AuditEvent"""
        row_data['level'] = AuditLevel(row_data['level'])
        row_data['category'] = AuditCategory(row_data['category'])
        row_data['action'] = AuditAction(row_data['action'])
        row_data['timestamp'] = datetime.fromisoformat(row_data['timestamp'])
        row_data['details'] = json.loads(row_data['details'] or '{}')
        
        compliance_frameworks_data = json.loads(row_data.get('compliance_frameworks', '[]'))
        row_data['compliance_frameworks'] = {ComplianceFramework(f) for f in compliance_frameworks_data}
        
        # Remove database-specific fields
        row_data.pop('checksum', None)
        
        return AuditEvent(**row_data)


class AuditLogger:
    """Main audit logging system"""
    
    def __init__(self, 
                 storage: AuditStorage,
                 filters: List[AuditFilter] = None,
                 async_logging: bool = True,
                 queue_size: int = 10000):
        self.storage = storage
        self.filters = filters or []
        self.async_logging = async_logging
        
        # Async logging setup
        if async_logging:
            self.event_queue = queue.Queue(maxsize=queue_size)
            self.worker_thread = threading.Thread(target=self._process_events, daemon=True)
            self.running = True
            self.worker_thread.start()
        
        # System information
        self.hostname = socket.gethostname()
        self.process_id = os.getpid()
        
        # Event handlers
        self.event_handlers: List[Callable[[AuditEvent], None]] = []
    
    def add_filter(self, filter: AuditFilter):
        """Add an audit filter"""
        self.filters.append(filter)
    
    def add_event_handler(self, handler: Callable[[AuditEvent], None]):
        """Add an event handler for real-time processing"""
        self.event_handlers.append(handler)
    
    def log_event(self, 
                  level: AuditLevel,
                  category: AuditCategory,
                  action: AuditAction,
                  actor: str,
                  target: str,
                  result: str,
                  message: str,
                  **kwargs) -> str:
        """Log an audit event"""
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            level=level,
            category=category,
            action=action,
            actor=actor,
            target=target,
            result=result,
            message=message,
            **kwargs
        )
        
        # Apply filters
        for filter in self.filters:
            if not filter.should_log(event):
                return event.event_id
        
        # Call event handlers
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                logging.error(f"Event handler failed: {e}")
        
        # Store event
        if self.async_logging:
            try:
                self.event_queue.put_nowait(event)
            except queue.Full:
                logging.error("Audit event queue is full, dropping event")
        else:
            self.storage.store_event(event)
        
        return event.event_id
    
    def _process_events(self):
        """Process events from the queue (async worker)"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1.0)
                self.storage.store_event(event)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Failed to process audit event: {e}")
    
    def shutdown(self):
        """Shutdown the audit logger"""
        if self.async_logging:
            self.running = False
            self.event_queue.join()  # Wait for queue to empty
            self.worker_thread.join(timeout=5.0)
    
    # Convenience methods for common audit events
    
    def log_authentication(self, actor: str, result: str, **kwargs):
        """Log authentication event"""
        return self.log_event(
            level=AuditLevel.SECURITY,
            category=AuditCategory.AUTHENTICATION,
            action=AuditAction.LOGIN if result == "success" else AuditAction.ACCESS_DENIED,
            actor=actor,
            target="authentication_system",
            result=result,
            message=f"Authentication {result} for {actor}",
            **kwargs
        )
    
    def log_data_access(self, actor: str, target: str, action: AuditAction, result: str, **kwargs):
        """Log data access event"""
        return self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action=action,
            actor=actor,
            target=target,
            result=result,
            message=f"Data {action.value} on {target} by {actor}",
            **kwargs
        )
    
    def log_security_event(self, actor: str, target: str, message: str, **kwargs):
        """Log security event"""
        return self.log_event(
            level=AuditLevel.SECURITY,
            category=AuditCategory.SECURITY_EVENT,
            action=AuditAction.ACCESS_DENIED,  # Default, can be overridden
            actor=actor,
            target=target,
            result="detected",
            message=message,
            **kwargs
        )
    
    def log_configuration_change(self, actor: str, target: str, details: Dict[str, Any], **kwargs):
        """Log configuration change"""
        return self.log_event(
            level=AuditLevel.WARNING,
            category=AuditCategory.SYSTEM_CONFIGURATION,
            action=AuditAction.CONFIGURATION_CHANGED,
            actor=actor,
            target=target,
            result="success",
            message=f"Configuration changed for {target}",
            details=details,
            **kwargs
        )
    
    def log_user_management(self, actor: str, target: str, action: AuditAction, **kwargs):
        """Log user management event"""
        return self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_MANAGEMENT,
            action=action,
            actor=actor,
            target=target,
            result="success",
            message=f"User management: {action.value} for {target}",
            **kwargs
        )
    
    def log_compliance_event(self, framework: ComplianceFramework, actor: str, target: str, message: str, **kwargs):
        """Log compliance-specific event"""
        event_id = self.log_event(
            level=AuditLevel.COMPLIANCE,
            category=AuditCategory.COMPLIANCE_EVENT,
            action=AuditAction.APPROVE,  # Default, can be overridden
            actor=actor,
            target=target,
            result="logged",
            message=message,
            compliance_frameworks={framework},
            **kwargs
        )
        return event_id
    
    # Query methods
    
    def get_events(self, filter: AuditFilter = None, limit: int = 1000) -> List[AuditEvent]:
        """Retrieve audit events"""
        return self.storage.retrieve_events(filter, limit)
    
    def get_events_by_actor(self, actor: str, limit: int = 100) -> List[AuditEvent]:
        """Get events for a specific actor"""
        filter = AuditFilter(actors={actor})
        return self.storage.retrieve_events(filter, limit)
    
    def get_events_by_category(self, category: AuditCategory, limit: int = 100) -> List[AuditEvent]:
        """Get events for a specific category"""
        filter = AuditFilter(categories={category})
        return self.storage.retrieve_events(filter, limit)
    
    def get_security_events(self, hours_back: int = 24, limit: int = 100) -> List[AuditEvent]:
        """Get recent security events"""
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        filter = AuditFilter(
            categories={AuditCategory.SECURITY_EVENT},
            time_range=(start_time, datetime.utcnow())
        )
        return self.storage.retrieve_events(filter, limit)
    
    def get_compliance_events(self, framework: ComplianceFramework, days_back: int = 30) -> List[AuditEvent]:
        """Get compliance events for a specific framework"""
        start_time = datetime.utcnow() - timedelta(days=days_back)
        filter = AuditFilter(
            compliance_frameworks={framework},
            time_range=(start_time, datetime.utcnow())
        )
        return self.storage.retrieve_events(filter, 10000)
    
    def generate_audit_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        start_time = datetime.utcnow() - timedelta(days=days_back)
        filter = AuditFilter(time_range=(start_time, datetime.utcnow()))
        
        events = self.storage.retrieve_events(filter, 10000)
        
        # Basic statistics
        total_events = len(events)
        events_by_level = {}
        events_by_category = {}
        events_by_actor = {}
        events_by_day = {}
        
        for event in events:
            # Count by level
            level_key = event.level.value
            events_by_level[level_key] = events_by_level.get(level_key, 0) + 1
            
            # Count by category
            cat_key = event.category.value
            events_by_category[cat_key] = events_by_category.get(cat_key, 0) + 1
            
            # Count by actor
            events_by_actor[event.actor] = events_by_actor.get(event.actor, 0) + 1
            
            # Count by day
            day_key = event.timestamp.strftime("%Y-%m-%d")
            events_by_day[day_key] = events_by_day.get(day_key, 0) + 1
        
        # Security analysis
        security_events = [e for e in events if e.category == AuditCategory.SECURITY_EVENT]
        failed_logins = [e for e in events if e.action == AuditAction.ACCESS_DENIED and e.category == AuditCategory.AUTHENTICATION]
        
        # Compliance analysis
        compliance_summary = {}
        for framework in ComplianceFramework:
            framework_events = [e for e in events if framework in e.compliance_frameworks]
            compliance_summary[framework.value] = {
                "event_count": len(framework_events),
                "categories": list(set(e.category.value for e in framework_events))
            }
        
        return {
            "report_period": {
                "start_date": start_time.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": days_back
            },
            "summary": {
                "total_events": total_events,
                "security_events": len(security_events),
                "failed_logins": len(failed_logins),
                "unique_actors": len(events_by_actor)
            },
            "events_by_level": events_by_level,
            "events_by_category": events_by_category,
            "top_actors": dict(sorted(events_by_actor.items(), key=lambda x: x[1], reverse=True)[:10]),
            "events_by_day": events_by_day,
            "compliance_summary": compliance_summary,
            "security_analysis": {
                "recent_security_events": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "actor": e.actor,
                        "target": e.target,
                        "message": e.message
                    } for e in security_events[-10:]  # Last 10 security events
                ],
                "failed_login_analysis": {
                    "total_failures": len(failed_logins),
                    "unique_actors": len(set(e.actor for e in failed_logins)),
                    "top_failed_actors": dict(sorted(
                        {e.actor: sum(1 for x in failed_logins if x.actor == e.actor) for e in failed_logins}.items(),
                        key=lambda x: x[1], reverse=True
                    )[:5])
                }
            }
        }
    
    def cleanup_old_events(self, retention_days: int = 2555) -> int:
        """Clean up old audit events (default 7 years for compliance)"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        return self.storage.cleanup_old_events(cutoff_date)


class AuditReporter:
    """Generates various audit reports and exports"""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def export_to_csv(self, events: List[AuditEvent], filename: str):
        """Export events to CSV format"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'event_id', 'timestamp', 'level', 'category', 'action',
                'actor', 'target', 'result', 'message', 'source_ip',
                'session_id', 'correlation_id', 'risk_score'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                row = {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp.isoformat(),
                    'level': event.level.value,
                    'category': event.category.value,
                    'action': event.action.value,
                    'actor': event.actor,
                    'target': event.target,
                    'result': event.result,
                    'message': event.message,
                    'source_ip': event.source_ip,
                    'session_id': event.session_id,
                    'correlation_id': event.correlation_id,
                    'risk_score': event.risk_score
                }
                writer.writerow(row)
    
    def export_to_json(self, events: List[AuditEvent], filename: str):
        """Export events to JSON format"""
        events_data = [event.to_dict() for event in events]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'export_timestamp': datetime.utcnow().isoformat(),
                'event_count': len(events),
                'events': events_data
            }, jsonfile, indent=2, default=str)
    
    def generate_compliance_report(self, framework: ComplianceFramework, days_back: int = 30) -> Dict[str, Any]:
        """Generate framework-specific compliance report"""
        events = self.audit_logger.get_compliance_events(framework, days_back)
        
        # Framework-specific analysis
        if framework == ComplianceFramework.SOX:
            return self._generate_sox_report(events, days_back)
        elif framework == ComplianceFramework.GDPR:
            return self._generate_gdpr_report(events, days_back)
        elif framework == ComplianceFramework.PCI_DSS:
            return self._generate_pci_report(events, days_back)
        else:
            return self._generate_generic_compliance_report(framework, events, days_back)
    
    def _generate_sox_report(self, events: List[AuditEvent], days_back: int) -> Dict[str, Any]:
        """Generate SOX compliance report"""
        financial_events = [e for e in events if 'financial' in e.target.lower() or 'finance' in e.message.lower()]
        config_changes = [e for e in events if e.category == AuditCategory.SYSTEM_CONFIGURATION]
        access_events = [e for e in events if e.category == AuditCategory.DATA_ACCESS]
        
        return {
            "framework": "SOX",
            "period_days": days_back,
            "total_events": len(events),
            "financial_data_events": len(financial_events),
            "configuration_changes": len(config_changes),
            "data_access_events": len(access_events),
            "key_controls": {
                "financial_reporting_access": len([e for e in financial_events if e.action in [AuditAction.READ, AuditAction.UPDATE]]),
                "system_changes": len(config_changes),
                "privileged_access": len([e for e in events if 'admin' in e.actor.lower() or 'root' in e.actor.lower()])
            },
            "events": [e.to_dict() for e in events[:100]]  # Sample events
        }
    
    def _generate_gdpr_report(self, events: List[AuditEvent], days_back: int) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        data_events = [e for e in events if e.category in [AuditCategory.DATA_ACCESS, AuditCategory.DATA_MODIFICATION]]
        consent_events = [e for e in events if 'consent' in e.message.lower()]
        export_events = [e for e in events if e.action == AuditAction.EXPORT]
        deletion_events = [e for e in events if e.action == AuditAction.DELETE and e.sensitive_data]
        
        return {
            "framework": "GDPR",
            "period_days": days_back,
            "total_events": len(events),
            "personal_data_events": len(data_events),
            "consent_events": len(consent_events),
            "data_exports": len(export_events),
            "data_deletions": len(deletion_events),
            "rights_exercised": {
                "data_exports": len(export_events),
                "data_deletions": len(deletion_events),
                "access_requests": len([e for e in events if 'access_request' in e.message.lower()])
            },
            "events": [e.to_dict() for e in events[:100]]
        }
    
    def _generate_pci_report(self, events: List[AuditEvent], days_back: int) -> Dict[str, Any]:
        """Generate PCI DSS compliance report"""
        payment_events = [e for e in events if any(term in e.target.lower() for term in ['payment', 'card', 'transaction'])]
        auth_events = [e for e in events if e.category == AuditCategory.AUTHENTICATION]
        access_events = [e for e in events if e.category == AuditCategory.AUTHORIZATION]
        
        return {
            "framework": "PCI_DSS",
            "period_days": days_back,
            "total_events": len(events),
            "payment_related_events": len(payment_events),
            "authentication_events": len(auth_events),
            "authorization_events": len(access_events),
            "security_requirements": {
                "access_control": len(access_events),
                "authentication": len(auth_events),
                "cardholder_data_access": len([e for e in payment_events if e.action in [AuditAction.READ, AuditAction.UPDATE]])
            },
            "events": [e.to_dict() for e in events[:100]]
        }
    
    def _generate_generic_compliance_report(self, framework: ComplianceFramework, events: List[AuditEvent], days_back: int) -> Dict[str, Any]:
        """Generate generic compliance report"""
        return {
            "framework": framework.value,
            "period_days": days_back,
            "total_events": len(events),
            "events_by_category": {
                cat.value: len([e for e in events if e.category == cat])
                for cat in AuditCategory
            },
            "events_by_level": {
                level.value: len([e for e in events if e.level == level])
                for level in AuditLevel
            },
            "events": [e.to_dict() for e in events[:100]]
        }


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize audit storage and logger
    # storage = FileAuditStorage("logs/audit", encrypt_files=True)
    storage = DatabaseAuditStorage("audit_test.db")
    
    # Create audit logger with filters
    audit_filter = AuditFilter(min_level=AuditLevel.INFO)
    audit_logger = AuditLogger(storage, filters=[audit_filter])
    
    # Test various audit events
    print("Testing Audit Logger...")
    print("=" * 50)
    
    # Authentication events
    audit_logger.log_authentication(
        actor="john.doe@company.com",
        result="success",
        source_ip="192.168.1.100",
        user_agent="Mozilla/5.0...",
        session_id="sess_123"
    )
    
    audit_logger.log_authentication(
        actor="attacker@malicious.com",
        result="failed",
        source_ip="10.0.0.1",
        details={"reason": "invalid_credentials", "attempts": 3}
    )
    
    # Data access events
    audit_logger.log_data_access(
        actor="john.doe@company.com",
        target="customer_database",
        action=AuditAction.READ,
        result="success",
        sensitive_data=True,
        details={"table": "customers", "records_accessed": 150}
    )
    
    # Configuration changes
    audit_logger.log_configuration_change(
        actor="admin@company.com",
        target="firewall_rules",
        details={
            "old_rules": ["allow 80", "allow 443"],
            "new_rules": ["allow 80", "allow 443", "allow 8080"],
            "change_reason": "New application deployment"
        }
    )
    
    # Security events
    audit_logger.log_security_event(
        actor="security_system",
        target="login_endpoint",
        message="Multiple failed login attempts detected",
        details={
            "threshold_exceeded": True,
            "attempts_count": 10,
            "time_window": "5 minutes"
        },
        risk_score=75
    )
    
    # Compliance events
    audit_logger.log_compliance_event(
        framework=ComplianceFramework.GDPR,
        actor="privacy_officer@company.com",
        target="personal_data_processor",
        message="Data subject access request processed",
        details={
            "request_id": "DSR-001",
            "data_subject": "customer_123",
            "request_type": "access",
            "response_time_hours": 48
        }
    )
    
    # Wait for async processing
    time.sleep(2)
    
    # Test queries
    print("\nTesting Queries...")
    print("-" * 30)
    
    # Get recent events
    recent_events = audit_logger.get_events(limit=10)
    print(f"Recent events count: {len(recent_events)}")
    
    # Get security events
    security_events = audit_logger.get_security_events(hours_back=1)
    print(f"Security events in last hour: {len(security_events)}")
    
    # Get events by actor
    john_events = audit_logger.get_events_by_actor("john.doe@company.com")
    print(f"Events by john.doe: {len(john_events)}")
    
    # Generate audit report
    print("\nGenerating Audit Report...")
    print("-" * 30)
    
    report = audit_logger.generate_audit_report(days_back=1)
    print(f"Total events in report: {report['summary']['total_events']}")
    print(f"Security events: {report['summary']['security_events']}")
    print(f"Failed logins: {report['summary']['failed_logins']}")
    print(f"Unique actors: {report['summary']['unique_actors']}")
    
    # Test compliance reporting
    print("\nTesting Compliance Reporting...")
    print("-" * 30)
    
    reporter = AuditReporter(audit_logger)
    gdpr_report = reporter.generate_compliance_report(ComplianceFramework.GDPR, days_back=1)
    print(f"GDPR events: {gdpr_report['total_events']}")
    print(f"Personal data events: {gdpr_report['personal_data_events']}")
    
    # Export test
    print("\nTesting Export...")
    print("-" * 30)
    
    events = audit_logger.get_events(limit=5)
    reporter.export_to_json(events, "audit_export_test.json")
    reporter.export_to_csv(events, "audit_export_test.csv")
    print("Exported events to JSON and CSV")
    
    # Cleanup
    audit_logger.shutdown()
    print("\nAudit logger test completed successfully!")