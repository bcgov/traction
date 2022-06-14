# flake8: noqa
"""v1-error_status_detail

Revision ID: 8ac2e131039d
Revises: b01986f67aa3
Create Date: 2022-06-09 13:34:45.813263

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8ac2e131039d"
down_revision = "b01986f67aa3"
branch_labels = None
depends_on = None

create_schema_template_timeline_func = """CREATE OR REPLACE FUNCTION schema_template_timeline_func() RETURNS trigger AS $body$
    BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status OR NEW.state IS DISTINCT FROM OLD.state THEN
            INSERT INTO "timeline" ( "item_id", "status", "state", "error_status_detail" )
            VALUES(NEW."schema_template_id", NEW."status", NEW."state", NEW."error_status_detail");
            RETURN NEW;
        END IF;
        RETURN null;
    END;
    $body$ LANGUAGE plpgsql
"""

drop_schema_template_timeline_func = """DROP FUNCTION schema_template_timeline_func"""

create_schema_template_timeline_trigger = """CREATE TRIGGER schema_template_timeline_trigger
AFTER INSERT OR UPDATE OF status, state ON schema_template
FOR EACH ROW EXECUTE PROCEDURE schema_template_timeline_func();"""

drop_schema_template_timeline_trigger = (
    """DROP TRIGGER schema_template_timeline_trigger ON schema_template"""
)


create_credential_template_timeline_func = """CREATE OR REPLACE FUNCTION credential_template_timeline_func() RETURNS trigger AS $body$
    BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status OR NEW.state IS DISTINCT FROM OLD.state THEN
            INSERT INTO "timeline" ( "item_id", "status", "state", "error_status_detail" )
            VALUES(NEW."credential_template_id", NEW."status", NEW."state", NEW."error_status_detail");
            RETURN NEW;
        END IF;
        RETURN null;
    END;
    $body$ LANGUAGE plpgsql
"""

drop_credential_template_timeline_func = (
    """DROP FUNCTION credential_template_timeline_func"""
)

create_credential_template_timeline_trigger = """CREATE TRIGGER credential_template_timeline_trigger
AFTER INSERT OR UPDATE OF status, state ON credential_template
FOR EACH ROW EXECUTE PROCEDURE credential_template_timeline_func();"""

drop_credential_template_timeline_trigger = (
    """DROP TRIGGER credential_template_timeline_trigger ON credential_template"""
)

update_contact_timeline_func = """CREATE OR REPLACE FUNCTION contact_timeline_func() RETURNS trigger AS $body$
    BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status OR NEW.state IS DISTINCT FROM OLD.state THEN
            INSERT INTO "timeline" ( "item_id", "status", "state", "error_status_detail" )
            VALUES(NEW."contact_id", NEW."status", NEW."state", NEW."error_status_detail");
            RETURN NEW;
        END IF;
        RETURN null;
    END;
    $body$ LANGUAGE plpgsql
"""

update_issuer_credential_timeline_func = """CREATE OR REPLACE FUNCTION issuer_credential_timeline_func() RETURNS trigger AS $body$
    BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status OR NEW.state IS DISTINCT FROM OLD.state THEN
            INSERT INTO "timeline" ( "item_id", "status", "state", "error_status_detail" )
            VALUES(NEW."issuer_credential_id", NEW."status", NEW."state", NEW."error_status_detail");
            RETURN NEW;
        END IF;
        RETURN null;
    END;
    $body$ LANGUAGE plpgsql
"""

restore_issuer_credential_timeline_func = """CREATE OR REPLACE FUNCTION issuer_credential_timeline_func() RETURNS trigger AS $body$
    BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status OR NEW.state IS DISTINCT FROM OLD.state THEN
            INSERT INTO "issuer_credential_timeline" ( "issuer_credential_id", "status", "state" )
            VALUES(NEW."issuer_credential_id",NEW."status",NEW."state");
            RETURN NEW;
        END IF;
        RETURN null;
    END;
    $body$ LANGUAGE plpgsql
"""

restore_contact_timeline_func = """CREATE OR REPLACE FUNCTION contact_timeline_func() RETURNS trigger AS $body$
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


def upgrade():
    op.create_table(
        "timeline",
        sa.Column(
            "error_status_detail", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "timeline_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("item_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("timeline_id"),
    )
    op.create_index(op.f("ix_timeline_item_id"), "timeline", ["item_id"], unique=False)
    op.add_column(
        "credential_template",
        sa.Column(
            "error_status_detail", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "issuer_credential",
        sa.Column(
            "error_status_detail", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "schema_template",
        sa.Column(
            "error_status_detail", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )

    op.drop_index("ix_contact_timeline_contact_id", table_name="contact_timeline")
    op.drop_table("contact_timeline")
    op.drop_index(
        "ix_issuer_credential_timeline_issuer_credential_id",
        table_name="issuer_credential_timeline",
    )
    op.drop_table("issuer_credential_timeline")
    op.add_column(
        "contact", sa.Column("error_status_detail", sa.VARCHAR(), nullable=True)
    )

    op.execute(create_credential_template_timeline_func)
    op.execute(create_credential_template_timeline_trigger)

    op.execute(create_schema_template_timeline_func)
    op.execute(create_schema_template_timeline_trigger)

    op.execute(update_contact_timeline_func)
    op.execute(update_issuer_credential_timeline_func)


def downgrade():
    op.execute(drop_credential_template_timeline_trigger)
    op.execute(drop_schema_template_timeline_trigger)

    op.execute(drop_credential_template_timeline_func)
    op.execute(drop_schema_template_timeline_func)

    op.execute(restore_contact_timeline_func)
    op.execute(restore_issuer_credential_timeline_func)

    op.drop_column("contact", "error_status_detail")
    op.create_table(
        "issuer_credential_timeline",
        sa.Column(
            "issuer_credential_timeline_id",
            postgresql.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "issuer_credential_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("status", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["issuer_credential_id"],
            ["issuer_credential.issuer_credential_id"],
            name="issuer_credential_timeline_issuer_credential_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "issuer_credential_timeline_id", name="issuer_credential_timeline_pkey"
        ),
    )
    op.create_index(
        "ix_issuer_credential_timeline_issuer_credential_id",
        "issuer_credential_timeline",
        ["issuer_credential_id"],
        unique=False,
    )
    op.create_table(
        "contact_timeline",
        sa.Column(
            "contact_timeline_id",
            postgresql.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("contact_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("status", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contact.contact_id"],
            name="contact_timeline_contact_id_fkey",
        ),
        sa.PrimaryKeyConstraint("contact_timeline_id", name="contact_timeline_pkey"),
    )
    op.create_index(
        "ix_contact_timeline_contact_id",
        "contact_timeline",
        ["contact_id"],
        unique=False,
    )

    op.drop_column("schema_template", "error_status_detail")
    op.drop_column("issuer_credential", "error_status_detail")
    op.drop_column("credential_template", "error_status_detail")
    op.drop_index(op.f("ix_timeline_item_id"), table_name="timeline")
    op.drop_table("timeline")
