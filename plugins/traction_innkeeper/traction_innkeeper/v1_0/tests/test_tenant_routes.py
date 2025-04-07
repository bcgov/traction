import json
import logging
from unittest.mock import MagicMock, AsyncMock, patch, ANY

import pytest
from aiohttp import web

# Import the module containing the routes to be tested
from traction_innkeeper.v1_0.tenant import routes as test_module

# Import Schemas and Models used for mocking return types or validation
from traction_innkeeper.v1_0.innkeeper.models import (
    TenantRecord,
    TenantAuthenticationApiRecord,
)
from acapy_agent.wallet.models.wallet_record import WalletRecord
from acapy_agent.multitenant.base import BaseMultitenantManager
from acapy_agent.storage.error import StorageNotFoundError
from acapy_agent.utils.testing import create_test_profile
from acapy_agent.core.profile import Profile

# Disable logging noise during tests
logging.disable(logging.CRITICAL)


# --- Simplified Fixtures ---

TEST_WALLET_ID = "test-wallet-id"
TEST_TENANT_ID = "test-tenant-id"
TEST_API_KEY = "test-secret-key"


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
async def mock_profile(mock_session: AsyncMock, mock_profile_inject: tuple):
    """Provides a mocked Profile with session and injection configured."""
    profile = await create_test_profile(
        {
            "wallet.id": TEST_WALLET_ID,
            "admin.admin_api_key": TEST_API_KEY,
            "wallet.type": "askar",
            "auto_provision": True,
            "wallet.key": "5BngFuBpS4wjFfVFCtPqoix3ZXG2XR8XJ7qosUzMak7R",
            "wallet.key_derivation_method": "RAW",
        }
    )
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    assert isinstance(profile, Profile)
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

    def getitem_side_effect(key):
        if key == "context":
            return mock_context
        return MagicMock()

    request.__getitem__.side_effect = getitem_side_effect
    request.json = AsyncMock()
    request.headers = {"x-api-key": TEST_API_KEY}
    request._set_json_body = lambda data: setattr(request.json, "return_value", data)
    request._set_match_info = lambda key, value: request.match_info.update({key: value})
    return request


@pytest.fixture
def mock_tenant_mgr(mock_profile: MagicMock):
    """Provides a mocked TenantManager AND configures it for injection."""
    mgr = AsyncMock(spec=test_module.TenantManager)
    mgr.profile = mock_profile
    mock_profile._injectables[test_module.TenantManager] = mgr
    return mgr


@pytest.fixture
def mock_multitenant_mgr(mock_profile: MagicMock):
    """Provides a mocked BaseMultitenantManager AND configures it for injection."""
    mgr = AsyncMock(spec=BaseMultitenantManager)
    mgr.profile = mock_profile
    mock_profile._injectables[BaseMultitenantManager] = mgr
    return mgr


