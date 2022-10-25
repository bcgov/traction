import logging
import jwt

from datetime import datetime, timedelta, timezone

from aries_cloudagent.config.wallet import wallet_config
from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.wallet.models.wallet_record import WalletRecord
from aries_cloudagent.multitenant.base import BaseMultitenantManager, MultitenantManagerError
from aries_cloudagent.multitenant.manager import MultitenantManager

from .models import TokensWalletRecord, TokensWalletRecordSchema

LOGGER = logging.getLogger(__name__)

class TractionMultitenantManager(MultitenantManager):

    def __init__(self, profile: Profile):
        super().__init__(profile)

    async def create_auth_token(
        self, wallet_record: WalletRecord, wallet_key: str = None) -> str:
        LOGGER.info('> create_auth_token')
        async with self._profile.session() as session:
            tokens_wallet_record = await TokensWalletRecord.retrieve_by_id(session, wallet_record.wallet_id)
            LOGGER.info(tokens_wallet_record)

        iat = datetime.now(tz=timezone.utc)
        # TODO: configuration for how long token is valid.
        exp = iat + timedelta(days=1)

        jwt_payload = {"wallet_id": wallet_record.wallet_id, "iat": iat, "exp": exp}
        jwt_secret = self._profile.settings.get("multitenant.jwt_secret")

        if tokens_wallet_record.requires_external_key:
            if not wallet_key:
                raise WalletKeyMissingError()

            jwt_payload["wallet_key"] = wallet_key

        encoded = jwt.encode(jwt_payload, jwt_secret, algorithm="HS256")
        decoded = jwt.decode(encoded, jwt_secret, algorithms=["HS256"])
        # the token we return is the encoded string...
        token = encoded

        # Store this iat as the "valid" singular one in the old multitenant world
        tokens_wallet_record.jwt_iat = decoded.get("iat")
        # add this to the list of issued claims in the multi-token data
        tokens_wallet_record.add_issued_at_claims(decoded.get("iat"))

        # save it...
        async with self._profile.session() as session:
            await tokens_wallet_record.save(session)

        # return this token...    
        LOGGER.info('< create_auth_token')
        return token

    async def get_profile_for_token(
            self, context: InjectionContext, token: str) -> Profile:
        LOGGER.info('> get_profile_for_token')

        jwt_secret = self._profile.context.settings.get("multitenant.jwt_secret")
        extra_settings = {}

        try:
            token_body = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        except jwt.exceptions.ExpiredSignatureError as err:
        	# if exp has expired, we end up here.
            LOGGER.error("Expired Signature... clean up claims")
            # ignore expiry so we can get the iat...
            token_body = jwt.decode(token, jwt_secret, algorithms=["HS256"], options={"verify_exp": False})
            wallet_id = token_body.get("wallet_id")
            iat = token_body.get("iat")
            async with self._profile.session() as session:
                wallet = await TokensWalletRecord.retrieve_by_id(session, wallet_id)
                wallet.issued_at_claims.remove(iat)
                await wallet.save(session)
            
            async with self._profile.session() as session:
                wallet = await TokensWalletRecord.retrieve_by_id(session, wallet_id)

            raise err

        wallet_id = token_body.get("wallet_id")
        wallet_key = token_body.get("wallet_key")
        iat = token_body.get("iat")

        async with self._profile.session() as session:
            wallet = await TokensWalletRecord.retrieve_by_id(session, wallet_id)

        if wallet.requires_external_key:
            if not wallet_key:
                raise WalletKeyMissingError()

            extra_settings["wallet.key"] = wallet_key

        # if we are here,      
        token_valid = False    
        for claim in wallet.issued_at_claims:
            if claim == iat:
                token_valid = True

        if not token_valid:
            raise MultitenantManagerError("Token not valid")

        profile = await self.get_wallet_profile(context, wallet, extra_settings)

        LOGGER.info('< get_profile_for_token')
        return profile