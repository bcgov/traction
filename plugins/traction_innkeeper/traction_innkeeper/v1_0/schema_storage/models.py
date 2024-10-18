from typing import Optional

from acapy_agent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from acapy_agent.messaging.valid import (
    INDY_SCHEMA_ID_EXAMPLE,
    INDY_SCHEMA_ID_VALIDATE,
)
from marshmallow import EXCLUDE, fields


class SchemaStorageRecord(BaseRecord):
    """Traction Schema Storage Record."""

    class Meta:
        """SchemaStorageRecord Meta."""

        schema_class = "SchemaStorageRecordSchema"

    RECORD_TYPE = "schema_storage"
    RECORD_ID_NAME = "schema_id"
    TAG_NAMES = {}

    def __init__(
        self,
        *,
        schema_id: str = None,
        ledger_id: str = None,
        schema: dict = None,
        schema_dict: dict = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(schema_id, new_with_id=schema_id is not None, **kwargs)
        self.ledger_id = ledger_id
        self.schema = schema
        self.schema_dict = schema_dict

    @property
    def schema_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "ledger_id",
                "schema",
                "schema_dict",
            )
        }


class SchemaStorageRecordSchema(BaseRecordSchema):
    """Traction Schema Storage Record Schema."""

    class Meta:
        """SchemaStorageRecord Meta."""

        model_class = "SchemaStorageRecord"
        unknown = EXCLUDE

    schema_id = fields.Str(
        required=True,
        description="Schema identifier",
        validate=INDY_SCHEMA_ID_VALIDATE,
        example=INDY_SCHEMA_ID_EXAMPLE,
    )
    ledger_id = fields.Str(required=False, description="Schema identifier")

    schema = fields.Dict(
        required=False,
        description="(Indy) schema",
    )
    schema_dict = fields.Dict(required=False, description="Serialized schema")
