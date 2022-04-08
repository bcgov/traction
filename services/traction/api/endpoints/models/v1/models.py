from datetime import datetime
from enum import Enum
from typing import List, Generic, TypeVar, Union, Optional
from uuid import UUID

from pydantic import BaseModel, AnyUrl, Field
from pydantic.generics import GenericModel

from acapy_wrapper.models.conn_record import ConnRecord
from acapy_wrapper.models.credential import Credential
from acapy_wrapper.models.credential_preview import CredentialPreview
from acapy_wrapper.models.indy_proof import IndyProof
from acapy_wrapper.models.indy_proof_request import IndyProofRequest
from acapy_wrapper.models.invitation_message import InvitationMessage
from acapy_wrapper.models.invitation_record import InvitationRecord
from acapy_wrapper.models.presentation_proposal import PresentationProposal
from acapy_wrapper.models.receive_invitation_request import ReceiveInvitationRequest
from acapy_wrapper.models.send_message import SendMessage
from acapy_wrapper.models.v10_credential_exchange import V10CredentialExchange
from acapy_wrapper.models.v10_credential_free_offer_request import (
    V10CredentialFreeOfferRequest,
)
from acapy_wrapper.models.v10_credential_proposal_request_opt import (
    V10CredentialProposalRequestOpt,
)
from acapy_wrapper.models.v10_presentation_exchange import V10PresentationExchange
from acapy_wrapper.models.v20_cred_ex_free import V20CredExFree
from acapy_wrapper.models.v20_cred_ex_record import V20CredExRecord
from acapy_wrapper.models.v20_cred_offer_request import V20CredOfferRequest
from acapy_wrapper.models.v20_cred_request_free import V20CredRequestFree
from acapy_wrapper.models.v20_pres import V20Pres
from acapy_wrapper.models.v20_pres_ex_record import V20PresExRecord
from acapy_wrapper.models.v20_pres_proposal import V20PresProposal
from acapy_wrapper.models.v20_pres_request import V20PresRequest
from api.endpoints.models.connections import ConnectionProtocolType

ItemType = TypeVar("ItemType")
StatusType = TypeVar("StatusType")
StateType = TypeVar("StateType")
AcapyType = TypeVar("AcapyType")
ProtocolType = TypeVar("ProtocolType")

class ContactStatusType(str, Enum):
    active = "Active"
    inactive = "Inactive"
    deleted = "Deleted"


class ContactStateType(str, Enum):
    start = "start"
    init = "init"
    invitation = "invitation"
    request = "request"
    response = "response"
    active = "active"
    completed = "completed"
    abandoned = "abandoned"
    error = "error"


class CredentialStatusType(str, Enum):
    pending = "Pending"
    completed = "Completed"
    revoked = "Revoked"
    deleted = "Deleted"


class CredentialStateType(str, Enum):
    # issuer states
    pending = "pending"
    proposal_received = "proposal_received"
    offer_sent = "offer_sent"
    request_received = "request_received"
    credential_issued = "credential_issued"
    # holder states
    proposal_sent = "proposal_sent"
    offer_received = "offer_received"
    request_sent = "request_sent"
    credential_received = "credential_received"
    # common states
    credential_acked = "credential_acked"
    done = "done"
    abandoned = "abandoned"
    error = "error"
    credential_revoked = "credential_revoked"


class PresentationStatusType(str, Enum):
    pass


class PresentationStateType(str, Enum):
    pass


class PresentationRequestStatusType(str, Enum):
    pass


class PresentationRequestStateType(str, Enum):
    pass



class MessageStatusType(str, Enum):
    new = "New"
    read = "Read"
    deleted = "Deleted"


class EventType(str, Enum):
    contacts = "Contacts"
    issuer = "Issuer"
    holder = "Holder"
    verifier = "Verifier"


class EventStatusType(str, Enum):
    new = "New"
    processed = "Processed"


class IssuerStatusType(str, Enum):
    enabled = "Enabled"
    active = "Active"


class EventCategory(BaseModel):
    type: EventType
    subtype: str


class ContactAcapy(BaseModel):
    invitation: InvitationRecord
    connection: ConnRecord


class CredentialAcapy(BaseModel):
    credential: Credential
    credential_exchange: Union[V10CredentialExchange, V20CredExRecord]


class PresentationAcapy(BaseModel):
    presentation_exchange: Union[V10PresentationExchange, V20PresExRecord]


class PresentationRequestAcapy(BaseModel):
    presentation_exchange: Union[V10PresentationExchange, V20PresExRecord]



class EventAcapy(BaseModel):
    pass


class MessageAcapy(BaseModel):
    message: SendMessage


