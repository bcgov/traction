import bcrypt
import logging
import uuid
from datetime import datetime, timedelta

from acapy_agent.core.profile import Profile
from acapy_agent.messaging.models.openapi import OpenAPISchema
from marshmallow import fields

from .models import ReservationRecord, TenantAuthenticationApiRecord, TenantRecord


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


async def refresh_registration_token(reservation_id: str, manager: TenantManager):
    """
    Invalidate the old token, generate a new token, and update the reservation record.
    :return: new_token: the new refreshed token
    """
    async with manager.profile.session() as session:
        try:
            reservation = await ReservationRecord.retrieve_by_reservation_id(
                session, reservation_id, for_update=True
            )
        except Exception as err:
            LOGGER.error("Failed to retrieve reservation: %s", err)
            raise ReservationException(
                "Could not retrieve reservation record."
            ) from err

        if reservation.state != ReservationRecord.STATE_APPROVED:
            raise ReservationException("Only approved reservations can refresh tokens.")

        # Generate new token data
        _pwd = str(uuid.uuid4().hex)  # This generates a new token
        _salt = bcrypt.gensalt()
        _hash = bcrypt.hashpw(_pwd.encode("utf-8"), _salt)

        minutes = manager._config.reservation.expiry_minutes
        _expiry = datetime.utcnow() + timedelta(minutes=minutes)

        # Update the reservation record with the new token and related info
        reservation.reservation_token_salt = _salt.decode("utf-8")
        reservation.reservation_token_hash = _hash.decode("utf-8")
        reservation.reservation_token_expiry = _expiry

        try:
            await reservation.save(session)
        except Exception as err:
            LOGGER.error("Failed to update reservation record: %s", err)
            raise ReservationException("Could not update reservation record.") from err

        LOGGER.info("Refreshed token for reservation %s", reservation_id)

        return _pwd


def generate_api_key_data():
    _key = str(uuid.uuid4().hex)
    LOGGER.info(f"_key = {_key}")

    _salt = bcrypt.gensalt()
    LOGGER.info(f"_salt = {_salt}")

    _hash = bcrypt.hashpw(_key.encode("utf-8"), _salt)
    LOGGER.info(f"_hash = {_hash}")

    return _key, _salt, _hash


async def create_api_key(rec: TenantAuthenticationApiRecord, manager: TenantManager):
    if rec.state == TenantRecord.STATE_DELETED:
        raise ValueError("Tenant is disabled")
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
