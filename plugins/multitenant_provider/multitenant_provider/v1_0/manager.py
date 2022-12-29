import logging
from datetime import datetime, timezone

import bcrypt
import jwt
from aries_cloudagent.askar.profile import AskarProfile
from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.error import BaseError
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.multitenant.askar_profile_manager import (
    AskarProfileMultitenantManager,
)
from aries_cloudagent.multitenant.base import (
    MultitenantManagerError,
)
from aries_cloudagent.multitenant.error import WalletKeyMissingError
from aries_cloudagent.multitenant.manager import MultitenantManager
from aries_cloudagent.storage.error import StorageError
from aries_cloudagent.wallet.models.wallet_record import WalletRecord

from .config import MultitenantProviderConfig
from .models import WalletTokenRecord


class WalletKeyMismatchError(BaseError):
    """Wallet key mismatch exception."""


class MulittokenHandler:
    def __init__(self, manager: MultitenantManager):
        self.manager = manager
        self.logger = logging.getLogger(__class__.__name__)

    def get_profile(self):
        return self.manager._profile

    async def find_or_create_wallet_token_record(
        self, wallet_id: str, wallet_key: str = None
    ):
        # first, try and find the wallet token record
        try:
            async with self.get_profile().session() as session:
                return await WalletTokenRecord.query_by_wallet_id(session, wallet_id)
        except StorageError:
            async with self.get_profile().session() as session:
                # need the wallet record...
                wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)
                # determine what wallet_key to use...
                token_key = (
                    wallet_key
                    if wallet_record.requires_external_key
                    else wallet_record.wallet_key
                )
                # hash and salt...
                wallet_key_salt = bcrypt.gensalt()
                wallet_key_hash = bcrypt.hashpw(
                    token_key.encode("utf-8"), wallet_key_salt
                )
                # save the hash and salt for security checks.
                wallet_token_record = WalletTokenRecord(
                    wallet_id=wallet_record.wallet_id,
                    wallet_key_salt=wallet_key_salt.decode("utf-8"),
                    wallet_key_hash=wallet_key_hash.decode("utf-8"),
                )
                await wallet_token_record.save(session)
                self.logger.debug(wallet_token_record)

            return wallet_token_record

    def check_wallet_key(self, wallet_token_record: WalletTokenRecord, wallet_key: str):
        # make a hash from passed in value with saved salt...
        wallet_key_token = bcrypt.hashpw(
            wallet_key.encode("utf-8"),
            wallet_token_record.wallet_key_salt.encode("utf-8"),
        )
        # check the passed in value/hash against the calculated hash.
        check_input = bcrypt.checkpw(wallet_key.encode("utf-8"), wallet_key_token)
        self.logger.debug(
            f"bcrypt.checkpw(wallet_key.encode('utf-8'), wallet_key_token) = {check_input}"
        )

        # check the passed in value against the saved hash
        check_saved = bcrypt.checkpw(
            wallet_key.encode("utf-8"),
            wallet_token_record.wallet_key_hash.encode("utf-8"),
        )
        self.logger.debug(
            f"bcrypt.checkpw(wallet_key.encode('utf-8'), wallet_record.wallet_key_hash.encode('utf-8')) = {check_saved}"
        )

        return check_input and check_saved

    async def create_wallet(
        self,
        settings: dict,
        key_management_mode: str,
    ) -> WalletRecord:
        """Create new wallet and wallet record.

        Args:
            settings: The context settings for this wallet
            key_management_mode: The mode to use for key management. Either "unmanaged"
                to not store the wallet key, or "managed" to store the wallet key

        Raises:
            MultitenantManagerError: If the wallet name already exists

        Returns:
            WalletRecord: The newly created wallet record

        """
        self.logger.info("> create_wallet")
        wallet_key = settings.get("wallet.key")
        try:
            # do the default create wallet...
            wallet_record = await self.manager._super_create_wallet(
                settings, key_management_mode
            )
            # ok, wallet exists, set up the token record
            try:
                await self.find_or_create_wallet_token_record(
                    wallet_record.wallet_id, wallet_key
                )
            except Exception:
                async with self.get_profile().session() as session:
                    await wallet_record.delete_record(session)
                raise
        except Exception:
            raise
        self.logger.info("< create_wallet")
        return wallet_record

    async def create_auth_token(
        self, wallet_record: WalletRecord, wallet_key: str = None
    ) -> str:
        self.logger.info("> create_auth_token")
        config = self.get_profile().context.inject(MultitenantProviderConfig)
        async with self.get_profile().session() as session:
            wallet_token_record = await self.find_or_create_wallet_token_record(
                wallet_record.wallet_id, wallet_key
            )
            self.logger.debug(wallet_token_record)

        iat = datetime.now(tz=timezone.utc)
        exp = iat + config.token_expiry.get_token_expiry_delta()

        jwt_payload = {"wallet_id": wallet_record.wallet_id, "iat": iat, "exp": exp}
        jwt_secret = self.get_profile().settings.get("multitenant.jwt_secret")

        if wallet_record.requires_external_key:
            if not wallet_key:
                raise WalletKeyMissingError()
            # add wallet key to token if external key is required...
            jwt_payload["wallet_key"] = wallet_key

        if config.manager.always_check_provided_wallet_key:
            # if a wallet key was passed in, we need to check it
            if wallet_key and not self.check_wallet_key(
                wallet_token_record, wallet_key
            ):
                raise WalletKeyMismatchError()

        encoded = jwt.encode(jwt_payload, jwt_secret, algorithm="HS256")
        decoded = jwt.decode(encoded, jwt_secret, algorithms=["HS256"])
        # the token we return is the encoded string...
        token = encoded

        # save wallet record with the jwt_iat
        async with self.get_profile().session() as session:
            # Store this iat as the "valid" singular one in the old multitenant world
            wallet_record.jwt_iat = decoded.get("iat")
            await wallet_record.save(session)
            self.logger.debug(wallet_record)

            # save wallet token record with the updated issued claims list
            wallet_token_record.add_issued_at_claims(decoded.get("iat"))
            await wallet_token_record.save(session)
            self.logger.debug(wallet_token_record)

        # return this token...
        self.logger.info("< create_auth_token")
        return token

    async def get_profile_for_token(
        self, context: InjectionContext, token: str
    ) -> Profile:
        self.logger.info("> get_profile_for_token")

        jwt_secret = self.get_profile().context.settings.get("multitenant.jwt_secret")
        extra_settings = {}

        try:
            token_body = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            self.logger.debug(f"token_body = {token_body}")
        except jwt.exceptions.ExpiredSignatureError as err:
            # if exp has expired, we end up here.
            self.logger.error("Expired Signature... clean up claims")
            # ignore expiry so we can get the iat...
            token_body = jwt.decode(
                token, jwt_secret, algorithms=["HS256"], options={"verify_exp": False}
            )
            wallet_id = token_body.get("wallet_id")
            iat = token_body.get("iat")
            async with self.get_profile().session() as session:
                tokens_record = await WalletTokenRecord.query_by_wallet_id(
                    session, wallet_id
                )
                tokens_record.issued_at_claims.remove(iat)
                await tokens_record.save(session)

            raise err

        wallet_id = token_body.get("wallet_id")
        wallet_key = token_body.get("wallet_key")
        iat = token_body.get("iat")

        async with self.get_profile().session() as session:
            wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)
            wallet_token_record = await WalletTokenRecord.query_by_wallet_id(
                session, wallet_id
            )

        if wallet_record.requires_external_key:
            if not wallet_key:
                raise WalletKeyMissingError()

            extra_settings["wallet.key"] = wallet_key

        # if wallet key in token, check it
        if wallet_key and not self.check_wallet_key(wallet_token_record, wallet_key):
            raise WalletKeyMismatchError()

        # if we are here, then check issued at time.
        token_valid = False
        for claim in wallet_token_record.issued_at_claims:
            if claim == iat:
                token_valid = True

        # check the top level iat, this could be an old token from before this plugin
        # was loaded into this acapy instance
        if not token_valid:
            token_valid = wallet_record.jwt_iat and wallet_record.jwt_iat == iat

        if not token_valid:
            raise MultitenantManagerError("Token not valid")

        profile = await self.manager.get_wallet_profile(
            context, wallet_record, extra_settings
        )

        self.logger.info("< get_profile_for_token")
        return profile


