import logging
from typing import Optional

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.ledger.error import LedgerError
from aries_cloudagent.ledger.multiple_ledger.ledger_requests_executor import (
    IndyLedgerRequestsExecutor,
    GET_SCHEMA,
)
from aries_cloudagent.messaging.schemas.util import SCHEMA_SENT_RECORD_TYPE
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.storage.error import StorageNotFoundError

from .models import SchemaStorageRecord

LOGGER = logging.getLogger(__name__)


async def read_item(profile: Profile, schema_id: str):
    LOGGER.info(f"> read_item({schema_id})")
    try:
        async with profile.session() as session:
            rec = await SchemaStorageRecord.retrieve_by_id(session, schema_id)
            LOGGER.debug(rec)
    except StorageNotFoundError:
        # this is to be expected... do nothing, do not log
        rec = None
    except Exception as err:
        LOGGER.error(f"Error fetching schema storage record for id {schema_id}", err)
        rec = None

    LOGGER.info(f"< read_item({schema_id}): {rec}")
    return rec


async def list_items(
    profile: Profile, tag_filter: Optional[dict] = {}, post_filter: Optional[dict] = {}
):
    LOGGER.info(f"> list_items({tag_filter}, {post_filter})")

    records = []
    async with profile.session() as session:
        # innkeeper can access all reservation records
        records = await SchemaStorageRecord.query(
            session=session,
            tag_filter=tag_filter,
            post_filter_positive=post_filter,
            alt=True,
        )

    LOGGER.info(f"< list_items({tag_filter}, {post_filter}): {len(records)}")
    return records


async def add_item(profile: Profile, schema_id: str):
    LOGGER.info(f"> add_item({schema_id})")
    # check if
    rec = await read_item(profile, schema_id)
    if not rec:

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
        LOGGER.debug(f"ledger_id = {ledger_id}")
        async with ledger:
            try:
                schema = await ledger.get_schema(schema_id)
                LOGGER.debug(f"schema = {schema}")
            except LedgerError as err:
                LOGGER.error(err)

        try:
            data = {"schema_id": schema_id, "schema": schema}
            if ledger_id:
                data["ledger_id"] = ledger_id
            rec: SchemaStorageRecord = SchemaStorageRecord.deserialize(data)
            LOGGER.debug(f"schema_storage_rec = {rec}")
            async with profile.session() as session:
                await rec.save(session, reason="New schema storage record")
        except Exception as err:
            LOGGER.error(f"Error adding schema storage record.", err)
            raise err

    LOGGER.info(f"< add_item({schema_id}): {rec}")
    return rec


async def sync_created(profile: Profile):
    LOGGER.info("> sync_created()")

    # find all known schema ids that i created...
    session = await profile.session()
    storage = session.inject(BaseStorage)
    schema_ids = await storage.find_all_records(
        type_filter=SCHEMA_SENT_RECORD_TYPE,
        tag_query={},
    )
    LOGGER.info(f"created count = {len(schema_ids)}")

    # for all found... go get details from ledger and put schema into storage.
    for schema_id in schema_ids:
        await add_item(profile, schema_id.value)

    records = await list_items(profile)

    LOGGER.info(f"< sync_created(): {len(records)}")
    return records
