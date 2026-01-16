import logging
from unittest.mock import MagicMock, AsyncMock, patch, call, ANY

import pytest
from acapy_agent.core.profile import Profile
from acapy_agent.storage.error import StorageNotFoundError
from acapy_agent.core.event_bus import Event

# Assuming models and service are importable like this
from traction_innkeeper.v1_0.creddef_storage.models import CredDefStorageRecord
from traction_innkeeper.v1_0.creddef_storage.creddef_storage_service import (
    CredDefStorageService,
    creddef_event_handler,  # Import the handler function as well
)

# Disable logging noise during tests
logging.disable(logging.CRITICAL)

# --- Constants ---
TEST_CRED_DEF_ID = "55GkHamhTU1ZbTbV2ab9DE:3:CL:1234:default"
TEST_ISSUER_DID = "55GkHamhTU1ZbTbV2ab9DE"
TEST_SCHEMA_ID = f"{TEST_ISSUER_DID}:2:schema_name:1.0"
TEST_TAG = "default"
TEST_SUPPORT_REVOCATION = False
TEST_CONTEXT = {
    "cred_def_id": TEST_CRED_DEF_ID,
    "issuer_did": TEST_ISSUER_DID,
    "schema_id": TEST_SCHEMA_ID,
    "tag": TEST_TAG,
    "support_revocation": TEST_SUPPORT_REVOCATION,
    "rev_reg_size": None,
    "options": {},
}


# --- Fixtures ---
@pytest.fixture
def mock_profile():
    """Provides a mocked Profile with a working async session manager."""
    profile = MagicMock(spec=Profile)
    mock_session = AsyncMock(name="MockSession")
    profile.session = MagicMock(return_value=mock_session)
    # Make the session usable in an 'async with' block
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    # Add inject mock
    profile.inject = MagicMock()
    return profile, mock_session


@pytest.fixture
def creddef_storage_service():
    """Provides a CredDefStorageService instance."""
    # The service itself doesn't require profile injection at init
    return CredDefStorageService()


@pytest.fixture
def mock_creddef_storage_record():
    """Provides a mocked CredDefStorageRecord instance."""
    record = AsyncMock(spec=CredDefStorageRecord)
    record.cred_def_id = TEST_CRED_DEF_ID
    # Add other attributes if needed for specific tests
    return record


