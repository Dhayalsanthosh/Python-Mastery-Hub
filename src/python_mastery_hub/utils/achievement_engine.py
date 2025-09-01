# src/python_mastery_hub/utils/achievement_engine.py
"""
Achievement Engine - Gamification and Badge System

Manages achievements, badges, and gamification elements to motivate learning.
Tracks milestones and provides rewards for learning progress.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Avoid circular imports
if TYPE_CHECKING:
    from .progress_calculator import ProgressCalculator

logger = logging.getLogger(__name__)


class AchievementCategory(Enum):
    """Categories for different types of achievements."""
    LEARNING = "Learning"
    STREAK = "Streak"
    COMPLETION = "Completion"
    MASTERY = "Mastery"
    TIME = "Time"
    EXPLORATION = "Exploration"
    SPECIAL = "Special"


class AchievementTier(Enum):
    """Achievement tiers indicating difficulty/rarity."""
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    DIAMOND = "Diamond"


@dataclass
class Achievement:
    """Represents a single achievement."""
    id: str
    name: str
    description: str
    badge: str
    category: AchievementCategory
    tier: AchievementTier
    points: int
    unlock_condition: str
    metadata: Dict[str, Any]
    unlocked: bool = False
    unlock_date: Optional[str] = None


class AchievementEngine:
    """Manages achievement system and progress tracking."""
    
    def __init__(self, data_dir: Optional[Path] = None, progress_calculator: Optional['ProgressCalculator'] = None):
        """
        Initialize achievement engine.
        
        Args:
            data_dir: Directory to store achievement data
            progress_calculator: Injected progress calculator instance to avoid circular imports
        """
        self.data_dir = data_dir or Path.home() / '.python_mastery_hub'
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / 'progress.db'
        self.progress_calculator = progress_calculator
        self.achievements = self._define_achievements()
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables for achievements."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User achievements table - only create if it doesn't exist
            # This table schema is shared with progress_calculator
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    badge TEXT,
                    category TEXT,
                    tier TEXT,
                    points INTEGER DEFAULT 0,
                    earned_date TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
    
    def _define_achievements(self) -> Dict[str, Achievement]:
        """Define all available achievements."""
        achievements = {}
        
        # Learning Achievements
        achievements.update(self._learning_achievements())
        
        # Streak Achievements
        achievements.update(self._streak_achievements())
        
        # Completion Achievements
        achievements.update(self._completion_achievements())
        
        # Mastery Achievements
        achievements.update(self._mastery_achievements())
        
        # Time Achievements
        achievements.update(self._time_achievements())
        
        # Exploration Achievements
        achievements.update(self._exploration_achievements())
        
        # Special Achievements
        achievements.update(self._special_achievements())
        
        return achievements
    
    def _learning_achievements(self) -> Dict[str, Achievement]:
        """Define learning-based achievements."""
        return {
            'first_steps': Achievement(
                id='first_steps',
                name='First Steps',
                description='Complete your first Python topic',
                badge='\U0001F476',  # Baby emoji
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.BRONZE,
                points=10,
                unlock_condition='complete_any_topic',
                metadata={'topics_required': 1}
            ),
            'getting_started': Achievement(
                id='getting_started',
                name='Getting Started',
                description='Complete 5 topics in any module',
                badge='\U0001F680',  # Rocket emoji
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.BRONZE,
                points=25,
                unlock_condition='complete_topics_count',
                metadata={'topics_required': 5}
            ),
            'dedicated_learner': Achievement(
                id='dedicated_learner',
                name='Dedicated Learner',
                description='Complete 25 topics across all modules',
                badge='\U0001F4DA',  # Books emoji
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.SILVER,
                points=100,
                unlock_condition='complete_topics_count',
                metadata={'topics_required': 25}
            ),
            'knowledge_seeker': Achievement(
                id='knowledge_seeker',
                name='Knowledge Seeker',
                description='Complete 50 topics across all modules',
                badge='\U0001F50D',  # Magnifying glass emoji
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.GOLD,
                points=250,
                unlock_condition='complete_topics_count',
                metadata={'topics_required': 50}
            ),
            'python_scholar': Achievement(
                id='python_scholar',
                name='Python Scholar',
                description='Complete 100 topics across all modules',
                badge='\U0001F393',  # Graduation cap emoji
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.PLATINUM,
                points=500,
                unlock_condition='complete_topics_count',
                metadata={'topics_required': 100}
            )
        }
    
    def _streak_achievements(self) -> Dict[str, Achievement]:
        """Define streak-based achievements."""
        return {
            'daily_habit': Achievement(
                id='daily_habit',
                name='Daily Habit',
                description='Maintain a 3-day learning streak',
                badge='\U0001F525',  # Fire emoji
                category=AchievementCategory.STREAK,
                tier=AchievementTier.BRONZE,
                points=30,
                unlock_condition='learning_streak',
                metadata={'streak_days': 3}
            ),
            'week_warrior': Achievement(
                id='week_warrior',
                name='Week Warrior',
                description='Maintain a 7-day learning streak',
                badge='\U0001F4AA',  # Flexed biceps emoji
                category=AchievementCategory.STREAK,
                tier=AchievementTier.SILVER,
                points=75,
                unlock_condition='learning_streak',
                metadata={'streak_days': 7}
            ),
            'month_master': Achievement(
                id='month_master',
                name='Month Master',
                description='Maintain a 30-day learning streak',
                badge='\U0001F3C6',  # Trophy emoji
                category=AchievementCategory.STREAK,
                tier=AchievementTier.GOLD,
                points=300,
                unlock_condition='learning_streak',
                metadata={'streak_days': 30}
            ),
            'unstoppable': Achievement(
                id='unstoppable',
                name='Unstoppable',
                description='Maintain a 100-day learning streak',
                badge='\U000026A1',  # High voltage emoji
                category=AchievementCategory.STREAK,
                tier=AchievementTier.PLATINUM,
                points=1000,
                unlock_condition='learning_streak',
                metadata={'streak_days': 100}
            )
        }
    
    def _completion_achievements(self) -> Dict[str, Achievement]:
        """Define module completion achievements."""
        modules = ['basics', 'oop', 'advanced', 'data_structures', 'algorithms', 
                  'async', 'web', 'data_science', 'testing']
        
        achievements = {}
        
        for module in modules:
            module_name = module.replace('_', ' ').title()
            achievements[f'{module}_complete'] = Achievement(
                id=f'{module}_complete',
                name=f'{module_name} Master',
                description=f'Complete all topics in {module_name}',
                badge='\U00002705',  # White heavy check mark emoji
                category=AchievementCategory.COMPLETION,
                tier=AchievementTier.SILVER,
                points=150,
                unlock_condition='complete_module',
                metadata={'module_id': module}
            )
        
        # Multi-module achievements
        achievements.update({
            'foundation_builder': Achievement(
                id='foundation_builder',
                name='Foundation Builder',
                description='Complete Basics and OOP modules',
                badge='\U0001F3D7',  # Building construction emoji
                category=AchievementCategory.COMPLETION,
                tier=AchievementTier.GOLD,
                points=350,
                unlock_condition='complete_modules',
                metadata={'modules_required': ['basics', 'oop']}
            ),
            'advanced_practitioner': Achievement(
                id='advanced_practitioner',
                name='Advanced Practitioner',
                description='Complete Advanced and Data Structures modules',
                badge='\U0001F9E0',  # Brain emoji
                category=AchievementCategory.COMPLETION,
                tier=AchievementTier.GOLD,
                points=400,
                unlock_condition='complete_modules',
                metadata={'modules_required': ['advanced', 'data_structures']}
            ),
            'full_stack_pythonista': Achievement(
                id='full_stack_pythonista',
                name='Full Stack Pythonista',
                description='Complete Web Development and Data Science modules',
                badge='\U0001F310',  # Globe with meridians emoji
                category=AchievementCategory.COMPLETION,
                tier=AchievementTier.PLATINUM,
                points=600,
                unlock_condition='complete_modules',
                metadata={'modules_required': ['web', 'data_science']}
            ),
            'python_master': Achievement(
                id='python_master',
                name='Python Master',
                description='Complete ALL modules in Python Mastery Hub',
                badge='\U0001F451',  # Crown emoji
                category=AchievementCategory.COMPLETION,
                tier=AchievementTier.DIAMOND,
                points=2000,
                unlock_condition='complete_all_modules',
                metadata={'modules_required': modules}
            )
        })
        
        return achievements
    
    def _mastery_achievements(self) -> Dict[str, Achievement]:
        """Define mastery-based achievements."""
        return {
            'perfectionist': Achievement(
                id='perfectionist',
                name='Perfectionist',
                description='Score 100% on 10 different topics',
                badge='\U0001F4AF',  # Hundred points emoji
                category=AchievementCategory.MASTERY,
                tier=AchievementTier.GOLD,
                points=200,
                unlock_condition='perfect_scores',
                metadata={'perfect_scores_required': 10}
            ),
            'quick_learner': Achievement(
                id='quick_learner',
                name='Quick Learner',
                description='Complete 5 topics in under 10 minutes each',
                badge='\U000026A1',  # High voltage emoji
                category=AchievementCategory.MASTERY,
                tier=AchievementTier.SILVER,
                points=150,
                unlock_condition='quick_completion',
                metadata={'topics_required': 5, 'max_minutes': 10}
            ),
            'deep_diver': Achievement(
                id='deep_diver',
                name='Deep Diver',
                description='Spend over 60 minutes on a single topic',
                badge='\U0001F93F',  # Diving mask emoji
                category=AchievementCategory.MASTERY,
                tier=AchievementTier.BRONZE,
                points=50,
                unlock_condition='long_session',
                metadata={'min_minutes': 60}
            )
        }
    
    def _time_achievements(self) -> Dict[str, Achievement]:
        """Define time-based achievements."""
        return {
            'night_owl': Achievement(
                id='night_owl',
                name='Night Owl',
                description='Complete a topic after 10 PM',
                badge='\U0001F989',  # Owl emoji
                category=AchievementCategory.TIME,
                tier=AchievementTier.BRONZE,
                points=25,
                unlock_condition='late_night_learning',
                metadata={'after_hour': 22}
            ),
            'early_bird': Achievement(
                id='early_bird',
                name='Early Bird',
                description='Complete a topic before 6 AM',
                badge='\U0001F426',  # Bird emoji
                category=AchievementCategory.TIME,
                tier=AchievementTier.BRONZE,
                points=25,
                unlock_condition='early_morning_learning',
                metadata={'before_hour': 6}
            ),
            'weekend_warrior': Achievement(
                id='weekend_warrior',
                name='Weekend Warrior',
                description='Complete topics on both Saturday and Sunday',
                badge='\U0001F5E1',  # Dagger emoji
                category=AchievementCategory.TIME,
                tier=AchievementTier.SILVER,
                points=75,
                unlock_condition='weekend_learning',
                metadata={}
            ),
            'time_traveler': Achievement(
                id='time_traveler',
                name='Time Traveler',
                description='Learn for 7 consecutive days across different timezones',
                badge='\U0001F570',  # Mantelpiece clock emoji
                category=AchievementCategory.TIME,
                tier=AchievementTier.GOLD,
                points=200,
                unlock_condition='varied_time_learning',
                metadata={'days_required': 7}
            )
        }
    
    def _exploration_achievements(self) -> Dict[str, Achievement]:
        """Define exploration-based achievements."""
        return {
            'explorer': Achievement(
                id='explorer',
                name='Explorer',
                description='Start learning in 3 different modules',
                badge='\U0001F5FA',  # World map emoji
                category=AchievementCategory.EXPLORATION,
                tier=AchievementTier.BRONZE,
                points=50,
                unlock_condition='explore_modules',
                metadata={'modules_required': 3}
            ),
            'polyglot': Achievement(
                id='polyglot',
                name='Polyglot',
                description='Complete at least one topic in 5 different modules',
                badge='\U0001F310',  # Globe with meridians emoji
                category=AchievementCategory.EXPLORATION,
                tier=AchievementTier.SILVER,
                points=125,
                unlock_condition='diverse_learning',
                metadata={'modules_required': 5, 'topics_per_module': 1}
            ),
            'renaissance_coder': Achievement(
                id='renaissance_coder',
                name='Renaissance Coder',
                description='Complete topics in all 9 modules',
                badge='\U0001F3A8',  # Artist palette emoji
                category=AchievementCategory.EXPLORATION,
                tier=AchievementTier.GOLD,
                points=300,
                unlock_condition='complete_all_module_types',
                metadata={'modules_required': 9}
            )
        }
    
    def _special_achievements(self) -> Dict[str, Achievement]:
        """Define special and hidden achievements."""
        return {
            'first_light': Achievement(
                id='first_light',
                name='First Light',
                description='Complete your first topic on the platform',
                badge='\U0001F305',  # Sunrise emoji
                category=AchievementCategory.SPECIAL,
                tier=AchievementTier.BRONZE,
                points=15,
                unlock_condition='first_topic_ever',
                metadata={}
            ),
            'speed_demon': Achievement(
                id='speed_demon',
                name='Speed Demon',
                description='Complete 10 topics in a single day',
                badge='\U0001F4A8',  # Dashing away emoji
                category=AchievementCategory.SPECIAL,
                tier=AchievementTier.GOLD,
                points=250,
                unlock_condition='topics_in_day',
                metadata={'topics_required': 10, 'days': 1}
            ),
            'marathon_runner': Achievement(
                id='marathon_runner',
                name='Marathon Runner',
                description='Study for 4+ hours in a single session',
                badge='\U0001F3C3',  # Runner emoji
                category=AchievementCategory.SPECIAL,
                tier=AchievementTier.PLATINUM,
                points=400,
                unlock_condition='long_study_session',
                metadata={'min_hours': 4}
            ),
            'comeback_kid': Achievement(
                id='comeback_kid',
                name='Comeback Kid',
                description='Return to learning after a 30+ day break',
                badge='\U0001F3AF',  # Direct hit emoji
                category=AchievementCategory.SPECIAL,
                tier=AchievementTier.SILVER,
                points=100,
                unlock_condition='return_after_break',
                metadata={'break_days': 30}
            )
        }
    
    def check_achievements(self, event_type: str, event_data: Dict[str, Any]) -> List[Achievement]:
        """
        Check if any achievements should be unlocked based on an event.
        
        Args:
            event_type: Type of event (e.g., 'topic_completed', 'streak_updated')
            event_data: Event-specific data
            
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if self.is_achievement_unlocked(achievement.id):
                continue
            
            if self._check_achievement_condition(achievement, event_type, event_data):
                self.unlock_achievement(achievement.id)
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _check_achievement_condition(
        self, 
        achievement: Achievement, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if an achievement condition is met."""
        condition = achievement.unlock_condition
        metadata = achievement.metadata
        
        # Use injected progress calculator if available
        if not self.progress_calculator:
            logger.warning("No progress calculator available for achievement checking")
            return False
        
        if condition == 'complete_any_topic':
            return event_type == 'topic_completed'
        
        elif condition == 'complete_topics_count':
            stats = self.progress_calculator.get_learning_statistics()
            return stats['completed_topics'] >= metadata['topics_required']
        
        elif condition == 'learning_streak':
            streak_info = self.progress_calculator.get_learning_streak()
            return streak_info['current_streak'] >= metadata['streak_days']
        
        elif condition == 'complete_module':
            module_id = metadata['module_id']
            module_progress = self.progress_calculator.get_module_progress(module_id)
            return module_progress and module_progress.get('is_completed', False)
        
        elif condition == 'complete_modules':
            required_modules = metadata['modules_required']
            for module_id in required_modules:
                module_progress = self.progress_calculator.get_module_progress(module_id)
                if not (module_progress and module_progress.get('is_completed', False)):
                    return False
            return True
        
        elif condition == 'complete_all_modules':
            required_modules = metadata['modules_required']
            for module_id in required_modules:
                module_progress = self.progress_calculator.get_module_progress(module_id)
                if not (module_progress and module_progress.get('is_completed', False)):
                    return False
            return True
        
        elif condition == 'first_topic_ever':
            return event_type == 'topic_completed' and event_data.get('is_first_topic', False)
        
        # Add more condition checks as needed...
        
        return False
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """
        Unlock an achievement for the user.
        
        Args:
            achievement_id: ID of achievement to unlock
            
        Returns:
            True if achievement was unlocked, False if already unlocked
        """
        if self.is_achievement_unlocked(achievement_id):
            return False
        
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            logger.warning(f"Unknown achievement ID: {achievement_id}")
            return False
        
        unlock_date = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_achievements 
                (achievement_id, name, description, badge, category, tier, points, earned_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                achievement.id,
                achievement.name,
                achievement.description,
                achievement.badge,
                achievement.category.value,
                achievement.tier.value,
                achievement.points,
                unlock_date,
                json.dumps(achievement.metadata)
            ))
            
            conn.commit()
        
        logger.info(f"Achievement unlocked: {achievement.name}")
        return True
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Check if an achievement is already unlocked."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 1 FROM user_achievements WHERE achievement_id = ?
            ''', (achievement_id,))
            
            return cursor.fetchone() is not None
    
    def get_user_achievements(self) -> List[Dict[str, Any]]:
        """Get all unlocked achievements for the user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT achievement_id, name, description, badge, category, tier, 
                       points, earned_date, metadata
                FROM user_achievements
                ORDER BY earned_date DESC
            ''')
            
            achievements = []
            for row in cursor.fetchall():
                achievement_data = {
                    'achievement_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'badge': row[3],
                    'category': row[4],
                    'tier': row[5],
                    'points': row[6],
                    'earned_date': row[7],
                    'metadata': json.loads(row[8]) if row[8] else {}
                }
                achievements.append(achievement_data)
            
            return achievements
    
    def get_recent_achievements(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get achievements unlocked in the last N days."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT achievement_id, name, description, badge, category, tier, 
                       points, earned_date, metadata
                FROM user_achievements
                WHERE earned_date >= ?
                ORDER BY earned_date DESC
            ''', (cutoff_date,))
            
            achievements = []
            for row in cursor.fetchall():
                achievement_data = {
                    'achievement_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'badge': row[3],
                    'category': row[4],
                    'tier': row[5],
                    'points': row[6],
                    'earned_date': row[7],
                    'metadata': json.loads(row[8]) if row[8] else {}
                }
                achievements.append(achievement_data)
            
            return achievements
    
    def get_achievement_progress(self, achievement_id: str) -> Dict[str, Any]:
        """Get progress towards a specific achievement."""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return {}
        
        if self.is_achievement_unlocked(achievement_id):
            return {
                'unlocked': True,
                'progress': 1.0,
                'current': achievement.metadata.get('target', 1),
                'target': achievement.metadata.get('target', 1)
            }
        
        # Calculate progress based on achievement type
        # This would need to be implemented for each achievement type
        # For now, return basic structure
        return {
            'unlocked': False,
            'progress': 0.0,
            'current': 0,
            'target': achievement.metadata.get('target', 1)
        }
    
    def get_total_points(self) -> int:
        """Get total achievement points earned by user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT SUM(points) FROM user_achievements')
            result = cursor.fetchone()
            
            return result[0] if result and result[0] else 0
    
    def get_achievement_statistics(self) -> Dict[str, Any]:
        """Get achievement statistics."""
        total_achievements = len(self.achievements)
        unlocked_count = len(self.get_user_achievements())
        total_points = self.get_total_points()
        
        # Count by category
        category_stats = {}
        for achievement in self.achievements.values():
            category = achievement.category.value
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'unlocked': 0}
            category_stats[category]['total'] += 1
        
        for user_achievement in self.get_user_achievements():
            category = user_achievement['category']
            if category in category_stats:
                category_stats[category]['unlocked'] += 1
        
        return {
            'total_achievements': total_achievements,
            'unlocked_achievements': unlocked_count,
            'completion_percentage': (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0,
            'total_points': total_points,
            'category_stats': category_stats
        }