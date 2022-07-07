# flake8: noqa
"""v1-fix_verifier_presentation_triggers

Revision ID: c81a005afd28
Revises: ac386d404ddf
Create Date: 2022-07-07 10:52:34.568573

"""
from alembic import op


# revision identifiers, used by Alembic.
from api.db.migrations.versions.v1_verifier_presentations_7c527dcfae03 import (
    create_verifier_presentation_timeline_trigger,
    drop_verifier_presentation_timeline_trigger,
    drop_verifier_presentation_request_timeline_func,
)

revision = "c81a005afd28"
down_revision = "ac386d404ddf"
branch_labels = None
depends_on = None


def upgrade():
    # original v1_verifier_presentations_7c527dcfae03 upgrade
    #     op.execute(create_verifier_presentation_request_timeline_func)
    #     op.execute(create_verifier_presentation_request_timeline_func)

    # not really sure what will happen with downgrades due to old migration
    op.execute(create_verifier_presentation_timeline_trigger)


def downgrade():
    # original v1_verifier_presentations_7c527dcfae03 downgrade
    #     op.drop_table("verifier_presentation_request")
    #     op.execute(create_verifier_presentation_timeline_trigger)
    #     op.execute(drop_verifier_presentation_timeline_trigger)

    # function was never dropped.
    # the existing func/triggers calls are done after table drops,
    # so old migration may explode.
    op.execute(drop_verifier_presentation_timeline_trigger)
    op.execute(drop_verifier_presentation_request_timeline_func)
