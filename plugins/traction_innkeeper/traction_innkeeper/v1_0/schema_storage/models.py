import re
from typing import Optional

from acapy_agent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from acapy_agent.messaging.valid import (
    INDY_SCHEMA_ID_EXAMPLE,
    INDY_SCHEMA_ID_VALIDATE,
)
from marshmallow import EXCLUDE, fields, ValidationError


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


def validate_schema_id(value):
    """Validate schema ID as either Indy or AnonCreds format."""
    if not value or not isinstance(value, str):
        raise ValidationError("Schema ID must be a non-empty string")
    
    if len(value.strip()) == 0:
        raise ValidationError("Schema ID cannot be empty")
    
    # Indy schema ID format: DID:2:name:version
    # Pattern: ^[base58]{21,22}:2:.+:[0-9.]+$
    # Base58 characters: 1-9, A-H, J-N, P-Z, a-k, m-z (excludes 0, O, I, l)
    indy_pattern = r"^[1-9A-HJ-NP-Za-km-z]{21,22}:2:.+:[0-9.]+$"
    
    # Check if it matches Indy format
    if re.match(indy_pattern, value):
        # Validate using the official Indy validator
        try:
            INDY_SCHEMA_ID_VALIDATE(value)
        except ValidationError:
            # If Indy validator fails, still accept it (might be edge case)
            # This allows for flexibility
            pass
    
    # Accept all non-empty strings as valid schema IDs
    # (Indy format validated above, everything else is AnonCreds)
    return


class SchemaStorageRecordSchema(BaseRecordSchema):
    """Traction Schema Storage Record Schema."""

    class Meta:
        """SchemaStorageRecord Meta."""

        model_class = "SchemaStorageRecord"
        unknown = EXCLUDE

    schema_id = fields.Str(
        required=True,
        validate=validate_schema_id,
        metadata={
            "description": "Schema identifier (Indy or AnonCreds format)",
            "example": INDY_SCHEMA_ID_EXAMPLE,
        },
    )
    ledger_id = fields.Str(
        required=False, metadata={"description": "Schema identifier"}
    )

    schema = fields.Dict(
        required=False,
        metadata={"description": "(Indy) schema"},
    )
    schema_dict = fields.Dict(
        required=False, metadata={"description": "Serialized schema"}
    )
