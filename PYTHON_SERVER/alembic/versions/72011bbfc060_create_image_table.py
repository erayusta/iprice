"""create image table

Revision ID: 72011bbfc060
Revises: 0ffbef0d8448
Create Date: 2024-12-31 16:35:54.990152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72011bbfc060'
down_revision = '0ffbef0d8448'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('mpn', sa.String()),
        sa.Column('image_url', sa.String()),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_images_mpn', 'mpn')
    )


def downgrade():
    op.drop_table('images')
