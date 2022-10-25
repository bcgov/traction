"""Profile manager for multitenancy."""

import logging

from aries_cloudagent.config.settings import BaseSettings
from aries_cloudagent.config.injector import BaseInjector

from aries_cloudagent.multitenant.manager_provider import MultitenantManagerProvider

LOGGER = logging.getLogger(__name__)

from .manager import TractionMultitenantManager

class TractionMultitenantManagerProvider(MultitenantManagerProvider):

    def provide(self, settings: BaseSettings, injector: BaseInjector):
        """Create the multitenant manager instance."""
        manager_class = "multitenant_tokens"

        if manager_class not in self._inst:
            LOGGER.info("Create multitenant_tokens manager")
            self._inst[manager_class] = TractionMultitenantManager(self.root_profile)

        return self._inst[manager_class]
