# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401
from acapy_wrapper.models.v20_pres import V20Pres
from acapy_wrapper.models.v20_pres_ex_record_by_format import V20PresExRecordByFormat
from acapy_wrapper.models.v20_pres_proposal import V20PresProposal
from acapy_wrapper.models.v20_pres_request import V20PresRequest


class V20PresExRecord(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    V20PresExRecord - a model defined in OpenAPI

        auto_present: The auto_present of this V20PresExRecord [Optional].
        by_format: The by_format of this V20PresExRecord [Optional].
        connection_id: The connection_id of this V20PresExRecord [Optional].
        created_at: The created_at of this V20PresExRecord [Optional].
        error_msg: The error_msg of this V20PresExRecord [Optional].
        initiator: The initiator of this V20PresExRecord [Optional].
        pres: The pres of this V20PresExRecord [Optional].
        pres_ex_id: The pres_ex_id of this V20PresExRecord [Optional].
        pres_proposal: The pres_proposal of this V20PresExRecord [Optional].
        pres_request: The pres_request of this V20PresExRecord [Optional].
        role: The role of this V20PresExRecord [Optional].
        state: The state of this V20PresExRecord [Optional].
        thread_id: The thread_id of this V20PresExRecord [Optional].
        trace: The trace of this V20PresExRecord [Optional].
        updated_at: The updated_at of this V20PresExRecord [Optional].
        verified: The verified of this V20PresExRecord [Optional].
    """

    auto_present: Optional[bool] = None
    by_format: Optional[V20PresExRecordByFormat] = None
    connection_id: Optional[str] = None
    created_at: Optional[str] = None
    error_msg: Optional[str] = None
    initiator: Optional[str] = None
    pres: Optional[V20Pres] = None
    pres_ex_id: Optional[str] = None
    pres_proposal: Optional[V20PresProposal] = None
    pres_request: Optional[V20PresRequest] = None
    role: Optional[str] = None
    state: Optional[str] = None
    thread_id: Optional[str] = None
    trace: Optional[bool] = None
    updated_at: Optional[str] = None
    verified: Optional[str] = None

    @validator("created_at")
    def created_at_pattern(cls, value):
        assert value is not None and re.match(
            r"^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$",
            value,
        )
        return value

    @validator("updated_at")
    def updated_at_pattern(cls, value):
        assert value is not None and re.match(
            r"^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$",
            value,
        )
        return value


V20PresExRecord.update_forward_refs()
