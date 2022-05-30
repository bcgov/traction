"""v1-tenant_token

Revision ID: c9b007919a5d
Revises: e8bba5c4557b
Create Date: 2022-05-18 14:55:32.794587

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "c9b007919a5d"
down_revision = "e8bba5c4557b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tenant",
        sa.Column("wallet_token", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.create_index(op.f("ix_tenant_name"), "tenant", ["name"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_tenant_name"), table_name="tenant")
    op.drop_column("tenant", "wallet_token")
