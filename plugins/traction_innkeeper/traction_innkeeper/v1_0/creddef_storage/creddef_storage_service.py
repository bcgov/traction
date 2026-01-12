import logging
import re
from typing import Optional

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError

from .models import CredDefStorageRecord

from acapy_agent.messaging.credential_definitions.util import (
    EVENT_LISTENER_PATTERN as INDY_CREDDEF_EVENT_PATTERN,
)
from acapy_agent.anoncreds.events import (
    CRED_DEF_FINISHED_EVENT as ANONCREDS_CREDDEF_FINISHED_EVENT,
)

LOGGER = logging.getLogger(__name__)


class CredDefStorageService:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    async def read_item(self, profile: Profile, cred_def_id: str):
        self.logger.info(f"> read_item({cred_def_id})")
        try:
            async with profile.session() as session:
                rec = await CredDefStorageRecord.retrieve_by_id(session, cred_def_id)
                self.logger.debug(rec)
        except StorageNotFoundError:
            # this is to be expected... do nothing, do not log
            rec = None
        except Exception as err:
            self.logger.error(
                f"Error fetching cred def storage record for id {cred_def_id}", err
            )
            rec = None

        self.logger.info(f"< read_item({cred_def_id}): {rec}")
        return rec

    async def list_items(
        self,
        profile: Profile,
        tag_filter: Optional[dict] = {},
        post_filter: Optional[dict] = {},
    ):
        self.logger.info(f"> list_items({tag_filter}, {post_filter})")

        records = []
        async with profile.session() as session:
            # innkeeper can access all reservation records
            records = await CredDefStorageRecord.query(
                session=session,
                tag_filter=tag_filter,
                post_filter_positive=post_filter,
                alt=True,
            )

        self.logger.info(f"< list_items({tag_filter}, {post_filter}): {len(records)}")
        return records

    def _is_anoncreds_wallet(self, profile: Profile) -> bool:
        """Check if the wallet is an anoncreds wallet."""
        wallet_type = profile.settings.get("wallet.type", "askar")
        return wallet_type in ("askar-anoncreds", "kanon-anoncreds")

    async def _fetch_tag(
        self,
        profile: Profile,
        cred_def_id: str,
    ) -> Optional[str]:
        """Fetch tag from registry for AnonCreds credential definitions.

        AnonCreds events never include tag in the event payload, so we must fetch it from the registry.
        This function is only called for AnonCreds credential definitions.

        Returns tag from registry, or None if fetch fails.
        """
        from acapy_agent.anoncreds.registry import AnonCredsRegistry
        from acapy_agent.anoncreds.base import AnonCredsResolutionError

        try:
            anoncreds_registry = profile.inject(AnonCredsRegistry)
            cred_def_result = await anoncreds_registry.get_credential_definition(
                profile, cred_def_id
            )

            cred_def = cred_def_result.credential_definition
            tag = cred_def.tag or "default"

            self.logger.debug(f"Fetched tag from registry: {tag}")
            return tag
        except AnonCredsResolutionError:
            # Registry doesn't support this identifier
            self.logger.error(
                f"Registry could not resolve credential definition: {cred_def_id}"
            )
            return None
        except Exception as err:
            # Other errors from registry (e.g., network issues, injection errors)
            self.logger.error(
                f"Error fetching credential definition from registry: {err}"
            )
            return None

    async def _create_storage_record(
        self, profile: Profile, data: dict
    ) -> CredDefStorageRecord:
        """Create and save a credential definition storage record."""
        rec: CredDefStorageRecord = CredDefStorageRecord.deserialize(data)
        self.logger.debug(f"cred_def_storage_rec = {rec}")
        async with profile.session() as session:
            await rec.save(session, reason="New cred def storage record")
        return rec

    async def add_item(self, profile: Profile, data: dict):
        self.logger.info(f"> add_item({data})")
        cred_def_id = data.get("cred_def_id")
        if not cred_def_id:
            raise ValueError("cred_def_id is required in data")

        # Early return if record already exists
        rec = await self.read_item(profile, cred_def_id)
        if rec:
            self.logger.info(f"< add_item({cred_def_id}): {rec}")
            return rec

        # Fetch tag from registry for AnonCreds credential definitions
        # AnonCreds events never include tag, so we must fetch it
        if self._is_anoncreds_wallet(profile):
            tag = await self._fetch_tag(profile, cred_def_id)
            if tag:
                data["tag"] = tag

        # Create and save the storage record
        try:
            rec = await self._create_storage_record(profile, data)
        except Exception as err:
            self.logger.error("Error adding cred def storage record.", err)
            raise err

        self.logger.info(f"< add_item({cred_def_id}): {rec}")
        return rec

    async def remove_item(self, profile: Profile, cred_def_id: str):
        self.logger.info(f"> remove_item({cred_def_id})")
        result = False
        try:
            async with profile.session() as session:
                self.logger.info("fetch record...")
                rec = await CredDefStorageRecord.retrieve_by_id(session, cred_def_id)
                self.logger.info(rec)
                self.logger.info("delete record...")
                await rec.delete_record(session)
                self.logger.info("fetch record again... should throw not found")
                await CredDefStorageRecord.retrieve_by_id(session, cred_def_id)
        except StorageNotFoundError:
            self.logger.info("record not found!!!")
            # this is to be expected... do nothing, do not log
            result = True
        except Exception as err:
            self.logger.error(
                f"Error removing cred def storage record for id {cred_def_id}", err
            )

        self.logger.info(f"< remove_item({cred_def_id}): {result}")
        return result


