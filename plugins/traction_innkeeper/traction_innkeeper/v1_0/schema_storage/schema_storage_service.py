import logging
import re
from typing import Optional, Tuple

from acapy_agent.core.event_bus import Event, EventBus
from acapy_agent.core.profile import Profile
from acapy_agent.ledger.error import LedgerError
from acapy_agent.ledger.multiple_ledger.ledger_requests_executor import (
    IndyLedgerRequestsExecutor,
    GET_SCHEMA,
)
from acapy_agent.messaging.schemas.util import SCHEMA_SENT_RECORD_TYPE
from acapy_agent.multitenant.base import BaseMultitenantManager
from acapy_agent.storage.base import BaseStorage
from acapy_agent.storage.error import StorageNotFoundError

from .models import SchemaStorageRecord
from acapy_agent.messaging.schemas.util import (
    EVENT_LISTENER_PATTERN as INDY_SCHEMA_EVENT_PATTERN,
)

# Try to import ANONCREDS_SCHEMA_FINISHED_EVENT, but handle the case where it doesn't exist
# (e.g., if using an older version of acapy that doesn't have this event yet)
try:
    from acapy_agent.anoncreds.events import (
        SCHEMA_FINISHED_EVENT as ANONCREDS_SCHEMA_FINISHED_EVENT,
    )
except (ImportError, AttributeError):
    # If the event doesn't exist, we'll only subscribe to Indy events
    ANONCREDS_SCHEMA_FINISHED_EVENT = None

LOGGER = logging.getLogger(__name__)


