import logging
from typing import Optional

from acapy_agent.core.error import BaseError
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageDuplicateError, StorageNotFoundError
from acapy_agent.wallet.base import BaseWallet
from acapy_agent.wallet.did_info import DIDInfo
from acapy_agent.wallet.error import WalletError
from marshmallow import ValidationError

from .models import OcaRecord

LOGGER = logging.getLogger(__name__)


class PublicDIDRequiredError(BaseError):
    """Public DID Required exception."""


class PublicDIDMismatchError(BaseError):
    """Public DID Mismatch exception."""


class OcaService:
    def __init__(self, profile: Profile):
        self._profile = profile
        self._logger = logging.getLogger(__name__)

    @property
    def profile(self) -> Profile:
        """
        Accessor for the current profile.

        Returns:
            The profile for this service

        """
        return self._profile

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    async def get_public_did_info(self, issuer_profile: Profile):
        self.logger.info("> get_public_did_info()")
        result = None
        async with issuer_profile.session() as session:
            wallet = session.inject_or(BaseWallet)
            if not wallet:
                raise WalletError("Wallet not found")
            try:
                result = await wallet.get_public_did()
            except WalletError as err:
                raise err
        self.logger.info(f"< get_public_did_info() = {result}")
        return result

    async def get_public_did(self, issuer_profile: Profile, raise_err: bool = False):
        self.logger.info("> get_public_did()")
        result = None
        public_info = await self.get_public_did_info(issuer_profile)
        if public_info and public_info.did:
            result = public_info.did
        else:
            if raise_err:
                raise PublicDIDRequiredError()
        self.logger.info(f"< get_public_did() = {result}")
        return result

    def is_cred_def_owner(self, issuer_did: str, cred_def_id: str):
        self.logger.info(f"> is_cred_def_owner({issuer_did}, {cred_def_id})")
        data_did = None
        result = False
        try:
            if cred_def_id:
                data_did = cred_def_id.split(":")[0]
            result = issuer_did == data_did
        except Exception as err:
            raise err
        self.logger.info(f"< is_cred_def_owner() = {result}")
        return result

    def validate_oca_data(self, issuer_did: str, oca_data: dict):
        # must have schema id, cred def id, one of url or bundle
        # must be the issuer
        message = {}
        schema_id = oca_data.get("schema_id")
        cred_def_id = oca_data.get("cred_def_id")
        if not schema_id:
            message["schema_id"] = "Schema ID is required."
        if not cred_def_id:
            message["cred_def_id"] = "Credential Definition ID is required."
        if cred_def_id and not self.is_cred_def_owner(issuer_did, cred_def_id):
            message["cred_def_id"] = "Credential Definition not created by caller"
        if not oca_data.get("url") and not oca_data.get("bundle"):
            message["url"] = "URL or bundle is required"

        if message != {}:
            raise ValidationError(message=message, data=oca_data)

        return True

    def build_tag_filter(self, schema_id: Optional[str], cred_def_id: Optional[str]):
        result = {}
        if schema_id:
            result["schema_id"] = schema_id
        if cred_def_id:
            result["cred_def_id"] = cred_def_id
        return result

    def build_post_filter(self, public_info: Optional[DIDInfo]):
        result = {}
        if public_info and public_info.did:
            result = {"owner_did": public_info.did}
        return result

    async def list_oca_records(
        self,
        issuer_profile: Profile,
        schema_id: Optional[str],
        cred_def_id: Optional[str],
    ):
        self.logger.info(
            f"> list_oca_records({issuer_profile}, {schema_id}, {cred_def_id})"
        )
        is_root_profile = issuer_profile == self.profile
        public_info = await self.get_public_did_info(issuer_profile)
        tag_filter = self.build_tag_filter(schema_id, cred_def_id)
        post_filter = {} if is_root_profile else self.build_post_filter(public_info)
        records = []
        if is_root_profile or public_info:
            self.logger.info(f"post_filter = {post_filter}")
            async with self.profile.session() as session:
                records = await OcaRecord.query(
                    session=session,
                    tag_filter=tag_filter,
                    post_filter_positive=post_filter,
                    alt=True,
                )
        else:
            # error
            self.logger.error("Profile does not have access to this function.")
        self.logger.info(f"< list_oca_records({tag_filter}): {len(records)}")
        return records

    async def find_or_new_oca_record(
        self, issuer_profile: Profile, oca_data: dict, update: bool = True
    ):
        self.logger.info(
            f"> find_or_new_oca_record({issuer_profile}, {oca_data}, update={update})"
        )
        public_info = await self.get_public_did_info(issuer_profile)
        tag_filter = self.build_tag_filter(
            oca_data.get("schema_id"), oca_data.get("cred_def_id")
        )
        post_filter = self.build_post_filter(public_info)
        async with self.profile.session() as session:
            records = await OcaRecord.query(
                session=session,
                tag_filter=tag_filter,
                post_filter_positive=post_filter,
                alt=True,
            )
        if len(records) > 1:
            raise StorageDuplicateError(
                "More than one OCA record was found for the given criteria"
            )
        elif len(records) == 1:
            self.logger.info("... found existing record ...")
            record = records[0]
            if update:
                record.bundle = oca_data.get("bundle")
                record.url = oca_data.get("url")
            self.logger.info(f"< find_or_new_oca_record() = {record}")
            return record
        else:
            self.logger.info("... creating new record ...")
            record = OcaRecord(
                schema_id=oca_data.get("schema_id"),
                cred_def_id=oca_data.get("cred_def_id"),
                url=oca_data.get("url"),
                bundle=oca_data.get("bundle"),
                owner_did=public_info.did,
            )
            self.logger.info(f"< find_or_new_oca_record() = {record}")
            return record

    async def create_or_update_oca_record(
        self, issuer_profile: Profile, oca_data: dict
    ):
        self.logger.info(f"> create_or_update_oca_record({issuer_profile}, {oca_data})")
        public_did = await self.get_public_did(issuer_profile, True)
        if self.validate_oca_data(public_did, oca_data):
            # validate that schema id and cred def id are present and match
            rec = await self.find_or_new_oca_record(issuer_profile, oca_data, True)
            try:
                self.logger.debug(f"oca_record = {rec}")
                async with self.profile.session() as session:
                    await rec.save(session, reason="Create/Update OCA record")
                self.logger.info(f"< create_or_update_oca_record() = {rec}")
                return rec
            except Exception as err:
                self.logger.error("Error creating or updating OCA record.", err)
                raise err

    async def read_oca_record(self, issuer_profile: Profile, oca_id: str):
        self.logger.info(f"> read_oca_record({issuer_profile}, {oca_id})")
        public_did = await self.get_public_did(issuer_profile, True)
        async with self.profile.session() as session:
            rec = await OcaRecord.retrieve_by_id(session, oca_id)
            # must exist, caller must be the owner...
            if rec.owner_did != public_did:
                raise PublicDIDMismatchError()

            await rec.save(session)
        self.logger.info(f"< read_oca_record({oca_id}) = {rec}")
        return rec

    async def update_oca_record(
        self, issuer_profile: Profile, oca_id: str, oca_data: dict
    ):
        self.logger.info(f"> update_oca_record({issuer_profile}, {oca_id}, {oca_data})")
        public_did = await self.get_public_did(issuer_profile, True)
        async with self.profile.session() as session:
            rec = await OcaRecord.retrieve_by_id(session, oca_id, for_update=True)
            # must exist, caller must be the owner...
            if rec.owner_did != public_did:
                raise PublicDIDMismatchError()

            if not oca_data.get("url") and not oca_data.get("bundle"):
                raise ValidationError("URL or bundle is required")

            rec.url = oca_data.get("url")
            rec.bundle = oca_data.get("bundle")

            await rec.save(session)
        self.logger.info(f"< update_oca_record({oca_id}) = {rec}")
        return rec

    async def delete_oca_record(self, issuer_profile: Profile, oca_id: str):
        self.logger.info(f"> delete_oca_record({issuer_profile}, {oca_id})")
        public_did = await self.get_public_did(issuer_profile, True)
        result = False
        async with self.profile.session() as session:
            rec = await OcaRecord.retrieve_by_id(session, oca_id, for_update=True)
            # must exist, caller must be the owner...
            if rec.owner_did != public_did:
                raise PublicDIDMismatchError()

            await rec.delete_record(session)

            try:
                await OcaRecord.retrieve_by_id(session, oca_id)
            except StorageNotFoundError:
                # this is to be expected... do nothing, do not log
                result = True
        self.logger.info(f"< delete_oca_record({oca_id}) = {result}")
        return result
