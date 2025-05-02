import json
import logging
from unittest.mock import MagicMock, AsyncMock

import pytest
from aiohttp import web
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError, StorageError
from acapy_agent.messaging.models.base import BaseModelError
from marshmallow import ValidationError

# Import the module containing the routes to be tested
# Adjust path as necessary
from traction_innkeeper.v1_0.oca import routes as test_module

# Import Service and Models used for mocking
from traction_innkeeper.v1_0.oca.oca_service import (
    OcaService,
    PublicDIDRequiredError,
    PublicDIDMismatchError,
)

# Assuming OcaRecord exists and has serialize method
from traction_innkeeper.v1_0.oca.models import OcaRecord

# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_OCA_ID = "test-oca-id-123"
TEST_SCHEMA_ID = "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
TEST_CRED_DEF_ID = "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
TEST_OCA_URL = "http://example.com/oca.json"
TEST_OCA_BUNDLE = {"format": "aries/oca-bundle", "version": ["1.0"]}
TEST_API_KEY = "test-oca-api-key"

# --- Reusable Fixtures (similar to test_innkeeper_routes.py) ---


@pytest.fixture
def mock_profile_inject():
    """Provides a mock injector function and tracks injectable mocks."""
    injectables = {}

    def _injector(cls_to_inject, *args, **kwargs):
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
def mock_oca_service(mock_profile: MagicMock):
    """Provides a mocked OcaService AND configures it for injection."""
    service = AsyncMock(spec=OcaService)
    # Add mocked methods expected by routes
    service.create_or_update_oca_record = AsyncMock()
    service.read_oca_record = AsyncMock()
    service.update_oca_record = AsyncMock()
    service.delete_oca_record = AsyncMock()
    service.list_oca_records = AsyncMock()
    # Configure injection
    mock_profile._injectables[OcaService] = service
    return service


@pytest.fixture
def mock_oca_record():
    """Provides a mocked OcaRecord instance."""
    record = MagicMock(spec=OcaRecord)
    record.oca_record_id = TEST_OCA_ID
    record.cred_def_id = TEST_CRED_DEF_ID
    # Add other fields if needed by specific tests
    record.serialize = MagicMock(
        return_value={
            "oca_record_id": TEST_OCA_ID,
            "cred_def_id": TEST_CRED_DEF_ID,
            "url": TEST_OCA_URL,
            "oca_bundle": TEST_OCA_BUNDLE,
        }
    )
    return record


# --- Test Cases ---


# Test Create OCA Record (POST /oca)
@pytest.mark.asyncio
async def test_oca_record_create_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
    mock_oca_record: MagicMock,
):
    """Test POST /oca endpoint success."""
    profile = mock_context.profile
    create_body = {"cred_def_id": TEST_CRED_DEF_ID, "url": TEST_OCA_URL}
    mock_request._set_json_body(create_body)
    mock_oca_service.create_or_update_oca_record.return_value = mock_oca_record

    response = await test_module.oca_record_create(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_request.json.assert_awaited_once()
    mock_oca_service.create_or_update_oca_record.assert_awaited_once_with(
        profile, create_body
    )
    assert response.status == 200
    assert json.loads(response.body) == mock_oca_record.serialize.return_value
    mock_oca_record.serialize.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (ValidationError, web.HTTPUnprocessableEntity),
        (PublicDIDRequiredError, web.HTTPBadRequest),
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
        (Exception, Exception),  # Test generic exception re-raising
    ],
)
async def test_oca_record_create_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test POST /oca endpoint error handling."""
    profile = mock_context.profile
    create_body = {"cred_def_id": TEST_CRED_DEF_ID}
    mock_request._set_json_body(create_body)
    error_message = "Test Error"
    # Use .messages for ValidationError
    error_instance = error_cls(
        error_message if error_cls != ValidationError else {"field": [error_message]}
    )
    mock_oca_service.create_or_update_oca_record.side_effect = error_instance

    with pytest.raises(expected_exception) as excinfo:
        await test_module.oca_record_create(mock_request)

    # For handled exceptions, check the reason
    if expected_exception is not Exception:
        assert error_message in str(excinfo.value)

    mock_oca_service.create_or_update_oca_record.assert_awaited_once_with(
        profile, create_body
    )


# Test Read OCA Record (GET /oca/{oca_id})
@pytest.mark.asyncio
async def test_oca_record_read_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
    mock_oca_record: MagicMock,
):
    """Test GET /oca/{oca_id} endpoint success."""
    profile = mock_context.profile
    mock_request._set_match_info("oca_id", TEST_OCA_ID)
    mock_oca_service.read_oca_record.return_value = mock_oca_record

    response = await test_module.oca_record_read(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_oca_service.read_oca_record.assert_awaited_once_with(profile, TEST_OCA_ID)
    assert response.status == 200
    assert json.loads(response.body) == mock_oca_record.serialize.return_value
    mock_oca_record.serialize.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (StorageNotFoundError, web.HTTPNotFound),
        (PublicDIDMismatchError, web.HTTPUnauthorized),
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
    ],
)
async def test_oca_record_read_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test GET /oca/{oca_id} endpoint error handling."""
    profile = mock_context.profile
    mock_request._set_match_info("oca_id", TEST_OCA_ID)
    error_message = "Test Read Error"
    mock_oca_service.read_oca_record.side_effect = error_cls(error_message)

    with pytest.raises(expected_exception) as excinfo:
        await test_module.oca_record_read(mock_request)

    assert error_message in str(excinfo.value)
    mock_oca_service.read_oca_record.assert_awaited_once_with(profile, TEST_OCA_ID)