class SchemaStorageService:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    async def read_item(self, profile: Profile, schema_id: str):
        self.logger.info(f"> read_item({schema_id})")
        try:
            async with profile.session() as session:
                rec = await SchemaStorageRecord.retrieve_by_id(session, schema_id)
                self.logger.debug(rec)
        except StorageNotFoundError:
            # this is to be expected... do nothing, do not log
            rec = None
        except Exception as err:
            self.logger.error(
                f"Error fetching schema storage record for id {schema_id}", err
            )
            rec = None

        self.logger.info(f"< read_item({schema_id}): {rec}")
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
            records = await SchemaStorageRecord.query(
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

    async def _fetch_schema_from_registry(
        self, profile: Profile, schema_id: str
    ) -> Tuple[dict, dict, Optional[str]]:
        """Fetch AnonCreds schema from registry.

        Returns:
            tuple: (schema dict, schema_dict, ledger_id)
        """
        from acapy_agent.anoncreds.registry import AnonCredsRegistry
        from acapy_agent.anoncreds.base import AnonCredsResolutionError

        try:
            anoncreds_registry = profile.inject(AnonCredsRegistry)
            schema_result = await anoncreds_registry.get_schema(profile, schema_id)

            # Convert anoncreds schema to storage format
            anoncreds_schema = schema_result.schema
            schema = {
                "id": schema_id,
                "name": anoncreds_schema.name,
                "version": anoncreds_schema.version,
                "attrNames": anoncreds_schema.attr_names,
                "issuerId": anoncreds_schema.issuer_id,
            }
            # Store the full schema_dict for anoncreds (serialized format)
            schema_dict = anoncreds_schema.serialize()

            # Extract ledger_id from resolution_metadata if available
            ledger_id = None
            if schema_result.resolution_metadata:
                ledger_id = schema_result.resolution_metadata.get("ledger_id")

            self.logger.debug(f"anoncreds schema = {schema}")
            return schema, schema_dict, ledger_id
        except AnonCredsResolutionError:
            # Registry doesn't support this identifier
            self.logger.error(f"Registry could not resolve schema: {schema_id}")
            raise StorageNotFoundError(f"AnonCreds schema not found: {schema_id}")
        except Exception as err:
            # Other errors from registry (e.g., network issues, injection errors)
            self.logger.error(f"Error fetching schema from registry: {err}")
            raise StorageNotFoundError(
                f"AnonCreds schema not found: {schema_id}"
            ) from err

    async def _fetch_schema_from_ledger(
        self, profile: Profile, schema_id: str
    ) -> Tuple[dict, dict, Optional[str]]:
        """Fetch Indy schema from ledger.

        Returns:
            tuple: (schema dict, schema_dict, ledger_id)
        """
        async with profile.session() as session:
            multitenant_mgr = session.inject_or(BaseMultitenantManager)
            if multitenant_mgr:
                ledger_exec_inst = IndyLedgerRequestsExecutor(profile)
            else:
                ledger_exec_inst = session.inject(IndyLedgerRequestsExecutor)

        ledger_id, ledger = await ledger_exec_inst.get_ledger_for_identifier(
            schema_id,
            txn_record_type=GET_SCHEMA,
        )
        self.logger.debug(f"ledger_id = {ledger_id}")
        async with ledger:
            try:
                schema = await ledger.get_schema(schema_id)
                self.logger.debug(f"indy schema = {schema}")
            except LedgerError as err:
                self.logger.error(err)
                schema = None

        if schema is None:
            raise StorageNotFoundError(f"Schema not found on ledger: {schema_id}")

        return schema, schema, ledger_id

    async def _create_storage_record(
        self, profile: Profile, data: dict
    ) -> SchemaStorageRecord:
        """Create and save a schema storage record."""
        rec: SchemaStorageRecord = SchemaStorageRecord.deserialize(data)
        self.logger.debug(f"schema_storage_rec = {rec}")
        async with profile.session() as session:
            await rec.save(session, reason="New schema storage record")
        return rec

    async def add_item(self, profile: Profile, data: dict):
        self.logger.info(f"> add_item({data})")
        schema_id = data.get("schema_id")
        if not schema_id:
            raise ValueError("schema_id is required in data")

        # Early return if record already exists
        rec = await self.read_item(profile, schema_id)
        if rec:
            self.logger.info(f"< add_item({schema_id}): {rec}")
            return rec

        # Auto-detect if anoncreds based on wallet type
        is_anoncreds = self._is_anoncreds_wallet(profile)

        # Fetch schema from registry or ledger if schema_dict is not provided
        if "schema_dict" not in data:
            if is_anoncreds:
                schema, schema_dict, ledger_id = await self._fetch_schema_from_registry(
                    profile, schema_id
                )
            else:
                schema, schema_dict, ledger_id = await self._fetch_schema_from_ledger(
                    profile, schema_id
                )

            # Update data with fetched information
            data["schema"] = schema
            data["schema_dict"] = schema_dict
            if ledger_id:
                data["ledger_id"] = ledger_id
        else:
            # schema_dict already provided, build schema dict if not present
            if "schema" not in data:
                # Build schema dict from provided data
                data["schema"] = {
                    "id": schema_id,
                    "name": data.get("name", ""),
                    "version": data.get("version", ""),
                    "attrNames": data.get("attr_names", []),
                    "issuerId": data.get("issuer_id", ""),
                }

        # Create and save the storage record
        try:
            rec = await self._create_storage_record(profile, data)
        except Exception as err:
            self.logger.error("Error adding schema storage record.", err)
            raise err

        self.logger.info(f"< add_item({schema_id}): {rec}")
        return rec

    async def remove_item(self, profile: Profile, schema_id: str):
        self.logger.info(f"> remove_item({schema_id})")
        result = True
        try:
            async with profile.session() as session:
                self.logger.info("fetch record...")
                rec = await SchemaStorageRecord.retrieve_by_id(session, schema_id)
                self.logger.info(rec)
                self.logger.info("delete record...")
                await rec.delete_record(session)
                self.logger.info("fetch record again... should throw not found")
                await SchemaStorageRecord.retrieve_by_id(session, schema_id)
        except StorageNotFoundError:
            self.logger.info("record not found!!!")
            # this is to be expected... do nothing, do not log
            result = True
        except Exception as err:
            self.logger.error(
                f"Error removing schema storage record for id {schema_id}", err
            )

        self.logger.info(f"< remove_item({schema_id}): {result}")
        return result

    async def sync_created(self, profile: Profile):
        self.logger.info("> sync_created()")

        # find all known schema ids that i created...
        session = await profile.session()
        storage = session.inject(BaseStorage)
        schema_ids = await storage.find_all_records(
            type_filter=SCHEMA_SENT_RECORD_TYPE,
            tag_query={},
        )
        self.logger.debug(f"created count = {len(schema_ids)}")

        # for all found... go get details from ledger and put schema into storage.
        for schema_id in schema_ids:
            await self.add_item(profile, {"schema_id": schema_id.value})

        records = await self.list_items(profile)

        self.logger.info(f"< sync_created(): {len(records)}")
        return records


def subscribe(bus: EventBus):
    # Subscribe to Indy schema events
    bus.subscribe(INDY_SCHEMA_EVENT_PATTERN, schemas_event_handler)
    # Subscribe to AnonCreds schema events if available
    # Explicitly compile as literal pattern to ensure it's a Pattern object, not a string
    if ANONCREDS_SCHEMA_FINISHED_EVENT:
        bus.subscribe(
            re.compile(re.escape(ANONCREDS_SCHEMA_FINISHED_EVENT)),
            schemas_event_handler,
        )


def _normalize_schema_event_payload(event: Event) -> dict:
    """Normalize schema event payload from either Indy (dict with context) or AnonCreds (NamedTuple) format.

    AnonCreds events use SchemaFinishedPayload NamedTuple (not a dict), so we check the event topic
    to determine the format and convert to a dict format for unified processing.
    """
    payload = event.payload

    # Check event topic to determine if it's AnonCreds or Indy
    if (
        ANONCREDS_SCHEMA_FINISHED_EVENT
        and event.topic == ANONCREDS_SCHEMA_FINISHED_EVENT
    ):
        # AnonCreds event: SchemaFinishedPayload NamedTuple
        if hasattr(payload, "schema_id"):
            return {
                "schema_id": payload.schema_id,
                "issuer_id": payload.issuer_id,
                "name": payload.name,
                "version": payload.version,
                "attr_names": payload.attr_names,
                "options": payload.options,
            }
    elif isinstance(payload, dict) and "context" in payload:
        # Indy event: dict with "context" key (pattern-based event)
        context = payload["context"]
        return {
            "schema_id": context.get("schema_id"),
            "issuer_id": context.get("issuer_id"),
            "name": context.get("name"),
            "version": context.get("version"),
            "attr_names": context.get("attr_names"),
            "options": context.get("options", {}),
        }

    # Fallback: assume it's already in the right format or extract schema_id
    if isinstance(payload, dict):
        return payload
    elif isinstance(payload, str):
        # Legacy: just schema_id string
        return {"schema_id": payload}
    elif hasattr(payload, "schema_id"):
        # AnonCreds-like payload but topic check didn't match
        return {
            "schema_id": payload.schema_id,
            "issuer_id": getattr(payload, "issuer_id", None),
            "name": getattr(payload, "name", None),
            "version": getattr(payload, "version", None),
            "attr_names": getattr(payload, "attr_names", []),
            "options": getattr(payload, "options", {}),
        }
    return {}


async def schemas_event_handler(profile: Profile, event: Event):
    LOGGER.info("> schemas_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")
    LOGGER.debug(f"event.payload = {event.payload}")

    try:
        normalized_data = _normalize_schema_event_payload(event)
        if not normalized_data.get("schema_id"):
            raise ValueError("Could not extract schema_id from event payload")

        srv = profile.inject(SchemaStorageService)
        # add_item will auto-detect if it's anoncreds based on wallet type
        schema_storage_record = await srv.add_item(profile, normalized_data)
        LOGGER.debug(f"schema_storage_record = {schema_storage_record}")
    except Exception as err:
        LOGGER.error(
            f"Error in schemas_event_handler for event {event}: {err}",
            exc_info=True,
        )
        raise

    LOGGER.info("< schemas_event_handler")
