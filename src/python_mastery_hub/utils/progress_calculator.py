# src/python_mastery_hub/utils/progress_calculator.py
"""
Progress Calculator - Learning Progress Tracking and Analytics

Manages user progress data, calculates statistics, and provides progress tracking
functionality across all learning modules and topics.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass, asdict
import logging

# Avoid circular imports
if TYPE_CHECKING:
    from .achievement_engine import AchievementEngine

logger = logging.getLogger(__name__)


@dataclass
class TopicProgress:
    """Represents progress for a single topic."""
    module_id: str
    topic_name: str
    completed: bool = False
    completion_date: Optional[str] = None
    time_spent: int = 0  # minutes
    attempts: int = 0
    score: Optional[float] = None


@dataclass
class ModuleProgress:
    """Represents progress for an entire module."""
    module_id: str
    module_name: str
    topics_completed: int = 0
    topics_total: int = 0
    percentage: float = 0.0
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    total_time_spent: int = 0  # minutes


@dataclass
class LearningSession:
    """Represents a single learning session."""
    session_id: str
    module_id: str
    topic_name: str
    start_time: str
    end_time: Optional[str] = None
    duration: int = 0  # minutes
    completed: bool = False


class ProgressCalculator:
    """Manages learning progress calculation and persistence."""
    
    def __init__(self, data_dir: Optional[Path] = None, achievement_engine: Optional['AchievementEngine'] = None):
        """
        Initialize progress calculator.
        
        Args:
            data_dir: Directory to store progress data (default: ~/.python_mastery_hub)
            achievement_engine: Optional achievement engine for progress-based rewards
        """
        self.data_dir = data_dir or Path.home() / '.python_mastery_hub'
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / 'progress.db'
        self.achievement_engine = achievement_engine
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for progress tracking."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Topics progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    completion_date TEXT,
                    time_spent INTEGER DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(module_id, topic_name)
                )
            ''')
            
            # Learning sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    module_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User achievements table - shared with achievement_engine
            # This ensures both modules can work with the same table
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
    
    def get_module_progress(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress for a specific module.
        
        Args:
            module_id: Module identifier
            
        Returns:
            Dictionary with progress information or None if no progress
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_topics,
                    SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_topics,
                    SUM(time_spent) as total_time,
                    MIN(created_at) as start_date,
                    MAX(CASE WHEN completed = 1 THEN completion_date END) as last_completion
                FROM topic_progress 
                WHERE module_id = ?
            ''', (module_id,))
            
            row = cursor.fetchone()
            if not row or row[0] == 0:
                return None
            
            total_topics, completed_topics, total_time, start_date, last_completion = row
            percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0
            
            return {
                'module_id': module_id,
                'completed': completed_topics or 0,
                'total': total_topics,
                'percentage': percentage,
                'total_time_minutes': total_time or 0,
                'start_date': start_date,
                'last_completion': last_completion,
                'is_completed': completed_topics == total_topics and total_topics > 0
            }
    
    def is_topic_completed(self, module_id: str, topic_name: str) -> bool:
        """
        Check if a specific topic is completed.
        
        Args:
            module_id: Module identifier
            topic_name: Topic name
            
        Returns:
            True if topic is completed, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT completed FROM topic_progress 
                WHERE module_id = ? AND topic_name = ?
            ''', (module_id, topic_name))
            
            row = cursor.fetchone()
            return bool(row and row[0])
    
    def mark_topic_completed(
        self, 
        module_id: str, 
        topic_name: str, 
        score: Optional[float] = None,
        time_spent: int = 0
    ) -> None:
        """
        Mark a topic as completed.
        
        Args:
            module_id: Module identifier
            topic_name: Topic name
            score: Optional score (0.0 - 1.0)
            time_spent: Time spent in minutes
        """
        completion_date = datetime.now().isoformat()
        
        # Check if this is the user's first topic ever
        stats = self.get_learning_statistics()
        is_first_topic = stats['completed_topics'] == 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert or update topic progress
            cursor.execute('''
                INSERT INTO topic_progress 
                (module_id, topic_name, completed, completion_date, score, time_spent, attempts, updated_at)
                VALUES (?, ?, 1, ?, ?, ?, 1, ?)
                ON CONFLICT(module_id, topic_name) DO UPDATE SET
                    completed = 1,
                    completion_date = ?,
                    score = COALESCE(?, score),
                    time_spent = time_spent + ?,
                    attempts = attempts + 1,
                    updated_at = ?
            ''', (
                module_id, topic_name, completion_date, score, time_spent, completion_date,
                completion_date, score, time_spent, completion_date
            ))
            
            conn.commit()
        
        logger.info(f"Marked topic completed: {module_id}.{topic_name}")
        
        # Check for achievements if achievement engine is available
        if self.achievement_engine:
            self._check_achievements(module_id, topic_name, is_first_topic)
    
    def get_topic_completion_date(self, module_id: str, topic_name: str) -> Optional[str]:
        """Get the completion date for a topic."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT completion_date FROM topic_progress 
                WHERE module_id = ? AND topic_name = ? AND completed = 1
            ''', (module_id, topic_name))
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Basic statistics
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT module_id) as modules_started,
                    COUNT(*) as total_topics,
                    SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_topics,
                    SUM(time_spent) as total_time,
                    AVG(score) as avg_score
                FROM topic_progress
            ''')
            
            basic_stats = cursor.fetchone()
            
            # Time-based statistics
            streak_info = self.get_learning_streak()
            weekly_activity = self._get_weekly_activity()
            
            # Module statistics
            cursor.execute('''
                SELECT 
                    module_id,
                    COUNT(*) as total_topics,
                    SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_topics,
                    SUM(time_spent) as time_spent
                FROM topic_progress
                GROUP BY module_id
            ''')
            
            module_stats = {}
            for row in cursor.fetchall():
                module_id, total, completed, time_spent = row
                module_stats[module_id] = {
                    'total': total,
                    'completed': completed,
                    'time_spent': time_spent or 0,
                    'percentage': (completed / total * 100) if total > 0 else 0
                }
            
            return {
                'modules_started': basic_stats[0] or 0,
                'total_topics': basic_stats[1] or 0,
                'completed_topics': basic_stats[2] or 0,
                'total_time_minutes': basic_stats[3] or 0,
                'average_score': basic_stats[4] or 0,
                'current_streak': streak_info.get('current_streak', 0),
                'longest_streak': streak_info.get('longest_streak', 0),
                'total_days': streak_info.get('total_days', 0),
                'avg_daily_progress': self._calculate_avg_daily_progress(),
                'weekly_activity': weekly_activity,
                'module_stats': module_stats
            }
    
    def get_learning_streak(self) -> Dict[str, Any]:
        """Calculate learning streak information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all completion dates
            cursor.execute('''
                SELECT DISTINCT DATE(completion_date) as completion_date
                FROM topic_progress 
                WHERE completed = 1 AND completion_date IS NOT NULL
                ORDER BY completion_date DESC
            ''')
            
            dates = [row[0] for row in cursor.fetchall()]
            
            if not dates:
                return {
                    'current_streak': 0,
                    'longest_streak': 0,
                    'total_days': 0,
                    'last_activity': None
                }
            
            # Calculate streaks
            current_streak = 0
            longest_streak = 0
            temp_streak = 1
            
            today = datetime.now().date()
            last_date = datetime.fromisoformat(dates[0]).date()
            
            # Check if we have activity today or yesterday
            if last_date == today or last_date == today - timedelta(days=1):
                current_streak = 1
                
                # Count consecutive days backward
                for i in range(1, len(dates)):
                    current_date = datetime.fromisoformat(dates[i]).date()
                    prev_date = datetime.fromisoformat(dates[i-1]).date()
                    
                    if (prev_date - current_date).days == 1:
                        current_streak += 1
                    else:
                        break
            
            # Calculate longest streak
            for i in range(len(dates)):
                if i == 0:
                    temp_streak = 1
                else:
                    current_date = datetime.fromisoformat(dates[i]).date()
                    prev_date = datetime.fromisoformat(dates[i-1]).date()
                    
                    if (prev_date - current_date).days == 1:
                        temp_streak += 1
                    else:
                        longest_streak = max(longest_streak, temp_streak)
                        temp_streak = 1
            
            longest_streak = max(longest_streak, temp_streak)
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'total_days': len(dates),
                'last_activity': dates[0] if dates else None
            }
    
    def _get_weekly_activity(self) -> Dict[str, int]:
        """Get activity for each day of the week."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    CASE CAST(strftime('%w', completion_date) AS INTEGER)
                        WHEN 0 THEN 'sun'
                        WHEN 1 THEN 'mon'
                        WHEN 2 THEN 'tue'
                        WHEN 3 THEN 'wed'
                        WHEN 4 THEN 'thu'
                        WHEN 5 THEN 'fri'
                        WHEN 6 THEN 'sat'
                    END as day_of_week,
                    COUNT(*) as activity_count
                FROM topic_progress 
                WHERE completed = 1 AND completion_date IS NOT NULL
                    AND completion_date >= date('now', '-30 days')
                GROUP BY day_of_week
            ''')
            
            activity = {day: 0 for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']}
            for row in cursor.fetchall():
                if row[0]:  # day_of_week is not None
                    activity[row[0]] = row[1]
            
            return activity
    
    def _calculate_avg_daily_progress(self) -> float:
        """Calculate average daily progress."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(completion_date) as completion_date,
                    COUNT(*) as daily_topics
                FROM topic_progress 
                WHERE completed = 1 AND completion_date IS NOT NULL
                GROUP BY DATE(completion_date)
            ''')
            
            daily_counts = [row[1] for row in cursor.fetchall()]
            
            if not daily_counts:
                return 0.0
            
            return sum(daily_counts) / len(daily_counts)
    
    def _check_achievements(self, module_id: str, topic_name: str, is_first_topic: bool = False) -> None:
        """Check and award achievements based on progress."""
        if not self.achievement_engine:
            return
        
        # Prepare event data for achievement checking
        event_data = {
            'module_id': module_id,
            'topic_name': topic_name,
            'is_first_topic': is_first_topic
        }
        
        # Check for new achievements
        try:
            new_achievements = self.achievement_engine.check_achievements('topic_completed', event_data)
            if new_achievements:
                logger.info(f"Unlocked {len(new_achievements)} new achievements")
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
    
    def reset_module_progress(self, module_id: str) -> None:
        """Reset progress for a specific module."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM topic_progress WHERE module_id = ?', (module_id,))
            cursor.execute('DELETE FROM learning_sessions WHERE module_id = ?', (module_id,))
            
            conn.commit()
        
        logger.info(f"Reset progress for module: {module_id}")
    
    def reset_all_progress(self) -> None:
        """Reset all user progress."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM topic_progress')
            cursor.execute('DELETE FROM learning_sessions')
            cursor.execute('DELETE FROM user_achievements')
            
            conn.commit()
        
        logger.info("Reset all user progress")
    
    def start_learning_session(self, module_id: str, topic_name: str) -> str:
        """Start a new learning session."""
        session_id = f"{module_id}_{topic_name}_{datetime.now().timestamp()}"
        start_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_sessions 
                (session_id, module_id, topic_name, start_time)
                VALUES (?, ?, ?, ?)
            ''', (session_id, module_id, topic_name, start_time))
            
            conn.commit()
        
        return session_id
    
    def end_learning_session(self, session_id: str, completed: bool = False) -> None:
        """End a learning session."""
        end_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get session start time to calculate duration
            cursor.execute('''
                SELECT start_time FROM learning_sessions WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if row:
                start_time = datetime.fromisoformat(row[0])
                duration = int((datetime.now() - start_time).total_seconds() / 60)
                
                cursor.execute('''
                    UPDATE learning_sessions 
                    SET end_time = ?, duration = ?, completed = ?
                    WHERE session_id = ?
                ''', (end_time, duration, completed, session_id))
                
                conn.commit()
    
    def get_user_setting(self, key: str, default: Any = None) -> Any:
        """Get a user setting value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM user_settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return row[0]
            
            return default
    
    def set_user_setting(self, key: str, value: Any) -> None:
        """Set a user setting value."""
        if not isinstance(value, str):
            value = json.dumps(value)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = ?,
                    updated_at = ?
            ''', (key, value, datetime.now().isoformat(), value, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_topics_by_module(self, module_id: str) -> List[TopicProgress]:
        """Get all topics for a specific module."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT module_id, topic_name, completed, completion_date, 
                       time_spent, attempts, score
                FROM topic_progress 
                WHERE module_id = ?
                ORDER BY created_at
            ''', (module_id,))
            
            topics = []
            for row in cursor.fetchall():
                topic = TopicProgress(
                    module_id=row[0],
                    topic_name=row[1],
                    completed=bool(row[2]),
                    completion_date=row[3],
                    time_spent=row[4] or 0,
                    attempts=row[5] or 0,
                    score=row[6]
                )
                topics.append(topic)
            
            return topics
    
    def get_learning_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent learning activity history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT module_id, topic_name, completion_date, time_spent, score
                FROM topic_progress 
                WHERE completed = 1 AND completion_date IS NOT NULL
                ORDER BY completion_date DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                entry = {
                    'module_id': row[0],
                    'topic_name': row[1],
                    'completion_date': row[2],
                    'time_spent': row[3] or 0,
                    'score': row[4],
                    'action': 'completed'
                }
                history.append(entry)
            
            return history