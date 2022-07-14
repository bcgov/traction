from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from api.db.session import TenantContext, tenant_context
from api.endpoints.dependencies.tenant_security import get_from_context


class TenantContextRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:

            global tenant_context
            tenant_context = TenantContext(
                tenant_wallet_id=get_from_context("TENANT_WALLET_ID"),
                tenant_id=get_from_context("TENANT_ID"),
            )
            print("TENANT_CONTEXT")
            print(tenant_context)
            response: Response = await original_route_handler(request)
            if await request.body():
                print(await request.body())

            return response

        return custom_route_handler
