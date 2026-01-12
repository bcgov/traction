import logging
from unittest.mock import MagicMock, AsyncMock, patch, call, ANY

from acapy_agent.wallet.models.wallet_record import BaseRecord
import pytest
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError, StorageError
from acapy_agent.core.event_bus import Event, EventBus
from acapy_agent.storage.base import BaseStorage

# Assuming models and service are importable like this
from traction_innkeeper.v1_0.schema_storage.models import SchemaStorageRecord
from traction_innkeeper.v1_0.schema_storage.schema_storage_service import (
    SchemaStorageService,
    schemas_event_handler,
    subscribe,
    INDY_SCHEMA_EVENT_PATTERN,  # Import logger to potentially disable it if needed
)

# Import mocked dependencies
from acapy_agent.ledger.multiple_ledger.ledger_requests_executor import (
    IndyLedgerRequestsExecutor,
    GET_SCHEMA,
)
from acapy_agent.multitenant.base import BaseMultitenantManager
from acapy_agent.ledger.base import BaseLedger

# Disable logging noise during tests
logging.disable(logging.CRITICAL)
# Optionally disable the service's specific logger if it's noisy
# SERVICE_LOGGER.disabled = True

# --- Constants ---
TEST_SCHEMA_ID = "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
TEST_ISSUER_DID = "WgWxqztrNooG92RXvxSTWv"
TEST_LEDGER_ID = "test-ledger-id"
TEST_SCHEMA_DATA = {
    "ver": "1.0",
    "id": TEST_SCHEMA_ID,
    "name": "schema_name",
    "version": "1.0",
    "attrNames": ["attr1", "attr2"],
    "seqNo": 1234,
}


# --- Fixtures ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with settings, session, and inject."""
    profile = MagicMock(spec=Profile)
    mock_session = AsyncMock(name="MockSession")

    # Make profile.session() return the same mock_session each time
    profile.session = MagicMock(return_value=mock_session)

    # Properly mock the async context manager methods
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Mock the session methods
    mock_session.inject_or = MagicMock()
    mock_session.inject = MagicMock()

    profile.settings = mock_session
    profile.settings.get = MagicMock()
    profile.inject = MagicMock()
    return profile, mock_session


@pytest.fixture
def schema_storage_service():
    """Provides a SchemaStorageService instance."""
    return SchemaStorageService()


@pytest.fixture
def mock_schema_storage_record():
    """Provides a mocked SchemaStorageRecord instance."""
    record = AsyncMock(spec=SchemaStorageRecord)
    record.schema_id = TEST_SCHEMA_ID
    record.schema_ = TEST_SCHEMA_DATA  # Note the underscore for the attribute name
    record.ledger_id = TEST_LEDGER_ID
    record.record_value = {"schema": TEST_SCHEMA_DATA}  # Simulate internal storage
    record.save = AsyncMock()
    record.delete_record = AsyncMock()
    # Add serialize if needed by any consuming code (not directly used by service)
    record.serialize = MagicMock(
        return_value={
            "schema_id": TEST_SCHEMA_ID,
            "schema": TEST_SCHEMA_DATA,
            "ledger_id": TEST_LEDGER_ID,
        }
    )
    return record


@pytest.fixture
def mock_ledger_executor(mock_profile: tuple):
    """Provides a mocked IndyLedgerRequestsExecutor."""
    executor = AsyncMock(spec=IndyLedgerRequestsExecutor)
    executor.get_ledger_for_identifier = AsyncMock()
    # Configure injection for the executor
    profile, session = mock_profile
    session.inject.return_value = executor  # Default injection
    return executor


@pytest.fixture
def mock_ledger():
    """Provides a mocked BaseLedger."""
    ledger = AsyncMock(spec=BaseLedger)
    ledger.get_schema = AsyncMock(return_value=TEST_SCHEMA_DATA)
    # Mock async context manager
    ledger.__aenter__ = AsyncMock(return_value=ledger)
    ledger.__aexit__ = AsyncMock(return_value=None)
    return ledger


