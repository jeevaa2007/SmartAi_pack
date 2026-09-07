"""Milestone 35 Percent Database Schema Migration

Revision ID: 20260907_0002
Revises: 20260905_0001
Create Date: 2026-09-07 09:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20260907_0002'
down_revision: Union[str, None] = '20260905_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create stores table
    op.create_table(
        'stores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('store_code', sa.String(30), nullable=False, unique=True),
        sa.Column('store_name', sa.String(100), nullable=False),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_stores_store_code'), 'stores', ['store_code'], unique=True)

    # 2. Add foreign key from users.store_id to stores.id
    op.create_foreign_key(
        'fk_users_store_id_stores',
        'users', 'stores',
        ['store_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_users_store_id'), 'users', ['store_id'], unique=False)

    # 3. Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sku', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('dimensions', sa.String(100), nullable=True),
        sa.Column('is_fragile', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('temperature_req', sa.String(20), nullable=False, server_default='AMBIENT'),
        sa.Column('is_liquid', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_crush_sensitive', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('preferred_packaging_type', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)

    # 4. Create packaging_materials table
    op.create_table(
        'packaging_materials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('material_type', sa.String(50), nullable=False),
        sa.Column('capacity_size', sa.String(50), nullable=False, server_default='MEDIUM'),
        sa.Column('protection_level', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('temperature_suitability', sa.String(20), nullable=False, server_default='ALL'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_packaging_materials_code'), 'packaging_materials', ['code'], unique=True)

    # 5. Create packaging_rules table
    op.create_table(
        'packaging_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rule_code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('condition_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('required_material_type', sa.String(50), nullable=True),
        sa.Column('min_protection_level', sa.String(20), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, server_default='HIGH'),
        sa.Column('deduction_points', sa.Integer(), nullable=False, server_default='25'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_packaging_rules_rule_code'), 'packaging_rules', ['rule_code'], unique=True)

    # 6. Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_number', sa.String(50), nullable=False, unique=True),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stores.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='CREATED'),
        sa.Column('verification_status', sa.String(20), nullable=False, server_default='UNVERIFIED'),
        sa.Column('packing_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_orders_order_number'), 'orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_orders_store_id'), 'orders', ['store_id'], unique=False)
    op.create_index(op.f('ix_orders_operator_id'), 'orders', ['operator_id'], unique=False)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)
    op.create_index(op.f('ix_orders_verification_status'), 'orders', ['verification_status'], unique=False)

    # 7. Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('item_attributes_snapshot', sa.Text(), nullable=True, server_default='{}')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)

    # 8. Create packing_verifications table
    op.create_table(
        'packing_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('image_path', sa.String(255), nullable=True),
        sa.Column('packing_score', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('violations_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('recommendations_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_packing_verifications_order_id'), 'packing_verifications', ['order_id'], unique=False)
    op.create_index(op.f('ix_packing_verifications_operator_id'), 'packing_verifications', ['operator_id'], unique=False)
    op.create_index(op.f('ix_packing_verifications_status'), 'packing_verifications', ['status'], unique=False)

    # 9. Create rule_violations table
    op.create_table(
        'rule_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('verification_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('packing_verifications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('packaging_rules.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rule_code', sa.String(50), nullable=True),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('detected_value', sa.String(255), nullable=True),
        sa.Column('expected_value', sa.String(255), nullable=True),
        sa.Column('deduction', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index(op.f('ix_rule_violations_verification_id'), 'rule_violations', ['verification_id'], unique=False)

def downgrade() -> None:
    op.drop_table('rule_violations')
    op.drop_table('packing_verifications')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('packaging_rules')
    op.drop_table('packaging_materials')
    op.drop_table('products')
    op.drop_constraint('fk_users_store_id_stores', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_store_id'), table_name='users')
    op.drop_table('stores')
