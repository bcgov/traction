import logging
from typing import Optional

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
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

    async def add_item(self, profile: Profile, data: dict):
        self.logger.info(f"> add_item({data})")
        # check if
        cred_def_id = data["cred_def_id"]
        rec = await self.read_item(profile, cred_def_id)
        if not rec:
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
