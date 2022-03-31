import json
import logging
from typing import Optional, List
from uuid import UUID
from enum import Enum

from aiohttp import ClientSession, ContentTypeError
from pydantic import parse_obj_as
from starlette import status
from starlette.exceptions import HTTPException

from api.core.config import settings
from api.core.utils import hash_password
from api.db.models import Lob
from api.db.models.base import BaseSchema
from api.services import traction_urls as t_urls

logger = logging.getLogger(__name__)


class ARIES_PROTOCOL_ROLES(str, Enum):
    HOLDER = "holder"
    VERIFIER = "verifier"
    ISSUER = "issuer"


class CredPrecisForProof(BaseSchema):
    cred_info: dict
    interval: dict | None = None
    presentation_referents: list


# TODO JS: I think this function should be a feature in Traction
# (we can make a response for you if you don't care)
def build_proof_presentation(
    present_request: dict,
    cred_results: List[CredPrecisForProof],
) -> dict:
    proof_presentation = {
        "requested_attributes": {},
        "requested_predicates": {},
        "self_attested_attributes": {},
    }

    for attr_name in present_request["requested_attributes"]:
        for cred in cred_results:
            if attr_name in cred.presentation_referents:
                proof_presentation["requested_attributes"][attr_name] = {
                    "cred_id": cred.cred_info["referent"],
                    "revealed": True,
                }
                break
        if attr_name not in proof_presentation["requested_attributes"]:
            proof_presentation["self_attested_attributes"][
                attr_name
            ] = "TBD Self-attested"
    for pred_name in present_request["requested_predicates"]:
        for cred in cred_results:
            if pred_name in cred.presentation_referents:
                proof_presentation["requested_predicates"][pred_name] = {
                    "cred_id": cred.cred_info["referent"],
                }
                break

    return proof_presentation


