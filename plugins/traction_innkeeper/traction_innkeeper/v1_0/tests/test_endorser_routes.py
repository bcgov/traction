import json
import logging
from unittest.mock import MagicMock, AsyncMock, patch, ANY

import pytest
from aiohttp import web
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageError
from acapy_agent.protocols.didexchange.v1_0.manager import DIDXManagerError

# Import the module containing the routes to be tested
# Adjust path as necessary
from traction_innkeeper.v1_0.endorser import routes as test_module

# Import Service and Models used for mocking
from traction_innkeeper.v1_0.endorser.endorser_connection_service import (
    EndorserConnectionService,
)

# Import models needed for the handlers' logic
from traction_innkeeper.v1_0.innkeeper.models import TenantRecord
from acapy_agent.connections.models.conn_record import ConnRecord

# Needed for injection in endorser_connection_set
from traction_innkeeper.v1_0.innkeeper.tenant_manager import TenantManager

# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_TENANT_WALLET_ID = "tenant-wallet-id-xyz"
TEST_CONN_ID = "conn-id-1234"
TEST_ENDORSER_ALIAS = "TestEndorser"
TEST_ENDORSER_DID = "did:sov:EndorserDID567"
TEST_API_KEY = "test-endorser-api-key"

# --- Reusable Fixtures (similar to test_innkeeper_routes.py) ---


@pytest.fixture
def mock_profile_inject():
    """Provides a mock injector function and tracks injectable mocks."""
    injectables = {}

    def _injector(cls_to_inject, *args, **kwargs):
        # Handle inject_or by checking if cls_to_inject is a type
        target_cls = (
            cls_to_inject if isinstance(cls_to_inject, type) else type(cls_to_inject)
        )
        mock_instance = injectables.get(target_cls)
        if not mock_instance:
            if args:
                return args[0]  # inject_or default
            # Create a default mock if not found for inject
            return (
                MagicMock(spec=target_cls)
                if isinstance(cls_to_inject, type)
                else MagicMock()
            )
        return mock_instance

    return MagicMock(side_effect=_injector), injectables


@pytest.fixture
def mock_session():
    """Provides a mocked async Session."""
    session = AsyncMock(name="Session")

    async def __aenter__(*args):
        return session

    async def __aexit__(*args):
        pass

    session.__aenter__ = __aenter__
    session.__aexit__ = __aexit__
    return session


@pytest.fixture
def mock_root_profile(mock_session: AsyncMock, mock_profile_inject: tuple):
    """Provides a mocked Root Profile (needed for TenantManager)."""
    # Simpler version, might need more details depending on TenantManager usage
    profile = MagicMock(name="RootProfile", spec=Profile)
    profile.context = MagicMock(name="RootContext")
    profile.settings = {"admin.admin_api_key": "dummy-root-key"}
    profile.context.settings = profile.settings
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    profile.inject_or = profile.inject
    return profile


@pytest.fixture
def mock_profile(mock_session: AsyncMock, mock_profile_inject: tuple):
    """Provides a mocked Tenant Profile."""
    profile = MagicMock(name="TenantProfile", spec=Profile)
    profile.context = MagicMock(name="TenantContext")
    profile.settings = {
        "wallet.id": TEST_TENANT_WALLET_ID,
        "admin.admin_api_key": TEST_API_KEY,
        # Assuming endorser config might be here or root profile
        "endorser.endorser_alias": TEST_ENDORSER_ALIAS,
        "endorser.endorser_public_did": TEST_ENDORSER_DID,
    }
    profile.context.settings = profile.settings
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    profile.inject_or = profile.inject
    return profile


@pytest.fixture
def mock_context(mock_profile: MagicMock):
    """Provides a mocked AdminRequestContext containing the tenant profile."""
    context = MagicMock(name="AdminRequestContext")
    context.profile = mock_profile
    context.inject = mock_profile.inject
    context.inject_or = mock_profile.inject_or
    context.injector = context  # Make context act as injector for service call
    return context


@pytest.fixture
def mock_request(mock_context: MagicMock):
    """Provides a mocked aiohttp.web.Request linked to the context."""
    request = MagicMock(spec=web.Request)
    request.match_info = {}
    request.query = {}
    request.headers = {"x-api-key": TEST_API_KEY}  # Satisfy tenant_authentication

    def getitem_side_effect(key):
        if key == "context":
            return mock_context
        if key == "headers":
            return request.headers
        return MagicMock()

    request.__getitem__.side_effect = getitem_side_effect
    request.json = AsyncMock()
    request._set_match_info = lambda key, value: request.match_info.update({key: value})
    return request


