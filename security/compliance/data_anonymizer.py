# File: security/compliance/data_anonymizer.py
"""
Data Anonymizer Implementation
Provides comprehensive data anonymization, pseudonymization, and privacy-preserving techniques.
Supports multiple anonymization methods including k-anonymity, l-diversity, and differential privacy.
"""

import re
import json
import hashlib
import secrets
import string
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import random
import math
import uuid
from collections import defaultdict, Counter
import numpy as np
from faker import Faker


class AnonymizationType(Enum):
    """Types of anonymization techniques"""
    SUPPRESSION = "suppression"                 # Remove data entirely
    GENERALIZATION = "generalization"           # Replace with broader categories
    PERTURBATION = "perturbation"              # Add noise to numerical data
    PSEUDONYMIZATION = "pseudonymization"       # Replace with consistent fake values
    RANDOMIZATION = "randomization"            # Replace with random values
    MASKING = "masking"                        # Partially hide data
    ENCRYPTION = "encryption"                  # Encrypt sensitive data
    TOKENIZATION = "tokenization"              # Replace with non-sensitive tokens
    SYNTHETIC = "synthetic"                    # Generate synthetic data
    K_ANONYMITY = "k_anonymity"                # Ensure k-anonymity
    L_DIVERSITY = "l_diversity"                # Ensure l-diversity
    DIFFERENTIAL_PRIVACY = "differential_privacy" # Add differential privacy noise


class DataType(Enum):
    """Types of data for anonymization"""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    DATE_OF_BIRTH = "date_of_birth"
    IP_ADDRESS = "ip_address"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    CUSTOM = "custom"


class PrivacyLevel(Enum):
    """Privacy protection levels"""
    LOW = "low"               # Basic anonymization
    MEDIUM = "medium"         # Standard anonymization
    HIGH = "high"             # Strong anonymization
    MAXIMUM = "maximum"       # Maximum privacy protection


@dataclass
class AnonymizationRule:
    """Defines how to anonymize a specific field"""
    field_name: str
    data_type: DataType
    anonymization_type: AnonymizationType
    privacy_level: PrivacyLevel
    parameters: Dict[str, Any] = field(default_factory=dict)
    preserve_format: bool = True
    preserve_length: bool = False
    custom_function: Optional[Callable] = None
    
    def validate(self) -> List[str]:
        """Validate the anonymization rule"""
        errors = []
        
        # Check if anonymization type is compatible with data type
        incompatible_combinations = {
            (DataType.NUMERIC, AnonymizationType.MASKING),
            (DataType.BOOLEAN, AnonymizationType.GENERALIZATION),
            (DataType.DATE, AnonymizationType.TOKENIZATION)
        }
        
        if (self.data_type, self.anonymization_type) in incompatible_combinations:
            errors.append(f"Incompatible combination: {self.data_type.value} with {self.anonymization_type.value}")
        
        # Validate parameters based on anonymization type
        if self.anonymization_type == AnonymizationType.K_ANONYMITY:
            if 'k_value' not in self.parameters or self.parameters['k_value'] < 2:
                errors.append("K-anonymity requires k_value parameter >= 2")
        
        if self.anonymization_type == AnonymizationType.PERTURBATION:
            if 'noise_level' not in self.parameters:
                errors.append("Perturbation requires noise_level parameter")
        
        return errors


@dataclass
class AnonymizationContext:
    """Context for anonymization process"""
    dataset_id: str
    total_records: int
    field_mappings: Dict[str, str] = field(default_factory=dict)  # original -> anonymized mappings
    anonymization_date: datetime = field(default_factory=datetime.utcnow)
    privacy_budget: float = 1.0  # For differential privacy
    k_value: int = 3  # For k-anonymity
    l_value: int = 2  # For l-diversity
    seed: Optional[int] = None
    
    def __post_init__(self):
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)


class Anonymizer(ABC):
    """Abstract base class for anonymization techniques"""
    
    @abstractmethod
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        """Anonymize a single value"""
        pass
    
    @abstractmethod
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        """Check if this anonymizer can handle the given data type and anonymization type"""
        pass


