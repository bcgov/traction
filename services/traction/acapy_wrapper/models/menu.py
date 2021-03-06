# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401
from acapy_wrapper.models.menu_option import MenuOption


class Menu(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    Menu - a model defined in OpenAPI

        id: The id of this Menu [Optional].
        type: The type of this Menu [Optional].
        description: The description of this Menu [Optional].
        errormsg: The errormsg of this Menu [Optional].
        options: The options of this Menu.
        title: The title of this Menu [Optional].
    """

    id: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    errormsg: Optional[str] = None
    options: List[MenuOption]
    title: Optional[str] = None


Menu.update_forward_refs()
