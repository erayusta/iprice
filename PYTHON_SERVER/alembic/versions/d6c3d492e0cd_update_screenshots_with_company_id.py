"""update screenshots with company_id

Revision ID: d6c3d492e0cd
Revises: 448be8c671d1
Create Date: 2025-01-29 09:37:16.189618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6c3d492e0cd'
down_revision = '448be8c671d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('screenshots', sa.Column('company_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_screenshots_company_id',
        'screenshots',
        'company',
        ['company_id'],
        ['id']
    )
    op.alter_column('screenshots', 'company_id',
                    existing_type=sa.Integer(),
                    nullable=False)


def downgrade() -> None:
    op.drop_constraint('fk_screenshots_company_id', 'screenshots', type_='foreignkey')

    op.drop_column('screenshots', 'company_id')
