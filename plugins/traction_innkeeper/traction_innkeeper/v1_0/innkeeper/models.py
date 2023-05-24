import uuid
from datetime import datetime, timezone
from typing import Optional, Union

from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.util import datetime_to_str, str_to_datetime
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.storage.error import StorageDuplicateError, StorageNotFoundError
from marshmallow import fields, EXCLUDE, validate


class ReservationRecord(BaseRecord):
    """Innkeeper Tenant Reservation Record."""

    class Meta:
        """ReservationRecord Meta."""

        schema_class = "ReservationRecordSchema"

    RECORD_TYPE = "tenant_reservation"
    RECORD_ID_NAME = "reservation_id"
    TAG_NAMES = {
        "state",
        "tenant_name",
    }

    STATE_REQUESTED = "requested"
    STATE_APPROVED = "approved"
    STATE_DENIED = "denied"
    STATE_CHECKED_IN = "checked_in"

    def __init__(
        self,
        *,
        reservation_id: str = None,
        state: str = None,
        tenant_name: str = None,
        tenant_reason: str = None,
        contact_name: str = None,
        contact_email: str = None,
        contact_phone: str = None,
        tenant_id: str = None,
        wallet_id: str = None,
        reservation_token_salt: str = None,
        reservation_token_hash: str = None,
        reservation_token_expiry: Union[str, datetime] = None,
        state_notes: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(reservation_id, state or self.STATE_REQUESTED, **kwargs)
        self.tenant_name = tenant_name
        self.tenant_reason = tenant_reason

        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone

        self.tenant_id = tenant_id
        self.wallet_id = wallet_id

        self.reservation_token_salt = reservation_token_salt
        self.reservation_token_hash = reservation_token_hash
        self._reservation_token_expiry: str = datetime_to_str(reservation_token_expiry)
        self.state_notes = state_notes

    @property
    def reservation_id(self) -> Optional[str]:
        """Return record id."""
        return uuid.UUID(self._id).hex

    @classmethod
    def transform_reservation_id(cls, value: str):
        # since reservation id is created/stored with dashes and returned without
        # we need a transform function so we can query the records...
        if "-" not in value:
            return str(uuid.UUID(hex=value))
        return value

    @classmethod
    async def retrieve_by_reservation_id(
        cls,
        session: ProfileSession,
        record_id: str,
        *,
        for_update=False,
    ) -> "ReservationRecord":
        """Retrieve TenantRecord by wallet_id.
        Args:
            session: the profile session to use
            record_id: the reservation_id (may or may not have dashes) by which to filter
        """
        reservation_id = cls.transform_reservation_id(record_id)
        record = await cls.retrieve_by_id(session, reservation_id, for_update=for_update)
        return record

    @property
    def reservation_token_expiry(self) -> str:
        return self._reservation_token_expiry

    @reservation_token_expiry.setter
    def reservation_token_expiry(self, value: Union[str, datetime] = None) -> None:
        self._reservation_token_expiry = datetime_to_str(value)

    @property
    def expired(self) -> bool:
        if not self._reservation_token_expiry:
            return False
        else:
            return datetime.now(tz=timezone.utc) > str_to_datetime(
                self._reservation_token_expiry
            )

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "tenant_name",
                "tenant_reason",
                "contact_name",
                "contact_email",
                "contact_phone",
                "tenant_id",
                "wallet_id",
                "reservation_token_salt",
                "reservation_token_hash",
                "reservation_token_expiry",
                "state_notes",
            )
        }


class ReservationRecordSchema(BaseRecordSchema):
    """Innkeeper Tenant Reservation Record Schema."""

    class Meta:
        """ReservationRecordSchema Meta."""

        model_class = "ReservationRecord"
        unknown = EXCLUDE

    reservation_id = fields.Str(
        required=True,
        description="Tenant Reservation Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    tenant_name = fields.Str(
        required=True,
        description="Proposed name of Tenant",
        example="line of business short name",
    )

    tenant_reason = fields.Str(
        required=True,
        description="Reason(s) for requesting a tenant",
        example="Issue permits to clients",
    )

    contact_name = fields.Str(
        required=True,
        description="Contact name for this tenant request",
    )

    contact_email = fields.Str(
        required=True,
        description="Contact email for this tenant request",
    )

    contact_phone = fields.Str(
        required=True,
        description="Contact phone number for this tenant request",
    )

    state = fields.Str(
        required=True,
        description="The state of the tenant request.",
        example=ReservationRecord.STATE_REQUESTED,
        validate=validate.OneOf(
            [
                ReservationRecord.STATE_REQUESTED,
                ReservationRecord.STATE_APPROVED,
                ReservationRecord.STATE_CHECKED_IN,
            ]
        ),
    )

    state_notes = fields.Str(
        required=False,
        description="Notes about the state of the tenant request",
    )

    tenant_id = fields.Str(
        required=False,
        description="Tenant Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    wallet_id = fields.Str(
        required=False,
        description="Tenant Wallet Record identifier",
        example=UUIDFour.EXAMPLE,
    )


class TenantRecord(BaseRecord):
    """Innkeeper Tenant Record."""

    class Meta:
        """TenantRecord Meta."""

        schema_class = "TenantRecordSchema"

    RECORD_TYPE = "innkeeper_tenant"
    RECORD_ID_NAME = "tenant_id"
    TAG_NAMES = {
        "state",
        "wallet_id",
        "tenant_name",
    }

    STATE_ACTIVE = "active"
    STATE_DELETED = "deleted"  # TODO: figure out states and other data...

    def __init__(
        self,
        *,
        tenant_id: str = None,
        state: str = None,
        tenant_name: str = None,
        wallet_id: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(
            tenant_id,
            state or self.STATE_ACTIVE,
            **kwargs,
        )
        self.tenant_name = tenant_name
        self.wallet_id = wallet_id

    @property
    def tenant_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "tenant_name",
                "wallet_id",
            )
        }

    @classmethod
    async def query_by_wallet_id(
        cls,
        session: ProfileSession,
        wallet_id: str,
    ) -> "TenantRecord":
        """Retrieve TenantRecord by wallet_id.
        Args:
            session: the profile session to use
            wallet_id: the wallet_id by which to filter
        """
        tag_filter = {
            **{"wallet_id": wallet_id for _ in [""] if wallet_id},
        }

        result = await cls.query(session, tag_filter)
        if len(result) > 1:
            raise StorageDuplicateError(
                "More than one TenantRecord was found for the given wallet_id"
            )
        if not result:
            raise StorageNotFoundError("No TenantRecord found for the given wallet_id")
        return result[0]


class TenantRecordSchema(BaseRecordSchema):
    """Innkeeper Tenant Record Schema."""

    class Meta:
        """TenantRecordSchema Meta."""

        model_class = "TenantRecord"
        unknown = EXCLUDE

    tenant_id = fields.Str(
        required=True,
        description="Tenant Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    tenant_name = fields.Str(
        required=True,
        description="Proposed name of Tenant",
        example="line of business short name",
    )

    state = fields.Str(
        required=True,
        description="The state of the tenant.",
        example=TenantRecord.STATE_ACTIVE,
        validate=validate.OneOf(
            [
                TenantRecord.STATE_ACTIVE,
                TenantRecord.STATE_DELETED,
            ]
        ),
    )

    wallet_id = fields.Str(
        required=False,
        description="Tenant Wallet Record identifier",
        example=UUIDFour.EXAMPLE,
    )
