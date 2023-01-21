from typing import Optional

from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from marshmallow import EXCLUDE, fields


class SchemaCacheRecord(BaseRecord):
    """Traction Schema Cache Record."""

    class Meta:
        """SchemaCacheRecord Meta."""

        schema_class = "SchemaCacheRecordSchema"

    RECORD_TYPE = "schema_cache"
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


class SchemaCacheRecordSchema(BaseRecordSchema):
    """Traction Schema Cache Record Schema."""

    class Meta:
        """SchemaRecord Meta."""

        model_class = "SchemaCacheRecord"
        unknown = EXCLUDE

    schema_id = fields.Str(required=True, description="Schema identifier")
    ledger_id = fields.Str(required=False, description="Schema identifier")

    schema = fields.Dict(
        required=False,
        description="(Indy) schema",
    )
    schema_dict = fields.Dict(required=False, description="Serialized schema")
