# coding: utf-8

from typing import Dict, List  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
)

from acapy_wrapper.models.extra_models import TokenModel  # noqa: F401
from acapy_wrapper.models.date import Date
from acapy_wrapper.models.endorser_info import EndorserInfo
from acapy_wrapper.models.transaction_jobs import TransactionJobs
from acapy_wrapper.models.transaction_list import TransactionList
from acapy_wrapper.models.transaction_record import TransactionRecord

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/transaction/{tran_id}/resend",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="For Author to resend a particular transaction request",
)
async def transaction_tran_id_resend_post(
    request: Request,
    tran_id: str = Path(None, description="Transaction identifier"),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/{conn_id}/set-endorser-info",
    responses={
        200: {"model": EndorserInfo, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="Set Endorser Info",
)
async def transactions_conn_id_set_endorser_info_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    endorser_did: str = Query(None, description="Endorser DID"),
    endorser_name: str = Query(None, description="Endorser Name"),
) -> EndorserInfo:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/{conn_id}/set-endorser-role",
    responses={
        200: {"model": TransactionJobs, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="Set transaction jobs",
)
async def transactions_conn_id_set_endorser_role_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    transaction_my_job: str = Query(None, description="Transaction related jobs"),
) -> TransactionJobs:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/create-request",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="For author to send a transaction request",
)
async def transactions_create_request_post(
    request: Request,
    tran_id: str = Query(None, description="Transaction identifier"),
    endorser_write_txn: bool = Query(
        None, description="Endorser will write the transaction after endorsing it"
    ),
    body: Date = Body(None, description=""),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/transactions",
    responses={
        200: {"model": TransactionList, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="Query transactions",
)
async def transactions_get(
    request: Request,
) -> TransactionList:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/{tran_id}/cancel",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="For Author to cancel a particular transaction request",
)
async def transactions_tran_id_cancel_post(
    request: Request,
    tran_id: str = Path(None, description="Transaction identifier"),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/{tran_id}/endorse",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="For Endorser to endorse a particular transaction record",
)
async def transactions_tran_id_endorse_post(
    request: Request,
    tran_id: str = Path(None, description="Transaction identifier"),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/transactions/{tran_id}",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="Fetch a single transaction record",
)
async def transactions_tran_id_get(
    request: Request,
    tran_id: str = Path(None, description="Transaction identifier"),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/{tran_id}/refuse",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="For Endorser to refuse a particular transaction record",
)
async def transactions_tran_id_refuse_post(
    request: Request,
    tran_id: str = Path(None, description="Transaction identifier"),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/transactions/{tran_id}/write",
    responses={
        200: {"model": TransactionRecord, "description": "null"},
    },
    tags=["endorse-transaction"],
    summary="For Author / Endorser to write an endorsed transaction to the ledger",
)
async def transactions_tran_id_write_post(
    request: Request,
    tran_id: str = Path(None, description="Transaction identifier"),
) -> TransactionRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
