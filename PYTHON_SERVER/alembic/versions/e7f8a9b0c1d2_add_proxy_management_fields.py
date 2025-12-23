"""Add proxy management fields

Revision ID: e7f8a9b0c1d2
Revises: aa2bfb34b05b
Create Date: 2025-01-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7f8a9b0c1d2'
down_revision = 'aa2bfb34b05b'
branch_labels = None
depends_on = None


def upgrade():
    """
    Proxies tablosuna akıllı proxy yönetimi için yeni alanlar ekle:
    - is_active: Boolean (aktif/pasif durumu)
    - failure_count: Integer (başarısızlık sayacı)
    - last_used_at: DateTime (son kullanım zamanı)
    """
    # is_active alanı ekle (varsayılan: true)
    op.add_column('proxies', 
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true')
    )
    
    # failure_count alanı ekle (varsayılan: 0)
    op.add_column('proxies', 
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0')
    )
    
    # last_used_at alanı ekle (nullable)
    op.add_column('proxies', 
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # is_active için index oluştur (hızlı filtreleme için)
    op.create_index('ix_proxies_is_active', 'proxies', ['is_active'])
    
    print("✅ Proxy management fields eklendi: is_active, failure_count, last_used_at")


def downgrade():
    """Migration'ı geri al"""
    op.drop_index('ix_proxies_is_active', table_name='proxies')
    op.drop_column('proxies', 'last_used_at')
    op.drop_column('proxies', 'failure_count')
    op.drop_column('proxies', 'is_active')
    
    print("⬇️ Proxy management fields kaldırıldı")

