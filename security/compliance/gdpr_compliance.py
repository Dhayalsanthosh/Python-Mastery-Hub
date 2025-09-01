# File: security/compliance/gdpr_compliance.py
"""
GDPR (General Data Protection Regulation) Compliance Implementation
Provides tools and utilities for GDPR compliance including data rights management,
consent tracking, data processing logging, and privacy controls.
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid
from cryptography.fernet import Fernet
import base64


class DataCategory(Enum):
    """Categories of personal data under GDPR"""
    PERSONAL_IDENTIFIERS = "personal_identifiers"      # Name, address, ID numbers
    CONTACT_INFORMATION = "contact_information"        # Email, phone, social media
    BIOMETRIC_DATA = "biometric_data"                 # Fingerprints, facial recognition
    HEALTH_DATA = "health_data"                       # Medical records, health status
    FINANCIAL_DATA = "financial_data"                 # Bank details, payment info
    LOCATION_DATA = "location_data"                   # GPS, IP addresses
    BEHAVIORAL_DATA = "behavioral_data"               # Browsing history, preferences
    EMPLOYMENT_DATA = "employment_data"               # Job history, performance
    EDUCATIONAL_DATA = "educational_data"             # Academic records, qualifications
    SPECIAL_CATEGORY = "special_category"             # Race, religion, political opinions


class LegalBasis(Enum):
    """Legal basis for processing personal data under GDPR Article 6"""
    CONSENT = "consent"                               # Article 6(1)(a)
    CONTRACT = "contract"                             # Article 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"             # Article 6(1)(c)
    VITAL_INTERESTS = "vital_interests"               # Article 6(1)(d)
    PUBLIC_TASK = "public_task"                       # Article 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests"     # Article 6(1)(f)


class ConsentStatus(Enum):
    """Status of data subject consent"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"
    INVALID = "invalid"


class DataSubjectRight(Enum):
    """Rights of data subjects under GDPR"""
    ACCESS = "access"                                 # Article 15 - Right of access
    RECTIFICATION = "rectification"                   # Article 16 - Right to rectification
    ERASURE = "erasure"                              # Article 17 - Right to erasure
    RESTRICT_PROCESSING = "restrict_processing"       # Article 18 - Right to restrict processing
    DATA_PORTABILITY = "data_portability"            # Article 20 - Right to data portability
    OBJECT = "object"                                # Article 21 - Right to object
    AUTOMATED_DECISION = "automated_decision"         # Article 22 - Automated individual decision-making


class ProcessingActivity(Enum):
    """Types of data processing activities"""
    COLLECTION = "collection"
    RECORDING = "recording"
    ORGANIZATION = "organization"
    STRUCTURING = "structuring"
    STORAGE = "storage"
    ADAPTATION = "adaptation"
    ALTERATION = "alteration"
    RETRIEVAL = "retrieval"
    CONSULTATION = "consultation"
    USE = "use"
    DISCLOSURE = "disclosure"
    DISSEMINATION = "dissemination"
    ALIGNMENT = "alignment"
    COMBINATION = "combination"
    RESTRICTION = "restriction"
    ERASURE = "erasure"
    DESTRUCTION = "destruction"


@dataclass
class DataSubject:
    """Represents a data subject (individual whose data is processed)"""
    subject_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_child: bool = False  # Under 16 years old
    country: Optional[str] = None
    preferred_language: str = "en"
    
    def __post_init__(self):
        if not self.subject_id:
            self.subject_id = str(uuid.uuid4())


@dataclass
class ConsentRecord:
    """Records consent given by data subjects"""
    consent_id: str
    subject_id: str
    purpose: str
    legal_basis: LegalBasis
    status: ConsentStatus
    given_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    consent_method: str = "web_form"  # web_form, email, phone, paper
    consent_text: str = ""
    version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.consent_id:
            self.consent_id = str(uuid.uuid4())
    
    def is_valid(self) -> bool:
        """Check if consent is currently valid"""
        if self.status != ConsentStatus.GIVEN:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def withdraw(self, reason: str = "User request"):
        """Withdraw consent"""
        self.status = ConsentStatus.WITHDRAWN
        self.withdrawn_at = datetime.utcnow()
        self.evidence['withdrawal_reason'] = reason


