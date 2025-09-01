# File: migrations/versions/002_add_user_tables.py

"""Add user tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add user-related tables."""
    
    # Create enum types for users
    op.execute("CREATE TYPE user_role AS ENUM ('student', 'instructor', 'admin')")
    op.execute("CREATE TYPE auth_provider AS ENUM ('local', 'google', 'github', 'discord')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('role', postgresql.ENUM('student', 'instructor', 'admin', name='user_role'), nullable=False, default='student'),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('github_username', sa.String(100), nullable=True),
        sa.Column('discord_username', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=True, default='UTC'),
        sa.Column('preferred_language', sa.String(10), nullable=True, default='en'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create user_auth_providers table for OAuth providers
    op.create_table(
        'user_auth_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', postgresql.ENUM('local', 'google', 'github', 'discord', name='auth_provider'), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('provider_username', sa.String(255), nullable=True),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('provider', 'provider_user_id')
    )
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(20), nullable=False, default='light'),
        sa.Column('code_editor_theme', sa.String(50), nullable=False, default='vs-code'),
        sa.Column('font_size', sa.Integer(), nullable=False, default=14),
        sa.Column('show_line_numbers', sa.Boolean(), nullable=False, default=True),
        sa.Column('auto_save', sa.Boolean(), nullable=False, default=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, default=True),
        sa.Column('daily_goal_minutes', sa.Integer(), nullable=False, default=30),
        sa.Column('preferred_difficulty', postgresql.ENUM('beginner', 'intermediate', 'advanced', name='difficulty_level'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token')
    )
    
    # Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token')
    )
    
    # Create indexes for performance
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_active', 'users', ['is_active'])
    op.create_index('idx_user_auth_providers_user', 'user_auth_providers', ['user_id'])
    op.create_index('idx_user_auth_providers_provider', 'user_auth_providers', ['provider', 'provider_user_id'])
    op.create_index('idx_user_sessions_user', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_expires', 'user_sessions', ['expires_at'])
    op.create_index('idx_password_reset_tokens_user', 'password_reset_tokens', ['user_id'])
    op.create_index('idx_password_reset_tokens_token', 'password_reset_tokens', ['token'])
    op.create_index('idx_email_verification_tokens_user', 'email_verification_tokens', ['user_id'])
    op.create_index('idx_email_verification_tokens_token', 'email_verification_tokens', ['token'])


def downgrade() -> None:
    """Drop user-related tables."""
    
    # Drop tables in reverse order
    op.drop_table('email_verification_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('user_sessions')
    op.drop_table('user_preferences')
    op.drop_table('user_auth_providers')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS auth_provider")
    op.execute("DROP TYPE IF EXISTS user_role")