# --- Test Cases (Simplified Setup) ---


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_self(
    MockTenantRecordCls: MagicMock,  # Patched Class
    mock_request: MagicMock,
):
    """Test GET /tenant endpoint."""
    # Setup mock TenantRecord instance and its query method
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.serialize.return_value = {
        "tenant_id": TEST_TENANT_ID,
        "wallet_id": TEST_WALLET_ID,
    }
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.tenant_self(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    mock_tenant_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_id": TEST_TENANT_ID,
        "wallet_id": TEST_WALLET_ID,
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.WalletRecord", autospec=True)
@patch(f"{test_module.__name__}.format_wallet_record")
async def test_tenant_wallet_get(
    mock_format_wallet_record: MagicMock,
    MockWalletRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test GET /tenant/wallet endpoint."""
    # Setup mock WalletRecord
    mock_wallet_rec = MagicMock(spec=WalletRecord)
    MockWalletRecordCls.retrieve_by_id = AsyncMock(return_value=mock_wallet_rec)
    mock_format_wallet_record.return_value = {
        "wallet_id": TEST_WALLET_ID,
        "settings": {},
    }

    response = await test_module.tenant_wallet_get(mock_request)

    # Assert
    MockWalletRecordCls.retrieve_by_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    mock_format_wallet_record.assert_called_once_with(mock_wallet_rec)
    assert response.status == 200
    assert json.loads(response.body) == {"wallet_id": TEST_WALLET_ID, "settings": {}}


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_config_get(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test GET /tenant/config endpoint."""
    # Setup mock TenantRecord with attributes
    mock_tenant_rec = MagicMock(
        spec=TenantRecord,
        connected_to_endorsers=[{"endorser_alias": "test-endorser"}],
        created_public_did=[{"did": "test-did"}],
        auto_issuer=True,
        enable_ledger_switch=False,
        curr_ledger_id="test-ledger",
    )
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.tenant_config_get(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    assert response.status == 200
    expected_body = {
        "connect_to_endorser": [{"endorser_alias": "test-endorser"}],
        "create_public_did": [{"did": "test-did"}],
        "auto_issuer": True,
        "enable_ledger_switch": False,
        "curr_ledger_id": "test-ledger",
    }
    assert json.loads(response.body) == expected_body


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_config_ledger_id_set(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test PUT /tenant/config/set-ledger-id endpoint."""
    new_ledger_id = "new-ledger-id"

    # Setup mock request body
    mock_request._set_json_body({"ledger_id": new_ledger_id})

    # Setup mock TenantRecord and its save method
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.curr_ledger_id = "old-ledger-id"  # Initial value to be overwritten
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.tenant_config_ledger_id_set(mock_request)

    # Assert
    mock_request.json.assert_awaited_once()
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    # Check that the attribute was updated before save
    assert mock_tenant_rec.curr_ledger_id == new_ledger_id
    mock_tenant_rec.save.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {"ledger_id": new_ledger_id}


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_multitenant_mgr")
@patch(f"{test_module.__name__}.format_wallet_record")
@patch(f"{test_module.__name__}.get_extra_settings_dict_per_tenant")
async def test_tenant_wallet_update(
    mock_get_extra_settings: MagicMock,
    mock_format_wallet_record: MagicMock,
    mock_request: MagicMock,
    mock_context: MagicMock,  # Used to access profile
    mock_multitenant_mgr: MagicMock,  # Get the instance for asserting calls
):
    """Test PUT /tenant/wallet endpoint."""
    profile = mock_context.profile
    update_body = {
        "label": "New Label",
        "image_url": "http://example.com/img.png",
        "wallet_webhook_urls": ["http://localhost:8080/webhooks"],
        "wallet_dispatch_type": "both",
        "extra_settings": {"some_setting": "value"},
    }

    # Setup mock request body
    mock_request._set_json_body(update_body)

    # Setup mock multitenant manager's update_wallet (on the instance fixture)
    mock_wallet_rec = MagicMock(spec=WalletRecord)
    mock_multitenant_mgr.update_wallet = AsyncMock(return_value=mock_wallet_rec)

    # Setup return value for helper functions
    mock_format_wallet_record.return_value = {
        "wallet_id": TEST_WALLET_ID,
        "settings": {"default_label": "New Label"},
    }
    mock_get_extra_settings.return_value = {"traction.some_setting": "value"}

    response = await test_module.tenant_wallet_update(mock_request)

    # Assert
    profile.inject.assert_called_once_with(BaseMultitenantManager)
    mock_request.json.assert_awaited_once()
    expected_settings_update = {
        "wallet.webhook_urls": ["http://localhost:8080/webhooks"],
        "wallet.dispatch_type": "both",
        "default_label": "New Label",
        "image_url": "http://example.com/img.png",
        "traction.some_setting": "value",
    }
    # Assert call on the specific mock instance
    mock_multitenant_mgr.update_wallet.assert_awaited_once_with(
        TEST_WALLET_ID, expected_settings_update
    )
    mock_format_wallet_record.assert_called_once_with(mock_wallet_rec)
    assert response.status == 200
    assert json.loads(response.body) == {
        "wallet_id": TEST_WALLET_ID,
        "settings": {"default_label": "New Label"},
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_email_update(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test PUT /tenant/contact_email endpoint."""
    new_email = "new.email@example.com"
    update_body = {"contact_email": new_email}

    # Setup mock request body
    mock_request._set_json_body(update_body)

    # Setup mock TenantRecord and its save method
    mock_tenant_rec = AsyncMock(spec=TenantRecord)
    mock_tenant_rec.contact_email = "old@example.com"
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.tenant_email_update(mock_request)

    # Assert
    mock_request.json.assert_awaited_once()
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    assert mock_tenant_rec.contact_email == new_email
    mock_tenant_rec.save.assert_awaited_once_with(ANY, reason="updated email")
    assert response.status == 200
    assert json.loads(response.body) == update_body


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
@patch(f"{test_module.__name__}.create_api_key")
async def test_tenant_api_key_create(
    mock_create_api_key: AsyncMock,
    MockTenantAuthApiRecordCls: MagicMock,  # Patched class
    MockTenantRecordCls: MagicMock,  # Patched class
    mock_request: MagicMock,
):
    """Test POST /tenant/authentications/api endpoint."""
    alias = "My Test Key"
    create_body = {"alias": alias}
    new_auth_api_id = "new-auth-id-123"
    new_api_key = "secret-key-xyz"

    # Mock TenantRecord query
    mock_tenant_rec = MagicMock(spec=TenantRecord, tenant_id=TEST_TENANT_ID)
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock request body
    mock_request._set_json_body(create_body)

    # Mock helper function return value
    mock_create_api_key.return_value = (new_api_key, new_auth_api_id)

    # Mock the TenantAuthenticationApiRecord constructor and instance
    mock_auth_rec_instance = MagicMock(spec=TenantAuthenticationApiRecord)
    MockTenantAuthApiRecordCls.return_value = mock_auth_rec_instance

    response = await test_module.tenant_api_key(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    mock_request.json.assert_awaited_once()
    # Assert constructor was called with correct data
    MockTenantAuthApiRecordCls.assert_called_once_with(
        alias=alias, tenant_id=TEST_TENANT_ID
    )
    # Assert helper was called with the constructed record instance and manager instance (injected)
    mock_create_api_key.assert_awaited_once_with(mock_auth_rec_instance, ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_authentication_api_id": new_auth_api_id,
        "api_key": new_api_key,
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_tenant_api_key_get_record(
    MockTenantAuthApiRecordCls: MagicMock,
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test GET /tenant/authentications/api/{id} endpoint."""
    auth_api_id_to_get = "auth-api-id-456"

    # Configure request match_info
    mock_request._set_match_info("tenant_authentication_api_id", auth_api_id_to_get)

    # Mock TenantRecord query
    mock_tenant_rec = MagicMock(spec=TenantRecord, tenant_id=TEST_TENANT_ID)
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock TenantAuthenticationApiRecord retrieval and serialize
    mock_auth_rec = MagicMock(
        spec=TenantAuthenticationApiRecord, tenant_id=TEST_TENANT_ID
    )
    mock_auth_rec.serialize.return_value = {
        "tenant_authentication_api_id": auth_api_id_to_get,
        "tenant_id": TEST_TENANT_ID,
        "alias": "Test Key",
    }
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id = AsyncMock(
        return_value=mock_auth_rec
    )

    response = await test_module.tenant_api_key_get(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.assert_awaited_once_with(
        ANY, auth_api_id_to_get
    )
    mock_auth_rec.serialize.assert_called_once()
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_authentication_api_id": auth_api_id_to_get,
        "tenant_id": TEST_TENANT_ID,
        "alias": "Test Key",
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_tenant_api_key_get_record_not_found_wrong_tenant(
    MockTenantAuthApiRecordCls: MagicMock,
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test GET /tenant/authentications/api/{id} raises 404 if tenant_id doesn't match."""
    other_tenant_id = "other-tenant-id"
    auth_api_id_to_get = "auth-api-id-789"

    # Configure request match_info
    mock_request._set_match_info("tenant_authentication_api_id", auth_api_id_to_get)

    # Mock TenantRecord query (returns record for TEST_TENANT_ID)
    mock_tenant_rec = MagicMock(spec=TenantRecord, tenant_id=TEST_TENANT_ID)
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock TenantAuthenticationApiRecord retrieval - return record belonging to different tenant
    mock_auth_rec = MagicMock(
        spec=TenantAuthenticationApiRecord, tenant_id=other_tenant_id
    )
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id = AsyncMock(
        return_value=mock_auth_rec
    )

    with pytest.raises(web.HTTPNotFound):
        await test_module.tenant_api_key_get(mock_request)

    # Assert mocks called
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.assert_awaited_once_with(
        ANY, auth_api_id_to_get
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_tenant_api_key_list_records(
    MockTenantAuthApiRecordCls: MagicMock,
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test GET /tenant/authentications/api/ endpoint."""
    # Mock TenantRecord query
    mock_tenant_rec = MagicMock(spec=TenantRecord, tenant_id=TEST_TENANT_ID)
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock TenantAuthenticationApiRecord query
    mock_auth_rec_1 = MagicMock(spec=TenantAuthenticationApiRecord)
    mock_auth_rec_1.serialize.return_value = {
        "tenant_authentication_api_id": "id1",
        "alias": "Key 1",
    }
    mock_auth_rec_2 = MagicMock(spec=TenantAuthenticationApiRecord)
    mock_auth_rec_2.serialize.return_value = {
        "tenant_authentication_api_id": "id2",
        "alias": "Key 2",
    }
    MockTenantAuthApiRecordCls.query_by_tenant_id = AsyncMock(
        return_value=[mock_auth_rec_1, mock_auth_rec_2]
    )

    response = await test_module.tenant_api_key_list(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    MockTenantAuthApiRecordCls.query_by_tenant_id.assert_awaited_once_with(
        ANY, TEST_TENANT_ID
    )
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [
            {"tenant_authentication_api_id": "id1", "alias": "Key 1"},
            {"tenant_authentication_api_id": "id2", "alias": "Key 2"},
        ]
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
@patch(f"{test_module.__name__}.TenantAuthenticationApiRecord", autospec=True)
async def test_tenant_api_key_delete_record(
    MockTenantAuthApiRecordCls: MagicMock,
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test DELETE /tenant/authentications/api/{id} endpoint."""
    auth_api_id_to_delete = "auth-api-id-abc"

    # Configure request match_info
    mock_request._set_match_info("tenant_authentication_api_id", auth_api_id_to_delete)

    # Mock TenantRecord query
    mock_tenant_rec = MagicMock(spec=TenantRecord, tenant_id=TEST_TENANT_ID)
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock TenantAuthenticationApiRecord retrieval and delete
    mock_auth_rec = AsyncMock(
        spec=TenantAuthenticationApiRecord, tenant_id=TEST_TENANT_ID
    )
    # Simulate retrieve succeeding the first time, failing the second time (after delete)
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.side_effect = [
        mock_auth_rec,
        StorageNotFoundError("Not Found after delete"),
    ]

    response = await test_module.tenant_api_key_delete(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    # Assert retrieve was called twice
    assert MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.await_count == 2
    MockTenantAuthApiRecordCls.retrieve_by_auth_api_id.assert_any_await(
        ANY, auth_api_id_to_delete
    )
    # Assert delete was called on the instance
    mock_auth_rec.delete_record.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {"success": True}


@pytest.mark.asyncio
# Need both manager fixtures for injection setup
@pytest.mark.usefixtures("mock_tenant_mgr", "mock_multitenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_delete_hard(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
    mock_multitenant_mgr: MagicMock,  # Used for assertions
):
    """Test DELETE /tenant/hard endpoint."""
    # Mock TenantRecord query and delete
    mock_tenant_rec = AsyncMock(
        spec=TenantRecord, tenant_id=TEST_TENANT_ID, wallet_id=TEST_WALLET_ID
    )
    mock_tenant_rec.serialize.return_value = {
        "tenant_id": TEST_TENANT_ID,
        "wallet_id": TEST_WALLET_ID,
    }
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    # Mock multitenant manager remove_wallet (on the instance)
    mock_multitenant_mgr.remove_wallet = AsyncMock()

    response = await test_module.tenant_delete(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    # Check multitenant remove was called BEFORE tenant record delete (can check call order if critical)
    mock_multitenant_mgr.remove_wallet.assert_awaited_once_with(TEST_WALLET_ID)
    mock_tenant_rec.delete_record.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "tenant_id": TEST_TENANT_ID,
        "wallet_id": TEST_WALLET_ID,
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_tenant_mgr")
@patch(f"{test_module.__name__}.TenantRecord", autospec=True)
async def test_tenant_delete_soft(
    MockTenantRecordCls: MagicMock,
    mock_request: MagicMock,
):
    """Test DELETE /tenant/soft endpoint."""
    # Mock TenantRecord query and soft_delete
    mock_tenant_rec = AsyncMock(spec=TenantRecord, tenant_id=TEST_TENANT_ID)
    MockTenantRecordCls.query_by_wallet_id = AsyncMock(return_value=mock_tenant_rec)

    response = await test_module.tenant_delete_soft(mock_request)

    # Assert
    MockTenantRecordCls.query_by_wallet_id.assert_awaited_once_with(ANY, TEST_WALLET_ID)
    mock_tenant_rec.soft_delete.assert_awaited_once_with(ANY)
    assert response.status == 200
    assert json.loads(response.body) == {
        "success": f"Tenant {TEST_TENANT_ID} soft deleted."
    }
