# flake8: noqa
"""v1-contacts-timeline

Revision ID: 0fbab19dd1f4
Revises: de77c04164a6
Create Date: 2022-04-20 15:00:23.771397

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0fbab19dd1f4"
down_revision = "de77c04164a6"
branch_labels = None
depends_on = None

create_contact_timeline_func = """CREATE OR REPLACE FUNCTION contact_timeline_func() RETURNS trigger AS $body$
    BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status OR NEW.state IS DISTINCT FROM OLD.state THEN
            INSERT INTO "contact_timeline" ( "contact_id", "status", "state" )
            VALUES(NEW."contact_id",NEW."status",NEW."state");
            RETURN NEW;
        END IF;
        RETURN null;
    END;
    $body$ LANGUAGE plpgsql
"""

drop_contact_timeline_func = """DROP FUNCTION contact_timeline_trigger"""

create_contact_timeline_trigger = """CREATE TRIGGER contact_timeline_trigger
AFTER INSERT OR UPDATE OF status, state ON contact
FOR EACH ROW EXECUTE PROCEDURE contact_timeline_func();"""

drop_contact_timeline_trigger = """DROP TRIGGER contact_timeline_trigger ON contact"""


def upgrade():
    op.create_table(
        "contact_timeline",
        sa.Column(
            "contact_timeline_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("contact_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contact.contact_id"],
        ),
        sa.PrimaryKeyConstraint("contact_timeline_id"),
    )
    op.create_index(
        op.f("ix_contact_timeline_contact_id"),
        "contact_timeline",
        ["contact_id"],
        unique=False,
    )

    op.execute(create_contact_timeline_func)
    op.execute(create_contact_timeline_trigger)


def downgrade():
    op.execute(drop_contact_timeline_trigger)
    op.execute(drop_contact_timeline_func)
    op.drop_index(
        op.f("ix_contact_timeline_timeline_id"), table_name="contact_timeline"
    )
    op.drop_table("contact_timeline")