# --- Test Cases for CredDefStorageService ---


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_read_item_success(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test successfully reading a CredDefStorageRecord."""
    profile, session = mock_profile
    mock_retrieve.return_value = mock_creddef_storage_record

    result = await creddef_storage_service.read_item(profile, TEST_CRED_DEF_ID)

    assert result == mock_creddef_storage_record
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_DEF_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_read_item_not_found(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test reading a non-existent CredDefStorageRecord."""
    profile, session = mock_profile
    mock_retrieve.side_effect = StorageNotFoundError("Record not found")

    result = await creddef_storage_service.read_item(profile, TEST_CRED_DEF_ID)

    assert result is None
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_DEF_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_read_item_other_error(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test handling unexpected errors during read."""
    profile, session = mock_profile
    mock_retrieve.side_effect = Exception("Database connection failed")

    # Should still return None and log the error (logging disabled)
    result = await creddef_storage_service.read_item(profile, TEST_CRED_DEF_ID)

    assert result is None
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_DEF_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.query",
    new_callable=AsyncMock,
)
async def test_list_items_success(
    mock_query: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test successfully listing items with filters."""
    profile, session = mock_profile
    mock_query.return_value = [mock_creddef_storage_record]
    tag_filter = {"issuer_did": TEST_ISSUER_DID}
    post_filter = {"support_revocation": False}

    result = await creddef_storage_service.list_items(profile, tag_filter, post_filter)

    assert result == [mock_creddef_storage_record]
    profile.session.assert_called_once()
    mock_query.assert_awaited_once_with(
        session=session,
        tag_filter=tag_filter,
        post_filter_positive=post_filter,
        alt=True,
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.query",
    new_callable=AsyncMock,
)
async def test_list_items_no_filters(
    mock_query: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test listing items with default empty filters."""
    profile, session = mock_profile
    mock_query.return_value = []

    result = await creddef_storage_service.list_items(profile)  # No filters passed

    assert result == []
    profile.session.assert_called_once()
    # Verify default empty dicts are passed
    mock_query.assert_awaited_once_with(
        session=session,
        tag_filter={},
        post_filter_positive={},
        alt=True,
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.creddef_storage_service.CredDefStorageService.read_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.deserialize"
)
async def test_add_item_new(
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test adding a new CredDefStorageRecord."""
    profile, session = mock_profile
    mock_read_item.return_value = None  # Simulate record doesn't exist
    mock_deserialize.return_value = mock_creddef_storage_record
    mock_creddef_storage_record.save = (
        AsyncMock()
    )  # Mock the save method on the instance

    data = TEST_CONTEXT.copy()
    result = await creddef_storage_service.add_item(profile, data)

    assert result == mock_creddef_storage_record
    mock_read_item.assert_awaited_once_with(profile, TEST_CRED_DEF_ID)
    mock_deserialize.assert_called_once_with(data)
    profile.session.assert_called_once()  # Called by save
    mock_creddef_storage_record.save.assert_awaited_once_with(
        session, reason="New cred def storage record"
    )


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.creddef_storage_service.CredDefStorageService.read_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.deserialize"
)
async def test_add_item_existing(
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test adding an item that already exists (should be no-op)."""
    profile, _ = mock_profile
    mock_read_item.return_value = mock_creddef_storage_record  # Simulate record exists

    data = TEST_CONTEXT.copy()
    result = await creddef_storage_service.add_item(profile, data)

    assert result == mock_creddef_storage_record  # Returns existing record
    mock_read_item.assert_awaited_once_with(profile, TEST_CRED_DEF_ID)
    mock_deserialize.assert_not_called()
    profile.session.assert_not_called()  # Save should not be called


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.creddef_storage_service.CredDefStorageService.read_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.deserialize"
)
async def test_add_item_deserialize_error(
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test error during deserialization when adding."""
    profile, _ = mock_profile
    mock_read_item.return_value = None
    mock_deserialize.side_effect = TypeError("Invalid data format")

    data = TEST_CONTEXT.copy()
    with pytest.raises(TypeError, match="Invalid data format"):
        await creddef_storage_service.add_item(profile, data)

    mock_read_item.assert_awaited_once_with(profile, TEST_CRED_DEF_ID)
    mock_deserialize.assert_called_once_with(data)
    profile.session.assert_not_called()


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.creddef_storage_service.CredDefStorageService.read_item",
    new_callable=AsyncMock,
)
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.deserialize"
)
async def test_add_item_save_error(
    mock_deserialize: MagicMock,
    mock_read_item: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test error during save when adding."""
    profile, session = mock_profile
    mock_read_item.return_value = None
    mock_deserialize.return_value = mock_creddef_storage_record
    mock_creddef_storage_record.save = AsyncMock(
        side_effect=Exception("DB write failed")
    )

    data = TEST_CONTEXT.copy()
    with pytest.raises(Exception, match="DB write failed"):
        await creddef_storage_service.add_item(profile, data)

    mock_read_item.assert_awaited_once_with(profile, TEST_CRED_DEF_ID)
    mock_deserialize.assert_called_once_with(data)
    profile.session.assert_called_once()
    mock_creddef_storage_record.save.assert_awaited_once_with(session, reason=ANY)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_success(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test successfully removing an item."""
    profile, session = mock_profile
    # Simulate retrieve succeeding first, then failing after delete
    mock_retrieve.side_effect = [
        mock_creddef_storage_record,
        StorageNotFoundError("Not found after delete"),
    ]
    mock_creddef_storage_record.delete_record = AsyncMock()

    result = await creddef_storage_service.remove_item(profile, TEST_CRED_DEF_ID)

    assert result is True
    assert profile.session.call_count == 1  # Only one session context used
    # Check retrieve was called twice (once to get, once to confirm deletion)
    assert mock_retrieve.await_count == 2
    mock_retrieve.assert_has_awaits(
        [
            call(session, TEST_CRED_DEF_ID),
            call(session, TEST_CRED_DEF_ID),
        ]
    )
    mock_creddef_storage_record.delete_record.assert_awaited_once_with(session)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_already_gone(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test removing an item that is already not found."""
    profile, session = mock_profile
    mock_retrieve.side_effect = StorageNotFoundError("Record not found")

    result = await creddef_storage_service.remove_item(profile, TEST_CRED_DEF_ID)

    assert result is True  # Still returns True as the end state is 'not found'
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_DEF_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_retrieve_error(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
):
    """Test error during initial retrieve when removing."""
    profile, session = mock_profile
    mock_retrieve.side_effect = Exception("DB read failed")

    result = await creddef_storage_service.remove_item(profile, TEST_CRED_DEF_ID)

    assert result is False
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_DEF_ID)


@pytest.mark.asyncio
@patch(
    "traction_innkeeper.v1_0.creddef_storage.models.CredDefStorageRecord.retrieve_by_id",
    new_callable=AsyncMock,
)
async def test_remove_item_delete_error(
    mock_retrieve: AsyncMock,
    creddef_storage_service: CredDefStorageService,
    mock_profile: tuple[MagicMock, AsyncMock],
    mock_creddef_storage_record: AsyncMock,
):
    """Test error during delete_record when removing."""
    profile, session = mock_profile
    mock_retrieve.return_value = mock_creddef_storage_record
    mock_creddef_storage_record.delete_record = AsyncMock(
        side_effect=Exception("DB write failed")
    )

    result = await creddef_storage_service.remove_item(profile, TEST_CRED_DEF_ID)

    assert result is False
    profile.session.assert_called_once()
    mock_retrieve.assert_awaited_once_with(session, TEST_CRED_DEF_ID)
    mock_creddef_storage_record.delete_record.assert_awaited_once_with(session)


# --- Test Cases for Event Handler ---


@pytest.mark.asyncio
async def test_creddef_event_handler(
    mock_profile: tuple[MagicMock, AsyncMock],
    creddef_storage_service: CredDefStorageService,  # Use the fixture
    mock_creddef_storage_record: AsyncMock,
):
    """Test the creddef_event_handler function."""
    profile, _ = mock_profile
    mock_event = MagicMock(spec=Event)
    mock_event.payload = {"context": TEST_CONTEXT}

    # Mock the service's add_item method specifically for this test
    creddef_storage_service.add_item = AsyncMock(
        return_value=mock_creddef_storage_record
    )

    # Mock profile.inject to return our service instance
    profile.inject.return_value = creddef_storage_service

    await creddef_event_handler(profile, mock_event)

    profile.inject.assert_called_once_with(CredDefStorageService)
    # The normalization function transforms the event payload
    # Expected normalized data structure
    expected_normalized_data = {
        "cred_def_id": TEST_CRED_DEF_ID,
        "schema_id": TEST_SCHEMA_ID,
        "tag": TEST_TAG,
        "support_revocation": TEST_SUPPORT_REVOCATION,
        "rev_reg_size": None,
        "issuer_did": TEST_ISSUER_DID,
        "options": {},
    }
    creddef_storage_service.add_item.assert_awaited_once_with(
        profile, expected_normalized_data
    )