def subscribe(bus: EventBus):
    # Subscribe to both Indy and AnonCreds credential definition events
    bus.subscribe(INDY_CREDDEF_EVENT_PATTERN, creddef_event_handler)
    # Explicitly compile as literal pattern to ensure it's a Pattern object, not a string
    bus.subscribe(
        re.compile(re.escape(ANONCREDS_CREDDEF_FINISHED_EVENT)), creddef_event_handler
    )


def _normalize_creddef_event_payload(event: Event) -> dict:
    """Normalize credential definition event payload from either Indy (dict with context) or AnonCreds (NamedTuple) format.

    AnonCreds events use CredDefFinishedPayload NamedTuple (not a dict), so we check for
    NamedTuple attributes and convert to a dict format for unified processing.
    """
    payload = event.payload

    # Check if it's an AnonCreds event (NamedTuple)
    # AnonCreds events are CredDefFinishedPayload NamedTuples, not dicts
    if hasattr(payload, "schema_id") and hasattr(payload, "cred_def_id"):
        # AnonCreds event: CredDefFinishedPayload NamedTuple
        rev_reg_size = payload.max_cred_num if payload.support_revocation else None
        return {
            "cred_def_id": payload.cred_def_id,
            "schema_id": payload.schema_id,
            "tag": None,  # NEVER in AnonCreds event, must be fetched from registry
            "support_revocation": payload.support_revocation,
            "rev_reg_size": rev_reg_size,  # Always set (from max_cred_num)
            "issuer_id": payload.issuer_id,
            "options": payload.options,  # Preserve for any other fields
        }
    elif isinstance(payload, dict) and "context" in payload:
        # Indy event: dict with "context" key
        context = payload["context"]
        return {
            "cred_def_id": context.get("cred_def_id"),
            "schema_id": context.get("schema_id"),
            "tag": context.get("tag"),
            "support_revocation": context.get("support_revocation", False),
            "rev_reg_size": context.get("rev_reg_size"),
            "issuer_did": context.get("issuer_did"),
            "options": context.get("options", {}),
        }
    else:
        # Fallback: assume it's already in the right format
        return payload if isinstance(payload, dict) else {}


async def creddef_event_handler(profile: Profile, event: Event):
    LOGGER.info("> creddef_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")
    LOGGER.debug(f"event.payload = {event.payload}")

    srv = profile.inject(CredDefStorageService)

    # Normalize event payload to common format
    normalized_data = _normalize_creddef_event_payload(event)
    LOGGER.debug(f"normalized_data = {normalized_data}")

    storage_record = await srv.add_item(profile, normalized_data)
    LOGGER.debug(f"creddef_storage_record = {storage_record}")

    LOGGER.info("< creddef_event_handler")
