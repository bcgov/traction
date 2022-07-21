"""rename reusable to multi_use

Revision ID: 5f13cfb97471
Revises: cd86ad6d3331
Create Date: 2022-07-21 18:27:12.052800

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "5f13cfb97471"
down_revision = "cd86ad6d3331"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("connection_invitation", "reusable", new_column_name="multi_use")


def downgrade():
    op.alter_column("connection_invitation", "multi_use", new_column_name="reusable")
