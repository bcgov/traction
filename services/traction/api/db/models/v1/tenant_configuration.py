"""Tenant Configuration Tables/Models.

Models of the Traction tables for tenant configuration. This is configuration at the
Tenant level - the tenant sets the data in this table.

"""
import uuid

from sqlmodel import Field
from sqlalchemy import (
    select,
)

from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import TimestampModel


class TenantConfiguration(TimestampModel, table=True):
    """TenantConfiguration.

    This is the model for the Tenant Configuration table. This is configuration for how
    the tenant will/can interact with Traction.

    Each tenant is responsible for setting their own configuration. However, some values
    will only apply if the Innkeeper has given them permission (ex. store message data).


    Attributes:
      tenant_id: Traction Tenant ID
      webhook_url: a url that will receive webhook data pushed from Traction.
      webhook_key: this will be sent as the X-API-Key header to the webhook_url. This
       allows the tenant to secure their webhook_url.
      auto_respond_messages: This allows each tenant to effectively set their own value
       for the AcaPy `auto-respond-messages` flag. Default is True
      auto_response_message: when auto_respond_messages is True, this is the message
       that is delivered. If auto_respond_messages is True and no value set, a default
       message will be returned.
      store_messages: when True, the messages will be stored. Requires Innkeeper
        permission.
      store_issuer_credentials: when True, the data used to create a credential offer
       will be stored. Requires Innkeeper permission.
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "tenant_configuration"

    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True, primary_key=True)
    webhook_url: str = Field(nullable=True, default=None)
    webhook_key: str = Field(nullable=True, default=None)
    auto_respond_messages: bool = Field(nullable=False, default=True)
    auto_response_message: str = Field(nullable=True, default=None)
    store_messages: bool = Field(nullable=False, default=False)
    store_issuer_credentials: bool = Field(nullable=False, default=False)

    @classmethod
    async def get_by_id(
        cls: "TenantConfiguration",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> "TenantConfiguration":
        """Get TenantConfiguration by tenant id.

        Find and return the database record.
        If one does not exist, insert a default and return it.

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call

        Returns: The Traction TenantConfiguration (db) record

        Raises:

        """

        q = select(cls).where(cls.tenant_id == tenant_id)
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            # perhaps this is an old tenant, just create a default record
            db_rec = cls(tenant_id=tenant_id)
            db.add(db_rec)
            await db.commit()

        return db_rec


class TenantAutoResponseLog(TimestampModel, table=True):
    """TenantAutoResponseLog.

    This is the model for the Tenant Auto-response table. We need to track which
    connections we've auto responded to so we don't flood them. Once they've received an
    auto-response they should not get another one (or we can set some elapsed time?).


    Attributes:
      tenant_id: Traction Tenant ID
      contact_id: Traction Contact ID - who this tenant has sent an auto response
      message: store the message we sent as a response
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "tenant_auto_response_log"

    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True, primary_key=True)
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id")
    message: str = Field(nullable=False)

    @classmethod
    async def get_from_tenant_to_contact(
        cls: "TenantAutoResponseLog",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> "TenantAutoResponseLog":
        """Get TenantAutoResponseLog by tenant id and contact id.

        Return true if the tenant has sent an auto response to the connection.

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          contact_id: AcaPy connection id of other agent.
        Returns: The record if record exists, None otherwise.

        Raises:

        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.contact_id == contact_id)
        )
        q_result = await db.execute(q)
        return q_result.scalar_one_or_none()
