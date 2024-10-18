import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Union, List

from acapy_agent.core.profile import ProfileSession
from acapy_agent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from acapy_agent.messaging.util import datetime_to_str, str_to_datetime
from acapy_agent.messaging.valid import UUIDFour
from acapy_agent.storage.error import StorageDuplicateError, StorageNotFoundError
from marshmallow import fields, EXCLUDE, validate

ENDORSER_LEDGER_CONFIG_EXAMPLE = {
    "endorser_alias": " ... ",
    "ledger_id": " ... ",
}

RESERVATION_CONTEXT_EXAMPLE = {
    "tenant_reason": " ... ",
    "contact_name": " ... ",
    "contact_phone": " ... ",
}


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
        context_data: dict = {},
        tenant_id: str = None,
        wallet_id: str = None,
        reservation_token_salt: str = None,
        reservation_token_hash: str = None,
        reservation_token_expiry: Union[str, datetime] = None,
        state_notes: str = None,
        connect_to_endorsers: List = [],
        create_public_did: List = [],
        **kwargs,
    ):
        """Construct record."""
        super().__init__(reservation_id, state or self.STATE_REQUESTED, **kwargs)
        self.tenant_name = tenant_name
        self.tenant_reason = tenant_reason

        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.context_data = context_data

        self.tenant_id = tenant_id
        self.wallet_id = wallet_id

        self.reservation_token_salt = reservation_token_salt
        self.reservation_token_hash = reservation_token_hash
        self._reservation_token_expiry: str = datetime_to_str(reservation_token_expiry)
        self.state_notes = state_notes
        self.connect_to_endorsers = connect_to_endorsers
        self.create_public_did = create_public_did

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
        record = await cls.retrieve_by_id(
            session, reservation_id, for_update=for_update
        )
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
                "context_data",
                "tenant_id",
                "wallet_id",
                "reservation_token_salt",
                "reservation_token_hash",
                "reservation_token_expiry",
                "state_notes",
                "connect_to_endorsers",
                "create_public_did",
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

    context_data = fields.Dict(
        required=False,
        description="Context data for this tenant request",
        example=json.dumps(RESERVATION_CONTEXT_EXAMPLE),
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

    connect_to_endorser = fields.List(
        fields.Dict(description="Endorser and ledger config", required=False),
        example=json.dumps(ENDORSER_LEDGER_CONFIG_EXAMPLE),
        required=False,
        attribute="connect_to_endorsers",
    )

    create_public_did = fields.List(
        fields.Str(description="Ledger id"),
        required=False,
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
        curr_ledger_id: str = None,
        connected_to_endorsers: List = [],
        created_public_did: List = [],
        auto_issuer: bool = False,
        enable_ledger_switch=False,
        deleted_at: str = None,
        contact_email: str = None,
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
        self.connected_to_endorsers = connected_to_endorsers
        self.created_public_did = created_public_did
        self.auto_issuer = auto_issuer
        self.enable_ledger_switch = enable_ledger_switch
        self.curr_ledger_id = curr_ledger_id
        self.deleted_at = deleted_at
        self.contact_email = contact_email

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
                "connected_to_endorsers",
                "created_public_did",
                "auto_issuer",
                "enable_ledger_switch",
                "curr_ledger_id",
                "deleted_at",
                "contact_email",
            )
        }

    @classmethod
    def transform_tenant_id(cls, value: str):
        if "-" not in value:
            return str(uuid.UUID(hex=value))
        return value

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

    async def soft_delete(self, session: ProfileSession):
        """
        Soft delete the tenant record by setting its state to 'deleted'.
        Note: This method should be called on an instance of the TenantRecord.
        """
        # Delete api records
        recs = await TenantAuthenticationApiRecord.query_by_tenant_id(
            session, self.tenant_id
        )
        for rec in recs:
            if rec.tenant_id == self.tenant_id:
                await rec.delete_record(session)

        if self.state != self.STATE_DELETED:
            self.state = self.STATE_DELETED
            self.deleted_at = datetime_to_str(datetime.utcnow())
            await self.save(session, reason="Soft delete")

    async def restore_deleted(self, session: ProfileSession):
        """
        Un-soft-delete the tenant record by setting its state to 'active'.
        """
        if self.state == self.STATE_DELETED:
            self.state = self.STATE_ACTIVE
            self.deleted_at = None
            await self.save(session, reason="Restore deleted")


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

    contact_email = fields.Str(
        required=True,
        description="Email used to contact this Tenant",
        example="tmp@emailserver.com",
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

    connect_to_endorser = fields.List(
        fields.Dict(description="Endorser and ledger config", required=False),
        example=json.dumps(ENDORSER_LEDGER_CONFIG_EXAMPLE),
        required=False,
        attribute="connected_to_endorsers",
    )

    created_public_did = fields.List(
        fields.Str(description="Ledger id"),
        required=False,
    )

    auto_issuer = fields.Bool(
        required=False,
        description="True if tenant can make itself issuer, false if only innkeeper can",
        default=False,
    )

    enable_ledger_switch = fields.Bool(
        required=False,
        description="True if tenant can switch endorser/ledger",
        default=False,
    )

    curr_ledger_id = fields.Str(
        required=False,
        description="Current ledger identifier",
    )
    deleted_at = fields.Str(
        required=False,
        description="Timestamp of the deletion",
        example="2023-10-30T01:01:01Z",
    )


class TenantAuthenticationApiRecord(BaseRecord):
    """Innkeeper Tenant Authentication - API Record Schema"""

    class Meta:
        """TenantAuthenticationApiRecord Meta."""

        schema_class = "TenantAuthenticationApiRecordSchema"

    RECORD_TYPE = "tenant_authentication_api"
    RECORD_ID_NAME = "tenant_authentication_api_id"
    TAG_NAMES = {
        "tenant_id",
    }

    def __init__(
        self,
        *,
        tenant_authentication_api_id: str = None,
        tenant_id: str = None,
        api_key_token_salt: str = None,
        api_key_token_hash: str = None,
        alias: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(tenant_authentication_api_id, **kwargs)
        self.tenant_id = tenant_id
        self.api_key_token_salt = api_key_token_salt
        self.api_key_token_hash = api_key_token_hash
        self.alias = alias

    @property
    def tenant_authentication_api_id(self) -> Optional[str]:
        """Return record id."""
        return uuid.UUID(self._id).hex

    @classmethod
    async def retrieve_by_auth_api_id(
        cls,
        session: ProfileSession,
        tenant_authentication_api_id: str,
        *,
        for_update=False,
    ) -> "TenantAuthenticationApiRecord":
        """Retrieve TenantAuthenticationApiRecord by tenant_authentication_api_id.
        Args:
            session: the profile session to use
            tenant_authentication_api_id: the tenant_authentication_api_id by which to filter
        """
        record = await cls.retrieve_by_id(
            session, tenant_authentication_api_id, for_update=for_update
        )
        return record

    @classmethod
    async def query_by_tenant_id(
        cls,
        session: ProfileSession,
        tenant_id: str,
    ) -> "List[TenantAuthenticationApiRecord]":
        """Retrieve TenantAuthenticationApiRecord by tenant_id.
        Args:
            session: the profile session to use
            tenant_id: the tenant_id by which to filter
        """
        tag_filter = {
            **{"tenant_id": tenant_id for _ in [""] if tenant_id},
        }

        result = await cls.query(session, tag_filter)
        return result

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "tenant_id",
                "api_key_token_salt",
                "api_key_token_hash",
                "alias",
            )
        }


class TenantAuthenticationApiRecordSchema(BaseRecordSchema):
    """Innkeeper Tenant Authentication - API Record Schema."""

    class Meta:
        """TenantAuthenticationApiRecordSchema Meta."""

        model_class = "TenantAuthenticationApi"
        unknown = EXCLUDE

    tenant_authentication_api_id = fields.Str(
        required=True,
        description="Tenant Authentication API Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    tenant_id = fields.Str(
        required=False,
        description="Tenant Record identifier",
        example=UUIDFour.EXAMPLE,
    )

    alias = fields.Str(
        required=True,
        description="Alias description for this API key",
    )
