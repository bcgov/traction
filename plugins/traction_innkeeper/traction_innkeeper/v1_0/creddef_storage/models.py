from typing import Optional

from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.valid import (
    INDY_SCHEMA_ID,
    INDY_REV_REG_SIZE,
    INDY_CRED_DEF_ID,
)
from marshmallow import EXCLUDE, fields


class CredDefStorageRecord(BaseRecord):
    """Traction CredDef Storage Record."""

    class Meta:
        """CredDefStorageRecord Meta."""

        schema_class = "CredDefStorageRecordSchema"

    RECORD_TYPE = "creddef_storage"
    RECORD_ID_NAME = "cred_def_id"
    TAG_NAMES = {"schema_id", "tag"}

    def __init__(
        self,
        *,
        cred_def_id: str = None,
        schema_id: str = None,
        issuer_did: str = None,
        support_revocation: bool = False,
        tag: str = None,
        rev_reg_size: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(cred_def_id, new_with_id=cred_def_id is not None, **kwargs)
        self.schema_id = schema_id
        self.support_revocation = support_revocation
        self.tag = tag
        self.rev_reg_size = rev_reg_size

    @property
    def cred_def_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in ("schema_id", "support_revocation", "tag", "rev_reg_size")
        }


class CredDefStorageRecordSchema(BaseRecordSchema):
    """Traction CredDef Storage Record Schema."""

    class Meta:
        """CredDefStorageRecord Meta."""

        model_class = "CredDefStorageRecord"
        unknown = EXCLUDE

    cred_def_id = fields.Str(
        required=True, description="Cred Def identifier", **INDY_CRED_DEF_ID
    )
    schema_id = fields.Str(description="Schema identifier", **INDY_SCHEMA_ID)
    support_revocation = fields.Boolean(
        required=False, description="Revocation supported flag"
    )
    rev_reg_size = fields.Int(
        description="Revocation registry size",
        required=False,
        strict=True,
        allow_none=True,
        **INDY_REV_REG_SIZE,
    )
    tag = fields.Str(
        required=False,
        description="Credential definition identifier tag",
        default="default",
        example="default",
    )
