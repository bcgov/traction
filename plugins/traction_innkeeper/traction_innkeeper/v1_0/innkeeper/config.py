import logging
from typing import Any, Mapping, Optional, List

from mergedeep import merge
from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)


def _alias_generator(key: str) -> str:
    return key.replace("_", "-")


class EndorserLedgerConfig(BaseModel):
    endorser_alias: str
    ledger_id: str

    class Config:
        alias_generator = _alias_generator
        populate_by_name = True

    def serialize(self) -> dict:
        """Serialize the EndorserLedgerConfig to a mapping."""
        ret = {}
        if self.endorser_alias:
            ret["endorser_alias"] = self.endorser_alias
        if self.ledger_id:
            ret["ledger_id"] = self.ledger_id
        return ret


class InnkeeperWalletConfig(BaseModel):
    tenant_id: Optional[str]  # real world, this is a UUID
    wallet_name: Optional[str]
    wallet_key: Optional[str]
    print_key: bool = False
    print_token: bool = False
    connect_to_endorser: List[EndorserLedgerConfig] = []
    create_public_did: List[str] = []
    enable_ledger_switch: bool = False

    class Config:
        alias_generator = _alias_generator
        populate_by_name = True

    @classmethod
    def default(cls):
        # consider this for local development only...
        return cls(
            tenant_id="innkeeper",
            wallet_key="MySecretKey123",
            wallet_name="traction_innkeeper_v1_0",
            print_key=False,
            print_token=False,
            enable_ledger_switch=False,
            connect_to_endorser=[],
            create_public_did=[],
        )


class ReservationConfig(BaseModel):
    expiry_minutes: int
    auto_approve: bool
    auto_issuer: bool = False

    class Config:
        alias_generator = _alias_generator
        populate_by_name = True

    @classmethod
    def default(cls):
        return cls(expiry_minutes=60, auto_approve=False, auto_issuer=False)


class TractionInnkeeperConfig(BaseModel):
    innkeeper_wallet: Optional[InnkeeperWalletConfig]
    reservation: Optional[ReservationConfig]

    @classmethod
    def default(cls):
        return cls(
            innkeeper_wallet=InnkeeperWalletConfig.default(),
            reservation=ReservationConfig.default(),
        )


def process_config_dict(config_dict: dict) -> dict:
    _filter = ["innkeeper_wallet", "reservation"]
    for key, value in config_dict.items():
        if key in _filter:
            config_dict[key] = value
    return config_dict


def get_config(settings: Mapping[str, Any]) -> TractionInnkeeperConfig:
    """Retrieve configuration from settings."""
    try:
        LOGGER.debug("Constructing config from: %s", settings.get("plugin_config"))
        plugin_config_dict = settings["plugin_config"].get("traction_innkeeper", {})
        LOGGER.debug("Retrieved: %s", plugin_config_dict)
        plugin_config_dict = process_config_dict(plugin_config_dict)
        LOGGER.debug("Parsed: %s", plugin_config_dict)
        default_config = TractionInnkeeperConfig.default().model_dump()
        LOGGER.debug("Default Config: %s", default_config)
        config_dict = merge({}, default_config, plugin_config_dict)
        LOGGER.debug("Merged: %s", config_dict)
        config = TractionInnkeeperConfig(**config_dict)
    except KeyError:
        LOGGER.warning("Using default configuration")
        config = TractionInnkeeperConfig.default()

    LOGGER.debug("Returning config: %s", config.model_dump_json(indent=2))
    LOGGER.debug("Returning config(aliases): %s", config.model_dump_json(by_alias=True, indent=2))
    return config