class SuppressionAnonymizer(Anonymizer):
    """Removes or masks data entirely"""
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        if value is None:
            return None
        
        suppression_char = rule.parameters.get('suppression_char', '*')
        
        if rule.preserve_length and isinstance(value, str):
            return suppression_char * len(value)
        elif rule.preserve_format and isinstance(value, str):
            # Preserve format structure (e.g., phone numbers, SSNs)
            result = ""
            for char in value:
                if char.isalnum():
                    result += suppression_char
                else:
                    result += char
            return result
        else:
            return rule.parameters.get('replacement_value', '[REDACTED]')
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return anonymization_type == AnonymizationType.SUPPRESSION


class GeneralizationAnonymizer(Anonymizer):
    """Generalizes data to broader categories"""
    
    def __init__(self):
        self.age_ranges = {
            (0, 18): "0-17",
            (18, 25): "18-24",
            (25, 35): "25-34",
            (35, 45): "35-44",
            (45, 55): "45-54",
            (55, 65): "55-64",
            (65, 150): "65+"
        }
        
        self.income_ranges = {
            (0, 25000): "Low",
            (25000, 50000): "Lower-Middle",
            (50000, 75000): "Middle",
            (75000, 100000): "Upper-Middle",
            (100000, float('inf')): "High"
        }
        
        self.location_hierarchy = {
            'city': 'state',
            'state': 'country',
            'country': 'continent',
            'zipcode': 'state'
        }
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        if value is None:
            return None
        
        generalization_level = rule.parameters.get('level', 1)
        
        if rule.data_type == DataType.NUMERIC:
            return self._generalize_numeric(value, rule)
        elif rule.data_type == DataType.DATE:
            return self._generalize_date(value, generalization_level)
        elif rule.data_type == DataType.ADDRESS:
            return self._generalize_location(value, generalization_level)
        elif rule.data_type == DataType.CATEGORICAL:
            return self._generalize_categorical(value, rule)
        else:
            return str(value)[:max(1, len(str(value)) // (generalization_level + 1))]
    
    def _generalize_numeric(self, value: Union[int, float], rule: AnonymizationRule) -> str:
        """Generalize numeric values into ranges"""
        if 'ranges' in rule.parameters:
            ranges = rule.parameters['ranges']
            for (min_val, max_val), label in ranges.items():
                if min_val <= value < max_val:
                    return label
        
        # Default age generalization
        if 'age' in rule.field_name.lower():
            for (min_age, max_age), range_label in self.age_ranges.items():
                if min_age <= value < max_age:
                    return range_label
        
        # Default income generalization
        if 'income' in rule.field_name.lower() or 'salary' in rule.field_name.lower():
            for (min_income, max_income), range_label in self.income_ranges.items():
                if min_income <= value < max_income:
                    return range_label
        
        # Generic range generalization
        range_size = rule.parameters.get('range_size', 10)
        range_start = (int(value) // range_size) * range_size
        return f"{range_start}-{range_start + range_size - 1}"
    
    def _generalize_date(self, value: Union[str, datetime], level: int) -> str:
        """Generalize dates (year only, year-month, etc.)"""
        if isinstance(value, str):
            try:
                date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        else:
            date_obj = value
        
        if level == 1:
            return date_obj.strftime("%Y-%m")  # Year-month
        elif level == 2:
            return date_obj.strftime("%Y")     # Year only
        elif level >= 3:
            return f"{(date_obj.year // 10) * 10}s"  # Decade
        else:
            return date_obj.strftime("%Y-%m-%d")
    
    def _generalize_location(self, value: str, level: int) -> str:
        """Generalize location data"""
        # This is a simplified implementation
        # In practice, you'd use a geographic database
        parts = value.split(',')
        if level >= len(parts):
            return "Unknown"
        return ','.join(parts[level:]).strip()
    
    def _generalize_categorical(self, value: str, rule: AnonymizationRule) -> str:
        """Generalize categorical data using mapping"""
        mapping = rule.parameters.get('category_mapping', {})
        return mapping.get(value, "Other")
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return anonymization_type == AnonymizationType.GENERALIZATION


class PerturbationAnonymizer(Anonymizer):
    """Adds noise to numerical data"""
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        if value is None or not isinstance(value, (int, float)):
            return value
        
        noise_type = rule.parameters.get('noise_type', 'gaussian')
        noise_level = rule.parameters.get('noise_level', 0.1)
        
        if noise_type == 'gaussian':
            noise = np.random.normal(0, abs(value) * noise_level)
        elif noise_type == 'laplace':
            # For differential privacy
            sensitivity = rule.parameters.get('sensitivity', 1.0)
            epsilon = rule.parameters.get('epsilon', 1.0)
            scale = sensitivity / epsilon
            noise = np.random.laplace(0, scale)
        elif noise_type == 'uniform':
            range_val = abs(value) * noise_level
            noise = np.random.uniform(-range_val, range_val)
        else:
            noise = 0
        
        result = value + noise
        
        # Ensure non-negative for certain fields
        if rule.parameters.get('non_negative', False) and result < 0:
            result = abs(result)
        
        # Round to appropriate precision
        if isinstance(value, int):
            return int(round(result))
        else:
            precision = rule.parameters.get('precision', 2)
            return round(result, precision)
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return (data_type == DataType.NUMERIC and 
                anonymization_type in [AnonymizationType.PERTURBATION, AnonymizationType.DIFFERENTIAL_PRIVACY])


class PseudonymizationAnonymizer(Anonymizer):
    """Replaces data with consistent fake values"""
    
    def __init__(self):
        self.faker = Faker()
        self.mapping_cache: Dict[str, Dict[str, str]] = defaultdict(dict)
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        if value is None:
            return None
        
        # Use consistent mapping for the same value
        cache_key = f"{context.dataset_id}_{rule.field_name}"
        str_value = str(value)
        
        if str_value in self.mapping_cache[cache_key]:
            return self.mapping_cache[cache_key][str_value]
        
        # Generate pseudonym based on data type
        if rule.data_type == DataType.NAME:
            pseudonym = self.faker.name()
        elif rule.data_type == DataType.EMAIL:
            pseudonym = self.faker.email()
        elif rule.data_type == DataType.PHONE:
            pseudonym = self.faker.phone_number()
        elif rule.data_type == DataType.ADDRESS:
            pseudonym = self.faker.address()
        elif rule.data_type == DataType.SSN:
            pseudonym = self.faker.ssn()
        elif rule.data_type == DataType.CREDIT_CARD:
            pseudonym = self.faker.credit_card_number()
        elif rule.data_type == DataType.DATE_OF_BIRTH:
            pseudonym = self.faker.date_of_birth().isoformat()
        elif rule.data_type == DataType.IP_ADDRESS:
            pseudonym = self.faker.ipv4()
        else:
            # Use deterministic pseudonymization
            pseudonym = self._generate_deterministic_pseudonym(str_value, rule)
        
        # Cache the mapping
        self.mapping_cache[cache_key][str_value] = pseudonym
        context.field_mappings[f"{rule.field_name}_{str_value}"] = pseudonym
        
        return pseudonym
    
    def _generate_deterministic_pseudonym(self, value: str, rule: AnonymizationRule) -> str:
        """Generate deterministic pseudonym using hash"""
        hash_input = f"{rule.field_name}_{value}_{rule.parameters.get('salt', 'default_salt')}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()
        
        if rule.preserve_format:
            # Preserve original format structure
            result = ""
            hash_index = 0
            for char in value:
                if char.isalpha():
                    result += hash_value[hash_index % len(hash_value)]
                    hash_index += 1
                elif char.isdigit():
                    result += str(int(hash_value[hash_index % len(hash_value)], 16) % 10)
                    hash_index += 1
                else:
                    result += char
            return result
        else:
            if rule.preserve_length:
                return hash_value[:len(value)]
            else:
                return hash_value[:8]  # Default length
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return anonymization_type == AnonymizationType.PSEUDONYMIZATION


class MaskingAnonymizer(Anonymizer):
    """Partially hides data while preserving some information"""
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        if value is None:
            return None
        
        str_value = str(value)
        mask_char = rule.parameters.get('mask_char', '*')
        mask_ratio = rule.parameters.get('mask_ratio', 0.5)
        
        if rule.data_type == DataType.EMAIL:
            return self._mask_email(str_value, mask_char)
        elif rule.data_type == DataType.PHONE:
            return self._mask_phone(str_value, mask_char)
        elif rule.data_type == DataType.CREDIT_CARD:
            return self._mask_credit_card(str_value, mask_char)
        elif rule.data_type == DataType.SSN:
            return self._mask_ssn(str_value, mask_char)
        else:
            return self._mask_generic(str_value, mask_char, mask_ratio)
    
    def _mask_email(self, email: str, mask_char: str) -> str:
        """Mask email address"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = mask_char * len(local)
        else:
            masked_local = local[0] + mask_char * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    def _mask_phone(self, phone: str, mask_char: str) -> str:
        """Mask phone number"""
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 4:
            return mask_char * len(phone)
        
        # Keep last 4 digits
        masked_digits = mask_char * (len(digits_only) - 4) + digits_only[-4:]
        
        # Reconstruct with original formatting
        result = ""
        digit_index = 0
        for char in phone:
            if char.isdigit():
                result += masked_digits[digit_index]
                digit_index += 1
            else:
                result += char
        
        return result
    
    def _mask_credit_card(self, card: str, mask_char: str) -> str:
        """Mask credit card number"""
        digits_only = re.sub(r'\D', '', card)
        if len(digits_only) < 4:
            return mask_char * len(card)
        
        # Keep first 4 and last 4 digits
        if len(digits_only) <= 8:
            masked_digits = digits_only[:4] + mask_char * (len(digits_only) - 4)
        else:
            masked_digits = digits_only[:4] + mask_char * (len(digits_only) - 8) + digits_only[-4:]
        
        # Reconstruct with original formatting
        result = ""
        digit_index = 0
        for char in card:
            if char.isdigit():
                result += masked_digits[digit_index]
                digit_index += 1
            else:
                result += char
        
        return result
    
    def _mask_ssn(self, ssn: str, mask_char: str) -> str:
        """Mask SSN"""
        digits_only = re.sub(r'\D', '', ssn)
        if len(digits_only) < 4:
            return mask_char * len(ssn)
        
        # Keep last 4 digits
        masked_digits = mask_char * (len(digits_only) - 4) + digits_only[-4:]
        
        # Reconstruct with original formatting
        result = ""
        digit_index = 0
        for char in ssn:
            if char.isdigit():
                result += masked_digits[digit_index]
                digit_index += 1
            else:
                result += char
        
        return result
    
    def _mask_generic(self, value: str, mask_char: str, mask_ratio: float) -> str:
        """Generic masking"""
        if len(value) <= 2:
            return mask_char * len(value)
        
        chars_to_mask = int(len(value) * mask_ratio)
        start_keep = (len(value) - chars_to_mask) // 2
        end_keep = len(value) - chars_to_mask - start_keep
        
        return value[:start_keep] + mask_char * chars_to_mask + value[-end_keep:] if end_keep > 0 else value[:start_keep] + mask_char * chars_to_mask
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return anonymization_type == AnonymizationType.MASKING


class TokenizationAnonymizer(Anonymizer):
    """Replaces sensitive data with non-sensitive tokens"""
    
    def __init__(self):
        self.token_mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        if value is None:
            return None
        
        str_value = str(value)
        
        # Check if already tokenized
        if str_value in self.token_mapping:
            return self.token_mapping[str_value]
        
        # Generate token
        token_format = rule.parameters.get('token_format', 'alphanumeric')
        token_length = rule.parameters.get('token_length', 16)
        
        if token_format == 'alphanumeric':
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(token_length))
        elif token_format == 'numeric':
            token = ''.join(secrets.choice(string.digits) for _ in range(token_length))
        elif token_format == 'uuid':
            token = str(uuid.uuid4())
        else:
            token = secrets.token_urlsafe(token_length)
        
        # Store mapping
        self.token_mapping[str_value] = token
        self.reverse_mapping[token] = str_value
        
        return token
    
    def detokenize(self, token: str) -> Optional[str]:
        """Reverse the tokenization process"""
        return self.reverse_mapping.get(token)
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return anonymization_type == AnonymizationType.TOKENIZATION


class KAnonymityAnonymizer(Anonymizer):
    """Ensures k-anonymity through generalization and suppression"""
    
    def __init__(self):
        self.equivalence_classes: Dict[str, List[Dict]] = {}
    
    def anonymize(self, value: Any, context: AnonymizationContext, rule: AnonymizationRule) -> Any:
        # K-anonymity is typically applied to entire datasets, not individual values
        # This is a simplified implementation for demonstration
        return value
    
    def anonymize_dataset(self, dataset: List[Dict], quasi_identifiers: List[str], k_value: int) -> List[Dict]:
        """Apply k-anonymity to entire dataset"""
        # Group records by quasi-identifier combinations
        groups = defaultdict(list)
        
        for record in dataset:
            key = tuple(record.get(qi, '') for qi in quasi_identifiers)
            groups[key].append(record)
        
        anonymized_dataset = []
        
        for group_key, records in groups.items():
            if len(records) < k_value:
                # Need to generalize or suppress
                anonymized_records = self._generalize_group(records, quasi_identifiers, k_value)
            else:
                anonymized_records = records
            
            anonymized_dataset.extend(anonymized_records)
        
        return anonymized_dataset
    
    def _generalize_group(self, records: List[Dict], quasi_identifiers: List[str], k_value: int) -> List[Dict]:
        """Generalize records to meet k-anonymity"""
        # Simple generalization strategy
        for qi in quasi_identifiers:
            # Get all values for this quasi-identifier
            values = [record.get(qi) for record in records if record.get(qi) is not None]
            
            if not values:
                continue
            
            # Apply generalization based on data type
            if all(isinstance(v, (int, float)) for v in values):
                # Numeric generalization - use ranges
                min_val, max_val = min(values), max(values)
                generalized_value = f"{min_val}-{max_val}"
            else:
                # Categorical generalization - use most common category or "Mixed"
                counter = Counter(values)
                if len(counter) == 1:
                    generalized_value = list(counter.keys())[0]
                else:
                    generalized_value = "Mixed"
            
            # Apply generalization to all records in group
            for record in records:
                record[qi] = generalized_value
        
        return records
    
    def can_handle(self, data_type: DataType, anonymization_type: AnonymizationType) -> bool:
        return anonymization_type == AnonymizationType.K_ANONYMITY


class DataAnonymizer:
    """Main data anonymization engine"""
    
    def __init__(self):
        self.anonymizers: List[Anonymizer] = [
            SuppressionAnonymizer(),
            GeneralizationAnonymizer(),
            PerturbationAnonymizer(),
            PseudonymizationAnonymizer(),
            MaskingAnonymizer(),
            TokenizationAnonymizer(),
            KAnonymityAnonymizer()
        ]
        
        self.rules: Dict[str, AnonymizationRule] = {}
        self.audit_trail: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: AnonymizationRule):
        """Add an anonymization rule"""
        errors = rule.validate()
        if errors:
            raise ValueError(f"Invalid rule: {', '.join(errors)}")
        
        self.rules[rule.field_name] = rule
        logging.info(f"Added anonymization rule for field: {rule.field_name}")
    
    def remove_rule(self, field_name: str):
        """Remove an anonymization rule"""
        if field_name in self.rules:
            del self.rules[field_name]
            logging.info(f"Removed anonymization rule for field: {field_name}")
    
    def anonymize_record(self, record: Dict[str, Any], context: AnonymizationContext) -> Dict[str, Any]:
        """Anonymize a single record"""
        anonymized_record = record.copy()
        
        for field_name, value in record.items():
            if field_name in self.rules:
                rule = self.rules[field_name]
                anonymizer = self._get_anonymizer(rule.data_type, rule.anonymization_type)
                
                if anonymizer:
                    try:
                        if rule.custom_function:
                            anonymized_value = rule.custom_function(value, context, rule)
                        else:
                            anonymized_value = anonymizer.anonymize(value, context, rule)
                        
                        anonymized_record[field_name] = anonymized_value
                        
                        # Log the anonymization
                        self.audit_trail.append({
                            'timestamp': datetime.utcnow().isoformat(),
                            'field': field_name,
                            'anonymization_type': rule.anonymization_type.value,
                            'original_type': type(value).__name__,
                            'anonymized_type': type(anonymized_value).__name__,
                            'context_id': context.dataset_id
                        })
                        
                    except Exception as e:
                        logging.error(f"Failed to anonymize field {field_name}: {e}")
                        # Fallback to suppression
                        anonymized_record[field_name] = "[ERROR]"
        
        return anonymized_record
    
    def anonymize_dataset(self, dataset: List[Dict[str, Any]], dataset_id: str = None) -> Tuple[List[Dict[str, Any]], AnonymizationContext]:
        """Anonymize an entire dataset"""
        if not dataset_id:
            dataset_id = f"dataset_{uuid.uuid4().hex[:8]}"
        
        context = AnonymizationContext(
            dataset_id=dataset_id,
            total_records=len(dataset)
        )
        
        anonymized_dataset = []
        
        # Check for k-anonymity rules
        k_anonymity_rules = [rule for rule in self.rules.values() if rule.anonymization_type == AnonymizationType.K_ANONYMITY]
        
        if k_anonymity_rules:
            # Apply k-anonymity at dataset level
            quasi_identifiers = [rule.field_name for rule in k_anonymity_rules]
            k_value = context.k_value
            
            k_anonymizer = KAnonymityAnonymizer()
            dataset = k_anonymizer.anonymize_dataset(dataset, quasi_identifiers, k_value)
        
        # Apply field-level anonymization
        for record in dataset:
            anonymized_record = self.anonymize_record(record, context)
            anonymized_dataset.append(anonymized_record)
        
        logging.info(f"Anonymized dataset {dataset_id} with {len(anonymized_dataset)} records")
        return anonymized_dataset, context
    
    def _get_anonymizer(self, data_type: DataType, anonymization_type: AnonymizationType) -> Optional[Anonymizer]:
        """Get appropriate anonymizer for data type and anonymization type"""
        for anonymizer in self.anonymizers:
            if anonymizer.can_handle(data_type, anonymization_type):
                return anonymizer
        return None
    
    def assess_privacy_risk(self, dataset: List[Dict[str, Any]], quasi_identifiers: List[str]) -> Dict[str, Any]:
        """Assess privacy risk of a dataset"""
        if not dataset:
            return {"risk_level": "unknown", "details": "Empty dataset"}
        
        # Calculate k-anonymity
        groups = defaultdict(list)
        for record in dataset:
            key = tuple(record.get(qi, '') for qi in quasi_identifiers)
            groups[key].append(record)
        
        group_sizes = [len(group) for group in groups.values()]
        min_group_size = min(group_sizes)
        avg_group_size = sum(group_sizes) / len(group_sizes)
        
        # Calculate l-diversity for sensitive attributes
        sensitive_attributes = [field for field, rule in self.rules.items() 
                             if rule.data_type in [DataType.SSN, DataType.CREDIT_CARD]]
        
        l_diversity_scores = {}
        for attr in sensitive_attributes:
            attr_diversity = []
            for group in groups.values():
                unique_values = len(set(record.get(attr) for record in group if record.get(attr)))
                attr_diversity.append(unique_values)
            
            if attr_diversity:
                l_diversity_scores[attr] = min(attr_diversity)
        
        # Determine risk level
        if min_group_size >= 5 and all(score >= 2 for score in l_diversity_scores.values()):
            risk_level = "low"
        elif min_group_size >= 3:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "k_anonymity": min_group_size,
            "average_group_size": round(avg_group_size, 2),
            "l_diversity": l_diversity_scores,
            "total_groups": len(groups),
            "total_records": len(dataset),
            "unique_combinations": len(groups)
        }
    
    def export_anonymization_report(self, context: AnonymizationContext) -> Dict[str, Any]:
        """Generate anonymization report"""
        rule_summary = {}
        for field_name, rule in self.rules.items():
            rule_summary[field_name] = {
                "data_type": rule.data_type.value,
                "anonymization_type": rule.anonymization_type.value,
                "privacy_level": rule.privacy_level.value,
                "preserve_format": rule.preserve_format,
                "preserve_length": rule.preserve_length
            }
        
        return {
            "anonymization_metadata": {
                "dataset_id": context.dataset_id,
                "total_records": context.total_records,
                "anonymization_date": context.anonymization_date.isoformat(),
                "privacy_budget_used": context.privacy_budget,
                "k_value": context.k_value,
                "l_value": context.l_value
            },
            "rules_applied": rule_summary,
            "field_mappings_count": len(context.field_mappings),
            "audit_trail_entries": len(self.audit_trail),
            "anonymization_summary": {
                "suppressed_fields": len([r for r in self.rules.values() if r.anonymization_type == AnonymizationType.SUPPRESSION]),
                "generalized_fields": len([r for r in self.rules.values() if r.anonymization_type == AnonymizationType.GENERALIZATION]),
                "pseudonymized_fields": len([r for r in self.rules.values() if r.anonymization_type == AnonymizationType.PSEUDONYMIZATION]),
                "masked_fields": len([r for r in self.rules.values() if r.anonymization_type == AnonymizationType.MASKING])
            }
        }
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get anonymization audit trail"""
        return self.audit_trail.copy()


# Utility functions for common anonymization scenarios

def create_gdpr_anonymization_rules() -> List[AnonymizationRule]:
    """Create GDPR-compliant anonymization rules"""
    return [
        AnonymizationRule("name", DataType.NAME, AnonymizationType.PSEUDONYMIZATION, PrivacyLevel.HIGH),
        AnonymizationRule("email", DataType.EMAIL, AnonymizationType.MASKING, PrivacyLevel.MEDIUM),
        AnonymizationRule("phone", DataType.PHONE, AnonymizationType.MASKING, PrivacyLevel.MEDIUM),
        AnonymizationRule("address", DataType.ADDRESS, AnonymizationType.GENERALIZATION, PrivacyLevel.MEDIUM, {"level": 2}),
        AnonymizationRule("ssn", DataType.SSN, AnonymizationType.SUPPRESSION, PrivacyLevel.MAXIMUM),
        AnonymizationRule("date_of_birth", DataType.DATE_OF_BIRTH, AnonymizationType.GENERALIZATION, PrivacyLevel.HIGH, {"level": 1}),
        AnonymizationRule("ip_address", DataType.IP_ADDRESS, AnonymizationType.GENERALIZATION, PrivacyLevel.MEDIUM),
        AnonymizationRule("credit_card", DataType.CREDIT_CARD, AnonymizationType.TOKENIZATION, PrivacyLevel.MAXIMUM)
    ]

def create_hipaa_anonymization_rules() -> List[AnonymizationRule]:
    """Create HIPAA-compliant anonymization rules"""
    return [
        AnonymizationRule("patient_name", DataType.NAME, AnonymizationType.SUPPRESSION, PrivacyLevel.MAXIMUM),
        AnonymizationRule("ssn", DataType.SSN, AnonymizationType.SUPPRESSION, PrivacyLevel.MAXIMUM),
        AnonymizationRule("medical_record_number", DataType.CUSTOM, AnonymizationType.TOKENIZATION, PrivacyLevel.MAXIMUM),
        AnonymizationRule("date_of_birth", DataType.DATE_OF_BIRTH, AnonymizationType.GENERALIZATION, PrivacyLevel.HIGH, {"level": 2}),
        AnonymizationRule("admission_date", DataType.DATE, AnonymizationType.GENERALIZATION, PrivacyLevel.MEDIUM, {"level": 1}),
        AnonymizationRule("zip_code", DataType.CATEGORICAL, AnonymizationType.GENERALIZATION, PrivacyLevel.MEDIUM),
        AnonymizationRule("phone", DataType.PHONE, AnonymizationType.SUPPRESSION, PrivacyLevel.HIGH),
        AnonymizationRule("email", DataType.EMAIL, AnonymizationType.SUPPRESSION, PrivacyLevel.HIGH)
    ]


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize data anonymizer
    anonymizer = DataAnonymizer()
    
    # Add anonymization rules
    rules = [
        AnonymizationRule("name", DataType.NAME, AnonymizationType.PSEUDONYMIZATION, PrivacyLevel.HIGH),
        AnonymizationRule("email", DataType.EMAIL, AnonymizationType.MASKING, PrivacyLevel.MEDIUM),
        AnonymizationRule("phone", DataType.PHONE, AnonymizationType.MASKING, PrivacyLevel.MEDIUM),
        AnonymizationRule("ssn", DataType.SSN, AnonymizationType.SUPPRESSION, PrivacyLevel.MAXIMUM),
        AnonymizationRule("age", DataType.NUMERIC, AnonymizationType.GENERALIZATION, PrivacyLevel.LOW),
        AnonymizationRule("salary", DataType.NUMERIC, AnonymizationType.PERTURBATION, PrivacyLevel.MEDIUM, {"noise_level": 0.1}),
        AnonymizationRule("credit_card", DataType.CREDIT_CARD, AnonymizationType.TOKENIZATION, PrivacyLevel.MAXIMUM)
    ]
    
    for rule in rules:
        anonymizer.add_rule(rule)
    
    # Test dataset
    test_dataset = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "ssn": "123-45-6789",
            "age": 35,
            "salary": 75000,
            "credit_card": "4532-1234-5678-9012"
        },
        {
            "name": "Jane Smith",
            "email": "jane.smith@example.com", 
            "phone": "(555) 987-6543",
            "ssn": "987-65-4321",
            "age": 28,
            "salary": 68000,
            "credit_card": "5555-4444-3333-2222"
        },
        {
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "phone": "(555) 555-5555",
            "ssn": "555-55-5555",
            "age": 42,
            "salary": 85000,
            "credit_card": "4111-1111-1111-1111"
        }
    ]
    
    print("Original Dataset:")
    print("=" * 50)
    for i, record in enumerate(test_dataset, 1):
        print(f"Record {i}: {record}")
    
    # Anonymize the dataset
    print("\nAnonymizing dataset...")
    anonymized_dataset, context = anonymizer.anonymize_dataset(test_dataset, "test_dataset_001")
    
    print("\nAnonymized Dataset:")
    print("=" * 50)
    for i, record in enumerate(anonymized_dataset, 1):
        print(f"Record {i}: {record}")
    
    # Assess privacy risk
    print("\nPrivacy Risk Assessment:")
    print("=" * 30)
    quasi_identifiers = ["age", "salary"]  # Simplified QI list
    risk_assessment = anonymizer.assess_privacy_risk(anonymized_dataset, quasi_identifiers)
    print(f"Risk Level: {risk_assessment['risk_level']}")
    print(f"K-Anonymity: {risk_assessment['k_anonymity']}")
    print(f"Average Group Size: {risk_assessment['average_group_size']}")
    print(f"Total Groups: {risk_assessment['total_groups']}")
    
    # Generate anonymization report
    print("\nAnonymization Report:")
    print("=" * 30)
    report = anonymizer.export_anonymization_report(context)
    print(f"Dataset ID: {report['anonymization_metadata']['dataset_id']}")
    print(f"Total Records: {report['anonymization_metadata']['total_records']}")
    print(f"Rules Applied: {len(report['rules_applied'])}")
    print(f"Audit Trail Entries: {report['audit_trail_entries']}")
    
    print("\nAnonymization Summary:")
    summary = report['anonymization_summary']
    print(f"- Suppressed fields: {summary['suppressed_fields']}")
    print(f"- Generalized fields: {summary['generalized_fields']}")
    print(f"- Pseudonymized fields: {summary['pseudonymized_fields']}")
    print(f"- Masked fields: {summary['masked_fields']}")
    
    print("\nData anonymization test completed successfully!")