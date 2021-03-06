# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401
from acapy_wrapper.models.indy_attr_value import IndyAttrValue


class IndyCredential(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    IndyCredential - a model defined in OpenAPI

        cred_def_id: The cred_def_id of this IndyCredential.
        rev_reg: The rev_reg of this IndyCredential [Optional].
        rev_reg_id: The rev_reg_id of this IndyCredential [Optional].
        schema_id: The schema_id of this IndyCredential.
        signature: The signature of this IndyCredential.
        signature_correctness_proof: The signature_correctness_proof of this IndyCredential.
        values: The values of this IndyCredential.
        witness: The witness of this IndyCredential [Optional].
    """

    cred_def_id: str
    rev_reg: Optional[Dict[str, Any]] = None
    rev_reg_id: Optional[str] = None
    schema_id: str
    signature: Dict[str, Any]
    signature_correctness_proof: Dict[str, Any]
    values: Dict[str, IndyAttrValue]
    witness: Optional[Dict[str, Any]] = None

    @validator("cred_def_id")
    def cred_def_id_pattern(cls, value):
        assert value is not None and re.match(
            r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
            value,
        )
        return value

    @validator("rev_reg_id")
    def rev_reg_id_pattern(cls, value):
        assert value is not None and re.match(
            r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
            value,
        )
        return value

    @validator("schema_id")
    def schema_id_pattern(cls, value):
        assert value is not None and re.match(
            r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$",
            value,
        )
        return value


IndyCredential.update_forward_refs()
