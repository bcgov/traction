"""autogenerate_sync

Revision ID: e7fdfee68c43
Revises: 2ab74e9499c0
Create Date: 2022-06-23 22:39:44.842386

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e7fdfee68c43"
down_revision = "2ab74e9499c0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # We don't want these to be nullable, but it's going to be re-written soon
    op.alter_column(
        "tenantwebhook", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )
    op.alter_column(
        "tenantwebhookmsg", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )

    op.create_index(
        op.f("ix_verifier_presentation_contact_id"),
        "verifier_presentation",
        ["contact_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_verifier_presentation_tenant_id"),
        "verifier_presentation",
        ["tenant_id"],
        unique=False,
    )
    op.create_foreign_key(
        None, "verifier_presentation", "tenant", ["tenant_id"], ["id"]
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "verifier_presentation", type_="foreignkey")
    op.drop_index(
        op.f("ix_verifier_presentation_tenant_id"), table_name="verifier_presentation"
    )
    op.drop_index(
        op.f("ix_verifier_presentation_contact_id"), table_name="verifier_presentation"
    )
    op.alter_column(
        "tenantwebhookmsg", "tenant_id", existing_type=postgresql.UUID(), nullable=False
    )
    op.alter_column(
        "tenantwebhook", "tenant_id", existing_type=postgresql.UUID(), nullable=False
    )
    # ### end Alembic commands ###
