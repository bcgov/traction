"""initial

Revision ID: 5e862aa4cc2f
Revises:
Create Date: 2022-02-03 14:15:53.134169

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision = "5e862aa4cc2f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sandbox",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tag", sa.String(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tenant",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("wallet_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("wallet_key", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("webhook_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("sandbox_id", pg.UUID(as_uuid=True), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["sandbox_id"], ["sandbox.id"]),
    )

    op.create_table(
        "student",
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
        sa.Column("sandbox_id", pg.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "sandbox_id"),
        sa.ForeignKeyConstraint(["sandbox_id"], ["sandbox.id"]),
    )


def downgrade():
    op.drop_table("student")
    op.drop_table("tenant")
    op.drop_table("sandbox")
