from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config(BaseModel.Config):
        orm_mode = True
