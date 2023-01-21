import logging
from typing import Optional

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.ledger.error import LedgerError
from aries_cloudagent.ledger.multiple_ledger.ledger_requests_executor import (
    IndyLedgerRequestsExecutor,
    GET_SCHEMA,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.storage.error import StorageNotFoundError

from .models import SchemaCacheRecord

LOGGER = logging.getLogger(__name__)


async def get_schema_from_cache(profile: Profile, schema_id: str):
    LOGGER.info(f"> get_schema_from_cache({schema_id})")
    try:
        async with profile.session() as session:
            rec = await SchemaCacheRecord.retrieve_by_id(session, schema_id)
            LOGGER.debug(rec)
    except StorageNotFoundError:
        # this is to be expected... do nothing, do not log
        rec = None
    except Exception as err:
        LOGGER.error(f"Error fetching schema cache record for id {schema_id}", err)
        rec = None

    LOGGER.info(f"< get_schema_from_cache({schema_id}): {rec}")
    return rec


async def list_schemas_from_cache(
    profile: Profile, tag_filter: Optional[dict] = {}, post_filter: Optional[dict] = {}
):
    LOGGER.info(f"> list_schemas_from_cache({tag_filter}, {post_filter})")

    records = []
    async with profile.session() as session:
        # innkeeper can access all reservation records
        records = await SchemaCacheRecord.query(
            session=session,
            tag_filter=tag_filter,
            post_filter_positive=post_filter,
            alt=True,
        )

    LOGGER.info(
        f"< list_schemas_from_cache({tag_filter}, {post_filter}): {len(records)}"
    )
    return records


async def add_schema_to_cache(profile: Profile, schema_id: str):
    LOGGER.info(f"> add_schema_to_cache({schema_id})")
    # check if
    rec = await get_schema_from_cache(profile, schema_id)
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
            rec: SchemaCacheRecord = SchemaCacheRecord.deserialize(data)
            LOGGER.debug(f"schema_cache_rec = {rec}")
            async with profile.session() as session:
                await rec.save(session, reason="New schema cache record")
        except Exception as err:
            LOGGER.error(f"Error adding schema cache record.", err)
            raise err

    LOGGER.info(f"< add_schema_to_cache({schema_id}): {rec}")
    return rec
