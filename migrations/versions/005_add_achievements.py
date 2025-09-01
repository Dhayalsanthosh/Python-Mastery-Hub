# File: migrations/versions/005_add_achievements.py

"""Add achievements and gamification tables

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add achievements and gamification tables."""
    
    # Create enum types for achievements
    op.execute("CREATE TYPE achievement_category AS ENUM ('learning', 'consistency', 'mastery', 'social', 'milestone', 'special')")
    op.execute("CREATE TYPE badge_tier AS ENUM ('bronze', 'silver', 'gold', 'platinum', 'diamond')")
    op.execute("CREATE TYPE notification_type AS ENUM ('achievement_unlocked', 'streak_milestone', 'course_complete', 'level_up', 'reminder', 'announcement')")
    
    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', postgresql.ENUM('learning', 'consistency', 'mastery', 'social', 'milestone', 'special', name='achievement_category'), nullable=False),
        sa.Column('tier', postgresql.ENUM('bronze', 'silver', 'gold', 'platinum', 'diamond', name='badge_tier'), nullable=False),
        sa.Column('icon_name', sa.String(100), nullable=False),
        sa.Column('icon_color', sa.String(20), nullable=False, default='#3B82F6'),
        sa.Column('points_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('criteria', sa.JSON(), nullable=False),  # Conditions to earn this achievement
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, default=False),  # Hidden until unlocked
        sa.Column('unlock_message', sa.String(500), nullable=True),
        sa.Column('rarity_percentage', sa.Float(), nullable=True),  # What % of users have this
        sa.Column('prerequisites', sa.JSON(), nullable=True),  # Required achievements
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('progress_data', sa.JSON(), nullable=True),  # Data used to unlock this achievement
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),  # Show on profile
        sa.Column('notification_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'achievement_id')
    )
    
    # Create user_levels table
    op.create_table(
        'user_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('current_level', sa.Integer(), nullable=False, default=1),
        sa.Column('current_xp', sa.Integer(), nullable=False, default=0),
        sa.Column('total_xp', sa.Integer(), nullable=False, default=0),
        sa.Column('xp_to_next_level', sa.Integer(), nullable=False, default=100),
        sa.Column('level_up_count', sa.Integer(), nullable=False, default=0),
        sa.Column('highest_level_reached', sa.Integer(), nullable=False, default=1),
        sa.Column('last_level_up_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create leaderboards table
    op.create_table(
        'leaderboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leaderboard_type', sa.String(50), nullable=False),  # daily, weekly, monthly, all_time
        sa.Column('metric_type', sa.String(50), nullable=False),  # xp, streak, course_completions, etc.
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('rewards', sa.JSON(), nullable=True),  # Rewards for top performers
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'leaderboard_type', 'start_date')
    )
    
    # Create leaderboard_entries table
    op.create_table(
        'leaderboard_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('leaderboard_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, default=0.0),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('previous_rank', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),  # Additional data for ranking
        sa.Column('last_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['leaderboard_id'], ['leaderboards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('leaderboard_id', 'user_id')
    )
    
    # Create user_notifications table
    op.create_table(
        'user_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', postgresql.ENUM('achievement_unlocked', 'streak_milestone', 'course_complete', 'level_up', 'reminder', 'announcement', name='notification_type'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create challenges table
    op.create_table(
        'challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('challenge_type', sa.String(50), nullable=False),  # daily, weekly, monthly, special
        sa.Column('difficulty', postgresql.ENUM('beginner', 'intermediate', 'advanced', name='difficulty_level'), nullable=False),
        sa.Column('objectives', sa.JSON(), nullable=False),  # List of objectives to complete
        sa.Column('rewards', sa.JSON(), nullable=True),  # XP, achievements, etc.
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create user_challenges table
    op.create_table(
        'user_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress', sa.JSON(), nullable=True),  # Progress on each objective
        sa.Column('progress_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('rewards_claimed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'challenge_id')
    )
    
    # Create user_social_stats table
    op.create_table(
        'user_social_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('followers_count', sa.Integer(), nullable=False, default=0),
        sa.Column('following_count', sa.Integer(), nullable=False, default=0),
        sa.Column('study_buddy_count', sa.Integer(), nullable=False, default=0),
        sa.Column('solutions_shared', sa.Integer(), nullable=False, default=0),
        sa.Column('helpful_feedback_given', sa.Integer(), nullable=False, default=0),
        sa.Column('helpful_feedback_received', sa.Integer(), nullable=False, default=0),
        sa.Column('forum_posts', sa.Integer(), nullable=False, default=0),
        sa.Column('forum_likes_received', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_achievements_category', 'achievements', ['category'])
    op.create_index('idx_achievements_tier', 'achievements', ['tier'])
    op.create_index('idx_achievements_active', 'achievements', ['is_active'])
    op.create_index('idx_user_achievements_user', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_achievement', 'user_achievements', ['achievement_id'])
    op.create_index('idx_user_achievements_unlocked', 'user_achievements', ['unlocked_at'])
    op.create_index('idx_user_achievements_featured', 'user_achievements', ['user_id', 'is_featured'])
    op.create_index('idx_user_levels_user', 'user_levels', ['user_id'])
    op.create_index('idx_user_levels_level', 'user_levels', ['current_level'])
    op.create_index('idx_leaderboards_type_active', 'leaderboards', ['leaderboard_type', 'is_active'])
    op.create_index('idx_leaderboard_entries_leaderboard_rank', 'leaderboard_entries', ['leaderboard_id', 'rank'])
    op.create_index('idx_leaderboard_entries_user', 'leaderboard_entries', ['user_id'])
    op.create_index('idx_user_notifications_user', 'user_notifications', ['user_id'])
    op.create_index('idx_user_notifications_type', 'user_notifications', ['notification_type'])
    op.create_index('idx_user_notifications_unread', 'user_notifications', ['user_id', 'is_read'])
    op.create_index('idx_user_notifications_created', 'user_notifications', ['created_at'])
    op.create_index('idx_challenges_active', 'challenges', ['is_active'])
    op.create_index('idx_challenges_dates', 'challenges', ['start_date', 'end_date'])
    op.create_index('idx_challenges_featured', 'challenges', ['is_featured'])
    op.create_index('idx_user_challenges_user', 'user_challenges', ['user_id'])
    op.create_index('idx_user_challenges_challenge', 'user_challenges', ['challenge_id'])
    op.create_index('idx_user_challenges_completed', 'user_challenges', ['completed_at'])
    op.create_index('idx_user_social_stats_user', 'user_social_stats', ['user_id'])


def downgrade() -> None:
    """Drop achievements and gamification tables."""
    
    # Drop tables in reverse order
    op.drop_table('user_social_stats')
    op.drop_table('user_challenges')
    op.drop_table('challenges')
    op.drop_table('user_notifications')
    op.drop_table('leaderboard_entries')
    op.drop_table('leaderboards')
    op.drop_table('user_levels')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS badge_tier")
    op.execute("DROP TYPE IF EXISTS achievement_category")