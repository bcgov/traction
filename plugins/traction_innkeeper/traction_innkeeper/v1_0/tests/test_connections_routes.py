import json
import logging
from unittest.mock import MagicMock, AsyncMock, patch, ANY

import pytest
from aiohttp import web
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError
from acapy_agent.messaging.models.base import BaseModelError

# Import the module containing the routes to be tested
from traction_innkeeper.v1_0.connections import routes as test_module

# Import Schemas and Models used for mocking return types or validation
from acapy_agent.connections.models.conn_record import ConnRecord
from acapy_agent.protocols.connections.v1_0.messages.connection_invitation import (
    ConnectionInvitation,
)

# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---

TEST_CONN_ID = "conn-id-abc-123"
TEST_INVITATION_KEY = "invite-key-xyz-789"
TEST_BASE_URL = "http://test-agent.com"
TEST_DEFAULT_ENDPOINT = "http://default.endpoint.com"
TEST_ALIAS = "Test Alias"

# --- Reusable Fixtures (similar to test_innkeeper_routes.py) ---


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
    """Provides a mocked Profile."""
    profile = MagicMock(name="Profile")
    profile.context = MagicMock(name="Context")
    profile.settings = {
        "multitenant.enabled": True,
        # Base settings potentially needed
        "admin.admin_api_key": "dummy-admin-key",
        # Settings specific to connections_invitation
        "invite_base_url": TEST_BASE_URL,
        "default_endpoint": TEST_DEFAULT_ENDPOINT,
    }
    profile.context.settings = profile.settings
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    return profile


@pytest.fixture
def mock_context(mock_profile: MagicMock):
    """Provides a mocked AdminRequestContext containing the mock profile."""
    context = MagicMock(name="AdminRequestContext")
    context.profile = mock_profile
    return context


@pytest.fixture
def mock_request(mock_context: MagicMock):
    """Provides a mocked aiohttp.web.Request linked to the context."""
    request = MagicMock(spec=web.Request)
    request.match_info = {}
    request.query = {}
    test_api_key = "dummy-test-key"
    request.headers = {
        "Authorization": test_api_key,
        "x-api-key": test_api_key,
    }

    def getitem_side_effect(key):
        if key == "context":
            return mock_context
        return MagicMock()

    request.__getitem__.side_effect = getitem_side_effect

    request.json = AsyncMock()
    request._set_match_info = lambda key, value: request.match_info.update({key: value})

    return request


