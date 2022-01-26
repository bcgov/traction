"""initial

Revision ID: 4a1094b37a2b
Revises:
Create Date: 2022-01-25 12:01:26.053551

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = "4a1094b37a2b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenant",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            pg.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            pg.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            onupdate=sa.text("now()"),
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("wallet_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade():
    op.drop_table("tenant")
