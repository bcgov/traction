import logging
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.db.models.tenant_connection import (
    TenantConnectionCreate,
    TenantConnectionRead,
    TenantConnectionUpdate,
)
from api.endpoints.models.connections import (
    ConnectionProtocolType,
    ConnectionStateType,
    ConnectionRoleType,
    Connection,
    BasicMessage,
)
from api.services.connections import (
    get_connections,
    get_connection_with_alias,
    send_basic_message,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
)
from api.services.tenant_workflows import create_workflow
from api.services.base import BaseWorkflow

from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.db.repositories.tenant_connections import TenantConnectionsRepository

logger = logging.getLogger(__name__)

router = APIRouter()


class TenantConnectionData(BaseModel):
    connection: TenantConnectionRead | None = None
    workflow: TenantWorkflowRead | None = None


@router.get("/", response_model=list[Connection])
async def get_tenant_connections(
    alias: Optional[str] = None,
    connection_protocol: Optional[ConnectionProtocolType] = None,
    invitation_key: Optional[str] = None,
    my_did: Optional[str] = None,
    connection_state: Optional[ConnectionStateType] = None,
    their_did: Optional[str] = None,
    their_role: Optional[ConnectionRoleType] = None,
):
    params = {}
    if alias:
        params["alias"] = alias
    if connection_protocol:
        params["connection_protocol"] = connection_protocol
    if invitation_key:
        params["invitation_key"] = invitation_key
    if my_did:
        params["my_did"] = my_did
    if connection_state:
        params["state"] = connection_state
    if their_did:
        params["their_did"] = their_did
    if their_role:
        params["their_role"] = their_role

    connections = get_connections(params)

    return connections


@router.post("/create-invitation", response_model=TenantConnectionData)
async def create_tenant_invitation(
    alias: str,
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.DIDExchange,
    db: AsyncSession = Depends(get_db),
) -> TenantConnectionData:
    existing_connection = get_connection_with_alias(alias)
    if existing_connection is not None:
        raise HTTPException(
            status_code=500,
            detail=f"Error alias {alias} already in use: {existing_connection}",
        )

    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    connection_repo = TenantConnectionsRepository(db_session=db)

    tenant_connection = TenantConnectionCreate(
        tenant_id=tenant_id,
        wallet_id=wallet_id,
        alias=alias,
        connection_role=ConnectionRoleType.inviter,
        connection_state=ConnectionStateType.start,
        connection_protocol=invitation_type,
    )
    tenant_connection = await connection_repo.create(tenant_connection)

    tenant_workflow = await create_workflow(
        wallet_id,
        TenantWorkflowTypeType.connection,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    connection_update = TenantConnectionUpdate(
        id=tenant_connection.id,
        workflow_id=tenant_workflow.id,
        connection_state=tenant_connection.connection_state,
        connection_protocol=tenant_connection.connection_protocol,
        connection_id=tenant_connection.connection_id,
    )
    tenant_connection = await connection_repo.update(connection_update)
    logger.debug(f">>> Updated tenant_connection: {tenant_connection}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db, tenant_workflow=tenant_workflow
    )
    logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

    # get updated issuer info (should have workflow id etc.)
    tenant_connection = await connection_repo.get_by_id(tenant_connection.id)
    logger.debug(f">>> Updated (final) tenant_connection: {tenant_connection}")

    connection = TenantConnectionData(
        connection=tenant_connection,
        workflow=tenant_workflow,
    )

    return connection


@router.post("/receive-invitation", response_model=TenantConnectionData)
async def receive_tenant_invitation(
    alias: str,
    payload: dict | None = None,
    their_public_did: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> TenantConnectionData:
    existing_connection = get_connection_with_alias(alias)
    if existing_connection is not None:
        raise HTTPException(
            status_code=500, detail=f"Error alias {alias} already in use"
        )

    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    connection_repo = TenantConnectionsRepository(db_session=db)

    tenant_connection = TenantConnectionCreate(
        tenant_id=tenant_id,
        wallet_id=wallet_id,
        alias=alias,
        connection_role=ConnectionRoleType.invitee,
        connection_state=ConnectionStateType.start,
        invitation=json.dumps(payload),
        their_public_did=their_public_did,
    )
    tenant_connection = await connection_repo.create(tenant_connection)

    tenant_workflow = await create_workflow(
        wallet_id,
        TenantWorkflowTypeType.connection,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    connection_update = TenantConnectionUpdate(
        id=tenant_connection.id,
        connection_state=tenant_connection.connection_state,
        connection_protocol=tenant_connection.connection_protocol,
        connection_id=tenant_connection.connection_id,
        invitation=tenant_connection.invitation,
        their_public_did=their_public_did,
        workflow_id=tenant_workflow.id,
    )
    tenant_connection = await connection_repo.update(connection_update)
    logger.debug(f">>> Updated tenant_connection: {tenant_connection}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db, tenant_workflow=tenant_workflow
    )
    logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

    # get updated issuer info (should have workflow id etc.)
    tenant_connection = await connection_repo.get_by_id(tenant_connection.id)
    logger.debug(f">>> Updated (final) tenant_connection: {tenant_connection}")

    connection = TenantConnectionData(
        connection=tenant_connection,
        workflow=tenant_workflow,
    )

    return connection


@router.post("/send-message", response_model=dict)
async def send_tenant_message(
    payload: BasicMessage,
    connection_id: str | None = None,
    alias: str | None = None,
):
    if not connection_id:
        existing_connection = get_connection_with_alias(alias)
        if not existing_connection:
            raise HTTPException(
                status_code=404, detail=f"Error alias {alias} does not exist"
            )
        connection_id = existing_connection.connection_id

    response = send_basic_message(connection_id, payload.content)

    return response
