from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.issue_credential import (
    IssueCredentialCreate,
    IssueCredentialUpdate,
    IssueCredentialRead,
    IssueCredential,
)
from api.db.repositories.base import BaseRepository


class IssueCredentialsRepository(
    BaseRepository[
        IssueCredentialCreate,
        IssueCredentialUpdate,
        IssueCredentialRead,
        IssueCredential,
    ]
):
    @property
    def _in_schema(self) -> Type[IssueCredentialCreate]:
        return IssueCredentialCreate

    @property
    def _upd_schema(self) -> Type[IssueCredentialUpdate]:
        return IssueCredentialUpdate

    @property
    def _schema(self) -> Type[IssueCredentialRead]:
        return IssueCredentialRead

    @property
    def _table(self) -> Type[IssueCredential]:
        return IssueCredential

    async def find_by_tenant_id(
        self, tenant_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[IssueCredentialRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.tenant_id == tenant_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[IssueCredentialRead], items)

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[IssueCredentialRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[IssueCredentialRead], items)

    async def find_by_wallet_id_and_role(
        self, wallet_id: UUID, role: str, offset: int = 0, limit: int = 100
    ) -> List[IssueCredentialRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .where(self._table.issue_role == role)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[IssueCredentialRead], items)

    async def get_by_workflow_id(self, workflow_id: UUID) -> Type[IssueCredentialRead]:
        q = select(self._table).where(self._table.workflow_id == workflow_id)
        result = await self._db_session.execute(q)
        issue_cred = result.scalar_one_or_none()
        if not issue_cred:
            raise DoesNotExist(
                f"{self._table.__name__}<workflow_id:{workflow_id}> does not exist"
            )
        return self._schema.from_orm(issue_cred)

    async def get_by_cred_exch_id(
        self, cred_exch_id: UUID
    ) -> Type[IssueCredentialRead]:
        q = select(self._table).where(self._table.cred_exch_id == cred_exch_id)
        result = await self._db_session.execute(q)
        issue_cred = result.scalar_one_or_none()
        if not issue_cred:
            raise DoesNotExist(
                f"{self._table.__name__}<cred_exch_id:{cred_exch_id}> does not exist"
            )
        return self._schema.from_orm(issue_cred)

    async def get_by_cred_rev_reg_id(
        self, rev_reg_id: str, cred_rev_id: str
    ) -> Type[IssueCredentialRead]:
        q = (
            select(self._table)
            .where(self._table.rev_reg_id == rev_reg_id)
            .where(self._table.cred_rev_id == cred_rev_id)
        )
        result = await self._db_session.execute(q)
        issue_cred = result.scalar_one_or_none()
        if not issue_cred:
            raise DoesNotExist(
                f"{self._table.__name__}<rev_reg_id/cred_rev_id:"
                f"{rev_reg_id}/{cred_rev_id}> does not exist"
            )
        return self._schema.from_orm(issue_cred)
