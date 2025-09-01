# File: migrations/versions/001_initial_schema.py

"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create enum types
    op.execute("CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced')")
    op.execute("CREATE TYPE content_type AS ENUM ('lesson', 'exercise', 'quiz', 'project')")
    op.execute("CREATE TYPE submission_status AS ENUM ('pending', 'passed', 'failed', 'reviewed')")
    
    # Create courses table
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('difficulty', postgresql.ENUM('beginner', 'intermediate', 'advanced', name='difficulty_level'), nullable=False),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('prerequisites', sa.Text(), nullable=True),
        sa.Column('learning_objectives', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title')
    )
    
    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('course_id', 'title')
    )
    
    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', postgresql.ENUM('lesson', 'exercise', 'quiz', 'project', name='content_type'), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True),
        sa.Column('difficulty', postgresql.ENUM('beginner', 'intermediate', 'advanced', name='difficulty_level'), nullable=False),
        sa.Column('learning_objectives', sa.Text(), nullable=True),
        sa.Column('prerequisites', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('module_id', 'title')
    )
    
    # Create exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=False),
        sa.Column('starter_code', sa.Text(), nullable=True),
        sa.Column('solution_code', sa.Text(), nullable=True),
        sa.Column('test_cases', sa.JSON(), nullable=True),
        sa.Column('hints', sa.JSON(), nullable=True),
        sa.Column('difficulty', postgresql.ENUM('beginner', 'intermediate', 'advanced', name='difficulty_level'), nullable=False),
        sa.Column('max_attempts', sa.Integer(), nullable=True, default=3),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('lesson_id', 'title')
    )
    
    # Create indexes for performance
    op.create_index('idx_courses_difficulty', 'courses', ['difficulty'])
    op.create_index('idx_courses_active', 'courses', ['is_active'])
    op.create_index('idx_modules_course_order', 'modules', ['course_id', 'order_index'])
    op.create_index('idx_lessons_module_order', 'lessons', ['module_id', 'order_index'])
    op.create_index('idx_lessons_content_type', 'lessons', ['content_type'])
    op.create_index('idx_exercises_lesson', 'exercises', ['lesson_id'])
    op.create_index('idx_exercises_difficulty', 'exercises', ['difficulty'])


def downgrade() -> None:
    """Drop initial database schema."""
    
    # Drop tables in reverse order
    op.drop_table('exercises')
    op.drop_table('lessons')
    op.drop_table('modules')
    op.drop_table('courses')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS submission_status")
    op.execute("DROP TYPE IF EXISTS content_type")
    op.execute("DROP TYPE IF EXISTS difficulty_level")