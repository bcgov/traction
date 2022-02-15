"""out of band

Revision ID: 3449c639cdbd
Revises: 5e862aa4cc2f
Create Date: 2022-02-11 15:41:14.509243

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = "3449c639cdbd"
down_revision = "5e862aa4cc2f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "outofband",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
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
        ),
        sa.Column("msg_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("msg", pg.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("sender_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("sandbox_id", pg.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipient_id"],
            ["tenant.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["tenant.id"],
        ),
        sa.ForeignKeyConstraint(["sandbox_id"], ["sandbox.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("outofband")
