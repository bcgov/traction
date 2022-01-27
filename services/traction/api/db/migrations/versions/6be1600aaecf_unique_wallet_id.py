"""unique_wallet_id

Revision ID: 6be1600aaecf
Revises: 4a1094b37a2b
Create Date: 2022-01-26 15:37:40.656968

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6be1600aaecf"
down_revision = "4a1094b37a2b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("tenant_wallet_id_key", "tenant", ["wallet_id"])


def downgrade():
    op.drop_constraint("tenant_wallet_id_key", "tenant")
