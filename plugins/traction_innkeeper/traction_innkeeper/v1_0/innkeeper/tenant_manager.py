import bcrypt
from datetime import datetime, timedelta
import logging
from typing import List, Optional

from acapy_agent.core.error import BaseError
from acapy_agent.core.profile import Profile
from acapy_agent.messaging.models.base import BaseModelError
from acapy_agent.multitenant.base import BaseMultitenantManager

# from acapy_agent.ledger.multiple_ledger.base_manager import (
#     BaseMultipleLedgerManager,
# )
from acapy_agent.storage.error import StorageError, StorageNotFoundError
from acapy_agent.wallet.models.wallet_record import WalletRecord

from .config import TractionInnkeeperConfig, InnkeeperWalletConfig, ReservationConfig
from .models import TenantAuthenticationApiRecord, TenantRecord, ReservationRecord


class TenantManager:
    """Class for managing tenants."""

    def __init__(self, profile: Profile, config: TractionInnkeeperConfig):
        """
        Initialize a TenantManager.

        Args:
            profile: The profile for this tenant manager
        """
        self._profile = profile
        self._logger = logging.getLogger(__name__)
        self._config = config

    @property
    def profile(self) -> Profile:
        """
        Accessor for the current profile.

        Returns:
            The profile for this tenant manager

        """
        return self._profile

    async def create_wallet(
        self,
        wallet_name: str,
        wallet_key: str,
        tenant_email: Optional[str],
        extra_settings: dict = {},
        tenant_id: str = None,
    ):
        # this is from multitenant / admin / routes.py -> wallet_create
        # (mostly) duplicate code.

        try:
            if "tenant.endorser_config" in extra_settings:
                connect_to_endorsers = extra_settings.get("tenant.endorser_config")
                del extra_settings["tenant.endorser_config"]
            else:
                connect_to_endorsers = self._config.innkeeper_wallet.connect_to_endorser
            if "tenant.public_did_config" in extra_settings:
                created_public_did = extra_settings.get("tenant.public_did_config")
                del extra_settings["tenant.public_did_config"]
            else:
                created_public_did = self._config.innkeeper_wallet.create_public_did
            if "tenant.auto_issuer" in extra_settings:
                auto_issuer = extra_settings.get("tenant.auto_issuer")
                del extra_settings["tenant.auto_issuer"]
            else:
                auto_issuer = self._config.reservation.auto_issuer
            if "tenant.enable_ledger_switch" in extra_settings:
                enable_ledger_switch = extra_settings.get("tenant.enable_ledger_switch")
                del extra_settings["tenant.enable_ledger_switch"]
            else:
                enable_ledger_switch = (
                    self._config.innkeeper_wallet.enable_ledger_switch
                )
            # we must stick with managed until AcaPy has full support for unmanaged.
            # transport/inbound/session.py only deals with managed.
            key_management_mode = WalletRecord.MODE_MANAGED
            wallet_webhook_urls = []
            wallet_dispatch_type = "base"  # use base notification until they add urls

            label = wallet_name  # use the name they provided as the label

            unique_wallet_name = await self.get_unique_wallet_name(wallet_name)
            if unique_wallet_name != wallet_name:
                # but... we have to change the actual wallet name
                wallet_name = unique_wallet_name

            settings = {
                "wallet.type": self._profile.context.settings["wallet.type"],
                "wallet.name": wallet_name,
                "wallet.key": wallet_key,
                "wallet.webhook_urls": wallet_webhook_urls,
                "wallet.dispatch_type": wallet_dispatch_type,
            }
            settings.update(extra_settings)
            # set the default label (our provided wallet name)
            settings["default_label"] = label

            multitenant_mgr = self._profile.inject(BaseMultitenantManager)

            wallet_record = await multitenant_mgr.create_wallet(
                settings, key_management_mode
            )
            token = await self.get_token(wallet_record, wallet_key)
        except BaseError as err:
            self._logger.error(f"Error creating wallet ('{wallet_name}').", err)
            raise err
        # auto_issuer check
        innkeeper_tenant_id = self._config.innkeeper_wallet.tenant_id
        if not auto_issuer or tenant_id == innkeeper_tenant_id:
            connect_to_endorsers = []
            created_public_did = []
        # ok, all is good, then create a tenant record
        tenant = await self.create_tenant(
            wallet_id=wallet_record.wallet_id,
            email=tenant_email,
            tenant_id=tenant_id,
            connected_to_endorsers=connect_to_endorsers,
            created_public_did=created_public_did,
            auto_issuer=auto_issuer,
            enable_ledger_switch=enable_ledger_switch,
        )

        return tenant, wallet_record, token

    async def get_token(self, wallet_record: WalletRecord, wallet_key):
        try:
            multitenant_mgr = self._profile.inject(BaseMultitenantManager)
            token = await multitenant_mgr.create_auth_token(wallet_record, wallet_key)
        except BaseError as err:
            self._logger.error(
                f"Error getting token for wallet ('{wallet_record.wallet_name}').", err
            )
            raise err
        return token

    async def create_tenant(
        self,
        wallet_id: str,
        email: str,
        connected_to_endorsers: List = [],
        created_public_did: List = [],
        auto_issuer: bool = False,
        tenant_id: str = None,
        enable_ledger_switch: bool = False,
    ):
        try:
            async with self._profile.session() as session:
                wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)
                tenant_name = (
                    wallet_record.settings.get("default_label")
                    if wallet_record.settings.get("default_label")
                    else wallet_record.wallet_name
                )
                tenant: TenantRecord = TenantRecord(
                    tenant_id=tenant_id,
                    tenant_name=tenant_name,
                    contact_email=email,
                    wallet_id=wallet_record.wallet_id,
                    new_with_id=tenant_id is not None,
                    connected_to_endorsers=list(
                        endorser_config.serialize()
                        for endorser_config in connected_to_endorsers
                    ),
                    created_public_did=created_public_did,
                    enable_ledger_switch=enable_ledger_switch,
                    auto_issuer=auto_issuer,
                )
                await tenant.save(session, reason="New tenant")
                await tenant.query(session)
                self._logger.info(tenant)
        except Exception as err:
            self._logger.error(err)
            raise err

        return tenant

    async def create_innkeeper(self):
        config: InnkeeperWalletConfig = self._config.innkeeper_wallet
        reservation_config: ReservationConfig = self._config.reservation
        tenant_id = config.tenant_id
        wallet_name = config.wallet_name
        wallet_key = config.wallet_key
        # multi_ledger_manager = self._profile.inject(BaseMultipleLedgerManager)

        # does innkeeper already exist?
        tenant_record = None
        wallet_record = None
        try:
            async with self._profile.session() as session:
                tenant_record = await TenantRecord.retrieve_by_id(session, tenant_id)
                wallet_record = await WalletRecord.retrieve_by_id(
                    session, tenant_record.wallet_id
                )
        except (StorageError, BaseModelError):
            self._logger.info(f"Tenant not found with ID '{tenant_id}'")

        if tenant_record and wallet_record:
            self._logger.info(f"'{wallet_name}' wallet exists.")
            token = await self.get_token(wallet_record, wallet_key)
        else:
            tenant_record, wallet_record, token = await self.create_wallet(
                wallet_name,
                wallet_key,
                None,
                {
                    "wallet.innkeeper": True,
                    "tenant.endorser_config": config.connect_to_endorser,
                    "tenant.public_did_config": config.create_public_did,
                    "tenant.auto_issuer": reservation_config.auto_issuer,
                },
                tenant_id,
            )
            self._logger.info(f"...created '{wallet_name}' tenant and wallet.")

        print(f"\ntenant.tenant_name = {tenant_record.tenant_name}")
        print(f"tenant.tenant_id = {tenant_record.tenant_id}")
        print(f"tenant.wallet_id = {tenant_record.wallet_id}")
        print(f"wallet.wallet_name = {wallet_record.wallet_name}")
        print(f"wallet.wallet_id = {wallet_record.wallet_id}")
        print(f"tenant.endorser_config = {tenant_record.connected_to_endorsers}")
        print(f"tenant.public_did_config = {tenant_record.created_public_did}")
        print(f"tenant.auto_issuer = {str(tenant_record.auto_issuer)}")
        print(
            f"tenant.enable_ledger_switch = {str(tenant_record.enable_ledger_switch)}"
        )
        _key = wallet_record.wallet_key if config.print_key else "********"
        print(f"wallet.wallet_key = {_key}\n")
        if config.print_token:
            print(f"Bearer {token}\n")

    def check_reservation_password(
        self, reservation_pwd: str, reservation: ReservationRecord
    ):
        if reservation_pwd is None or reservation is None:
            return None

        # make a hash from passed in value with saved salt...
        reservation_token = bcrypt.hashpw(
            reservation_pwd.encode("utf-8"),
            reservation.reservation_token_salt.encode("utf-8"),
        )
        # check the passed in value/hash against the calculated hash.
        checkpw = bcrypt.checkpw(reservation_pwd.encode("utf-8"), reservation_token)
        self._logger.debug(
            f"bcrypt.checkpw(reservation_pwd.encode('utf-8'), reservation_token) = {checkpw}"
        )

        # check the passed in value against the saved hash
        checkpw2 = bcrypt.checkpw(
            reservation_pwd.encode("utf-8"),
            reservation.reservation_token_hash.encode("utf-8"),
        )
        self._logger.debug(
            f"bcrypt.checkpw(reservation_pwd.encode('utf-8'), reservation.reservation_token_hash.encode('utf-8')) = {checkpw2}"
        )

        if checkpw and checkpw2:
            # if password is correct, then return the string equivalent...
            return reservation_token.decode("utf-8")
        else:
            # else return None
            return None

    async def get_unique_wallet_name(self, wallet_name: str):
        self._logger.info(f"> get_unique_wallet_name('{wallet_name}')")
        unique_wallet_name = wallet_name
        async with self._profile.session() as session:
            w = await self.check_tables_for_wallet_name(session, unique_wallet_name)
            idx = 1
            while w:
                self._logger.info(f"'{unique_wallet_name}': wallet_exists = {w}")
                unique_wallet_name = f"{unique_wallet_name}-{idx}"
                w = await self.check_tables_for_wallet_name(session, unique_wallet_name)
                idx += 1
        # return a unique wallet/tenant name, either the input or calculated...
        self._logger.info(
            f"< get_unique_wallet_name('{wallet_name}') = '{unique_wallet_name}'"
        )
        return unique_wallet_name

    async def check_tables_for_wallet_name(self, session, wallet_name: str):
        # we can add more tables here if need (ie reservations, tenants...)
        wallet_records = await WalletRecord.query(session, {"wallet_name": wallet_name})
        wallet_exists = len(wallet_records) > 0

        return wallet_exists

    async def get_wallet_and_tenant(self, wallet_id: str):
        self._logger.info(f"> get_wallet_and_tenant('{wallet_id}')")
        tenant_record = None
        wallet_record = None
        try:
            async with self._profile.session() as session:
                wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)
                tenant_record = await TenantRecord.query_by_wallet_id(
                    session, wallet_id
                )
        except (StorageError, BaseModelError):
            self._logger.warning(f"Tenant not found with wallet_id '{wallet_id}'")

        self._logger.info(
            f"< get_wallet_and_tenant('{wallet_id}'): wallet_record = {wallet_record} & tenant_record = {tenant_record}"
        )
        if not wallet_record:
            raise StorageNotFoundError(f"Tenant not found with wallet_id '{wallet_id}'")
        return wallet_record, tenant_record

    def check_api_key(self, api_key: str, apiRecord: TenantAuthenticationApiRecord):
        if api_key is None or apiRecord is None:
            return None

        # make a hash from passed in value with saved salt...
        key_token = bcrypt.hashpw(
            api_key.encode("utf-8"),
            apiRecord.api_key_token_salt.encode("utf-8"),
        )
        # check the passed in value/hash against the calculated hash.
        checkpw = bcrypt.checkpw(api_key.encode("utf-8"), key_token)
        self._logger.debug(
            f"bcrypt.checkpw(api_key.encode('utf-8'), key_token) = {checkpw}"
        )

        # check the passed in value against the saved hash
        checkpw2 = bcrypt.checkpw(
            api_key.encode("utf-8"),
            apiRecord.api_key_token_hash.encode("utf-8"),
        )
        self._logger.debug(
            f"bcrypt.checkpw(api_key.encode('utf-8'), reservation.api_key_token_hash.encode('utf-8')) = {checkpw2}"
        )

        if checkpw and checkpw2:
            # if password is correct, then return...
            return key_token.decode("utf-8")
        else:
            # else return None
            return None
