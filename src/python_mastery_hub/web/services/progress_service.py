# Location: src/python_mastery_hub/web/services/progress_service.py

"""
Progress Service

Handles user progress tracking, analytics, achievements, and learning 
path recommendations across the platform.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

from python_mastery_hub.web.models.progress import (
    UserProgress, ModuleProgress, TopicProgress, Achievement,
    ProgressStatus, LearningStreak, StudySession, ProgressUpdate,
    ProgressSummary, LeaderboardEntry, ProgressAnalytics
)
from python_mastery_hub.web.models.user import User
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ProgressTracker:
    """Tracks and calculates user progress metrics."""
    
    @staticmethod
    def calculate_module_progress(topics: List[TopicProgress]) -> Dict[str, Any]:
        """Calculate overall module progress from topics."""
        if not topics:
            return {
                'completion_percentage': 0.0,
                'overall_score': 0.0,
                'topics_completed': 0,
                'time_spent': 0
            }
        
        completed_topics = [t for t in topics if t.status == ProgressStatus.COMPLETED]
        total_score = sum(t.score for t in topics)
        total_time = sum(t.time_spent for t in topics)
        
        return {
            'completion_percentage': (len(completed_topics) / len(topics)) * 100,
            'overall_score': total_score / len(topics) if topics else 0.0,
            'topics_completed': len(completed_topics),
            'time_spent': total_time
        }
    
    @staticmethod
    def calculate_experience_points(score: float, difficulty: str, time_spent: int) -> int:
        """Calculate experience points based on performance."""
        base_points = 100
        
        # Score multiplier (0.0 to 1.0)
        score_multiplier = score
        
        # Difficulty multiplier
        difficulty_multipliers = {
            'beginner': 1.0,
            'intermediate': 1.5,
            'advanced': 2.0,
            'expert': 2.5
        }
        difficulty_multiplier = difficulty_multipliers.get(difficulty, 1.0)
        
        # Time bonus (faster completion gets bonus)
        time_bonus = max(0, (30 - time_spent) / 30) * 0.2  # Up to 20% bonus
        
        total_points = base_points * score_multiplier * difficulty_multiplier * (1 + time_bonus)
        
        return int(total_points)
    
    @staticmethod
    def calculate_level(experience_points: int) -> Tuple[int, int]:
        """Calculate user level and points needed for next level."""
        # Level formula: level = floor(sqrt(xp / 100))
        import math
        level = int(math.sqrt(experience_points / 100)) + 1
        
        # Points needed for next level
        next_level_total = ((level) ** 2) * 100
        next_level_points = next_level_total - experience_points
        
        return level, next_level_points
    
    @staticmethod
    def update_streak(last_activity: Optional[datetime], current_activity: datetime) -> Dict[str, Any]:
        """Update learning streak based on activity."""
        if not last_activity:
            return {
                'current_streak': 1,
                'streak_start_date': current_activity,
                'is_new_day': True
            }
        
        # Check if it's a new day
        last_date = last_activity.date()
        current_date = current_activity.date()
        
        if last_date == current_date:
            # Same day, no streak change
            return {'is_new_day': False}
        
        days_diff = (current_date - last_date).days
        
        if days_diff == 1:
            # Consecutive day, increment streak
            return {'current_streak': 1, 'is_new_day': True, 'increment': True}
        else:
            # Streak broken, reset
            return {
                'current_streak': 1,
                'streak_start_date': current_activity,
                'is_new_day': True,
                'reset': True
            }


class ProgressService:
    """Main progress tracking service."""
    
    def __init__(self):
        self.tracker = ProgressTracker()
        self.achievement_rules = self._load_achievement_rules()
    
    def _load_achievement_rules(self) -> Dict[str, Any]:
        """Load achievement rules and criteria."""
        return {
            'first_exercise': {
                'type': 'milestone',
                'criteria': {'exercises_completed': 1},
                'points': 50,
                'title': 'First Steps',
                'description': 'Complete your first exercise'
            },
            'streak_7': {
                'type': 'streak',
                'criteria': {'streak_days': 7},
                'points': 200,
                'title': 'Week Warrior',
                'description': 'Study for 7 days in a row'
            },
            'perfectionist': {
                'type': 'skill',
                'criteria': {'perfect_scores': 10},
                'points': 300,
                'title': 'Perfectionist',
                'description': 'Get perfect scores on 10 exercises'
            },
            'speed_demon': {
                'type': 'skill',
                'criteria': {'fast_completions': 5},
                'points': 250,
                'title': 'Speed Demon',
                'description': 'Complete 5 exercises in record time'
            },
            'module_master': {
                'type': 'milestone',
                'criteria': {'modules_completed': 1},
                'points': 500,
                'title': 'Module Master',
                'description': 'Complete your first module'
            }
        }
    
    async def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Get comprehensive user progress."""
        try:
            # TODO: Query database for user progress
            # progress_data = await database.fetch_one(
            #     "SELECT * FROM user_progress WHERE user_id = :user_id",
            #     {"user_id": user_id}
            # )
            
            # Mock data for demonstration
            if user_id == "mock_user_id":
                from datetime import datetime
                return UserProgress(
                    user_id=user_id,
                    overall_progress=0.65,
                    total_time_spent=1800,  # 30 hours
                    modules_completed=2,
                    total_modules=5,
                    exercises_completed=25,
                    total_exercises_attempted=30,
                    average_score=0.85,
                    current_level=3,
                    experience_points=750,
                    next_level_points=250,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return None
    
    async def update_topic_progress(
        self,
        user_id: str,
        progress_update: ProgressUpdate
    ) -> bool:
        """Update progress for a specific topic."""
        try:
            # Get current progress
            current_progress = await self.get_topic_progress(user_id, progress_update.topic_id)
            
            # Calculate new values
            new_score = progress_update.score or (current_progress.score if current_progress else 0.0)
            new_time = (current_progress.time_spent if current_progress else 0) + (progress_update.time_spent or 0)
            
            # Determine status
            if progress_update.status:
                new_status = progress_update.status
            elif new_score >= 0.9:
                new_status = ProgressStatus.MASTERED
            elif new_score >= 0.7:
                new_status = ProgressStatus.COMPLETED
            elif new_score > 0:
                new_status = ProgressStatus.IN_PROGRESS
            else:
                new_status = ProgressStatus.NOT_STARTED
            
            # Update database
            # TODO: Implement database update
            # await database.execute(
            #     """
            #     INSERT INTO topic_progress (user_id, topic_id, module_id, score, time_spent, status, notes, last_accessed)
            #     VALUES (:user_id, :topic_id, :module_id, :score, :time_spent, :status, :notes, :last_accessed)
            #     ON CONFLICT (user_id, topic_id) DO UPDATE SET
            #         score = :score,
            #         time_spent = :time_spent,
            #         status = :status,
            #         notes = :notes,
            #         last_accessed = :last_accessed,
            #         completion_date = CASE WHEN :status = 'completed' THEN :last_accessed ELSE completion_date END
            #     """,
            #     {
            #         "user_id": user_id,
            #         "topic_id": progress_update.topic_id,
            #         "module_id": progress_update.module_id,
            #         "score": new_score,
            #         "time_spent": new_time,
            #         "status": new_status.value,
            #         "notes": progress_update.notes,
            #         "last_accessed": datetime.now()
            #     }
            # )
            
            # Update module progress
            await self._update_module_progress(user_id, progress_update.module_id)
            
            # Update overall user progress
            await self._update_user_progress(user_id)
            
            # Check for new achievements
            await self._check_achievements(user_id)
            
            logger.info(f"Updated topic progress for user {user_id}, topic {progress_update.topic_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating topic progress: {e}")
            return False
    
    async def mark_topic_completed(
        self,
        user_id: str,
        module_id: str,
        topic_id: str,
        score: float,
        time_spent: int
    ) -> bool:
        """Mark a topic as completed with score and time."""
        progress_update = ProgressUpdate(
            topic_id=topic_id,
            module_id=module_id,
            score=score,
            time_spent=time_spent,
            status=ProgressStatus.COMPLETED
        )
        
        return await self.update_topic_progress(user_id, progress_update)
    
    async def get_topic_progress(self, user_id: str, topic_id: str) -> Optional[TopicProgress]:
        """Get progress for a specific topic."""
        try:
            # TODO: Query database
            # return await database.fetch_one(
            #     "SELECT * FROM topic_progress WHERE user_id = :user_id AND topic_id = :topic_id",
            #     {"user_id": user_id, "topic_id": topic_id}
            # )
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting topic progress: {e}")
            return None
    
    async def get_module_progress(self, user_id: str, module_id: str) -> Optional[ModuleProgress]:
        """Get progress for a specific module."""
        try:
            # TODO: Query database for module and its topics
            # module_data = await database.fetch_one(
            #     "SELECT * FROM module_progress WHERE user_id = :user_id AND module_id = :module_id",
            #     {"user_id": user_id, "module_id": module_id}
            # )
            
            # topics_data = await database.fetch_all(
            #     "SELECT * FROM topic_progress WHERE user_id = :user_id AND module_id = :module_id",
            #     {"user_id": user_id, "module_id": module_id}
            # )
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting module progress: {e}")
            return None
    
    async def _update_module_progress(self, user_id: str, module_id: str) -> None:
        """Update module progress based on topic progress."""
        try:
            # Get all topics for the module
            # topics = await database.fetch_all(
            #     "SELECT * FROM topic_progress WHERE user_id = :user_id AND module_id = :module_id",
            #     {"user_id": user_id, "module_id": module_id}
            # )
            
            # Calculate module metrics
            # metrics = self.tracker.calculate_module_progress(topics)
            
            # Update module progress
            # TODO: Update database
            pass
        
        except Exception as e:
            logger.error(f"Error updating module progress: {e}")
    
    async def _update_user_progress(self, user_id: str) -> None:
        """Update overall user progress."""
        try:
            # Get all user progress data
            # Calculate overall metrics
            # Update user progress record
            # TODO: Implement
            pass
        
        except Exception as e:
            logger.error(f"Error updating user progress: {e}")
    
    async def _check_achievements(self, user_id: str) -> List[Achievement]:
        """Check and award new achievements."""
        new_achievements = []
        
        try:
            # Get user stats
            user_progress = await self.get_user_progress(user_id)
            if not user_progress:
                return new_achievements
            
            # Check each achievement rule
            for achievement_id, rule in self.achievement_rules.items():
                # Check if user already has this achievement
                has_achievement = await self._user_has_achievement(user_id, achievement_id)
                if has_achievement:
                    continue
                
                # Check criteria
                if self._check_achievement_criteria(user_progress, rule['criteria']):
                    achievement = Achievement(
                        id=achievement_id,
                        title=rule['title'],
                        description=rule['description'],
                        type=rule['type'],
                        points=rule['points'],
                        earned_date=datetime.now()
                    )
                    
                    # Award achievement
                    await self._award_achievement(user_id, achievement)
                    new_achievements.append(achievement)
            
            return new_achievements
        
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return new_achievements
    
    def _check_achievement_criteria(self, user_progress: UserProgress, criteria: Dict[str, Any]) -> bool:
        """Check if user meets achievement criteria."""
        for key, required_value in criteria.items():
            if key == 'exercises_completed':
                if user_progress.exercises_completed < required_value:
                    return False
            elif key == 'streak_days':
                if user_progress.streak.current_streak < required_value:
                    return False
            elif key == 'modules_completed':
                if user_progress.modules_completed < required_value:
                    return False
            # Add more criteria checks as needed
        
        return True
    
    async def _user_has_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Check if user already has an achievement."""
        # TODO: Query database
        return False
    
    async def _award_achievement(self, user_id: str, achievement: Achievement) -> None:
        """Award achievement to user."""
        try:
            # TODO: Insert into database
            # await database.execute(
            #     "INSERT INTO user_achievements (user_id, achievement_id, earned_date, points) VALUES (:user_id, :achievement_id, :earned_date, :points)",
            #     {
            #         "user_id": user_id,
            #         "achievement_id": achievement.id,
            #         "earned_date": achievement.earned_date,
            #         "points": achievement.points
            #     }
            # )
            
            logger.info(f"Awarded achievement '{achievement.title}' to user {user_id}")
        
        except Exception as e:
            logger.error(f"Error awarding achievement: {e}")
    
    async def get_progress_summary(self, user_id: str) -> ProgressSummary:
        """Get progress summary for dashboard."""
        try:
            # Calculate this week's metrics
            week_start = datetime.now() - timedelta(days=7)
            
            # TODO: Query database for weekly stats
            # weekly_stats = await database.fetch_one(
            #     """
            #     SELECT 
            #         COALESCE(SUM(time_spent), 0) as time_this_week,
            #         COUNT(*) as exercises_this_week
            #     FROM topic_progress 
            #     WHERE user_id = :user_id AND last_accessed >= :week_start
            #     """,
            #     {"user_id": user_id, "week_start": week_start}
            # )
            
            # Mock data for demonstration
            return ProgressSummary(
                total_time_this_week=420,  # 7 hours
                exercises_completed_this_week=8,
                current_streak=5,
                modules_in_progress=2,
                weekly_goal_progress=70.0,
                performance_trend="improving"
            )
        
        except Exception as e:
            logger.error(f"Error getting progress summary: {e}")
            return ProgressSummary()
    
    async def get_leaderboard(
        self,
        limit: int = 10,
        timeframe: str = "all_time"
    ) -> List[LeaderboardEntry]:
        """Get leaderboard data."""
        try:
            # TODO: Query database with proper ranking
            # leaderboard_data = await database.fetch_all(
            #     """
            #     SELECT 
            #         u.id, u.username, u.full_name, up.experience_points,
            #         up.current_level, up.streak_current, up.exercises_completed,
            #         COUNT(ua.achievement_id) as achievements_count,
            #         ROW_NUMBER() OVER (ORDER BY up.experience_points DESC) as rank
            #     FROM users u
            #     JOIN user_progress up ON u.id = up.user_id
            #     LEFT JOIN user_achievements ua ON u.id = ua.user_id
            #     WHERE u.is_active = true
            #     GROUP BY u.id, u.username, u.full_name, up.experience_points, up.current_level, up.streak_current, up.exercises_completed
            #     ORDER BY up.experience_points DESC
            #     LIMIT :limit
            #     """,
            #     {"limit": limit}
            # )
            
            # Mock data for demonstration
            return [
                LeaderboardEntry(
                    rank=1,
                    user_id="user1",
                    username="python_master",
                    full_name="John Doe",
                    points=2500,
                    level=8,
                    streak=15,
                    exercises_completed=75,
                    achievements_count=12
                ),
                LeaderboardEntry(
                    rank=2,
                    user_id="user2", 
                    username="code_ninja",
                    full_name="Jane Smith",
                    points=2200,
                    level=7,
                    streak=8,
                    exercises_completed=68,
                    achievements_count=10
                )
            ]
        
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_exercise_attempt_count(self, user_id: str, exercise_id: str) -> int:
        """Get number of attempts for an exercise."""
        try:
            # TODO: Query database
            # result = await database.fetch_one(
            #     "SELECT COUNT(*) as count FROM exercise_submissions WHERE user_id = :user_id AND exercise_id = :exercise_id",
            #     {"user_id": user_id, "exercise_id": exercise_id}
            # )
            # return result['count'] if result else 0
            
            return 0  # Mock
        
        except Exception as e:
            logger.error(f"Error getting exercise attempt count: {e}")
            return 0
    
    async def save_exercise_submission(
        self,
        user_id: str,
        exercise_id: str,
        submission_id: str,
        code: str,
        score: float,
        max_score: float,
        passed: bool,
        execution_time: float
    ) -> bool:
        """Save exercise submission."""
        try:
            # TODO: Insert into database
            # await database.execute(
            #     """
            #     INSERT INTO exercise_submissions 
            #     (id, user_id, exercise_id, code, score, max_score, passed, execution_time, submitted_at)
            #     VALUES (:id, :user_id, :exercise_id, :code, :score, :max_score, :passed, :execution_time, :submitted_at)
            #     """,
            #     {
            #         "id": submission_id,
            #         "user_id": user_id,
            #         "exercise_id": exercise_id,
            #         "code": code,
            #         "score": score,
            #         "max_score": max_score,
            #         "passed": passed,
            #         "execution_time": execution_time,
            #         "submitted_at": datetime.now()
            #     }
            # )
            
            logger.info(f"Saved exercise submission: {submission_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving exercise submission: {e}")
            return False
    
    # Additional methods for admin functionality
    async def get_users_for_admin(self, **filters) -> List[Dict[str, Any]]:
        """Get users for admin panel."""
        # TODO: Implement database query with filters
        return []
    
    async def get_user_details_for_admin(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed user info for admin."""
        # TODO: Implement database query
        return None
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        # TODO: Implement comprehensive stats query
        return {}
    
    async def get_exercise_statistics(self, module_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get exercise performance statistics."""
        # TODO: Implement stats calculation
        return []
    
    async def get_module_analytics(self) -> List[Dict[str, Any]]:
        """Get module analytics."""
        # TODO: Implement analytics calculation
        return []
    
    async def log_admin_action(self, admin_id: str, action: str, target_type: str, target_id: Optional[str], details: Dict[str, Any], ip_address: str) -> None:
        """Log admin action for audit."""
        # TODO: Implement audit logging
        pass