class Link(BaseModel):
    href: AnyUrl
    rel: str



class History(GenericModel, Generic[StatusType, AcapyType]):
    created_at: datetime
    status: StatusType
    protocol: str
    acapy: AcapyType


class Item(GenericModel, Generic[StatusType, StateType]):
    status: ContactStatusType
    state: ContactStateType


class TagsItem(Item[StatusType, StateType], Generic[StatusType, StateType]):
    tags: List[str] = []


class AcapyItem(
    TagsItem[StatusType, StateType], Generic[StatusType, StateType, AcapyType]
):
    tags: List[str] = []
    history: List[History[StatusType, AcapyType]] = []
    acapy: AcapyType


class ListBase(GenericModel, Generic[ItemType]):
    items: List[ItemType] = []
    links: List[Link] = []


class Contact(AcapyItem[ContactStatusType, ContactStateType, ContactAcapy]):
    contact_id: UUID = Field(...)
    alias: str = Field(...)
    public_did: Optional[str]
    ping_enabled: bool = Field(default=False)
    last_connected_ts: datetime
    external_reference_id: str
    links: List[Link] = []


class ContactList(ListBase[Contact]):
    pass


class CreateInvitationPayload(BaseModel):
    alias: str
    invitation_type: ConnectionProtocolType = (ConnectionProtocolType.DIDExchange,)


class CreateInvitationResponse(BaseModel):
    contact: Contact


class ReceiveInvitationPayload(BaseModel):
    alias: str = Field(...)
    invitation: Union[InvitationMessage, ReceiveInvitationRequest]
    public_did: Optional[str]


class ReceiveInvitationResponse(BaseModel):
    contact: Contact


class UpdateContactPayload(BaseModel):
    contact_id: UUID = Field(...)
    alias: str = Field(...)
    public_did: Optional[str]
    ping_enabled: bool
    external_reference_id: str
    status: ContactStatusType
    tags: List[str]


class TractionEvent(BaseModel):
    event_id: UUID
    category: EventCategory
    status: EventStatusType
    timestamp: datetime = Field(...)
    link: Link
    acapy: EventAcapy


class TractionEventList(ListBase[TractionEvent]):
    pass


class UpdateTractionEventPayload(BaseModel):
    event_id: UUID
    status: EventStatusType


class DeleteTractionEventPayload(BaseModel):
    event_id: UUID


class BulkUpdateTractionEventPayload(BaseModel):
    events: List[UpdateTractionEventPayload]


class BulkDeleteTractionEventPayload(BaseModel):
    events: List[DeleteTractionEventPayload]


class PushNotificationUrl(BaseModel):
    url: AnyUrl
    key: Optional[str]
    filter: dict = []


class TractionEventConfig(BaseModel):
    push_notifications_urls: List[PushNotificationUrl]


class UpdateTractionEventConfigPayload(BaseModel):
    push_notifications_urls: List[PushNotificationUrl]


class Credential(AcapyItem[CredentialStatusType, CredentialStateType, CredentialAcapy]):
    credential_id: UUID
    preview: CredentialPreview
    contact: Contact = Field(...)
    external_reference_id: str
    links: List[Link] = []


class UpdateCredentialPayload(BaseModel):
    credential_id: UUID
    external_reference_id: str
    status: CredentialStatusType
    tags: List[str] = []


class CredentialList(ListBase[Credential]):
    pass


class ProposeCredentialPayload(BaseModel):
    contact_id: UUID
    proposal: Union[V10CredentialProposalRequestOpt, V20CredExFree]


class ProposeCredentialResponse(BaseModel):
    credential: Credential


class RequestCredentialPayload(BaseModel):
    contact_id: UUID
    request: V20CredRequestFree


class RequestCredentialResponse(BaseModel):
    credential: Credential


class OfferCredentialPayload(BaseModel):
    contact_id: UUID
    offer: Union[V10CredentialFreeOfferRequest, V20CredOfferRequest]


class OfferCredentialResponse(BaseModel):
    credential: Credential


class IssueCredentialPayload(BaseModel):
    credential_id: UUID


class IssueCredentialResponse(BaseModel):
    credential: Credential


class AbandonCredentialPayload(BaseModel):
    credential_id: UUID


class AbandonCredentialResponse(BaseModel):
    credential: Credential


class RevokeCredentialResponse(BaseModel):
    credential: Credential


class AcceptCredentialResponse(BaseModel):
    credential: Credential


class RejectCredentialResponse(BaseModel):
    credential: Credential


