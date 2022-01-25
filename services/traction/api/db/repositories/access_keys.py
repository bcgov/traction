from typing import Type

from api.db.repositories.base import BaseRepository
from api.db.tables.access_keys import AccessKey
from api.models.schema.access_keys import InAccessKeySchema, AccessKeySchema


class AccessKeysRepository(
    BaseRepository[InAccessKeySchema, AccessKeySchema, AccessKey]
):
    @property
    def _in_schema(self) -> Type[InAccessKeySchema]:
        return InAccessKeySchema

    @property
    def _schema(self) -> Type[AccessKeySchema]:
        return AccessKeySchema

    @property
    def _table(self) -> Type[AccessKey]:
        return AccessKey
