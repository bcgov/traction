import json
import logging
from unittest.mock import MagicMock, AsyncMock

import pytest
from aiohttp import web
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError, StorageError
from acapy_agent.messaging.models.base import BaseModelError

# Import the module containing the routes to be tested
# Adjust path as necessary
from traction_innkeeper.v1_0.schema_storage import routes as test_module

# Import Service and Models used for mocking
from traction_innkeeper.v1_0.schema_storage.schema_storage_service import (
    SchemaStorageService,
)
from traction_innkeeper.v1_0.schema_storage.models import (
    SchemaStorageRecord,  # Although schema not directly used, good practice
)


# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_SCHEMA_ID = "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
TEST_ISSUER_DID = "WgWxqztrNooG92RXvxSTWv"
TEST_API_KEY = "test-schema-storage-api-key"
TEST_SCHEMA_DATA = {
    "ver": "1.0",
    "id": TEST_SCHEMA_ID,
    "name": "schema_name",
    "version": "1.0",
    "attrNames": ["attr1", "attr2"],
    "seqNo": 1234,
}

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
    }
    profile.context.settings = profile.settings
    profile.session = MagicMock(return_value=mock_session)
    profile.inject, profile._injectables = mock_profile_inject
    profile.inject_or = (
        profile.inject
    )  # Assume inject_or behaves like inject for simplicity
    return profile


@pytest.fixture
def mock_context(mock_profile: MagicMock):
    """Provides a mocked AdminRequestContext containing the mock profile."""
    context = MagicMock(name="AdminRequestContext")
    context.profile = mock_profile
    context.inject = mock_profile.inject
    context.inject_or = mock_profile.inject_or
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
    request._set_json_body = lambda data: setattr(request.json, "return_value", data)
    return request


@pytest.fixture
def mock_schema_storage_service(mock_profile: MagicMock):
    """Provides a mocked SchemaStorageService AND configures it for injection."""
    service = AsyncMock(spec=SchemaStorageService)
    # Add mocked methods expected by routes
    service.list_items = AsyncMock()
    service.add_item = AsyncMock()
    service.read_item = AsyncMock()
    service.remove_item = AsyncMock()
    service.sync_created = AsyncMock()
    # Configure injection
    mock_profile._injectables[SchemaStorageService] = service
    return service


@pytest.fixture
def mock_schema_storage_record():
    """Provides a mocked SchemaStorageRecord instance."""
    record = MagicMock(spec=SchemaStorageRecord)
    record.schema_id = TEST_SCHEMA_ID
    record.serialize = MagicMock(
        return_value={
            "schema_id": TEST_SCHEMA_ID,
            "schema": TEST_SCHEMA_DATA,
            "ledger_id": "test-ledger",
        }
    )
    return record


# --- Test Cases ---


# Test List Schemas (GET /schema-storage)
@pytest.mark.asyncio
async def test_schema_storage_list(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage endpoint."""
    profile = mock_context.profile

    # Mock service response
    mock_rec_1 = MagicMock(spec=SchemaStorageRecord)
    mock_rec_1.serialize.return_value = {"schema_id": "schema-1"}
    mock_rec_2 = MagicMock(spec=SchemaStorageRecord)
    mock_rec_2.serialize.return_value = {"schema_id": "schema-2"}
    mock_schema_storage_service.list_items.return_value = [mock_rec_1, mock_rec_2]

    response = await test_module.schema_storage_list(mock_request)

    # Check service was injected and called
    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.list_items.assert_awaited_once_with(
        profile,
        {},
        {},  # Default filters
    )

    # Check response
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [
            {"schema_id": "schema-1"},
            {"schema_id": "schema-2"},
        ]
    }
    mock_rec_1.serialize.assert_called_once()
    mock_rec_2.serialize.assert_called_once()


@pytest.mark.asyncio
async def test_schema_storage_list_empty(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage endpoint with no results."""
    profile = mock_context.profile
    mock_schema_storage_service.list_items.return_value = []  # Empty list

    response = await test_module.schema_storage_list(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.list_items.assert_awaited_once_with(profile, {}, {})
    assert response.status == 200
    assert json.loads(response.body) == {"results": []}


@pytest.mark.asyncio
async def test_schema_storage_list_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage endpoint with StorageError."""
    mock_schema_storage_service.list_items.side_effect = StorageError(
        "DB connection lost"
    )

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.schema_storage_list(mock_request)
    assert "DB connection lost" in str(excinfo.value)


# Test Add Schema (POST /schema-storage)
@pytest.mark.asyncio
async def test_schema_storage_add_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
    mock_schema_storage_record: MagicMock,
):
    """Test POST /schema-storage endpoint success."""
    profile = mock_context.profile
    add_body = {"schema_id": TEST_SCHEMA_ID}
    mock_request._set_json_body(add_body)
    mock_schema_storage_service.add_item.return_value = mock_schema_storage_record

    response = await test_module.schema_storage_add(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_request.json.assert_awaited_once()
    mock_schema_storage_service.add_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )
    assert response.status == 200
    assert (
        json.loads(response.body) == mock_schema_storage_record.serialize.return_value
    )
    mock_schema_storage_record.serialize.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (StorageNotFoundError, web.HTTPNotFound),  # If add_item uses ledger and fails
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
        (Exception, Exception),  # Check re-raise
    ],
)
async def test_schema_storage_add_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test POST /schema-storage endpoint error handling."""
    profile = mock_context.profile
    add_body = {"schema_id": TEST_SCHEMA_ID}
    mock_request._set_json_body(add_body)
    error_message = "Test Add Error"
    mock_schema_storage_service.add_item.side_effect = error_cls(error_message)

    with pytest.raises(expected_exception) as excinfo:
        await test_module.schema_storage_add(mock_request)

    if expected_exception is not Exception:
        assert error_message in str(excinfo.value)

    mock_schema_storage_service.add_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )


# Test Get Schema (GET /schema-storage/{schema_id})
@pytest.mark.asyncio
async def test_schema_storage_get_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
    mock_schema_storage_record: MagicMock,
):
    """Test GET /schema-storage/{schema_id} endpoint success."""
    profile = mock_context.profile
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    mock_schema_storage_service.read_item.return_value = mock_schema_storage_record

    response = await test_module.schema_storage_get(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.read_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )
    assert response.status == 200
    assert (
        json.loads(response.body) == mock_schema_storage_record.serialize.return_value
    )
    mock_schema_storage_record.serialize.assert_called_once()


