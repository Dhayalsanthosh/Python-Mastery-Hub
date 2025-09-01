# File: security/policies/data_retention.py
"""
Data Retention Policy Implementation
Manages data lifecycle, retention periods, and automated cleanup
"""

import json
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import schedule
import time
from pathlib import Path


class RetentionAction(Enum):
    """Actions to take when retention period expires"""
    DELETE = "delete"
    ARCHIVE = "archive"
    ANONYMIZE = "anonymize"
    REVIEW = "review"
    MIGRATE = "migrate"


class DataCategory(Enum):
    """Data categories for retention policies"""
    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    AUDIT_LOGS = "audit_logs"
    SYSTEM_LOGS = "system_logs"
    BACKUP_DATA = "backup_data"
    TEMPORARY_DATA = "temporary_data"
    ARCHIVED_DATA = "archived_data"
    METADATA = "metadata"
    CONFIGURATION = "configuration"
    APPLICATION_DATA = "application_data"


class DataSensitivity(Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class RetentionStatus(Enum):
    """Status of retention policy application"""
    ACTIVE = "active"
    PENDING_REVIEW = "pending_review"
    PENDING_DELETION = "pending_deletion"
    DELETED = "deleted"
    ARCHIVED = "archived"
    ANONYMIZED = "anonymized"
    ERROR = "error"


@dataclass
class RetentionPolicy:
    """Defines a data retention policy"""
    policy_id: str
    name: str
    description: str
    data_category: DataCategory
    sensitivity_level: DataSensitivity
    retention_period_days: int
    action: RetentionAction
    conditions: Dict[str, Any] = field(default_factory=dict)
    exceptions: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_applicable(self, data_item: 'DataItem') -> bool:
        """Check if policy applies to a data item"""
        if not self.is_active:
            return False
        
        # Check category match
        if data_item.category != self.data_category:
            return False
        
        # Check sensitivity level
        if data_item.sensitivity != self.sensitivity_level:
            return False
        
        # Check exceptions
        if data_item.item_id in self.exceptions:
            return False
        
        # Check additional conditions
        for condition_key, condition_value in self.conditions.items():
            if not self._evaluate_condition(condition_key, condition_value, data_item):
                return False
        
        return True
    
    def _evaluate_condition(self, key: str, value: Any, data_item: 'DataItem') -> bool:
        """Evaluate a condition against a data item"""
        if key == "owner":
            return data_item.metadata.get("owner") == value
        elif key == "location":
            return data_item.location == value
        elif key == "min_size":
            return data_item.size_bytes >= value
        elif key == "max_size":
            return data_item.size_bytes <= value
        elif key == "tags":
            item_tags = set(data_item.metadata.get("tags", []))
            required_tags = set(value) if isinstance(value, list) else {value}
            return required_tags.issubset(item_tags)
        
        return True


@dataclass
class DataItem:
    """Represents a data item subject to retention policies"""
    item_id: str
    name: str
    category: DataCategory
    sensitivity: DataSensitivity
    location: str
    size_bytes: int
    created_at: datetime
    last_accessed: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retention_status: RetentionStatus = RetentionStatus.ACTIVE
    retention_policy_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        if self.last_modified is None:
            self.last_modified = self.created_at
    
    def calculate_checksum(self, content: bytes = None) -> str:
        """Calculate checksum for data integrity"""
        if content:
            self.checksum = hashlib.sha256(content).hexdigest()
        return self.checksum
    
    def update_access_time(self):
        """Update last access time"""
        self.last_accessed = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if data item has expired"""
        if self.expiry_date is None:
            return False
        return datetime.utcnow() > self.expiry_date


@dataclass
class RetentionJob:
    """Represents a retention job to be executed"""
    job_id: str
    policy_id: str
    data_items: List[str]  # List of data item IDs
    action: RetentionAction
    scheduled_time: datetime
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class DataStore(ABC):
    """Abstract interface for data storage backends"""
    
    @abstractmethod
    def get_data_item(self, item_id: str) -> Optional[DataItem]:
        """Get data item by ID"""
        pass
    
    @abstractmethod
    def list_data_items(self, filters: Dict[str, Any] = None) -> List[DataItem]:
        """List data items with optional filters"""
        pass
    
    @abstractmethod
    def delete_data_item(self, item_id: str) -> bool:
        """Delete data item"""
        pass
    
    @abstractmethod
    def archive_data_item(self, item_id: str, archive_location: str) -> bool:
        """Archive data item"""
        pass
    
    @abstractmethod
    def anonymize_data_item(self, item_id: str) -> bool:
        """Anonymize data item"""
        pass


class FileSystemDataStore(DataStore):
    """File system implementation of data store"""
    
    def __init__(self, base_path: str, metadata_file: str = "metadata.json"):
        self.base_path = Path(base_path)
        self.metadata_file = self.base_path / metadata_file
        self.data_items: Dict[str, DataItem] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for item_data in data.get('data_items', []):
                        item = DataItem(**item_data)
                        # Convert datetime strings back to datetime objects
                        for field_name in ['created_at', 'last_accessed', 'last_modified', 'expiry_date']:
                            if hasattr(item, field_name) and getattr(item, field_name):
                                setattr(item, field_name, datetime.fromisoformat(str(getattr(item, field_name))))
                        self.data_items[item.item_id] = item
            except Exception as e:
                logging.error(f"Failed to load metadata: {e}")
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            data = {
                'data_items': []
            }
            
            for item in self.data_items.values():
                item_data = {
                    'item_id': item.item_id,
                    'name': item.name,
                    'category': item.category.value,
                    'sensitivity': item.sensitivity.value,
                    'location': item.location,
                    'size_bytes': item.size_bytes,
                    'created_at': item.created_at.isoformat(),
                    'last_accessed': item.last_accessed.isoformat() if item.last_accessed else None,
                    'last_modified': item.last_modified.isoformat() if item.last_modified else None,
                    'metadata': item.metadata,
                    'retention_status': item.retention_status.value,
                    'retention_policy_id': item.retention_policy_id,
                    'expiry_date': item.expiry_date.isoformat() if item.expiry_date else None,
                    'checksum': item.checksum
                }
                data['data_items'].append(item_data)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save metadata: {e}")
    
    def get_data_item(self, item_id: str) -> Optional[DataItem]:
        """Get data item by ID"""
        return self.data_items.get(item_id)
    
    def list_data_items(self, filters: Dict[str, Any] = None) -> List[DataItem]:
        """List data items with optional filters"""
        items = list(self.data_items.values())
        
        if filters:
            if 'category' in filters:
                items = [item for item in items if item.category == filters['category']]
            if 'sensitivity' in filters:
                items = [item for item in items if item.sensitivity == filters['sensitivity']]
            if 'status' in filters:
                items = [item for item in items if item.retention_status == filters['status']]
            if 'expired' in filters and filters['expired']:
                items = [item for item in items if item.is_expired()]
        
        return items
    
    def add_data_item(self, item: DataItem):
        """Add data item"""
        self.data_items[item.item_id] = item
        self._save_metadata()
    
    def update_data_item(self, item: DataItem):
        """Update data item"""
        if item.item_id in self.data_items:
            self.data_items[item.item_id] = item
            self._save_metadata()
    
    def delete_data_item(self, item_id: str) -> bool:
        """Delete data item"""
        try:
            if item_id in self.data_items:
                item = self.data_items[item_id]
                file_path = Path(item.location)
                
                # Delete physical file if it exists
                if file_path.exists():
                    file_path.unlink()
                
                # Update metadata
                item.retention_status = RetentionStatus.DELETED
                self.update_data_item(item)
                
                return True
        except Exception as e:
            logging.error(f"Failed to delete data item {item_id}: {e}")
        
        return False
    
    def archive_data_item(self, item_id: str, archive_location: str) -> bool:
        """Archive data item"""
        try:
            if item_id in self.data_items:
                item = self.data_items[item_id]
                current_path = Path(item.location)
                archive_path = Path(archive_location)
                
                # Create archive directory
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file to archive location
                if current_path.exists():
                    current_path.rename(archive_path)
                    item.location = str(archive_path)
                
                # Update metadata
                item.retention_status = RetentionStatus.ARCHIVED
                self.update_data_item(item)
                
                return True
        except Exception as e:
            logging.error(f"Failed to archive data item {item_id}: {e}")
        
        return False
    
    def anonymize_data_item(self, item_id: str) -> bool:
        """Anonymize data item"""
        try:
            if item_id in self.data_items:
                item = self.data_items[item_id]
                
                # Simple anonymization - replace with hash
                file_path = Path(item.location)
                if file_path.exists():
                    # Create anonymized content
                    anonymized_content = f"ANONYMIZED_DATA_{hashlib.sha256(item_id.encode()).hexdigest()}"
                    
                    with open(file_path, 'w') as f:
                        f.write(anonymized_content)
                
                # Update metadata
                item.retention_status = RetentionStatus.ANONYMIZED
                item.metadata['anonymized_at'] = datetime.utcnow().isoformat()
                self.update_data_item(item)
                
                return True
        except Exception as e:
            logging.error(f"Failed to anonymize data item {item_id}: {e}")
        
        return False


class RetentionPolicyManager:
    """Manages retention policies and enforcement"""
    
    def __init__(self, data_store: DataStore):
        self.data_store = data_store
        self.policies: Dict[str, RetentionPolicy] = {}
        self.jobs: Dict[str, RetentionJob] = {}
        self.scheduler_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.action_handlers: Dict[RetentionAction, Callable] = {
            RetentionAction.DELETE: self._handle_delete,
            RetentionAction.ARCHIVE: self._handle_archive,
            RetentionAction.ANONYMIZE: self._handle_anonymize,
            RetentionAction.REVIEW: self._handle_review,
            RetentionAction.MIGRATE: self._handle_migrate
        }
        
        # Initialize default policies
        self._initialize_default_policies()
        
        # Setup scheduler
        self._setup_scheduler()
    
    def _initialize_default_policies(self):
        """Initialize default retention policies"""
        policies = [
            RetentionPolicy(
                policy_id="temp_data_policy",
                name="Temporary Data Cleanup",
                description="Delete temporary data after 7 days",
                data_category=DataCategory.TEMPORARY_DATA,
                sensitivity_level=DataSensitivity.INTERNAL,
                retention_period_days=7,
                action=RetentionAction.DELETE
            ),
            RetentionPolicy(
                policy_id="audit_log_policy",
                name="Audit Log Retention",
                description="Archive audit logs after 2 years",
                data_category=DataCategory.AUDIT_LOGS,
                sensitivity_level=DataSensitivity.CONFIDENTIAL,
                retention_period_days=730,
                action=RetentionAction.ARCHIVE
            ),
            RetentionPolicy(
                policy_id="personal_data_policy",
                name="Personal Data Retention",
                description="Review personal data after 3 years",
                data_category=DataCategory.PERSONAL_DATA,
                sensitivity_level=DataSensitivity.RESTRICTED,
                retention_period_days=1095,
                action=RetentionAction.REVIEW
            ),
            RetentionPolicy(
                policy_id="system_log_policy",
                name="System Log Cleanup",
                description="Delete system logs after 90 days",
                data_category=DataCategory.SYSTEM_LOGS,
                sensitivity_level=DataSensitivity.INTERNAL,
                retention_period_days=90,
                action=RetentionAction.DELETE
            )
        ]
        
        for policy in policies:
            self.add_policy(policy)
    
    def add_policy(self, policy: RetentionPolicy):
        """Add a retention policy"""
        self.policies[policy.policy_id] = policy
        logging.info(f"Added retention policy: {policy.name}")
    
    def remove_policy(self, policy_id: str):
        """Remove a retention policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logging.info(f"Removed retention policy: {policy_id}")
    
    def get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get retention policy by ID"""
        return self.policies.get(policy_id)
    
    def apply_policies_to_item(self, data_item: DataItem) -> Optional[RetentionPolicy]:
        """Apply retention policies to a data item"""
        for policy in self.policies.values():
            if policy.is_applicable(data_item):
                # Calculate expiry date
                expiry_date = data_item.created_at + timedelta(days=policy.retention_period_days)
                
                # Update data item
                data_item.retention_policy_id = policy.policy_id
                data_item.expiry_date = expiry_date
                
                if isinstance(self.data_store, FileSystemDataStore):
                    self.data_store.update_data_item(data_item)
                
                logging.info(f"Applied policy {policy.name} to data item {data_item.item_id}")
                return policy
        
        return None
    
    def scan_and_apply_policies(self):
        """Scan all data items and apply policies"""
        logging.info("Starting policy application scan")
        
        data_items = self.data_store.list_data_items()
        applied_count = 0
        
        for data_item in data_items:
            if data_item.retention_policy_id is None:
                if self.apply_policies_to_item(data_item):
                    applied_count += 1
        
        logging.info(f"Applied policies to {applied_count} data items")
    
    def identify_expired_items(self) -> List[DataItem]:
        """Identify data items that have expired"""
        expired_items = []
        data_items = self.data_store.list_data_items()
        
        for data_item in data_items:
            if (data_item.retention_status == RetentionStatus.ACTIVE and 
                data_item.is_expired()):
                expired_items.append(data_item)
        
        return expired_items
    
    def schedule_retention_jobs(self):
        """Schedule retention jobs for expired items"""
        expired_items = self.identify_expired_items()
        
        # Group by policy and action
        policy_groups: Dict[str, List[DataItem]] = {}
        
        for item in expired_items:
            policy_id = item.retention_policy_id
            if policy_id not in policy_groups:
                policy_groups[policy_id] = []
            policy_groups[policy_id].append(item)
        
        # Create jobs for each policy group
        for policy_id, items in policy_groups.items():
            policy = self.get_policy(policy_id)
            if policy:
                job_id = f"retention_job_{policy_id}_{int(time.time())}"
                job = RetentionJob(
                    job_id=job_id,
                    policy_id=policy_id,
                    data_items=[item.item_id for item in items],
                    action=policy.action,
                    scheduled_time=datetime.utcnow()
                )
                
                self.jobs[job_id] = job
                logging.info(f"Scheduled retention job {job_id} for {len(items)} items")
    
    def execute_retention_job(self, job_id: str) -> bool:
        """Execute a retention job"""
        if job_id not in self.jobs:
            logging.error(f"Retention job {job_id} failed: {e}")
            return False
    
    def _handle_delete(self, item_id: str) -> bool:
        """Handle delete action"""
        return self.data_store.delete_data_item(item_id)
    
    def _handle_archive(self, item_id: str) -> bool:
        """Handle archive action"""
        data_item = self.data_store.get_data_item(item_id)
        if not data_item:
            return False
        
        # Generate archive location
        archive_location = f"archive/{data_item.category.value}/{data_item.item_id}"
        return self.data_store.archive_data_item(item_id, archive_location)
    
    def _handle_anonymize(self, item_id: str) -> bool:
        """Handle anonymize action"""
        return self.data_store.anonymize_data_item(item_id)
    
    def _handle_review(self, item_id: str) -> bool:
        """Handle review action"""
        data_item = self.data_store.get_data_item(item_id)
        if not data_item:
            return False
        
        data_item.retention_status = RetentionStatus.PENDING_REVIEW
        if isinstance(self.data_store, FileSystemDataStore):
            self.data_store.update_data_item(data_item)
        
        logging.info(f"Data item {item_id} marked for review")
        return True
    
    def _handle_migrate(self, item_id: str) -> bool:
        """Handle migrate action"""
        # Implementation depends on migration target
        logging.info(f"Migration not implemented for item {item_id}")
        return False
    
    def _setup_scheduler(self):
        """Setup retention job scheduler"""
        # Schedule daily retention check
        schedule.every().day.at("02:00").do(self._run_retention_cycle)
        
        # Schedule weekly policy application
        schedule.every().monday.at("01:00").do(self.scan_and_apply_policies)
    
    def _run_retention_cycle(self):
        """Run complete retention cycle"""
        logging.info("Starting retention cycle")
        
        try:
            # Apply policies to new items
            self.scan_and_apply_policies()
            
            # Schedule jobs for expired items
            self.schedule_retention_jobs()
            
            # Execute pending jobs
            pending_jobs = [job for job in self.jobs.values() if job.status == "pending"]
            for job in pending_jobs:
                self.execute_retention_job(job.job_id)
            
            logging.info("Retention cycle completed successfully")
            
        except Exception as e:
            logging.error(f"Retention cycle failed: {e}")
    
    def start_scheduler(self):
        """Start the retention scheduler"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        
        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logging.info("Retention scheduler started")
    
    def stop_scheduler(self):
        """Stop the retention scheduler"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logging.info("Retention scheduler stopped")
    
    def get_retention_report(self) -> Dict[str, Any]:
        """Generate retention policy report"""
        data_items = self.data_store.list_data_items()
        
        report = {
            'summary': {
                'total_items': len(data_items),
                'active_items': 0,
                'expired_items': 0,
                'archived_items': 0,
                'deleted_items': 0,
                'pending_review': 0,
                'anonymized_items': 0
            },
            'policies': {},
            'upcoming_expirations': [],
            'failed_jobs': []
        }
        
        # Count by status
        for item in data_items:
            if item.retention_status == RetentionStatus.ACTIVE:
                report['summary']['active_items'] += 1
                if item.is_expired():
                    report['summary']['expired_items'] += 1
            elif item.retention_status == RetentionStatus.ARCHIVED:
                report['summary']['archived_items'] += 1
            elif item.retention_status == RetentionStatus.DELETED:
                report['summary']['deleted_items'] += 1
            elif item.retention_status == RetentionStatus.PENDING_REVIEW:
                report['summary']['pending_review'] += 1
            elif item.retention_status == RetentionStatus.ANONYMIZED:
                report['summary']['anonymized_items'] += 1
        
        # Policy statistics
        for policy in self.policies.values():
            applicable_items = [item for item in data_items if item.retention_policy_id == policy.policy_id]
            report['policies'][policy.policy_id] = {
                'name': policy.name,
                'applicable_items': len(applicable_items),
                'action': policy.action.value,
                'retention_days': policy.retention_period_days
            }
        
        # Upcoming expirations (next 30 days)
        future_date = datetime.utcnow() + timedelta(days=30)
        for item in data_items:
            if (item.retention_status == RetentionStatus.ACTIVE and 
                item.expiry_date and 
                datetime.utcnow() < item.expiry_date <= future_date):
                report['upcoming_expirations'].append({
                    'item_id': item.item_id,
                    'name': item.name,
                    'expiry_date': item.expiry_date.isoformat(),
                    'policy_id': item.retention_policy_id
                })
        
        # Failed jobs
        failed_jobs = [job for job in self.jobs.values() if job.status == "failed"]
        for job in failed_jobs:
            report['failed_jobs'].append({
                'job_id': job.job_id,
                'policy_id': job.policy_id,
                'error_message': job.error_message,
                'created_at': job.created_at.isoformat()
            })
        
        return report
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export retention configuration"""
        return {
            'policies': {
                policy_id: {
                    'name': policy.name,
                    'description': policy.description,
                    'data_category': policy.data_category.value,
                    'sensitivity_level': policy.sensitivity_level.value,
                    'retention_period_days': policy.retention_period_days,
                    'action': policy.action.value,
                    'conditions': policy.conditions,
                    'exceptions': policy.exceptions,
                    'is_active': policy.is_active
                }
                for policy_id, policy in self.policies.items()
            }
        }
    
    def import_configuration(self, config: Dict[str, Any]):
        """Import retention configuration"""
        for policy_id, policy_data in config.get('policies', {}).items():
            policy = RetentionPolicy(
                policy_id=policy_id,
                name=policy_data['name'],
                description=policy_data['description'],
                data_category=DataCategory(policy_data['data_category']),
                sensitivity_level=DataSensitivity(policy_data['sensitivity_level']),
                retention_period_days=policy_data['retention_period_days'],
                action=RetentionAction(policy_data['action']),
                conditions=policy_data.get('conditions', {}),
                exceptions=policy_data.get('exceptions', []),
                is_active=policy_data.get('is_active', True)
            )
            self.add_policy(policy)


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize data store and retention manager
    data_store = FileSystemDataStore("/tmp/test_data")
    retention_manager = RetentionPolicyManager(data_store)
    
    # Create sample data items
    sample_items = [
        DataItem(
            item_id="temp_001",
            name="temporary_file.tmp",
            category=DataCategory.TEMPORARY_DATA,
            sensitivity=DataSensitivity.INTERNAL,
            location="/tmp/temporary_file.tmp",
            size_bytes=1024,
            created_at=datetime.utcnow() - timedelta(days=10)
        ),
        DataItem(
            item_id="audit_001",
            name="audit_log_2023.log",
            category=DataCategory.AUDIT_LOGS,
            sensitivity=DataSensitivity.CONFIDENTIAL,
            location="/logs/audit_log_2023.log",
            size_bytes=50000,
            created_at=datetime.utcnow() - timedelta(days=800)
        ),
        DataItem(
            item_id="personal_001",
            name="user_data.json",
            category=DataCategory.PERSONAL_DATA,
            sensitivity=DataSensitivity.RESTRICTED,
            location="/data/user_data.json",
            size_bytes=2048,
            created_at=datetime.utcnow() - timedelta(days=1200),
            metadata={"owner": "user123", "tags": ["pii", "customer"]}
        )
    ]
    
    # Add sample items to data store
    for item in sample_items:
        data_store.add_data_item(item)
    
    # Apply policies
    print("Applying retention policies...")
    retention_manager.scan_and_apply_policies()
    
    # Check for expired items
    print("\nChecking for expired items...")
    expired_items = retention_manager.identify_expired_items()
    print(f"Found {len(expired_items)} expired items")
    
    for item in expired_items:
        policy = retention_manager.get_policy(item.retention_policy_id)
        print(f"- {item.name} (expires: {item.expiry_date}, action: {policy.action.value})")
    
    # Schedule and execute retention jobs
    if expired_items:
        print("\nScheduling retention jobs...")
        retention_manager.schedule_retention_jobs()
        
        # Execute pending jobs
        pending_jobs = [job for job in retention_manager.jobs.values() if job.status == "pending"]
        for job in pending_jobs:
            print(f"Executing job {job.job_id}...")
            success = retention_manager.execute_retention_job(job.job_id)
            print(f"Job result: {'Success' if success else 'Failed'}")
    
    # Generate report
    print("\nGenerating retention report...")
    report = retention_manager.get_retention_report()
    print(f"Total items: {report['summary']['total_items']}")
    print(f"Active items: {report['summary']['active_items']}")
    print(f"Expired items: {report['summary']['expired_items']}")
    print(f"Archived items: {report['summary']['archived_items']}")
    print(f"Deleted items: {report['summary']['deleted_items']}")
    
    # Export configuration
    config = retention_manager.export_configuration()
    print(f"\nExported configuration with {len(config['policies'])} policies") not found")
            return False
        
        job = self.jobs[job_id]
        job.status = "running"
        
        try:
            handler = self.action_handlers.get(job.action)
            if not handler:
                raise ValueError(f"No handler for action {job.action}")
            
            results = []
            for item_id in job.data_items:
                try:
                    result = handler(item_id)
                    results.append({'item_id': item_id, 'success': result})
                except Exception as e:
                    results.append({'item_id': item_id, 'success': False, 'error': str(e)})
            
            job.result = {
                'processed_items': len(results),
                'successful': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success']),
                'details': results
            }
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            logging.info(f"Completed retention job {job_id}: {job.result['successful']}/{job.result['processed_items']} successful")
            return True
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            logging.error(f"Retention job {job_id}