# --- Test Cases for connections_invitation ---


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.ConnRecord", autospec=True)
async def test_connections_invitation_direct(
    MockConnRecordCls: MagicMock, mock_request: MagicMock, mock_profile: MagicMock
):
    """Test GET /connections/{conn_id}/invitation - direct invitation found."""
    mock_request._set_match_info("conn_id", TEST_CONN_ID)
    mock_profile.settings["invite_base_url"] = TEST_BASE_URL  # Ensure base url is set

    # Mock ConnectionRecord and its invitation
    mock_conn_rec = AsyncMock(spec=ConnRecord, alias=TEST_ALIAS)
    mock_invitation = MagicMock(spec=ConnectionInvitation)
    mock_invitation.serialize.return_value = {
        "@type": "did:sov:...",
        "recipientKeys": ["key1"],
    }
    mock_invitation.to_url.return_value = (
        f"{TEST_BASE_URL}?c_i=ey..."  # Returns full URL
    )

    mock_conn_rec.retrieve_invitation = AsyncMock(return_value=mock_invitation)
    MockConnRecordCls.retrieve_by_id = AsyncMock(return_value=mock_conn_rec)

    response = await test_module.connections_invitation(mock_request)

    MockConnRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_CONN_ID)
    mock_conn_rec.retrieve_invitation.assert_awaited_once_with(ANY)
    mock_invitation.to_url.assert_called_once_with(TEST_BASE_URL)
    mock_invitation.serialize.assert_called_once()

    assert response.status == 200
    expected_body = {
        "connection_id": TEST_CONN_ID,
        "invitation": mock_invitation.serialize.return_value,
        "invitation_url": mock_invitation.to_url.return_value,
        "alias": TEST_ALIAS,
    }
    assert json.loads(response.body) == expected_body


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.ConnRecord", autospec=True)
async def test_connections_invitation_multi_use(
    MockConnRecordCls: MagicMock, mock_request: MagicMock, mock_profile: MagicMock
):
    """Test GET /connections/{conn_id}/invitation - multi-use invitation found."""
    mock_request._set_match_info("conn_id", TEST_CONN_ID)
    # Use default_endpoint as base url
    del mock_profile.settings["invite_base_url"]
    mock_profile.settings["default_endpoint"] = TEST_DEFAULT_ENDPOINT

    # Mock primary ConnectionRecord (no alias, direct invite fails)
    mock_conn_rec = AsyncMock(
        spec=ConnRecord, alias=None, invitation_key=TEST_INVITATION_KEY
    )
    mock_conn_rec.retrieve_invitation = AsyncMock(
        side_effect=StorageNotFoundError("Direct invite not found")
    )
    MockConnRecordCls.retrieve_by_id = AsyncMock(return_value=mock_conn_rec)

    # Mock Multi-use ConnectionRecord and its invitation
    mock_multi_use_conn = AsyncMock(spec=ConnRecord)
    mock_multi_use_invitation = MagicMock(spec=ConnectionInvitation)
    mock_multi_use_invitation.serialize.return_value = {
        "@type": "...",
        "label": "MultiUse",
    }
    # Simulate to_url returning only query params
    mock_multi_use_invitation.to_url.return_value = "?c_i=ey..."

    mock_multi_use_conn.retrieve_invitation = AsyncMock(
        return_value=mock_multi_use_invitation
    )
    MockConnRecordCls.retrieve_by_invitation_key = AsyncMock(
        return_value=mock_multi_use_conn
    )

    response = await test_module.connections_invitation(mock_request)

    MockConnRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_CONN_ID)
    mock_conn_rec.retrieve_invitation.assert_awaited_once_with(
        ANY
    )  # First attempt (failed)
    MockConnRecordCls.retrieve_by_invitation_key.assert_awaited_once_with(
        ANY, TEST_INVITATION_KEY
    )
    mock_multi_use_conn.retrieve_invitation.assert_awaited_once_with(
        ANY
    )  # Second attempt (success)
    mock_multi_use_invitation.to_url.assert_called_once_with(TEST_DEFAULT_ENDPOINT)
    mock_multi_use_invitation.serialize.assert_called_once()

    assert response.status == 200
    expected_invitation_url = (
        f"{TEST_DEFAULT_ENDPOINT}{mock_multi_use_invitation.to_url.return_value}"
    )
    expected_body = {
        "connection_id": TEST_CONN_ID,
        "invitation": mock_multi_use_invitation.serialize.return_value,
        "invitation_url": expected_invitation_url,
        # No alias expected
    }
    assert json.loads(response.body) == expected_body


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.ConnRecord", autospec=True)
async def test_connections_invitation_conn_not_found(
    MockConnRecordCls: MagicMock, mock_request: MagicMock, mock_profile: MagicMock
):
    """Test GET /connections/{conn_id}/invitation - Connection not found."""
    mock_request._set_match_info("conn_id", TEST_CONN_ID)
    MockConnRecordCls.retrieve_by_id = AsyncMock(
        side_effect=StorageNotFoundError("Conn not found")
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.connections_invitation(mock_request)
    assert "Conn not found" in str(excinfo.value)

    MockConnRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_CONN_ID)


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.ConnRecord", autospec=True)
async def test_connections_invitation_direct_and_multi_use_not_found(
    MockConnRecordCls: MagicMock, mock_request: MagicMock, mock_profile: MagicMock
):
    """Test GET /connections/{conn_id}/invitation - Both direct and multi-use invitations not found."""
    mock_request._set_match_info("conn_id", TEST_CONN_ID)

    # Mock primary ConnectionRecord (direct invite fails)
    mock_conn_rec = AsyncMock(
        spec=ConnRecord, alias=None, invitation_key=TEST_INVITATION_KEY
    )
    mock_conn_rec.retrieve_invitation = AsyncMock(
        side_effect=StorageNotFoundError("Direct invite not found")
    )
    MockConnRecordCls.retrieve_by_id = AsyncMock(return_value=mock_conn_rec)

    # Mock multi-use retrieval failure
    MockConnRecordCls.retrieve_by_invitation_key = AsyncMock(
        side_effect=StorageNotFoundError("Multi-use not found")
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.connections_invitation(mock_request)
    assert "Multi-use not found" in str(excinfo.value)  # Error from the second lookup

    MockConnRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_CONN_ID)
    mock_conn_rec.retrieve_invitation.assert_awaited_once_with(ANY)
    MockConnRecordCls.retrieve_by_invitation_key.assert_awaited_once_with(
        ANY, TEST_INVITATION_KEY
    )


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.ConnRecord", autospec=True)
async def test_connections_invitation_base_model_error(
    MockConnRecordCls: MagicMock, mock_request: MagicMock, mock_profile: MagicMock
):
    """Test GET /connections/{conn_id}/invitation - BaseModelError during retrieval."""
    mock_request._set_match_info("conn_id", TEST_CONN_ID)
    MockConnRecordCls.retrieve_by_id = AsyncMock(
        side_effect=BaseModelError("Invalid record data")
    )

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.connections_invitation(mock_request)
    assert "Invalid record data" in str(excinfo.value)

    MockConnRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_CONN_ID)


@pytest.mark.asyncio
@patch(f"{test_module.__name__}.ConnRecord", autospec=True)
async def test_connections_invitation_no_base_url_set(
    MockConnRecordCls: MagicMock, mock_request: MagicMock, mock_profile: MagicMock
):
    """Test GET /connections/{conn_id}/invitation - Neither invite_base_url nor default_endpoint set."""
    mock_request._set_match_info("conn_id", TEST_CONN_ID)
    # Remove both base URL settings
    del mock_profile.settings["invite_base_url"]
    del mock_profile.settings["default_endpoint"]

    # Mock ConnectionRecord and its invitation
    mock_conn_rec = AsyncMock(spec=ConnRecord, alias=None)
    mock_invitation = MagicMock(spec=ConnectionInvitation)
    mock_invitation.serialize.return_value = {
        "@type": "did:sov:...",
        "recipientKeys": ["key1"],
    }
    # Assume to_url returns just the query part when base_url is empty
    mock_invitation.to_url.return_value = "?c_i=ey..."

    mock_conn_rec.retrieve_invitation = AsyncMock(return_value=mock_invitation)
    MockConnRecordCls.retrieve_by_id = AsyncMock(return_value=mock_conn_rec)

    response = await test_module.connections_invitation(mock_request)

    MockConnRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_CONN_ID)
    mock_conn_rec.retrieve_invitation.assert_awaited_once_with(ANY)
    # Expect "" as the base_url passed to to_url
    mock_invitation.to_url.assert_called_once_with("")

    assert response.status == 200
    # The URL should be constructed with an empty base, effectively starting with "?"
    expected_invitation_url = "?c_i=ey..."
    expected_body = {
        "connection_id": TEST_CONN_ID,
        "invitation": mock_invitation.serialize.return_value,
        "invitation_url": expected_invitation_url,
    }
    assert json.loads(response.body) == expected_body