@pytest.mark.asyncio
async def test_schema_storage_get_not_found(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage/{schema_id} not found."""
    profile = mock_context.profile
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    mock_schema_storage_service.read_item.side_effect = StorageNotFoundError(
        "Record not found"
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.schema_storage_get(mock_request)
    assert "Record not found" in str(excinfo.value)

    mock_schema_storage_service.read_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )


@pytest.mark.asyncio
async def test_schema_storage_get_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage/{schema_id} with StorageError."""
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    mock_schema_storage_service.read_item.side_effect = StorageError("Bad read")

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.schema_storage_get(mock_request)
    assert "Bad read" in str(excinfo.value)


# Test Remove Schema (DELETE /schema-storage/{schema_id})
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "service_return, expected_success",
    [
        (True, True),
        (False, False),
    ],
)
async def test_schema_storage_remove_success(
    service_return,
    expected_success,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test DELETE /schema-storage/{schema_id} success cases."""
    profile = mock_context.profile
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    mock_schema_storage_service.remove_item.return_value = service_return

    response = await test_module.schema_storage_remove(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.remove_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )
    assert response.status == 200
    assert json.loads(response.body) == {"success": expected_success}


@pytest.mark.asyncio
async def test_schema_storage_remove_not_found(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test DELETE /schema-storage/{schema_id} not found."""
    profile = mock_context.profile
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    mock_schema_storage_service.remove_item.side_effect = StorageNotFoundError(
        "Cannot find to remove"
    )

    with pytest.raises(web.HTTPNotFound) as excinfo:
        await test_module.schema_storage_remove(mock_request)
    assert "Cannot find to remove" in str(excinfo.value)

    mock_schema_storage_service.remove_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )


