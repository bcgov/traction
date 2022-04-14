from typing import List, Generic, TypeVar, Optional

from pydantic import BaseModel, AnyUrl
from pydantic.generics import GenericModel

ItemType = TypeVar("ItemType")
StatusType = TypeVar("StatusType")
StateType = TypeVar("StateType")
AcapyType = TypeVar("AcapyType")


class Link(BaseModel):
    href: AnyUrl
    rel: str


class Item(GenericModel, Generic[StatusType, StateType]):
    status: StatusType
    state: StateType
    deleted: bool = False


class TagsItem(Item[StatusType, StateType], Generic[StatusType, StateType]):
    tags: List[str] | None = []


class AcapyItem(
    TagsItem[StatusType, StateType], Generic[StatusType, StateType, AcapyType]
):
    acapy: Optional[AcapyType] = None


class ListResponse(GenericModel, Generic[ItemType]):
    items: List[ItemType] = []
    links: List[Link] = []


class ListItemParameters(GenericModel, Generic[StatusType, StateType]):
    skip: int = (0,)
    limit: int | None = (20,)
    status: Optional[StatusType] = None
    state: Optional[StateType] = None
    deleted: bool | None = False


class ListTagsItemParameters(
    ListItemParameters[StatusType, StateType], Generic[StatusType, StateType]
):
    tags: Optional[List[str]] | None = []


class ListAcapyItemParameters(
    ListItemParameters[StatusType, StateType], Generic[StatusType, StateType]
):
    acapy: bool | None = False


class GetResponse(GenericModel, Generic[ItemType]):
    item: ItemType
    links: List[Link] = []
