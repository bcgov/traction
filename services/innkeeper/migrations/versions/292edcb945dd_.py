"""empty message

Revision ID: 292edcb945dd
Revises:
Create Date: 2022-01-17 11:24:23.821971

"""
from alembic import context, op
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "292edcb945dd"
down_revision = None
branch_labels = None
depends_on = None


def table_schema():
    return context.get_context().version_table_schema


def upgrade():
    TABLE_SCHEMA = table_schema()
    op.create_table(
        "tenant",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("public.gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("wallet_id", UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("wallet_id"),
        schema=TABLE_SCHEMA,
    )

    op.create_table(
        "access_key",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("public.gen_random_uuid()"),
        ),
        sa.Column("password", sa.String(length=256), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            [f"{TABLE_SCHEMA}.tenant.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=TABLE_SCHEMA,
    )


def downgrade():
    TABLE_SCHEMA = table_schema()
    op.drop_table("access_key", schema=TABLE_SCHEMA)
    op.drop_table("tenant", schema=TABLE_SCHEMA)
