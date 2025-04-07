import json
import logging
from unittest.mock import MagicMock, AsyncMock, patch, ANY

import pytest
from aiohttp import web
from acapy_agent.core.profile import Profile

# Import the module containing the routes to be tested
# Note: Adjust the import path based on your project structure
from traction_innkeeper.v1_0.innkeeper import routes as test_module

# Import Schemas and Models used for mocking return types or validation
from traction_innkeeper.v1_0.innkeeper.models import (
    ReservationRecord,
    TenantRecord,
    TenantAuthenticationApiRecord,
)
from traction_innkeeper.v1_0.innkeeper.config import (
    InnkeeperWalletConfig,
    EndorserLedgerConfig,
)
from traction_innkeeper.v1_0.innkeeper.utils import (
    ReservationException,
)
from acapy_agent.multitenant.base import BaseMultitenantManager
from acapy_agent.storage.error import StorageNotFoundError
from acapy_agent.version import __version__

# Disable logging noise during tests
logging.disable(logging.CRITICAL)


# --- Constants ---

TEST_INNKEEPER_WALLET_ID = "test-innkeeper-wallet-id"
TEST_INNKEEPER_WALLET_NAME = "TestInnkeeper"
TEST_TENANT_ID = "test-tenant-id-123"
TEST_WALLET_ID = "test-wallet-id-456"  # For a sub-tenant
TEST_RESERVATION_ID = "res-id-789"
TEST_AUTH_API_ID = "auth-api-id-abc"
TEST_API_KEY = "test-api-key-xyz"
TEST_RESERVATION_PWD = "test-res-pwd-123"

# --- Simplified Fixtures (Based on test_tenant_routes.py structure) ---


@pytest.fixture
def mock_profile_inject():
    """Provides a mock injector function and tracks injectable mocks."""
    injectables = {}

    def _injector(cls_to_inject, *args, **kwargs):
        mock_instance = injectables.get(cls_to_inject)
        if not mock_instance:
            return MagicMock()
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
def mock_profile(mock_session: AsyncMock, mock_profile_inject: tuple):
    """Provides a mocked Profile configured as an Innkeeper."""
    profile = MagicMock(name="InnkeeperProfile")
    profile.context = MagicMock(
        name="InnkeeperContext"
    )  # Add context attribute for settings
    profile.settings = {
        "wallet.id": TEST_INNKEEPER_WALLET_ID,
        "wallet.name": TEST_INNKEEPER_WALLET_NAME,
        "wallet.innkeeper": True,  # <<< Mark as Innkeeper
        # Add other base settings if needed by the code under test
        "admin.admin_api_key": "dummy-admin-key",  # If base routes use it
    }
    # Link settings to the nested context expected by some ACA-Py parts
    profile.context.settings = profile.settings
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    return profile


@pytest.fixture
def mock_context(mock_profile: MagicMock):
    """Provides a mocked AdminRequestContext containing the mock innkeeper profile."""
    context = MagicMock(name="AdminRequestContext")
    context.profile = mock_profile
    return context


@pytest.fixture
def mock_request(mock_context: MagicMock):
    """Provides a mocked aiohttp.web.Request linked to the innkeeper context."""
    request = MagicMock(spec=web.Request)
    request.match_info = {}
    request.query = {}
    request.headers = {}  # Innkeeper routes might rely on tenant token auth

    # Configure __getitem__ specifically for the "context" key
    def getitem_side_effect(key):
        if key == "context":
            return mock_context
        return MagicMock()

    request.__getitem__.side_effect = getitem_side_effect

    request.json = AsyncMock()
    # Helper to easily set request body
    request._set_json_body = lambda data: setattr(request.json, "return_value", data)
    # Helper to easily set match_info
    request._set_match_info = lambda key, value: request.match_info.update({key: value})

    return request


@pytest.fixture
def mock_tenant_mgr(mock_profile: MagicMock):
    """Provides a mocked TenantManager AND configures it for injection."""
    mgr = AsyncMock(spec=test_module.TenantManager)
    mgr.profile = mock_profile  # Link profile
    # Mock config attributes needed by routes
    mgr._config = MagicMock()
    mgr._config.reservation = MagicMock(auto_approve=False)
    mgr._config.innkeeper_wallet = MagicMock(spec=InnkeeperWalletConfig)
    mgr._config.innkeeper_wallet.connect_to_endorser = []
    mgr._config.innkeeper_wallet.create_public_did = []

    mock_profile._injectables[test_module.TenantManager] = mgr
    return mgr


