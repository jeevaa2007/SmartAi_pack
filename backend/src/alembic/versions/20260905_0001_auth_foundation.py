"""Authentication Database Foundation Schema

Revision ID: 20260905_0001
Revises: None
Create Date: 2026-09-05 10:18:00.000000

"""
import uuid
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260905_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Initial seed roles definitions
ADMIN_ROLE_ID = "11111111-1111-4111-8111-111111111111"
SUPERVISOR_ROLE_ID = "22222222-2222-4222-8222-222222222222"
OPERATOR_ROLE_ID = "33333333-3333-4333-8333-333333333333"

def upgrade() -> None:
    # 1. Create 'roles' table
    roles_table = op.create_table(
        'roles',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)

    # Seed initial roles
    now_utc = datetime.now(timezone.utc)
    op.bulk_insert(
        roles_table,
        [
            {
                'id': uuid.UUID(ADMIN_ROLE_ID),
                'name': 'ADMIN',
                'description': 'System administrator with full administrative access',
                'is_active': True,
                'created_at': now_utc,
                'updated_at': now_utc,
            },
            {
                'id': uuid.UUID(SUPERVISOR_ROLE_ID),
                'name': 'SUPERVISOR',
                'description': 'Store supervisor with override validation capabilities',
                'is_active': True,
                'created_at': now_utc,
                'updated_at': now_utc,
            },
            {
                'id': uuid.UUID(OPERATOR_ROLE_ID),
                'name': 'OPERATOR',
                'description': 'Dark store packing operator performing order quality verification',
                'is_active': True,
                'created_at': now_utc,
                'updated_at': now_utc,
            },
        ]
    )

    # 2. Create 'users' table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('store_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role_id', 'users', ['role_id'], unique=False)

    # 3. Create 'audit_logs' table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)

def downgrade() -> None:
    # Drop tables in strict reverse dependency order
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_users_role_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

    op.drop_index('ix_roles_name', table_name='roles')
    op.drop_table('roles')