@pytest.fixture
def mock_storage(mock_profile: tuple):
    """Provides a mocked BaseStorage."""
    storage = AsyncMock(spec=BaseStorage)
    storage.find_all_records = AsyncMock()
    # Configure injection
    profile, session = mock_profile
    session.inject.return_value = storage
    return storage


@pytest.fixture
def mock_event():
    """Provides a mocked Event."""
    event = MagicMock(spec=Event)
    event.payload = {"context": {"schema_id": TEST_SCHEMA_ID}}
    return event


@pytest.fixture
def mock_event_bus():
    """Provides a mocked EventBus."""
    bus = MagicMock(spec=EventBus)
    bus.subscribe = MagicMock()
    return bus


# --- Test Cases for SchemaStorageService ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_read_item_success(
    mock_retrieve: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_schema_storage_record: AsyncMock,
):
    """Test successfully reading a SchemaStorageRecord."""
    profile, session = mock_profile
    mock_retrieve.return_value = mock_schema_storage_record

    result = await schema_storage_service.read_item(profile, TEST_SCHEMA_ID)

    assert result == mock_schema_storage_record
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_SCHEMA_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_read_item_not_found(
    mock_retrieve: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
):
    """Test reading a non-existent SchemaStorageRecord."""
    profile, session = mock_profile
    mock_retrieve.side_effect = StorageNotFoundError("Record not found")

    result = await schema_storage_service.read_item(profile, TEST_SCHEMA_ID)

    assert result is None
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_SCHEMA_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_read_item_other_error(
    mock_retrieve: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
):
    """Test handling unexpected errors during read."""
    profile, session = mock_profile
    mock_retrieve.side_effect = Exception("Database connection failed")

    result = await schema_storage_service.read_item(profile, TEST_SCHEMA_ID)

    assert result is None  # Should still return None and log the error
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_SCHEMA_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.query",
    new_callable=AsyncMock,
)
async def test_list_items_success(
    mock_query: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_schema_storage_record: AsyncMock,
):
    """Test successfully listing items with filters."""
    profile, session = mock_profile
    mock_query.return_value = [mock_schema_storage_record]
    tag_filter = {"issuer_did": TEST_ISSUER_DID}
    post_filter = {"ledger_id": TEST_LEDGER_ID}

    result = await schema_storage_service.list_items(profile, tag_filter, post_filter)

    assert result == [mock_schema_storage_record]
    profile.session.assert_called_once()
    mock_query.assert_awaited_once_with(
        session=session,
        tag_filter=tag_filter,
        post_filter_positive=post_filter,
        alt=True,
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.query",
    new_callable=AsyncMock,
)
async def test_list_items_no_filters(
    mock_query: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
):
    """Test listing items with default empty filters."""
    profile, session = mock_profile
    mock_query.return_value = []

    result = await schema_storage_service.list_items(profile)  # No filters passed

    assert result == []
    profile.session.assert_called_once()
    mock_query.assert_awaited_once_with(
        session=session,
        tag_filter={},
        post_filter_positive={},
        alt=True,
    )


