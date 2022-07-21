from pydantic import BaseModel


def underscore_field(string: str) -> str:
    if string == "_from":
        return "x_from"
    return string


class IndyNonRevokedBaseModel(BaseModel):
    class Config:
        check_fields = False
        alias_generator = underscore_field
