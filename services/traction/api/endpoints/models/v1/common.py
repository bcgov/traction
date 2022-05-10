from pydantic import BaseModel


class CommentPayload(BaseModel):
    comment: str