@dataclass
class PersonalDataRecord:
    """Records personal data being processed"""
    record_id: str
    subject_id: str
    data_category: DataCategory
    data_fields: List[str]
    purpose: str
    legal_basis: LegalBasis
    controller: str
    processor: Optional[str] = None
    retention_period: Optional[timedelta] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    location: str = "EU"  # Data location
    third_countries: List[str] = field(default_factory=list)
    safeguards: List[str] = field(default_factory=list)
    is_encrypted: bool = True
    
    def __post_init__(self):
        if not self.record_id:
            self.record_id = str(uuid.uuid4())
        
        if self.retention_period and not self.expires_at:
            self.expires_at = self.created_at + self.retention_period
    
    def is_expired(self) -> bool:
        """Check if data retention period has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at


@dataclass
class ProcessingLog:
    """Logs data processing activities for audit trail"""
    log_id: str
    subject_id: str
    activity: ProcessingActivity
    purpose: str
    legal_basis: LegalBasis
    data_categories: List[DataCategory]
    processor: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    automated: bool = False
    
    def __post_init__(self):
        if not self.log_id:
            self.log_id = str(uuid.uuid4())


@dataclass
class DataSubjectRequest:
    """Represents a data subject rights request"""
    request_id: str
    subject_id: str
    right_type: DataSubjectRight
    status: str = "pending"  # pending, in_progress, completed, rejected
    request_date: datetime = field(default_factory=datetime.utcnow)
    completion_date: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)
    requester_verification: bool = False
    response_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


class DataProcessor(ABC):
    """Abstract interface for data processors"""
    
    @abstractmethod
    def get_personal_data(self, subject_id: str) -> Dict[str, Any]:
        """Retrieve all personal data for a subject"""
        pass
    
    @abstractmethod
    def update_personal_data(self, subject_id: str, updates: Dict[str, Any]) -> bool:
        """Update personal data for a subject"""
        pass
    
    @abstractmethod
    def delete_personal_data(self, subject_id: str, categories: List[DataCategory] = None) -> bool:
        """Delete personal data for a subject"""
        pass
    
    @abstractmethod
    def anonymize_personal_data(self, subject_id: str, categories: List[DataCategory] = None) -> bool:
        """Anonymize personal data for a subject"""
        pass
    
    @abstractmethod
    def export_personal_data(self, subject_id: str, format: str = "json") -> bytes:
        """Export personal data in portable format"""
        pass


class DatabaseDataProcessor(DataProcessor):
    """Database implementation of data processor"""
    
    def __init__(self, connection_string: str = None):
        # In a real implementation, this would connect to your database
        self.data_store: Dict[str, Dict[str, Any]] = {}
    
    def get_personal_data(self, subject_id: str) -> Dict[str, Any]:
        """Retrieve all personal data for a subject"""
        return self.data_store.get(subject_id, {})
    
    def update_personal_data(self, subject_id: str, updates: Dict[str, Any]) -> bool:
        """Update personal data for a subject"""
        try:
            if subject_id not in self.data_store:
                self.data_store[subject_id] = {}
            
            self.data_store[subject_id].update(updates)
            self.data_store[subject_id]['last_updated'] = datetime.utcnow().isoformat()
            return True
        except Exception as e:
            logging.error(f"Failed to update data for subject {subject_id}: {e}")
            return False
    
    def delete_personal_data(self, subject_id: str, categories: List[DataCategory] = None) -> bool:
        """Delete personal data for a subject"""
        try:
            if subject_id in self.data_store:
                if categories:
                    # Delete specific categories
                    for category in categories:
                        category_fields = self._get_fields_for_category(category)
                        for field in category_fields:
                            self.data_store[subject_id].pop(field, None)
                else:
                    # Delete all data
                    del self.data_store[subject_id]
            return True
        except Exception as e:
            logging.error(f"Failed to delete data for subject {subject_id}: {e}")
            return False
    
    def anonymize_personal_data(self, subject_id: str, categories: List[DataCategory] = None) -> bool:
        """Anonymize personal data for a subject"""
        try:
            if subject_id not in self.data_store:
                return True
            
            anonymized_id = hashlib.sha256(subject_id.encode()).hexdigest()[:16]
            
            if categories:
                # Anonymize specific categories
                for category in categories:
                    category_fields = self._get_fields_for_category(category)
                    for field in category_fields:
                        if field in self.data_store[subject_id]:
                            self.data_store[subject_id][field] = f"ANONYMIZED_{anonymized_id}"
            else:
                # Anonymize all personal identifiers
                personal_fields = ['name', 'email', 'phone', 'address', 'ssn']
                for field in personal_fields:
                    if field in self.data_store[subject_id]:
                        self.data_store[subject_id][field] = f"ANONYMIZED_{anonymized_id}"
            
            self.data_store[subject_id]['anonymized_at'] = datetime.utcnow().isoformat()
            return True
        except Exception as e:
            logging.error(f"Failed to anonymize data for subject {subject_id}: {e}")
            return False
    
    def export_personal_data(self, subject_id: str, format: str = "json") -> bytes:
        """Export personal data in portable format"""
        data = self.get_personal_data(subject_id)
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str).encode('utf-8')
        elif format.lower() == "csv":
            import csv
            import io
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data.keys())
                writer.writeheader()
                writer.writerow(data)
            return output.getvalue().encode('utf-8')
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _get_fields_for_category(self, category: DataCategory) -> List[str]:
        """Get database fields for a data category"""
        category_mapping = {
            DataCategory.PERSONAL_IDENTIFIERS: ['name', 'first_name', 'last_name', 'ssn', 'id_number'],
            DataCategory.CONTACT_INFORMATION: ['email', 'phone', 'address', 'city', 'postal_code'],
            DataCategory.FINANCIAL_DATA: ['credit_card', 'bank_account', 'payment_method'],
            DataCategory.LOCATION_DATA: ['ip_address', 'gps_coordinates', 'country', 'region'],
            DataCategory.BEHAVIORAL_DATA: ['preferences', 'browsing_history', 'search_history'],
            DataCategory.HEALTH_DATA: ['medical_records', 'health_status', 'medications'],
            DataCategory.EMPLOYMENT_DATA: ['job_title', 'company', 'salary', 'performance_review'],
            DataCategory.EDUCATIONAL_DATA: ['education_level', 'qualifications', 'certifications'],
            DataCategory.BIOMETRIC_DATA: ['fingerprint', 'face_id', 'voice_print'],
            DataCategory.SPECIAL_CATEGORY: ['race', 'religion', 'political_opinion', 'sexual_orientation']
        }
        return category_mapping.get(category, [])


class GDPRComplianceManager:
    """Main GDPR compliance manager"""
    
    def __init__(self, data_processor: DataProcessor):
        self.data_processor = data_processor
        self.subjects: Dict[str, DataSubject] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.personal_data_records: Dict[str, PersonalDataRecord] = {}
        self.processing_logs: List[ProcessingLog] = []
        self.subject_requests: Dict[str, DataSubjectRequest] = {}
        
        # Encryption for sensitive data
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
    
    def register_data_subject(self, subject: DataSubject) -> str:
        """Register a new data subject"""
        self.subjects[subject.subject_id] = subject
        self.logger.info(f"Registered data subject: {subject.subject_id}")
        return subject.subject_id
    
    def record_consent(self, consent: ConsentRecord) -> str:
        """Record consent from a data subject"""
        if consent.status == ConsentStatus.GIVEN:
            consent.given_at = datetime.utcnow()
        
        self.consent_records[consent.consent_id] = consent
        
        # Log the consent activity
        self.log_processing_activity(
            subject_id=consent.subject_id,
            activity=ProcessingActivity.RECORDING,
            purpose="Consent management",
            legal_basis=LegalBasis.CONSENT,
            data_categories=[],
            details={"consent_id": consent.consent_id, "purpose": consent.purpose}
        )
        
        self.logger.info(f"Recorded consent: {consent.consent_id} for subject: {consent.subject_id}")
        return consent.consent_id
    
    def withdraw_consent(self, consent_id: str, reason: str = "User request") -> bool:
        """Withdraw consent"""
        if consent_id not in self.consent_records:
            return False
        
        consent = self.consent_records[consent_id]
        consent.withdraw(reason)
        
        # Log the withdrawal
        self.log_processing_activity(
            subject_id=consent.subject_id,
            activity=ProcessingActivity.RESTRICTION,
            purpose="Consent withdrawal",
            legal_basis=LegalBasis.CONSENT,
            data_categories=[],
            details={"consent_id": consent_id, "reason": reason}
        )
        
        self.logger.info(f"Withdrawn consent: {consent_id}")
        return True
    
    def check_consent(self, subject_id: str, purpose: str) -> bool:
        """Check if valid consent exists for a purpose"""
        for consent in self.consent_records.values():
            if (consent.subject_id == subject_id and 
                consent.purpose == purpose and 
                consent.is_valid()):
                return True
        return False
    
    def record_personal_data(self, data_record: PersonalDataRecord) -> str:
        """Record personal data being processed"""
        self.personal_data_records[data_record.record_id] = data_record
        
        # Log the data collection
        self.log_processing_activity(
            subject_id=data_record.subject_id,
            activity=ProcessingActivity.COLLECTION,
            purpose=data_record.purpose,
            legal_basis=data_record.legal_basis,
            data_categories=[data_record.data_category],
            details={"record_id": data_record.record_id, "fields": data_record.data_fields}
        )
        
        self.logger.info(f"Recorded personal data: {data_record.record_id}")
        return data_record.record_id
    
    def log_processing_activity(self, subject_id: str, activity: ProcessingActivity, 
                              purpose: str, legal_basis: LegalBasis, 
                              data_categories: List[DataCategory], 
                              processor: str = "System", 
                              details: Dict[str, Any] = None) -> str:
        """Log a data processing activity"""
        log_entry = ProcessingLog(
            log_id=str(uuid.uuid4()),
            subject_id=subject_id,
            activity=activity,
            purpose=purpose,
            legal_basis=legal_basis,
            data_categories=data_categories,
            processor=processor,
            details=details or {}
        )
        
        self.processing_logs.append(log_entry)
        return log_entry.log_id
    
    def handle_subject_request(self, request: DataSubjectRequest) -> str:
        """Handle a data subject rights request"""
        self.subject_requests[request.request_id] = request
        
        # Process the request based on type
        if request.right_type == DataSubjectRight.ACCESS:
            self._handle_access_request(request)
        elif request.right_type == DataSubjectRight.RECTIFICATION:
            self._handle_rectification_request(request)
        elif request.right_type == DataSubjectRight.ERASURE:
            self._handle_erasure_request(request)
        elif request.right_type == DataSubjectRight.DATA_PORTABILITY:
            self._handle_portability_request(request)
        elif request.right_type == DataSubjectRight.RESTRICT_PROCESSING:
            self._handle_restriction_request(request)
        elif request.right_type == DataSubjectRight.OBJECT:
            self._handle_objection_request(request)
        
        self.logger.info(f"Handled subject request: {request.request_id} of type: {request.right_type.value}")
        return request.request_id
    
    def _handle_access_request(self, request: DataSubjectRequest):
        """Handle right of access request (Article 15)"""
        try:
            subject_id = request.subject_id
            
            # Gather all personal data
            personal_data = self.data_processor.get_personal_data(subject_id)
            
            # Get consent records
            subject_consents = [
                {
                    "purpose": consent.purpose,
                    "status": consent.status.value,
                    "given_at": consent.given_at.isoformat() if consent.given_at else None,
                    "expires_at": consent.expires_at.isoformat() if consent.expires_at else None
                }
                for consent in self.consent_records.values()
                if consent.subject_id == subject_id
            ]
            
            # Get data processing records
            data_records = [
                {
                    "category": record.data_category.value,
                    "purpose": record.purpose,
                    "legal_basis": record.legal_basis.value,
                    "retention_period": str(record.retention_period) if record.retention_period else None,
                    "created_at": record.created_at.isoformat()
                }
                for record in self.personal_data_records.values()
                if record.subject_id == subject_id
            ]
            
            # Get processing logs (last 12 months)
            twelve_months_ago = datetime.utcnow() - timedelta(days=365)
            recent_logs = [
                {
                    "activity": log.activity.value,
                    "purpose": log.purpose,
                    "timestamp": log.timestamp.isoformat(),
                    "processor": log.processor
                }
                for log in self.processing_logs
                if log.subject_id == subject_id and log.timestamp > twelve_months_ago
            ]
            
            request.response_data = {
                "personal_data": personal_data,
                "consents": subject_consents,
                "data_records": data_records,
                "processing_activities": recent_logs,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            request.status = "completed"
            request.completion_date = datetime.utcnow()
            
        except Exception as e:
            request.status = "error"
            self.logger.error(f"Failed to handle access request {request.request_id}: {e}")
    
    def _handle_rectification_request(self, request: DataSubjectRequest):
        """Handle right to rectification request (Article 16)"""
        try:
            updates = request.details.get('updates', {})
            success = self.data_processor.update_personal_data(request.subject_id, updates)
            
            if success:
                # Log the rectification
                self.log_processing_activity(
                    subject_id=request.subject_id,
                    activity=ProcessingActivity.ALTERATION,
                    purpose="Data rectification",
                    legal_basis=LegalBasis.CONSENT,
                    data_categories=[],
                    details={"request_id": request.request_id, "updates": list(updates.keys())}
                )
                
                request.status = "completed"
                request.completion_date = datetime.utcnow()
            else:
                request.status = "error"
                
        except Exception as e:
            request.status = "error"
            self.logger.error(f"Failed to handle rectification request {request.request_id}: {e}")
    
    def _handle_erasure_request(self, request: DataSubjectRequest):
        """Handle right to erasure request (Article 17)"""
        try:
            categories = request.details.get('categories')
            if categories:
                categories = [DataCategory(cat) for cat in categories]
            
            success = self.data_processor.delete_personal_data(request.subject_id, categories)
            
            if success:
                # Log the erasure
                self.log_processing_activity(
                    subject_id=request.subject_id,
                    activity=ProcessingActivity.ERASURE,
                    purpose="Data erasure (right to be forgotten)",
                    legal_basis=LegalBasis.CONSENT,
                    data_categories=categories or [],
                    details={"request_id": request.request_id}
                )
                
                request.status = "completed"
                request.completion_date = datetime.utcnow()
            else:
                request.status = "error"
                
        except Exception as e:
            request.status = "error"
            self.logger.error(f"Failed to handle erasure request {request.request_id}: {e}")
    
    def _handle_portability_request(self, request: DataSubjectRequest):
        """Handle right to data portability request (Article 20)"""
        try:
            export_format = request.details.get('format', 'json')
            exported_data = self.data_processor.export_personal_data(request.subject_id, export_format)
            
            # Encrypt the exported data
            encrypted_data = self.cipher_suite.encrypt(exported_data)
            encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
            
            request.response_data = {
                "exported_data": encoded_data,
                "format": export_format,
                "encryption_key": base64.b64encode(self.encryption_key).decode('utf-8'),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Log the export
            self.log_processing_activity(
                subject_id=request.subject_id,
                activity=ProcessingActivity.DISCLOSURE,
                purpose="Data portability",
                legal_basis=LegalBasis.CONSENT,
                data_categories=[],
                details={"request_id": request.request_id, "format": export_format}
            )
            
            request.status = "completed"
            request.completion_date = datetime.utcnow()
            
        except Exception as e:
            request.status = "error"
            self.logger.error(f"Failed to handle portability request {request.request_id}: {e}")
    
    def _handle_restriction_request(self, request: DataSubjectRequest):
        """Handle right to restrict processing request (Article 18)"""
        try:
            # In a real implementation, this would mark data for restricted processing
            # For now, we'll log the restriction
            self.log_processing_activity(
                subject_id=request.subject_id,
                activity=ProcessingActivity.RESTRICTION,
                purpose="Processing restriction",
                legal_basis=LegalBasis.CONSENT,
                data_categories=[],
                details={"request_id": request.request_id, "reason": request.details.get('reason')}
            )
            
            request.status = "completed"
            request.completion_date = datetime.utcnow()
            
        except Exception as e:
            request.status = "error"
            self.logger.error(f"Failed to handle restriction request {request.request_id}: {e}")
    
    def _handle_objection_request(self, request: DataSubjectRequest):
        """Handle right to object request (Article 21)"""
        try:
            # Stop processing based on legitimate interests
            processing_purposes = request.details.get('purposes', [])
            
            self.log_processing_activity(
                subject_id=request.subject_id,
                activity=ProcessingActivity.RESTRICTION,
                purpose="Processing objection",
                legal_basis=LegalBasis.CONSENT,
                data_categories=[],
                details={"request_id": request.request_id, "objected_purposes": processing_purposes}
            )
            
            request.status = "completed"
            request.completion_date = datetime.utcnow()
            
        except Exception as e:
            request.status = "error"
            self.logger.error(f"Failed to handle objection request {request.request_id}: {e}")
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        total_subjects = len(self.subjects)
        active_consents = sum(1 for consent in self.consent_records.values() if consent.is_valid())
        expired_data = sum(1 for record in self.personal_data_records.values() if record.is_expired())
        
        # Rights requests summary
        requests_by_type = {}
        for request in self.subject_requests.values():
            right_type = request.right_type.value
            if right_type not in requests_by_type:
                requests_by_type[right_type] = {"total": 0, "completed": 0, "pending": 0}
            
            requests_by_type[right_type]["total"] += 1
            if request.status == "completed":
                requests_by_type[right_type]["completed"] += 1
            elif request.status == "pending":
                requests_by_type[right_type]["pending"] += 1
        
        # Recent processing activities
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activities = [
            {
                "activity": log.activity.value,
                "purpose": log.purpose,
                "timestamp": log.timestamp.isoformat()
            }
            for log in self.processing_logs
            if log.timestamp > thirty_days_ago
        ]
        
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_data_subjects": total_subjects,
                "active_consents": active_consents,
                "total_consent_records": len(self.consent_records),
                "expired_data_records": expired_data,
                "total_data_records": len(self.personal_data_records),
                "total_processing_logs": len(self.processing_logs),
                "pending_requests": len([r for r in self.subject_requests.values() if r.status == "pending"])
            },
            "rights_requests": requests_by_type,
            "recent_processing_activities": recent_activities[:50],  # Last 50 activities
            "data_categories_processed": list(set(
                record.data_category.value for record in self.personal_data_records.values()
            )),
            "legal_bases_used": list(set(
                record.legal_basis.value for record in self.personal_data_records.values()
            ))
        }
    
    def cleanup_expired_data(self) -> int:
        """Clean up expired personal data records"""
        expired_count = 0
        
        for record in list(self.personal_data_records.values()):
            if record.is_expired():
                # Delete the actual data
                success = self.data_processor.delete_personal_data(
                    record.subject_id, 
                    [record.data_category]
                )
                
                if success:
                    # Log the automatic deletion
                    self.log_processing_activity(
                        subject_id=record.subject_id,
                        activity=ProcessingActivity.ERASURE,
                        purpose="Automatic retention period expiry",
                        legal_basis=record.legal_basis,
                        data_categories=[record.data_category],
                        details={"record_id": record.record_id, "automated": True}
                    )
                    
                    expired_count += 1
                    self.logger.info(f"Automatically deleted expired data record: {record.record_id}")
        
        return expired_count


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize GDPR compliance manager
    data_processor = DatabaseDataProcessor()
    gdpr_manager = GDPRComplianceManager(data_processor)
    
    # Create a data subject
    subject = DataSubject(
        subject_id="user_001",
        email="john.doe@example.com",
        name="John Doe",
        country="DE"
    )
    gdpr_manager.register_data_subject(subject)
    
    # Record consent
    consent = ConsentRecord(
        consent_id="consent_001",
        subject_id=subject.subject_id,
        purpose="Email marketing",
        legal_basis=LegalBasis.CONSENT,
        status=ConsentStatus.GIVEN,
        consent_text="I agree to receive marketing emails",
        ip_address="192.168.1.1"
    )
    gdpr_manager.record_consent(consent)
    
    # Record personal data processing
    data_record = PersonalDataRecord(
        record_id="record_001",
        subject_id=subject.subject_id,
        data_category=DataCategory.CONTACT_INFORMATION,
        data_fields=["email", "name"],
        purpose="Email marketing",
        legal_basis=LegalBasis.CONSENT,
        controller="Company Inc",
        retention_period=timedelta(days=365*2)  # 2 years
    )
    gdpr_manager.record_personal_data(data_record)
    
    # Add some test data to the processor
    data_processor.update_personal_data(subject.subject_id, {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+49123456789",
        "preferences": {"newsletter": True, "promotions": False}
    })
    
    # Handle a data access request
    access_request = DataSubjectRequest(
        request_id="req_001",
        subject_id=subject.subject_id,
        right_type=DataSubjectRight.ACCESS,
        requester_verification=True
    )
    gdpr_manager.handle_subject_request(access_request)
    
    print("GDPR Compliance Test Results:")
    print("=" * 50)
    
    # Check consent
    has_consent = gdpr_manager.check_consent(subject.subject_id, "Email marketing")
    print(f"Has valid consent for email marketing: {has_consent}")
    
    # Generate compliance report
    report = gdpr_manager.generate_compliance_report()
    print(f"\nCompliance Report Summary:")
    print(f"Total data subjects: {report['summary']['total_data_subjects']}")
    print(f"Active consents: {report['summary']['active_consents']}")
    print(f"Total processing logs: {report['summary']['total_processing_logs']}")
    print(f"Data categories processed: {', '.join(report['data_categories_processed'])}")
    
    # Test data export
    if access_request.status == "completed" and access_request.response_data:
        print(f"\nAccess request completed successfully")
        print(f"Personal data records found: {len(access_request.response_data.get('personal_data', {}))}")
        print(f"Consent records found: {len(access_request.response_data.get('consents', []))}")
    
    print(f"\nGDPR compliance system initialized with {len(gdpr_manager.subjects)} subjects")