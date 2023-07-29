import bcrypt
import logging
import uuid
from datetime import datetime, timedelta

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from marshmallow import fields

from .models import (
    ReservationRecord,
    TenantAuthenticationApiRecord
)


from . import TenantManager

LOGGER = logging.getLogger(__name__)


class EndorserLedgerConfigSchema(OpenAPISchema):
    """Schema for EndorserLedgerConfig."""

    endorser_alias = fields.Str(
        description="Endorser alias/identifier",
        required=True,
    )
    ledger_id = fields.Str(
        description="Ledger identifier",
        required=True,
    )


class TenantConfigSchema(OpenAPISchema):
    """Response schema for Tenant config."""

    connect_to_endorser = fields.List(
        fields.Nested(EndorserLedgerConfigSchema()),
        description="Endorser config",
    )
    create_public_did = fields.List(
        fields.Str(
            description="Ledger identifier",
            required=False,
        ),
        description="Public DID config",
    )


def generate_reservation_token_data(expiry_minutes: int):
    _pwd = str(uuid.uuid4().hex)
    LOGGER.info(f"_pwd = {_pwd}")

    _salt = bcrypt.gensalt()
    LOGGER.info(f"_salt = {_salt}")

    _hash = bcrypt.hashpw(_pwd.encode("utf-8"), _salt)
    LOGGER.info(f"_hash = {_hash}")

    minutes = expiry_minutes
    _expiry = datetime.utcnow() + timedelta(minutes=minutes)
    LOGGER.info(f"_expiry = {_expiry}")

    return _pwd, _salt, _hash, _expiry


async def approve_reservation(
    reservation_id: str, state_notes: str, manager: TenantManager
):
    async with manager.profile.session() as session:
        # find reservation records.
        rec = await ReservationRecord.retrieve_by_reservation_id(
            session, reservation_id, for_update=True
        )
        if rec.state == ReservationRecord.STATE_REQUESTED:
            _pwd, _salt, _hash, _expiry = generate_reservation_token_data(
                manager._config.reservation.expiry_minutes
            )
            rec.reservation_token_salt = _salt.decode("utf-8")
            rec.reservation_token_hash = _hash.decode("utf-8")
            rec.reservation_token_expiry = _expiry
            rec.state_notes = state_notes
            rec.state = ReservationRecord.STATE_APPROVED
            await rec.save(session)
            LOGGER.info(rec)
        else:
            raise ReservationException(
                f"Reservation state is currently '{rec.state}' and cannot be set to '{ReservationRecord.STATE_APPROVED}'."
            )

    return _pwd


def generate_api_key_data():
    _key = str(uuid.uuid4().hex)
    LOGGER.info(f"_key = {_key}")

    _salt = bcrypt.gensalt()
    LOGGER.info(f"_salt = {_salt}")

    _hash = bcrypt.hashpw(_key.encode("utf-8"), _salt)
    LOGGER.info(f"_hash = {_hash}")

    return _key, _salt, _hash


async def create_api_key(
    rec: TenantAuthenticationApiRecord, manager: TenantManager
):
    async with manager.profile.session() as session:
        _key, _salt, _hash = generate_api_key_data()
        rec.api_key_token_salt = _salt.decode("utf-8")
        rec.api_key_token_hash = _hash.decode("utf-8")
        await rec.save(session)
        LOGGER.info(rec)

    # return the generated key and the created record id
    return _key, rec.tenant_authentication_api_id


class ReservationException(Exception):
    pass


class TenantApiKeyException(Exception):
    pass
