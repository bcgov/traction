from datetime import datetime
from typing import List, Generic, TypeVar, Optional

from pydantic import BaseModel, AnyUrl
from pydantic.generics import GenericModel

from api.core.config import settings

"""
Models v1 - Base

These are base classes (interfaces) for the API resources.
It is expected that we create concrete classes
 that will specify specific implementations for any of the Generic *Types.

Conceptually, there are several base classes:
- *Item: an individual resource, like a record in a database
- *Response: this would be the outgoing (response) object of an API call
- *Payload: this would be the incoming (request) body of an API call.
- *Parameters: class that encapsulates various search and filter parameters
- List*Parameters: class that encapsulates search/filter parameters for an *Item type

"""
ItemType = TypeVar("ItemType")
StatusType = TypeVar("StatusType")
StateType = TypeVar("StateType")
TimelineType = TypeVar("TimelineType")
AcapyType = TypeVar("AcapyType")


class Link(BaseModel):
    """
    Link class that provides some navigational context to a Resource.
    Point the caller to other related functions or for navigation of paged lists.

    This is a concrete class
    """

    href: AnyUrl
    rel: str


class Item(GenericModel, Generic[StatusType, StateType]):
    """
    Basic building block for all our resource classes.

    Concrete classes will specify the exact classes to use for Status and State

    status: Represents a business level status for the object
    state: Represents a low-level state of the underlying AcaPy object
    deleted: true if object is deleted. Traction uses soft deletes
    created_at: timestamp when created
    updated_at: timestamp when object last modified
    """

    status: StatusType
    state: StateType
    deleted: bool = False
    created_at: datetime
    updated_at: datetime


class TimelineItem(GenericModel, Generic[StatusType, StateType]):
    """
    Basic building block for items in a Timeline list.

    Concrete classes will specify the exact classes to use for Status and State

    status: Represents a business level status for the object
    state: Represents a low-level state of the underlying AcaPy object
    created_at: timestamp when timeline item was created
    """

    status: StatusType
    state: StateType
    created_at: datetime


class TagsItem(Item[StatusType, StateType], Generic[StatusType, StateType]):
    """
    Inherits from Item.
    Adds a tags attribute, a list of strings used for categorization.

    tags: List[str]
    """

    tags: List[str] | None = []


class AcapyItem(
    TagsItem[StatusType, StateType], Generic[StatusType, StateType, AcapyType]
):
    """
    Inherits from TagsItem

    Adds a field: acapy, which itself will contain any AcaPy data.

    In general, AcaPy data must be specifically request via query parameters.
    The content of AcaPy will be determined by the AcapyType class

    acapy: dict
    """

    acapy: Optional[AcapyType] = None


class ListResponse(GenericModel, Generic[ItemType]):
    """
    Basic building block for collection APIs (list, search).
    This is the structure of the Response

    Concrete classes will specify the exact classes to use for Item

    items: list of items, items are paged and filtered by parameters
    links: list of related links
    count: the number of items in this page/list
    total: total number of items that match provided parameters
    """

    items: List[ItemType] = []
    links: List[Link] = []
    count: int
    total: int


class ListItemParameters(GenericModel, Generic[StatusType, StateType]):
    """
    Basic building block for collection APIs (list, search).
    This is the structure of the parameters used to populate the response.

    Concrete classes will specify the exact classes to use for Status and Type

    url: str, the url of the collection, used to build out links
    page_num: int, which page to return (1 based)
    page_size: int, maximum number of items to return (0 based)
    status: filter on status (exact match)
    state: filter on state (exact match)
    deleted: bool, when true return only deleted items
    """

    url: str | None = None
    page_num: int | None = 1
    page_size: int | None = settings.DEFAULT_PAGE_SIZE
    status: Optional[StatusType] = None
    state: Optional[StateType] = None
    deleted: bool | None = False


class ListTagsItemParameters(
    ListItemParameters[StatusType, StateType], Generic[StatusType, StateType]
):
    """
    Inherits from ListItemParameters

    tags: List[str], used to filter results based on their tags
    """

    tags: Optional[List[str]] | None = []


class ListAcapyItemParameters(
    ListItemParameters[StatusType, StateType], Generic[StatusType, StateType]
):
    """
    Inherits from ListTagsItemParameters

    acapy: bool, when true, return AcaPy data for each item
    """

    acapy: bool | None = False


class GetResponse(GenericModel, Generic[ItemType]):
    """
    Basic building block for single resource API
    This is the structure of the Response

    Concrete classes will specify the exact classes to use for Item

    item: the data object
    links: list of related links
    """

    item: ItemType
    links: List[Link] = []


class GetTimelineResponse(GetResponse[ItemType], Generic[ItemType, TimelineType]):
    """
    Builds on GetResponse
    This is the structure of the Response

    Concrete classes will specify the exact classes to use for Timeline Item

    timeline: list of timeline items for item
    """

    timeline: Optional[List[TimelineType]] | None = []
