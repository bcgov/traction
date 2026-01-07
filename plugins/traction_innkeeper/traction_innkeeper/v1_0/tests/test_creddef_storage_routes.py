import json
import logging
from unittest.mock import MagicMock, AsyncMock

import pytest
from aiohttp import web
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError, StorageError

# Import the module containing the routes to be tested
# Adjust path as necessary
from traction_innkeeper.v1_0.creddef_storage import routes as test_module

# Import Service and Models used for mocking
from traction_innkeeper.v1_0.creddef_storage.creddef_storage_service import (
    CredDefStorageService,
)
from traction_innkeeper.v1_0.creddef_storage.models import (
    CredDefStorageRecord,  # Although schema not directly used, good practice
)


# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_CRED_DEF_ID = "55GkHamhTU1ZbTbV2ab9DE:3:CL:1234:default"
TEST_ISSUER_DID = "55GkHamhTU1ZbTbV2ab9DE"
TEST_API_KEY = "test-creddef-api-key"

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
            # Return the default if provided (for inject_or)
            if args:
                return args[0]
            return MagicMock()  # Fallback for regular inject
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
    profile = MagicMock(name="Profile", spec=Profile)
    profile.context = MagicMock(name="Context")
    profile.settings = {
        "admin.admin_api_key": TEST_API_KEY,
        # Add other base settings if needed
    }
    profile.context.settings = profile.settings
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    # Add inject_or mock based on inject
    profile.inject_or = profile.inject
    return profile


@pytest.fixture
def mock_context(mock_profile: MagicMock):
    """Provides a mocked AdminRequestContext containing the mock profile."""
    context = MagicMock(name="AdminRequestContext")
    context.profile = mock_profile
    # Link inject/inject_or for convenience if context is used directly for injection
    context.inject = mock_profile.inject
    context.inject_or = mock_profile.inject_or
    return context


@pytest.fixture
def mock_request(mock_context: MagicMock):
    """Provides a mocked aiohttp.web.Request linked to the context."""
    request = MagicMock(spec=web.Request)
    request.match_info = {}
    request.query = {}
    # --- Crucial for tenant_authentication ---
    request.headers = {"x-api-key": TEST_API_KEY}
    # -----------------------------------------

    def getitem_side_effect(key):
        if key == "context":
            return mock_context
        # Allow accessing headers like a dict
        if key == "headers":
            return request.headers
        return MagicMock()

    request.__getitem__.side_effect = getitem_side_effect

    request.json = AsyncMock()
    request._set_match_info = lambda key, value: request.match_info.update({key: value})

    return request


@pytest.fixture
def mock_creddef_storage_service(mock_profile: MagicMock):
    """Provides a mocked CredDefStorageService AND configures it for injection."""
    service = AsyncMock(spec=CredDefStorageService)
    # Add mocked methods expected by routes
    service.list_items = AsyncMock()
    service.read_item = AsyncMock()
    service.remove_item = AsyncMock()

    # Configure injection
    mock_profile._injectables[CredDefStorageService] = service
    return service


# --- Test Cases ---