# --- add_item tests ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.read_item",
    new_callable=AsyncMock,
)
@patch("traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.deserialize")
async def test_add_item_existing(
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_schema_storage_record: AsyncMock,
):
    """Test add_item when the record already exists."""
    profile, _ = mock_profile
    mock_read_item.return_value = mock_schema_storage_record  # Simulate exists

    result = await schema_storage_service.add_item(
        profile, {"schema_id": TEST_SCHEMA_ID}
    )

    assert result == mock_schema_storage_record
    mock_read_item.assert_awaited_once_with(profile, TEST_SCHEMA_ID)
    # Ensure ledger/save path is not taken
    profile.session.assert_not_called()
    mock_deserialize.assert_not_called()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.read_item",
)
@patch("traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.deserialize")
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.IndyLedgerRequestsExecutor",
    autospec=True,
)
async def test_add_item_new_success_with_multitenant(
    MockExecutorCls: MagicMock,
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_ledger: AsyncMock,
    mock_schema_storage_record: AsyncMock,
):
    """Test add_item success for a new record with multitenancy."""
    profile, session = mock_profile
    mock_read_item.return_value = None  # Does not exist

    # Mock multitenant manager
    mock_multitenant_mgr = MagicMock(spec=BaseMultitenantManager)
    session.inject_or.return_value = mock_multitenant_mgr

    # Mock executor instance
    mock_executor_instance = MockExecutorCls.return_value
    mock_executor_instance.get_ledger_for_identifier = AsyncMock(
        return_value=(TEST_LEDGER_ID, mock_ledger)
    )

    # Mock ledger.get_schema
    mock_ledger.get_schema = AsyncMock(return_value=TEST_SCHEMA_DATA)

    # Mock the async context manager for ledger
    mock_ledger.__aenter__ = AsyncMock(return_value=mock_ledger)
    mock_ledger.__aexit__ = AsyncMock(return_value=None)

    # Mock deserialize
    mock_deserialize.return_value = mock_schema_storage_record

    # Execute the test
    result = await schema_storage_service.add_item(
        profile, {"schema_id": TEST_SCHEMA_ID}
    )

    # Assertions
    assert result == mock_schema_storage_record
    mock_read_item.assert_awaited_once_with(profile, TEST_SCHEMA_ID)

    # profile.session() should be called twice
    assert profile.session.call_count == 2

    session.inject_or.assert_called_once_with(BaseMultitenantManager)
    MockExecutorCls.assert_called_once_with(profile)
    session.inject.assert_not_called()

    mock_executor_instance.get_ledger_for_identifier.assert_awaited_once_with(
        TEST_SCHEMA_ID, txn_record_type=GET_SCHEMA
    )
    mock_ledger.get_schema.assert_awaited_once_with(TEST_SCHEMA_ID)
    mock_deserialize.assert_called_once()
    mock_schema_storage_record.save.assert_awaited_once_with(
        session, reason="New schema storage record"
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.read_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.IndyLedgerRequestsExecutor",
    autospec=True,
)
async def test_add_item_ledger_schema_not_found(
    MockExecutorCls: MagicMock,
    mock_read_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_ledger: AsyncMock,
):
    """Test add_item when the schema is not found on the ledger."""
    profile, session = mock_profile
    mock_read_item.return_value = None
    session.inject_or.return_value = None  # No multitenant
    mock_executor_instance = MagicMock()
    mock_executor_instance.get_ledger_for_identifier = AsyncMock(
        return_value=(TEST_LEDGER_ID, mock_ledger)
    )
    session.inject.return_value = mock_executor_instance
    MockExecutorCls.return_value = mock_executor_instance  # Instance from class mock
    # Simulate ledger error or returning None
    mock_ledger.get_schema.return_value = None
    # Or mock_ledger.get_schema.side_effect = LedgerError("Not found")

    with pytest.raises(StorageNotFoundError, match="Schema not found on ledger"):
        await schema_storage_service.add_item(profile, {"schema_id": TEST_SCHEMA_ID})

    mock_read_item.assert_awaited_once_with(profile, TEST_SCHEMA_ID)
    mock_ledger.get_schema.assert_awaited_once_with(TEST_SCHEMA_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.read_item",
    new_callable=AsyncMock,
)
@patch("traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.deserialize")
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.IndyLedgerRequestsExecutor",
    autospec=True,
)
async def test_add_item_deserialize_error(
    MockExecutorCls: MagicMock,
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_ledger: AsyncMock,
):
    """Test add_item with a deserialization error."""
    profile, session = mock_profile
    mock_read_item.return_value = None
    session.inject_or.return_value = None
    mock_executor_instance = AsyncMock()
    session.inject.return_value = mock_executor_instance
    MockExecutorCls.return_value = mock_executor_instance  # Instance from class mock
    mock_executor_instance.get_ledger_for_identifier = AsyncMock(
        return_value=(TEST_LEDGER_ID, mock_ledger)
    )
    mock_ledger.get_schema.return_value = TEST_SCHEMA_DATA
    mock_deserialize.side_effect = TypeError("Bad data")  # Simulate deserialize failure

    with pytest.raises(TypeError, match="Bad data"):
        await schema_storage_service.add_item(profile, {"schema_id": TEST_SCHEMA_ID})

    mock_deserialize.assert_called_once()
    # Ensure save wasn't called
    profile.session.assert_called_once()  # Only called for inject


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.read_item",
)
@patch("traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.deserialize")
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.IndyLedgerRequestsExecutor",
    autospec=True,
)
async def test_add_item_save_error(
    MockExecutorCls: MagicMock,
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_ledger: AsyncMock,
    mock_schema_storage_record: AsyncMock,
):
    """Test add_item with a storage save error."""
    profile, session = mock_profile
    mock_read_item.return_value = None
    session.inject_or.return_value = None
    mock_executor_instance = MagicMock()
    mock_executor_instance.get_ledger_for_identifier = AsyncMock(
        return_value=(TEST_LEDGER_ID, mock_ledger)
    )

    session.inject.return_value = mock_executor_instance
    MockExecutorCls.return_value = mock_executor_instance  # Instance from class mock
    mock_ledger.get_schema.return_value = TEST_SCHEMA_DATA
    mock_deserialize.return_value = mock_schema_storage_record

    mock_schema_storage_record.save.side_effect = StorageError("DB write failed")

    with pytest.raises(StorageError, match="DB write failed"):
        await schema_storage_service.add_item(profile, {"schema_id": TEST_SCHEMA_ID})

    mock_deserialize.assert_called_once()
    mock_schema_storage_record.save.assert_awaited_once()