@pytest.fixture
def mock_multitenant_mgr(mock_profile: MagicMock):
    """Provides a mocked BaseMultitenantManager AND configures it for injection."""
    mgr = AsyncMock(spec=BaseMultitenantManager)
    mgr.profile = mock_profile  # Link profile
    mock_profile._injectables[BaseMultitenantManager] = mgr
    return mgr


# --- Test Cases ---


# Test Reservation Creation (POST /innkeeper/reservations)
# This route just calls the non-innkeeper version, so we mostly test the pass-through
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.tenant_reservation")
async def test_innkeeper_tenant_reservation(
    mock_underlying_handler: AsyncMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test POST /innkeeper/reservations endpoint."""
    profile = mock_context.profile  # Needed to check innkeeper status

    # Mock the return value of the underlying handler
    mock_response_data = {"reservation_id": TEST_RESERVATION_ID}
    mock_underlying_handler.return_value = web.json_response(
        mock_response_data, status=200
    )

    response = await test_module.innkeeper_tenant_reservation(mock_request)

    # 1. Check innkeeper_only decorator logic (implicitly passed by profile setup)
    assert profile.settings.get("wallet.innkeeper") is True
    # 2. Check that the underlying handler was called
    mock_underlying_handler.assert_awaited_once_with(mock_request)
    # 3. Check that the response from the underlying handler is returned
    assert response.status == 200
    assert json.loads(response.body) == mock_response_data


# Test Default Config Settings (GET /innkeeper/default-config)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
async def test_tenant_default_config_settings(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_tenant_mgr: MagicMock,  # Need the instance to configure its config
):
    """Test GET /innkeeper/default-config endpoint."""
    mock_context.inject.return_value = mock_tenant_mgr
    profile = mock_context.profile

    # Configure the mock manager's config
    mock_endorser_config = MagicMock(
        spec=EndorserLedgerConfig,
    )
    mock_endorser_config.serialize.return_value = {"endorser_alias": "test-endorser"}
    # Get the specific mock objects for the nested config
    mock_wallet_config = mock_tenant_mgr._config.innkeeper_wallet

    # Set attributes directly on the target mock objects
    mock_wallet_config.connect_to_endorser = [mock_endorser_config]
    mock_wallet_config.create_public_did = ["did:sov:123"]  # Assign the actual list
    expected_response = {
        "connected_to_endorsers": [{"endorser_alias": "test-endorser"}],
        "created_public_did": ["did:sov:123"],
    }

    response = await test_module.tenant_default_config_settings(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    assert response.status == 200
    assert json.loads(response.body) == expected_response


# Test Tenant Config Update (PUT /innkeeper/tenants/{tenant_id}/config)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_config_update(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test PUT /innkeeper/tenants/{tenant_id}/config endpoint."""
    profile = mock_context.profile
    update_body = {
        "connect_to_endorser": [{"endorser_alias": "new-endorser"}],
        "create_public_did": ["did:sov:xyz"],
        "enable_ledger_switch": True,
        "curr_ledger_id": "ledger-2",
    }

    # Mock request body and match_info
    mock_request._set_json_body(update_body)
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval and save
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.serialize.return_value = {
        "tenant_id": TEST_TENANT_ID,
        "wallet_id": TEST_WALLET_ID,
    }
    MockTenantRecordCls.retrieve_by_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.tenant_config_update(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    mock_request.json.assert_awaited_once()
    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)

    # Check attributes were updated before save
    assert mock_tenant_rec.connected_to_endorsers == update_body["connect_to_endorser"]
    assert mock_tenant_rec.created_public_did == update_body["create_public_did"]
    assert mock_tenant_rec.enable_ledger_switch == update_body["enable_ledger_switch"]
    assert mock_tenant_rec.curr_ledger_id == update_body["curr_ledger_id"]

    mock_tenant_rec.save.assert_awaited_once_with(ANY)
    mock_tenant_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_id": TEST_TENANT_ID,
        "wallet_id": TEST_WALLET_ID,
    }