class BasicMultitokenMultitenantManager(MultitenantManager):
    def __init__(self, profile: Profile):
        super().__init__(profile)
        self.logger = logging.getLogger(__class__.__name__)
        # we need to call the default implementation of create_wallet then add our token code afterward
        self._super_create_wallet = super().create_wallet

    async def create_auth_token(
        self, wallet_record: WalletRecord, wallet_key: str = None
    ) -> str:
        self.logger.info("> create_auth_token")
        handler = MulittokenHandler(self)
        token = await handler.create_auth_token(wallet_record, wallet_key)
        self.logger.info("< create_auth_token")
        return token

    async def get_profile_for_token(
        self, context: InjectionContext, token: str
    ) -> Profile:
        self.logger.info("> get_profile_for_token")
        handler = MulittokenHandler(self)
        profile = await handler.get_profile_for_token(context, token)
        self.logger.info("< get_profile_for_token")
        return profile

    async def create_wallet(
        self,
        settings: dict,
        key_management_mode: str,
    ) -> WalletRecord:
        self.logger.info("> create_wallet")
        handler = MulittokenHandler(self)
        wallet_record = await handler.create_wallet(settings, key_management_mode)
        self.logger.info("< create_wallet")
        return wallet_record


class AskarMultitokenMultitenantManager(AskarProfileMultitenantManager):
    def __init__(self, profile: Profile, multitenant_profile: AskarProfile = None):
        super().__init__(profile, multitenant_profile)
        self.logger = logging.getLogger(__class__.__name__)
        # we need to call the default implementation of create_wallet then add our token code afterward
        self._super_create_wallet = super().create_wallet

    async def create_auth_token(
        self, wallet_record: WalletRecord, wallet_key: str = None
    ) -> str:
        self.logger.info("> create_auth_token")
        handler = MulittokenHandler(self)
        token = await handler.create_auth_token(wallet_record, wallet_key)
        self.logger.info("< create_auth_token")
        return token

    async def get_profile_for_token(
        self, context: InjectionContext, token: str
    ) -> Profile:
        self.logger.info("> get_profile_for_token")
        handler = MulittokenHandler(self)
        profile = await handler.get_profile_for_token(context, token)
        self.logger.info("< get_profile_for_token")
        return profile

    async def create_wallet(
        self,
        settings: dict,
        key_management_mode: str,
    ) -> WalletRecord:
        self.logger.info("> create_wallet")
        handler = MulittokenHandler(self)
        wallet_record = await handler.create_wallet(settings, key_management_mode)
        self.logger.info("< create_wallet")
        return wallet_record
