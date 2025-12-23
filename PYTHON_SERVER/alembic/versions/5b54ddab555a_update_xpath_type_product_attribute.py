"""update_xpath_type product_attribute

Revision ID: 5b54ddab555a
Revises: 72011bbfc060
Create Date: 2024-12-31 18:37:06.531850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b54ddab555a'
down_revision = '72011bbfc060'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('product_attribute', 'xpath',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    nullable=False)


def downgrade():
    op.alter_column('product_attribute', 'xpath',
                    existing_type=sa.String(),
                    type_=sa.Integer(),
                    nullable=True)
