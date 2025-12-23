"""create tables

Revision ID: 0ffbef0d8448
Revises: 
Create Date: 2024-12-31 16:34:32.372229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ffbef0d8448'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'company',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_marketplace', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'attribute',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'screenshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('mpn', sa.String()),
        sa.Column('url', sa.String()),
        sa.Column('image_name', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_screenshots_mpn', 'mpn')
    )

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String()),
        sa.Column('mpn', sa.String()),
        sa.Column('gtin', sa.String()),
        sa.Column('availability', sa.String()),
        sa.Column('price', sa.String()),
        sa.Column('sale_price', sa.String()),
        sa.Column('web_price', sa.String()),
        sa.Column('merchant_price', sa.String()),
        sa.Column('condition', sa.String()),
        sa.Column('description', sa.String()),
        sa.Column('brand', sa.String()),
        sa.Column('link', sa.String()),
        sa.Column('product_type', sa.String()),
        sa.Column('status', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_hero', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_products_mpn', 'mpn'),
        sa.Index('ix_products_gtin', 'gtin'),
        sa.Index('ix_products_availability', 'availability'),
        sa.Index('ix_products_price', 'price'),
        sa.Index('ix_products_sale_price', 'sale_price'),
        sa.Index('ix_products_web_price', 'web_price'),
        sa.Index('ix_products_merchant_price', 'merchant_price')
    )

    op.create_table(
        'products_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('process_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String()),
        sa.Column('mpn', sa.String()),
        sa.Column('gtin', sa.String()),
        sa.Column('availability', sa.String()),
        sa.Column('price', sa.String()),
        sa.Column('sale_price', sa.String()),
        sa.Column('web_price', sa.String()),
        sa.Column('merchant_price', sa.String()),
        sa.Column('condition', sa.String()),
        sa.Column('description', sa.String()),
        sa.Column('brand', sa.String()),
        sa.Column('link', sa.String()),
        sa.Column('product_type', sa.String()),
        sa.Column('cron_source', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_products_history_mpn', 'mpn'),
        sa.Index('ix_products_history_gtin', 'gtin'),
        sa.Index('ix_products_history_availability', 'availability'),
        sa.Index('ix_products_history_price', 'price'),
        sa.Index('ix_products_history_sale_price', 'sale_price'),
        sa.Index('ix_products_history_web_price', 'web_price'),
        sa.Index('ix_products_history_merchant_price', 'merchant_price')
    )

    op.create_table(
        'product_url',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('mpn', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='fk_product_url_company'),
        sa.Index('ix_product_url_mpn', 'mpn')
    )

    op.create_table(
        'product_attribute',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('attribute_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('xpath', sa.Integer(), nullable=False),
        sa.Column('selector_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['attribute_id'], ['attribute.id'], name='fk_product_attribute_attribute'),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='fk_product_attribute_company')
    )

    op.create_table(
        'product_attribute_value',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer()),
        sa.Column('attribute_id', sa.Integer()),
        sa.Column('mpn', sa.String()),
        sa.Column('value', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='fk_product_attribute_value_company'),
        sa.ForeignKeyConstraint(['attribute_id'], ['attribute.id'], name='fk_product_attribute_value_attribute'),
        sa.Index('ix_product_attribute_value_mpn', 'mpn')
    )

def downgrade():
    op.drop_table('product_attribute_value')
    op.drop_table('product_attribute')
    op.drop_table('product_url')

    op.drop_table('products_history')
    op.drop_table('products')
    op.drop_table('screenshots')
    op.drop_table('attribute')
    op.drop_table('company')
