import logging
from typing import Optional

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
    EVENT_LISTENER_PATTERN as SCHEMAS_EVENT_LISTENER_PATTERN,
)

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

    async def add_item(
        self, profile: Profile, schema_id: str, is_anoncreds: Optional[bool] = None
    ):
        self.logger.info(f"> add_item({schema_id})")
        # check if
        rec = await self.read_item(profile, schema_id)
        if not rec:
            schema = None
            ledger_id = None

            # Auto-detect if anoncreds based on wallet type if not explicitly specified
            if is_anoncreds is None:
                is_anoncreds = self._is_anoncreds_wallet(profile)

            if is_anoncreds:
                # Fetch anoncreds schema from registry
                # Retry logic: schema might not be immediately available after transaction
                from acapy_agent.anoncreds.registry import AnonCredsRegistry
                import asyncio

                anoncreds_registry = profile.inject(AnonCredsRegistry)

                max_retries = 3
                base_delay = 1.0  # seconds - base delay for exponential backoff
                schema_result = None

                for attempt in range(max_retries):
                    try:
                        schema_result = await anoncreds_registry.get_schema(
                            profile, schema_id
                        )
                        break  # Success, exit retry loop
                    except Exception as err:
                        if attempt < max_retries - 1:
                            # Exponential backoff: delay = base_delay * (2 ^ attempt)
                            delay = base_delay * (2**attempt)
                            self.logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} failed to fetch anoncreds schema {schema_id}, retrying in {delay}s: {err}"
                            )
                            await asyncio.sleep(delay)
                        else:
                            self.logger.error(
                                f"Error fetching anoncreds schema after {max_retries} attempts: {err}"
                            )
                            raise StorageNotFoundError(
                                f"AnonCreds schema not found: {schema_id}"
                            ) from err

                if schema_result is None:
                    raise StorageNotFoundError(
                        f"AnonCreds schema not found: {schema_id}"
                    )

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
                if schema_result.resolution_metadata:
                    ledger_id = schema_result.resolution_metadata.get("ledger_id")

                self.logger.debug(f"anoncreds schema = {schema}")
            else:
                # Fetch Indy schema from ledger
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

                if schema is None:
                    raise StorageNotFoundError(
                        f"Schema not found on ledger: {schema_id}"
                    )
                schema_dict = schema

            try:
                data = {
                    "schema_id": schema_id,
                    "schema": schema,
                    "schema_dict": schema_dict,
                }
                if ledger_id:
                    data["ledger_id"] = ledger_id
                rec: SchemaStorageRecord = SchemaStorageRecord.deserialize(data)
                self.logger.debug(f"schema_storage_rec = {rec}")
                async with profile.session() as session:
                    await rec.save(session, reason="New schema storage record")
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
            await self.add_item(profile, schema_id.value)

        records = await self.list_items(profile)

        self.logger.info(f"< sync_created(): {len(records)}")
        return records


def subscribe(bus: EventBus):
    bus.subscribe(SCHEMAS_EVENT_LISTENER_PATTERN, schemas_event_handler)


async def schemas_event_handler(profile: Profile, event: Event):
    LOGGER.info("> schemas_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")

    try:
        schema_id = event.payload["context"]["schema_id"]
        srv = profile.inject(SchemaStorageService)
        # add_item will auto-detect if it's anoncreds based on wallet type
        schema_storage_record = await srv.add_item(profile, schema_id)
        LOGGER.debug(f"schema_storage_record = {schema_storage_record}")
    except Exception as err:
        LOGGER.error(
            f"Error in schemas_event_handler for schema_id {event.payload.get('context', {}).get('schema_id', 'unknown')}: {err}",
            exc_info=True,
        )
        raise

    LOGGER.info("< schemas_event_handler")
