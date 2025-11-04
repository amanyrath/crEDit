"""Initial schema

Revision ID: 84631dd483c
Revises: 
Create Date: 2025-11-03 21:14:34.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '84631dd483c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        comment='User profile with role information'
    )
    op.create_index(op.f('ix_profiles_email'), 'profiles', ['email'], unique=True)
    
    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.String(length=10), server_default='1.0', nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Consent record for user data processing consent'
    )
    op.create_index(op.f('ix_consent_records_user_id'), 'consent_records', ['user_id'], unique=False)
    
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_type', sa.String(length=30), nullable=False),
        sa.Column('account_number_last4', sa.String(length=4), nullable=True),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('limit', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Bank account information'
    )
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'], unique=False)
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('merchant', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Transaction record'
    )
    op.create_index(op.f('ix_transactions_account_id'), 'transactions', ['account_id'], unique=False)
    op.create_index(op.f('ix_transactions_date'), 'transactions', ['date'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index('idx_transactions_user_date', 'transactions', ['user_id', sa.text('date DESC')], unique=False)
    
    # Create computed_features table
    op.create_table(
        'computed_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('time_window', sa.String(length=10), nullable=False),
        sa.Column('signal_type', sa.String(length=100), nullable=False),
        sa.Column('signal_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Computed behavioral signal for a user'
    )
    op.create_index(op.f('ix_computed_features_signal_type'), 'computed_features', ['signal_type'], unique=False)
    op.create_index(op.f('ix_computed_features_user_id'), 'computed_features', ['user_id'], unique=False)
    op.create_index('idx_computed_features_user_window', 'computed_features', ['user_id', 'time_window'], unique=False)
    
    # Create persona_assignments table
    op.create_table(
        'persona_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('time_window', sa.String(length=10), nullable=False),
        sa.Column('persona', sa.String(length=50), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Persona assignment for a user in a time window'
    )
    op.create_index(op.f('ix_persona_assignments_user_id'), 'persona_assignments', ['user_id'], unique=False)
    op.create_index('idx_persona_assignments_user_window', 'persona_assignments', ['user_id', 'time_window'], unique=False)
    
    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('shown_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Recommendation for a user (education or offer)'
    )
    op.create_index(op.f('ix_recommendations_shown_at'), 'recommendations', ['shown_at'], unique=False)
    op.create_index(op.f('ix_recommendations_user_id'), 'recommendations', ['user_id'], unique=False)
    
    # Create decision_traces table
    op.create_table(
        'decision_traces',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trace_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recommendation_id', name='uq_decision_traces_recommendation_id'),
        comment='Decision trace for a recommendation (one-to-one with recommendation)'
    )
    
    # Create chat_logs table
    op.create_table(
        'chat_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('guardrails_passed', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Chat log entry for AI chat interactions'
    )
    op.create_index(op.f('ix_chat_logs_user_id'), 'chat_logs', ['user_id'], unique=False)
    
    # Create operator_actions table
    op.create_table(
        'operator_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['operator_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Operator action (override, flag, etc.)'
    )
    op.create_index(op.f('ix_operator_actions_operator_id'), 'operator_actions', ['operator_id'], unique=False)
    op.create_index(op.f('ix_operator_actions_user_id'), 'operator_actions', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('operator_actions')
    op.drop_table('chat_logs')
    op.drop_table('decision_traces')
    op.drop_table('recommendations')
    op.drop_table('persona_assignments')
    op.drop_table('computed_features')
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('consent_records')
    op.drop_table('profiles')
    
    # Drop UUID extension (optional, may be used by other databases)
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')