# Test List Cred Defs (GET /credential-definition-storage)
@pytest.mark.asyncio
async def test_creddef_storage_list(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test GET /credential-definition-storage endpoint."""
    profile = mock_context.profile

    # Mock service response
    mock_rec_1 = MagicMock(spec=CredDefStorageRecord)
    mock_rec_1.serialize.return_value = {"cred_def_id": "cred-def-1"}
    mock_rec_2 = MagicMock(spec=CredDefStorageRecord)
    mock_rec_2.serialize.return_value = {"cred_def_id": "cred-def-2"}
    mock_creddef_storage_service.list_items.return_value = [mock_rec_1, mock_rec_2]

    response = await test_module.creddef_storage_list(mock_request)

    # Check service was injected and called
    mock_context.inject_or.assert_called_once_with(CredDefStorageService)
    mock_creddef_storage_service.list_items.assert_awaited_once_with(
        profile, {}, {}  # Default filters
    )

    # Check response
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [
            {"cred_def_id": "cred-def-1"},
            {"cred_def_id": "cred-def-2"},
        ]
    }
    mock_rec_1.serialize.assert_called_once()
    mock_rec_2.serialize.assert_called_once()


@pytest.mark.asyncio
async def test_creddef_storage_list_empty(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test GET /credential-definition-storage endpoint with no results."""
    profile = mock_context.profile
    mock_creddef_storage_service.list_items.return_value = []  # Empty list

    response = await test_module.creddef_storage_list(mock_request)

    mock_context.inject_or.assert_called_once_with(CredDefStorageService)
    mock_creddef_storage_service.list_items.assert_awaited_once_with(profile, {}, {})
    assert response.status == 200
    assert json.loads(response.body) == {"results": []}


@pytest.mark.asyncio
async def test_creddef_storage_list_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test GET /credential-definition-storage endpoint with StorageError."""
    mock_creddef_storage_service.list_items.side_effect = StorageError(
        "DB connection lost"
    )

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.creddef_storage_list(mock_request)
    assert "DB connection lost" in str(excinfo.value)


# Test Get Cred Def (GET /credential-definition-storage/{cred_def_id})
@pytest.mark.asyncio
async def test_creddef_storage_get(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test GET /credential-definition-storage/{cred_def_id} endpoint."""
    profile = mock_context.profile
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)

    # Mock service response
    mock_rec = MagicMock(spec=CredDefStorageRecord)
    mock_rec.serialize.return_value = {
        "cred_def_id": TEST_CRED_DEF_ID,
        "issuer_did": TEST_ISSUER_DID,
    }
    mock_creddef_storage_service.read_item.return_value = mock_rec

    response = await test_module.creddef_storage_get(mock_request)

    # Check service was injected and called
    mock_context.inject_or.assert_called_once_with(CredDefStorageService)
    mock_creddef_storage_service.read_item.assert_awaited_once_with(
        profile, TEST_CRED_DEF_ID
    )

    # Check response
    assert response.status == 200
    assert json.loads(response.body) == {
        "cred_def_id": TEST_CRED_DEF_ID,
        "issuer_did": TEST_ISSUER_DID,
    }
    mock_rec.serialize.assert_called_once()


@pytest.mark.asyncio
async def test_creddef_storage_get_not_found(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test GET /credential-definition-storage/{cred_def_id} not found."""
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)
    mock_creddef_storage_service.read_item.side_effect = StorageNotFoundError(
        "Record not found"
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.creddef_storage_get(mock_request)
    assert "Record not found" in str(excinfo.value)

    mock_creddef_storage_service.read_item.assert_awaited_once_with(
        mock_context.profile, TEST_CRED_DEF_ID
    )


@pytest.mark.asyncio
async def test_creddef_storage_get_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test GET /credential-definition-storage/{cred_def_id} with StorageError."""
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)
    mock_creddef_storage_service.read_item.side_effect = StorageError("Bad read")

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.creddef_storage_get(mock_request)
    assert "Bad read" in str(excinfo.value)


# Test Remove Cred Def (DELETE /credential-definition-storage/{cred_def_id})
@pytest.mark.asyncio
async def test_creddef_storage_remove_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test DELETE /credential-definition-storage/{cred_def_id} success."""
    profile = mock_context.profile
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)

    # Mock service response
    mock_creddef_storage_service.remove_item.return_value = True

    response = await test_module.creddef_storage_remove(mock_request)

    # Check service was injected and called
    mock_context.inject_or.assert_called_once_with(CredDefStorageService)
    mock_creddef_storage_service.remove_item.assert_awaited_once_with(
        profile, TEST_CRED_DEF_ID
    )

    # Check response
    assert response.status == 200
    assert json.loads(response.body) == {"success": True}


@pytest.mark.asyncio
async def test_creddef_storage_remove_failure_from_service(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test DELETE /credential-definition-storage/{cred_def_id} where service returns false."""
    profile = mock_context.profile
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)
    mock_creddef_storage_service.remove_item.return_value = False

    response = await test_module.creddef_storage_remove(mock_request)

    mock_context.inject_or.assert_called_once_with(CredDefStorageService)
    mock_creddef_storage_service.remove_item.assert_awaited_once_with(
        profile, TEST_CRED_DEF_ID
    )
    assert response.status == 200
    assert json.loads(response.body) == {"success": False}


