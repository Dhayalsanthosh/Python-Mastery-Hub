# Location: src/python_mastery_hub/web/api/admin.py

"""
Admin API Router

Handles admin panel endpoints for user management, content administration,
system monitoring, and analytics.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, validator

from python_mastery_hub.web.middleware.auth import get_current_user, require_admin
from python_mastery_hub.web.models.user import User
from python_mastery_hub.web.services.progress_service import ProgressService
from python_mastery_hub.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class UserSummary(BaseModel):
    """User summary for admin view."""
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: str
    last_login: Optional[str]
    total_exercises: int
    completed_exercises: int
    total_time_spent: int  # minutes


class UserDetails(BaseModel):
    """Detailed user information for admin."""
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: str
    last_login: Optional[str]
    login_count: int
    profile_data: Dict[str, Any]
    progress_summary: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]


class UserUpdate(BaseModel):
    """User update request for admin."""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SystemStats(BaseModel):
    """System-wide statistics."""
    total_users: int
    active_users_24h: int
    active_users_7d: int
    active_users_30d: int
    total_exercises: int
    total_submissions: int
    total_code_executions: int
    average_session_duration: float  # minutes
    popular_modules: List[Dict[str, Any]]
    user_growth_trend: List[Dict[str, Any]]


class ExerciseStats(BaseModel):
    """Exercise performance statistics."""
    exercise_id: str
    title: str
    module_id: str
    total_attempts: int
    unique_users: int
    success_rate: float
    average_attempts: float
    average_time: float  # minutes
    difficulty_rating: float
    common_errors: List[str]


class ModuleAnalytics(BaseModel):
    """Module analytics data."""
    module_id: str
    title: str
    total_users: int
    completion_rate: float
    average_time: float  # minutes
    exercises_count: int
    difficulty_distribution: Dict[str, int]
    user_satisfaction: float
    drop_off_points: List[str]


class ContentRequest(BaseModel):
    """Content creation/update request."""
    title: str
    description: str
    content_type: str  # exercise, lesson, quiz
    module_id: str
    difficulty: str
    metadata: Dict[str, Any] = {}


class BulkAction(BaseModel):
    """Bulk action request."""
    action: str  # activate, deactivate, delete, verify
    user_ids: List[str]
    reason: Optional[str] = None


class AuditLog(BaseModel):
    """Audit log entry."""
    id: str
    timestamp: str
    admin_user_id: str
    admin_username: str
    action: str
    target_type: str  # user, exercise, system
    target_id: Optional[str]
    details: Dict[str, Any]
    ip_address: str


# Routes
@router.get("/users", response_model=List[UserSummary])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    sort_by: str = Query("created_at", regex="^(created_at|last_login|username|email)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Get list of users with filtering and pagination."""
    try:
        users_data = await progress_service.get_users_for_admin(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            is_verified=is_verified,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return [
            UserSummary(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                full_name=user['full_name'],
                is_active=user['is_active'],
                is_verified=user['is_verified'],
                created_at=user['created_at'],
                last_login=user.get('last_login'),
                total_exercises=user.get('total_exercises', 0),
                completed_exercises=user.get('completed_exercises', 0),
                total_time_spent=user.get('total_time_spent', 0)
            )
            for user in users_data
        ]
    
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/users/{user_id}", response_model=UserDetails)
async def get_user_details(
    user_id: str,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Get detailed information about a specific user."""
    try:
        user_data = await progress_service.get_user_details_for_admin(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found"
            )
        
        return UserDetails(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            is_active=user_data['is_active'],
            is_verified=user_data['is_verified'],
            is_admin=user_data.get('is_admin', False),
            created_at=user_data['created_at'],
            last_login=user_data.get('last_login'),
            login_count=user_data.get('login_count', 0),
            profile_data=user_data.get('profile_data', {}),
            progress_summary=user_data.get('progress_summary', {}),
            recent_activity=user_data.get('recent_activity', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user details {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user details"
        )


@router.put("/users/{user_id}", response_model=UserDetails)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Update user information."""
    try:
        # Log admin action
        await progress_service.log_admin_action(
            admin_id=current_user.id,
            action="update_user",
            target_type="user",
            target_id=user_id,
            details=user_update.dict(exclude_unset=True),
            ip_address="0.0.0.0"  # Would get from request in real implementation
        )
        
        updated_user = await progress_service.update_user_by_admin(
            user_id, 
            user_update.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found"
            )
        
        return UserDetails(
            id=updated_user['id'],
            username=updated_user['username'],
            email=updated_user['email'],
            full_name=updated_user['full_name'],
            is_active=updated_user['is_active'],
            is_verified=updated_user['is_verified'],
            is_admin=updated_user.get('is_admin', False),
            created_at=updated_user['created_at'],
            last_login=updated_user.get('last_login'),
            login_count=updated_user.get('login_count', 0),
            profile_data=updated_user.get('profile_data', {}),
            progress_summary=updated_user.get('progress_summary', {}),
            recent_activity=updated_user.get('recent_activity', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Delete a user account."""
    try:
        # Prevent admin from deleting themselves
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Log admin action
        await progress_service.log_admin_action(
            admin_id=current_user.id,
            action="delete_user",
            target_type="user",
            target_id=user_id,
            details={},
            ip_address="0.0.0.0"
        )
        
        result = await progress_service.delete_user_by_admin(user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found"
            )
        
        return {"message": f"User '{user_id}' deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/users/bulk-action")
async def bulk_user_action(
    bulk_action: BulkAction,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Perform bulk action on multiple users."""
    try:
        # Validate action
        valid_actions = ["activate", "deactivate", "verify", "unverify", "delete"]
        if bulk_action.action not in valid_actions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action. Must be one of: {valid_actions}"
            )
        
        # Prevent admin from affecting their own account in bulk operations
        if current_user.id in bulk_action.user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot perform bulk actions on your own account"
            )
        
        # Log admin action
        await progress_service.log_admin_action(
            admin_id=current_user.id,
            action=f"bulk_{bulk_action.action}",
            target_type="users",
            target_id=None,
            details={
                "user_ids": bulk_action.user_ids,
                "reason": bulk_action.reason
            },
            ip_address="0.0.0.0"
        )
        
        result = await progress_service.bulk_user_action(
            action=bulk_action.action,
            user_ids=bulk_action.user_ids,
            admin_id=current_user.id
        )
        
        return {
            "message": f"Bulk {bulk_action.action} completed",
            "affected_users": result.get("affected_users", 0),
            "failed_users": result.get("failed_users", [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform bulk action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk action"
        )


@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Get system-wide statistics."""
    try:
        stats_data = await progress_service.get_system_statistics()
        
        return SystemStats(
            total_users=stats_data.get('total_users', 0),
            active_users_24h=stats_data.get('active_users_24h', 0),
            active_users_7d=stats_data.get('active_users_7d', 0),
            active_users_30d=stats_data.get('active_users_30d', 0),
            total_exercises=stats_data.get('total_exercises', 0),
            total_submissions=stats_data.get('total_submissions', 0),
            total_code_executions=stats_data.get('total_code_executions', 0),
            average_session_duration=stats_data.get('average_session_duration', 0.0),
            popular_modules=stats_data.get('popular_modules', []),
            user_growth_trend=stats_data.get('user_growth_trend', [])
        )
    
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )


@router.get("/stats/exercises", response_model=List[ExerciseStats])
async def get_exercise_stats(
    module_id: Optional[str] = None,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Get exercise performance statistics."""
    try:
        stats_data = await progress_service.get_exercise_statistics(module_id)
        
        return [
            ExerciseStats(
                exercise_id=exercise['exercise_id'],
                title=exercise['title'],
                module_id=exercise['module_id'],
                total_attempts=exercise['total_attempts'],
                unique_users=exercise['unique_users'],
                success_rate=exercise['success_rate'],
                average_attempts=exercise['average_attempts'],
                average_time=exercise['average_time'],
                difficulty_rating=exercise['difficulty_rating'],
                common_errors=exercise['common_errors']
            )
            for exercise in stats_data
        ]
    
    except Exception as e:
        logger.error(f"Failed to get exercise stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise statistics"
        )


@router.get("/stats/modules", response_model=List[ModuleAnalytics])
async def get_module_analytics(
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Get module analytics data."""
    try:
        analytics_data = await progress_service.get_module_analytics()
        
        return [
            ModuleAnalytics(
                module_id=module['module_id'],
                title=module['title'],
                total_users=module['total_users'],
                completion_rate=module['completion_rate'],
                average_time=module['average_time'],
                exercises_count=module['exercises_count'],
                difficulty_distribution=module['difficulty_distribution'],
                user_satisfaction=module['user_satisfaction'],
                drop_off_points=module['drop_off_points']
            )
            for module in analytics_data
        ]
    
    except Exception as e:
        logger.error(f"Failed to get module analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module analytics"
        )


@router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    admin_user_id: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Get audit logs with filtering."""
    try:
        logs_data = await progress_service.get_audit_logs(
            skip=skip,
            limit=limit,
            action=action,
            admin_user_id=admin_user_id,
            target_type=target_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return [
            AuditLog(
                id=log['id'],
                timestamp=log['timestamp'],
                admin_user_id=log['admin_user_id'],
                admin_username=log['admin_username'],
                action=log['action'],
                target_type=log['target_type'],
                target_id=log.get('target_id'),
                details=log['details'],
                ip_address=log['ip_address']
            )
            for log in logs_data
        ]
    
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.post("/system/backup")
async def create_system_backup(
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Create a system backup."""
    try:
        # Log admin action
        await progress_service.log_admin_action(
            admin_id=current_user.id,
            action="create_backup",
            target_type="system",
            target_id=None,
            details={},
            ip_address="0.0.0.0"
        )
        
        backup_result = await progress_service.create_system_backup()
        
        return {
            "message": "System backup created successfully",
            "backup_id": backup_result.get("backup_id"),
            "backup_size": backup_result.get("backup_size"),
            "created_at": backup_result.get("created_at")
        }
    
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create system backup"
        )


@router.post("/system/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    current_user: User = Depends(require_admin),
    progress_service: ProgressService = Depends(ProgressService)
):
    """Toggle system maintenance mode."""
    try:
        # Log admin action
        await progress_service.log_admin_action(
            admin_id=current_user.id,
            action="toggle_maintenance",
            target_type="system",
            target_id=None,
            details={"enabled": enabled, "message": message},
            ip_address="0.0.0.0"
        )
        
        result = await progress_service.set_maintenance_mode(enabled, message)
        
        return {
            "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}",
            "status": result.get("status"),
            "maintenance_message": result.get("maintenance_message")
        }
    
    except Exception as e:
        logger.error(f"Failed to toggle maintenance mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle maintenance mode"
        )