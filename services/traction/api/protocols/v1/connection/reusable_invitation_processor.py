from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.db.models.v1.connection_invitation import ConnectionInvitation
from api.endpoints.models.connections import ConnectionRoleType, ConnectionStateType
from api.endpoints.models.v1.contacts import ContactStatusType
from api.protocols.v1.connection.connection_protocol import DefaultConnectionProtocol


class ReusableInvitationProcessor(DefaultConnectionProtocol):
    def __init__(self):
        super().__init__(role=ConnectionRoleType.inviter)

    async def on_request(self, profile: Profile, payload: dict):
        self.logger.debug(f"on_request({profile.wallet_id} {payload})")
        # see if we have an invitation

        if "invitation_key" in payload.keys():
            invitation = await ConnectionInvitation.get_by_invitation_key(
                profile.db, profile.tenant_id, payload["invitation_key"]
            )
            if invitation:

                # create a contact, we will update the alias when we reach active
                label = payload["invitation_key"]
                db_contact = Contact(
                    alias=label,
                    tenant_id=profile.tenant_id,
                    status=ContactStatusType.pending,
                    state=ConnectionStateType.request,
                    role=ConnectionRoleType.inviter,
                    connection_id=payload["connection_id"],
                    connection_alias=label,
                    invitation=invitation.invitation,
                    connection=payload,
                    tags=invitation.tags,
                )
                profile.db.add(db_contact)
                await profile.db.commit()

    async def on_response(self, profile: Profile, payload: dict):
        self.logger.debug(f"on_response({profile.wallet_id} {payload})")

        # now that the connection is far enough along
        # update the alias, connection alias...
        label = payload["their_label"]
        values = {"alias": label, "connection_alias": label}
        stmt = (
            update(Contact)
            .where(Contact.connection_id == payload["connection_id"])
            .values(values)
        )
        await profile.db.execute(stmt)
        await profile.db.commit()
