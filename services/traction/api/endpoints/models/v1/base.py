from typing import List, Generic, TypeVar, Optional
from urllib.parse import urlencode

from pydantic import BaseModel, AnyUrl
from pydantic.generics import GenericModel

from api.core.config import settings

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
    count: int
    total: int


class ListItemParameters(GenericModel, Generic[StatusType, StateType]):
    page_num: int | None = 1
    page_size: int | None = settings.DEFAULT_PAGE_SIZE
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


def build_list_links(
    total_record_count: int, parameters: ListItemParameters, list_api_path: str
) -> List[Link]:
    links = []

    start = (parameters.page_num - 1) * parameters.page_size
    end = start + parameters.page_size

    prev_page = build_paging_link(parameters, list_api_path, "prev", -1)
    next_page = build_paging_link(parameters, list_api_path, "next", 1)
    self_page = build_paging_link(parameters, list_api_path, "self", 0)

    if parameters.page_num > 1:
        links.append(prev_page)

    links.append(self_page)

    if total_record_count >= end:
        links.append(next_page)

    return links


def build_paging_link(
    parameters: ListItemParameters, list_api_path: str, rel: str, page_inc: int
) -> Link:
    full_api_path = f"{settings.TRACTION_HOST_URL}/{list_api_path}"
    params = parameters.dict(exclude_none=True, exclude_unset=True)
    params["page_num"] = parameters.page_num + page_inc
    query_string = urlencode(params)
    return Link(
        rel=rel,
        href=f"{full_api_path}?{query_string}",
    )
