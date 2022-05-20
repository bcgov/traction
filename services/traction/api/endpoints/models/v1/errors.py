from typing import List

from api.endpoints.models.v1.base import Link


class BaseError(Exception):
    def __init__(
        self,
        code: str | None = None,
        title: str | None = None,
        detail: str | None = None,
        links: List[Link] | None = [],
    ):
        self.code = code
        self.title = title
        self.detail = detail
        self.links = links
        super().__init__(self.detail)


class MethodNotImplementedError(BaseError):
    pass


class AlreadyExistsError(BaseError):
    pass


class NotFoundError(BaseError):
    pass


class IdNotMatchError(BaseError):
    pass


class NotAnIssuerError(BaseError):
    pass
