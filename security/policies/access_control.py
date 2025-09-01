# File: security/policies/access_control.py
"""
Access Control Policy Implementation
Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) system
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import secrets


class Action(Enum):
    """Standard actions for access control"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    APPROVE = "approve"
    DENY = "deny"


class ResourceType(Enum):
    """Standard resource types"""
    USER = "user"
    DOCUMENT = "document"
    DATABASE = "database"
    API = "api"
    FILE = "file"
    SYSTEM = "system"
    REPORT = "report"
    CONFIGURATION = "configuration"


class AccessDecision(Enum):
    """Access control decisions"""
    PERMIT = "permit"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"
    INDETERMINATE = "indeterminate"


@dataclass
class Permission:
    """Represents a permission with action and resource"""
    action: Action
    resource_type: ResourceType
    resource_id: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        resource_str = f"{self.resource_type.value}"
        if self.resource_id:
            resource_str += f":{self.resource_id}"
        return f"{self.action.value}:{resource_str}"


@dataclass
class Role:
    """Represents a role with permissions and metadata"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_permission(self, permission: Permission):
        """Add permission to role"""
        self.permissions.add(permission)
        self.updated_at = datetime.utcnow()
    
    def remove_permission(self, permission: Permission):
        """Remove permission from role"""
        self.permissions.discard(permission)
        self.updated_at = datetime.utcnow()


@dataclass
class User:
    """Represents a user with roles and attributes"""
    user_id: str
    username: str
    email: str
    roles: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_role(self, role_name: str):
        """Add role to user"""
        self.roles.add(role_name)
        self.updated_at = datetime.utcnow()
    
    def remove_role(self, role_name: str):
        """Remove role from user"""
        self.roles.discard(role_name)
        self.updated_at = datetime.utcnow()


@dataclass
class Resource:
    """Represents a resource that can be accessed"""
    resource_id: str
    resource_type: ResourceType
    owner: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessRequest:
    """Represents an access request"""
    user_id: str
    action: Action
    resource_type: ResourceType
    resource_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __str__(self):
        resource_str = f"{self.resource_type.value}"
        if self.resource_id:
            resource_str += f":{self.resource_id}"
        return f"{self.user_id} -> {self.action.value}:{resource_str}"


@dataclass
class AccessLog:
    """Access control audit log entry"""
    request: AccessRequest
    decision: AccessDecision
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    ip_address: Optional[str] = None


class PolicyEvaluator(ABC):
    """Abstract base class for policy evaluators"""
    
    @abstractmethod
    def evaluate(self, request: AccessRequest, user: User, resource: Optional[Resource] = None) -> Tuple[AccessDecision, str]:
        """Evaluate access request"""
        pass


class RBACEvaluator(PolicyEvaluator):
    """Role-Based Access Control evaluator"""
    
    def __init__(self, role_manager: 'RoleManager'):
        self.role_manager = role_manager
    
    def evaluate(self, request: AccessRequest, user: User, resource: Optional[Resource] = None) -> Tuple[AccessDecision, str]:
        """Evaluate RBAC request"""
        if not user.is_active:
            return AccessDecision.DENY, "User account is inactive"
        
        # Get all permissions for user's roles
        user_permissions = self.role_manager.get_user_permissions(user.user_id)
        
        # Check if user has required permission
        required_permission = Permission(
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id
        )
        
        # Check exact permission match
        if required_permission in user_permissions:
            return AccessDecision.PERMIT, "Direct permission match"
        
        # Check wildcard permissions (without resource_id)
        wildcard_permission = Permission(
            action=request.action,
            resource_type=request.resource_type
        )
        
        if wildcard_permission in user_permissions:
            return AccessDecision.PERMIT, "Wildcard permission match"
        
        # Check admin permissions
        admin_permission = Permission(
            action=Action.ADMIN,
            resource_type=request.resource_type
        )
        
        if admin_permission in user_permissions:
            return AccessDecision.PERMIT, "Admin permission"
        
        # Check system admin
        system_admin = Permission(
            action=Action.ADMIN,
            resource_type=ResourceType.SYSTEM
        )
        
        if system_admin in user_permissions:
            return AccessDecision.PERMIT, "System admin permission"
        
        return AccessDecision.DENY, "No matching permissions found"


class ABACEvaluator(PolicyEvaluator):
    """Attribute-Based Access Control evaluator"""
    
    def __init__(self):
        self.policies: List[Dict[str, Any]] = []
    
    def add_policy(self, policy: Dict[str, Any]):
        """Add ABAC policy"""
        self.policies.append(policy)
    
    def evaluate(self, request: AccessRequest, user: User, resource: Optional[Resource] = None) -> Tuple[AccessDecision, str]:
        """Evaluate ABAC request"""
        if not user.is_active:
            return AccessDecision.DENY, "User account is inactive"
        
        context = {
            'user': user.attributes,
            'resource': resource.attributes if resource else {},
            'environment': request.context,
            'time': request.timestamp,
            'action': request.action.value,
            'resource_type': request.resource_type.value
        }
        
        for policy in self.policies:
            decision = self._evaluate_policy(policy, context)
            if decision != AccessDecision.NOT_APPLICABLE:
                return decision, f"Policy '{policy.get('name', 'unnamed')}' applied"
        
        return AccessDecision.DENY, "No applicable policies found"
    
    def _evaluate_policy(self, policy: Dict[str, Any], context: Dict[str, Any]) -> AccessDecision:
        """Evaluate a single ABAC policy"""
        try:
            # Simple rule evaluation (in real implementation, use a proper rule engine)
            target = policy.get('target', {})
            
            # Check if policy applies to this request
            if not self._matches_target(target, context):
                return AccessDecision.NOT_APPLICABLE
            
            # Evaluate conditions
            conditions = policy.get('conditions', [])
            for condition in conditions:
                if not self._evaluate_condition(condition, context):
                    return AccessDecision.DENY
            
            # Return policy effect
            effect = policy.get('effect', 'deny')
            return AccessDecision.PERMIT if effect.lower() == 'permit' else AccessDecision.DENY
            
        except Exception:
            return AccessDecision.INDETERMINATE
    
    def _matches_target(self, target: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if target matches context"""
        for key, expected_value in target.items():
            if key in context:
                if isinstance(expected_value, list):
                    if context[key] not in expected_value:
                        return False
                else:
                    if context[key] != expected_value:
                        return False
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition"""
        condition_type = condition.get('type')
        
        if condition_type == 'time_range':
            return self._evaluate_time_condition(condition, context)
        elif condition_type == 'attribute_match':
            return self._evaluate_attribute_condition(condition, context)
        elif condition_type == 'ownership':
            return self._evaluate_ownership_condition(condition, context)
        
        return True
    
    def _evaluate_time_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate time-based condition"""
        current_time = context['time']
        start_time = condition.get('start_time')
        end_time = condition.get('end_time')
        
        if start_time and current_time.time() < datetime.strptime(start_time, '%H:%M').time():
            return False
        if end_time and current_time.time() > datetime.strptime(end_time, '%H:%M').time():
            return False
        
        return True
    
    def _evaluate_attribute_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate attribute-based condition"""
        subject = condition.get('subject', 'user')
        attribute = condition.get('attribute')
        operator = condition.get('operator', 'equals')
        value = condition.get('value')
        
        if subject not in context or attribute not in context[subject]:
            return False
        
        actual_value = context[subject][attribute]
        
        if operator == 'equals':
            return actual_value == value
        elif operator == 'contains':
            return value in actual_value if isinstance(actual_value, (list, str)) else False
        elif operator == 'greater_than':
            return actual_value > value
        elif operator == 'less_than':
            return actual_value < value
        
        return False
    
    def _evaluate_ownership_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate ownership condition"""
        if 'user' not in context or 'resource' not in context:
            return False
        
        user_id = context['user'].get('user_id')
        resource_owner = context['resource'].get('owner')
        
        return user_id == resource_owner


