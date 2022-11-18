import logging
import uuid

from aries_cloudagent.core.error import BaseError
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.storage.error import StorageError
from aries_cloudagent.wallet.models.wallet_record import WalletRecord

from .models import TenantRecord


class TenantManager:
    """Class for managing tenants."""

    def __init__(self, profile: Profile):
        """
        Initialize a TenantManager.

        Args:
            profile: The profile for this tenant manager
        """
        self._profile = profile
        self._logger = logging.getLogger(__name__)

    @property
    def profile(self) -> Profile:
        """
        Accessor for the current profile.

        Returns:
            The profile for this tenant manager

        """
        return self._profile

    async def create_wallet(
        self, wallet_name: str = None, wallet_key: str = None, extra_settings: dict = {}
    ):
        if not wallet_name:
            wallet_name = str(uuid.uuid4())  # can we generate random words?

        if not wallet_key:
            wallet_key = str(uuid.uuid4())

        try:
            key_management_mode = WalletRecord.MODE_MANAGED
            wallet_webhook_urls = []
            wallet_dispatch_type = "base"

            settings = {
                "wallet.type": self._profile.context.settings["wallet.type"],
                "wallet.name": wallet_name,
                "wallet.key": wallet_key,
                "wallet.webhook_urls": wallet_webhook_urls,
                "wallet.dispatch_type": wallet_dispatch_type,
            }
            settings.update(extra_settings)

            label = wallet_name
            settings["default_label"] = label

            multitenant_mgr = self._profile.inject(BaseMultitenantManager)

            wallet_record = await multitenant_mgr.create_wallet(
                settings, key_management_mode
            )
            token = await multitenant_mgr.create_auth_token(wallet_record, wallet_key)
        except BaseError as err:
            self._logger.error(f"Error creating wallet ('{wallet_name}').", err)
            raise err

        # ok, all is good, then create a tenant record
        tenant: TenantRecord = TenantRecord(
            tenant_name=wallet_name, wallet_id=wallet_record.wallet_id
        )
        try:
            async with self._profile.session() as session:
                await tenant.save(session, reason="New tenant")
                self._logger.info(tenant)
        except Exception as err:
            self._logger.error(err)
            raise err

        return tenant, wallet_record, token

    async def create_innkeeper(self):
        # does innkeeper already exist?
        query = {}
        wallet_name = "traction_innkeeper"  # TODO: get from config
        if wallet_name:
            query["wallet_name"] = wallet_name

        wallet_key = "change-me"  # TODO: get from config

        try:
            async with self._profile.session() as session:
                records = await WalletRecord.query(session, tag_filter=query)
                has_traction_innkeeper = len(records)
        except (StorageError, BaseModelError) as err:
            raise err

        if has_traction_innkeeper:
            self._logger.info(f"'{wallet_name}' wallet exists.")
        else:
            self._logger.info(f"creating '{wallet_name}' wallet...")
            tenant, wallet_record, token = await self.create_wallet(
                wallet_name, wallet_key, {"wallet.innkeeper": True}
            )
            self._logger.info(f"...created '{wallet_name}' tenant and wallet.")
            # do some configuration or something to print this out...
            print(f"tenant.tenant_name = '{tenant.tenant_name}'")
            print(f"tenant.tenant_id = '{tenant.tenant_id}'")
            print(f"tenant.wallet_id = '{tenant.wallet_id}'")
            print(f"wallet.wallet_name = '{wallet_record.wallet_name}'")
            print(f"wallet.wallet_id = '{wallet_record.wallet_id}'")
            print(f"wallet.wallet_key = {wallet_record.wallet_key}\n")
            print(f"Bearer {token}\n")
