from typing import List, Generic, TypeVar


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
    deleted: bool


class TagsItem(Item[StatusType, StateType], Generic[StatusType, StateType]):
    tags: List[str] = []


class AcapyItem(
    TagsItem[StatusType, StateType], Generic[StatusType, StateType, AcapyType]
):
    tags: List[str] = []
    acapy: AcapyType


class ListResponse(GenericModel, Generic[ItemType]):
    items: List[ItemType] = []
    links: List[Link] = []


class GetResponse(GenericModel, Generic[ItemType]):
    item: ItemType
    links: List[Link] = []