@pytest.fixture
def mock_endorser_service(mock_profile: MagicMock):
    """Provides a mocked EndorserConnectionService AND configures it for injection."""
    service = MagicMock(spec=EndorserConnectionService)
    service.endorser_connection = AsyncMock()
    service.connect_with_endorser = AsyncMock()
    service.endorser_info = MagicMock()
    mock_profile._injectables[EndorserConnectionService] = service
    return service


@pytest.fixture
def mock_tenant_mgr(mock_profile: MagicMock, mock_root_profile: MagicMock):
    """Provides a mocked TenantManager AND configures it for injection."""
    mgr = AsyncMock(spec=TenantManager)
    mgr.profile = mock_root_profile  # TenantManager uses root profile
    mock_profile._injectables[TenantManager] = mgr
    return mgr


# --- Test Cases ---


# Test Endorser Connection Set (POST /tenant/endorser-connection)
@pytest.mark.asyncio
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_endorser_connection_set_success(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
    mock_tenant_mgr: AsyncMock,  # Needed for injection
    mock_root_profile: MagicMock,  # Used by TenantManager
):
    """Test POST /tenant/endorser-connection success."""
    profile = mock_context.profile  # This is the tenant profile

    # Mock TenantRecord retrieval to show tenant is configured as issuer
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.connected_to_endorsers = ["some_endorser_config"]
    mock_tenant_rec.created_public_did = ["some_did"]
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock endorser service methods
    mock_endorser_service.endorser_info.return_value = {
        "endorser_did": TEST_ENDORSER_DID,
        "endorser_name": TEST_ENDORSER_ALIAS,
    }
    mock_conn_rec = MagicMock(spec=ConnRecord)
    mock_conn_rec.serialize.return_value = {
        "connection_id": TEST_CONN_ID,
        "state": "request_sent",
    }
    mock_endorser_service.connect_with_endorser.return_value = mock_conn_rec

    response = await test_module.endorser_connection_set(mock_request)

    # Check injections
    mock_context.inject.assert_any_call(TenantManager)
    mock_context.inject.assert_any_call(EndorserConnectionService)
    # Check TenantRecord query
    mock_root_profile.session.assert_called_once()  # Called within handler
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(
        ANY, TEST_TENANT_WALLET_ID
    )
    # Check service calls
    mock_endorser_service.endorser_info.assert_called_once_with(profile)
    mock_endorser_service.connect_with_endorser.assert_awaited_once_with(
        profile, mock_context.injector
    )
    # Check response
    assert response.status == 200
    assert json.loads(response.body) == {
        "connection_id": TEST_CONN_ID,
        "state": "request_sent",
    }
    mock_conn_rec.serialize.assert_called_once()


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@pytest.mark.parametrize(
    "endorsers, did",
    [
        ([], ["some_did"]),  # No endorser config
        (["some_config"], []),  # No public DID
        ([], []),  # Neither
    ],
)
async def test_endorser_connection_set_tenant_not_issuer(
    MockTenantRecordCls: MagicMock,
    endorsers,
    did,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_tenant_mgr: AsyncMock,
    mock_root_profile: MagicMock,
):
    """Test POST /tenant/endorser-connection when tenant not configured as issuer."""
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.connected_to_endorsers = endorsers
    mock_tenant_rec.created_public_did = did
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.endorser_connection_set(mock_request)

    assert "Tenant is not configured as an issuer" in str(excinfo.value)
    mock_context.inject.assert_called_once_with(TenantManager)
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(
        ANY, TEST_TENANT_WALLET_ID
    )


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_endorser_connection_set_no_endorser_info(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
    mock_tenant_mgr: AsyncMock,
    mock_root_profile: MagicMock,
):
    """Test POST /tenant/endorser-connection when endorser service has no info."""
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.connected_to_endorsers = ["some_config"]
    mock_tenant_rec.created_public_did = ["some_did"]
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)
    mock_endorser_service.endorser_info.return_value = None  # No info configured
    mock_request["context"] = MagicMock()
    mock_request["context"].inject.return_value = mock_endorser_service

    endsrv = mock_request["context"].inject(EndorserConnectionService)
    assert endsrv.endorser_info(2) is None
    with pytest.raises(web.HTTPConflict) as excinfo:
        await test_module.endorser_connection_set(mock_request)

    assert "Endorser is not configured" in str(excinfo.value)
    mock_endorser_service.endorser_info.assert_called_with(mock_context.profile)
    mock_endorser_service.connect_with_endorser.assert_not_called()


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_endorser_connection_set_connect_error(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
    mock_tenant_mgr: AsyncMock,
    mock_root_profile: MagicMock,
):
    """Test POST /tenant/endorser-connection with error during connection."""
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.connected_to_endorsers = ["some_config"]
    mock_tenant_rec.created_public_did = ["some_did"]
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)
    mock_endorser_service.endorser_info.return_value = {"did": "...", "name": "..."}
    mock_endorser_service.connect_with_endorser.side_effect = DIDXManagerError(
        "Failed to connect"
    )

    with pytest.raises(web.HTTPBadRequest) as excinfo:  # Check error_handler mapping
        await test_module.endorser_connection_set(mock_request)

    assert "Failed to connect" in str(excinfo.value)
    mock_endorser_service.connect_with_endorser.assert_awaited_once()


