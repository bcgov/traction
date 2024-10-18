from typing import Optional

from acapy_agent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from acapy_agent.messaging.valid import (
    INDY_SCHEMA_ID_VALIDATE,
    INDY_SCHEMA_ID_EXAMPLE,
    INDY_CRED_DEF_ID_VALIDATE,
    INDY_CRED_DEF_ID_EXAMPLE,
    UUIDFour,
)
from marshmallow import EXCLUDE, fields


class OcaRecord(BaseRecord):
    """Traction OCA Record."""

    class Meta:
        """OcaRecord Meta."""

        schema_class = "OcaRecordSchema"

    RECORD_TYPE = "oca"
    RECORD_ID_NAME = "oca_id"
    TAG_NAMES = {
        "schema_id",
        "cred_def_id",
        "owner_did",
    }

    def __init__(
        self,
        *,
        oca_id: str = None,
        schema_id: str = None,
        cred_def_id: str = None,
        url: str = None,
        bundle: dict = None,
        owner_did: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(oca_id, **kwargs)
        self.schema_id = schema_id
        self.cred_def_id = cred_def_id
        self.url = url
        self.bundle = bundle
        self.owner_did = owner_did

    @property
    def oca_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in ("schema_id", "cred_def_id", "url", "bundle", "owner_did")
        }


class OcaRecordSchema(BaseRecordSchema):
    """Traction Oca Record Schema."""

    class Meta:
        """SchemaStorageRecord Meta."""

        model_class = "OcaRecord"
        unknown = EXCLUDE

    oca_id = fields.Str(
        required=True,
        description="OCA Record identifier",
        example=UUIDFour.EXAMPLE,
    )
    schema_id = fields.Str(
        required=False,
        description="Schema identifier",
        validate=INDY_SCHEMA_ID_VALIDATE,
        example=INDY_SCHEMA_ID_EXAMPLE,
    )
    cred_def_id = fields.Str(
        required=False,
        description="Cred Def identifier",
        validate=INDY_CRED_DEF_ID_VALIDATE,
        example=INDY_CRED_DEF_ID_EXAMPLE,
    )
    url = fields.Str(required=False, description="(Public) Url for OCA Bundle")
    bundle = fields.Dict(
        required=False,
        description="OCA Bundle",
    )
    owner_did = fields.Str(required=False, description="Public DID of OCA record owner")