# Test Reservation Config Update (PUT /innkeeper/reservations/{reservation_id}/config)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.ReservationRecord", autospec=True)
async def test_innkeeper_tenant_res_update(
    MockReservationRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test PUT /innkeeper/reservations/{reservation_id}/config endpoint."""
    profile = mock_context.profile
    update_body = {
        "connect_to_endorser": [{"endorser_alias": "res-endorser"}],
        "create_public_did": ["did:sov:res"],
    }

    # Mock request body and match_info
    mock_request._set_json_body(update_body)
    mock_request._set_match_info("reservation_id", TEST_RESERVATION_ID)

    # Mock ReservationRecord retrieval and save
    mock_res_rec = AsyncMock(spec=ReservationRecord)
    mock_res_rec.serialize.return_value = {"reservation_id": TEST_RESERVATION_ID}
    MockReservationRecordCls.retrieve_by_reservation_id = AsyncMock(
        return_value=mock_res_rec
    )

    response = await test_module.innkeeper_tenant_res_update(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    mock_request.json.assert_awaited_once()
    MockReservationRecordCls.retrieve_by_reservation_id.assert_awaited_once_with(
        ANY, TEST_RESERVATION_ID
    )

    # Check attributes were updated before save
    assert mock_res_rec.connect_to_endorsers == update_body["connect_to_endorser"]
    assert mock_res_rec.create_public_did == update_body["create_public_did"]

    mock_res_rec.save.assert_awaited_once_with(ANY)
    mock_res_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body) == {"reservation_id": TEST_RESERVATION_ID}


# Test Reservations List (GET /innkeeper/reservations/)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.ReservationRecord", autospec=True)
async def test_innkeeper_reservations_list(
    MockReservationRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/reservations/ endpoint."""
    profile = mock_context.profile

    # Mock ReservationRecord query
    mock_rec_1 = MagicMock(spec=ReservationRecord)
    mock_rec_1.serialize.return_value = {"reservation_id": "res-1"}
    mock_rec_2 = MagicMock(spec=ReservationRecord)
    mock_rec_2.serialize.return_value = {"reservation_id": "res-2"}
    MockReservationRecordCls.query = AsyncMock(return_value=[mock_rec_1, mock_rec_2])

    response = await test_module.innkeeper_reservations_list(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockReservationRecordCls.query.assert_awaited_once_with(
        session=ANY, tag_filter={}, post_filter_positive={}, alt=True
    )
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [{"reservation_id": "res-1"}, {"reservation_id": "res-2"}]
    }


# Test Reservation Approve (PUT /innkeeper/reservations/{reservation_id}/approve)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.approve_reservation")
async def test_innkeeper_reservations_approve(
    mock_approve_helper: AsyncMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_tenant_mgr: MagicMock,  # Need instance to pass to helper
):
    """Test PUT /innkeeper/reservations/{reservation_id}/approve endpoint."""
    profile = mock_context.profile
    approve_body = {"state_notes": "Welcome!"}

    # Mock request body and match_info
    mock_request._set_json_body(approve_body)
    mock_request._set_match_info("reservation_id", TEST_RESERVATION_ID)

    # Mock helper return value
    mock_approve_helper.return_value = TEST_RESERVATION_PWD

    response = await test_module.innkeeper_reservations_approve(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    mock_request.json.assert_awaited_once()
    mock_approve_helper.assert_awaited_once_with(
        TEST_RESERVATION_ID, approve_body["state_notes"], ANY
    )
    assert response.status == 200
    assert json.loads(response.body) == {"reservation_pwd": TEST_RESERVATION_PWD}


# Test Reservation Approve - Conflict
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.approve_reservation")
async def test_innkeeper_reservations_approve_conflict(
    mock_approve_helper: AsyncMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_tenant_mgr: MagicMock,
):
    """Test PUT /innkeeper/reservations/{reservation_id}/approve endpoint conflict."""
    approve_body = {"state_notes": "Welcome!"}

    # Mock request body and match_info
    mock_request._set_json_body(approve_body)
    mock_request._set_match_info("reservation_id", TEST_RESERVATION_ID)

    # Mock helper to raise exception
    mock_approve_helper.side_effect = ReservationException("Already approved")

    with pytest.raises(web.HTTPConflict) as excinfo:
        await test_module.innkeeper_reservations_approve(mock_request)
    assert "Already approved" in str(excinfo.value)

    mock_approve_helper.assert_awaited_once_with(
        TEST_RESERVATION_ID, approve_body["state_notes"], ANY
    )


# Test Reservation Refresh Password (PUT /innkeeper/reservations/{reservation_id}/refresh-password)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.refresh_registration_token")
async def test_innkeeper_reservations_refresh_password(
    mock_refresh_helper: AsyncMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_tenant_mgr: MagicMock,
):
    """Test PUT /innkeeper/reservations/{reservation_id}/refresh-password endpoint."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("reservation_id", TEST_RESERVATION_ID)

    # Mock helper return value
    new_pwd = "refreshed-pwd"
    mock_refresh_helper.return_value = new_pwd

    response = await test_module.innkeeper_reservations_refresh_password(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    mock_refresh_helper.assert_awaited_once_with(TEST_RESERVATION_ID, ANY)
    assert response.status == 200
    assert json.loads(response.body) == {"reservation_pwd": new_pwd}


# Test Reservation Deny (PUT /innkeeper/reservations/{reservation_id}/deny)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.ReservationRecord", autospec=True)
async def test_innkeeper_reservations_deny(
    MockReservationRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test PUT /innkeeper/reservations/{reservation_id}/deny endpoint."""
    profile = mock_context.profile
    deny_body = {"state_notes": "No room."}

    # Mock request body and match_info
    mock_request._set_json_body(deny_body)
    mock_request._set_match_info("reservation_id", TEST_RESERVATION_ID)

    # States as strings for serialization
    MockReservationRecordCls.STATE_DENIED = "denied"
    MockReservationRecordCls.STATE_REQUESTED = "requested"

    # Mock ReservationRecord retrieval (state=REQUESTED) and save
    mock_res_rec = MagicMock(
        spec=ReservationRecord, state=MockReservationRecordCls.STATE_REQUESTED
    )
    mock_res_rec.serialize.return_value = {
        "reservation_id": TEST_RESERVATION_ID,
        "state": MockReservationRecordCls.STATE_DENIED,
    }
    MockReservationRecordCls.retrieve_by_reservation_id = AsyncMock(
        return_value=mock_res_rec
    )

    response = await test_module.innkeeper_reservations_deny(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    mock_request.json.assert_awaited_once()
    MockReservationRecordCls.retrieve_by_reservation_id.assert_awaited_once_with(
        ANY, TEST_RESERVATION_ID, for_update=True
    )

    # Check state and notes updated before save
    assert mock_res_rec.state == MockReservationRecordCls.STATE_DENIED
    assert mock_res_rec.state_notes == deny_body["state_notes"]

    mock_res_rec.save.assert_awaited_once_with(ANY)
    mock_res_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body)["state"] == MockReservationRecordCls.STATE_DENIED


# Test Reservation Deny - Conflict
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.ReservationRecord", autospec=True)
async def test_innkeeper_reservations_deny_conflict(
    MockReservationRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test PUT /innkeeper/reservations/{reservation_id}/deny endpoint conflict."""
    deny_body = {"state_notes": "No room."}

    # Mock request body and match_info
    mock_request._set_json_body(deny_body)
    mock_request._set_match_info("reservation_id", TEST_RESERVATION_ID)

    # Mock ReservationRecord retrieval (state=APPROVED)
    mock_res_rec = AsyncMock(
        spec=ReservationRecord, state=ReservationRecord.STATE_APPROVED
    )
    MockReservationRecordCls.retrieve_by_reservation_id = AsyncMock(
        return_value=mock_res_rec
    )

    with pytest.raises(web.HTTPConflict) as excinfo:
        await test_module.innkeeper_reservations_deny(mock_request)
    assert f"state is currently '{ReservationRecord.STATE_APPROVED}'" in str(
        excinfo.value
    )

    # Check retrieval was attempted
    MockReservationRecordCls.retrieve_by_reservation_id.assert_awaited_once_with(
        ANY, TEST_RESERVATION_ID, for_update=True
    )


# Test Tenants List (GET /innkeeper/tenants/)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenants_list_default(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/tenants/ endpoint (default state=active)."""
    profile = mock_context.profile

    MockTenantRecordCls.STATE_ACTIVE = "active"
    # Mock TenantRecord query
    mock_rec_1 = MagicMock(spec=TenantRecord)
    mock_rec_1.serialize.return_value = {
        "tenant_id": "t-1",
        "state": TenantRecord.STATE_ACTIVE,
    }
    MockTenantRecordCls.query = AsyncMock(return_value=[mock_rec_1])

    response = await test_module.innkeeper_tenants_list(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    # Default filter is state=active
    MockTenantRecordCls.query.assert_awaited_once_with(
        session=ANY,
        tag_filter={"state": TenantRecord.STATE_ACTIVE},
        post_filter_positive={},
        alt=True,
    )
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [{"tenant_id": "t-1", "state": TenantRecord.STATE_ACTIVE}]
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenants_list_deleted(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/tenants/?state=deleted endpoint."""
    profile = mock_context.profile

    # Set query parameter
    mock_request.query["state"] = TenantRecord.STATE_DELETED

    # Mock TenantRecord query
    mock_rec_1 = MagicMock(spec=TenantRecord)
    mock_rec_1.serialize.return_value = {
        "tenant_id": "t-del",
        "state": TenantRecord.STATE_DELETED,
    }
    MockTenantRecordCls.query = AsyncMock(return_value=[mock_rec_1])

    response = await test_module.innkeeper_tenants_list(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockTenantRecordCls.query.assert_awaited_once_with(
        session=ANY,
        tag_filter={"state": TenantRecord.STATE_DELETED},
        post_filter_positive={},
        alt=True,
    )
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [{"tenant_id": "t-del", "state": TenantRecord.STATE_DELETED}]
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenants_list_all(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/tenants/?state=all endpoint."""
    profile = mock_context.profile

    # Set query parameter
    mock_request.query["state"] = "all"

    # Mock TenantRecord query
    mock_rec_1 = MagicMock(spec=TenantRecord)
    mock_rec_1.serialize.return_value = {
        "tenant_id": "t-1",
        "state": TenantRecord.STATE_ACTIVE,
    }
    mock_rec_2 = MagicMock(spec=TenantRecord)
    mock_rec_2.serialize.return_value = {
        "tenant_id": "t-del",
        "state": TenantRecord.STATE_DELETED,
    }
    MockTenantRecordCls.query = AsyncMock(return_value=[mock_rec_1, mock_rec_2])

    response = await test_module.innkeeper_tenants_list(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    # No state filter when state=all
    MockTenantRecordCls.query.assert_awaited_once_with(
        session=ANY, tag_filter={}, post_filter_positive={}, alt=True
    )
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [
            {"tenant_id": "t-1", "state": TenantRecord.STATE_ACTIVE},
            {"tenant_id": "t-del", "state": TenantRecord.STATE_DELETED},
        ]
    }


# Test Tenant Get (GET /innkeeper/tenants/{tenant_id})
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenant_get(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/tenants/{tenant_id} endpoint."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval
    mock_tenant_rec = MagicMock(spec=TenantRecord)
    mock_tenant_rec.serialize.return_value = {"tenant_id": TEST_TENANT_ID}
    MockTenantRecordCls.retrieve_by_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.innkeeper_tenant_get(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)
    mock_tenant_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body) == {"tenant_id": TEST_TENANT_ID}


# Test Tenant Soft Delete (DELETE /innkeeper/tenants/{tenant_id})
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenant_delete(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test DELETE /innkeeper/tenants/{tenant_id} endpoint (soft delete)."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval and soft_delete
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    MockTenantRecordCls.retrieve_by_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.innkeeper_tenant_delete(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)
    mock_tenant_rec.soft_delete.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "success": f"Tenant {TEST_TENANT_ID} soft deleted."
    }


# Test Tenant Soft Delete - Not Found
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenant_delete_not_found(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test DELETE /innkeeper/tenants/{tenant_id} endpoint not found."""

    # Mock request match_info
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval to raise error
    MockTenantRecordCls.retrieve_by_id = AsyncMock(
        side_effect=StorageNotFoundError("Not found")
    )

    with pytest.raises(web.HTTPNotFound):
        await test_module.innkeeper_tenant_delete(mock_request)

    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)


# Test Tenant Hard Delete (DELETE /innkeeper/tenants/{tenant_id}/hard)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr", "mock_multitenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@patch(f"{test_module.__name__}.WalletRecord", autospec=True)
async def test_innkeeper_tenant_hard_delete(
    MockWalletRecordCls: MagicMock,  # Added patch
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_multitenant_mgr: MagicMock,  # Need instance
):
    """Test DELETE /innkeeper/tenants/{tenant_id}/hard endpoint."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval and delete
    mock_tenant_rec = AsyncMock(spec=TenantRecord, wallet_id=TEST_WALLET_ID)
    MockTenantRecordCls.retrieve_by_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock WalletRecord retrieval (needed by handler)
    MockWalletRecordCls.retrieve_by_id = AsyncMock()

    # Mock multitenant manager remove_wallet
    mock_multitenant_mgr.remove_wallet = AsyncMock()

    response = await test_module.innkeeper_tenant_hard_delete(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True

    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)
    MockWalletRecordCls.retrieve_by_id.assert_awaited_once_with(
        ANY, TEST_WALLET_ID
    )  # Verify wallet check
    mock_multitenant_mgr.remove_wallet.assert_awaited_once_with(TEST_WALLET_ID)
    mock_tenant_rec.delete_record.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "success": f"Tenant {TEST_TENANT_ID} hard deleted."
    }


# Test Tenant Restore (PUT /innkeeper/tenants/{tenant_id}/restore)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenant_restore(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test PUT /innkeeper/tenants/{tenant_id}/restore endpoint."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval (state=DELETED) and restore_deleted
    mock_tenant_rec = AsyncMock(
        spec=TenantRecord, state=MockTenantRecordCls.STATE_DELETED
    )
    MockTenantRecordCls.retrieve_by_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.innkeeper_tenant_restore(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)
    mock_tenant_rec.restore_deleted.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "success": f"Tenant {TEST_TENANT_ID} restored."
    }


# Test Tenant Restore - Not Deleted
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_innkeeper_tenant_restore_not_deleted(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test PUT /innkeeper/tenants/{tenant_id}/restore endpoint when not deleted."""

    # Mock request match_info
    mock_request._set_match_info("tenant_id", TEST_TENANT_ID)

    # Mock TenantRecord retrieval (state=ACTIVE)
    mock_tenant_rec = AsyncMock(spec=TenantRecord, state=TenantRecord.STATE_ACTIVE)
    MockTenantRecordCls.retrieve_by_id = AsyncMock(return_value=mock_tenant_rec)

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.innkeeper_tenant_restore(mock_request)
    assert f"Tenant {TEST_TENANT_ID} is not deleted" in str(excinfo.value)

    MockTenantRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_TENANT_ID)


# Test Create API Key (POST /innkeeper/authentications/api)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
@patch(f"{test_module.__name__}.create_api_key")
async def test_innkeeper_authentications_api_create(
    mock_create_api_key_helper: AsyncMock,
    MockTenantAuthApiRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_tenant_mgr: MagicMock,  # Need instance for helper
):
    """Test POST /innkeeper/authentications/api endpoint."""
    profile = mock_context.profile
    create_body = {"tenant_id": TEST_TENANT_ID, "alias": "Innkeeper Test Key"}

    # Mock request body
    mock_request._set_json_body(create_body)

    # Mock TenantAuthenticationApiRecord constructor (used internally)
    mock_auth_rec_instance = MagicMock(spec=TenantAuthenticationApiRecord)
    MockTenantAuthApiRecordCls.return_value = mock_auth_rec_instance

    # Mock helper return value
    mock_create_api_key_helper.return_value = (TEST_API_KEY, TEST_AUTH_API_ID)

    response = await test_module.innkeeper_authentications_api(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    mock_request.json.assert_awaited_once()

    MockTenantAuthApiRecordCls.assert_called_once_with(**create_body)

    mock_create_api_key_helper.assert_awaited_once_with(mock_auth_rec_instance, ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_authentication_api_id": TEST_AUTH_API_ID,
        "api_key": TEST_API_KEY,
    }


# Test List API Keys (GET /innkeeper/authentications/api/)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_innkeeper_authentications_api_list(
    MockTenantAuthApiRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/authentications/api/ endpoint."""
    profile = mock_context.profile

    # Mock query
    mock_rec_1 = MagicMock(spec=TenantAuthenticationApiRecord)
    mock_rec_1.serialize.return_value = {"tenant_authentication_api_id": "api-1"}
    mock_rec_2 = MagicMock(spec=TenantAuthenticationApiRecord)
    mock_rec_2.serialize.return_value = {"tenant_authentication_api_id": "api-2"}
    MockTenantAuthApiRecordCls.query = AsyncMock(return_value=[mock_rec_1, mock_rec_2])

    response = await test_module.innkeeper_authentications_api_list(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockTenantAuthApiRecordCls.query.assert_awaited_once_with(
        session=ANY, tag_filter={}, post_filter_positive={}, alt=True
    )
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [
            {"tenant_authentication_api_id": "api-1"},
            {"tenant_authentication_api_id": "api-2"},
        ]
    }


# Test Get API Key (GET /innkeeper/authentications/api/{id})
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_innkeeper_authentications_api_get(
    MockTenantAuthApiRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test GET /innkeeper/authentications/api/{id} endpoint."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("tenant_authentication_api_id", TEST_AUTH_API_ID)

    # Mock retrieval
    mock_auth_rec = MagicMock(spec=TenantAuthenticationApiRecord)
    mock_auth_rec.serialize.return_value = {
        "tenant_authentication_api_id": TEST_AUTH_API_ID
    }
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id = AsyncMock(
        return_value=mock_auth_rec
    )

    response = await test_module.innkeeper_authentications_api_get(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.assert_awaited_once_with(
        ANY, TEST_AUTH_API_ID
    )
    mock_auth_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_authentication_api_id": TEST_AUTH_API_ID
    }


# Test Delete API Key (DELETE /innkeeper/authentications/api/{id})
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_innkeeper_authentications_api_delete(
    MockTenantAuthApiRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,
):
    """Test DELETE /innkeeper/authentications/api/{id} endpoint."""
    profile = mock_context.profile

    # Mock request match_info
    mock_request._set_match_info("tenant_authentication_api_id", TEST_AUTH_API_ID)

    # Mock retrieval and delete
    mock_auth_rec = AsyncMock(spec=TenantAuthenticationApiRecord)
    # Simulate retrieve succeeding the first time, failing the second time (after delete)
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.side_effect = [
        mock_auth_rec,
        StorageNotFoundError("Not Found after delete"),
    ]

    response = await test_module.innkeeper_authentications_api_delete(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_context.inject.assert_called_once_with(test_module.TenantManager)

    assert MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.await_count == 2
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.assert_any_await(
        ANY, TEST_AUTH_API_ID
    )

    mock_auth_rec.delete_record.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {"success": True}


# Test Config Handler (GET /innkeeper/server/status/config)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
async def test_innkeeper_config_handler(
    mock_request: MagicMock,
    # mock_context: MagicMock,
    # mock_profile: MagicMock,  # Need the profile directly to check settings
):
    """Test GET /innkeeper/server/status/config endpoint."""
    profile: Profile = mock_request["context"].profile
    # Add some more settings to the mock profile context for the test
    profile.context.settings = {
        "admin.admin_api_key": "dummy-admin-key",
        "wallet.id": "test-innkeeper-wallet-id",
        "wallet.innkeeper": True,
        "wallet.name": "TestInnkeeper",
        "default_label": "TestAgent",
        "wallet.key": "SHOULD_BE_REMOVED",
        "plugin_config": {
            "traction_innkeeper": {
                "innkeeper_wallet": {"wallet_key": "SHOULD_BE_REMOVED_NESTED"}
            }
        },
        "some_other_setting": "value",
    }
    # Ensure wallet.innkeeper is still True from the fixture
    assert profile.context.settings["wallet.innkeeper"] is True
    # assert mock_request["context"].profile.context.settings["plugin_config"] is True

    # Expected config structure (keys removed, version added)

    mock_request["context"].profile = profile
    mock_request["context"].inject.return_value = mock_request["context"]

    response = await test_module.innkeeper_config_handler(mock_request)

    assert profile.settings.get("wallet.innkeeper") is True
    mock_request["context"].inject.assert_called_once_with(test_module.TenantManager)
    assert response.status == 200
    response_body = json.loads(response.body)

    # Check that sensitive keys are NOT present
    assert "admin.admin_api_key" not in response_body["config"]
    assert "wallet.key" not in response_body["config"]
    assert (
        "wallet_key"
        not in response_body["config"]["plugin_config"]["traction_innkeeper"][
            "innkeeper_wallet"
        ]
    )

    # Check that expected keys ARE present
    assert response_body["config"]["wallet.id"] == TEST_INNKEEPER_WALLET_ID
    assert response_body["config"]["version"] == __version__
    assert response_body["config"]["some_other_setting"] == "value"
