from enum import Enum


class PublicDIDStateType(str, Enum):
    private = "private"
    requested = "requested"
    endorsed = "endorsed"
    published = "published"
    public = "public"
