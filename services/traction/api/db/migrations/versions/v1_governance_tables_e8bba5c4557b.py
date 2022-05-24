# flake8: noqa
"""v1-governance-tables

Revision ID: e8bba5c4557b
Revises: 1b08dc73d5f3
Create Date: 2022-05-18 10:20:46.655412

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e8bba5c4557b"
down_revision = "1b08dc73d5f3"
branch_labels = None
depends_on = None


create_timeline_func = """CREATE OR REPLACE FUNCTION issuer_credential_timeline_func() RETURNS trigger AS $body$
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

drop_timeline_func = """DROP FUNCTION issuer_credential_timeline_func"""

create_timeline_trigger = """CREATE TRIGGER issuer_credential_timeline_trigger
AFTER INSERT OR UPDATE OF status, state ON issuer_credential
FOR EACH ROW EXECUTE PROCEDURE issuer_credential_timeline_func();"""

drop_timeline_trigger = (
    """DROP TRIGGER issuer_credential_timeline_trigger ON issuer_credential"""
)


def upgrade():
    op.create_table(
        "schema_template",
        sa.Column(
            "schema_template_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("attributes", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("schema_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("imported", sa.Boolean(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("schema_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("transaction_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
        ),
        sa.PrimaryKeyConstraint("schema_template_id"),
        sa.UniqueConstraint("tenant_id", "schema_id"),
    )
    op.create_index(
        op.f("ix_schema_template_schema_id"),
        "schema_template",
        ["schema_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_schema_template_tenant_id"),
        "schema_template",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "credential_template",
        sa.Column(
            "credential_template_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("attributes", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("schema_template_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("cred_def_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("schema_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("transaction_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("tag", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("revocation_enabled", sa.Boolean(), nullable=False),
        sa.Column("revocation_registry_size", sa.Integer(), nullable=True),
        sa.Column(
            "revocation_registry_state",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["schema_template_id"],
            ["schema_template.schema_template_id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
        ),
        sa.PrimaryKeyConstraint("credential_template_id"),
    )
    op.create_index(
        op.f("ix_credential_template_cred_def_id"),
        "credential_template",
        ["cred_def_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credential_template_schema_template_id"),
        "credential_template",
        ["schema_template_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credential_template_tenant_id"),
        "credential_template",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "issuer_credential",
        sa.Column(
            "issuer_credential_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("credential_preview", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "credential_template_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("contact_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "external_reference_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("preview_persisted", sa.Boolean(), nullable=False),
        sa.Column("comment", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "revocation_comment", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("cred_def_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "credential_exchange_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("revoc_reg_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("revocation_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contact.contact_id"],
        ),
        sa.ForeignKeyConstraint(
            ["credential_template_id"],
            ["credential_template.credential_template_id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
        ),
        sa.PrimaryKeyConstraint("issuer_credential_id"),
    )
    op.create_index(
        op.f("ix_issuer_credential_contact_id"),
        "issuer_credential",
        ["contact_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_issuer_credential_cred_def_id"),
        "issuer_credential",
        ["cred_def_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_issuer_credential_credential_template_id"),
        "issuer_credential",
        ["credential_template_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_issuer_credential_tenant_id"),
        "issuer_credential",
        ["tenant_id"],
        unique=False,
    )
    op.create_table(
        "issuer_credential_timeline",
        sa.Column(
            "issuer_credential_timeline_id",
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
        sa.Column("issuer_credential_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["issuer_credential_id"],
            ["issuer_credential.issuer_credential_id"],
        ),
        sa.PrimaryKeyConstraint("issuer_credential_timeline_id"),
    )
    op.create_index(
        op.f("ix_issuer_credential_timeline_issuer_credential_id"),
        "issuer_credential_timeline",
        ["issuer_credential_id"],
        unique=False,
    )

    op.drop_index(
        "ix_connection_invitation_invitation_key", table_name="connection_invitation"
    )

    op.execute(create_timeline_func)
    op.execute(create_timeline_trigger)


def downgrade():
    op.execute(drop_timeline_trigger)
    op.execute(drop_timeline_func)

    op.create_index(
        "ix_connection_invitation_invitation_key",
        "connection_invitation",
        ["invitation_key"],
        unique=False,
    )
    op.drop_index(
        op.f("ix_issuer_credential_timeline_issuer_credential_id"),
        table_name="issuer_credential_timeline",
    )
    op.drop_table("issuer_credential_timeline")
    op.drop_index(
        op.f("ix_issuer_credential_tenant_id"), table_name="issuer_credential"
    )
    op.drop_index(
        op.f("ix_issuer_credential_credential_template_id"),
        table_name="issuer_credential",
    )
    op.drop_index(
        op.f("ix_issuer_credential_cred_def_id"), table_name="issuer_credential"
    )
    op.drop_index(
        op.f("ix_issuer_credential_contact_id"), table_name="issuer_credential"
    )
    op.drop_table("issuer_credential")
    op.drop_index(
        op.f("ix_credential_template_tenant_id"), table_name="credential_template"
    )
    op.drop_index(
        op.f("ix_credential_template_schema_template_id"),
        table_name="credential_template",
    )
    op.drop_index(
        op.f("ix_credential_template_cred_def_id"), table_name="credential_template"
    )
    op.drop_table("credential_template")
    op.drop_index(op.f("ix_schema_template_tenant_id"), table_name="schema_template")
    op.drop_index(op.f("ix_schema_template_schema_id"), table_name="schema_template")
    op.drop_table("schema_template")
