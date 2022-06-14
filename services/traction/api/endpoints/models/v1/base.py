"""Traction v1 API Base Models.


These are base classes (interfaces) for the API resources.
It is expected that we create concrete classes that will specify specific
implementations for any of the Generic xTypes.

  Conceptually, there are several base classes/interfaces:
    *Type: indicates that the implementing class will specify a concrete class for this
      field.

    *Item: an individual resource, like a record in a database.

    *Response: this would be the outgoing (response) object of an API call.

    *Payload: this would be the incoming (request) body of an API call.

    *Parameters: class that encapsulates various search and filter parameters.

    List*Parameters: class that encapsulates search/filter parameters for an *Item type.

  For example:
    ContactItem is a concrete implementation of AcapyItem that is our API
    representation of the database Contact record. It specifies ContactStatusType,
    ConnectionStateType, and ContactAcapy for its StatusType, StateType and AcapyType
    implementations.

"""
from datetime import datetime
from typing import List, Generic, TypeVar, Optional

from pydantic import BaseModel, AnyUrl
from pydantic.generics import GenericModel

from api.core.config import settings

ItemType = TypeVar("ItemType")
StatusType = TypeVar("StatusType")
StateType = TypeVar("StateType")
TimelineType = TypeVar("TimelineType")
AcapyType = TypeVar("AcapyType")


class Link(BaseModel):
    """Link.

    Link class that provides some navigational context to a Resource.
    Point the caller to other related functions or for navigation of paged lists.

    Attributes:
      href: URL to call
      rel: relation to this object; what purpose does this link serve?
    """

    href: AnyUrl
    rel: str


class Item(GenericModel, Generic[StatusType, StateType]):
    """Item.

    Base class for any individual object/resource with status/state.
    Concrete classes will specify the exact classes to use for Status and State.

    Attributes:
      status: Represents a business level status for the object
      state: Represents a low-level state of the underlying AcaPy object
      deleted: true if object is deleted. Traction uses soft deletes
      created_at: timestamp when created
      updated_at: timestamp when object last modified
    """

    status: StatusType | None = None
    state: StateType | None = None
    error_status_detail: str | None = None
    deleted: bool = False
    created_at: datetime
    updated_at: datetime


class TimelineItem(GenericModel, Generic[StatusType, StateType]):
    """TimelineItem.

    Base class for items in a Timeline list.
    Concrete classes will specify the exact classes to use for Status and State.

    A collection of TimelineItems will represent the history of changes to Status and
    state.

    Attributes:
      status: Represents a business level status for the object
      state: Represents a low-level state of the underlying AcaPy object
      created_at: timestamp when created
    """

    status: StatusType
    state: StateType
    error_status_detail: str | None = None
    created_at: datetime


class TagsItem(Item[StatusType, StateType], Generic[StatusType, StateType]):
    """TagsItem.

    Inherits from Item.
    Adds a tags attribute, a list of strings used for categorization.

    Attributes:
      tags: list of strings used to categorize an Item
    """

    tags: List[str] | None = []


class AcapyItem(
    TagsItem[StatusType, StateType], Generic[StatusType, StateType, AcapyType]
):
    """AcapyItem.

    Inherits from TagsItem.
    Adds a acapy attribute (dict).

    Attributes:
      acapy: a dict of AcaPy data objects related to the Item
    """

    acapy: Optional[AcapyType] = None


class ListResponse(GenericModel, Generic[ItemType]):
    """ListResponse.

    Base class for collection APIs (list, search).
    In general, these will have a matching ListItemParameters class that will specify
    filters to use when fetching lists.

    Attributes:
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
    """ListItemParameters.

    Base class for parameters to collection APIs (list, search).
    In general, these will be for a specific implementation of a ListItemResponse.

    Attributes:
      url: the url of the collection, used to build out links
      page_num: which page to return (1 based)
      page_size: maximum number of items to return (0 based)
      status: filter on status (exact match)
      state: filter on state (exact match)
      deleted: when true return only deleted items
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
    """ListTagsItemParameters.

    Inherits from ListItemParameters.
    Should be used when fetching lists of TagsItem

    Attributes:
      tags: comma separated string, used to match tags array
    """

    tags: str | None = None


class ListAcapyItemParameters(
    ListTagsItemParameters[StatusType, StateType], Generic[StatusType, StateType]
):
    """ListAcapyItemParameters.

    Inherits from ListTagsItemParameters.
    Should be used when fetching lists of AcapyItem

    Attributes:
      acapy: when True, populate the item's acapy field
    """

    acapy: bool | None = False


class GetResponse(GenericModel, Generic[ItemType]):
    """GetResponse.

    Base class for single resource APIs (Get, Update, Delete).
    This is the structure of the Response, the type of the item is specified by the
    implementation.

    Attributes:
      item: the data object
      links: list of related links
    """

    item: ItemType
    links: List[Link] = []


class GetTimelineResponse(GetResponse[ItemType], Generic[ItemType, TimelineType]):
    """GetTimelineResponse.

    Inherits from GetResponse.
    Implementing class will specify the Item's type and the Timeline Item's type.

    Attributes:
      timeline: list of timeline items for item
    """

    timeline: Optional[List[TimelineType]] | None = []
