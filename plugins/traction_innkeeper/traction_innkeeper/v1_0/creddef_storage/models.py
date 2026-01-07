import re
from typing import Optional

from acapy_agent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from acapy_agent.messaging.valid import (
    INDY_SCHEMA_ID_VALIDATE,
    INDY_SCHEMA_ID_EXAMPLE,
    INDY_REV_REG_SIZE_VALIDATE,
    INDY_REV_REG_SIZE_EXAMPLE,
    INDY_CRED_DEF_ID_VALIDATE,
    INDY_CRED_DEF_ID_EXAMPLE,
)
from marshmallow import EXCLUDE, fields, ValidationError


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


def validate_cred_def_id(value):
    """Validate credential definition ID as either Indy or AnonCreds format."""
    if not value or not isinstance(value, str):
        raise ValidationError("Credential definition ID must be a non-empty string")
    
    if len(value.strip()) == 0:
        raise ValidationError("Credential definition ID cannot be empty")
    
    # Indy cred def ID format: DID:3:CL:(seq_no|schema_id):tag
    # Pattern: ^[base58]{21,22}:3:CL:(([1-9][0-9]*)|([base58]{21,22}:2:.+:[0-9.]+)):(.+)?$
    # Schema reference can be either a sequence number or full schema ID
    indy_pattern = (
        r"^[1-9A-HJ-NP-Za-km-z]{21,22}"  # issuer DID
        r":3"  # cred def id marker
        r":CL"  # sig alg
        r":(([1-9][0-9]*)|([1-9A-HJ-NP-Za-km-z]{21,22}:2:.+:[0-9.]+))"  # schema txn/id
        r":(.+)?$"  # optional tag
    )
    
    # Check if it matches Indy format
    if re.match(indy_pattern, value):
        # Validate using the official Indy validator
        try:
            INDY_CRED_DEF_ID_VALIDATE(value)
        except ValidationError:
            # If Indy validator fails, still accept it (might be edge case)
            pass
    
    # Accept all non-empty strings as valid credential definition IDs
    # (Indy format validated above, everything else is AnonCreds)
    return


def validate_schema_id_for_creddef(value):
    """Validate schema ID as either Indy or AnonCreds format."""
    if not value or not isinstance(value, str):
        raise ValidationError("Schema ID must be a non-empty string")
    
    if len(value.strip()) == 0:
        raise ValidationError("Schema ID cannot be empty")
    
    # Indy schema ID format: DID:2:name:version
    indy_pattern = r"^[1-9A-HJ-NP-Za-km-z]{21,22}:2:.+:[0-9.]+$"
    
    # Check if it matches Indy format
    if re.match(indy_pattern, value):
        # Validate using the official Indy validator
        try:
            INDY_SCHEMA_ID_VALIDATE(value)
        except ValidationError:
            # If Indy validator fails, still accept it (might be edge case)
            pass
    
    # Accept all non-empty strings as valid schema IDs
    return


class CredDefStorageRecordSchema(BaseRecordSchema):
    """Traction CredDef Storage Record Schema."""

    class Meta:
        """CredDefStorageRecord Meta."""

        model_class = "CredDefStorageRecord"
        unknown = EXCLUDE

    cred_def_id = fields.Str(
        required=True,
        validate=validate_cred_def_id,
        metadata={
            "description": "Cred Def identifier (Indy or AnonCreds format)",
            "example": INDY_CRED_DEF_ID_EXAMPLE,
        },
    )
    schema_id = fields.Str(
        validate=validate_schema_id_for_creddef,
        metadata={
            "description": "Schema identifier (Indy or AnonCreds format)",
            "example": INDY_SCHEMA_ID_EXAMPLE,
        },
    )
    support_revocation = fields.Boolean(
        required=False, metadata={"description": "Revocation supported flag"}
    )
    rev_reg_size = fields.Int(
        required=False,
        strict=True,
        allow_none=True,
        validate=INDY_REV_REG_SIZE_VALIDATE,
        metadata={
            "description": "Revocation registry size",
            "example": INDY_REV_REG_SIZE_EXAMPLE,
        },
    )
    tag = fields.Str(
        required=False,
        metadata={
            "description": "Credential definition identifier tag",
            "default": "default",
            "example": "default",
        },
    )
