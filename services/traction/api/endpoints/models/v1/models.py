from pydantic import BaseModel


class Contact(BaseModel):
    pass


class CreateInvitationPayload(BaseModel):
    pass


class CreateInvitationResponse(BaseModel):
    pass


class ReceiveInvitationPayload(BaseModel):
    pass


class ReceiveInvitationResponse(BaseModel):
    pass


class CreateContactPayload(BaseModel):
    pass


class UpdateContactPayload(BaseModel):
    pass


class ProposeCredentialPayload(BaseModel):
    pass


class ProposeCredentialResponse(BaseModel):
    pass


class RequestCredentialPayload(BaseModel):
    pass


class RequestCredentialResponse(BaseModel):
    pass


class OfferCredentialPayload(BaseModel):
    pass


class OfferCredentialResponse(BaseModel):
    pass


class IssueCredentialPayload(BaseModel):
    pass


class IssueCredentialResponse(BaseModel):
    pass


class AbandonCredentialPayload(BaseModel):
    pass


class AbandonCredentialResponse(BaseModel):
    pass


class RevokeCredentialResponse(BaseModel):
    pass


class Credential(BaseModel):
    pass


class AcceptCredentialResponse(BaseModel):
    pass


class RejectCredentialResponse(BaseModel):
    pass


class Presentation(BaseModel):
    pass


class PresentationCredential(BaseModel):
    pass


class SendPresentationPayload(BaseModel):
    pass


class SendPresentationResponse(BaseModel):
    pass


class SendPresentationProposalPayload(BaseModel):
    pass


class SendPresentationProposalResponse(BaseModel):
    pass


class AbandonPresentationPayload(BaseModel):
    pass


class AbandonPresentationResponse(BaseModel):
    pass


class PresentationRequest(BaseModel):
    pass


class SendPresentationRequestPayload(BaseModel):
    pass


class SendPresentationRequestResponse(BaseModel):
    pass


class AcceptPresentationResponse(BaseModel):
    pass


class RejectPresentationResponse(BaseModel):
    pass


class AcceptProposalResponse(BaseModel):
    pass


class RejectProposalResponse(BaseModel):
    pass


class PresentationRequestTemplate(BaseModel):
    pass


class CreatePresentationRequestTemplatePayload(BaseModel):
    pass


class UpdatePresentationRequestTemplatePayload(BaseModel):
    pass


class TractionEvent(BaseModel):
    pass


class UpdateTractionEventPayload(BaseModel):
    pass


class TractionEventConfig(BaseModel):
    pass


class UpdateTractionEventConfigPayload(BaseModel):
    pass


class ProfileConfig(BaseModel):
    pass


class UpdateProfileConfigPayload(BaseModel):
    pass


class Profile(BaseModel):
    pass


class UpdateProfilePayload(BaseModel):
    pass


class IssuerConfig(BaseModel):
    pass


class TractionMessage(BaseModel):
    pass


class SendTractionMessageResponse(BaseModel):
    pass


class SendTractionMessagePayload(BaseModel):
    pass


class UpdateTractionMessagePayload(BaseModel):
    pass
