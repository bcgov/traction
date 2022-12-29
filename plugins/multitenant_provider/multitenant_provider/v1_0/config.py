import logging
from datetime import timedelta
from typing import Any, Mapping, Optional

from mergedeep import merge
from pydantic import BaseModel


LOGGER = logging.getLogger(__name__)


def _alias_generator(key: str) -> str:
    return key.replace("_", "-")


class ManagerConfig(BaseModel):
    class_name: Optional[str]  # real world, this is a UUID
    always_check_provided_wallet_key: bool = False

    class Config:
        alias_generator = _alias_generator
        allow_population_by_field_name = True

    @classmethod
    def default(cls):
        # consider this for local development only...
        return cls(
            class_name="multitenant_provider.v1_0.manager.BasicMultitokenMultitenantManager",
            always_check_provided_wallet_key=True,
        )


class ErrorsConfig(BaseModel):
    on_unneeded_wallet_key: bool = True

    class Config:
        alias_generator = _alias_generator
        allow_population_by_field_name = True

    @classmethod
    def default(cls):
        return cls(on_unneeded_wallet_key=True)


class TokenExpiryConfig(BaseModel):
    units: Optional[str] = "weeks"  # weeks, days, hours, minutes
    amount: int = 52

    class Config:
        alias_generator = _alias_generator
        allow_population_by_field_name = True

    @classmethod
    def default(cls):
        return cls(units="weeks", quantity=52)

    def get_token_expiry_delta(self) -> timedelta:
        result = timedelta(weeks=52)
        if "weeks" == self.units:
            result = timedelta(weeks=self.amount)
        elif "days" == self.units:
            result = timedelta(days=self.amount)
        elif "hours" == self.units:
            result = timedelta(hours=self.amount)
        elif "minutes" == self.units:
            result = timedelta(minutes=self.amount)
        return result


class MultitenantProviderConfig(BaseModel):
    manager: Optional[ManagerConfig]
    errors: Optional[ErrorsConfig]
    token_expiry: Optional[TokenExpiryConfig]

    @classmethod
    def default(cls):
        return cls(
            manager=ManagerConfig.default(),
            errors=ErrorsConfig.default(),
            token_expiry=TokenExpiryConfig.default(),
        )


def process_config_dict(config_dict: dict) -> dict:
    _filter = ["manager", "errors", "token_expiry"]
    for key, value in config_dict.items():
        if key in _filter:
            config_dict[key] = value
    return config_dict


def get_config(settings: Mapping[str, Any]) -> MultitenantProviderConfig:
    """Retrieve configuration from settings."""
    try:
        LOGGER.debug("Constructing config from: %s", settings.get("plugin_config"))
        plugin_config_dict = settings["plugin_config"].get("multitenant_provider", {})
        LOGGER.debug("Retrieved: %s", plugin_config_dict)
        plugin_config_dict = process_config_dict(plugin_config_dict)
        LOGGER.debug("Parsed: %s", plugin_config_dict)
        default_config = MultitenantProviderConfig.default().dict()
        LOGGER.debug("Default Config: %s", default_config)
        config_dict = merge({}, default_config, plugin_config_dict)
        LOGGER.debug("Merged: %s", config_dict)
        config = MultitenantProviderConfig(**config_dict)
    except KeyError:
        LOGGER.warning("Using default configuration")
        config = MultitenantProviderConfig.default()

    LOGGER.debug("Returning config: %s", config.json(indent=2))
    LOGGER.debug("Returning config(aliases): %s", config.json(by_alias=True, indent=2))
    return config