@pytest.mark.asyncio
async def test_creddef_storage_remove_not_found(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test DELETE /credential-definition-storage/{cred_def_id} not found."""
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)
    mock_creddef_storage_service.remove_item.side_effect = StorageNotFoundError(
        "Cannot find to remove"
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.creddef_storage_remove(mock_request)
    assert "Cannot find to remove" in str(excinfo.value)

    mock_creddef_storage_service.remove_item.assert_awaited_once_with(
        mock_context.profile, TEST_CRED_DEF_ID
    )


@pytest.mark.asyncio
async def test_creddef_storage_remove_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_creddef_storage_service: AsyncMock,
):
    """Test DELETE /credential-definition-storage/{cred_def_id} with StorageError."""
    mock_request._set_match_info("cred_def_id", TEST_CRED_DEF_ID)
    mock_creddef_storage_service.remove_item.side_effect = StorageError("Cannot delete")

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.creddef_storage_remove(mock_request)
    assert "Cannot delete" in str(excinfo.value)


# --- Optional: Test register and post_process_routes ---
# These are usually simple and less critical to unit test,
# but can be added for completeness if desired.


async def test_register():
    """Test route registration."""
    mock_app = MagicMock(spec=web.Application)
    mock_app.add_routes = MagicMock()

    await test_module.register(mock_app)  # Call the sync function

    calls = mock_app.add_routes.call_args_list
    # Check that add_routes was called once with a list containing the expected routes
    assert len(calls) == 1
    registered_routes = calls[0][0][0]  # Get the list of web.RouteDef objects
    assert len(registered_routes) == 4
    # Check paths and methods (can be more specific if needed)
    assert any(
        r.method == "GET" and r.path == "/credential-definition-storage"
        for r in registered_routes
    )
    assert any(
        r.method == "POST" and r.path == "/credential-definition-storage"
        for r in registered_routes
    )
    assert any(
        r.method == "GET" and r.path == "/credential-definition-storage/{cred_def_id}"
        for r in registered_routes
    )
    assert any(
        r.method == "DELETE"
        and r.path == "/credential-definition-storage/{cred_def_id}"
        for r in registered_routes
    )


def test_post_process_routes():
    """Test swagger documentation tagging."""
    mock_app = MagicMock()
    mock_app._state = {"swagger_dict": {}}  # Simulate swagger dict state

    test_module.post_process_routes(mock_app)

    assert "tags" in mock_app._state["swagger_dict"]
    assert len(mock_app._state["swagger_dict"]["tags"]) == 1
    assert (
        mock_app._state["swagger_dict"]["tags"][0]["name"]
        == test_module.SWAGGER_CATEGORY
    )
    assert "description" in mock_app._state["swagger_dict"]["tags"][0]


def test_post_process_routes_existing_tags():
    """Test swagger documentation tagging when tags list already exists."""
    mock_app = MagicMock()
    mock_app._state = {"swagger_dict": {"tags": [{"name": "existing_tag"}]}}

    test_module.post_process_routes(mock_app)

    assert len(mock_app._state["swagger_dict"]["tags"]) == 2
    assert mock_app._state["swagger_dict"]["tags"][0]["name"] == "existing_tag"
    assert (
        mock_app._state["swagger_dict"]["tags"][1]["name"]
        == test_module.SWAGGER_CATEGORY
    )