async def get_auth_headers(
    wallet_id: Optional[UUID] = None, wallet_key: Optional[UUID] = None
):
    username = str(wallet_id) if wallet_id else settings.TRACTION_API_ADMIN_USER
    password = str(wallet_key) if wallet_key else settings.TRACTION_API_ADMIN_KEY
    token_url = t_urls.TENANT_TOKEN if wallet_id else t_urls.INNKEEPER_TOKEN

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": username,
        "password": password,
        "grant_type": "",
        "scope": "",
    }

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=token_url,
            data=data,
            headers=headers,
        ) as response:
            try:
                resp = await response.json()
                token = resp["access_token"]
                return {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
            except ContentTypeError:
                logger.exception("Error getting token", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_tenant(name: str):
    auth_headers = await get_auth_headers()
    # name, we will set the webhook url with security afterward.
    data = {"name": name}
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.INNKEEPER_CHECKIN,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error creating tenant", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_tenant_webhook(tenant: Lob):
    # here we connect as the tenant, passing in their traction credentials.
    auth_headers = await get_auth_headers(tenant.wallet_id, tenant.wallet_key)
    # set the webhook up with security
    # in a real LOB, do not use your wallet_key, configure it in a vault or env secret.
    # must simpler in the showcase to do this...
    hashed_wallet_key = hash_password(str(tenant.wallet_key))
    data = {
        "webhook_url": f"{settings.SHOWCASE_ENDPOINT}/api/v1/webhook/{tenant.id}",
        "webhook_key": hashed_wallet_key,
        "config": {"acapy": True},
    }
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_ADMIN_WEBHOOK,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error creating tenant webhook", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_get_credential_offers(
    wallet_id: UUID,
    wallet_key: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = {}

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_GET_CRED_OFFERS,
            params=query_params,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error getting credential offers list",
                    exc_info=True,
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_accept_credential_offer(
    wallet_id: UUID,
    wallet_key: UUID,
    cred_issue_id: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = {"cred_issue_id": str(cred_issue_id)}

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_ACCEPT_CRED_OFFER,
            params=query_params,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error accepting credential offer",
                    exc_info=True,
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_reject_credential_offer(
    wallet_id: UUID,
    wallet_key: UUID,
    cred_issue_id: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = {"cred_issue_id": str(cred_issue_id)}

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_REJECT_CRED_OFFER,
            params=query_params,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error rejecting credential offer",
                    exc_info=True,
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_get_credentials(
    wallet_id: UUID,
    wallet_key: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = {}

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_GET_CREDENTIALS,
            params=query_params,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error getting credentials list",
                    exc_info=True,
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def get_connections(
    wallet_id: UUID,
    wallet_key: UUID,
    alias: Optional[str] = None,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    # no body...
    data = {}
    query_params = {}
    if alias:
        query_params = {"alias": alias}

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_GET_CONNECTIONS,
            params=query_params,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error getting connections list",
                    exc_info=True,
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_invitation(
    wallet_id: UUID,
    wallet_key: UUID,
    alias: str,
):
    # call Traction to create an invitation...
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    # no body...
    data = {}
    query_params = {"alias": alias, "invitation_type": "didexchange/1.0"}
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREATE_INVITATION,
            params=query_params,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                connection = resp["connection"]
                return connection
            except ContentTypeError:
                logger.exception("Error creating invitation", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def accept_invitation(
    wallet_id: UUID, wallet_key: UUID, alias: str, invitation: dict
):
    # call Traction to accept an invitation...
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = {"alias": alias}
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_RECEIVE_INVITATION,
            params=query_params,
            json=invitation,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                connection = resp["connection"]
                return connection
            except ContentTypeError:
                logger.exception("Error accepting invitation", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def innkeeper_make_issuer(tenant_id: UUID):
    # call Traction to accept an invitation...
    innkeeper_auth_headers = await get_auth_headers()
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.INNKEEPER_MAKE_ISSUER + f"/{tenant_id}",
            headers=innkeeper_auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error registering tenant as issuer", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_admin_issuer(wallet_id: UUID, wallet_key: UUID, tenant_id: UUID):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_MAKE_ISSUER,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error registering self as issuer", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_create_schema(
    wallet_id: UUID,
    wallet_key: UUID,
    schema: dict = None,
    schema_id: str = None,
    cred_def_tag: str = None,
    revocable: bool = True,
    revoc_reg_size: int = 10,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = schema
    params = {}
    if schema_id is not None:
        params["schema_id"] = schema_id
    if cred_def_tag is not None:
        params["cred_def_tag"] = cred_def_tag
    if revocable:
        params["revocable"] = str(revocable)
        params["revoc_reg_size"] = revoc_reg_size

    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREATE_SCHEMA,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error creating schema/credential definition", exc_info=True
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_issue_credential(
    wallet_id: UUID,
    wallet_key: UUID,
    connection_id: str,
    alias: str,
    cred_def_id: str,
    attributes: list = [],
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {"attributes": attributes}
    params = {
        "cred_protocol": "v1.0",
        "cred_def_id": cred_def_id,
        "connection_id": connection_id,
        "alias": alias,
    }
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREDENTIAL_ISSUE,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error issuing credential", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_revoke_credential(
    wallet_id: UUID,
    wallet_key: UUID,
    rev_reg_id: str,
    cred_rev_id: str,
    comment: str,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {}
    params = {
        "rev_reg_id": rev_reg_id,
        "cred_rev_id": cred_rev_id,
        "comment": comment,
    }
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREDENTIAL_REVOKE,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error revoking credential", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_get_issued_credentials(
    wallet_id: UUID,
    wallet_key: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {}
    params = {}
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_CREDENTIAL_ISSUE,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                # we are going to transform this to something usable
                # {
                #   "credential": {
                #     "tenant_id": "8448fefa-e7a3-443c-8e12-da254e390fde",
                #     "wallet_id": "7284c309-0dcf-440e-9ae9-61439d47ae2a",
                #     "connection_id": "61afc10d-3710-4997-bb6a-d778884aba87",
                #     "cred_type": "anoncreds",
                #     "cred_protocol": "v1.0",
                #     "cred_def_id": "...",
                #     "credential":  ...
                #     "issue_role": "issuer",
                #     "issue_state": "credential_acked",
                #     "workflow_id": "62d15719-5166-46c5-9b0f-056d818dc4f8",
                #     "cred_exch_id": "e43c98b0-98ab-4b4e-a224-d1a21f530e45",
                #     "id": "80d27752-3768-4913-95ad-57b7e8f3a95b",
                #     "created_at": "2022-03-18T18:02:59.581580",
                #     "updated_at": "2022-03-18T18:05:13.288659"
                #   },
                #   "workflow": {
                #     "wallet_id": "7284c309-0dcf-440e-9ae9-61439d47ae2a",
                #     "workflow_type": "api.services.IssueCredentialWorkflow",
                #     "workflow_state": "completed",
                #     "workflow_state_msg": null,
                #     "wallet_bearer_token": null,
                #     "id": "62d15719-5166-46c5-9b0f-056d818dc4f8",
                #     "created_at": "2022-03-18T18:02:59.586718",
                #     "updated_at": "2022-03-18T18:05:13.293895"
                #   }
                # }

                # def xform(o):
                #     credential = o["credential"]
                #     workflow = o["workflow"]
                #
                #     credential_data = json.loads(credential["credential"])
                #     simple_cred_data = {}
                #     for d in credential_data["attributes"]:
                #         simple_cred_data[d["name"]] = d["value"]
                #     return {
                #         "id": credential["id"],
                #         "cred_def_id": credential["cred_def_id"],
                #         "data": simple_cred_data,
                #         "state": workflow["workflow_state"],
                #         "created_at": credential["created_at"],
                #         "updated_at": credential["updated_at"]
                #     }
                #
                # iterator = map(xform, resp)
                # return list(iterator)
                return resp
            except ContentTypeError:
                logger.exception("Error getting issued credential list", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


# PRESENTATION EXCHANGES
async def tenant_get_credential_exchanges(
    wallet_id: UUID, wallet_key: UUID, present_req: dict
):
    presentation_id = present_req["id"]
    # find for presentation request
    resp = await tenant_get_creds_for_request(wallet_id, wallet_key, presentation_id)
    cred_results = parse_obj_as(List[CredPrecisForProof], resp)
    present_request = json.loads(present_req["present_request"])
    proof_presentation = build_proof_presentation(present_request, cred_results)

    # submit proof
    resp = await tenant_present_credential(
        wallet_id,
        wallet_key,
        presentation_id,
        proof_presentation,
    )

    return resp


async def tenant_request_credential_presentation(
    wallet_id: UUID,
    wallet_key: UUID,
    connection_id: str,
    alias: str,
    proof_req: dict,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = proof_req
    params = {"pres_protocol": "v1.0", "alias": alias, "connection_id": connection_id}
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_VERIFIER_REQUEST_CREDENTIALS,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error sending credential presentation request", exc_info=True
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_send_credential(wallet_id: UUID, wallet_key: UUID, present_req: dict):
    presentation_id = present_req["id"]
    # find for presentation request
    resp = await tenant_get_creds_for_request(wallet_id, wallet_key, presentation_id)
    cred_results = parse_obj_as(List[CredPrecisForProof], resp)
    present_request = json.loads(present_req["present_request"])
    proof_presentation = build_proof_presentation(present_request, cred_results)

    # submit proof
    resp = await tenant_present_credential(
        wallet_id,
        wallet_key,
        presentation_id,
        proof_presentation,
    )

    return resp


async def tenant_present_credential(
    wallet_id: UUID, wallet_key: UUID, presentation_id: str, proof_presentation: dict
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = proof_presentation
    params = {
        "pres_req_id": presentation_id,
    }
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_HOLDER_PRESENT_CREDS,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error presenting credentials", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_get_cred_requests(
    wallet_id: UUID,
    wallet_key: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {}
    params = {}
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_HOLDER_CREDENTIAL_REQUESTS,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error getting credentials for presentation request", exc_info=True
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_get_creds_for_request(
    wallet_id: UUID,
    wallet_key: UUID,
    presentation_id: str,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {}
    params = {
        "pres_req_id": presentation_id,
    }
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_HOLDER_CREDENTIALS_FOR_REQ,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error getting credentials for presentation request", exc_info=True
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_cred_request_reject(
    wallet_id: UUID, wallet_key: UUID, pres_req_id: UUID
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {}
    params = {"pres_req_id": str(pres_req_id)}
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_HOLDER_CREDENTIAL_REQUEST_REJECT,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error rejecting presentation request", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


# CREDENTIAL OFFER


async def tenant_accept_cred_offer(
    wallet_id: UUID,
    wallet_key: UUID,
    cred_issue_id: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_ACCEPT_CRED_OFFER,
            params={"cred_issue_id": cred_issue_id},
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error accepting credential", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )
