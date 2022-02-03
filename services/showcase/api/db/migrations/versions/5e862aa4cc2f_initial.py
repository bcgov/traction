"""initial

Revision ID: 5e862aa4cc2f
Revises:
Create Date: 2022-02-03 14:15:53.134169

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg



# revision identifiers, used by Alembic.
revision = '5e862aa4cc2f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade():
    op.drop_table("student")