class Presentation(
    AcapyItem[PresentationStatusType, PresentationStateType, PresentationAcapy]
):
    presentation_id: UUID
    presentation: Union[IndyProof, V20Pres]
    contact: Contact = Field(...)
    external_reference_id: str
    links: List[Link] = []


class PresentationList(ListBase[Presentation]):
    pass


class PresentationCredential(BaseModel):
    credential: Credential
    cred_info: dict
    interval: dict | None = None
    presentation_referents: list


class PresentationCredentialList(ListBase[PresentationCredential]):
    pass


class SendPresentationPayload(BaseModel):
    presentation_id: UUID
    credentials: PresentationCredentialList


class SendPresentationResponse(BaseModel):
    presentation: Presentation


class SendPresentationProposalPayload(BaseModel):
    presentation_id: UUID
    credentials: PresentationCredentialList


class SendPresentationProposalResponse(BaseModel):
    presentation: Presentation


class AbandonPresentationPayload(BaseModel):
    presentation_id: UUID


class AbandonPresentationResponse(BaseModel):
    presentation: Presentation


class PresentationRequest(
    AcapyItem[PresentationRequestStatusType, PresentationRequestStateType, PresentationRequestAcapy]
):
    presentation_request_id: UUID
    presentation_request: Union[IndyProofRequest, V20PresRequest]
    presentation_proposal: Union[PresentationProposal, V20PresProposal]
    contact: Contact = Field(...)
    external_reference_id: str
    links: List[Link] = []



class PresentationRequestList(ListBase[PresentationRequest]):
    pass


class SendPresentationRequestPayload(BaseModel):
    contact_id: UUID
    presentation_request: Union[IndyProofRequest, V20PresRequest]


class SendPresentationRequestResponse(BaseModel):
    presentation_request: PresentationRequest


class AcceptPresentationResponse(BaseModel):
    presentation_request: PresentationRequest



class RejectPresentationResponse(BaseModel):
    presentation_request: PresentationRequest



class AcceptProposalResponse(BaseModel):
    presentation_request: PresentationRequest


class RejectProposalResponse(BaseModel):
    presentation_request: PresentationRequest


class PresentationRequestTemplate(BaseModel):
    presentation_request_template_id: UUID = Field(...)
    name: str = Field(...)
    presentation_request: Union[IndyProofRequest, V20PresRequest]
    tags: List[str] = []

class PresentationRequestTemplateList(ListBase[PresentationRequestTemplate]):
    pass


class CreatePresentationRequestTemplatePayload(BaseModel):
    name: str = Field(...)
    presentation_request: Union[IndyProofRequest, V20PresRequest]
    tags: List[str] = []


class UpdatePresentationRequestTemplatePayload(BaseModel):
    name: str = Field(...)
    presentation_request: Union[IndyProofRequest, V20PresRequest]
    tags: List[str] = []



class IssuerConfig(BaseModel):
    status: IssuerStatusType


class TractionMessage(BaseModel):
    message_id: UUID
    status: MessageStatusType
    message: str = Field(...)
    contact: Contact
    acapy: MessageAcapy


class TractionMessageList(ListBase[TractionMessage]):
    pass


class UpdateTractionMessagePayload(BaseModel):
    message_id: UUID
    status: MessageStatusType


class DeleteTractionMessagePayload(BaseModel):
    message_id: UUID


class BulkUpdateTractionMessagePayload(BaseModel):
    events: List[UpdateTractionMessagePayload]


class BulkDeleteTractionMessagePayload(BaseModel):
    events: List[DeleteTractionMessagePayload]


class SendTractionMessageResponse(BaseModel):
    message: TractionMessage


class SendTractionMessagePayload(BaseModel):
    contact_id: UUID = Field(...)
    message: str = Field(...)


class TractionSchema(BaseModel):
    schema_id: str
    name: str
    version: str
    description: str
    attributes: List[str]


class TractionSchemaList(ListBase[TractionSchema]):
    pass


class CreateTractionSchemaPayload(BaseModel):
    name: str
    version: str
    attributes: List[str]
    tags: List[str]


class ImportTractionSchemaPayload(BaseModel):
    schema_id: str
    name: str


class CredentialDefinition(BaseModel):
    cred_def_id: str
    revocation_enabled: bool
    revocation_registry_size: int
    schema_id: str
    tags: List[str]


class CredentialDefinitionList(ListBase[CredentialDefinition]):
    pass


class CreateCredentialDefinitionPayload(BaseModel):
    cred_def_id: str
    revocation_enabled: bool
    revocation_registry_size: int
    schema_id: str
    tags: List[str]


class CreateCredentialDefinitionResponse(BaseModel):
    credential_definition: CredentialDefinition
