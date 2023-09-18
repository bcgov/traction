from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.valid import (
    INDY_ISO8601_DATETIME_EXAMPLE,
    INDY_ISO8601_DATETIME_VALIDATE,
)
from marshmallow import fields


class BasicMessageRecord(BaseRecord):
    """BasicMessage Record."""

    # pylint: disable=too-few-public-methods

    RECORD_ID_NAME = "record_id"
    RECORD_TYPE = "basicmessage"

    STATE_SENT = "sent"
    STATE_RECV = "received"

    class Meta:
        """BasicMessage metadata."""

        schema_class = "BasicMessageRecordSchema"

    def __init__(
        self,
        *,
        record_id: str = None,
        connection_id: str = None,
        message_id: str = None,
        locale: str = None,
        content: str = None,
        sent_time: str = None,
        state: str = None,
        **kwargs,
    ):
        """Initialize a new SchemaRecord."""
        super().__init__(record_id, state or self.STATE_SENT, **kwargs)
        self.connection_id = connection_id
        self.message_id = message_id
        self.locale = locale
        self.content = content
        self.sent_time = sent_time

    @property
    def record_id(self) -> str:
        """Accessor for this schema's id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Get record value."""
        return {
            prop: getattr(self, prop)
            for prop in ("content", "locale", "sent_time", "state")
        }

    @property
    def record_tags(self) -> dict:
        """Get tags for record."""
        return {"connection_id": self.connection_id, "message_id": self.message_id}

    @classmethod
    async def retrieve_by_message_id(
        cls, session: ProfileSession, message_id: str
    ) -> "BasicMessageRecord":
        """Retrieve a basic message record by message id."""
        return await cls.retrieve_by_tag_filter(session, {"message_id": message_id})


class BasicMessageRecordSchema(BaseRecordSchema):
    """Schema to allow serialization/deserialization of BasicMessage
    records.
    """

    # pylint: disable=too-few-public-methods

    class Meta:
        """BasicMessageRecordSchema metadata."""

        model_class = BasicMessageRecord

    connection_id = fields.Str(required=False)
    message_id = fields.Str(required=False)
    sent_time = fields.Str(
        required=False,
        validate=INDY_ISO8601_DATETIME_VALIDATE,
        example=INDY_ISO8601_DATETIME_EXAMPLE,
    )
    locale = fields.Str(required=False)
    content = fields.Str(required=False)
