"""Profile manager for multitenancy."""
import inspect
import os
import logging

from aries_cloudagent.config.settings import BaseSettings
from aries_cloudagent.config.injector import BaseInjector
from aries_cloudagent.config.base import InjectionError
from aries_cloudagent.utils.classloader import ClassLoader, ClassNotFoundError

from aries_cloudagent.multitenant.manager_provider import MultitenantManagerProvider

LOGGER = logging.getLogger(__name__)


class CustomMultitenantManagerProvider(MultitenantManagerProvider):
    """
    Multitenant manager provider.

    Decides which manager to use based on the settings.
    """
    config_key = "multitenant_provider"

    def __init__(self, root_profile):
         super().__init__(root_profile)


    def get_config(self, settings: BaseSettings):
        try:
            plugin_config = settings["plugin_config"] or {}
            config = plugin_config[self.config_key]
            return config
        except KeyError as error:
            # will just proceed with defaults
            LOGGER.warning(f"No configuration found for plugin '{self.config_key}', proceeding with defaults.")
            return {}    

    def get_manager_type(self, config: dict):
        try:
            return config["manager_type"]
        except KeyError as error:
            return "custom"     

    def get_manager_class(self, config: dict):
        try:
            return config["manager_class"]
        except KeyError as error:
            return "multitenant_provider.manager.BasicMultitokenMultitenantManager"     
        

    def provide(self, settings: BaseSettings, injector: BaseInjector):
        """Create the multitenant manager instance."""

        config = self.get_config(settings)
        manager_type = self.get_manager_type(config)
        if manager_type == "custom":
            manager_class = self.get_manager_class(config)
            if manager_class not in self._inst:
                LOGGER.info(f"Create multitenant manager (type={manager_type}, class={manager_class})")
                try:
                    self._inst[manager_class] = ClassLoader.load_class(manager_class)(
                        self.root_profile
                    )
                except ClassNotFoundError as err:
                    raise InjectionError(
                        f"Error loading multitenant manager, class '{manager_class}' not found."
                    ) from err

            return self._inst[manager_class]
        else:
            # do the default provider behaviour
            return super().provide(settings=settings, injector=injector)