class RoleManager:
    """Manages roles and role hierarchies"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.role_hierarchy: Dict[str, Set[str]] = {}  # role -> parent roles
    
    def create_role(self, name: str, description: str, parent_roles: List[str] = None) -> Role:
        """Create a new role"""
        if name in self.roles:
            raise ValueError(f"Role '{name}' already exists")
        
        parent_set = set(parent_roles) if parent_roles else set()
        
        # Validate parent roles exist
        for parent in parent_set:
            if parent not in self.roles:
                raise ValueError(f"Parent role '{parent}' does not exist")
        
        role = Role(name=name, description=description, parent_roles=parent_set)
        self.roles[name] = role
        self.role_hierarchy[name] = parent_set
        
        return role
    
    def delete_role(self, name: str):
        """Delete a role"""
        if name not in self.roles:
            raise ValueError(f"Role '{name}' does not exist")
        
        # Check if role is used as parent
        for role_name, parents in self.role_hierarchy.items():
            if name in parents:
                raise ValueError(f"Cannot delete role '{name}' - it is used as parent for '{role_name}'")
        
        del self.roles[name]
        del self.role_hierarchy[name]
    
    def add_permission_to_role(self, role_name: str, permission: Permission):
        """Add permission to role"""
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")
        
        self.roles[role_name].add_permission(permission)
    
    def remove_permission_from_role(self, role_name: str, permission: Permission):
        """Remove permission from role"""
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")
        
        self.roles[role_name].remove_permission(permission)
    
    def get_role_permissions(self, role_name: str, include_inherited: bool = True) -> Set[Permission]:
        """Get all permissions for a role"""
        if role_name not in self.roles:
            return set()
        
        permissions = set(self.roles[role_name].permissions)
        
        if include_inherited:
            # Add permissions from parent roles
            for parent_role in self.role_hierarchy.get(role_name, set()):
                permissions.update(self.get_role_permissions(parent_role, True))
        
        return permissions
    
    def get_user_permissions(self, user_id: str, user_roles: Set[str] = None) -> Set[Permission]:
        """Get all permissions for a user based on their roles"""
        if user_roles is None:
            # In real implementation, fetch from user store
            return set()
        
        permissions = set()
        for role_name in user_roles:
            permissions.update(self.get_role_permissions(role_name))
        
        return permissions


class AccessControlManager:
    """Main access control manager"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.resources: Dict[str, Resource] = {}
        self.role_manager = RoleManager()
        self.rbac_evaluator = RBACEvaluator(self.role_manager)
        self.abac_evaluator = ABACEvaluator()
        self.access_logs: List[AccessLog] = []
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default roles
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        # Super admin role
        super_admin = self.role_manager.create_role(
            "super_admin",
            "Super administrator with full system access"
        )
        super_admin.add_permission(Permission(Action.ADMIN, ResourceType.SYSTEM))
        
        # Admin role
        admin = self.role_manager.create_role(
            "admin",
            "Administrator with elevated privileges",
            ["super_admin"]
        )
        
        # User role
        user = self.role_manager.create_role(
            "user",
            "Standard user with basic access"
        )
        user.add_permission(Permission(Action.READ, ResourceType.DOCUMENT))
        user.add_permission(Permission(Action.CREATE, ResourceType.DOCUMENT))
        user.add_permission(Permission(Action.UPDATE, ResourceType.DOCUMENT))
        
        # Guest role
        guest = self.role_manager.create_role(
            "guest",
            "Guest user with read-only access"
        )
        guest.add_permission(Permission(Action.READ, ResourceType.DOCUMENT))
    
    def create_user(self, user_id: str, username: str, email: str, roles: List[str] = None) -> User:
        """Create a new user"""
        if user_id in self.users:
            raise ValueError(f"User '{user_id}' already exists")
        
        user_roles = set(roles) if roles else {"user"}
        
        # Validate roles exist
        for role in user_roles:
            if role not in self.role_manager.roles:
                raise ValueError(f"Role '{role}' does not exist")
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=user_roles
        )
        
        self.users[user_id] = user
        return user
    
    def create_resource(self, resource_id: str, resource_type: ResourceType, owner: str, attributes: Dict[str, Any] = None) -> Resource:
        """Create a new resource"""
        if resource_id in self.resources:
            raise ValueError(f"Resource '{resource_id}' already exists")
        
        resource = Resource(
            resource_id=resource_id,
            resource_type=resource_type,
            owner=owner,
            attributes=attributes or {}
        )
        
        self.resources[resource_id] = resource
        return resource
    
    def check_access(self, request: AccessRequest, use_abac: bool = False) -> Tuple[AccessDecision, str]:
        """Check access for a request"""
        # Get user
        if request.user_id not in self.users:
            decision = AccessDecision.DENY
            reason = "User not found"
        else:
            user = self.users[request.user_id]
            
            # Get resource if specified
            resource = None
            if request.resource_id and request.resource_id in self.resources:
                resource = self.resources[request.resource_id]
            
            # Choose evaluator
            if use_abac:
                decision, reason = self.abac_evaluator.evaluate(request, user, resource)
            else:
                decision, reason = self.rbac_evaluator.evaluate(request, user, resource)
        
        # Log access attempt
        access_log = AccessLog(
            request=request,
            decision=decision,
            reason=reason,
            ip_address=request.context.get('ip_address'),
            session_id=request.context.get('session_id')
        )
        self.access_logs.append(access_log)
        
        return decision, reason
    
    def create_session(self, user_id: str, ip_address: str = None) -> str:
        """Create a user session"""
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'ip_address': ip_address,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        # Update user last login
        if user_id in self.users:
            self.users[user_id].last_login = datetime.utcnow()
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str = None) -> Optional[str]:
        """Validate session and return user_id"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check IP address if provided
        if ip_address and session.get('ip_address') != ip_address:
            return None
        
        # Check session timeout (24 hours)
        if datetime.utcnow() - session['last_activity'] > timedelta(hours=24):
            del self.sessions[session_id]
            return None
        
        # Update last activity
        session['last_activity'] = datetime.utcnow()
        
        return session['user_id']
    
    def revoke_session(self, session_id: str):
        """Revoke a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_access_logs(self, user_id: str = None, start_time: datetime = None, end_time: datetime = None) -> List[AccessLog]:
        """Get access logs with optional filtering"""
        logs = self.access_logs
        
        if user_id:
            logs = [log for log in logs if log.request.user_id == user_id]
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        return logs
    
    def export_policy_config(self) -> Dict[str, Any]:
        """Export access control configuration"""
        return {
            'roles': {
                name: {
                    'description': role.description,
                    'permissions': [str(perm) for perm in role.permissions],
                    'parent_roles': list(role.parent_roles),
                    'is_active': role.is_active
                }
                for name, role in self.role_manager.roles.items()
            },
            'users': {
                user.user_id: {
                    'username': user.username,
                    'email': user.email,
                    'roles': list(user.roles),
                    'is_active': user.is_active
                }
                for user in self.users.values()
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize access control manager
    acm = AccessControlManager()
    
    # Create users
    admin_user = acm.create_user("admin1", "admin", "admin@example.com", ["admin"])
    regular_user = acm.create_user("user1", "johndoe", "john@example.com", ["user"])
    
    # Create resources
    doc1 = acm.create_resource("doc1", ResourceType.DOCUMENT, "user1", {"classification": "public"})
    config1 = acm.create_resource("config1", ResourceType.CONFIGURATION, "admin1", {"environment": "production"})
    
    # Test access control
    requests_to_test = [
        AccessRequest("user1", Action.READ, ResourceType.DOCUMENT, "doc1"),
        AccessRequest("user1", Action.DELETE, ResourceType.DOCUMENT, "doc1"),
        AccessRequest("admin1", Action.DELETE, ResourceType.DOCUMENT, "doc1"),
        AccessRequest("user1", Action.UPDATE, ResourceType.CONFIGURATION, "config1"),
        AccessRequest("admin1", Action.UPDATE, ResourceType.CONFIGURATION, "config1"),
    ]
    
    print("Access Control Test Results:")
    print("=" * 50)
    
    for request in requests_to_test:
        decision, reason = acm.check_access(request)
        print(f"Request: {request}")
        print(f"Decision: {decision.value}")
        print(f"Reason: {reason}")
        print("-" * 30)
    
    # Export configuration
    config = acm.export_policy_config()
    print(f"\nConfiguration exported with {len(config['roles'])} roles and {len(config['users'])} users")