# Test Endorser Connection Get (GET /tenant/endorser-connection)
@pytest.mark.asyncio
async def test_endorser_connection_get_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
):
    """Test GET /tenant/endorser-connection success."""
    profile = mock_context.profile
    mock_conn_rec = MagicMock(spec=ConnRecord)
    mock_conn_rec.serialize.return_value = {
        "connection_id": TEST_CONN_ID,
        "state": "completed",
    }
    mock_endorser_service.endorser_connection.return_value = mock_conn_rec

    response = await test_module.endorser_connection_get(mock_request)

    mock_context.inject_or.assert_called_once_with(EndorserConnectionService)
    mock_endorser_service.endorser_connection.assert_awaited_once_with(profile)
    assert response.status == 200
    assert json.loads(response.body) == {
        "connection_id": TEST_CONN_ID,
        "state": "completed",
    }
    mock_conn_rec.serialize.assert_called_once()


@pytest.mark.asyncio
async def test_endorser_connection_get_not_found(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
):
    """Test GET /tenant/endorser-connection not found."""
    profile = mock_context.profile
    mock_endorser_service.endorser_connection.return_value = (
        None  # Service returns None
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.endorser_connection_get(mock_request)

    assert "Connection with endorser not found" in str(excinfo.value)
    mock_endorser_service.endorser_connection.assert_awaited_once_with(profile)


@pytest.mark.asyncio
async def test_endorser_connection_get_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
):
    """Test GET /tenant/endorser-connection with storage error."""
    profile = mock_context.profile
    mock_endorser_service.endorser_connection.side_effect = StorageError(
        "DB read failed"
    )

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.endorser_connection_get(mock_request)

    assert "DB read failed" in str(excinfo.value)
    mock_endorser_service.endorser_connection.assert_awaited_once_with(profile)


# Test Endorser Info Get (GET /tenant/endorser-info)
@pytest.mark.asyncio
async def test_endorser_info_get_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
):
    """Test GET /tenant/endorser-info success."""
    profile = mock_context.profile
    endorser_info_dict = {
        "endorser_did": TEST_ENDORSER_DID,
        "endorser_name": TEST_ENDORSER_ALIAS,
    }
    mock_endorser_service.endorser_info.return_value = endorser_info_dict

    response = await test_module.endorser_info_get(mock_request)

    mock_context.inject_or.assert_called_once_with(EndorserConnectionService)
    mock_endorser_service.endorser_info.assert_called_once_with(profile)
    assert response.status == 200
    assert json.loads(response.body) == endorser_info_dict


@pytest.mark.asyncio
async def test_endorser_info_get_not_found(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_endorser_service: AsyncMock,
):
    """Test GET /tenant/endorser-info when info not configured."""
    profile = mock_context.profile
    mock_endorser_service.endorser_info.return_value = None

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.endorser_info_get(mock_request)

    assert "Configured Endorser Information not found" in str(excinfo.value)
    mock_endorser_service.endorser_info.assert_called_once_with(profile)


# Test register function
@pytest.mark.asyncio  # Needs to be async because register itself is async
async def test_register():
    """Test route registration."""
    mock_app = MagicMock(spec=web.Application)
    mock_app.add_routes = MagicMock()

    await test_module.register(mock_app)  # Await the async function

    calls = mock_app.add_routes.call_args_list
    assert len(calls) == 1
    registered_routes = calls[0][0][0]
    assert len(registered_routes) == 3
    paths_methods = {(r.path, r.method) for r in registered_routes}
    assert ("/tenant/endorser-connection", "POST") in paths_methods
    assert ("/tenant/endorser-connection", "GET") in paths_methods
    assert ("/tenant/endorser-info", "GET") in paths_methods