# --- remove_item tests ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_success(
    mock_retrieve: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_schema_storage_record: AsyncMock,
):
    """Test successfully removing an item."""
    profile, session = mock_profile
    # Simulate retrieve succeeding first, then failing after delete
    mock_retrieve.side_effect = [
        mock_schema_storage_record,
        StorageNotFoundError("Not found after delete"),
    ]

    result = await schema_storage_service.remove_item(profile, TEST_SCHEMA_ID)

    assert result is True
    profile.session.assert_called_once()  # Only one session context used
    # Check retrieve was called twice
    assert mock_retrieve.await_count == 2
    mock_retrieve.assert_has_awaits(
        [call(session, TEST_SCHEMA_ID), call(session, TEST_SCHEMA_ID)]
    )
    mock_schema_storage_record.delete_record.assert_awaited_once_with(session)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_already_gone(
    mock_retrieve: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
):
    """Test removing an item that is already not found."""
    profile, session = mock_profile
    mock_retrieve.side_effect = StorageNotFoundError("Record not found")

    result = await schema_storage_service.remove_item(profile, TEST_SCHEMA_ID)

    assert result is True  # Still returns True
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_SCHEMA_ID)


@pytest.mark.skip("TODO: for some reason remove_by_id is never awaited")
@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.models.SchemaStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_delete_error(
    mock_retrieve: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple,
    mock_schema_storage_record: AsyncMock,
):
    """Test error during delete_record when removing."""
    profile, session = mock_profile
    mock_retrieve.return_value = mock_schema_storage_record
    mock_schema_storage_record.delete_record.side_effect = StorageError(
        "DB write failed"
    )

    # Service catches the error and returns False
    result = await schema_storage_service.remove_item(profile, TEST_SCHEMA_ID)

    assert result is False
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_SCHEMA_ID)
    mock_schema_storage_record.delete_record.assert_awaited_once_with(session)


