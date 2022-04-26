from typing import List
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from api.endpoints.models.v1.base import ListItemParameters, Link, Item


def build_list_links(
    total_record_count: int, parameters: ListItemParameters
) -> List[Link]:
    links = []

    start = (parameters.page_num - 1) * parameters.page_size
    end = start + parameters.page_size

    prev_page = build_paging_link(parameters, "prev", -1)
    next_page = build_paging_link(parameters, "next", 1)
    self_page = build_paging_link(parameters, "self", 0)

    if parameters.page_num > 1:
        links.append(prev_page)

    links.append(self_page)

    if total_record_count >= end:
        links.append(next_page)

    return links


def build_paging_link(parameters: ListItemParameters, rel: str, page_inc: int) -> Link:
    url = url_base(parameters.url)
    params = parameters.dict(
        exclude_none=True, exclude_unset=True, exclude_defaults=False
    )
    params["page_num"] = parameters.page_num + page_inc
    # do not include the url in the query string...
    del params["url"]
    query_string = urlencode(params)
    return Link(
        rel=rel,
        href=f"{url}?{query_string}",
    )


def url_base(url: str):
    parsed_url = urlparse(url)
    return urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            None,
            None,
            None,
        )
    )


def build_item_links(url: str, item: Item) -> List[Link]:
    links = []

    if not item.deleted:
        links.append(Link(rel="self", href=url))
        links.append(Link(rel="update", href=url))
        links.append(Link(rel="delete", href=url))
    else:
        parsed_url = urlparse(url)
        parsed_qs = parse_qs(parsed_url.query)
        parsed_qs["deleted"] = True
        new_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                urlencode(parsed_qs, doseq=True),
                parsed_url.fragment,
            )
        )
        links.append(Link(rel="self", href=str(new_url)))

    return links