@pytest.mark.asyncio
async def test_schema_storage_remove_storage_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test DELETE /schema-storage/{schema_id} with StorageError."""
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    mock_schema_storage_service.remove_item.side_effect = StorageError("Cannot delete")

    with pytest.raises(web.HTTPBadRequest) as excinfo:
        await test_module.schema_storage_remove(mock_request)
    assert "Cannot delete" in str(excinfo.value)


# Test Sync Created Schemas (POST /schema-storage/sync-created)
@pytest.mark.asyncio
async def test_schema_storage_sync_created_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
    mock_schema_storage_record: MagicMock,
):
    """Test POST /schema-storage/sync-created endpoint success."""
    profile = mock_context.profile

    # Mock service response
    mock_rec_synced = MagicMock(spec=SchemaStorageRecord)
    mock_rec_synced.serialize.return_value = {"schema_id": "synced-schema-1"}
    mock_schema_storage_service.sync_created.return_value = [mock_rec_synced]

    response = await test_module.schema_storage_sync_created(mock_request)

    # Check service was injected and called
    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.sync_created.assert_awaited_once_with(profile)

    # Check response
    assert response.status == 200
    assert json.loads(response.body) == {"results": [{"schema_id": "synced-schema-1"}]}
    mock_rec_synced.serialize.assert_called_once()


@pytest.mark.asyncio
async def test_schema_storage_sync_created_empty(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test POST /schema-storage/sync-created endpoint with no results."""
    profile = mock_context.profile
    mock_schema_storage_service.sync_created.return_value = []  # Empty list

    response = await test_module.schema_storage_sync_created(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.sync_created.assert_awaited_once_with(profile)
    assert response.status == 200
    assert json.loads(response.body) == {"results": []}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
        (Exception, Exception),  # Check re-raise
    ],
)
async def test_schema_storage_sync_created_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test POST /schema-storage/sync-created endpoint error handling."""
    profile = mock_context.profile
    error_message = "Test Sync Error"
    mock_schema_storage_service.sync_created.side_effect = error_cls(error_message)

    with pytest.raises(expected_exception) as excinfo:
        await test_module.schema_storage_sync_created(mock_request)

    if expected_exception is not Exception:
        assert error_message in str(excinfo.value)

    mock_schema_storage_service.sync_created.assert_awaited_once_with(profile)


# Test register function
@pytest.mark.asyncio
async def test_register():
    """Test route registration."""
    mock_app = MagicMock(spec=web.Application)
    mock_app.add_routes = MagicMock()

    await test_module.register(mock_app)  # Await the async function

    calls = mock_app.add_routes.call_args_list
    assert len(calls) == 1
    registered_routes = calls[0][0][0]  # Get the list of web.RouteDef objects
    assert len(registered_routes) == 5  # Check number of routes
    paths_methods = {(r.path, r.method) for r in registered_routes}
    assert ("/schema-storage", "GET") in paths_methods
    assert ("/schema-storage", "POST") in paths_methods
    assert ("/schema-storage/{schema_id}", "GET") in paths_methods
    assert ("/schema-storage/{schema_id}", "DELETE") in paths_methods
    assert ("/schema-storage/sync-created", "POST") in paths_methods


# Test post_process_routes function
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


@pytest.mark.asyncio
async def test_schema_storage_list_generic_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage endpoint with generic Exception."""
    profile = mock_context.profile
    error_message = "Generic unexpected list error"
    mock_schema_storage_service.list_items.side_effect = Exception(error_message)

    # The error_handler should catch Exception and re-raise it
    with pytest.raises(Exception, match=error_message):
        await test_module.schema_storage_list(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.list_items.assert_awaited_once_with(profile, {}, {})


@pytest.mark.asyncio
async def test_schema_storage_add_generic_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test POST /schema-storage endpoint with generic Exception."""
    profile = mock_context.profile
    add_body = {"schema_id": TEST_SCHEMA_ID}
    mock_request._set_json_body(add_body)
    error_message = "Generic unexpected add error"
    mock_schema_storage_service.add_item.side_effect = Exception(error_message)

    # The error_handler should catch Exception and re-raise it
    with pytest.raises(Exception, match=error_message):
        await test_module.schema_storage_add(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_request.json.assert_awaited_once()
    mock_schema_storage_service.add_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )


@pytest.mark.asyncio
async def test_schema_storage_get_generic_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test GET /schema-storage/{schema_id} endpoint with generic Exception."""
    profile = mock_context.profile
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    error_message = "Generic unexpected get error"
    mock_schema_storage_service.read_item.side_effect = Exception(error_message)

    # The error_handler should catch Exception and re-raise it
    with pytest.raises(Exception, match=error_message):
        await test_module.schema_storage_get(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.read_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )


@pytest.mark.asyncio
async def test_schema_storage_remove_generic_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test DELETE /schema-storage/{schema_id} endpoint with generic Exception."""
    profile = mock_context.profile
    mock_request._set_match_info("schema_id", TEST_SCHEMA_ID)
    error_message = "Generic unexpected remove error"
    mock_schema_storage_service.remove_item.side_effect = Exception(error_message)

    # The error_handler should catch Exception and re-raise it
    with pytest.raises(Exception, match=error_message):
        await test_module.schema_storage_remove(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.remove_item.assert_awaited_once_with(
        profile, TEST_SCHEMA_ID
    )


@pytest.mark.asyncio
async def test_schema_storage_sync_created_generic_error(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_schema_storage_service: AsyncMock,
):
    """Test POST /schema-storage/sync-created endpoint with generic Exception."""
    profile = mock_context.profile
    error_message = "Generic unexpected sync error"
    mock_schema_storage_service.sync_created.side_effect = Exception(error_message)

    # The error_handler should catch Exception and re-raise it
    with pytest.raises(Exception, match=error_message):
        await test_module.schema_storage_sync_created(mock_request)

    mock_context.inject_or.assert_called_once_with(SchemaStorageService)
    mock_schema_storage_service.sync_created.assert_awaited_once_with(profile)
