import logging
from typing import Optional

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.ledger.error import LedgerError
from aries_cloudagent.ledger.multiple_ledger.ledger_requests_executor import (
    IndyLedgerRequestsExecutor,
    GET_CRED_DEF,
)
from aries_cloudagent.messaging.credential_definitions.util import (
    CRED_DEF_SENT_RECORD_TYPE,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.storage.error import StorageNotFoundError

from .models import CredDefStorageRecord

LOGGER = logging.getLogger(__name__)


async def read_item(profile: Profile, cred_def_id: str):
    LOGGER.info(f"> read_item({cred_def_id})")
    try:
        async with profile.session() as session:
            rec = await CredDefStorageRecord.retrieve_by_id(session, cred_def_id)
            LOGGER.debug(rec)
    except StorageNotFoundError:
        # this is to be expected... do nothing, do not log
        rec = None
    except Exception as err:
        LOGGER.error(
            f"Error fetching cred def storage record for id {cred_def_id}", err
        )
        rec = None

    LOGGER.info(f"< read_item({cred_def_id}): {rec}")
    return rec


async def list_items(
    profile: Profile, tag_filter: Optional[dict] = {}, post_filter: Optional[dict] = {}
):
    LOGGER.info(f"> list_items({tag_filter}, {post_filter})")

    records = []
    async with profile.session() as session:
        # innkeeper can access all reservation records
        records = await CredDefStorageRecord.query(
            session=session,
            tag_filter=tag_filter,
            post_filter_positive=post_filter,
            alt=True,
        )

    LOGGER.info(f"< list_items({tag_filter}, {post_filter}): {len(records)}")
    return records


async def add_item(profile: Profile, data: dict):
    LOGGER.info(f"> add_item({data})")
    # check if
    cred_def_id = data["cred_def_id"]
    rec = await read_item(profile, cred_def_id)
    if not rec:
        try:
            rec: CredDefStorageRecord = CredDefStorageRecord.deserialize(data)
            LOGGER.debug(f"cred_def_storage_rec = {rec}")
            async with profile.session() as session:
                await rec.save(session, reason="New cred def storage record")
        except Exception as err:
            LOGGER.error(f"Error adding cred def storage record.", err)
            raise err

    LOGGER.info(f"< add_item({cred_def_id}): {rec}")
    return rec
