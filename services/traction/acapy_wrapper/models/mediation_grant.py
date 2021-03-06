# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401


class MediationGrant(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    MediationGrant - a model defined in OpenAPI

        id: The id of this MediationGrant [Optional].
        type: The type of this MediationGrant [Optional].
        endpoint: The endpoint of this MediationGrant [Optional].
        routing_keys: The routing_keys of this MediationGrant [Optional].
    """

    id: Optional[str] = None
    type: Optional[str] = None
    endpoint: Optional[str] = None
    routing_keys: Optional[List[str]] = None


MediationGrant.update_forward_refs()
