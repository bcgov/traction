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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("wallet_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("wallet_id"),
    )

    op.create_table(
        "tenantwebhook",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("webhook_url", sa.String(), nullable=False),
        sa.Column("webhook_key", sa.String(), nullable=True),
        sa.Column("config", pg.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), nullable=False),
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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
    )

    op.create_table(
        "tenantwebhookmsg",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("msg_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("response_code", sa.Integer(), nullable=True),
        sa.Column("response", sa.String(), nullable=True),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), nullable=False),
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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
    )

    op.create_table(
        "tenantworkflow",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("wallet_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_type", sa.String(), nullable=False),
        sa.Column("workflow_state", sa.String(), nullable=False),
        sa.Column("workflow_state_msg", sa.String(), nullable=True),
        sa.Column("wallet_bearer_token", sa.String(), nullable=True),
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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tenantissuer",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("wallet_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("endorser_connection_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("endorser_connection_state", sa.String(), nullable=True),
        sa.Column("public_did", sa.String(), nullable=True),
        sa.Column("public_did_state", sa.String(), nullable=True),
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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("tenantissuer")
    op.drop_table("tenantworkflow")
    op.drop_table("tenantwebhookmsg")
    op.drop_table("tenantwebhook")
    op.drop_table("tenant")
