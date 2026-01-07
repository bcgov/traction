import logging
from typing import Optional

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
from acapy_agent.ledger.error import LedgerError
from acapy_agent.ledger.multiple_ledger.ledger_requests_executor import (
    IndyLedgerRequestsExecutor,
    GET_CRED_DEF,
)
from acapy_agent.multitenant.base import BaseMultitenantManager
from acapy_agent.storage.error import StorageNotFoundError

from .models import CredDefStorageRecord

from acapy_agent.messaging.credential_definitions.util import (
    EVENT_LISTENER_PATTERN as CREDDEF_EVENT_LISTENER_PATTERN,
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

    async def add_item(self, profile: Profile, data: dict):
        self.logger.info(f"> add_item({data})")
        # check if
        cred_def_id = data.get("cred_def_id")
        if not cred_def_id:
            raise ValueError("cred_def_id is required in data")
        
        # Preserve rev_reg_size from original data before we potentially overwrite it
        original_rev_reg_size = data.get("rev_reg_size")
        if original_rev_reg_size is None and "options" in data:
            options = data.get("options", {})
            if isinstance(options, dict):
                original_rev_reg_size = options.get("revocation_registry_size")
        
        rec = await self.read_item(profile, cred_def_id)
        if not rec:
            # Check if we need to fetch from anoncreds registry or ledger
            is_anoncreds = self._is_anoncreds_wallet(profile)
            
            # Check if we have all required fields for storage record
            has_required_fields = all(key in data for key in ["schema_id", "tag"])
            
            if is_anoncreds and not has_required_fields:
                # Fetch anoncreds credential definition from registry
                try:
                    from acapy_agent.anoncreds.registry import AnonCredsRegistry
                    anoncreds_registry = profile.inject(AnonCredsRegistry)
                    cred_def_result = await anoncreds_registry.get_credential_definition(
                        profile, cred_def_id
                    )
                    
                    # Convert anoncreds credential definition to storage format
                    cred_def = cred_def_result.credential_definition
                    
                    # Determine support_revocation from the credential definition value
                    support_revocation = False
                    if hasattr(cred_def, 'value') and cred_def.value:
                        if hasattr(cred_def.value, 'revocation'):
                            support_revocation = cred_def.value.revocation is not None
                    
                    # Use the preserved rev_reg_size from original data, or try to extract it
                    rev_reg_size = original_rev_reg_size
                    if rev_reg_size is None:
                        # Try to get it from data (in case it wasn't preserved)
                        rev_reg_size = data.get("rev_reg_size")
                        if rev_reg_size is None and "options" in data:
                            options = data.get("options", {})
                            if isinstance(options, dict):
                                rev_reg_size = options.get("revocation_registry_size")
                    
                    # Update data with anoncreds credential definition info
                    # Preserve rev_reg_size if it was in the original data
                    data = {
                        "cred_def_id": cred_def_id,
                        "schema_id": cred_def.schema_id,
                        "tag": cred_def.tag or "default",
                        "support_revocation": support_revocation,
                        "rev_reg_size": rev_reg_size,
                    }
                    
                    self.logger.debug(f"anoncreds cred def = {data}")
                except Exception as err:
                    self.logger.error(f"Error fetching anoncreds credential definition: {err}")
                    # Fall back to using the provided data if available
                    if not data.get("schema_id"):
                        raise StorageNotFoundError(
                            f"AnonCreds credential definition not found: {cred_def_id}"
                        ) from err
            elif not is_anoncreds and not has_required_fields:
                # For Indy credential definitions, ensure we have all required fields
                # If missing, try to fetch from ledger
                try:
                    async with profile.session() as session:
                        multitenant_mgr = session.inject_or(BaseMultitenantManager)
                        if multitenant_mgr:
                            ledger_exec_inst = IndyLedgerRequestsExecutor(profile)
                        else:
                            ledger_exec_inst = session.inject(IndyLedgerRequestsExecutor)

                    ledger_id, ledger = await ledger_exec_inst.get_ledger_for_identifier(
                        cred_def_id,
                        txn_record_type=GET_CRED_DEF,
                    )
                    async with ledger:
                        try:
                            cred_def = await ledger.get_credential_definition(cred_def_id)
                            if cred_def:
                                # Extract missing fields from ledger response
                                if "schema_id" not in data:
                                    data["schema_id"] = cred_def.get("schemaId", "")
                                if "tag" not in data:
                                    data["tag"] = cred_def.get("tag", "default")
                                if "support_revocation" not in data:
                                    # Check if revocation is supported
                                    value = cred_def.get("value", {})
                                    data["support_revocation"] = value.get("revocation") is not None
                        except LedgerError as err:
                            self.logger.error(f"Error fetching cred def from ledger: {err}")
                except Exception as err:
                    self.logger.warning(f"Could not fetch cred def from ledger: {err}")
            
            try:
                rec: CredDefStorageRecord = CredDefStorageRecord.deserialize(data)
                self.logger.debug(f"cred_def_storage_rec = {rec}")
                async with profile.session() as session:
                    await rec.save(session, reason="New cred def storage record")
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
    bus.subscribe(CREDDEF_EVENT_LISTENER_PATTERN, creddef_event_handler)


async def creddef_event_handler(profile: Profile, event: Event):
    LOGGER.info("> creddef_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")
    srv = profile.inject(CredDefStorageService)
    storage_record = await srv.add_item(profile, event.payload["context"])
    LOGGER.debug(f"creddef_storage_record = {storage_record}")

    LOGGER.info("< creddef_event_handler")