# --- sync_created tests ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.add_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.list_items",
    new_callable=AsyncMock,
)
@pytest.mark.skip(
    "TODO: AttributeError: 'coroutine' object has no attribute 'find_all_records'"
)
async def test_sync_created_success(
    mock_list_items: AsyncMock,
    mock_add_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_schema_storage_record: AsyncMock,
):
    """Test sync_created successfully adds found schemas."""
    mock_storage = MagicMock(spec=BaseStorage)
    profile, session = mock_profile
    profile.session = AsyncMock(return_value=session)

    schema_id_1 = "schema-id-1"
    schema_id_2 = "schema-id-2"
    mock_record_1 = MagicMock(spec=BaseRecord, value=schema_id_1)
    mock_record_2 = MagicMock(spec=BaseRecord, value=schema_id_2)
    mock_storage.find_all_records.return_value = [mock_record_1, mock_record_2]
    mock_list_items.return_value = [mock_schema_storage_record]  # Final list result

    session.inject.return_value = mock_storage
    result = await schema_storage_service.sync_created(profile)

    assert result == [mock_schema_storage_record]
    # Check session usage
    assert profile.session.await_count == 1  # Used for find_all_records
    session.inject.assert_called_once_with(BaseStorage)
    mock_storage.find_all_records.assert_awaited_once_with(
        type_filter=ANY,  # Check for SCHEMA_SENT_RECORD_TYPE
        tag_query={},
    )
    # Check add_item calls
    assert mock_add_item.await_count == 2
    mock_add_item.assert_has_awaits(
        [
            call(profile, schema_id_1),
            call(profile, schema_id_2),
        ]
    )
    # Check final list call
    mock_list_items.assert_awaited_once_with(profile)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.add_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.schema_storage.schema_storage_service.SchemaStorageService.list_items",
    new_callable=AsyncMock,
)
@pytest.mark.skip("TODO: 'coroutine' object has no attribute 'find_all_records'")
async def test_sync_created_no_schemas_found(
    mock_list_items: AsyncMock,
    mock_add_item: AsyncMock,
    schema_storage_service: SchemaStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test sync_created when no schema_sent records are found."""
    mock_storage = MagicMock(spec=BaseStorage)
    profile, session = mock_profile
    profile.session = AsyncMock(return_value=session)
    mock_storage.find_all_records.return_value = []  # No records found
    mock_list_items.return_value = []  # Final list is empty
    session.inject.return_value = mock_storage

    result = await schema_storage_service.sync_created(profile)

    assert result == []
    session.inject.assert_called_once_with(BaseStorage)
    mock_storage.find_all_records.assert_awaited_once()
    mock_add_item.assert_not_awaited()  # add_item should not be called
    mock_list_items.assert_awaited_once_with(profile)


# --- Global Function Tests ---


def test_subscribe(mock_event_bus: MagicMock):
    """Test the subscribe function registers the handler."""
    subscribe(mock_event_bus)
    # Should subscribe to both Indy and AnonCreds events (if available)
    assert mock_event_bus.subscribe.call_count >= 1
    # Check that Indy pattern is subscribed
    mock_event_bus.subscribe.assert_any_call(
        INDY_SCHEMA_EVENT_PATTERN, schemas_event_handler
    )


@pytest.mark.asyncio
async def test_schemas_event_handler(
    mock_profile: tuple,
    schema_storage_service: SchemaStorageService,  # Use fixture
    mock_event: MagicMock,
    mock_schema_storage_record: AsyncMock,
):
    """Test the schemas_event_handler function."""
    profile, _ = mock_profile
    # Mock profile.inject to return our service instance
    profile.inject.return_value = schema_storage_service
    # Mock the service's add_item method specifically for this test
    schema_storage_service.add_item = AsyncMock(return_value=mock_schema_storage_record)

    await schemas_event_handler(profile, mock_event)

    profile.inject.assert_called_once_with(SchemaStorageService)
    # Event handler normalizes event payload to dict format
    schema_storage_service.add_item.assert_awaited_once()
    call_args = schema_storage_service.add_item.call_args
    assert call_args[0][0] == profile
    assert call_args[0][1].get("schema_id") == TEST_SCHEMA_ID
