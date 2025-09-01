# File: migrations/versions/004_add_exercise_submissions.py

"""Add exercise submissions tables

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add exercise submission tables."""
    
    # Create enum types for submissions
    op.execute("CREATE TYPE test_result_status AS ENUM ('passed', 'failed', 'error', 'timeout')")
    op.execute("CREATE TYPE feedback_type AS ENUM ('automated', 'instructor', 'peer')")
    op.execute("CREATE TYPE code_quality_metric AS ENUM ('readability', 'efficiency', 'best_practices', 'maintainability')")
    
    # Create exercise_submissions table
    op.create_table(
        'exercise_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('lesson_progress_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'passed', 'failed', 'reviewed', name='submission_status'), nullable=False, default='pending'),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=False, default=100.0),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('test_results', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('compiler_output', sa.Text(), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False, default=1),
        sa.Column('is_final', sa.Boolean(), nullable=False, default=False),
        sa.Column('hints_used', sa.JSON(), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_progress_id'], ['user_lesson_progress.id'], ondelete='CASCADE')
    )
    
    # Create test_case_results table
    op.create_table(
        'test_case_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('test_case_name', sa.String(255), nullable=False),
        sa.Column('status', postgresql.ENUM('passed', 'failed', 'error', 'timeout', name='test_result_status'), nullable=False),
        sa.Column('expected_output', sa.Text(), nullable=True),
        sa.Column('actual_output', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('points_earned', sa.Float(), nullable=False, default=0.0),
        sa.Column('points_possible', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['exercise_submissions.id'], ondelete='CASCADE')
    )
    
    # Create submission_feedback table
    op.create_table(
        'submission_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),  # NULL for automated feedback
        sa.Column('feedback_type', postgresql.ENUM('automated', 'instructor', 'peer', name='feedback_type'), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('column_number', sa.Integer(), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, default='info'),  # info, warning, error
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['exercise_submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create code_quality_metrics table
    op.create_table(
        'code_quality_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', postgresql.ENUM('readability', 'efficiency', 'best_practices', 'maintainability', name='code_quality_metric'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False, default=100.0),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['exercise_submissions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('submission_id', 'metric_type')
    )
    
    # Create submission_snapshots table for version history
    op.create_table(
        'submission_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('snapshot_type', sa.String(50), nullable=False),  # auto_save, manual_save, submission
        sa.Column('message', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['exercise_submissions.id'], ondelete='CASCADE')
    )
    
    # Create plagiarism_checks table
    op.create_table(
        'plagiarism_checks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('flagged', sa.Boolean(), nullable=False, default=False),
        sa.Column('similar_submissions', sa.JSON(), nullable=True),
        sa.Column('check_algorithm', sa.String(100), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['exercise_submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('submission_id')
    )
    
    # Create submission_collaborations table for pair programming
    op.create_table(
        'submission_collaborations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('collaborator_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),  # driver, navigator, reviewer
        sa.Column('contribution_percentage', sa.Float(), nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['exercise_submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['collaborator_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('submission_id', 'collaborator_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_exercise_submissions_user', 'exercise_submissions', ['user_id'])
    op.create_index('idx_exercise_submissions_exercise', 'exercise_submissions', ['exercise_id'])
    op.create_index('idx_exercise_submissions_status', 'exercise_submissions', ['status'])
    op.create_index('idx_exercise_submissions_submitted', 'exercise_submissions', ['submitted_at'])
    op.create_index('idx_exercise_submissions_user_exercise', 'exercise_submissions', ['user_id', 'exercise_id', 'attempt_number'])
    op.create_index('idx_test_case_results_submission', 'test_case_results', ['submission_id'])
    op.create_index('idx_test_case_results_status', 'test_case_results', ['status'])
    op.create_index('idx_submission_feedback_submission', 'submission_feedback', ['submission_id'])
    op.create_index('idx_submission_feedback_reviewer', 'submission_feedback', ['reviewer_id'])
    op.create_index('idx_submission_feedback_type', 'submission_feedback', ['feedback_type'])
    op.create_index('idx_code_quality_metrics_submission', 'code_quality_metrics', ['submission_id'])
    op.create_index('idx_submission_snapshots_submission', 'submission_snapshots', ['submission_id'])
    op.create_index('idx_submission_snapshots_created', 'submission_snapshots', ['created_at'])
    op.create_index('idx_plagiarism_checks_flagged', 'plagiarism_checks', ['flagged'])
    op.create_index('idx_plagiarism_checks_score', 'plagiarism_checks', ['similarity_score'])
    op.create_index('idx_submission_collaborations_submission', 'submission_collaborations', ['submission_id'])
    op.create_index('idx_submission_collaborations_collaborator', 'submission_collaborations', ['collaborator_id'])


def downgrade() -> None:
    """Drop exercise submission tables."""
    
    # Drop tables in reverse order
    op.drop_table('submission_collaborations')
    op.drop_table('plagiarism_checks')
    op.drop_table('submission_snapshots')
    op.drop_table('code_quality_metrics')
    op.drop_table('submission_feedback')
    op.drop_table('test_case_results')
    op.drop_table('exercise_submissions')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS code_quality_metric")
    op.execute("DROP TYPE IF EXISTS feedback_type")
    op.execute("DROP TYPE IF EXISTS test_result_status")