# File: migrations/versions/003_add_progress_tracking.py

"""Add progress tracking tables

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add progress tracking tables."""
    
    # Create enum types for progress tracking
    op.execute("CREATE TYPE completion_status AS ENUM ('not_started', 'in_progress', 'completed', 'skipped')")
    op.execute("CREATE TYPE activity_type AS ENUM ('lesson_start', 'lesson_complete', 'exercise_attempt', 'exercise_complete', 'quiz_attempt', 'quiz_complete', 'module_complete', 'course_complete', 'streak_achieved', 'goal_reached')")
    
    # Create user_course_enrollments table
    op.create_table(
        'user_course_enrollments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('status', postgresql.ENUM('not_started', 'in_progress', 'completed', 'skipped', name='completion_status'), nullable=False, default='not_started'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'course_id')
    )
    
    # Create user_module_progress table
    op.create_table(
        'user_module_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('status', postgresql.ENUM('not_started', 'in_progress', 'completed', 'skipped', name='completion_status'), nullable=False, default='not_started'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['enrollment_id'], ['user_course_enrollments.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'module_id')
    )
    
    # Create user_lesson_progress table
    op.create_table(
        'user_lesson_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('module_progress_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('status', postgresql.ENUM('not_started', 'in_progress', 'completed', 'skipped', name='completion_status'), nullable=False, default='not_started'),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('bookmarked', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_progress_id'], ['user_module_progress.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'lesson_id')
    )
    
    # Create user_activity_log table
    op.create_table(
        'user_activity_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', postgresql.ENUM('lesson_start', 'lesson_complete', 'exercise_attempt', 'exercise_complete', 'quiz_attempt', 'quiz_complete', 'module_complete', 'course_complete', 'streak_achieved', 'goal_reached', name='activity_type'), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('exercise_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='SET NULL')
    )
    
    # Create user_learning_streaks table
    op.create_table(
        'user_learning_streaks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('longest_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
        sa.Column('streak_start_date', sa.Date(), nullable=True),
        sa.Column('total_active_days', sa.Integer(), nullable=False, default=0),
        sa.Column('total_points', sa.Integer(), nullable=False, default=0),
        sa.Column('weekly_goal_minutes', sa.Integer(), nullable=False, default=210),  # 30 minutes * 7 days
        sa.Column('current_week_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('week_start_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create user_daily_goals table
    op.create_table(
        'user_daily_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('goal_minutes', sa.Integer(), nullable=False, default=30),
        sa.Column('actual_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('goal_achieved', sa.Boolean(), nullable=False, default=False),
        sa.Column('lessons_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('exercises_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('points_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'date')
    )
    
    # Create indexes for performance
    op.create_index('idx_user_course_enrollments_user', 'user_course_enrollments', ['user_id'])
    op.create_index('idx_user_course_enrollments_course', 'user_course_enrollments', ['course_id'])
    op.create_index('idx_user_course_enrollments_status', 'user_course_enrollments', ['status'])
    op.create_index('idx_user_module_progress_user', 'user_module_progress', ['user_id'])
    op.create_index('idx_user_module_progress_module', 'user_module_progress', ['module_id'])
    op.create_index('idx_user_module_progress_enrollment', 'user_module_progress', ['enrollment_id'])
    op.create_index('idx_user_lesson_progress_user', 'user_lesson_progress', ['user_id'])
    op.create_index('idx_user_lesson_progress_lesson', 'user_lesson_progress', ['lesson_id'])
    op.create_index('idx_user_lesson_progress_module', 'user_lesson_progress', ['module_progress_id'])
    op.create_index('idx_user_lesson_progress_bookmarked', 'user_lesson_progress', ['user_id', 'bookmarked'])
    op.create_index('idx_user_activity_log_user', 'user_activity_log', ['user_id'])
    op.create_index('idx_user_activity_log_created', 'user_activity_log', ['created_at'])
    op.create_index('idx_user_activity_log_type', 'user_activity_log', ['activity_type'])
    op.create_index('idx_user_learning_streaks_user', 'user_learning_streaks', ['user_id'])
    op.create_index('idx_user_daily_goals_user_date', 'user_daily_goals', ['user_id', 'date'])
    op.create_index('idx_user_daily_goals_date', 'user_daily_goals', ['date'])


def downgrade() -> None:
    """Drop progress tracking tables."""
    
    # Drop tables in reverse order
    op.drop_table('user_daily_goals')
    op.drop_table('user_learning_streaks')
    op.drop_table('user_activity_log')
    op.drop_table('user_lesson_progress')
    op.drop_table('user_module_progress')
    op.drop_table('user_course_enrollments')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS activity_type")
    op.execute("DROP TYPE IF EXISTS completion_status")