# Test Update OCA Record (PUT /oca/{oca_id})
@pytest.mark.asyncio
async def test_oca_record_update_success(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
    mock_oca_record: MagicMock,
):
    """Test PUT /oca/{oca_id} endpoint success."""
    profile = mock_context.profile
    mock_request._set_match_info("oca_id", TEST_OCA_ID)
    update_body = {"url": "http://new.url/bundle.json"}
    mock_request._set_json_body(update_body)
    mock_oca_service.update_oca_record.return_value = mock_oca_record

    response = await test_module.oca_record_update(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_request.json.assert_awaited_once()
    mock_oca_service.update_oca_record.assert_awaited_once_with(
        profile, TEST_OCA_ID, update_body
    )
    assert response.status == 200
    assert json.loads(response.body) == mock_oca_record.serialize.return_value
    mock_oca_record.serialize.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (
            ValidationError,
            web.HTTPUnprocessableEntity,
        ),  # From potential request body validation
        (StorageNotFoundError, web.HTTPNotFound),
        (PublicDIDMismatchError, web.HTTPUnauthorized),
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
    ],
)
async def test_oca_record_update_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test PUT /oca/{oca_id} endpoint error handling."""
    profile = mock_context.profile
    mock_request._set_match_info("oca_id", TEST_OCA_ID)
    update_body = {"url": "http://new.url/bundle.json"}
    mock_request._set_json_body(update_body)
    error_message = "Test Update Error"
    error_instance = error_cls(
        error_message if error_cls != ValidationError else {"field": [error_message]}
    )
    mock_oca_service.update_oca_record.side_effect = error_instance

    with pytest.raises(expected_exception) as excinfo:
        await test_module.oca_record_update(mock_request)

    assert error_message in str(excinfo.value)
    mock_oca_service.update_oca_record.assert_awaited_once_with(
        profile, TEST_OCA_ID, update_body
    )


# Test Delete OCA Record (DELETE /oca/{oca_id})
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "service_return, expected_success",
    [
        (True, True),
        (False, False),
    ],
)
async def test_oca_record_delete_success(
    service_return,
    expected_success,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test DELETE /oca/{oca_id} endpoint success cases."""
    profile = mock_context.profile
    mock_request._set_match_info("oca_id", TEST_OCA_ID)
    mock_oca_service.delete_oca_record.return_value = service_return

    response = await test_module.oca_record_delete(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_oca_service.delete_oca_record.assert_awaited_once_with(profile, TEST_OCA_ID)
    assert response.status == 200
    assert json.loads(response.body) == {"success": expected_success}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (StorageNotFoundError, web.HTTPNotFound),
        (PublicDIDMismatchError, web.HTTPUnauthorized),
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
    ],
)
async def test_oca_record_delete_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test DELETE /oca/{oca_id} endpoint error handling."""
    profile = mock_context.profile
    mock_request._set_match_info("oca_id", TEST_OCA_ID)
    error_message = "Test Delete Error"
    mock_oca_service.delete_oca_record.side_effect = error_cls(error_message)

    with pytest.raises(expected_exception) as excinfo:
        await test_module.oca_record_delete(mock_request)

    assert error_message in str(excinfo.value)
    mock_oca_service.delete_oca_record.assert_awaited_once_with(profile, TEST_OCA_ID)


# Test List OCA Records (GET /oca)
@pytest.mark.asyncio
async def test_oca_record_list_success_no_filter(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
    mock_oca_record: MagicMock,
):
    """Test GET /oca endpoint success without filters."""
    profile = mock_context.profile
    # Need a second mock record for list
    mock_rec2 = MagicMock(spec=OcaRecord)
    mock_rec2.serialize.return_value = {"oca_record_id": "oca-id-456"}
    mock_oca_service.list_oca_records.return_value = [mock_oca_record, mock_rec2]

    response = await test_module.oca_record_list(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_oca_service.list_oca_records.assert_awaited_once_with(
        profile, None, None
    )  # No filters
    assert response.status == 200
    assert json.loads(response.body) == {
        "results": [mock_oca_record.serialize(), mock_rec2.serialize()]
    }
    mock_oca_record.serialize.assert_called()
    mock_rec2.serialize.assert_called()


@pytest.mark.asyncio
async def test_oca_record_list_success_with_filter(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
    mock_oca_record: MagicMock,
):
    """Test GET /oca endpoint success with cred_def_id filter."""
    profile = mock_context.profile
    mock_request.query["cred_def_id"] = TEST_CRED_DEF_ID  # Set query param
    mock_oca_service.list_oca_records.return_value = [
        mock_oca_record
    ]  # Assume filter returns one

    response = await test_module.oca_record_list(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_oca_service.list_oca_records.assert_awaited_once_with(
        profile, None, TEST_CRED_DEF_ID
    )
    assert response.status == 200
    assert json.loads(response.body) == {"results": [mock_oca_record.serialize()]}
    mock_oca_record.serialize.assert_called()


@pytest.mark.asyncio
async def test_oca_record_list_empty(
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test GET /oca endpoint success with empty results."""
    profile = mock_context.profile
    mock_oca_service.list_oca_records.return_value = []  # Empty list

    response = await test_module.oca_record_list(mock_request)

    mock_context.inject.assert_called_once_with(OcaService)
    mock_oca_service.list_oca_records.assert_awaited_once_with(profile, None, None)
    assert response.status == 200
    assert json.loads(response.body) == {"results": []}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_cls, expected_exception",
    [
        (StorageError, web.HTTPBadRequest),
        (BaseModelError, web.HTTPBadRequest),
    ],
)
async def test_oca_record_list_errors(
    error_cls,
    expected_exception,
    mock_request: MagicMock,
    mock_context: MagicMock,
    mock_oca_service: AsyncMock,
):
    """Test GET /oca endpoint error handling."""
    profile = mock_context.profile
    error_message = "Test List Error"
    mock_oca_service.list_oca_records.side_effect = error_cls(error_message)

    with pytest.raises(expected_exception) as excinfo:
        await test_module.oca_record_list(mock_request)

    assert error_message in str(excinfo.value)
    mock_oca_service.list_oca_records.assert_awaited_once_with(profile, None, None)


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
    assert ("/oca", "GET") in paths_methods
    assert ("/oca", "POST") in paths_methods
    assert ("/oca/{oca_id}", "GET") in paths_methods
    assert ("/oca/{oca_id}", "PUT") in paths_methods
    assert ("/oca/{oca_id}", "DELETE") in paths_methods


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
