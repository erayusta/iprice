"""update null default product_url

Revision ID: 448be8c671d1
Revises: 5b54ddab555a
Create Date: 2024-12-31 18:53:06.590960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '448be8c671d1'
down_revision = '5b54ddab555a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE product_url SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    op.alter_column('product_url', 'created_at',
                    existing_type=sa.DateTime(),
                    server_default=sa.text('CURRENT_TIMESTAMP'),
                    nullable=False)


def downgrade():
    op.alter_column('product_url', 'created_at',
                    existing_type=sa.DateTime(),
                    server_default=None,
                    nullable=True)
